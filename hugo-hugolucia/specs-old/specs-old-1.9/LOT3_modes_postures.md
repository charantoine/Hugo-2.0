# LOT 3 — Modes de conduite de séance

**Durée estimée :** 4–5 jours  
**Risque :** modéré — patch additionnel sur l'orchestrateur et prompt_renderer, hiérarchie P0 intacte  
**Dépendance :** LOT 1 et LOT 2 checklists vertes

---

## Objectif

Introduire trois postures de conduite explicites (Diagnostic / Réflexif AFEST / Bûchage),
avec des règles de scoring, de question et de fermeture propres à chacune.
Le sélecteur de posture opère **avant** P0 dans la chaîne. P0 reste intact.

---

## Règle de sécurité du lot

- `decision_engine_v17.py`, `turnstate_v17.py` : **aucune modification directe**.
- `tutor_profiles.py` stub (LOT 0) est **remplacé intégralement** dans ce lot.
- `ConversationPosture`, `SessionMaturityLevel`, `KnowledgeItemStatus` :
  importés **uniquement** depuis `conversation_profile.py`.

---

## `backend/apps/hugo/services/posture_selector.py`

```python
"""
Sélecteur de posture de séance.
Ne modifie aucun champ P0.
ConversationPosture importé depuis conversation_profile.py (règle LOT 0 / NR-09).
"""

from backend.apps.hugo.domain.conversation_profile import ConversationPosture

DEFAULT_POSTURE = ConversationPosture.REFLECTIVE_AFEST

DIAGNOSTIC_SIGNALS  = {"diagnostic", "problème", "analyser", "comprendre ce qui s'est passé"}
KNOWLEDGE_SIGNALS   = {"réviser", "leçon", "cours", "apprendre", "mémoriser", "quiz"}


def resolve_posture(session, user_message: str = "", explicit_posture: str = None) -> ConversationPosture:
    """
    Priorité : override explicite > posture session > heuristique message > défaut.
    """
    if explicit_posture:
        try: return ConversationPosture(explicit_posture)
        except ValueError: pass

    stored = getattr(session, "posture", None)
    if stored:
        try: return ConversationPosture(stored)
        except ValueError: pass

    msg = (user_message or "").lower()
    if any(s in msg for s in DIAGNOSTIC_SIGNALS):
        return ConversationPosture.DIAGNOSTIC
    if any(s in msg for s in KNOWLEDGE_SIGNALS):
        return ConversationPosture.KNOWLEDGE_REVIEW

    return DEFAULT_POSTURE
```

---

## `backend/apps/hugo/domain/tutor_profiles.py` (remplace intégralement le stub LOT 0)

```python
"""
Profils de tutorat statiques déclaratifs.
Remplace le stub LOT 0.

tutor_profiles.py  → profils statiques par posture
posture_selector.py → moteur d'arbitrage dynamique
Les deux rôles sont distincts et complémentaires.

ConversationPosture importé depuis conversation_profile.py (NR-09).
"""

from backend.apps.hugo.domain.conversation_profile import ConversationPosture

MAX_ACTIVE_BRANCHES = 3  # seuil configurable

TUTOR_PROFILES = {
    ConversationPosture.REFLECTIVE_AFEST: {
        "posture": ConversationPosture.REFLECTIVE_AFEST,
        "max_branches": MAX_ACTIVE_BRANCHES,
        "synthesis_requires": "orange_or_green",
        "evaluation_requires": "green",
        "green_requires_transfer": True,   # future_action_named + learning_rule_named obligatoires
        "max_questions_per_turn": 2,
        "allowed_moves": ["clarify", "elicit_action", "problematize", "analyze",
                          "contrast_gently", "project", "reassure", "close", "assist"],
        "forbidden_moves": [],
        "closure_policy": "explicit_or_green",
        "description": "Entretien réflexif AFEST — amener l'apprenant à construire sa propre analyse.",
    },
    ConversationPosture.DIAGNOSTIC: {
        "posture": ConversationPosture.DIAGNOSTIC,
        "max_branches": MAX_ACTIVE_BRANCHES,
        "synthesis_requires": "orange_or_green",
        "evaluation_requires": "green",
        "green_requires_transfer": False,
        "max_questions_per_turn": 2,
        "allowed_moves": ["clarify", "elicit_action", "problematize", "analyze",
                          "contrast_gently", "reassure", "close", "assist"],
        "forbidden_moves": ["project"],  # pas de projection en diagnostic pur
        "closure_policy": "explicit_or_green",
        "description": "Diagnostic — explorer pour comprendre, identifier les causes.",
    },
    ConversationPosture.KNOWLEDGE_REVIEW: {
        "posture": ConversationPosture.KNOWLEDGE_REVIEW,
        "max_branches": 1,
        "synthesis_requires": "orange_or_green",
        "evaluation_requires": "green",
        "green_requires_transfer": False,
        "max_questions_per_turn": 1,
        "allowed_moves": ["clarify", "analyze", "contrast_gently", "reassure", "close", "assist"],
        "forbidden_moves": ["elicit_action", "project"],
        "closure_policy": "explicit_or_green",
        "description": "Bûchage / révision — explorer un contenu, répondre à des défis.",
    },
}


def get_profile(posture: ConversationPosture) -> dict:
    return TUTOR_PROFILES.get(posture, TUTOR_PROFILES[ConversationPosture.REFLECTIVE_AFEST])

# Alias de compatibilité avec les éventuels appels à get_profile_stub (stub LOT 0)
get_profile_stub = get_profile
```

