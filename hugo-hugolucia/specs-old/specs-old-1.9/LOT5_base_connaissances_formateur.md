# LOT 5 — Base de connaissances formateur (V1)

**Durée estimée :** 5–7 jours  
**Risque :** modéré — nouveau pipeline, pas de modification du moteur conversationnel  
**Dépendance :** LOT 0 + LOT 1 opérationnels ; LOT 3 optionnel mais recommandé

---

## Objectif

Permettre au formateur d'uploader des documents, de saisir des compléments dialogiques,
et de produire une base de connaissances structurée utilisée par Hugo.
Les critères provisoires sont tracés et soumis à validation humaine.

---

## Règle de sécurité du lot

- `KnowledgeItemStatus` importé depuis `conversation_profile.py` (NR-09).
- Aucun critère `DERIVED_PROVISIONAL` ne peut passer à `VALIDATED_TRAINER` sans action humaine explicite.
- La base de connaissances n'est jamais source primaire de vérité sur la conformité réglementaire.
- Le champ RLS : `organisation_id` (avec s).

---

## Modèle Django `TrainerKnowledgeItem`

```python
# backend/apps/hugo/models.py — ajouter

class TrainerKnowledgeItem(models.Model):
    """
    Élément de connaissance structuré produit par ou pour le formateur.
    statut : declared | derived_provisional | validated_trainer
    """
    organisation_id = models.CharField(max_length=128, db_index=True)   # avec s
    referential_item_id = models.CharField(max_length=256, blank=True, default="")
    content         = models.TextField()
    content_type    = models.CharField(max_length=64, default="mastery_criterion")
    # mastery_criterion | frequent_error | reasoning_chain | reference_rule | procedure
    source_type     = models.CharField(max_length=64, default="declared")
    # declared | document_extracted | dialogue_elicited | llm_derived
    status          = models.CharField(
        max_length=32,
        choices=[(s.value, s.value) for s in KnowledgeItemStatus],
        default=KnowledgeItemStatus.DECLARED.value,
    )
    confidence_score = models.FloatField(null=True, blank=True)
    provenance_note  = models.TextField(blank=True, default="")
    validated_by     = models.CharField(max_length=128, blank=True, default="")
    validated_at     = models.DateTimeField(null=True, blank=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Connaissance formateur"
```

---

## Pipeline d'ingestion documentaire

### `backend/apps/hugo/services/document_ingestor.py`

```python
"""
Pipeline d'ingestion de documents formateur.
Supporte : PDF texte, PDF scanné (OCR), JPEG/PNG.
Pour les PDF non vectoriels et les images : utilise vision LLM.
"""

import base64, mimetypes
from pathlib import Path


def ingest_document(file_path: str, organisation_id: str, referential_item_id: str = "") -> list[dict]:
    """
    Retourne une liste de raw_items (non encore validés).
    Chaque item est un dict compatible TrainerKnowledgeItem.
    """
    path = Path(file_path)
    mime, _ = mimetypes.guess_type(str(path))
    if mime == "application/pdf":
        text = _extract_pdf_text(path)
        if text.strip():
            return _extract_items_from_text(text, organisation_id, referential_item_id)
        else:
            return _extract_items_from_image_pdf(path, organisation_id, referential_item_id)
    elif mime and mime.startswith("image/"):
        return _extract_items_from_image(path, organisation_id, referential_item_id)
    return []


def _extract_pdf_text(path: Path) -> str:
    try:
        import pdfplumber
        with pdfplumber.open(str(path)) as pdf:
            return "\n".join(p.extract_text() or "" for p in pdf.pages)
    except Exception:
        return ""


def _extract_items_from_text(text: str, org_id: str, ref_id: str) -> list[dict]:
    from backend.apps.hugo.services.llm_client import call_llm_extraction
    prompt = _build_extraction_prompt(text)
    return call_llm_extraction(prompt, org_id, ref_id)


def _extract_items_from_image_pdf(path: Path, org_id: str, ref_id: str) -> list[dict]:
    from backend.apps.hugo.services.llm_client import call_llm_vision_extraction
    with open(str(path), "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return call_llm_vision_extraction(b64, "application/pdf", org_id, ref_id)


def _extract_items_from_image(path: Path, org_id: str, ref_id: str) -> list[dict]:
    from backend.apps.hugo.services.llm_client import call_llm_vision_extraction
    mime, _ = mimetypes.guess_type(str(path))
    with open(str(path), "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return call_llm_vision_extraction(b64, mime or "image/png", org_id, ref_id)


def _build_extraction_prompt(text: str) -> str:
    return f"""
Tu es un assistant qui extrait des éléments pédagogiques structurés depuis un document de formation.
Pour chaque élément identifié, produis un JSON avec :
- content      : texte de l'élément
- content_type : mastery_criterion | frequent_error | reasoning_chain | reference_rule | procedure
- confidence   : score entre 0.0 et 1.0
- provenance   : phrase source ou page

Texte à analyser :
---
{text[:8000]}
---
Réponds uniquement en JSON, liste d'objets.
"""
```

