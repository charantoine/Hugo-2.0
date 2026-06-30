# Cluster 2 — Matrice runtime ↔ cible Hugo 2.0

**Workspace :** `/Users/machin/Desktop/Zone de travail Hugo`  
**Version :** 6 (post-profils globaux apprenant — 2026-06-20)  
**V5 :** post-cluster 16 — 2026-06-18 · **V4 :** post-tests cluster 15 · **V3 :** 2026-06-18 · **V2 :** 2026-06-16 · **V1 :** même date  
**Méthode :** `00_HIERARCHIE_DOCUMENTAIRE.md`, `DOC_METHODO_REFERENCE_CONVERGENCE_HUGO_REVISE.md`, `plan_documentation_cto_convergence_hugo.md`, `synthese_globale_ecarts_par_domaine.md`, écarts 10–120, glossaire, `02`–`05`, `07`–`10`, code `hugo_back` + `hugo-hugolucia/frontend_1.8`.

> **Référence trajectoire CTO :** voir `plan_documentation_cto_convergence_hugo.md`, section  
> **« Trajectoire de convergence – étapes 5 à 8 (vague encadrants & couronne) »**.

> **Note fichier d’écarts domaine 10 :** le rapport existe sous `ecarts —10_runtime_p0_progression_uistate.md` (sans espace après `—`).

### Légendes

| Symbole / tag | Signification |
|---------------|---------------|
| **CIBLE** | Spec 2.0 / compléments ; non prouvé livré |
| **RÉEL OBSERVÉ** | Code local + tests ou audit produit vérifiables |
| **ÉCART CONFIRMÉ** | Divergence recoupée et documentée |
| **A_VÉRIFIER** | Dépend prod Encoors, flag, RLS ou environnement non inspecté |
| **HYPOTHÈSE** | Recommandation de replay / choix, non prouvée |
| **IMPLÉMENTÉ** | Vérifiable dans code local + tests |
| **CREDIBLE** | Cohérent avec code/docs mais preuve partielle |
| **PARTIEL** | Couverture incomplète |
| **ABSENT_NOUVEAU_CONTRAT** | Cible identifiée ; contrat à produire |

| Statut doc | Signification |
|------------|---------------|
| **ALIGNE** | Réel et cible raccordés |
| **ALIGNE_DOC_PARTIEL** | Bon alignement ; noms réels sous-documentés |
| **RENOMMER_DANS_DOC** | Pont glossaire à formaliser |
| **PARTIEL** | Couverture incomplète |
| **ABSENT_NOUVEAU_CONTRAT** | Cible identifiée ; contrat à produire |
| **A_VÉRIFIER** | Preuve insuffisante |

**Colonnes standard (tableaux domaine) :** Nom doctrinal 2.0 · Nom(s) réel(s) · Niveau vérité · Sources · Statut doc · Action · Justification courte

---

## 0. Synthèse transversale cluster 2 (V6 — post-profils globaux — 2026-06-20)

| Domaine | Intitulé | Alignement | Lacune principale | Preuve dominante |
|---------|----------|------------|-------------------|------------------|
| **10** | runtime / P0 / progression / UIState | Fort backend + CTA + scène UIState | Double stack UIState ; v17 A_VÉRIFIER | `test_cluster4`, `test_cluster16_interface_apprenant_backend.py` |
| **20** | mémoire gouvernée intra-conversation | Contract + API + panneau **PARTIEL+** | Pas injection prompt ; inter-sessions hors tour | `test_session_memory_contract.py`, B16-M1/M2, C16 Playwright |
| **30** | référentiel documentaire / RAG | Lexical opérationnel | pgvector inactif ; hiérarchie contexte non contractualisée | `test_rag_support_tracing.py` |
| **31** | front apprenant postures & bascule | CTA + profils + posture/scène **PARTIEL+** ; **admin profils globaux OK** | Matrice SW-xx ; verrou phase/tours ; synthèse/starter prompts sans admin | `PostureSelector.vue`, cluster 16 ; **`test_learner_conversation_global_profile.py`** |
| **40** | base connaissances formateur | Objets + workflow API C15 | Lien RAG runtime A_VÉRIFIER | `test_cluster15_interfaces_formateur.py` |
| **50** | orchestrateur formateur | API élicitation + atelier V0 | Script F1–F4 non prouvé bout-en-bout | C15 formateur tests |
| **60** | orchestrateur tuteur | Backend riche ; B1-01 vert | Surface métier tuteur partielle | `test_cluster3_oracles.py` |
| **70** | évaluation / traces / preuves | Branche terminale + CTA advisory UI ; slot eval dans profil global | Payload trace minimal ; policies **groupe** sans UI dédiée | `test_request_evaluation_guard.py`, B16-C2, profil global |
| **80** | observabilité / qualité conversationnelle | Signaux présents | Catalogue signaux ABSENT ; D9bis CIBLE | `test_observabilite_base.py` |
| **90** | confidentialité / multi-tenant / rôles | Doctrine + tests locaux + **Playwright tenant 11/11** | RLS prod A_VÉRIFIER ; CI strict partiel | `test_d2_m07`, cluster 3, `tenant_personas.spec.ts` |
| **100** | exports / preuves / Qualiopi lite | Objets réels testés | Encoors A_VÉRIFIER | `test_d2_m06_d2_m11`, D1-02 |
| **110** | interfaces formateur / tuteur | Apprenant **PARTIEL+ C16** ; formateur C15 ; **admin convo profils globaux** | Tuteur prod ; IFT-042 choix profil ; trous synthèse/orchestrateur | cluster 16 ; **`LearnerConversationProfilesView.vue`** ; Playwright pipeline |
| **120** | intercalaires v1 | CIBLE cadrée | Aucune feature observée runtime local | `audit_domaine_120`, ecarts-120 |

