# Prompt Cursor — Audit Hugo 1.9 v2 + TutorConductProfiles

**À copier-coller directement dans Cursor.**
**Ce prompt est auto-suffisant.**

---

## CONTEXTE PRODUIT

Hugo est un assistant réflexif AFEST centré apprenant, dans une webapp multi-tenant Django + Vue.js.

**Invariants absolus :**
1. `turn_state_v17.py` et `decision_engine_v17.py` ne sont JAMAIS modifiés directement
2. Enums (`ConversationPosture`, `SessionMaturityLevel`, `KnowledgeItemStatus`) importées UNIQUEMENT depuis `conversation_profile.py`
3. `UIState` n'expose jamais un champ P0 brut
4. `organisation_id` avec `s` partout (jamais `organization_id`)
5. Consolidation et analytics post-conversation uniquement
6. `DERIVED_PROVISIONAL` n'est jamais auto-upgradé
7. Désérialisation JSONB via fonction explicite - ne jamais utiliser `ConversationProgress(**raw)`
8. Toutes modifications front sur `frontend1.8` (pas `main` ni `frontend`)
9. Le front ne recalcule aucun signal pédagogique - il consomme uniquement `ui-state`

---

## PHASE 1 - AUDIT VARIABLES P0

```bash
grep -n "covered_points" backend/apps/hugo/services/conversation_progress_calculator.py
grep -n "session_history\|messages\|history" backend/apps/hugo/services/conversation_progress_calculator.py
grep -n "remaining_open_points\|overall_maturity" backend/apps/hugo/services/conversation_progress_calculator.py
```

Diagnostique: les calculs sont-ils cumulatifs (historique session) ou limités au dernier tour?
Si limités au dernier tour: bug critique, progression reste toujours rouge.

---

## PHASE 2 - AUDIT FRONT LOT 2

```bash
grep -rn "covered_points\|episode_clarity\|can_close_for_now\|remaining_open_points\|turn_state\|conversation_decision" \
  frontend1.8/src/ --include="*.js" --include="*.vue"

grep -rn "request-synthesis\|request-evaluation\|requestSynthesis\|requestEvaluation" \
  frontend1.8/src/ --include="*.js" --include="*.vue"
```

Diagnostique:
- Fallbacks P0 présents/absents
- Boutons Synthèse/Évaluation présents/absents

---

## PHASE 3 - AUDIT MEMOIRE ET OBSERVABILITE

```bash
grep -rn "consolidate_session" backend/apps/hugo/views/ --include="*.py"
grep -rn "LearnerThemeMemory\|MEMORY_INJECTION\|theme_memory" backend/apps/hugo/hugoorchestrator.py
grep -rn "record_session_signal" backend/apps/hugo/views/ --include="*.py"
```

---

## PHASE 4 - CORRECTIONS PRIORITAIRES

### Patch 1 - Supprimer fallbacks P0 dans engagement_ui_model.js

Remplacer tout fallback sur turnstate/conversation_decision par mode dégradé minimal:

```javascript
function buildDegradedDisplayModel() {
  return {
    sceneLabel: "Chargement...",
    sceneProgress: 0,
    showProgressBar: false,
    questLabel: null,
    questProgress: 0,
    maturityLabel: null,
    maturityColor: "red",
    synthesisButton: { state: "locked", label: "Continuer", visible: true, disabled: true, highlighted: false },
    evaluationButton: { state: "locked", label: null, visible: false, disabled: true, highlighted: false },
    persistentObjects: [],
  };
}
```

### Patch 2 - Brancher boutons Synthèse/Évaluation dans frontend1.8

```javascript
async function requestSynthesis(sessionId) {
  try {
    const res = await fetch(`/api/hugo/sessions/${sessionId}/request-synthesis/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
    });
    if (res.status === 400) {
      const err = await res.json();
      return { eligible: false, reason_codes: err.reason_codes };
    }
    return { eligible: true };
  } catch {
    return { eligible: false, reason_codes: ["network_error"] };
  }
}
```

### Patch 3 - Post-conversation hooks

Dans backend/apps/hugo/views/sessions.py, créer:

```python
def _post_conversation_hooks(session, progress, turn_count):
    from backend.apps.hugo.services.memory_consolidator import consolidate_session
    from backend.apps.hugo.services.quality_tracker import record_session_signal
    consolidate_session(session, progress)
    record_session_signal(session, progress, turn_count=turn_count)
