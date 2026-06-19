# Hugo 1.9 — Spec d'implémentation complète v2

**Version :** 2.0 — 1 juin 2026
**Objet :** Document auto-suffisant pour Cursor. Inclut TutorConductProfiles + corrections audit.
**Hiérarchie :** SPEC POC v1.5 > Hugo 1.6 > README Cursor > Lots 0-6 > Contextualisation complète

---

## A. Invariants absolus

1. Gel P0 — turn_state_v17.py et decision_engine_v17.py jamais modifiés directement
2. Source unique des enums — conversation_profile.py UNIQUEMENT
3. UIState propre — jamais de champ P0 brut
4. organisation_id avec s partout (jamais organization_id)
5. Consolidation post-conversation uniquement, jamais pendant un tour
6. Enums en base = .value, reconstruites explicitement en code métier
7. Désérialisation JSONB via deserialize_conversation_progress() uniquement
8. DERIVED_PROVISIONAL jamais auto-upgradé en VALIDATED_TRAINER
9. Modifications front sur frontend1.8 uniquement
10. Le front ne recalcule aucun signal pédagogique

---

## B. Architecture logique du tour (cible)

```
1. Construction contexte
2. Analyse tour apprenant
3. Résolution posture -> TutorConductProfile [NOUVEAU]
4. Décision tutorale locale P0 (intact)
5. Rendu prompt via TutorPrompt + build_posture_block (system_template si présent)
6. Appel LLM
7. Post-traitement, garde-fous, journalisation
8. Post-conversation : consolidate_session() + record_session_signal()
```

---

## C. Contrats fondamentaux (LOT 0)

### Enums (conversation_profile.py — source unique)

```python
class ConversationPosture(str, Enum):
    DIAGNOSTIC = "diagnostic"
    REFLECTIVE_AFEST = "reflective_afest"
    KNOWLEDGE_REVIEW = "knowledge_review"

class SessionMaturityLevel(str, Enum):
    RED = "red"
    ORANGE = "orange"
    GREEN = "green"

class KnowledgeItemStatus(str, Enum):
    DECLARED = "declared"
    DERIVED_PROVISIONAL = "derived_provisional"
    VALIDATED_TRAINER = "validated_trainer"
```

### UIState (jamais de champ P0)

```python
@dataclass
class UIState:
    scene_label: str = "Raconter"
    scene_progress: float = 0.0
    active_quest_label: str = "Démarrer la conversation"
    quest_progress: float = 0.0
    maturity_color: SessionMaturityLevel = SessionMaturityLevel.RED
    synthesis_button_state: str = "locked"   # locked | possible | ready
    evaluation_button_state: str = "locked"  # locked | possible | ready
    persistent_objects: list = field(default_factory=list)
    gamification_profile: str = "B"           # A | B | C
```

---

## D. Désérialisation JSONB (LOT 1 — obligatoire)

```python
def deserialize_conversation_progress(raw: dict | None) -> Optional[ConversationProgress]:
    if not raw:
        return None
    try:
        branches = [
            ConversationBranch(
                branch_id=b["branch_id"],
                theme_label=b["theme_label"],
                objective_label=b["objective_label"],
                referential_item_id=b.get("referential_item_id"),
                exploration_level=SessionMaturityLevel(b.get("exploration_level", "red")),
                is_active=b.get("is_active", True),
                reason_codes=b.get("reason_codes", []),
            )
            for b in raw.get("active_branches", [])
        ]
        return ConversationProgress(
            session_id=raw["session_id"],
            posture=ConversationPosture(raw.get("posture", "reflective_afest")),
            active_branches=branches,
            active_branches_count=raw.get("active_branches_count", len([b for b in branches if b.is_active])),
            priority_branch_id=raw.get("priority_branch_id"),
            dispersion_risk=raw.get("dispersion_risk", False),
            overall_maturity=SessionMaturityLevel(raw.get("overall_maturity", "red")),
            synthesis_eligible=raw.get("synthesis_eligible", False),
            evaluation_eligible=raw.get("evaluation_eligible", False),
            missing_for_next_level=raw.get("missing_for_next_level", []),
            reason_codes=raw.get("reason_codes", []),
        )
    except (KeyError, TypeError, ValueError):
        return None
```