> **V5 (18/06)** : voir historique §18. **V6** intègre `LearnerConversationGlobalProfile`, admin `/admin/conversation/learner/profiles`, affectation groupe, résolution runtime avec fallback legacy — preuves §19.

### Taxonomie des sorties (cluster 2 — à ne pas confondre)

| Catégorie | Exemples réels / cibles | Surfaces autorisées | Niveau vérité typique |
|-----------|-------------------------|---------------------|------------------------|
| **État produit dérivé** | UIState, CTA, badges RAG | Apprenant `/app` | IMPLÉMENTÉ (partiel) |
| **Mémoire gouvernée API** | memory-summary, SessionMemoryContract | API ; pas panneau prod | IMPLÉMENTÉ |
| **Export métier** | Trace, Evidence, synthèse partagée, LearnerEvaluationRecord | Apprenant, tuteur (filtré), trainer | IMPLÉMENTÉ / PARTIEL |
| **Bundle audit** | EvidenceBundleView ZIP | ORGADMIN, auditeur | IMPLÉMENTÉ — contenu A_VÉRIFIER |
| **Export run CSV/JSON** | `apps/exports` ExportRun | ORGADMIN | CREDIBLE |
| **Export technique debug** | export-md, turn-review, modales P0 | Testeur, superadmin **uniquement** | CIBLE / PARTIEL |
| **Artefact analytique LLM** | ConversationTurnLLMAnalysis | Superadmin debug **uniquement** | CIBLE — ABSENT_NOUVEAU_CONTRAT |
| **Intercalaire pédagogique V1** | SessionInterstitial (conceptuel) | Apprenant passif | CIBLE — ABSENT_NOUVEAU_CONTRAT |

---

## 1. Domaine 10 — runtime / P0 / progression / UIState

**Écart domaine :** `ecarts —10_runtime_p0_progression_uistate.md`

### 1.1 P0 et TurnState

| Nom doctrinal 2.0 | Nom(s) réel(s) | Niveau | Sources | Statut doc | Action | Justification |
|-------------------|----------------|--------|---------|------------|--------|---------------|
| P0 classifieur tour | `classify_p0_turn_state`, `p0_classifier.py` | IMPLÉMENTÉ | `p0_classifier.py`, tests | ALIGNE_DOC_PARTIEL | D2-M10 flag doc | Tests présents |
| TurnState | `TurnState`, `analyze_turn_state` | IMPLÉMENTÉ | `schemas.py`, orchestrateur | ALIGNE | — | — |
| TurnState v17 | `turn_state_v17`, `reconcile_turn_state_v17` | CREDIBLE | Code ; `HUGO_P0_V17_ENABLED` | A_VÉRIFIER | D2-M10 | Flag non audité prod |
| P0 hors surface produit | Front `/app` sans TurnState | IMPLÉMENTÉ | `03_ETAT_PRODUIT_REEL` | ALIGNE | — | Confirmé |
| Phase session | `current_phase`, `phase_decider` | IMPLÉMENTÉ | models, override view | ALIGNE | — | — |

### 1.2 DecisionContract / ConversationProgress / UIState

| Nom doctrinal 2.0 | Nom(s) réel(s) | Niveau | Sources | Statut doc | Action | Justification |
|-------------------|----------------|--------|---------|------------|--------|---------------|
| DecisionContract | `ConversationDecision`, `decide_conversation` | IMPLÉMENTÉ | `decision_engine.py` | RENOMMER_DANS_DOC | Glossaire D2 | Nom réel stable |
| ConversationProgress | `build_conversation_progress_contract` | IMPLÉMENTÉ | calculator, tests | ALIGNE | D2-M02 | Branches + maturité |
| UIState produit | `build_contract_ui_state`, `GET ui-state/` | IMPLÉMENTÉ | `ui_state_builder`, tests CTA | ALIGNE | — | — |
| Double builder UIState | `build_ui_state` vs `build_contract_ui_state` | PARTIEL | orchestrateur | ALIGNE_DOC_PARTIEL | DOC | **ÉCART CONFIRMÉ** confusion doc |
| `conversation_mode` UIState | `_build_conversation_mode` + `allowed_posture_transitions` | IMPLÉMENTÉ | cluster4, **cluster 16** | ALIGNE | **D2-M01 livré C4/C16** | Distinct domaine 31 rendu |
| `learner_display_profile` | query param + cascade groupe/org + CSS 3 profils | **IMPLÉMENTÉ** | cluster4, C15/C16 Playwright | ALIGNE_DOC_PARTIEL | IFT-042 | Même contenu 3 profils ; style différencié |
| CTA synthèse / éval | `cta_*`, lot 1 ; **`ui.advisory`** éval | IMPLÉMENTÉ | `cta_ui_state.py`, B16-C2 | ALIGNE | — | Backend-driven |
| CTA × posture (libellés) | Libellés identiques | PARTIEL | `cta_ui_state` | ABSENT_NOUVEAU_CONTRAT | D2-M02 | CIBLE variation messages |
| Scène / dispersion UIState | `dispersion_risk`, `priority_branch_label` | **IMPLÉMENTÉ** | cluster 16, `ui_state_builder` | ALIGNE | — | Bandeau `LearnerSceneContextBar` |
| Sélecteur posture prod | `PostureSelector.vue` | **PARTIEL+** | cluster 15/16, Playwright 10/10 | ALIGNE_DOC_PARTIEL | S16-A2 manuel | Transitions backend ; Encoors A_VÉRIFIER |

