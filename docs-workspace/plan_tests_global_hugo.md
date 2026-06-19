# Plan de tests global Hugo 2.0 — cartographie & scénarios persona

> **Sources mobilisées :** clusters 8–16, `cluster2_matrice_runtime_vs_cible.md` **(V5)**, personae/oracles cluster 2–3, écarts domaines 10–120, protocoles `protocole_tests_*`, `cluster16_protocole_tests_interface_apprenant_v1.md`.  
> **Réel confirmé :** pytest ~45 fichiers `hugo_back/apps/hugo/tests/` (dont `test_cluster15_*`, `test_cluster16_*`) ; Playwright `frontend_1.8/tests_playwright/` (smokes + `e2e/cluster16_learner_interface.spec.ts` **10 PASS**) ; oracles `encoors_oracle.py`.  
> **Dernière mise à jour :** 2026-06-18 (post-cluster 16).

---

## 1. Synthèse par domaine

| Domaine | Thème | Pytest existant | Playwright | Oracle Encoors | SQL RLS | Gaps principaux |
|---------|-------|-----------------|------------|----------------|---------|-----------------|
| **10** | P0 / progression / UIState / CTA | `test_cluster3_oracles`, `test_cluster4`, `test_cluster15/16_apprenant`, `test_cta_*`, `test_posture_modes` | `e2e/learner_a1`, **`e2e/cluster16_learner_interface`** (U16-S) | — | — | Verrou posture phase/tours **PARTIEL** ; v17 prod **A_VÉRIFIER** |
| **20** | Mémoire gouvernée intra-conversation | `test_session_memory_contract`, `test_memory_summary_smoke`, **`test_cluster16`** B16-M | **`cluster16`** U16-S3 (panneau mémoire) | **M1** | — | Inter-sessions **hors périmètre** ; mémoire UIState **CIBLE** |
| **30** | RAG lexical / référentiel | `test_rag_support_tracing`, `test_preprod_garde_fou` | B1-06 **GAP** (badge Appui) | — | — | pgvector **OFF** |
| **31** | Front apprenant postures & profils | `test_posture_modes`, `test_cluster4`, **`test_cluster15/16`** | **`cluster16`** U16-S1/P (posture, profils) | — | — | Matrice SW-xx **CIBLE** ; Encoors **A_VÉRIFIER** |
| **40** | Base connaissances formateur | `test_trainer_knowledge`, `test_vague5` F1 | `test_smoke_trainer` | — | — | Ingest/elicitation prod UI **PARTIEL** |
| **50** | Orchestrateur formateur | `test_context_builder_criteria`, `test_hugo_calibration_scenarios` | — | — | — | Pas d’oracle persona dédié formateur orchestration |
| **60** | Orchestrateur tuteur | `test_tutor_access_control`, `test_tutorprompt`, `test_vague5` T1 | `test_smoke_tutor`, `e2e/tutor_b1` | — | — | Observabilité interne **sans UI** |
| **70** | Évaluation / traces / pivot v1 | `test_evaluation_trace_minimal`, `test_request_evaluation_guard`, `test_cluster3`, **`test_cluster16`** B16-C2 advisory | — (CTA visibles en U16-S2) | **EVAL1** | — | Playwright advisory dédié **U16-S2b ouvert** |
| **80** | Observabilité qualité conversationnelle | `test_observabilite_base`, `test_observabilite_avancee_v1`, `test_quality_signals`, `test_d9bis_*` | — | **OBS_BASE**, **D9BIS** | — | Zéro surface front observabilité interne |
| **90** | Confidentialité / multi-tenant / rôles | `test_rls_postgres_minimal`, `test_d2_m07_confidentiality_oracles`, `test_encadrants_role_guards`, `test_preprod_garde_fou` | guards e2e (learner/tutor) | auth probes | `audit_rls_prod_template.sql` | RLS prod **A_VÉRIFIER** ; COORDO UI dédiée **ABSENTE** |
| **100** | Exports / preuves Qualiopi lite | `test_d2_m06_d2_m11_*`, `test_analytics_absence_*`, `test_vague5` O1 | `test_smoke_orgadmin_exports` | **O1** | — | E1–E6 org **PARTIEL** (tester layout) ; Felix v3 **ABSENT** Encoors |
| **110** | Interfaces formateur / tuteur | `test_encadrants_role_guards`, `test_cluster4`, **`test_cluster15_*`** | smokes tutor/trainer/coordo + **cluster16** apprenant | — | — | Tuteur prod **A_VÉRIFIER** ; IFT-042 **CIBLE** |
| **120** | Intercalaires v1 | — | — | — | — | **GAP** — pas de suite dédiée ; N/A preprod immédiat |

