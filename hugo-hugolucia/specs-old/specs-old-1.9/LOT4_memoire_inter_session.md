# LOT 4 — Mémoire thématique inter-session (V1)

**Durée estimée :** 4–5 jours  
**Risque :** modéré — nouveau modèle Django + logique de consolidation  
**Dépendance :** LOT 3 checklist verte

---

## Objectif

Poser une mémoire thématique structurée, gouvernée côté backend, qui survive à la fin de la
conversation et sert aux séances suivantes. Cette V1 se limite aux thèmes, acquis, points fragiles
et rattachements au référentiel.

---

## Règle de sécurité du lot

- Aucune mémoire de texte brut verbatim en base principale.
- Aucune recréation d'une mémoire "totale" ou de type RAG.
- `KnowledgeItemStatus` importé depuis `conversation_profile.py` (NR-09).
- Le champ RLS s'appelle `organisation_id` (avec s, SPEC v1.5 section 13).
- La consolidation est strictement **post-conversation** — jamais pendant le tour.
- Convention stricte `KnowledgeItemStatus` :
  - en base Django : stockage sous forme de string `.value`
  - en code métier : manipulation sous forme d'enum `KnowledgeItemStatus(...)`
  - avant sauvegarde : réécriture explicite en `.value`

---

## Nouveau modèle Django

```python
# backend/apps/hugo/models.py — ajouter à la suite des modèles existants

from django.db import models
from backend.apps.hugo.domain.conversation_profile import KnowledgeItemStatus


class LearnerThemeMemory(models.Model):
    """
    Mémoire thématique persistante par apprenant + thème.
    Créée / mise à jour à chaque consolidation post-conversation.
    Un seul enregistrement par couple (learner_id, theme_key, organisation_id).
    """
    learner_id      = models.CharField(max_length=128, db_index=True)
    organisation_id = models.CharField(max_length=128, db_index=True)   # SPEC v1.5 s. 13
    theme_key       = models.CharField(max_length=256, db_index=True)
    referential_item_id = models.CharField(max_length=256, blank=True, default="")
    stabilised_points   = models.JSONField(default=list)   # ["action_concrète_décrite", ...]
    open_loops          = models.JSONField(default=list)
    persistent_difficulties = models.JSONField(default=list)
    knowledge_status    = models.CharField(
        max_length=32,
        choices=[(s.value, s.value) for s in KnowledgeItemStatus],
        default=KnowledgeItemStatus.DECLARED.value,
    )
    last_conversation_id = models.CharField(max_length=128, blank=True, default="")
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("learner_id", "organisation_id", "theme_key")]
        verbose_name = "Mémoire thématique apprenant"

    def __str__(self):
        return f"{self.learner_id} / {self.theme_key}"
```

---

## Migration

```python
# backend/apps/hugo/migrations/XXXX_add_learner_theme_memory.py

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("hugo", "XXXX_previous")]

    operations = [
        migrations.CreateModel(
            name="LearnerThemeMemory",
            fields=[
                ("id", models.BigAutoField(primary_key=True)),
                ("learner_id",       models.CharField(max_length=128, db_index=True)),
                ("organisation_id",  models.CharField(max_length=128, db_index=True)),
                ("theme_key",        models.CharField(max_length=256, db_index=True)),
                ("referential_item_id", models.CharField(max_length=256, blank=True, default="")),
                ("stabilised_points",   models.JSONField(default=list)),
                ("open_loops",          models.JSONField(default=list)),
                ("persistent_difficulties", models.JSONField(default=list)),
                ("knowledge_status",    models.CharField(max_length=32, default="declared")),
                ("last_conversation_id", models.CharField(max_length=128, blank=True, default="")),
                ("updated_at",          models.DateTimeField(auto_now=True)),
            ],
            options={"unique_together": {("learner_id", "organisation_id", "theme_key")}},
        ),
    ]

# Notes RLS :
# La politique RLS existante couvre LearnerThemeMemory via organisation_id (avec s).
# SET LOCAL app.organisation_id requis avant toute lecture / écriture.
```

---

## `backend/apps/hugo/services/memory_consolidator.py`

