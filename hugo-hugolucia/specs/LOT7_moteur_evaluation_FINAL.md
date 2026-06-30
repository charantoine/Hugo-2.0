# LOT 7 — Moteur de co-construction du récap et de l'évaluation

**Version** : 2.0 — 02 juin 2026  
**Statut** : Spec cible complète, vérifiée, prête pour Cursor  
**Dépendances** : LOT 0 ✅ LOT 1 ✅ LOT 3 ✅ LOT 5 recommandé  
**Durée estimée** : 8–10 jours  
**Risque** : Modéré — nouveau pipeline additif, P0 intact, orchestrateur en lecture seule

---

## Vérification de compatibilité avec les lots précédents

| Contrat | Lot source | Status LOT 7 |
|---|---|---|
| `ConversationPosture`, `SessionMaturityLevel`, `KnowledgeItemStatus` importés depuis `conversationprofile.py` | LOT 0 NR-09 | ✅ respecté |
| `organisationid` avec `s` partout | LOT 0, SPEC v1.5 §13 | ✅ respecté |
| `UIState` sans champ P0 brut | LOT 0 NR-07 | ✅ — `EvaluationContext` testé séparément, même règle |
| `decisionenginev17.py`, `turnstatev17.py`, `hugoorchestrator.py` : lecture seule | LOT 1 | ✅ respecté |
| `ConversationProgressCalculator` exécuté après `decide_conversation` | LOT 1 | ✅ LOT 7 s'exécute après le cycle ordinaire, en mode séparé |
| `tutorprofiles.py` complet (non stub) et `TUTORPROFILES` à clés canoniques | LOT 3 | ✅ non modifié |
| `synthesisservice.py` appelé par `request-synthesis` | LOT 3 | ✅ non modifié — LOT 7 ajoute ses propres endpoints |
| `KnowledgeItemStatus.VALIDATED_TRAINER.value` pour persistance | LOT 5 | ✅ respecté |
| Aucun passage automatique `derived_provisional` → `validated_trainer` | LOT 5 | ✅ — LOT 7 ne modifie pas `TrainerKnowledgeItem` |
| RLS `SET LOCAL app.organisationid` avant toute lecture/écriture | LOT 0, LOT 5 | ✅ respecté dans toutes les vues |

---

## Principe directeur

**Parcimonieux, robuste, sécure.** Ce lot ne crée pas de nouveau moteur LLM parallèle. Il s'appuie sur les briques existantes (orchestrateur, `ConversationProgress`, `TrainerKnowledgeItem`) et les étend par additions strictement délimitées.

**Trois axes de configuration distincts et non mélangés :**
- **Superadmin** → édite les blocs de prompt (`EvaluationPromptProfile`) via le backoffice Django admin. Seul niveau avec accès direct aux prompts.
- **Formateur** → configure la politique pédagogique et opérationnelle (`EvaluationPolicy`) : partage, validation, déclenchement anticipé, directives libres. Pas d'accès aux prompts.
- **Apprenant** → peut déclencher l'évaluation à tout moment (jamais bloqué), reçoit un avertissement gradué rouge/orange/vert.

L'évaluation n'est pas une note autonome. C'est un **processus dialogué** : Hugo aide l'apprenant à se positionner par rapport aux critères du parcours, avec validation humaine possible côté tuteur/formateur.

---

## Règles de sécurité du lot

```
- decisionenginev17.py, turnstatev17.py, hugoorchestrator.py, promptrenderer.py : LECTURE SEULE
- ConversationPosture, SessionMaturityLevel, KnowledgeItemStatus : import UNIQUEMENT depuis conversationprofile.py (NR-09)
- organisationid avec s partout, dans tous les modèles, filtres et helpers
- Aucun passage automatique derived_provisional → validated_trainer
- EvaluationContext ne doit contenir aucun champ P0 brut (testé par NR-P0-LOT7)
- EvaluationPromptProfile : accès en écriture SUPERADMIN uniquement
- EvaluationPolicy : accès en écriture TRAINER et ORGADMIN uniquement
- LearnerEvaluationRecord : idempotent sur (organisationid, session_id)
- Les 9 tests NR LOT 0, les 8 tests LOT 1, les 10 tests LOT 3 restent verts
```

---

## 1. Modèle Django — `EvaluationPromptProfile`

Prompts éditables en backoffice superadmin. Les profils statiques dans le code servent de **fallback** si la base est vide ou si le profil est désactivé.

```python
# backend/apps/hugo/models.py — ajouter

class EvaluationPromptProfile(models.Model):
    """
    Profil de prompt d'évaluation éditable par le superadmin en backoffice.
    ACCÈS EN ÉCRITURE : superadmin uniquement (réglé dans admin.py via has_add/change/delete_permission).
    Les formateurs n'ont pas accès à ce modèle.
    Résolution par priorité :
      1. Profil organisation actif en base (organisationid non vide)
      2. Profil global plateforme en base (organisationid = "")
      3. Fallback statique dans evaluation_profiles.py
    """
    organisationid = models.CharField(
        max_length=128, db_index=True, blank=True, default="",
        help_text="Vide = profil global plateforme. Non vide = surcharge pour cette organisation."
    )
    code = models.CharField(
        max_length=64, db_index=True,
        help_text="Identifiant du profil : 'default', 'early_trigger', 'diagnostic', etc."
    )
    label = models.CharField(max_length=128, help_text="Nom lisible du profil.")
    is_active = models.BooleanField(default=True)

    # Les trois blocs de prompt — éditables uniquement par superadmin
    prompt_frame = models.TextField(
        help_text=(
            "Cadrage du rôle d'Hugo en phase d'évaluation. "
            "Ce que Hugo fait et ne fait pas. Contraintes de posture. "
            "Ne pas mentionner les critères bruts à l'apprenant."
        )
    )
    prompt_judgement_guide = models.TextField(
        help_text=(
            "Comment interpréter les indices de la conversation. "
            "Règles pour attribuer not_covered / partial / demonstrated / mastered."
        )
    )
    prompt_output_guide = models.TextField(
        help_text=(
            "Format de sortie attendu. Structure JSON avec recap_text et items. "
            "Doit être cohérent avec le schéma LearnerEvaluationRecord.items."
        )
    )

    max_dialogue_turns = models.PositiveSmallIntegerField(
        default=6,
        help_text="Nombre maximum de tours dans le dialogue d'évaluation avant de figer le récap."
    )
    ask_learner_confirmation = models.BooleanField(
        default=True,
        help_text="Hugo demande confirmation à l'apprenant sur les points clés avant de finaliser."
    )
    human_validation_required = models.BooleanField(
        default=True,
        help_text="Indique si une validation humaine (tuteur/formateur) est attendue après."
    )

    # Traçabilité éditoriale
    updated_by = models.CharField(max_length=128, blank=True, default="")
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Profil de prompt d'évaluation"
        verbose_name_plural = "Profils de prompt d'évaluation"
        unique_together = [("organisationid", "code")]
        ordering = ["organisationid", "code"]

    def __str__(self):
        scope = self.organisationid or "plateforme"
        return f"[{scope}] {self.code} — {self.label}"
```