---

## 2. Domaine 20 — mémoire gouvernée intra-conversation

**Écart domaine :** `ecarts — 20_memoire_gouvernee.md` · **Note lot :** `20_memoire_gouvernee_note_lot_courant_memoire_intra_conversation.md`

| Nom doctrinal 2.0 | Nom(s) réel(s) | Niveau | Sources | Statut doc | Action | Justification |
|-------------------|----------------|--------|---------|------------|--------|---------------|
| Mémoire intra gouvernée | `SessionMemoryContract`, `build_session_memory` | IMPLÉMENTÉ | `session_memory.py`, tests | ALIGNE | Lot 1 Vague 1 | Tests OK |
| memory-summary | `GET .../memory-summary/` | IMPLÉMENTÉ | `SessionMemorySummaryView` | ALIGNE_DOC_PARTIEL | D2-M04 | Schéma plat vs nested |
| Injection prompt LLM | Absente (`prompt_renderer`) | PARTIEL | grep code | PARTIEL | DOC décision | **ÉCART CONFIRMÉ** — hors lot 1 |
| Contrat API memory-summary v1 | `contrat_api_memory_summary_v1.md` | DOC | cluster 10 | **ALIGNE doc** | — | C9-DOC-01 livré |
| LearnerThemeMemory | modèle + consolidator | IMPLÉMENTÉ stockage | models | ALIGNE_DOC_PARTIEL | Hors injection tour | Inter-sessions préparé |
| Mémoire UI apprenant (panneau) | `LearnerMemoryPanel.vue` + `ExpandableText` | **PARTIEL+** | cluster 15/16, B16-M1/M2 | ALIGNE_DOC_PARTIEL | S16-A3 manuel | `session_memory` seul ; troncature « Voir plus » |
| Mémoire UIState contrat | Absente | CIBLE | `build_contract_ui_state` | ABSENT_NOUVEAU_CONTRAT | D2-M04 | Distinct panneau API |
| Verbatim ≠ mémoire | Doctrine | ALIGNE | ecarts-20 | ALIGNE | — | — |

---

## 3. Domaine 30 — référentiel documentaire / RAG

**Écart domaine :** `ecarts — 30_referentiel_documentaire_RAG.md` · **Couronne** plan CTO (renfort situé, pas noyau bloquant)

| Nom doctrinal 2.0 | Nom(s) réel(s) | Niveau | Sources | Statut doc | Action | Justification |
|-------------------|----------------|--------|---------|------------|--------|---------------|
| RAG lexical gouverné | `select_rag_chunks`, `should_use_rag` | IMPLÉMENTÉ | `rag_support.py`, tests | ALIGNE | Contrat minimal ecarts-30 | **RÉEL OBSERVÉ** |
| RAG vectoriel | pgvector champ inactif | CIBLE | library models | ABSENT_NOUVEAU_CONTRAT | Couronne | **ÉCART CONFIRMÉ** non actif runtime |
| RAG × posture | Gating par profile | IMPLÉMENTÉ | rag_support | ALIGNE_DOC_PARTIEL | D2-M02 | — |
| Citations produit | `rag_citations`, badge « Appui » | IMPLÉMENTÉ | views_sessions, front | ALIGNE | — | — |
| Référentiel vs library | apps séparées | IMPLÉMENTÉ | context_builder | PARTIEL | — | — |
| Hiérarchie contexte 2.0 | Ordre état→mémoire→RAG | PARTIEL | compléments 2.0 | ABSENT_NOUVEAU_CONTRAT | DOC B1/B2 | Non contractualisé bout en bout |
| RAG UIState prod | Absent | PARTIEL | ecarts-30 | PARTIEL | — | Engagement only |

---

## 4. Domaine 31 — front apprenant (postures et bascule)

**Écart domaine :** `ecarts — 31_front_apprenant_postures_et_bascule.md`  
**Frontière avec 10 :** ce domaine couvre **rendu front**, **bascule posture**, **grammaires UX** ; le backend `conversation_mode` / UIState relève de 10.