Les endpoints /progress et /ui-state utilisent exclusivement deserialize_conversation_progress().

---

## E. Audit variables P0 — demande explicite

La prochaine session Cursor doit auditer comment les variables P0 sont calculées.

Points à vérifier obligatoirement :

1. covered_points est-il cumulatif sur la session entière ou recalculé sur le seul dernier tour ?
   - Si recalculé uniquement sur le dernier tour : BUG CRITIQUE, progression reste toujours rouge

2. remaining_open_points : même question

3. overall_maturity : dérivée de covered_points ? Cohérente avec session_maturity de P0 ?

4. Toutes les variables P0 bornées : chaque variable a sa borne min/max respectée ?

Commandes d'audit :
```bash
grep -n "covered_points" backend/apps/hugo/services/conversation_progress_calculator.py
grep -n "session_history\|messages\|history" backend/apps/hugo/services/conversation_progress_calculator.py
```

---

## F. Corrections LOT 2 front

### Règle absolue

engagement_ui_model.js ne contient aucune référence à covered_points, remaining_open_points,
episode_clarity, can_close_for_now, turn_state, conversation_decision.

Mode dégradé minimal si ui-state indisponible :

```javascript
function buildDegradedDisplayModel() {
  return {
    sceneLabel: "Chargement...",
    sceneProgress: 0,
    showProgressBar: false,
    synthesisButton: { state: "locked", visible: true, disabled: true },
    evaluationButton: { state: "locked", visible: false, disabled: true },
    persistentObjects: [],
  };
}
```

### Boutons Synthèse et Évaluation (correction bloquante)

Ajouter dans HugoProgressPanel ou composant équivalent dans frontend1.8 :

```javascript
async function requestSynthesis(sessionId) {
  const res = await fetch(`/api/hugo/sessions/${sessionId}/request-synthesis/`, {
    method: "POST", headers: { "Content-Type": "application/json" }, credentials: "include",
  });
  if (res.status === 400) {
    const err = await res.json();
    return { eligible: false, reason_codes: err.reason_codes };
  }
  return { eligible: true };
}
```

---

## G. TutorConductProfiles (nouveau lot)

### Modèle Django

```python
class TutorConductProfile(models.Model):
    # organisation_id="" = profil système fallback global
    organisation_id = models.CharField(max_length=128, db_index=True, blank=True, default="")
    posture = models.CharField(max_length=64)
    system_template = models.TextField()
    user_template = models.TextField(blank=True, default="")
    max_questions_per_turn = models.IntegerField(null=True, blank=True)
    forbidden_moves = models.JSONField(default=list, blank=True)
    allowed_moves = models.JSONField(default=list, blank=True)
    closure_policy = models.CharField(max_length=64, blank=True, default="")
    description = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "Profil de conduite tutorale"
        unique_together = [("organisation_id", "posture")]
```

### Résolution 3 niveaux (conduct_profile_resolver.py)

```python
def resolve_conduct_profile(posture, organisation_id):
    # Niveau 1 : profil organisation
    try:
        profile = TutorConductProfile.objects.get(
            organisation_id=organisation_id, posture=posture.value, is_active=True)
        return _to_conduct_dict(profile, posture)
    except TutorConductProfile.DoesNotExist:
        pass
    # Niveau 2 : profil système
    try:
        profile = TutorConductProfile.objects.get(
            organisation_id="", posture=posture.value, is_active=True)
        return _to_conduct_dict(profile, posture)
    except TutorConductProfile.DoesNotExist:
        pass
    # Niveau 3 : fallback statique
    return get_profile(posture)
```

### Patch orchestrateur (additif)

```python
# Remplace get_profile(posture) dans le bloc LOT 3 :
from backend.apps.hugo.services.conduct_profile_resolver import resolve_conduct_profile
profile = resolve_conduct_profile(posture, str(getattr(session, "organisation_id", "")))
```

### Patch build_posture_block (additif)

```python
def build_posture_block(pc: dict) -> str:
    if pc.get("system_template"):
        return pc["system_template"].format(
            posture=pc["posture"].upper(),
            max_questions=pc.get("max_questions_per_turn", 2),
            forbidden_moves=", ".join(pc.get("forbidden_moves", [])) or "aucun",
            description=pc.get("description", ""),
        )
    # Builder par défaut LOT 3 inchangé
    ...
```

