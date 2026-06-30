# A2 — Cartographie fonctionnelle existante

**Date :** 22 juin 2026  
**Méthode :** domaines alignés sur `cluster2_matrice_runtime_vs_cible.md` et fichiers `ecarts — <domaine>.md`.

Pour chaque domaine : **RÉEL OBSERVÉ** sauf mention contraire.

---

## 1. Conversation apprenant

### Ce qui existe réellement

- Création session : `POST /hugo/sessions/` (groupe + `tutor_prompt_id` optionnel).
- Chat : `POST .../messages/` et `POST .../messages/stream/` (SSE avec fallback).
- Pipeline complet `build_hugo_turn` : contexte → P0 → décision → prompt → LLM → guardrails.
- Postures : diagnostic, réflexif, bûchage ; résolution via `resolve_posture` + profils globaux (`LearnerConversationGlobalProfile`, juin 2026).
- Bascule posture prod : `PostureSelector.vue` + `POST .../set-posture/` (cluster 15–16).

### Surfaces visibles

- Parcours `/app` : `ProdLearnerHomeView`, `ProdLearnerWorkspace`, `HugoProgressPanel`.
- Bandeau scène : `LearnerSceneContextBar.vue`.
- Mode testeur : `LearnerDetailView.vue` (~2400 lignes) — debug TurnState si `VITE_P0_DEBUG_ENABLED`.

### Backends / endpoints

| Endpoint | Rôle |
|----------|------|
| `GET/PATCH /hugo/sessions/{id}/` | Détail session |
| `GET/POST .../messages/` | Historique / envoi |
| `POST .../messages/stream/` | SSE |
| `GET .../ui-state/` | Contrat produit |
| `POST .../set-posture/` | Bascule posture |

### Statut de vérité

**RÉEL OBSERVÉ** (local) — **A_VERIFIER** (Encoors, SSE, flags P0).

### Limites

- TurnState / P0 bruts absents du parcours `/app`.
- v17 et classifieur P0 off par défaut local.
- Matrice états bascule SW-xx (cible interface 2.0) non implémentée.

### Dépendances

- LLM (Ollama ou OVH selon groupe/session).
- TutorPrompt ou profil global résolu.
- Flags `HUGO_P0_*`.

### Documents à relire

- `02_ETAT_MOTEUR_REEL.md` §4
- `ecarts —10_runtime_p0_progression_uistate.md`
- `cluster16_interface_apprenant_spec_conformite_resultats.md`

---

## 2. Progression

### Ce qui existe réellement

- `build_conversation_progress`, `build_conversation_progress_contract`.
- Branches, `priority_branch_id`, maturité `RED/ORANGE/GREEN` (`SessionMaturityLevel`).
- `reason_codes`, `missing_for_next_level`, dispersion (`dispersion_risk`).
- Phase session : `current_phase`, `phase_decider` + classifieur LLM phase.
- 5 jalons internes moteur vs 3 macro-scènes UI (`progressionLabels.js`).

### Surfaces visibles

- Panneau progression : scène, quêtes, maturité, barres (profil gamification A/B/C).
- Liste sessions : libellés phase résumés.

### Backends

- Persisté sur `HugoSession` (phase, progress JSON).
- Exposé via `ui-state` : `scene_label`, `scene_progress`, `quest_progress`, `maturity_color`.

### Statut

**RÉEL OBSERVÉ** — mapping 5 jalons → 3 scènes = **ÉCART CONFIRMÉ** documentaire (pas bug).

### Limites

- Verrou phase/tours partiel sur bascule posture.
- `recalc_learner_state` Celery = placeholder vide.

### Documents

- `ecarts —10_runtime_p0_progression_uistate.md`
- `variables_prompting.md`

---

## 3. UIState

### Ce qui existe réellement

- `build_contract_ui_state` dans `ui_state_builder.py`.
- Endpoint `GET /hugo/sessions/{id}/ui-state/?gamification_profile=`.
- CTA synthèse/évaluation : `cta_ui_state.py`, états `locked/ready/...`.
- `conversation_mode`, `allowed_posture_transitions`, `dispersion_risk`.
- `learner_display_profile` (cascade session → groupe → org).
- Advisory évaluation : `ui.advisory` (cluster 16).

### Surfaces