| Nom doctrinal 2.0 | Nom(s) réel(s) | Niveau | Sources | Statut doc | Action | Justification |
|-------------------|----------------|--------|---------|------------|--------|---------------|
| UIState consommé prod | `engagementUiModel.js`, `HugoProgressPanel` | IMPLÉMENTÉ | `03`, front 1.8 | ALIGNE | — | Backend-first |
| CTA synthèse / éval front | Branchés, pas recalcul local | IMPLÉMENTÉ | `09`, tests front | ALIGNE | — | **RÉEL OBSERVÉ** |
| Affichage `conversation_mode` | `PostureSelector.vue` (bandeau + select + verrou) | **PARTIEL+** | cluster 15/16 | ALIGNE_DOC_PARTIEL | S16-A2 manuel | `allowed_posture_transitions` ; message refus |
| 3 grammaires `learner_display_profile` | `displayProfilePresets.js` + CSS | **PARTIEL+** | D2-M08, C15/C16 U16-P | ALIGNE_DOC_PARTIEL | IFT-042 | **Même blocs** ; densité/style différenciés |
| Sélecteur posture / bascule | `PostureSelector.vue` | **PARTIEL+** | cluster 16 Playwright | ALIGNE_DOC_PARTIEL | Encoors A_VÉRIFIER | **ÉCART RÉDUIT** — livré local |
| `POST .../set-posture/` | `SessionSetPostureView` + sync progress | **IMPLÉMENTÉ** | cluster 15, fix C15 | ALIGNE | D2-M03 partiel | UI branchée ; POST vs PATCH spec ouvert |
| Matrice états bascule SW-xx | Spec maquettée | CIBLE | ecarts-31 | ABSENT_NOUVEAU_CONTRAT | Annexe spec interface | Non implémentée |

---

## 5. Domaine 40 — base de connaissances formateur

**Écart domaine :** `ecarts — 40_base_connaissances_formateur.md` · **Vague 3** plan CTO (encadrants)

| Nom doctrinal 2.0 | Nom(s) réel(s) | Niveau | Sources | Statut doc | Action | Justification |
|-------------------|----------------|--------|---------|------------|--------|---------------|
| TrainerKnowledgeItem | modèle + vues trainer | IMPLÉMENTÉ | models, views_trainer | ALIGNE | — | Alignement glossaire fort |
| Ingestion documentaire | library, upload | IMPLÉMENTÉ | `library`, ecarts-30 | ALIGNE_DOC_PARTIEL | — | — |
| Statuts gouvernés | declared / derived / validated | PARTIEL | specs, code | ALIGNE_DOC_PARTIEL | Matrice validation | Enforcement partiel |
| Validation humaine | validate/reject/provisional/edit API+UI | **PARTIEL+** | cluster 15 | ALIGNE_DOC_PARTIEL | usage_count RAG | Workflow C1 V0 livré local |
| Lien item → RAG apprenant | Consommation runtime | PARTIEL | pipeline | A_VÉRIFIER | Audit V3 domaine 30 | Non prouvé par tests C15 |
| Workflow dialogique complet | Atelier élicitation V0 + API F1 partiel | **PARTIEL** | cluster 15 | ALIGNE_DOC_PARTIEL | Script F1–F4 | Objets réels ; flux incomplet |

---

## 6. Domaine 50 — orchestrateur formateur

**Écart domaine :** `ecarts — 50_orchestrateur_formateur.md` · **Vague 3** plan CTO

| Nom doctrinal 2.0 | Nom(s) réel(s) | Niveau | Sources | Statut doc | Action | Justification |
|-------------------|----------------|--------|---------|------------|--------|---------------|
| Base formateur nominale | `TrainerKnowledgeItem`, trainer views | IMPLÉMENTÉ | ecarts-50 | ALIGNE | — | Non théorique |
| Ingestion + explicitation | DocumentIngestor, vues | PARTIEL | code | ALIGNE_DOC_PARTIEL | — | — |
| Questionnaire dialogique | Élicitation API + atelier V0 | **PARTIEL** | cluster 15 | ALIGNE_DOC_PARTIEL | F2–F4 | **ÉCART RÉDUIT** — F1 partiel |
| Surfaces prod formateur | `/app/trainer/knowledge` + `/elicitation` | **PARTIEL+** | cluster 15 | ALIGNE local | Encoors A_VÉRIFIER | Tableau + actions C1 |

---

## 7. Domaine 60 — orchestrateur tuteur

**Écart domaine :** `ecarts — 60_orchestrateur_tuteur.md` · **Vague 3** plan CTO (persona B1)

| Nom doctrinal 2.0 | Nom(s) réel(s) | Niveau | Sources | Statut doc | Action | Justification |
|-------------------|----------------|--------|---------|------------|--------|---------------|
| Progression + UIState (lecture) | `build_conversation_progress`, ui-state | IMPLÉMENTÉ | glossaire, code | ALIGNE | — | Briques backend |
| Timeline tuteur B1-01 | `DashboardTimelineView` | IMPLÉMENTÉ | patch C3, tests | ALIGNE | D2-M09 | Verbatim masqué si non partagé |
| Synthèse / éval partageables | `request-synthesis`, evaluation workflow | PARTIEL | endpoints | ALIGNE_DOC_PARTIEL | — | Surfaces tuteur partielles |
| Signaux qualité | `QualityTracker`, `ConversationQualitySignal` | IMPLÉMENTÉ | domaine 80 | ALIGNE_DOC_PARTIEL | Catalogue ouvert | — |
| Vues cohorte | `cohort_dashboard`, analytics | PARTIEL | code | A_VÉRIFIER | Prod | — |
| Validation terminale tuteur (générique) | Extension ultérieure | CIBLE | complément 2.0 | ABSENT_NOUVEAU_CONTRAT | DOC | Ne pas sur-affirmer |
| Service unique TutorOrchestrator | N/A — assemblage briques | PARTIEL | ecarts-60 | RENOMMER_DANS_DOC | — | Pas de service homonyme |