```python
"""
Consolidation post-conversation : met à jour LearnerThemeMemory.
Appelé UNIQUEMENT à la fin de la séance, jamais pendant un tour.
"""

from backend.apps.hugo.domain.conversation_profile import (
    ConversationProgress, KnowledgeItemStatus,
)
from backend.apps.hugo.models import LearnerThemeMemory


def normalize_knowledge_status(raw_value: str | None) -> KnowledgeItemStatus:
    try:
        return KnowledgeItemStatus(raw_value or KnowledgeItemStatus.DECLARED.value)
    except ValueError:
        return KnowledgeItemStatus.DECLARED


def consolidate_session(session, progress: ConversationProgress) -> list[LearnerThemeMemory]:
    """
    Parcourt les branches de la conversation terminée et met à jour la mémoire thématique.
    Retourne la liste des enregistrements mis à jour.
    """
    learner_id      = str(session.learner_id)
    organisation_id = str(session.organisation_id)   # avec s
    session_id      = str(session.id)
    updated = []

    for branch in progress.active_branches:
        record, _ = LearnerThemeMemory.objects.get_or_create(
            learner_id=learner_id,
            organisation_id=organisation_id,
            theme_key=branch.theme_label,
        )
        record.referential_item_id = branch.referential_item_id or record.referential_item_id

        covered  = set(getattr(record, "stabilised_points", []) or [])
        open_set = set(getattr(record, "open_loops", []) or [])
        diff_set = set(getattr(record, "persistent_difficulties", []) or [])

        for code in (branch.reason_codes or []):
            covered.discard(code)
            open_set.add(code)
        if not branch.reason_codes:
            if branch.exploration_level.value == "green":
                covered.add(branch.objective_label)
                open_set.discard(branch.objective_label)
            elif branch.exploration_level.value == "orange":
                open_set.add(branch.objective_label)
            else:
                diff_set.add(branch.objective_label)

        record.stabilised_points = sorted(covered)
        record.open_loops        = sorted(open_set)
        record.persistent_difficulties = sorted(diff_set)
        record.last_conversation_id = session_id

      raw_status = record.knowledge_status or KnowledgeItemStatus.DECLARED.value
current_status = KnowledgeItemStatus(raw_status)

# Règle métier :
# - un statut DERIVED_PROVISIONAL ne devient jamais VALIDATED_TRAINER automatiquement
# - à défaut, on conserve le statut courant
if current_status == KnowledgeItemStatus.DERIVED_PROVISIONAL:
    next_status = KnowledgeItemStatus.DERIVED_PROVISIONAL
else:
    next_status = current_status

record.knowledge_status = next_status.value

        record.save()
        updated.append(record)
    return updated
```

---

## Endpoint `/memory-summary`

```python
# backend/apps/hugo/views/sessions.py — ajouter

@action(detail=True, methods=["get"], url_path="memory-summary")
def memory_summary(self, request, pk=None):
    session = self.get_object()
    from backend.apps.hugo.models import LearnerThemeMemory
    learner_id = str(session.learner_id)
    organisation_id = str(session.organisation_id)
    records = LearnerThemeMemory.objects.filter(
        learner_id=learner_id, organisation_id=organisation_id,
    ).order_by("-updated_at")[:10]
    return Response([{
        "theme_key":       r.theme_key,
        "stabilised":      r.stabilised_points,
        "open_loops":      r.open_loops,
        "difficulties":    r.persistent_difficulties,
        "status":          r.knowledge_status,
        "last_session":    r.last_conversation_id,
        "updated_at":      r.updated_at.isoformat(),
    } for r in records])
```

---

## Injection mémoire dans le contexte (optionnel LOT 4, configurable)

Dans `hugo_orchestrator.py`, **avant** l'appel P0 :

```python
# LOT 4 — injection mémoire thématique (additif, conditionnel)
USE_THEME_MEMORY = True  # feature flag

if USE_THEME_MEMORY:
    from backend.apps.hugo.models import LearnerThemeMemory
    theme_records = LearnerThemeMemory.objects.filter(
        learner_id=str(session.learner_id),
        organisation_id=str(session.organisation_id),
    ).order_by("-updated_at")[:5]
    if theme_records:
        turn_state.prior_theme_memory = [
            {
                "theme": r.theme_key,
                "stabilised": r.stabilised_points,
                "open": r.open_loops,
                "difficulties": r.persistent_difficulties,
                "status": r.knowledge_status,
            }
            for r in theme_records
        ]
```

---

## Tests du LOT 4 (`test_memory_consolidation.py` — 6 tests)