### Labels UI obligatoires (jamais les noms techniques)

- diagnostic -> "Séance de diagnostic"
- reflective_afest -> "Entretien réflexif AFEST"
- knowledge_review -> "Révision / bâchage"

### Interface ConductProfilesView.vue (dans frontend1.8)

Fonctionnalités :
- Liste 3 postures avec indicateur "personnalisé / défaut système"
- Formulaire d'édition : system_template, user_template, max_questions_per_turn, forbidden_moves, closure_policy, description
- Comparaison côte à côte org vs système
- Bouton "Réinitialiser au défaut système"
- Prévisualisation du bloc posture résolu

---

## H. Corrections LOT 4 — mémoire

### Correction 1 : consolidation post-session

```python
def _post_conversation_hooks(session, progress, turn_count):
    consolidate_session(session, progress)
    record_session_signal(session, progress, turn_count=turn_count)
# Appeler après chaque conversation, pas seulement sur generate-trace
```

### Correction 2 : injection mémoire (feature flag)

```python
if getattr(settings, "HUGO_MEMORY_INJECTION_ENABLED", False):
    theme_memories = LearnerThemeMemory.objects.filter(
        organisation_id=session.organisation_id,
        learner_id=session.learner_id,
        knowledge_status=KnowledgeItemStatus.VALIDATED_TRAINER.value,
    ).order_by("-updated_at")[:5]
    if theme_memories.exists():
        context["theme_memory_summary"] = [
            {"theme": m.theme_key, "status": m.knowledge_status} for m in theme_memories
        ]
```

---

## I. État des fichiers

| Fichier | Statut | Action |
|---|---|---|
| conversation_profile.py | Conforme | - |
| deserialize_conversation_progress() | Conforme | - |
| engagement_ui_model.js | Fallback P0 à supprimer | Correction Phase 1 |
| HugoProgressPanel (boutons) | Non branchés | Correction Phase 1 |
| synthesis_service.py | Stub seulement | Correction Phase 2 |
| memory_consolidator.py | Branchement partiel | Correction Phase 3 |
| quality_tracker.py | Déclenchement partiel | Correction Phase 3 |
| tutor_conduct_profile.py (modèle) | A créer | Phase 4 |
| conduct_profile_resolver.py | A créer | Phase 4 |
| ConductProfilesView.vue | A créer | Phase 4 |
| UsersView.vue (ORGADMIN complet) | A compléter | Phase 5 |

---

## J. Tests à ajouter

```python
# test_conduct_profiles.py (5 tests obligatoires)

def test_fallback_to_static_when_no_profile():
    result = resolve_conduct_profile(ConversationPosture.REFLECTIVE_AFEST, "org-test")
    assert "max_questions_per_turn" in result

def test_organisation_profile_overrides_system():
    TutorConductProfile.objects.create(
        organisation_id="org-a", posture="reflective_afest",
        system_template="Custom org-a", max_questions_per_turn=1)
    result = resolve_conduct_profile(ConversationPosture.REFLECTIVE_AFEST, "org-a")
    assert result["system_template"] == "Custom org-a"

def test_system_profile_used_when_no_org_profile():
    TutorConductProfile.objects.create(
        organisation_id="", posture="diagnostic",
        system_template="Système diagnostic", max_questions_per_turn=2)
    result = resolve_conduct_profile(ConversationPosture.DIAGNOSTIC, "org-b")
    assert result["system_template"] == "Système diagnostic"

def test_inactive_profile_ignored():
    TutorConductProfile.objects.create(
        organisation_id="org-c", posture="knowledge_review",
        system_template="Désactivé", is_active=False)
    result = resolve_conduct_profile(ConversationPosture.KNOWLEDGE_REVIEW, "org-c")
    assert result.get("system_template") != "Désactivé"

def test_p0_not_in_conduct_profile():
    result = resolve_conduct_profile(ConversationPosture.REFLECTIVE_AFEST, "org-test")
    for field in P0_CORE_FIELDS:
        assert field not in result
```