---

## 8. Domaine 70 — évaluation / traces / preuves

**Écart domaine :** `ecarts — 70_evaluation_traces_preuves.md` · **Mapping :** `mapping_EvaluationTrace_runtime_local.md` (D2-M05)

| Nom doctrinal 2.0 | Nom(s) réel(s) | Niveau | Sources | Statut doc | Action | Justification |
|-------------------|----------------|--------|---------|------------|--------|---------------|
| Branche terminale évaluation | `request-evaluation`, `finalize-evaluation` | IMPLÉMENTÉ | views_sessions, tests | ALIGNE | — | ≠ posture diagnostic |
| CTA évaluation / synthèse | `cta_*` UIState ; **`ui.advisory`** | IMPLÉMENTÉ | `cta_ui_state.py`, B16-C2 | ALIGNE | — | Rendu advisory front C16 |
| EvaluationTrace (doctrinal) | Agrégat conceptuel + **pivot `evaluation_trace_pivot_v1`** | PARTIEL | mapping D2-M05, pivot v3 | ALIGNE_DOC_PARTIEL | **Pivot livré local** | Dispersion record/trace ; pivot testé |
| LearnerEvaluationRecord | OneToOne session | IMPLÉMENTÉ | models | ALIGNE_DOC_PARTIEL | Pont glossaire | — |
| Trace + Evidence | `Trace`, `Evidence`, generate-trace | IMPLÉMENTÉ | models, views | PARTIEL | — | Pivot enrichit lien export |
| Payload `trace_rich_v1` | pivot + export E2E | PARTIEL | v5 EVAL1 | ALIGNE_DOC_PARTIEL | — | criteria legacy vides |
| Validation humaine | Trainer/tutor views + E2E T1 | PARTIEL | v5 | ALIGNE_DOC_PARTIEL | — | Circuits parallèles |
| Certification autonome | Absente | ALIGNE | doctrine | ALIGNE | — | Interdit produit |

---

## 9. Domaine 80 — observabilité / qualité conversationnelle

**Écart domaine :** `ecarts — 80_observabilite_qualite_conversationnelle.md` · **Couronne** plan CTO

| Nom doctrinal 2.0 | Nom(s) réel(s) | Niveau | Sources | Statut doc | Action | Justification |
|-------------------|----------------|--------|---------|------------|--------|---------------|
| ConversationQualitySignal | modèle + `quality_tracker` | IMPLÉMENTÉ | models, tests | ALIGNE_DOC_PARTIEL | Catalogue ABSENT | **RÉEL OBSERVÉ** |
| analytics_state | JSON session + compteurs CTA bloqués | IMPLÉMENTÉ | orchestrateur, v3 | ALIGNE_DOC_PARTIEL | — | **+ v3** |
| Session observability admin | `/internal/.../observability/` | IMPLÉMENTÉ | views_internal v3 | ALIGNE_DOC_PARTIEL | — | ORGADMIN+ |
| Conversation summary v1 | `/internal/hugo/analytics/conversation-summary/` | IMPLÉMENTÉ | v4 | ALIGNE_DOC_PARTIEL | — | SUPERADMIN only |
| Vues cohorte | `cohort_dashboard` | PARTIEL | analytics | A_VÉRIFIER | — | — |
| Qualité visible apprenant | Absente (doctrine) | ALIGNE | ecarts-80 | ALIGNE | — | — |
| LLM analysis qualité (D9bis) | Modèles + export SUPERADMIN | PARTIEL | ecarts-80, 100, v4 | ALIGNE_DOC_PARTIEL | **Backend livré local** | Hors exports métier |
| Catalogue signaux canonique | n/a | CIBLE | spec | ABSENT_NOUVEAU_CONTRAT | OBSQ backlog | — |
| Dashboards observabilité produit | n/a | CIBLE | Couronne | ABSENT_NOUVEAU_CONTRAT | — | — |

---

## 10. Domaine 90 — confidentialité / multi-tenant / rôles

**Écart domaine :** `ecarts — 90_confidentialite_partage_multitenant_roles.md`