```python
import pytest
from unittest.mock import MagicMock, patch
from backend.apps.hugo.domain.conversation_profile import (
    ConversationPosture, ConversationProgress, ConversationBranch, SessionMaturityLevel,
)
from backend.apps.hugo.services.memory_consolidator import consolidate_session


def make_session(learner_id="l1", org_id="org1", session_id="s1"):
    s = MagicMock()
    s.learner_id = learner_id
    s.organisation_id = org_id
    s.id = session_id
    return s


def make_progress_with_branch(level: SessionMaturityLevel):
    branch = ConversationBranch(
        branch_id="b1", theme_label="gestion_conflit",
        objective_label="identifier_cause", exploration_level=level, is_active=True,
    )
    return ConversationProgress(
        session_id="s1", posture=ConversationPosture.REFLECTIVE_AFEST,
        active_branches=[branch], overall_maturity=level,
    )


@pytest.mark.django_db
def test_consolidation_creates_record():
    session = make_session()
    progress = make_progress_with_branch(SessionMaturityLevel.GREEN)
    result = consolidate_session(session, progress)
    assert len(result) == 1


@pytest.mark.django_db
def test_green_branch_added_to_stabilised():
    session = make_session()
    progress = make_progress_with_branch(SessionMaturityLevel.GREEN)
    result = consolidate_session(session, progress)
    assert "identifier_cause" in result[0].stabilised_points


@pytest.mark.django_db
def test_red_branch_added_to_difficulties():
    session = make_session()
    progress = make_progress_with_branch(SessionMaturityLevel.RED)
    result = consolidate_session(session, progress)
    assert "identifier_cause" in result[0].persistent_difficulties


@pytest.mark.django_db
def test_idempotent_on_second_call():
    session = make_session()
    p = make_progress_with_branch(SessionMaturityLevel.GREEN)
    consolidate_session(session, p)
    result = consolidate_session(session, p)
    assert len(result) == 1  # unique_together → pas de doublon


@pytest.mark.django_db
def test_organisation_id_with_s():
    """Vérifie l'orthographe canonique organisation_id (avec s)."""
    from backend.apps.hugo.models import LearnerThemeMemory
    session = make_session(org_id="org_test")
    progress = make_progress_with_branch(SessionMaturityLevel.ORANGE)
    consolidate_session(session, progress)
    record = LearnerThemeMemory.objects.get(
        learner_id="l1", organisation_id="org_test", theme_key="gestion_conflit",
    )
    assert record.organisation_id == "org_test"


@pytest.mark.django_db
def test_provisional_status_not_auto_upgraded():
    """Un critère provisional ne doit pas passer à validated_trainer automatiquement."""
    from backend.apps.hugo.models import LearnerThemeMemory
    from backend.apps.hugo.domain.conversation_profile import KnowledgeItemStatus
    session = make_session()
    LearnerThemeMemory.objects.create(
        learner_id="l1", organisation_id="org1", theme_key="gestion_conflit",
        knowledge_status=KnowledgeItemStatus.DERIVED_PROVISIONAL.value,
    )
    progress = make_progress_with_branch(SessionMaturityLevel.GREEN)
    result = consolidate_session(session, progress)
    assert result[0].knowledge_status == KnowledgeItemStatus.DERIVED_PROVISIONAL.value
    
    def test_invalid_knowledge_status_falls_back_to_declared():
    from backend.apps.hugo.services.memory_consolidator import normalize_knowledge_status
    from backend.apps.hugo.domain.conversation_profile import KnowledgeItemStatus

    assert normalize_knowledge_status(None) == KnowledgeItemStatus.DECLARED
    assert normalize_knowledge_status("invalid_status") == KnowledgeItemStatus.DECLARED
    
```

---

## Checklist de sortie du LOT 4

- [ ] Les 9 tests NR LOT 0 restent verts.
- [ ] Les 8 tests LOT 1, les 10 tests LOT 3 restent verts.
- [ ] Les 6 tests `test_memory_consolidation.py` passent.
- [ ] `KnowledgeItemStatus` importé depuis `conversation_profile.py` (NR-09).
- [ ] `organisation_id` (avec s) dans tous les filtres et la migration.
- [ ] `consolidate_session` appelé post-conversation uniquement.
- [ ] Verbatim brut absent du modèle `LearnerThemeMemory`.
- [ ] `USE_THEME_MEMORY = True` activable / désactivable sans redéploiement.
