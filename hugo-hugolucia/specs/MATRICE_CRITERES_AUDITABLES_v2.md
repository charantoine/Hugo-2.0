# Matrice de critères auditables — Hugo 1.9 v2

**Version :** 2.0 — 1 juin 2026
**Nouveautés :** CRIT-031/032 (variables P0 cumulatives), CRIT-033 à 036 (TutorConductProfiles), CRIT-037 à 042

---

## Légende

| Symbole | Signification |
|---|---|
| Conforme | OK (audit 19/05) |
| Bloquant | Non conforme, bloque le fonctionnement |
| Partiel | Implémenté mais incomplet |
| A créer | Nouveau lot à implémenter |
| A vérifier | Non vérifiable sans Postgres actif |

---

## Groupe 1 — Sécurité et multi-tenant

| ID | Critère | Commande de vérification | Preuve attendue | Statut |
|---|---|---|---|---|
| CRIT-001 | RLS transactionnel app.organisation_id | grep -r "SET LOCAL" backend/ | TenantRLSMiddleware pose SET LOCAL | Partiel |
| CRIT-002 | Isolation cross-tenant sous Postgres | pytest tests/cross_tenant.py | Tests verts, 404 pas 403 | A vérifier Bloquant |
| CRIT-003 | Gel P0 — aucun commit sur turn_state_v17.py | git log -- turn_state_v17.py decision_engine_v17.py | Zéro modification directe | Partiel |

---

## Groupe 2 — Contrats de données (LOT 0)

| ID | Critère | Commande | Preuve | Statut |
|---|---|---|---|---|
| CRIT-004 | Enums canoniques dans conversation_profile.py | pytest test_p0_non_regression.py::NR-09 | Test vert | Conforme |
| CRIT-005 | UIState sans champ P0 brut | pytest test_p0_non_regression.py::NR-07 | Test vert | Conforme (back) / Bloquant (front) |
| CRIT-006 | organisation_id avec s dans migrations | grep -r "organisation_id" migrations/ | Aucun organization_id | Conforme |

---

## Groupe 3 — Progression conversationnelle (LOT 1)

| ID | Critère | Commande | Preuve | Statut |
|---|---|---|---|---|
| CRIT-007 | Endpoint /progress cohérent | curl /api/hugo/sessions/{id}/progress/ | JSON avec overall_maturity, active_branches | Conforme |
| CRIT-008 | Endpoint /ui-state cohérent | curl /api/hugo/sessions/{id}/ui-state/ | JSON avec scene_label, synthesis_button_state | Conforme |
| CRIT-031 | covered_points cumulatif (pas par tour) | grep -n "covered_points" conversation_progress_calculator.py | Valeur croît sur l'historique session | A vérifier CRITIQUE |
| CRIT-032 | overall_maturity cohérent avec P0 session_maturity | Lire les deux calculs | Pas de contradiction RED/ORANGE/GREEN | A vérifier |

---

## Groupe 4 — Adaptateur UI (LOT 2)

| ID | Critère | Commande | Preuve | Statut |
|---|---|---|---|---|
| CRIT-009 | Front sans fallback P0 | grep -rn "covered_points\|episode_clarity\|can_close_for_now" frontend1.8/src/ | Aucun résultat | Bloquant |
| CRIT-010 | Panneau progression visible | Lire composants + routes | Progression / scènes / quêtes visibles | Conforme |
| CRIT-011 | Bouton Synthèse branché | grep -rn "request-synthesis\|requestSynthesis" frontend1.8/src/ | Appel réseau observable | Bloquant |
| CRIT-012 | Bouton Évaluation branché | grep -rn "request-evaluation\|requestEvaluation" frontend1.8/src/ | Appel réseau observable | Bloquant |

---

## Groupe 5 — Modes de conduite (LOT 3 + TutorConductProfiles)

| ID | Critère | Commande | Preuve | Statut |
|---|---|---|---|---|
| CRIT-013 | set-posture réel et testé | pytest test_posture_modes.py | Tests verts | Conforme |
| CRIT-014 | synthesisservice.py appel LLM réel | Lire generate_synthesis() | Appel LLM effectif | Bloquant (stub) |
| CRIT-033 | TutorConductProfile modèle créé | python -c "from hugo.models import TutorConductProfile; print('OK')" | Import OK | A créer |
| CRIT-034 | conduct_profile_resolver.py résolution 3 niveaux | pytest test_conduct_profiles.py | 5 tests verts | A créer |
| CRIT-035 | ConductProfilesView.vue dans frontend1.8 | Lire routes front | Vue accessible ORGADMIN | A créer |
| CRIT-036 | system_template injecté dans build_posture_block() | Lire prompt_renderer.py | Condition présente | A créer |

---

## Groupe 6 — Mémoire thématique (LOT 4)