| Nom doctrinal 2.0 | Nom(s) réel(s) | Niveau | Sources | Statut doc | Action | Justification |
|-------------------|----------------|--------|---------|------------|--------|---------------|
| Multi-tenant | `organisation_id` | IMPLÉMENTÉ | models | ALIGNE | — | — |
| Partage explicite | share flags, ShareView | IMPLÉMENTÉ | models | ALIGNE | — | — |
| Tuteur sans verbatim non partagé | B1-01 timeline | IMPLÉMENTÉ | `test_cluster3_oracles.py` | ALIGNE | D2-M07 partiel | **RÉEL OBSERVÉ** local |
| RLS Postgres | migrations | CREDIBLE | migrations | A_VÉRIFIER | ecarts-90 | SQLite local |
| Matrice rôle × visibilité | §6.2 cluster 2 amorcée | PARTIEL | design D2-M07 | ALIGNE_DOC_PARTIEL | D2-M07 | Pack pytest 10 tests |
| COORDO | Absent | CIBLE | personae E1 | ABSENT_NOUVEAU_CONTRAT | — | — |
| Frontière ORGADMIN / superadmin | §6.3 | PARTIEL | specs interface | ABSENT_NOUVEAU_CONTRAT | D2-M12 Vague 3 | export-md CIBLE |

---

## 11. Domaine 100 — exports / preuves / Qualiopi lite

**Écart domaine :** `ecarts — 100_exports_preuves_qualiopi_lite.md`

| Nom doctrinal 2.0 | Nom(s) réel(s) | Niveau | Sources | Statut doc | Action | Justification |
|-------------------|----------------|--------|---------|------------|--------|---------------|
| EvidenceBundle Qualiopi lite | `EvidenceBundleView` | IMPLÉMENTÉ | tests E2E v5 | **ALIGNE local** | A_VÉRIFIER Encoors | Métadonnées traces |
| ExportRun CSV/JSON | `apps/exports`, `trace_rich_v1` + pivot | IMPLÉMENTÉ | tests E2E v5 | **ALIGNE local** | A_VÉRIFIER Encoors | Distinct bundle |
| Trainer eval export | `trainer/evaluation-records/export/` | IMPLÉMENTÉ | views_trainer | ALIGNE | — | — |
| Permissions rôle exports org | `is_admin_like` backend + front `isOrgAdminLike` | ALIGNE | design C7, cluster dev v2 | **RÉEL OBSERVÉ** local | D2-M11 partiel |
| ConversationTurnLLMAnalysis | Modèles + export SUPERADMIN | PARTIEL | D9bis v4 | ALIGNE_DOC_PARTIEL | D2-M06 partiel | Canal technique séparé |
| Export debug md | Route absente | CIBLE | specs | ABSENT_NOUVEAU_CONTRAT | G3-03 oracle | D9bis export JSON livré |
| Trace riche pour exports | generate-trace + pivot v1 | PARTIEL | ecarts-70/100, v3 | ALIGNE_DOC_PARTIEL | — | Pivot testé ; criteria legacy vides |

---

## 12. Domaine 110 — interfaces formateur / tuteur

**Écart domaine :** `ecarts — 110_interfaces_formateur_tuteur.md`

| Nom doctrinal 2.0 | Nom(s) réel(s) | Niveau | Sources | Statut doc | Action | Justification |
|-------------------|----------------|--------|---------|------------|--------|---------------|
| Parcours apprenant prod | `ProdLearnerWorkspace`, `/app*` | IMPLÉMENTÉ | 03 | ALIGNE | — | — |
| Surface testeur | `LearnerDetailView`, tester mode | IMPLÉMENTÉ | 03, 05 | ALIGNE | Hors démo | — |
| Interface tuteur timeline | `DashboardTimelineView` + `/app/tutor` | PARTIEL | B1-01, v5 T1 | **ALIGNE local UI** | Encoors A_VÉRIFIER | Verbatim masqué si non partagé |
| Interface formateur | `/app/trainer/knowledge` + élicitation | **PARTIEL+** | cluster 15, v5 F1 | ALIGNE local | Encoors A_VÉRIFIER | validate/reject/provisional/usage |
| ConductProfiles / TutorPrompts | Admin UI + API | IMPLÉMENTÉ | front + back | ALIGNE | — | — |
| Profils affichage 3 UX | `learner_display_profile` + CSS | **PARTIEL+** | cluster4/C15/C16 | ALIGNE_DOC_PARTIEL | IFT-042 | E2E U16-P1/P2 PASS |
| conversation_mode + sélecteur | Backend + `PostureSelector` + bandeau scène | **PARTIEL+** | cluster 16 | ALIGNE_DOC_PARTIEL | Encoors A_VÉRIFIER | **ÉCART RÉDUIT** vs V4 |
| Mémoire visible apprenant | `LearnerMemoryPanel` | **PARTIEL+** | B16-M*, U16-S3 | ALIGNE_DOC_PARTIEL | — | Intra-conversation gouvernée |
| Choix profil par formateur | Absent surface dédiée | CIBLE | IFT-042 | ABSENT_NOUVEAU_CONTRAT | DSP-05 | PATCH groupe orgadmin partiel |

---

## 13. Domaine 120 — intercalaires v1

**Écart domaine :** `ecarts — 120_intercalaires_v1.md` · **Couronne** plan CTO (post-cœur)