### 1.1 Admin Django — restriction superadmin

```python
# backend/apps/hugo/admin.py — ajouter

from django.contrib import admin
from backend.apps.hugo.models import EvaluationPromptProfile


@admin.register(EvaluationPromptProfile)
class EvaluationPromptProfileAdmin(admin.ModelAdmin):
    list_display = ["code", "organisationid", "label", "is_active", "updated_by", "updated_at"]
    list_filter = ["is_active", "organisationid"]
    search_fields = ["code", "label", "organisationid"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = [
        ("Identité", {"fields": ["organisationid", "code", "label", "is_active"]}),
        ("Prompts", {"fields": ["prompt_frame", "prompt_judgement_guide", "prompt_output_guide"]}),
        ("Paramètres", {"fields": ["max_dialogue_turns", "ask_learner_confirmation", "human_validation_required"]}),
        ("Traçabilité", {"fields": ["updated_by", "created_at", "updated_at"]}),
    ]

    def save_model(self, request, obj, form, change):
        obj.updated_by = str(request.user)
        super().save_model(request, obj, form, change)

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        # Les formateurs et orgadmin peuvent voir en lecture, pas modifier
        return request.user.is_staff or request.user.is_superuser
```

---

## 2. Modèle Django — `EvaluationPolicy`

Politique pédagogique et opérationnelle. Éditée par les formateurs/orgadmin, pas par l'apprenant.

```python
class EvaluationPolicy(models.Model):
    """
    Politique d'évaluation définie par le formateur ou orgadmin pour un parcours/groupe.
    Un seul enregistrement actif par (organisationid, group_id).
    """
    organisationid = models.CharField(max_length=128, db_index=True)  # avec s
    group_id = models.CharField(
        max_length=256, blank=True, default="",
        help_text="Vide = s'applique à toute l'organisation."
    )
    share_with_tutor = models.BooleanField(default=True)
    tutor_validation_required = models.BooleanField(default=False)
    allow_early_trigger = models.BooleanField(
        default=True,
        help_text="Autoriser l'apprenant à déclencher avant que la conversation soit GREEN."
    )
    early_trigger_warning = models.TextField(
        default=(
            "La conversation n'est pas encore suffisamment mûre. "
            "L'évaluation sera partielle."
        )
    )
    trainer_directives = models.TextField(
        blank=True, default="",
        help_text=(
            "Directives libres du formateur injectées dans le contexte d'évaluation : "
            "situations à cibler particulièrement, items critiques à ne pas rater, "
            "configurations particulières à explorer, biais à éviter."
        )
    )
    # Profil de prompt override : si renseigné, surcharge la résolution standard
    evaluation_profile_code = models.CharField(
        max_length=64, blank=True, default="",
        help_text=(
            "Code du profil de prompt à utiliser pour ce groupe. "
            "Vide = résolution automatique par la logique standard."
        )
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Politique d'évaluation"
        unique_together = [("organisationid", "group_id")]
```

---

## 3. Modèle Django — `LearnerEvaluationRecord`

L'objet persistant d'évaluation à maille fine, produit à l'issue du dialogue d'évaluation.

```python
class LearnerEvaluationRecord(models.Model):
    """
    Résultat persistant d'un cycle d'évaluation dialogué.
    Idempotent sur (organisationid, session_id) :
    une session ne peut produire qu'un seul enregistrement.
    Mise à jour possible si l'évaluation est relancée avant finalisation.
    """
    organisationid = models.CharField(max_length=128, db_index=True)  # avec s
    session_id = models.CharField(max_length=256, db_index=True)
    learner_id = models.CharField(max_length=256, db_index=True)
    group_id = models.CharField(max_length=256, blank=True, default="")

    overall_status = models.CharField(
        max_length=32,
        choices=[
            ("partial", "partial"),
            ("complete", "complete"),
            ("early_trigger", "early_trigger"),
        ],
        default="partial",
    )
    items = models.JSONField(default=list)
    # Chaque item : voir section 3.1

    recap_text = models.TextField(blank=True, default="")
    evaluation_profile_used = models.CharField(
        max_length=64, blank=True, default="",
        help_text="Code du profil de prompt utilisé pour cette évaluation."
    )

    shared_with_tutor = models.BooleanField(default=False)
    tutor_validated = models.BooleanField(null=True, blank=True)
    tutor_comment = models.TextField(blank=True, default="")
    tutor_validated_at = models.DateTimeField(null=True, blank=True)
    tutor_validated_by = models.CharField(max_length=128, blank=True, default="")

    trigger_maturity = models.CharField(
        max_length=16, default="red",
        help_text="Maturité de la conversation au moment du déclenchement : red / orange / green."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Évaluation apprenant"
        unique_together = [("organisationid", "session_id")]
```

### 3.1 Structure d'un item d'évaluation (JSONField `items`)

```json
{
  "target_item_id": "ref-item-uuid-ou-slug",
  "label": "Identifier la cause d'un dysfonctionnement",
  "content_type": "mastery_criterion",
  "positioning_level": "partial",
  "evidence_basis": "L'apprenant a mentionné une cause hypothétique sans la confirmer.",
  "confidence": 0.65,
  "missing_evidence": ["Confirmation par un second exemple", "Transfert explicite à une règle"],
  "learner_self_position": "Je pense avoir compris mais je ne suis pas sûr.",
  "status": "draft"
}
```

**Valeurs canoniques :**
- `positioning_level` : `"not_covered"` / `"partial"` / `"demonstrated"` / `"mastered"`
- `status` : `"draft"` / `"learner_confirmed"` / `"tutor_validated"` / `"tutor_rejected"`
- `confidence` : float 0.0–1.0

---

## 4. Migration Django