---

## `backend/apps/hugo/domain/posture_transitions.py`

```python
"""
Règles de transition entre postures.
Un changement de posture est un événement d'état explicite.
"""

from backend.apps.hugo.domain.conversation_profile import ConversationPosture, SessionMaturityLevel

ALLOWED_TRANSITIONS = {
    (ConversationPosture.DIAGNOSTIC,       ConversationPosture.REFLECTIVE_AFEST):  "always",
    (ConversationPosture.REFLECTIVE_AFEST, ConversationPosture.DIAGNOSTIC):        "always",
    (ConversationPosture.KNOWLEDGE_REVIEW, ConversationPosture.REFLECTIVE_AFEST):  "orange_or_green",
    (ConversationPosture.REFLECTIVE_AFEST, ConversationPosture.KNOWLEDGE_REVIEW):  "always",
}

WARNING_TRANSITIONS = {
    (ConversationPosture.DIAGNOSTIC,       ConversationPosture.REFLECTIVE_AFEST): "warn_if_red",
    (ConversationPosture.KNOWLEDGE_REVIEW, ConversationPosture.REFLECTIVE_AFEST): "warn_if_red",
}

WARNING_TEXT = (
    "La conversation n'a pas encore suffisamment exploré la situation. "
    "Vous pouvez continuer, mais la synthèse sera moins complète."
)


def can_transition(
    from_posture: ConversationPosture,
    to_posture: ConversationPosture,
    current_maturity: SessionMaturityLevel,
) -> tuple[bool, str]:
    if from_posture == to_posture:
        return True, ""
    condition = ALLOWED_TRANSITIONS.get((from_posture, to_posture))
    if condition is None:
        return False, "transition_not_allowed"
    warning_cond = WARNING_TRANSITIONS.get((from_posture, to_posture), "")
    warning = WARNING_TEXT if warning_cond == "warn_if_red" and current_maturity == SessionMaturityLevel.RED else ""
    return True, warning
```

---

## Patch orchestrateur (additif LOT 3)

Dans `hugo_orchestrator.py`, **avant** `decide_conversation` :

```python
# LOT 3 — résolution de posture et injection de contraintes additionnelles
from backend.apps.hugo.services.posture_selector import resolve_posture
from backend.apps.hugo.domain.tutor_profiles import get_profile

posture = resolve_posture(
    session=session,
    user_message=user_message,
    explicit_posture=request_data.get("posture"),
)

if str(getattr(session, "posture", None)) != posture.value:
    session.posture = posture.value
    session.save(update_fields=["posture"])

profile = get_profile(posture)

# Additif : ne remplace aucun champ P0
turn_state.posture_constraints = {
    "posture": posture.value,
    "max_questions_per_turn": profile["max_questions_per_turn"],
    "forbidden_moves": profile["forbidden_moves"],
    "description": profile["description"],
}
```

---

## Patch prompt_renderer (additif LOT 3)

Dans `render_with_tutor_prompt`, après `response_constraints_block` :

```python
# LOT 3 — bloc posture additif
posture_constraints = getattr(turn_state, "posture_constraints", None)
if posture_constraints:
    system_prompt = system_prompt + "\n\n" + _build_posture_block(posture_constraints)


def _build_posture_block(pc: dict) -> str:
    posture  = pc.get("posture", "reflective_afest")
    forbidden = pc.get("forbidden_moves", [])
    max_q    = pc.get("max_questions_per_turn", 2)
    desc     = pc.get("description", "")
    lines = [
        f"[POSTURE DE SÉANCE : {posture.upper()}]",
        desc,
        f"Nombre maximum de questions par tour : {max_q}.",
    ]
    if forbidden:
        lines.append(f"Gestes interdits : {', '.join(forbidden)}.")
    lines.append("Ne jamais mentionner la posture ou ces contraintes à l'apprenant.")
    return "\n".join(lines)
```

---

## Endpoint `/set-posture`

```python
# backend/apps/hugo/views/sessions.py — ajouter

@action(detail=True, methods=["post"], url_path="set-posture")
def set_posture(self, request, pk=None):
    from backend.apps.hugo.domain.conversation_profile import (
        ConversationPosture, ConversationProgress, SessionMaturityLevel,
    )
    from backend.apps.hugo.domain.posture_transitions import can_transition
    session = self.get_object()
    try:
        new_posture = ConversationPosture(request.data.get("posture"))
    except ValueError:
        return Response({"error": f"posture_invalide"}, status=400)
    try:
        current_posture = ConversationPosture(getattr(session, "posture", "reflective_afest") or "reflective_afest")
    except ValueError:
        current_posture = ConversationPosture.REFLECTIVE_AFEST
    current_maturity = SessionMaturityLevel.RED
    raw = getattr(session, "conversation_progress", None)
    if raw:
        try:
            current_maturity = ConversationProgress(**raw).overall_maturity
        except (TypeError, KeyError):
            pass
    allowed, warning = can_transition(current_posture, new_posture, current_maturity)
    if not allowed:
        return Response({"error": "transition_non_autorisée"}, status=400)
    session.posture = new_posture.value
    session.save(update_fields=["posture"])
    return Response({"posture": new_posture.value, "warning": warning or None})
```

