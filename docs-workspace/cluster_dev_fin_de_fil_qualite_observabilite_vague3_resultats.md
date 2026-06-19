# Cluster dev — fin de fil, qualité et observabilité de base (vague 3)

> Périmètre : pivot EvaluationTrace minimal (70/100), observabilité de base (80), préparation D9bis sans exposition produit.

## Sources mobilisées

- `ecarts — 70_evaluation_traces_preuves.md`, `ecarts — 80_observabilite_qualite_conversationnelle.md`, `ecarts — 100_exports_preuves_qualiopi_lite.md`
- `cluster2_matrice_runtime_vs_cible.md`, `mapping_EvaluationTrace_runtime_local.md`
- `cluster_dev_encadrants_exports_vague2_resultats.md`, `cluster_tests_encadrants_exports_post_vague2_resultats.md`
- Code `hugo_back` : models, views_sessions, exports, views_internal

## Réel confirmé (local)

### EvaluationTrace pivot (`evaluation_trace_pivot_v1`)

| Élément | Détail |
|---|---|
| Builder | `apps/hugo/services/evaluation_trace_pivot.py` — `build_evaluation_trace_pivot`, `enrich_trace_payload_with_pivot` |
| Schéma | `evaluation_trace_pivot_v1` — session, evaluation_record, trace, evidence[], human_validation, certification_disclaimer |
| Intégration generate-trace | `GenerateTraceView` enrichit `payload_structured` + retourne `evaluation_trace_pivot_v1` |
| Intégration ExportRun JSON | `_build_json_response` ajoute pivot dans `payload_structured` et clé top-level par trace |
| Modèle unique EvaluationTrace 2.0 | **Non** — pivot JSON agrégateur, objets existants inchangés |

### Observabilité de base (domaine 80)

| Signal | Emplacement |
|---|---|
| Compteurs CTA bloqués | `analytics_state.cta_evaluation_blocked_count`, `cta_synthesis_blocked_count` |
| Snapshot session | `build_session_observability_snapshot` — tours, CTA, analytics_state, quality_signal |
| Endpoint admin | `GET /internal/hugo/sessions/{id}/observability/` — ORGADMIN/SUPERADMIN only |
| Exposition UIState apprenant | **Absente** (confirmé tests) |

### D9bis (Couronne — squelettes CIBLE)

| Élément | Statut |
|---|---|
| `apps/hugo/domain/d9bis_contracts.py` | TypedDict `ConversationTurnLLMAnalysisContract`, `ConversationLLMAnalysisContract` |
| Modèle DB / runtime produit | **Absent** — non branché |
| UIState / exports métier | **Absents** — tests d'absence dédiés |

## Cible 2.0 (rappel)

- EvaluationTrace doctrinale = agrégat complet, validation humaine, export structuré — **partiellement convergé** via pivot minimal.
- Observabilité avancée, dashboards cohorte, catalogue signaux canonique — **Couronne**.
- D9bis export analytique LLM — **Couronne**, priorisation CTO explicite requise.

## Écarts restants

| Écart | Statut |
|---|---|
| Payload generate-trace legacy (criteria/modalities vides) | **PARTIEL** — pivot ajouté, richesse métier encore minimale |
| EvaluationTrace 2.0 modèle unique | **CIBLE** — pivot ≠ agrégat complet |
| Catalogue signaux observabilité | **CIBLE** |
| D9bis runtime | **CIBLE** |
| Prod Encoors fin de fil / observabilité | **A_VÉRIFIER** |

## Garde-fous respectés

- Pas de changement UX apprenant.
- Pas d'explicit LLM analysis dans UIState ni exports métier.
- EvidenceBundle reste lite (métadonnées traces).
- Disclaimer non certifiant dans le pivot.

## Prochaine sortie utile

- Campagne tests archivée : `cluster_tests_fin_de_fil_qualite_observabilite_vague3_resultats.md`
- Mises à jour écarts 70/80/100, matrice cluster 2, specs interface / canonique