```python
# backend/apps/hugo/migrations/XXXX_add_lot7_evaluation.py

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("hugo", "XXXX_previous_migration"),
    ]

    operations = [
        # EvaluationPromptProfile
        migrations.CreateModel(
            name="EvaluationPromptProfile",
            fields=[
                ("id", models.AutoField(primary_key=True)),
                ("organisationid", models.CharField(max_length=128, db_index=True, blank=True, default="")),
                ("code", models.CharField(max_length=64, db_index=True)),
                ("label", models.CharField(max_length=128)),
                ("is_active", models.BooleanField(default=True)),
                ("prompt_frame", models.TextField()),
                ("prompt_judgement_guide", models.TextField()),
                ("prompt_output_guide", models.TextField()),
                ("max_dialogue_turns", models.PositiveSmallIntegerField(default=6)),
                ("ask_learner_confirmation", models.BooleanField(default=True)),
                ("human_validation_required", models.BooleanField(default=True)),
                ("updated_by", models.CharField(max_length=128, blank=True, default="")),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"verbose_name": "Profil de prompt d'évaluation"},
        ),
        migrations.AlterUniqueTogether(
            name="evaluationpromptprofile",
            unique_together={("organisationid", "code")},
        ),
        # EvaluationPolicy
        migrations.CreateModel(
            name="EvaluationPolicy",
            fields=[
                ("id", models.AutoField(primary_key=True)),
                ("organisationid", models.CharField(max_length=128, db_index=True)),
                ("group_id", models.CharField(max_length=256, blank=True, default="")),
                ("share_with_tutor", models.BooleanField(default=True)),
                ("tutor_validation_required", models.BooleanField(default=False)),
                ("allow_early_trigger", models.BooleanField(default=True)),
                ("early_trigger_warning", models.TextField(
                    default="La conversation n'est pas encore suffisamment mûre. L'évaluation sera partielle."
                )),
                ("trainer_directives", models.TextField(blank=True, default="")),
                ("evaluation_profile_code", models.CharField(max_length=64, blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"verbose_name": "Politique d'évaluation"},
        ),
        migrations.AlterUniqueTogether(
            name="evaluationpolicy",
            unique_together={("organisationid", "group_id")},
        ),
        # LearnerEvaluationRecord
        migrations.CreateModel(
            name="LearnerEvaluationRecord",
            fields=[
                ("id", models.AutoField(primary_key=True)),
                ("organisationid", models.CharField(max_length=128, db_index=True)),
                ("session_id", models.CharField(max_length=256, db_index=True)),
                ("learner_id", models.CharField(max_length=256, db_index=True)),
                ("group_id", models.CharField(max_length=256, blank=True, default="")),
                ("overall_status", models.CharField(
                    max_length=32,
                    choices=[("partial", "partial"), ("complete", "complete"), ("early_trigger", "early_trigger")],
                    default="partial",
                )),
                ("items", models.JSONField(default=list)),
                ("recap_text", models.TextField(blank=True, default="")),
                ("evaluation_profile_used", models.CharField(max_length=64, blank=True, default="")),
                ("shared_with_tutor", models.BooleanField(default=False)),
                ("tutor_validated", models.BooleanField(null=True, blank=True)),
                ("tutor_comment", models.TextField(blank=True, default="")),
                ("tutor_validated_at", models.DateTimeField(null=True, blank=True)),
                ("tutor_validated_by", models.CharField(max_length=128, blank=True, default="")),
                ("trigger_maturity", models.CharField(max_length=16, default="red")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"verbose_name": "Évaluation apprenant"},
        ),
        migrations.AlterUniqueTogether(
            name="learnerevaluationrecord",
            unique_together={("organisationid", "session_id")},
        ),
        # Champ evaluation_in_progress sur HugoSession
        migrations.AddField(
            model_name="hugosession",
            name="evaluation_in_progress",
            field=models.BooleanField(default=False),
        ),
    ]
```

---

## 5. Profils statiques fallback — `evaluation_profiles.py`

Ces profils sont utilisés si aucun `EvaluationPromptProfile` actif n'est trouvé en base.

```python
# backend/apps/hugo/domain/evaluation_profiles.py

from __future__ import annotations
from typing import Optional

# Profils statiques — fallback sûr si la base est vide ou si le profil est désactivé
EVALUATION_PROFILES_STATIC = {
    "default": {
        "name": "default",
        "max_dialogue_turns": 6,
        "prompt_frame": (
            "Tu es en phase d'évaluation réflexive avec l'apprenant. "
            "Ton rôle est de l'aider à se positionner par rapport aux critères du parcours, "
            "pas de le noter unilatéralement. "
            "Tu ne poses pas de questions sur des sujets déjà clarifiés dans la conversation. "
            "Tu t'appuies uniquement sur les éléments de la conversation et les critères fournis. "
            "Tu ne révèles pas les critères bruts à l'apprenant, mais tu les utilises pour orienter "
            "tes questions de positionnement."
        ),
        "prompt_judgement_guide": (
            "Pour chaque critère, cherche dans la conversation des indices de maîtrise : "
            "description concrète d'une action liée au critère, identification d'une cause ou règle, "
            "formulation d'un transfert futur. "
            "Si l'indice est présent mais partiel, note 'partial'. "
            "Si l'indice est absent, note 'not_covered'. "
            "Si l'indice est complet et confirmé par l'apprenant, note 'demonstrated'."
        ),
        "prompt_output_guide": (
            "À la fin du dialogue, produis un JSON structuré avec : "
            "recap_text (string narratif bref), "
            "items (liste d'objets avec target_item_id, label, positioning_level, "
            "evidence_basis, confidence, missing_evidence, learner_self_position, status). "
            "Avant de finaliser, demande confirmation à l'apprenant sur un ou deux points clés."
        ),
        "ask_learner_confirmation": True,
        "human_validation_required": True,
    },
    "early_trigger": {
        "name": "early_trigger",
        "max_dialogue_turns": 4,
        "prompt_frame": (
            "L'apprenant a déclenché l'évaluation avant que la conversation soit suffisamment mûre. "
            "Informe-le que l'évaluation sera partielle, et aide-le à se positionner sur les éléments "
            "déjà explorés. Ne l'incite pas à conclure sur des points non couverts."
        ),
        "prompt_judgement_guide": (
            "Limite-toi aux critères pour lesquels des indices existent dans la conversation. "
            "Marque explicitement 'not_covered' les critères non abordés."
        ),
        "prompt_output_guide": (
            "Produis un JSON partiel. overall_status = 'early_trigger'. "
            "Indique clairement dans recap_text que l'évaluation est partielle."
        ),
        "ask_learner_confirmation": True,
        "human_validation_required": True,
    },
    "diagnostic": {
        "name": "diagnostic",
        "max_dialogue_turns": 5,
        "prompt_frame": (
            "Tu es en phase d'évaluation diagnostique. "
            "L'objectif est d'identifier les acquis et les lacunes, pas de valider une performance finale. "
            "Sois factuel, non jugeant, orienté vers l'identification des points à renforcer."
        ),
        "prompt_judgement_guide": (
            "Cherche principalement les indices de compréhension causale et de maîtrise des procédures. "
            "Un critère est 'partial' si l'apprenant a une intuition juste mais pas encore de formulation solide."
        ),
        "prompt_output_guide": (
            "Produis un JSON structuré. Inclure un champ 'missing_evidence' pour chaque item. "
            "Le recap_text doit identifier 2-3 priorités de renforcement."
        ),
        "ask_learner_confirmation": False,
        "human_validation_required": True,
    },
}


def get_evaluation_profile(
    organisationid: str = "",
    group_id: str = "",
    code: str = "default",
    is_early_trigger: bool = False,
) -> dict:
    """
    Résolution du profil de prompt d'évaluation.
    Priorité :
    1. EvaluationPromptProfile en base pour cette organisation (organisationid non vide, code)
    2. EvaluationPromptProfile en base global plateforme (organisationid = "", code)
    3. Fallback statique selon code ou is_early_trigger

    Le code est déterminé par :
    - EvaluationPolicy.evaluation_profile_code si renseigné
    - "early_trigger" si is_early_trigger
    - "default" sinon
    """
    from backend.apps.hugo.models import EvaluationPromptProfile

    effective_code = code
    if is_early_trigger and not code:
        effective_code = "early_trigger"
    if not effective_code:
        effective_code = "default"

    # 1. Profil organisation
    if organisationid:
        try:
            db_profile = EvaluationPromptProfile.objects.get(
                organisationid=organisationid,
                code=effective_code,
                is_active=True,
            )
            return _db_profile_to_dict(db_profile)
        except EvaluationPromptProfile.DoesNotExist:
            pass

    # 2. Profil global plateforme
    try:
        db_profile = EvaluationPromptProfile.objects.get(
            organisationid="",
            code=effective_code,
            is_active=True,
        )
        return _db_profile_to_dict(db_profile)
    except EvaluationPromptProfile.DoesNotExist:
        pass

    # 3. Fallback statique
    return EVALUATION_PROFILES_STATIC.get(
        effective_code,
        EVALUATION_PROFILES_STATIC["default"]
    )


def _db_profile_to_dict(db_profile) -> dict:
    """Convertit un EvaluationPromptProfile Django en dict compatible avec le service."""
    return {
        "name": db_profile.code,
        "max_dialogue_turns": db_profile.max_dialogue_turns,
        "prompt_frame": db_profile.prompt_frame,
        "prompt_judgement_guide": db_profile.prompt_judgement_guide,
        "prompt_output_guide": db_profile.prompt_output_guide,
        "ask_learner_confirmation": db_profile.ask_learner_confirmation,
        "human_validation_required": db_profile.human_validation_required,
    }
```