| Nom doctrinal 2.0 | Nom(s) réel(s) | Niveau | Sources | Statut doc | Action | Justification |
|-------------------|----------------|--------|---------|------------|--------|---------------|
| Intercalaire pédagogique V1 | Capacité additive cible | CIBLE | spec 2.0, ecarts-120 | ABSENT_NOUVEAU_CONTRAT | INT backlog | **Aucun réel observé** |
| SessionInterstitial (concept) | Aucun modèle homonyme | CIBLE | glossaire | A_VÉRIFIER | — | Objet conceptuel |
| Producteur post-tour | Service dédié | CIBLE | spec | ABSENT_NOUVEAU_CONTRAT | Contrat cible | Non branché |
| Composant apprenant passif | Non interactif | CIBLE | ecarts-120 | ABSENT_NOUVEAU_CONTRAT | — | — |
| Typologie NONE/NOTION/CONTRAST | Enum cible | CIBLE | docs projet | ABSENT_NOUVEAU_CONTRAT | — | — |
| Effet nul sur P0 | Garde-fou | ALIGNE | doctrine | ALIGNE | — | Compatible architecture |
| Flags / variante distante | Possible | A_VÉRIFIER | — | A_VÉRIFIER | INT-022 | — |

---

## 14. Backlog documentaire cluster 2 (V3) — D2-Mxx × plan CTO

| ID | Domaine | Action | Priorité | Statut | **Lot plan CTO** |
|----|---------|--------|----------|--------|------------------|
| D2-M01 | 10/110 | Contrat `conversation_mode` dans UIState | — | **Livré C4** | Vague 2 |
| D2-M02 | 10 | Tableau posture → RAG → maturité → CTA | Haute | Ouvert | **Vague 3** |
| D2-M03 | 10/31 | Route set-posture POST + UI + sync progress | — | **Partiel livré C15** | Vague 2–3 |
| D2-M04 | 20 | memory-summary schéma plat vs nested cible | Moyenne | Ouvert | **Vague 1–2** |
| D2-M05 | 70/100/110 | Mapping EvaluationTrace | — | **Livré doc** | Vague 2 |
| D2-M06 | 80/100 | D9bis export analytique LLM | Moyenne | **CIBLE** | **Couronne optionnelle** |
| D2-M07 | 90 | Matrice rôle × visibilité × partage | Haute | **Partiel** (pack pytest) | Vague 2 |
| D2-M08 | 110/31 | Profils affichage + `learner_display_profile` | — | **Partiel+ C16** | Vague 2 |
| D2-M09 | 60/110 | Checklist parcours tuteur B1 | Moyenne | Ouvert | **Vague 3** |
| D2-M10 | 10 | Flag v17 dans 08_FLAGS | Haute | Ouvert | **Vague 3** |
| D2-M11 | 100 | Taxonomie export E1–E6 | — | **Partiel C7** | Vague 2 |
| D2-M12 | 90/100 | Frontière ORGADMIN/superadmin | Haute | Ouvert | **Vague 3** |

---

## 15. Zones A_VÉRIFIER transverses

- `hugoback.encoors.com` : UIState, CTA, memory-summary, exports, interfaces encadrants (`10_FICHE_RUNTIME_PROD_ENCOORS`).
- RLS PostgreSQL prod (domaine 90).
- `HUGO_P0_V17_ENABLED` local et prod (domaine 10).
- Richesse `generate-trace` et EvidenceBundle sur données réelles (70/100).
- Sélecteur posture et bascule front prod (31) — **PARTIEL+ livré local** ; verrou phase/tours **PARTIEL** ; Encoors A_VÉRIFIER.
- Workflows formateur/tuteur bout-en-bout prod (40/50/60/110).
- Intercalaires v1 derrière flags ou variante distante (120).

---

## 16. Fichiers cluster 2 liés

| Fichier | Rôle |
|---------|------|
| `synthese_globale_ecarts_par_domaine.md` | Vue globale 13 domaines |
| `plan_documentation_cto_convergence_hugo.md` | Trajectoire Vagues 1–3 + couronne |
| `cluster2_prompts_audit_runtime_et_memoire.md` | Boîte à outils audits Cursor |
| `cluster2_oracles_test_par_persona.md` | Oracles par persona |
| `Cluster 2 — Oracles de test par persona + validation courte.md` | Synthèse clusters 2–4 |
| `ecarts — *.md` | Rapports d’écarts par domaine (13 fichiers) |
| `Bibliothèque canonique de personae Hugo 2.0.md` | Scénarios B1/C1/D1 |

**Confiance globale V3 :** **IMPLÉMENTÉ** sur noyau backend local, parcours `/app`, CTA, confidentialité B1-01, exports tenant-scoped, guards trainer/exports, EXIF Evidence ; **PARTIEL** sur encadrants prod (surfaces minimales livrées), 3 grammaires front, frontière ORGADMIN/SUPERADMIN ; **CIBLE/A_VÉRIFIER** sur prod Encoors, v17, RLS, intercalaires, D9bis.

---

## 17. Manques résiduels du cluster 2 (V3)

