# LOT 0 — Contrats et fondations

**Durée estimée :** 2–3 jours  
**Risque :** très faible — additif pur, aucune modification des fichiers P0 existants  
**Priorité :** bloquant pour tous les lots suivants

---

## Objectif

Formaliser les objets d'état intermédiaires communs (profils conversationnels, progression de séance,
UIState) et les reason codes associés, sous forme de dataclasses backend testables sans LLM.
Poser les tests de non-régression P0 qui valideront chaque lot suivant.

Aucun comportement visible ne change à l'issue de ce lot.

---

## Règle de sécurité du lot

Aucun des champs P0 listés dans `backend/apps/hugo/domain/turnstate_v17.py` ou
`backend/apps/hugo/services/decision_engine_v17.py` ne doit être modifié.
Tous les nouveaux objets sont **additifs**.
Les anciens champs (`covered_points`, `remaining_open_points`, `session_maturity`,
`can_close_for_now`, etc.) sont en **lecture seule** pour ce lot.

---

## Décision d'architecture — source de vérité des enums

**Règle absolue :** `ConversationPosture`, `SessionMaturityLevel` et `KnowledgeItemStatus`
sont définis **uniquement** dans `conversation_profile.py`.
Tous les autres modules (LOT 3, LOT 5, LOT 6, `schemas.py`, `turn_state_v17.py`)
doivent les **importer** depuis ce fichier. Toute redéfinition locale est interdite.

Cette règle est vérifiée par NR-09 (voir section tests).

---

## Décision d'architecture — nom du champ RLS

La SPEC v1.5 (section 3.2 et section 13) utilise systématiquement `organisation_id`
(avec un `s`, orthographe française). Ce nom est canonique dans toute la base de code.
La politique RLS utilise `current_setting('app.organisation_id', true)`.

---

## Fichiers à créer

### `backend/apps/hugo/domain/conversation_profile.py`

```python
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional


class ConversationPosture(str, Enum):
    """Source de vérité unique. Importer depuis ce module partout ailleurs."""
    DIAGNOSTIC = "diagnostic"
    REFLECTIVE_AFEST = "reflective_afest"
    KNOWLEDGE_REVIEW = "knowledge_review"


class SessionMaturityLevel(str, Enum):
    """Source de vérité unique. Hérite de str pour permettre == 'red' etc."""
    RED = "red"        # exploration insuffisante
    ORANGE = "orange"  # explorable, synthèse possible mais partielle
    GREEN = "green"    # base suffisante pour bilan / évaluation facultative


class KnowledgeItemStatus(str, Enum):
    """Source de vérité unique. Importer depuis ce module partout ailleurs."""
    DECLARED = "declared"
    DERIVED_PROVISIONAL = "derived_provisional"
    VALIDATED_TRAINER = "validated_trainer"


@dataclass
class ConversationBranch:
    """
    Unité de suivi : couplage thème de situation + objectif pédagogique.
    Un même thème peut soutenir plusieurs objectifs.
    Maximum 3 branches actives simultanément (contrôlé par ConversationProgressCalculator).
    """
    branch_id: str = ""
    theme_label: str = ""
    objective_label: str = ""
    referential_item_id: Optional[str] = None
    exploration_level: SessionMaturityLevel = SessionMaturityLevel.RED
    is_active: bool = True
    reason_codes: list = field(default_factory=list)


@dataclass
class ConversationProgress:
    """
    État de progression d'une conversation entière.
    Calculé à chaque tour utile par ConversationProgressCalculator (LOT 1).
    Stocké dans HugoSession.conversation_progress (champ JSONB).
    """
    session_id: str = ""
    posture: ConversationPosture = ConversationPosture.REFLECTIVE_AFEST
    active_branches: list = field(default_factory=list)
    active_branches_count: int = 0          # raccourci pour les consumers
    priority_branch_id: Optional[str] = None
    dispersion_risk: bool = False
    overall_maturity: SessionMaturityLevel = SessionMaturityLevel.RED
    synthesis_eligible: bool = False
    evaluation_eligible: bool = False
    missing_for_next_level: list = field(default_factory=list)
    reason_codes: list = field(default_factory=list)


@dataclass
class UIState:
    """
    Modèle dérivé destiné exclusivement au front prod montrable.
    INTERDIT : aucun champ P0 brut ici.
    Calculé depuis ConversationProgress + ConversationDecision existante.
    Vérifié par NR-07.
    """
    scene_label: str = "Raconter"
    scene_progress: float = 0.0
    active_quest_label: str = "Démarrer la conversation"
    quest_progress: float = 0.0
    maturity_color: SessionMaturityLevel = SessionMaturityLevel.RED
    synthesis_button_state: str = "locked"    # "locked" | "possible" | "ready"
    evaluation_button_state: str = "locked"   # "locked" | "possible" | "ready"
    persistent_objects: list = field(default_factory=list)
    gamification_profile: str = "B"           # "A" | "B" | "C"
```