---

## 6. Domaine — `EvaluationWorkflowEngine`

```python
# backend/apps/hugo/services/evaluation_workflow_engine.py

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from backend.apps.hugo.domain.conversationprofile import (
    ConversationProgress, SessionMaturityLevel
)


@dataclass
class EvaluationContext:
    """
    Contexte assemblé avant d'entrer dans le dialogue d'évaluation.
    Réunit les trois sources : conversation, référentiel, connaissances formateur.
    Règle : aucun champ P0 brut ici (testé par NR-P0-LOT7).
    """
    session_id: str
    conversation_evidence: list = field(default_factory=list)
    # Liste d'indices issus de la conversation (branches, maturité, reason_codes)
    referential_items: list = field(default_factory=list)
    # Items du référentiel ciblés par ce parcours/groupe
    trainer_knowledge_items: list = field(default_factory=list)
    # TrainerKnowledgeItem validés pertinents
    trainer_directives: str = ""
    # Texte libre de directives formateur
    maturity_at_trigger: SessionMaturityLevel = SessionMaturityLevel.RED
    is_early_trigger: bool = False


def assemble_evaluation_context(
    session,
    progress: ConversationProgress,
    policy,
    referential_items: list,
    trainer_knowledge_items: list,
) -> EvaluationContext:
    """Assemble le contexte d'évaluation depuis les sources disponibles. Ne modifie aucun état."""
    evidence = []
    for branch in progress.active_branches:
        evidence.append({
            "branch_id": branch.branch_id,
            "theme": branch.theme_label,
            "objective": branch.objective_label,
            "maturity": branch.exploration_level.value,
            "reason_codes": branch.reason_codes,
        })

    return EvaluationContext(
        session_id=str(session.id),
        conversation_evidence=evidence,
        referential_items=referential_items,
        trainer_knowledge_items=trainer_knowledge_items,
        trainer_directives=getattr(policy, "trainer_directives", ""),
        maturity_at_trigger=progress.overall_maturity,
        is_early_trigger=(progress.overall_maturity != SessionMaturityLevel.GREEN),
    )
```

---

## 7. Service d'évaluation — `EvaluationService`