---

## Questionnaire dialogique formateur (endpoint)

```python
# backend/apps/hugo/views/trainer.py

from django.http import JsonResponse
from backend.apps.hugo.domain.conversation_profile import KnowledgeItemStatus

ELICITATION_QUESTIONS = [
    {"id": "q_mastery",   "text": "Qu'est-ce qu'un apprenant qui maîtrise vraiment ce point est capable de faire ?"},
    {"id": "q_errors",    "text": "Quelles sont les erreurs les plus fréquentes que vous observez sur ce point ?"},
    {"id": "q_chains",    "text": "Quelle est la chaîne de raisonnement que vous attendez (ou à éviter absolument) ?"},
    {"id": "q_rules",     "text": "Existe-t-il des règles réglementaires ou de sécurité absolues à ne jamais violer ?"},
    {"id": "q_situations","text": "Pouvez-vous donner un exemple de situation professionnelle typique ?"},
]


def get_elicitation_questions(request, referential_item_id):
    return JsonResponse({"questions": ELICITATION_QUESTIONS, "referential_item_id": referential_item_id})


def save_elicitation_answers(request, referential_item_id):
    import json
    from backend.apps.hugo.models import TrainerKnowledgeItem
    answers = json.loads(request.body).get("answers", {})
    items_created = []
    for q_id, answer_text in answers.items():
        if answer_text.strip():
            item = TrainerKnowledgeItem.objects.create(
                organisation_id=request.user.organisation_id,  # avec s
                referential_item_id=referential_item_id,
                content=answer_text.strip(),
                content_type=_q_to_content_type(q_id),
                source_type="dialogue_elicited",
                status=KnowledgeItemStatus.DECLARED.value,
                provenance_note=f"Elicitation question: {q_id}",
            )
            items_created.append(item.id)
    return JsonResponse({"created": items_created})


def _q_to_content_type(q_id: str) -> str:
    return {
        "q_mastery":    "mastery_criterion",
        "q_errors":     "frequent_error",
        "q_chains":     "reasoning_chain",
        "q_rules":      "reference_rule",
        "q_situations": "mastery_criterion",
    }.get(q_id, "mastery_criterion")
```

---

## Endpoint validation humaine

```python
# backend/apps/hugo/views/trainer.py — ajouter

from django.utils import timezone


def validate_knowledge_item(request, item_id):
    from backend.apps.hugo.models import TrainerKnowledgeItem
    from backend.apps.hugo.domain.conversation_profile import KnowledgeItemStatus
    item = TrainerKnowledgeItem.objects.get(id=item_id, organisation_id=request.user.organisation_id)
    action = request.POST.get("action")  # "validate" | "reject" | "edit"
    if action == "validate":
        item.status = KnowledgeItemStatus.VALIDATED_TRAINER.value
        item.validated_by = str(request.user.id)
        item.validated_at = timezone.now()
        item.save()
        return JsonResponse({"status": "validated"})
    elif action == "reject":
        item.delete()
        return JsonResponse({"status": "rejected"})
    elif action == "edit":
        item.content = request.POST.get("content", item.content)
        item.status  = KnowledgeItemStatus.VALIDATED_TRAINER.value
        item.validated_by = str(request.user.id)
        item.validated_at = timezone.now()
        item.save()
        return JsonResponse({"status": "edited_and_validated"})
    return JsonResponse({"error": "action_inconnue"}, status=400)
```

---

## Checklist de sortie du LOT 5

- [ ] Les 9 tests NR LOT 0 restent verts.
- [ ] `TrainerKnowledgeItem` créé, migration appliquée.
- [ ] `KnowledgeItemStatus` importé depuis `conversation_profile.py`.
- [ ] `organisation_id` (avec s) dans tous les filtres.
- [ ] Pipeline ingestion : PDF texte ✓, PDF scanné ✓, JPEG/PNG ✓.
- [ ] Tout item extrait par LLM = statut `derived_provisional`.
- [ ] Aucun passage automatique à `validated_trainer`.
- [ ] Questionnaire dialogique retourne 5 questions structurées.
- [ ] Endpoint `/validate/<item_id>` opérationnel.
- [ ] Schémas validés et documentés.