**Contrainte :** `UIState` ne doit exposer aucun des champs de `P0_CORE_FIELDS`
ni `P0_LLM_FIELDS`. Le test NR-07 vérifie cela automatiquement.

---

### `backend/apps/hugo/domain/reason_codes.py`

```python
# Codes de raison partagés — constantes string uniquement, jamais de logique.

RC_NOT_ENOUGH_DESCRIPTION       = "not_enough_description"
RC_NO_CONCRETE_ACTIONS          = "no_concrete_actions"
RC_NO_CAUSE_NAMED               = "no_cause_named"
RC_NO_TRANSFER_RULE             = "no_transfer_rule"
RC_LOOP_RISK_HIGH               = "loop_risk_high"
RC_DISPERSION_RISK              = "dispersion_risk"
RC_SYNTHESIS_ELIGIBLE           = "synthesis_eligible"
RC_EVALUATION_ELIGIBLE          = "evaluation_eligible"
RC_EVALUATION_BLOCKED_MATURITY  = "evaluation_blocked_maturity"
RC_EVALUATION_BLOCKED_INTERACTION_RISK = "evaluation_blocked_interaction_risk"
RC_EVALUATION_BLOCKED_COGNITIVE_LOAD   = "evaluation_blocked_cognitive_load"
RC_EVALUATION_BLOCKED_RECENT_BILAN     = "evaluation_blocked_recent_bilan"
RC_SYNTHESIS_BLOCKED_MATURITY   = "synthesis_blocked_maturity"
RC_POSTURE_DIAGNOSTIC           = "posture_diagnostic"
RC_POSTURE_REFLECTIVE           = "posture_reflective_afest"
RC_POSTURE_KNOWLEDGE            = "posture_knowledge_review"
```

> `RC_SYNTHESIS_BLOCKED_MATURITY` est distinct de `RC_EVALUATION_BLOCKED_MATURITY` :
> synthèse = seuil orange, évaluation = seuil green.

---

### `backend/apps/hugo/domain/tutor_profiles.py` (stub LOT 0 — remplacé intégralement au LOT 3)

```python
from backend.apps.hugo.domain.conversation_profile import ConversationPosture

SUPPORTED_POSTURES = [
    ConversationPosture.DIAGNOSTIC,
    ConversationPosture.REFLECTIVE_AFEST,
    ConversationPosture.KNOWLEDGE_REVIEW,
]

MAX_ACTIVE_BRANCHES = 3


def get_profile_stub(posture: ConversationPosture) -> dict:
    """Stub minimal. Remplacé intégralement par des profils complets au LOT 3."""
    return {
        "posture": posture,
        "max_branches": MAX_ACTIVE_BRANCHES,
        "synthesis_requires": "orange_or_green",
        "evaluation_requires": "green",
    }
```

---

### Migration Django

```python
# backend/apps/hugo/migrations/XXXX_add_conversation_progress.py

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hugo", "XXXX_previous_migration"),
    ]

    operations = [
        migrations.AddField(
            model_name="hugosession",
            name="conversation_progress",
            field=models.JSONField(null=True, blank=True, default=None),
        ),
    ]

# Notes RLS :
# - HugoSession possède déjà organisation_id (orthographe avec 's', SPEC v1.5 section 13).
# - La politique RLS existante couvre automatiquement le nouveau champ JSONB.
# - Aucune nouvelle politique RLS requise.
# - SET LOCAL app.organisation_id doit être appliqué avant toute lecture/écriture.
```

---

### Trois endpoints GET (stubs LOT 0, câblés au LOT 1 et LOT 2)

```python
# backend/apps/hugo/views/sessions.py — ajouter au ViewSet existant

@action(detail=True, methods=["get"], url_path="progress")
def get_progress(self, request, pk=None):
    session = self.get_object()
    return Response({"status": "no_progress_yet", "session_id": str(session.id)})


@action(detail=True, methods=["get"], url_path="ui-state")
def get_ui_state(self, request, pk=None):
    session = self.get_object()
    return Response({
        "scene_label": "Raconter",
        "scene_progress": 0.0,
        "active_quest_label": "Démarrer la conversation",
        "quest_progress": 0.0,
        "maturity_color": "red",
        "synthesis_button_state": "locked",
        "evaluation_button_state": "locked",
        "persistent_objects": [],
        "gamification_profile": "B",
    })


@action(detail=True, methods=["get"], url_path="posture")
def get_posture(self, request, pk=None):
    session = self.get_object()
    posture = getattr(session, "posture", "reflective_afest") or "reflective_afest"
    return Response({"posture": posture, "session_id": str(session.id)})
```

---