- `engagementUiModel.js` → `HugoProgressPanel.vue`.
- État dégradé si ui-state indisponible (`isDegraded: true`).

### Statut

**RÉEL OBSERVÉ** — double builder (`build_ui_state` vs `build_contract_ui_state`) = **ÉCART CONFIRMÉ** confusion doc.

### Limites

- Mémoire absente du contrat UIState (distinct panneau API).
- CTA × posture : libellés identiques (cible : variation par posture).

### Documents

- `cluster4_surface_contracts.md`
- `ecarts — 31_front_apprenant_postures_et_bascule.md`

---

## 4. Mémoire

### Ce qui existe réellement

- **Intra-conversation :** `build_session_memory`, `SessionMemoryContract`, injecté dans orchestrateur.
- **API :** `GET /hugo/sessions/{id}/memory-summary/` (schéma plat).
- **UI :** `LearnerMemoryPanel.vue` (troncature, vouvoiement).
- **Inter-sessions :** `LearnerThemeMemory`, `memory_consolidator.py`, consolidation après chaque message.

### Ce qui n'existe pas (confirmé)

- Injection `LearnerThemeMemory` dans `build_hugo_turn` — **ÉCART CONFIRMÉ**.
- Injection `session_memory` dans templates prompt (`prompt_renderer.py`) — **ÉCART CONFIRMÉ** lot courant.

### Statut

**RÉEL OBSERVÉ PARTIEL** — stockage inter-session oui ; consommation tour non.

### Documents

- `ecarts — 20_memoire_gouvernee.md`
- `contrat_api_memory_summary_v1.md`
- `20_memoire_gouvernee_note_lot_courant_memoire_intra_conversation.md`

---

## 5. RAG / bibliothèque documentaire

### Ce qui existe réellement

- `apps/library/` : upload, `index_document` (chunks 500 car., **sans embedding**).
- `select_rag_chunks`, `should_use_rag` — sélection **lexicale**.
- Citations produit : `rag_citations`, badge « Appui ».
- Gating par profil conducteur / posture.
- Corpus démo : `RAG Melec/` (données, pas runtime).

### Surfaces

- Admin testeur : bibliothèque groupe (`/groups-admin/:groupId`).
- Apprenant : citations dans chat si chunks sélectionnés.

### Statut

**RÉEL OBSERVÉ** lexical — RAG vectoriel = **CIBLE** (pgvector inactif).

### Documents

- `ecarts — 30_referentiel_documentaire_rag.md`

---

## 6. Synthèse

### Ce qui existe réellement

- `POST /hugo/sessions/{id}/request-synthesis/`.
- `synthesis_service.py` : LLM + fallback heuristique (pas stub).
- Éligibilité via progression + `reason_codes` (`synthesis_eligible`, etc.).
- Bouton piloté par `synthesis_button_state` dans ui-state.

### Statut

**RÉEL OBSERVÉ** local — **A_VERIFIER** Encoors.

### Limites

- Prompts synthèse admin absents (hardcodé `synthesis_service.py`) — **CIBLE**.

---

## 7. Évaluation

### Ce qui existe réellement

- `POST .../request-evaluation/`, `POST .../finalize-evaluation/`.
- `GET .../evaluation-readiness/` (local ; **absent Encoors** inspection 12/06).
- `LearnerEvaluationRecord`, `EvaluationPolicy`, workflow LLM.
- Garde-fous maturité : `evaluation_blocked_maturity`, `evaluation_eligible`.
- CTA advisory front cluster 16.

### Statut

**RÉEL OBSERVÉ PARTIEL** — pas de certification autonome (doctrine respectée).

### Limites

- `EvaluationTrace` doctrinal = agrégat conceptuel + pivot `evaluation_trace_pivot_v1`, pas objet unique.
- Policies évaluation groupe : backend oui, UI org-level surtout.

### Documents

- `ecarts — 70_evaluation_traces_preuves.md`
- `mapping_EvaluationTrace_runtime_local.md`

---

## 8. Traces / preuves / partages

### Ce qui existe réellement

- `Trace`, `TraceCriterionAssessment`, `Evidence`.
- `POST .../generate-trace/` — payload **minimal** (messages_count, listes vides).
- `POST .../share/` — flags partage résumé/preuves/verbatim.
- `GET /learners/traces/`, `GET /learners/evidence/`.

### Statut