```

Appeler cette fonction à la fin de chaque conversation (pas seulement generate-trace).

### Patch 4 - Feature flag injection mémoire

Dans hugoorchestrator.py (patch additif):

```python
if getattr(settings, "HUGO_MEMORY_INJECTION_ENABLED", False):
    theme_memories = LearnerThemeMemory.objects.filter(
        organisation_id=session.organisation_id,
        learner_id=session.learner_id,
        knowledge_status=KnowledgeItemStatus.VALIDATED_TRAINER.value,
    ).order_by("-updated_at")[:5]
    if theme_memories.exists():
        context["theme_memory_summary"] = [
            {"theme": m.theme_key, "status": m.knowledge_status}
            for m in theme_memories
        ]
```

---

## PHASE 5 - CREATION LOT TUTORCONDUCTPROFILES

### Objet: TutorConductProfile

Cet objet pilote les 3 modes de conduite de séance de manière administrable.
Il est DIFFERENT de TutorPrompt (personnalisation textuelle par session).
Il ne modifie pas P0.

Labels UI obligatoires (ne jamais exposer les noms techniques):
- `diagnostic` → "Séance de diagnostic"
- `reflective_afest` → "Entretien réflexif AFEST"
- `knowledge_review` → "Révision / bâchage"

### 5.1 - Modèle

```python
# Dans backend/apps/hugo/models.py
class TutorConductProfile(models.Model):
    organisation_id = models.CharField(max_length=128, db_index=True, blank=True, default="")
    # organisation_id="" = profil système fallback global
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

### 5.2 - Resolver (3 niveaux)

Créer backend/apps/hugo/services/conduct_profile_resolver.py:
1. Cherche profil actif pour (organisation_id, posture)
2. Sinon cherche profil système ("", posture)
3. Sinon fallback tutorprofiles.py statique

### 5.3 - Patch orchestrateur (additif)

Remplacer dans le bloc LOT 3:
```python
# Avant:
profile = get_profile(posture)
# Après:
from backend.apps.hugo.services.conduct_profile_resolver import resolve_conduct_profile
profile = resolve_conduct_profile(posture, str(getattr(session, "organisation_id", "")))
```

### 5.4 - Patch build_posture_block (additif)

Dans prompt_renderer.py, si system_template présent, l'utiliser à la place du builder par défaut.

### 5.5 - Endpoint CRUD

Créer backend/apps/hugo/views/conduct_profiles.py:
- ORGADMIN: voit et modifie profils de son organisation + profils système en lecture
- SUPERADMIN: voit tous les profils
- Route: /conduct-profiles/

### 5.6 - Vue front (dans frontend1.8)

Créer ConductProfilesView.vue avec:
- Liste 3 postures avec labels lisibles
- Formulaire: system_template, user_template, max_questions_per_turn, forbidden_moves, closure_policy, description
- Comparaison profil org vs profil système
- Bouton "Réinitialiser au défaut système"
- Prévisualisation du bloc posture résolu

---

## PHASE 6 - CHECKLIST DE SORTIE

```bash
# Tests backend
python -m pytest backend/apps/hugo/tests/ -v --tb=short

# Tests front
cd frontend1.8 && npm test -- --run

# Vérification P0 absent du front
grep -rn "covered_points\|episode_clarity" frontend1.8/src/ && echo "ERREUR P0" || echo "OK"

# Synthèse branchée
grep -rn "request-synthesis" frontend1.8/src/ && echo "OK" || echo "MANQUANT"

# TutorConductProfile créé
python -c "from backend.apps.hugo.models import TutorConductProfile; print('OK')"

# Orthographe organisation_id
grep -r "organization_id" backend/ --include="*.py" && echo "ERREUR orthographe" || echo "OK"
```

Produis en fin de session:
1. Rapport statut chaque critère (CONFORME / NON CONFORME / PARTIEL)
2. Liste patchs appliqués avec fichier + ligne
3. Tests résultants
4. Points en suspens à arbitrer