| ID | Critère | Commande | Preuve | Statut |
|---|---|---|---|---|
| CRIT-015 | Consolidation post-conversation (pas seulement generate-trace) | grep -rn "consolidate_session" views/ | Appelé hors GenerateTraceView | Bloquant |
| CRIT-016 | Injection LearnerThemeMemory dans contexte | grep -rn "LearnerThemeMemory\|MEMORY_INJECTION" hugoorchestrator.py | Feature flag + injection présents | Bloquant (absent) |
| CRIT-037 | Feature flag HUGO_MEMORY_INJECTION_ENABLED | grep -r "MEMORY_INJECTION" backend/ | Présent dans settings et orchestrateur | A créer |

---

## Groupe 7 — Base connaissances formateur (LOT 5)

| ID | Critère | Commande | Preuve | Statut |
|---|---|---|---|---|
| CRIT-017 | Validation humaine TrainerKnowledgeItem | pytest test_trainer_knowledge.py | Tests verts | Conforme |
| CRIT-018 | UI trainer dédiée | Lire routes front | TrainerKnowledgeView.vue présente | Bloquant (absent) |

---

## Groupe 8 — Observabilité cohorte (LOT 6)

| ID | Critère | Commande | Preuve | Statut |
|---|---|---|---|---|
| CRIT-019 | Signaux qualité post-session | grep -rn "record_session_signal" views/ | Appelé au même endroit que consolidate_session | Partiel |
| CRIT-038 | Double appel consolidate + record synchronisé | Lire point d'appel commun | Fonction _post_conversation_hooks présente | A créer |

---

## Groupe 9 — Administration des comptes

| ID | Critère | Commande | Preuve | Statut |
|---|---|---|---|---|
| CRIT-020 | ORGADMIN CRUD apprenants scopé org | Lire permissions + UI | Vue avec création/suppression apprenants | Partiel |
| CRIT-021 | SUPERADMIN technique (pas contenu pédagogique) | Lire API + front | Pas d'API front cross-org avec contenu apprenant | Partiel |
| CRIT-039 | Interface ORGADMIN création apprenants et tuteurs | Lire routes frontend1.8 | Vue ORGADMIN complète | A créer |
| CRIT-040 | Interface tuteur consignes pédagogiques | Lire routes frontend1.8 | Vue tuteur avec édition TutorPrompt groupe | A créer |

---

## Groupe 10 — Tests et qualité

| ID | Critère | Commande | Preuve | Statut |
|---|---|---|---|---|
| CRIT-023 | Tests front exécutables | cd frontend1.8 && npm test -- --run | 14/14 verts | Conforme |
| CRIT-024 | Tests backend exécutables | python -m pytest backend/ -v --tb=short | 19/21 verts (2 SQLite normaux) | Conforme |
| CRIT-025 | Campagne Playwright configurée | find . -name "playwright.config*" | Config versionnée + tests E2E | Bloquant (absent) |
| CRIT-041 | Tests test_conduct_profiles.py verts | pytest test_conduct_profiles.py | 5 tests verts | A créer |
| CRIT-042 | Test P0 variables cumulatives | pytest -k "cumulative" test_conversation_progress.py | covered_points croît correctement | A créer |

---

## Commande d'audit global à lancer dans Cursor

```bash
echo "=== 1. ENUMS CANONIQUES ==="
python -m pytest backend/apps/hugo/tests/test_p0_non_regression.py -k "NR-09" -v

echo "=== 2. VARIABLES P0 CUMULATIVES - CRITIQUE ==="
grep -n "covered_points" backend/apps/hugo/services/conversation_progress_calculator.py
grep -n "session_history\|messages\|history" backend/apps/hugo/services/conversation_progress_calculator.py
echo "-> Vérifier si le calcul est cumulatif ou limité au dernier tour"

echo "=== 3. FRONT - FALLBACK P0 INTERDIT ==="
grep -rn "covered_points\|episode_clarity\|can_close_for_now\|remaining_open_points" \
  frontend1.8/src/ --include="*.js" --include="*.vue"

echo "=== 4. SYNTHESE/EVALUATION BRANCHEES ==="
grep -rn "request-synthesis\|request-evaluation\|requestSynthesis\|requestEvaluation" \
  frontend1.8/src/ --include="*.js" --include="*.vue"

echo "=== 5. CONSOLIDATION POST-SESSION ==="
grep -rn "consolidate_session\|record_session_signal" backend/apps/hugo/views/ --include="*.py"

echo "=== 6. INJECTION MEMOIRE ==="
grep -rn "LearnerThemeMemory\|MEMORY_INJECTION" backend/apps/hugo/hugoorchestrator.py

echo "=== 7. TUTORCONDUCTPROFILE - NOUVEAU ==="
python -c "from backend.apps.hugo.models import TutorConductProfile; print('OK TutorConductProfile')" 2>&1 || echo "ABSENT - a creer"

echo "=== 8. ORTHOGRAPHE ORGANISATION_ID ==="
grep -r "organization_id" backend/ --include="*.py" && echo "ERREUR orthographe" || echo "OK"

echo "=== 9. TESTS ==="
python -m pytest backend/apps/hugo/tests/ -v --tb=short 2>&1 | tail -20
cd frontend1.8 && npm test -- --run 2>&1 | tail -10
```