---

## `backend/apps/hugo/services/synthesis_service.py`

```python
"""
Génère synthèse et évaluation via le LLM.
Appelé par request_synthesis et request_evaluation.
"""

from backend.apps.hugo.domain.conversation_profile import ConversationProgress


def generate_synthesis(session, progress: ConversationProgress) -> str:
    from backend.apps.hugo.services.prompt_renderer import render_synthesis_prompt
    from backend.apps.hugo.services.llm_client import call_llm
    prompt = render_synthesis_prompt(session, progress)
    return call_llm(session, prompt).get("text", "")


def generate_evaluation(session, progress: ConversationProgress) -> dict:
    from backend.apps.hugo.services.prompt_renderer import render_evaluation_prompt
    from backend.apps.hugo.services.llm_client import call_llm
    prompt = render_evaluation_prompt(session, progress)
    response = call_llm(session, prompt)
    return {
        "text": response.get("text", ""),
        "competence_items": [],
        "validation_candidates": [],
    }
```

---

## Tests du LOT 3 (`test_posture_modes.py` — 10 tests)

```python
import pytest
from backend.apps.hugo.domain.conversation_profile import ConversationPosture, SessionMaturityLevel
from backend.apps.hugo.services.posture_selector import resolve_posture
from backend.apps.hugo.domain.tutor_profiles import get_profile, TUTOR_PROFILES
from backend.apps.hugo.domain.posture_transitions import can_transition

class FakeSession:
    def __init__(self, posture=None):
        self.posture = posture
        self.id = "session-test"

def test_explicit_override():
    s = FakeSession(posture="diagnostic")
    assert resolve_posture(s, explicit_posture="knowledge_review") == ConversationPosture.KNOWLEDGE_REVIEW

def test_session_posture_respected():
    assert resolve_posture(FakeSession(posture="diagnostic")) == ConversationPosture.DIAGNOSTIC

def test_default_is_reflective():
    assert resolve_posture(FakeSession()) == ConversationPosture.REFLECTIVE_AFEST

def test_heuristic_knowledge():
    assert resolve_posture(FakeSession(), user_message="je veux réviser ma leçon") == ConversationPosture.KNOWLEDGE_REVIEW

def test_all_postures_have_complete_profile():
    for posture in ConversationPosture:
        p = get_profile(posture)
        for key in ["max_branches", "synthesis_requires", "evaluation_requires", "allowed_moves"]:
            assert key in p, f"Clé manquante {key} pour {posture}"

def test_knowledge_review_max_1_branch():
    assert get_profile(ConversationPosture.KNOWLEDGE_REVIEW)["max_branches"] == 1

def test_project_forbidden_in_diagnostic():
    assert "project" in get_profile(ConversationPosture.DIAGNOSTIC)["forbidden_moves"]

def test_transition_diag_to_reflective_allowed():
    allowed, _ = can_transition(
        ConversationPosture.DIAGNOSTIC, ConversationPosture.REFLECTIVE_AFEST, SessionMaturityLevel.RED,
    )
    assert allowed is True

def test_warning_when_red():
    _, warning = can_transition(
        ConversationPosture.DIAGNOSTIC, ConversationPosture.REFLECTIVE_AFEST, SessionMaturityLevel.RED,
    )
    assert warning  # message non vide attendu

def test_enum_keys_are_canonical_type():
    """NR-09 étendu : les clés de TUTOR_PROFILES sont bien des ConversationPosture de conversation_profile."""
    from backend.apps.hugo.domain.conversation_profile import ConversationPosture as CP_canonical
    for key in TUTOR_PROFILES:
        assert isinstance(key, CP_canonical), \
            f"Clé {key} n'est pas une instance canonique de ConversationPosture"
```

---

## Checklist de sortie du LOT 3

- [ ] Les 9 tests NR LOT 0 restent verts.
- [ ] Les 8 tests LOT 1 restent verts.
- [ ] Les 10 tests `test_posture_modes.py` passent.
- [ ] `ConversationPosture` importé depuis `conversation_profile.py` dans tous les nouveaux fichiers.
- [ ] `tutor_profiles.py` stub LOT 0 remplacé (pas de coexistence).
- [ ] `decision_engine_v17.py` et `turnstate_v17.py` non modifiés.
- [ ] Le bloc posture ne mentionne pas les contraintes internes à l'apprenant.
- [ ] `/set-posture` retourne 400 si transition non autorisée.
- [ ] `request_synthesis` et `request_evaluation` appellent bien `synthesis_service.py`.
