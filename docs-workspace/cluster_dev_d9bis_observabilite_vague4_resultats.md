# Cluster dev — D9bis analytics LLM & observabilité avancée v1 (vague 4)

> Périmètre : D9bis backend persisté, observabilité avancée v1 SUPERADMIN, zero impact UX métier.

## Sources mobilisées

- Écarts 70/80/100, matrice cluster 2, specs canonique / compléments / interface
- `cluster_dev_fin_de_fil_qualite_observabilite_vague3_resultats.md`
- Code : `d9bis_contracts.py`, `d9bis_analytics.py`, `observability_advanced_v1.py`, `views_internal_analytics.py`

## Design retenu

### D9bis — choix d’implémentation

**Combinaison minimaliste** : modèles DB persistants + build explicite via endpoint SUPERADMIN (pas d’injection automatique dans le runtime apprenant).

| Objet | Stockage | Données autorisées |
|---|---|---|
| `ConversationTurnLLMAnalysis` | DB | bucket longueur message, indices progression dérivés, tags pédagogiques |
| `ConversationLLMAnalysis` | DB OneToOne session | agrégats CTA, maturité, compteurs tours |

**Interdits** : verbatim, P0, `llm_request_payload` / `llm_response_payload` bruts.

### Endpoints techniques (SUPERADMIN only)

| Méthode | URI | Rôle |
|---|---|---|
| POST | `/internal/hugo/sessions/{id}/d9bis/build/` | Construit/persiste D9bis |
| GET | `/internal/hugo/sessions/{id}/d9bis/export/` | JSON `d9bis_session_export_v1` |
| GET | `/internal/hugo/analytics/conversation-summary/` | Agrégats org/groupe `conversation_summary_v1` |

Observabilité de base (`session_observability_v1`) reste **ORGADMIN/SUPERADMIN**.

### Observabilité avancée v1 — métriques

- Sessions count, tours learner/assistant, durée moyenne estimée
- CTA : synthèse/évaluation demandées, blocages
- Postures : distribution, switches
- Qualité : maturité finale, dispersion, stuck_red

## Réel confirmé (local)

| Élément | Statut |
|---|---|
| Modèles D9bis | **RÉEL OBSERVÉ** — migration `0019_d9bis_analytics_models` |
| Build/export D9bis | **RÉEL OBSERVÉ** — SUPERADMIN, tenant-scoped |
| Conversation summary | **RÉEL OBSERVÉ** — SUPERADMIN only |
| UIState / exports métier | **Absents D9bis** — tests absence |
| Front `/app` | **Inchangé** — zero consommation analytics |

## Cible 2.0 vs Couronne

| Élément | Statut |
|---|---|
| D9bis backend QA/ops | **RÉEL OBSERVÉ** local |
| Analytics LLM exposées produit | **CIBLE / Couronne** |
| Dashboards observabilité | **CIBLE / Couronne** |
| Scoring LLM temps réel | **CIBLE / Couronne** |

## Garde-fous

- `is_superadmin()` sur D9bis et conversation-summary
- `assert_d9bis_payload_clean()` avant export
- Exports Qualiopi / trace_rich_v1 / pivot : pas de branchement D9bis

## Prochaine sortie utile

- Campagne tests : `cluster_tests_d9bis_observabilite_vague4_resultats.md`
- Oracle Encoors sur endpoints SUPERADMIN