```python
# backend/apps/hugo/services/evaluation_service.py

from __future__ import annotations
from typing import Optional
from django.utils import timezone

from backend.apps.hugo.domain.conversationprofile import (
    ConversationProgress, SessionMaturityLevel
)
from backend.apps.hugo.domain.evaluation_profiles import get_evaluation_profile
from backend.apps.hugo.services.evaluation_workflow_engine import (
    assemble_evaluation_context, EvaluationContext
)
from backend.apps.hugo.models import LearnerEvaluationRecord, EvaluationPolicy


def get_or_create_policy(organisationid: str, group_id: str = "") -> EvaluationPolicy:
    policy, _ = EvaluationPolicy.objects.get_or_create(
        organisationid=organisationid,
        group_id=group_id,
        defaults={
            "share_with_tutor": True,
            "tutor_validation_required": False,
            "allow_early_trigger": True,
        }
    )
    return policy


def resolve_evaluation_readiness(progress: ConversationProgress) -> dict:
    """
    Détermine l'état rouge/orange/vert du déclenchement.
    can_trigger est TOUJOURS True : l'apprenant n'est jamais bloqué.
    """
    maturity = progress.overall_maturity
    if maturity == SessionMaturityLevel.GREEN:
        return {"trigger_state": "green", "message": None, "can_trigger": True}
    elif maturity == SessionMaturityLevel.ORANGE:
        return {
            "trigger_state": "orange",
            "message": "La conversation est explorable mais incomplète. L'évaluation sera partielle.",
            "can_trigger": True,
        }
    else:
        return {
            "trigger_state": "red",
            "message": (
                "La conversation n'a pas encore suffisamment exploré la situation. "
                "L'évaluation sera très partielle."
            ),
            "can_trigger": True,
        }


def build_evaluation_prompt(
    context: EvaluationContext,
    profile: dict,
    conversation_history: list,
) -> str:
    """Construit le prompt de démarrage du dialogue d'évaluation."""
    lines = [profile["prompt_frame"], ""]

    if context.trainer_directives:
        lines += ["DIRECTIVES FORMATEUR :", context.trainer_directives, ""]

    lines += ["CRITÈRES D'ÉVALUATION CIBLÉS :"]
    for item in context.referential_items:
        lines.append(f"- [{item.get('id', '')}] {item.get('label', '')}")
    lines.append("")

    if context.trainer_knowledge_items:
        lines += ["CONNAISSANCES FORMATEUR VALIDÉES PERTINENTES :"]
        for ki in context.trainer_knowledge_items:
            lines.append(f"- ({ki.get('content_type', '')}) {ki.get('content', '')[:200]}")
        lines.append("")

    lines += ["INDICES DE LA CONVERSATION :"]
    for ev in context.conversation_evidence:
        lines.append(
            f"- Thème {ev['theme']} / Objectif {ev['objective']} : maturité {ev['maturity']}"
        )
    lines.append("")

    lines += [profile["prompt_judgement_guide"], ""]
    lines += [profile["prompt_output_guide"], ""]

    if context.is_early_trigger:
        lines += [
            "ATTENTION : L'apprenant a déclenché l'évaluation avant la fin recommandée. "
            "L'évaluation est partielle. Informe-le clairement.",
            "",
        ]

    lines += [
        "HISTORIQUE DE LA CONVERSATION (derniers tours pertinents) :",
        "\n".join(
            f"[{m.get('role', '?')}] {m.get('content', '')[:300]}"
            for m in conversation_history[-10:]
        ),
    ]

    return "\n".join(lines)


def save_evaluation_record(
    session,
    organisationid: str,
    progress: ConversationProgress,
    llm_output: dict,
    policy: EvaluationPolicy,
    profile_code: str = "default",
) -> LearnerEvaluationRecord:
    """
    Persiste le LearnerEvaluationRecord.
    Idempotent sur (organisationid, session_id) : update_or_create.
    """
    is_early = (progress.overall_maturity != SessionMaturityLevel.GREEN)
    overall_status = "early_trigger" if is_early else llm_output.get("overall_status", "complete")

    record, _ = LearnerEvaluationRecord.objects.update_or_create(
        organisationid=organisationid,
        session_id=str(session.id),
        defaults={
            "learner_id": str(getattr(session, "learner_id", session.id)),
            "group_id": getattr(session, "group_id", "") or "",
            "overall_status": overall_status,
            "items": llm_output.get("items", []),
            "recap_text": llm_output.get("recap_text", ""),
            "evaluation_profile_used": profile_code,
            "shared_with_tutor": policy.share_with_tutor,
            "trigger_maturity": progress.overall_maturity.value,
        }
    )
    return record
```

---

## 8. Endpoints

### 8.1 `evaluation-readiness` — état du bouton (GET)

```python
# backend/apps/hugo/views/sessions.py — ajouter dans le ViewSet

@action(detail=True, methods=["get"], url_path="evaluation-readiness")
def get_evaluation_readiness(self, request, pk=None):
    from backend.apps.hugo.services.evaluation_service import resolve_evaluation_readiness
    from backend.apps.hugo.services.conversation_progress_calculator import deserialize_conversation_progress

    session = self.get_object()
    raw = getattr(session, "conversation_progress", None)
    progress = deserialize_conversation_progress(raw)

    if progress is None:
        return Response({
            "trigger_state": "red",
            "message": "Aucune progression calculée pour cette session.",
            "can_trigger": True,
        })

    return Response(resolve_evaluation_readiness(progress))
```

### 8.2 `request-evaluation` — déclenchement (POST)

```python
@action(detail=True, methods=["post"], url_path="request-evaluation")
def request_evaluation(self, request, pk=None):
    from backend.apps.hugo.services.conversation_progress_calculator import deserialize_conversation_progress
    from backend.apps.hugo.services.evaluation_service import (
        get_or_create_policy, resolve_evaluation_readiness, build_evaluation_prompt,
    )
    from backend.apps.hugo.services.evaluation_workflow_engine import assemble_evaluation_context
    from backend.apps.hugo.domain.evaluation_profiles import get_evaluation_profile
    from backend.apps.hugo.services.llm_client import call_llm
    from backend.apps.hugo.domain.conversationprofile import KnowledgeItemStatus
    from backend.apps.hugo.models import TrainerKnowledgeItem, ConversationTurn

    session = self.get_object()
    organisationid = getattr(request.user, "organisationid", "")

    raw = getattr(session, "conversation_progress", None)
    progress = deserialize_conversation_progress(raw)
    if progress is None:
        return Response({"error": "no_progress"}, status=400)

    group_id = getattr(session, "group_id", "") or ""
    policy = get_or_create_policy(organisationid=organisationid, group_id=group_id)
    readiness = resolve_evaluation_readiness(progress)
    is_early = (readiness["trigger_state"] != "green")

    # Résolution du code de profil
    profile_code = policy.evaluation_profile_code or ("early_trigger" if is_early else "default")
    profile = get_evaluation_profile(
        organisationid=organisationid,
        group_id=group_id,
        code=profile_code,
        is_early_trigger=is_early,
    )

    # Référentiel (à adapter selon implémentation réelle)
    referential_items = list(getattr(session, "referential_items", None) or [])

    # TrainerKnowledgeItems validés
    trainer_items = list(
        TrainerKnowledgeItem.objects.filter(
            organisationid=organisationid,
            status=KnowledgeItemStatus.VALIDATED_TRAINER.value,
        ).values("id", "content", "content_type", "referential_item_id")[:30]
    )

    # Historique conversation
    history = list(
        ConversationTurn.objects.filter(session_id=session.id)
        .order_by("created_at")
        .values("role", "content")[-20:]
    )

    context = assemble_evaluation_context(
        session=session,
        progress=progress,
        policy=policy,
        referential_items=referential_items,
        trainer_knowledge_items=trainer_items,
    )

    prompt = build_evaluation_prompt(context, profile, history)
    llm_response = call_llm(session, prompt)

    session.evaluation_in_progress = True
    session.save(update_fields=["evaluation_in_progress"])

    return Response({
        "evaluation_started": True,
        "trigger_state": readiness["trigger_state"],
        "warning": readiness.get("message"),
        "first_message": llm_response.get("text", ""),
        "profile_name": profile["name"],
        "max_dialogue_turns": profile["max_dialogue_turns"],
    })
```

### 8.3 `finalize-evaluation` — persistance (POST)