---

## 2. Inventaire pytest par fichier (référence rapide)

| Fichier | Domaines couverts |
|---------|-------------------|
| `test_cluster3_oracles.py` | 10, 70, 90 |
| `test_cluster4_surface_contracts.py` | 10, 31, 110 |
| `test_session_memory_contract.py` | 20 |
| `test_memory_summary_smoke.py` | 20 |
| `test_preprod_garde_fou.py` | 20, 30, 90, 100 |
| `test_rag_support_tracing.py` | 30 |
| `test_posture_modes.py` | 10, 31 |
| `test_cta_synthesis_contract.py` / `test_cta_evaluation_contract.py` | 10, 70 |
| `test_evaluation_trace_minimal.py` | 70, 100 |
| `test_observabilite_base.py` / `test_d9bis_analytics_llm.py` | 80 |
| `test_d2_m07_confidentiality_oracles.py` | 90 |
| `test_rls_postgres_minimal.py` | 90 |
| `test_d2_m06_d2_m11_exports_and_analytics.py` | 100, 80 |
| `test_encadrants_role_guards.py` | 110, 90, 100 |
| `test_vague5_e2e_scenarios.py` | 60, 40, 100, 70 (API E2E) |
| `test_trainer_knowledge.py` | 40 |
| `test_cluster15_interfaces_apprenant.py` | 10, 20, 31, 70, 110 (apprenant) |
| `test_cluster15_interfaces_formateur.py` | 40, 50, 110 (formateur) |
| `test_cluster16_interface_apprenant_backend.py` | 10, 20, 31, 70 (B16-P/C/M/L/S) |
| `test_phase_progression.py` | 10 |

**Suite preprod consolidée :** `hugo_back/scripts/run_preprod_suite.sh`

---

## 3. Inventaire Playwright

| Spec | Persona | Scénarios |
|------|---------|-----------|
| `test_smoke_tutor.spec.ts` | B1 tuteur | Timeline prod |
| `test_smoke_trainer.spec.ts` | C planifié | Knowledge list |
| `test_smoke_orgadmin_exports.spec.ts` | D1 ORGADMIN | Exports visibles / learner bloqué |
| `e2e/learner_a1.spec.ts` | A1 apprenant | A1-01 P0 DOM ; A1-02 pas exports ; A1-03 groups-admin bloqué |
| `e2e/tutor_b1.spec.ts` | B1 tuteur | B1-T1 sans verbatim/P0 ; B1-T2 pas exports |
| `e2e/coordo_c14.spec.ts` | COORDO | C14-C1 espace tuteur |
| **`e2e/cluster16_learner_interface.spec.ts`** | **A1/A2/A3** | **U16-S1→S4** posture, CTA, mémoire, scène ; **U16-P1/P2** profils (10 tests PASS local) |

**Bootstrap :** `python manage.py bootstrap_smoke_playwright` → `smoke-fixtures.json` (+ `cluster16_sessions.youth|adult|professional`)

**Protocoles :** `protocole_tests_interfaces_apprenant_formateur_v1.md`, `cluster16_protocole_tests_interface_apprenant_v1.md`

---

## 4. Oracles Encoors & RLS

| Scénario | Script | Sans auth | Avec auth |
|----------|--------|-----------|-----------|
| M1 memory-summary | `encoors_oracle.py` | — | GET session memory |
| EVAL1 | idem | — | readiness / request-evaluation / generate-trace |
| O1 exports | idem | — | `/exports/run/`, evidence-bundle |
| OBS_BASE / D9BIS | idem | 404 probes | observability + d9bis export |
| RLS prod | `audit_rls_prod_template.sql` | — | exécution psql **A_VÉRIFIER** |

**Commande unique :** `bash hugo_back/scripts/run_encoors_preprod_oracle.sh`

---

## 5. Plan par persona

### A1 — Apprenant réflexif (LEARNER)

**Parcours cibles :** `/app` → `/app/session/:id` ; CTA synthèse/éval selon UIState ; badges Appui RAG.

| ID | Scénario | Attendus domaines | Statut |
|----|----------|-------------------|--------|
| A1-01 | Session sans P0 DOM | 10, 90 | **Playwright OK** |
| A1-02 | Pas d’exports org | 100, 90 | **Playwright OK** |
| A1-03 | Bloqué groups-admin | 90 | **Playwright OK** |
| A1-04 | CTA éligibilité ui-state | 10, 70 | **pytest OK** (cluster 3/15/16) |
| A1-05 | memory-summary / panneau mémoire | 20 | **pytest OK** ; **Playwright U16-S3 OK** |
| A1-07 | set-posture API | 10, 31 | **pytest OK** (cluster 15/16) |
| A1-08 | Posture UI + profils | 31, 110 | **Playwright U16-S1/P OK** |
| A1-06 | Badge Appui RAG | 30, 31 | **GAP** Playwright (B1-06) |