**RÉEL OBSERVÉ PARTIEL** — génération trace pauvre = **ÉCART CONFIRMÉ**.

### Documents

- `ecarts — 70_evaluation_traces_preuves.md`
- `fiche_trace_exploitable_pivot_v1.md`

---

## 9. Tuteur

### Ce qui existe réellement

- `DashboardTimelineView`, route `/app/tutor` (cluster 3 B1-01).
- Lecture progression, synthèse/éval partageables.
- Verbatim masqué si non partagé (oracle test).
- Analytics cohorte partiel (`cohort_dashboard.py`).

### Surfaces

- Timeline tuteur — **PARTIEL** vs cible orchestrateur tuteur 2.0.
- Pas de service homonyme `TutorOrchestrator`.

### Statut

**RÉEL OBSERVÉ PARTIEL** local — **A_VERIFIER** Encoors.

### Documents

- `ecarts — 60_orchestrateur_tuteur.md`

---

## 10. Formateur

### Ce qui existe réellement

- `TrainerKnowledgeItem`, `views_trainer.py`.
- Surfaces `/app/trainer/knowledge`, élicitation atelier V0.
- Workflow validate/reject/provisional/edit (cluster 15).
- Ingestion documentaire liée à `library`.

### Statut

**RÉEL OBSERVÉ PARTIEL+** — script F1–F4 non prouvé bout-en-bout.

### Limites

- Lien item formateur → RAG apprenant runtime : **A_VERIFIER**.

### Documents

- `ecarts — 40_base_connaissances_formateur.md`
- `ecarts — 50_orchestrateur_formateur.md`
- `cluster15_interfaces_apprenant_formateur_resultats.md`

---

## 11. Administration

### Ce qui existe réellement

- Users : création/édition (`UsersView`) — **pas DELETE**.
- Groupes, référentiels, import RNCP.
- `TutorPromptsView`, `ConductProfilesView` (mode testeur).
- `LearnerConversationProfilesView` — profils globaux apprenant (20/06).
- `OvhLlmView`, hub `/admin/conversation`.
- Multi-org : `OrgTenantSwitcher` (SUPERADMIN).

### Statut

**RÉEL OBSERVÉ** — admin comptes incomplet vs cible 2.0.

---

## 12. Exports

### Ce qui existe réellement

- `POST /exports/run/` — CSV/JSON synchrone.
- `EvidenceBundleView` — ZIP Qualiopi lite.
- `trainer/evaluation-records/export/`.
- Permissions `is_admin_like` / `isOrgAdminLike` (cluster dev vague 2).
- Pivot `trace_rich_v1` + export E2E (vague 5).

### Statut

**RÉEL OBSERVÉ** local — **A_VERIFIER** Encoors.

### Documents

- `ecarts — 100_exports_preuves_qualiopi_lite.md` (si présent) ou domaine 100 dans cluster 2
- `design_D2-M06_D2-M11_exports_analytics.md`

---

## 13. Observabilité / qualité

### Ce qui existe réellement

- `ConversationQualitySignal`, `quality_tracker.py`, `record_session_signal` post-message.
- `analytics_state` JSON session.
- `/internal/.../observability/` (ORGADMIN+).
- `/internal/hugo/analytics/conversation-summary/` (SUPERADMIN).
- `ConversationTurnLLMAnalysis` — export SUPERADMIN (D9bis partiel).

### Statut

**RÉEL OBSERVÉ PARTIEL** — catalogue signaux canonique = **CIBLE**.

### Documents

- `ecarts — 80_observabilite_qualite_conversationnelle.md`

---

## 14. Surfaces debug / techniques

### Ce qui existe réellement

- `/internal/hugo/sessions/{id}/turn-review/`.
- `POST /internal/rag/search/`.
- Modales TurnState / ConversationDecision (testeur + `p0_debug`).
- Override `PATCH .../phase/`, `PATCH .../classifier-config/`.
- `HUGO_DEBUG_TRACING` si DEBUG.

### Statut

**RÉEL OBSERVÉ** — réservé calibration, hors démo client.

### Interdits produit

- Exposition P0 brut, verbatim complet comme « mémoire », diagnostics non validés au front `/app`.

---

*Sources : 02, 03, cluster2 v6, ecarts par domaine, clusters 15–16. Cible 2.0 utilisée uniquement pour comparaison implicite via écarts.*