```python
@action(detail=True, methods=["post"], url_path="finalize-evaluation")
def finalize_evaluation(self, request, pk=None):
    from backend.apps.hugo.services.conversation_progress_calculator import deserialize_conversation_progress
    from backend.apps.hugo.services.evaluation_service import get_or_create_policy, save_evaluation_record

    session = self.get_object()
    organisationid = getattr(request.user, "organisationid", "")

    raw = getattr(session, "conversation_progress", None)
    progress = deserialize_conversation_progress(raw)
    if progress is None:
        return Response({"error": "no_progress"}, status=400)

    llm_output = request.data.get("evaluation_output", {})
    if not llm_output:
        return Response({"error": "evaluation_output_required"}, status=400)

    group_id = getattr(session, "group_id", "") or ""
    policy = get_or_create_policy(organisationid=organisationid, group_id=group_id)
    profile_code = policy.evaluation_profile_code or "default"

    record = save_evaluation_record(
        session=session,
        organisationid=organisationid,
        progress=progress,
        llm_output=llm_output,
        policy=policy,
        profile_code=profile_code,
    )

    session.evaluation_in_progress = False
    session.save(update_fields=["evaluation_in_progress"])

    return Response({
        "evaluation_record_id": str(record.id),
        "overall_status": record.overall_status,
        "shared_with_tutor": record.shared_with_tutor,
        "tutor_validation_required": policy.tutor_validation_required,
        "items_count": len(record.items),
        "evaluation_profile_used": record.evaluation_profile_used,
    })
```

### 8.4 Vue formateur — `evaluation-records` et actions (GET/POST)

```python
# backend/apps/hugo/views/trainer.py — ajouter

from django.http import JsonResponse
from django.utils import timezone
from backend.apps.hugo.models import LearnerEvaluationRecord


def get_evaluation_records(request):
    """Vue formateur : liste consolidée des évaluations de ses apprenants."""
    organisationid = getattr(request.user, "organisationid", "")
    group_id = request.GET.get("group_id", "")
    status_filter = request.GET.get("status", "")

    qs = LearnerEvaluationRecord.objects.filter(organisationid=organisationid)
    if group_id:
        qs = qs.filter(group_id=group_id)
    if status_filter:
        qs = qs.filter(overall_status=status_filter)

    records = list(qs.order_by("-created_at").values(
        "id", "session_id", "learner_id", "group_id",
        "overall_status", "recap_text", "items",
        "shared_with_tutor", "tutor_validated", "tutor_comment",
        "trigger_maturity", "evaluation_profile_used", "created_at"
    ))
    return JsonResponse({"records": records, "total": len(records)})


def validate_evaluation_record(request, record_id):
    """Tuteur ou formateur valide / rejette / commente une évaluation."""
    import json
    organisationid = getattr(request.user, "organisationid", "")

    try:
        record = LearnerEvaluationRecord.objects.get(
            id=record_id, organisationid=organisationid
        )
    except LearnerEvaluationRecord.DoesNotExist:
        return JsonResponse({"error": "not_found"}, status=404)

    body = json.loads(request.body)
    action = body.get("action")  # "validate" | "reject" | "comment"
    comment = body.get("comment", "")

    if action == "validate":
        record.tutor_validated = True
        record.tutor_comment = comment
        record.tutor_validated_at = timezone.now()
        record.tutor_validated_by = str(request.user.id)
        for item in record.items:
            if item.get("status") == "draft":
                item["status"] = "tutor_validated"
        record.save()
        return JsonResponse({"status": "validated"})
    elif action == "reject":
        record.tutor_validated = False
        record.tutor_comment = comment
        record.tutor_validated_at = timezone.now()
        record.tutor_validated_by = str(request.user.id)
        record.save()
        return JsonResponse({"status": "rejected"})
    elif action == "comment":
        record.tutor_comment = comment
        record.save()
        return JsonResponse({"status": "commented"})

    return JsonResponse({"error": "action_inconnue"}, status=400)


def export_evaluation_records(request):
    """Export JSON ou CSV vers application tierce."""
    import csv
    from io import StringIO
    from django.http import HttpResponse

    organisationid = getattr(request.user, "organisationid", "")
    fmt = request.GET.get("format", "json")
    group_id = request.GET.get("group_id", "")

    qs = LearnerEvaluationRecord.objects.filter(
        organisationid=organisationid, shared_with_tutor=True
    )
    if group_id:
        qs = qs.filter(group_id=group_id)

    if fmt == "csv":
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "session_id", "learner_id", "group_id", "overall_status",
            "trigger_maturity", "recap_text", "items_count",
            "evaluation_profile_used", "tutor_validated", "created_at"
        ])
        for r in qs:
            writer.writerow([
                r.session_id, r.learner_id, r.group_id, r.overall_status,
                r.trigger_maturity, r.recap_text[:200], len(r.items),
                r.evaluation_profile_used, r.tutor_validated,
                r.created_at.isoformat()
            ])
        response = HttpResponse(output.getvalue(), content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=evaluations.csv"
        return response

    records = list(qs.values(
        "session_id", "learner_id", "group_id", "overall_status",
        "recap_text", "items", "trigger_maturity", "evaluation_profile_used",
        "tutor_validated", "tutor_comment", "created_at"
    ))
    return JsonResponse({"records": records})
```

---

## 9. Front — Bouton de déclenchement rouge/orange/vert

```javascript
// frontend/src/components/EvaluationTriggerButton.jsx

async function fetchEvaluationReadiness(sessionId) {
  try {
    const res = await fetch(`/api/hugo/sessions/${sessionId}/evaluation-readiness/`);
    if (!res.ok) return { trigger_state: "red", message: null, can_trigger: true };
    return await res.json();
  } catch {
    return { trigger_state: "red", message: null, can_trigger: true };
  }
}

const BUTTON_STYLES = {
  green:  { label: "Évaluation recommandée",  cssClass: "eval-btn--green" },
  orange: { label: "Évaluation possible",     cssClass: "eval-btn--orange" },
  red:    { label: "Évaluation prématurée",   cssClass: "eval-btn--red" },
};

// Logique d'affichage :
// 1. Au montage du composant : appeler fetchEvaluationReadiness
// 2. Colorer le bouton selon trigger_state (vert / orange / rouge)
// 3. Afficher le message d'avertissement si présent
// 4. Sur clic : appeler POST /api/hugo/sessions/{id}/request-evaluation/
//    puis afficher le premier message du dialogue dans la fenêtre de conversation
// 5. Sur clic "finaliser" : appeler POST /api/hugo/sessions/{id}/finalize-evaluation/
//    avec { evaluation_output: { recap_text, items, overall_status } }
```