1. **Domaines nouvellement explicités** : 31, 40, 50, 60, 120 intégrés — parcours encadrants et intercalaires restent ouverts.
2. **Contrats non encore écrits** : matrice bascule front (31), DocumentContextBundle (30), catalogue signaux (80), contrat intercalaire (120), D9bis (80/100).
3. **Preuves prod** : parité Encoors non tranchée (transversal).
4. **Double stack** : UIState engagement vs contrat (10).
5. **Parcours encadrants** : B1-01 local vert ; formateur C15 **PARTIEL+ livré local** (validation + élicitation) ; tuteur prod **A_VÉRIFIER** Encoors.
6. **Injection mémoire prompt** : décision doc à figer (20) — hors lot 1 intentionnel.
7. **Permissions exports org** : ~~scoping rôle à durcir~~ **RÉDUIT cluster dev vague 2** — front aligné `isOrgAdminLike` ; backend inchangé ; D2-M12 ouvert.

---

## 18. Statut post-clusters 3–7 (2026-06-18)

| Élément | Statut | Domaines |
|---------|--------|----------|
| Cluster 3 oracles (8/8) | **Fait** | 90, 110 (B1-01) |
| Cluster 4 surface UIState | **Fait backend** | 10, 31, 110 |
| Cluster 5 grammaires front | **Partiel** | 31, 110 |
| Cluster 6 confidentialité D2-M07 | **Partiel** (10 tests) | 90, 100 |
| Cluster 7 exports D2-M06/M11 | **Partiel** (13 tests ; D9bis verrouillé absent) | 100, 80 |
| Vagues 2–4 dev + tests | **Livré local** | 90/100/70/80/110 |
| Vague 5 audit E2E/Encoors | **Livré** | transversal |
| Cluster 8 OPS (Playwright + RLS + oracle) | **Livré local** | 90/100/70/110 + OPS |
| Cluster 9 contrats transverses (20/70/80/90/100) | **Livré doc** | 20/70/80/90/100 |
| Cluster 10 clôture runtime/OPS | **Livré** | OPS + DOC C9 |
| **Cluster 15 interfaces apprenant/formateur** | **Livré local** | 10, 20, 31, 40, 50, 110 |
| **Campagne pytest post-C15 (90 tests)** | **PASS local 2026-06-18** | transversal |
| **Cluster 16 interface apprenant spec 2.0** | **Livré local** | 10, 20, 31, 70, 110 |
| **Campagne tests C16 (15 backend + 10 Playwright)** | **PASS local 2026-06-18** | 10, 20, 31, 110 |

**Vague runtime/OPS :** **Clôturée** (clusters 8–10) — `cluster10_cloture_vague_runtime_ops_resultats.md`.  
**Vague interfaces C15 :** **Livré local** — `cluster15_interfaces_apprenant_formateur_resultats.md`, `rapport_mise_a_jour_doc_post_tests_2026-06-18.md`.  
**Vague interface apprenant C16 :** **Livré local** — `cluster16_interface_apprenant_spec_conformite_resultats.md`, `cluster16_interface_apprenant_resultats_tests.md`.

**Hors périmètre immédiat (couronne) :** RAG vectoriel, D9bis exposé produit / dashboards analytics, intercalaires v1, parité Encoors authentifiée, mémoire inter-sessions injection tour, certification autonome, scénarios manuels S16-A1→A5, IFT-042 choix profil cohorte.

---

## 19. Statut post-profils globaux apprenant (2026-06-20)

| Élément | Statut | Domaines | Preuve |
|---------|--------|----------|--------|
| Modèle `LearnerConversationGlobalProfile` | **Livré local** | 10, 31, 70, 110 | `models.py`, migration 0020 |
| API CRUD + legacy template | **Livré local** | 110 | `test_learner_conversation_global_profile.py` (12 PASS) |
| Admin `/admin/conversation/learner/profiles` | **Livré local** | 110 | Playwright `admin_learner_profiles.spec.ts` |
| Affectation groupe | **Livré local** | 110, 90 | `GroupAdminDetailView` ; Playwright `admin_conversation_pipeline.spec.ts` |
| Résolution runtime (session → groupe → org) | **Livré local** | 10 | `learner_profile_resolver.py`, tests résolution |
| Fallback legacy TutorPrompt | **Conservé actif** | 10 | `test_resolve_tutor_prompt_legacy_fallback_when_no_global_profile` |
| Apprenant choisit mode, pas profil global | **Conforme produit** | 31 | `PostureSelector.vue` ; doc `MINI_SPEC_*` |
| Prompts synthèse admin | **Absent** | 10, 70 | `synthesis_service.py` hardcodé — **CIBLE Phase 3** |
| Orchestrateur params éditables | **Absent** | 10 | Panneau read-only — **PARTIEL** |
| Starter prompts admin | **Absent** | 110 | API seule — tester only |
| `session.learner_conversation_profile` REST | **Absent** | 90, 110 | Modèle + résolveur ; pas d’API PATCH session |
| Policies évaluation groupe UI | **Partiel** | 70 | Backend `EvaluationPolicy(group=…)` ; UI org-level surtout |

**Pipe nominal documenté :** admin compose profil global → affecte au groupe → runtime résout slots par posture → apprenant bascule diag/réflexif/bûchage → évaluation finale via slot eval / policy org.

**Référence :** `MINI_SPEC_PROFILS_CONVERSATIONNELS_APPRENANT.md`, archive `tests/archives/tests_hugo_2_0_2026-06-18_20.md` §2 bis.