### B1 — Tuteur (TUTOR) / COORDO (héritage)

| ID | Scénario | Attendus | Statut |
|----|----------|----------|--------|
| B1-T1 | Espace tuteur sans verbatim/P0 | 60, 70, 90, 110 | **Playwright OK** |
| B1-T2 | Pas exports org | 100, 90 | **Playwright OK** |
| B1-T3 | Timeline API sans verbatim | 90 | pytest vague5 |
| B1-T4 | Validation trace | 70 | pytest vague5 |
| C14-C1 | COORDO → `/app/tutor` | 110, 90 | **Playwright OK** (bootstrap coordo) |

### C1 — Formateur (TRAINER)

| ID | Scénario | Attendus | Statut |
|----|----------|----------|--------|
| C1-01 | Knowledge list prod | 40, 110 | smoke trainer |
| C1-02 | Validate item | 40 | pytest F1 |
| C1-03 | 403 ExportRun org | 100, 90 | pytest + preprod |
| C1-04 | Pas accès verbatim apprenant | 90 | pytest guards |

### D1 — ORGADMIN

| ID | Scénario | Attendus | Statut |
|----|----------|----------|--------|
| D1-01 | Exports JSON/CSV visibles | 100 | smoke orgadmin |
| D1-02 | Learner sans exports | 90, 100 | smoke orgadmin |
| D1-03 | Export pivot v1 JSON | 70, 100 | pytest O1 |
| D1-04 | Evidence bundle | 100 | pytest |
| D1-05 | Observabilité interne API | 80 | pytest ; Encoors **A_VÉRIFIER** |

### D2 — SUPERADMIN (optionnel)

| ID | Scénario | Statut |
|----|----------|--------|
| D2-01 | ExportRun cross-org guard | pytest vague5 |
| D2-02 | UI superadmin exports | **GAP** Playwright |

---

## 6. Scénarios apprenant — statut post-clusters 15–16

| ID | Description | Statut | Preuve |
|----|-------------|--------|--------|
| B1-01 / U16-S1 | Posture visible | **OK local** | `PostureSelector.vue`, Playwright |
| B1-02 | Changement posture autorisé | **OK API** ; UI Playwright partiel | B16-P2, cluster 15 |
| B1-03 | Refus posture | **OK API** ; message UI **PARTIEL** | B16-P3 ; manuel S16-A2 |
| B1-04 / U16-P | Profils youth/adult/pro | **OK local** | bootstrap `cluster16_sessions`, U16-P |
| B1-05 / U16-S2 | CTA conformes UIState | **PARTIEL** | U16-S2 permissif ; U16-S2b **ouvert** |
| U16-S3 | Mémoire sans verbatim (panneau) | **OK** | Playwright |
| U16-S4 | Scène / progression / maturité | **OK** | `LearnerSceneContextBar`, Playwright |
| B1-06 | RAG badge Appui | **GAP** | — |

**Référence protocole :** `cluster16_protocole_tests_interface_apprenant_v1.md`

---

## 7. Garde-fou — invariants testés

| Invariant | Test |
|-----------|------|
| Pas de P0/TurnState en UIState | `test_cluster3_oracles` INV-01 |
| memory-summary sans verbatim | `test_memory_summary_smoke`, `test_preprod_garde_fou` |
| RAG lexical only | `test_preprod_garde_fou`, `test_rag_support_tracing` |
| EVAL1 non certifiant / pivot v1 | `test_evaluation_trace_minimal` |
| TRAINER 403 exports org | `test_preprod_garde_fou`, `test_encadrants_role_guards` |
| RLS policies actives | `test_rls_postgres_minimal` (skip si pas Postgres) |
| Pas analytics LL/widgets en export | `test_analytics_absence_ui_exports` |

---

## 8. Prochaine sortie utile

1. Scénarios manuels S16-A1→A5 et check-lists C15 §4 (QA persona).
2. Playwright U16-S2b (CTA advisory explicite) + B1-06 badge Appui RAG.
3. Exécuter oracles Encoors avec credentials → comparer JSON local vs `encoors_oracle_preprod.generated.json`.
4. Exécuter `audit_rls_prod_template.sql` sur prod **A_VÉRIFIER**.
5. Domaine 120 : contrat minimal intercalaires avant tests.