## Tests de non-régression P0 (9 tests — écrire en premier, ne jamais modifier)

**Fichier :** `backend/apps/hugo/tests/test_p0_non_regression.py`

```python
import dataclasses, pytest

P0_CORE_FIELDS = {
    "has_concrete_actions", "episode_clarity", "problem_salience",
    "reflection_phase", "affect_valence", "cognitive_load",
    "interaction_risk", "session_phase",
}
P0_LLM_FIELDS = {
    "has_concrete_actions", "episode_clarity", "problem_salience",
    "reflection_phase", "affect_valence", "cognitive_load", "interaction_risk",
}

def test_p0_core_fields_present(build_minimal_turn_state):
    ts = build_minimal_turn_state()
    p0 = ts.to_dict().get("p0", {})
    assert P0_CORE_FIELDS.issubset(p0.keys()), f"Champs manquants : {P0_CORE_FIELDS - p0.keys()}"

def test_session_phase_not_llm_overridable():
    assert "session_phase" not in P0_LLM_FIELDS

def test_thread_tracking_fields_present(build_minimal_turn_state):
    ts = build_minimal_turn_state()
    d = ts.to_dict()
    assert "covered_points" in d
    assert "remaining_open_points" in d

def test_protected_mode_cognitive_load_high(build_decision_with):
    decision = build_decision_with(cognitive_load="high")
    assert decision.number_of_questions <= 1
    assert decision.question_style in ("single_safe", "single")

def test_explicit_closure(build_decision_with):
    decision = build_decision_with(closure_signal="explicit")
    assert decision.pedagogical_move == "close"
    assert decision.number_of_questions == 0

def test_explicit_repetition(build_decision_with):
    decision = build_decision_with(repetition_signal="explicit")
    assert decision.pedagogical_move in ("repair", "close", "repair_repetition")
    assert "do_not_repeat_covered_point" in (decision.response_constraints or [])

def test_ui_state_no_p0_fields():
    from backend.apps.hugo.domain.conversation_profile import UIState
    ui_fields = {f.name for f in dataclasses.fields(UIState)}
    forbidden = P0_CORE_FIELDS | {
        "session_maturity", "evidence_strength", "covered_points",
        "remaining_open_points", "loop_risk", "repetition_signal",
        "closure_signal", "learner_help_request", "assistant_meta_leak_risk",
        "intervention_necessity", "available_material", "conversation_goal",
        "consecutive_clarify_turns", "sticky_has_concrete_actions",
    }
    overlap = ui_fields & forbidden
    assert not overlap, f"UIState expose des champs P0 interdits : {overlap}"

def test_rls_cross_tenant_hugo_session(create_session, set_local_org):
    """Utilise organisation_id (avec s) — SPEC v1.5 section 13."""
    session_a = create_session(org="org_a")
    session_b = create_session(org="org_b")
    with set_local_org("org_a"):
        from backend.apps.hugo.models import HugoSession
        result = HugoSession.objects.filter(id=session_b.id)
        assert result.count() == 0, "RLS fail : org A peut lire la session de org B"

def test_enum_single_source_of_truth():
    from backend.apps.hugo.domain.conversation_profile import (
        ConversationPosture, SessionMaturityLevel, KnowledgeItemStatus,
    )
    assert ConversationPosture.REFLECTIVE_AFEST == "reflective_afest"
    assert SessionMaturityLevel.GREEN == "green"
    assert KnowledgeItemStatus.VALIDATED_TRAINER == "validated_trainer"
    try:
        from backend.apps.hugo.domain import schemas
        if hasattr(schemas, "ConversationPosture"):
            assert schemas.ConversationPosture is ConversationPosture, \
                "schemas.ConversationPosture doit importer depuis conversation_profile, pas redéfinir"
    except ImportError:
        pass
```

---

## Checklist de sortie du LOT 0

- [ ] Les 9 tests NR passent sur le code actuel.
- [ ] `conversation_profile.py` et `reason_codes.py` importent sans erreur.
- [ ] `tutor_profiles.py` stub importable.
- [ ] Migration appliquée, champ `conversation_progress` nullable sur `HugoSession`.
- [ ] Les 3 endpoints GET répondent 200 avec valeurs par défaut.
- [ ] Aucune modification dans `turnstate_v17.py`, `decision_engine_v17.py`,
      `hugo_orchestrator.py`, `prompt_renderer.py`.
- [ ] `UIState` ne contient aucun champ listé dans `P0_CORE_FIELDS` (vérifié par NR-07).
- [ ] Tous les imports de `ConversationPosture` / `SessionMaturityLevel` /
      `KnowledgeItemStatus` pointent vers `conversation_profile.py` (NR-09).
- [ ] Le champ RLS s'appelle `organisation_id` (avec s) dans migration et helper `set_local_org`.