### Intégration dans `UIState` (patch LOT 1)

Ajouter deux champs à `UIState` dans `conversationprofile.py` :

```python
# backend/apps/hugo/domain/conversationprofile.py
# Dans la dataclass UIState — ajouter APRÈS les champs existants :

evaluation_trigger_state: str = "red"  # "red" | "orange" | "green"
evaluation_trigger_message: Optional[str] = None
```

Mettre à jour `build_ui_state_from_progress` dans `conversation_progress_calculator.py` :

```python
# Dans build_ui_state_from_progress — ajouter à la fin, avant le return :
from backend.apps.hugo.services.evaluation_service import resolve_evaluation_readiness
readiness = resolve_evaluation_readiness(progress)

return UIState(
    # ... tous les champs existants inchangés ...
    evaluation_trigger_state=readiness["trigger_state"],
    evaluation_trigger_message=readiness.get("message"),
)
```

**Attention** : vérifier que le test NR-07 ne casse pas. `evaluation_trigger_state` et `evaluation_trigger_message` ne sont pas des champs P0 ; ils ne doivent pas figurer dans `P0_CORE_FIELDS`. C'est le cas — ces champs sont nouveaux et ne figurent nulle part dans `turn_state_v17.py` ou `decision_engine_v17.py`.

---

## 10. Tests — `test_evaluation_workflow.py`

```python
# backend/apps/hugo/tests/test_evaluation_workflow.py

import pytest
import dataclasses
from backend.apps.hugo.domain.conversationprofile import (
    ConversationProgress, ConversationPosture, SessionMaturityLevel, ConversationBranch
)
from backend.apps.hugo.services.evaluation_service import resolve_evaluation_readiness
from backend.apps.hugo.domain.evaluation_profiles import (
    get_evaluation_profile, EVALUATION_PROFILES_STATIC
)
from backend.apps.hugo.services.evaluation_workflow_engine import EvaluationContext


def make_progress(maturity: SessionMaturityLevel) -> ConversationProgress:
    return ConversationProgress(
        session_id="s1",
        posture=ConversationPosture.REFLECTIVE_AFEST,
        active_branches=[
            ConversationBranch(
                branch_id="b1",
                theme_label="situation_travail",
                objective_label="analyser_cause",
                exploration_level=maturity,
                is_active=True,
            )
        ],
        overall_maturity=maturity,
        evaluation_eligible=(maturity == SessionMaturityLevel.GREEN),
    )


# --- Tests de déclenchement ---

def test_green_trigger_state():
    result = resolve_evaluation_readiness(make_progress(SessionMaturityLevel.GREEN))
    assert result["trigger_state"] == "green"
    assert result["can_trigger"] is True
    assert result["message"] is None


def test_orange_trigger_state():
    result = resolve_evaluation_readiness(make_progress(SessionMaturityLevel.ORANGE))
    assert result["trigger_state"] == "orange"
    assert result["can_trigger"] is True
    assert result["message"] is not None


def test_red_trigger_state_never_blocks():
    result = resolve_evaluation_readiness(make_progress(SessionMaturityLevel.RED))
    assert result["trigger_state"] == "red"
    assert result["can_trigger"] is True  # jamais bloqué


# --- Tests des profils ---

def test_early_trigger_profile_selected():
    profile = get_evaluation_profile(is_early_trigger=True)
    assert profile["name"] == "early_trigger"
    assert profile["max_dialogue_turns"] <= 4


def test_default_profile_selected():
    profile = get_evaluation_profile(is_early_trigger=False, code="default")
    assert profile["name"] == "default"
    assert profile["human_validation_required"] is True
    assert profile["ask_learner_confirmation"] is True


def test_diagnostic_profile_selected():
    profile = get_evaluation_profile(code="diagnostic", is_early_trigger=False)
    assert profile["name"] == "diagnostic"


def test_unknown_profile_falls_back_to_default():
    profile = get_evaluation_profile(code="inexistant_profile", is_early_trigger=False)
    assert profile["name"] == "default"


def test_static_profiles_have_required_keys():
    required_keys = {
        "name", "max_dialogue_turns", "prompt_frame",
        "prompt_judgement_guide", "prompt_output_guide",
        "ask_learner_confirmation", "human_validation_required"
    }
    for code, profile in EVALUATION_PROFILES_STATIC.items():
        for key in required_keys:
            assert key in profile, f"Clé manquante '{key}' dans profil statique '{code}'"


# --- Tests du modèle EvaluationContext ---

def test_nr_p0_fields_not_in_evaluation_context():
    """
    NR-P0-LOT7 : EvaluationContext ne doit exposer aucun champ P0 brut.
    Cohérent avec NR-07 (UIState) — même principe appliqué au domaine évaluation.
    """
    P0_FIELDS = {
        "has_concrete_actions", "episode_clarity", "problem_salience",
        "reflection_phase", "affect_valence", "cognitive_load",
        "interaction_risk", "session_phase", "session_maturity",
        "evidence_strength", "covered_points", "remaining_open_points",
        "loop_risk",
    }
    context_fields = {f.name for f in dataclasses.fields(EvaluationContext)}
    overlap = context_fields & P0_FIELDS
    assert not overlap, f"EvaluationContext expose des champs P0 interdits : {overlap}"


# --- Tests du service de persistance ---

def test_evaluation_policy_defaults(db):
    from backend.apps.hugo.services.evaluation_service import get_or_create_policy
    policy = get_or_create_policy(organisationid="org-test")
    assert policy.share_with_tutor is True
    assert policy.tutor_validation_required is False
    assert policy.allow_early_trigger is True


def test_save_evaluation_record_idempotent(db):
    from backend.apps.hugo.models import HugoSession, LearnerEvaluationRecord
    from backend.apps.hugo.services.evaluation_service import save_evaluation_record, get_or_create_policy

    session = HugoSession.objects.create(organisationid="org-test")
    progress = make_progress(SessionMaturityLevel.GREEN)
    policy = get_or_create_policy(organisationid="org-test")
    llm_output = {
        "recap_text": "L'apprenant a bien identifié la cause.",
        "items": [{"target_item_id": "ref-1", "label": "Identifier la cause", "positioning_level": "demonstrated"}],
        "overall_status": "complete",
    }

    record1 = save_evaluation_record(session, "org-test", progress, llm_output, policy)
    record2 = save_evaluation_record(session, "org-test", progress, llm_output, policy)
    assert record1.id == record2.id
    assert LearnerEvaluationRecord.objects.filter(session_id=str(session.id)).count() == 1


def test_evaluation_record_items_structure(db):
    from backend.apps.hugo.models import HugoSession
    from backend.apps.hugo.services.evaluation_service import save_evaluation_record, get_or_create_policy

    session = HugoSession.objects.create(organisationid="org-test")
    progress = make_progress(SessionMaturityLevel.GREEN)
    policy = get_or_create_policy(organisationid="org-test")
    llm_output = {
        "recap_text": "Récap test",
        "items": [{
            "target_item_id": "ref-1",
            "label": "Identifier la cause",
            "positioning_level": "partial",
            "evidence_basis": "Mention d'une cause hypothétique.",
            "confidence": 0.6,
            "missing_evidence": ["Confirmation"],
            "learner_self_position": "Je pense mais je ne suis pas sûr.",
            "status": "draft",
        }],
        "overall_status": "complete",
    }
    record = save_evaluation_record(session, "org-test", progress, llm_output, policy)
    assert len(record.items) == 1
    item = record.items[0]
    required_item_keys = {
        "target_item_id", "label", "positioning_level",
        "evidence_basis", "confidence", "missing_evidence",
        "learner_self_position", "status"
    }
    for key in required_item_keys:
        assert key in item, f"Clé manquante '{key}' dans item d'évaluation"


# --- Test de résolution DB vs fallback statique ---

def test_db_profile_overrides_static_fallback(db):
    """Vérifier que le profil en base prend la priorité sur le statique."""
    from backend.apps.hugo.models import EvaluationPromptProfile
    from backend.apps.hugo.domain.evaluation_profiles import get_evaluation_profile

    EvaluationPromptProfile.objects.create(
        organisationid="",
        code="default",
        label="Profil test",
        is_active=True,
        prompt_frame="Mon prompt_frame personnalisé",
        prompt_judgement_guide="Mon guide",
        prompt_output_guide="Mon output guide",
        max_dialogue_turns=8,
        ask_learner_confirmation=True,
        human_validation_required=True,
    )
    profile = get_evaluation_profile(code="default", is_early_trigger=False)
    assert profile["prompt_frame"] == "Mon prompt_frame personnalisé"
    assert profile["max_dialogue_turns"] == 8


def test_db_org_profile_overrides_global(db):
    """Vérifier que le profil organisation prend la priorité sur le profil global."""
    from backend.apps.hugo.models import EvaluationPromptProfile
    from backend.apps.hugo.domain.evaluation_profiles import get_evaluation_profile

    EvaluationPromptProfile.objects.create(
        organisationid="", code="default", label="Global",
        is_active=True, prompt_frame="global",
        prompt_judgement_guide="g", prompt_output_guide="g",
    )
    EvaluationPromptProfile.objects.create(
        organisationid="org-A", code="default", label="Org A",
        is_active=True, prompt_frame="org-A-specifique",
        prompt_judgement_guide="a", prompt_output_guide="a",
    )
    profile_a = get_evaluation_profile(
        organisationid="org-A", code="default", is_early_trigger=False
    )
    profile_other = get_evaluation_profile(
        organisationid="org-B", code="default", is_early_trigger=False
    )
    assert profile_a["prompt_frame"] == "org-A-specifique"
    assert profile_other["prompt_frame"] == "global"
```

---

## 11. Checklist de sortie du LOT 7

**Modèles et migrations :**
- [ ] `EvaluationPromptProfile` créé, migration appliquée
- [ ] `EvaluationPolicy` créé, migration appliquée
- [ ] `LearnerEvaluationRecord` créé, migration appliquée
- [ ] Champ `evaluation_in_progress` sur `HugoSession`, migration appliquée
- [ ] `organisationid` avec `s` dans tous les modèles, filtres et helpers

**Contrôle d'accès :**
- [ ] `EvaluationPromptProfileAdmin` : `has_add/change/delete_permission` limité à `is_superuser`
- [ ] `EvaluationPolicy` : accès formateur/orgadmin uniquement (pas d'écriture apprenant)
- [ ] `LearnerEvaluationRecord` : filtré par `organisationid` dans toutes les vues

**Profils et résolution :**
- [ ] Résolution DB → org → global → fallback statique fonctionne (tests `test_db_profile_overrides_static_fallback` et `test_db_org_profile_overrides_global` verts)
- [ ] Profil inconnu retombe sur `default`
- [ ] Tous les profils statiques contiennent les 7 clés requises

**Compatibilité lots précédents :**
- [ ] Les 9 tests NR LOT 0 restent verts
- [ ] Les 8 tests LOT 1 restent verts
- [ ] Les 10 tests LOT 3 restent verts
- [ ] `KnowledgeItemStatus` importé depuis `conversationprofile.py` (NR-09)
- [ ] `EvaluationContext` ne contient aucun champ P0 brut (NR-P0-LOT7 vert)
- [ ] `decisionenginev17.py`, `turnstatev17.py`, `hugoorchestrator.py` non modifiés
- [ ] `tutorprofiles.py` et `synthesisservice.py` non modifiés
- [ ] `UIState` enrichi de `evaluation_trigger_state` et `evaluation_trigger_message` sans casser NR-07

**Endpoints et comportement :**
- [ ] `evaluation-readiness` retourne rouge/orange/vert, `can_trigger = True` toujours
- [ ] `request-evaluation` déclenche le dialogue, retourne `first_message`
- [ ] `finalize-evaluation` persiste `LearnerEvaluationRecord` de manière idempotente
- [ ] Un enregistrement au maximum par `(organisationid, session_id)`
- [ ] Vue formateur filtre par `group_id` et `organisationid`
- [ ] Endpoint de validation tuteur (validate / reject / comment) opérationnel
- [ ] Export CSV/JSON opérationnel
- [ ] Champ `evaluation_profile_used` renseigné dans `LearnerEvaluationRecord`

**Tests :**
- [ ] Les 12 tests `test_evaluation_workflow.py` passent

---

## 12. Ce qui est volontairement hors périmètre de ce lot

Les éléments suivants sont hors scope pour rester parcimonieux :

1. **Interface UI formateur pour configurer `EvaluationPolicy`** — backend prêt, l'interface sera branchée dans un lot UI ultérieur
2. **Édition des `EvaluationPromptProfile` par une interface autre que Django admin** — Django admin superadmin suffit pour le POC
3. **Webhook/push sortant vers application tierce** — l'export CSV/JSON suffit pour le POC
4. **Scoring numérique** — volontairement absent, l'évaluation est qualitative
5. **Évaluation multi-sessions consolidée** — vue formateur par apprenant sur plusieurs sessions, lot ultérieur
6. **Notifications push tuteur** — tuteur consulte sur demande dans le POC

