# Rapport — Mise à jour documentaire post-tests (2026-06-18)

**Workspace :** `/Users/machin/Desktop/Zone de travail Hugo`  
**ENVIRONMENT :** `local`  
**BRANCH :** working tree cluster 15 (pas de dépôt git racine unifié ; `hugo_back` local)  
**DATE_RUN :** `2026-06-18`  
**AUTEUR_DOC :** `conv-hugo-post-tests`

---

## 1. Sources de preuve mobilisées

| Campagne | Fichiers tests | Résultat local |
|----------|----------------|----------------|
| Cluster 3 court | `test_cluster3_oracles.py` (5 tests) | PASS |
| Cluster 4 surface UIState | `test_cluster4_surface_contracts.py` (11 tests) | PASS |
| Cluster 15 apprenant | `test_cluster15_interfaces_apprenant.py` (13 tests) | PASS |
| Cluster 15 formateur | `test_cluster15_interfaces_formateur.py` (8 tests) | PASS |
| Mémoire | `test_session_memory_contract.py`, `test_memory_summary_smoke.py` | PASS |
| Posture | `test_posture_modes.py` (6 tests) | PASS |
| CTA | `test_cta_*_contract.py`, `test_request_evaluation_guard.py` | PASS |
| Trainer | `test_trainer_knowledge.py` (3 tests) | PASS |
| Confidentialité D2-M07 | `test_d2_m07_confidentiality_oracles.py` | PASS |
| Exports D2-M06/M11 | `test_d2_m06_d2_m11_exports_and_analytics.py` | PASS |
| RAG lexical | `test_rag_support_tracing.py` | PASS |

**Run consolidé exécuté le 2026-06-18 :** **90 passed**, 0 failed (~70 s) — voir commande §6.

**Non exécutés dans ce run :** Playwright E2E, RLS Postgres prod, oracle Encoors authentifié, tests v17 flag ON, intercalaires (aucun test applicable).

---

## 2. Tableau de synthèse transversal (domaines 10–120)

| Domaine | Capacités confirmées par tests auto | Couverture manuelle / protocole | Encore CIBLE / non testé |
|---------|--------------------------------------|---------------------------------|---------------------------|
| **10** | UIState sans P0 ; `conversation_mode` ; `learner_display_profile` ; CTA ; set-posture 200/400 ; sync `conversation_progress.posture` (fix C15) | Check-lists A1–A3 posture/profil | Double builder UIState ; v17 prod ; libellés CTA × posture |
| **20** | SessionMemoryContract ; memory-summary sans verbatim ; scope intra | LearnerMemoryPanel UI §4 protocole | Injection prompt LLM ; mémoire dans UIState ; inter-session injection tour |
| **30** | RAG lexical, gating, citations | Badge Appui (A1-09) manuel | pgvector ; hiérarchie contexte 2.0 contractualisée |
| **31** | UIState consommé ; CTA front ; profils CSS 3 grammaires | PostureSelector, profils A1/A2/A3 | Matrice SW-xx bascule ; PATCH vs POST spec |
| **40** | TrainerKnowledgeItem CRUD cycle ; validate/provisional/reject/edit | Tableau C1 §4 | Lien item→RAG runtime ; ingest upload front |
| **50** | Élicitation API (questions/answers) | Atelier `/app/trainer/elicitation` | Script F1–F4 complet ; orchestrateur dialogique bout-en-bout |
| **60** | Timeline B1-01 (cluster 3) ; guards tuteur | `/app/tutor` smoke | Vues cohorte prod ; TutorOrchestrator homonyme |
| **70** | request-evaluation guard ; CTA éval/synthèse ; traces/evidence modèles | Playwright partiel | EvaluationTrace agrégat ; trace_rich complet |
| **80** | quality signals, observability base tests | — | Catalogue signaux canonique ; dashboards produit |
| **90** | IDOR ui-state ; verbatim masqué timeline ; trainer 403 learner | Protocole confidentialité | RLS prod ; COORDO ; matrice rôle complète |
| **100** | EvidenceBundle tenant-scoped ; exports permissions ; EXIF | D1-02 cluster 3 | Encoors bundle ; export-md debug |
| **110** | Parcours apprenant prod ; formateur list/validate/élicitation ; posture UI | Check-lists C1 | Choix profil C1 (IFT-042) ; tuteur prod Encoors |
| **120** | — (audit code : 0 implémentation) | — | Intégralité domaine CIBLE |

---

## 3. Synthèse par domaine (post-tests)

### 10 — Runtime / P0 / UIState
**Confirmé :** contrat UIState, CTA backend-driven, `conversation_mode`, set-posture API + sync progress (C15).  
**PARTIEL :** sélecteur posture UI (`PostureSelector.vue`).  
**CIBLE / A_VÉRIFIER :** v17 prod, variation libellés CTA par posture.

### 20 — Mémoire gouvernée
**Confirmé :** memory-summary intra sans verbatim (13+ tests).  
**PARTIEL :** panneau `LearnerMemoryPanel` (front, lecture seule, `session_memory` seul).  
**CIBLE :** injection tour LLM ; mémoire dans UIState.

### 30 — RAG lexical
**Confirmé :** `select_rag_chunks`, tracing tests.  
**CIBLE :** RAG vectoriel (31/domaine 30 couronne).

### 31 — Front postures & bascule
**Confirmé :** CTA + profils + PostureSelector branché.  
**PARTIEL :** matrice états bascule SW-xx ; polish UX adult/pro.  
**A_VÉRIFIER :** POST vs PATCH doctrinal.

### 40 — Base connaissances formateur
**Confirmé :** cycle statuts via API (C15).  
**PARTIEL :** surfaces prod tableau + atelier V0.  
**A_VÉRIFIER :** consommation RAG des items validés.

### 50 — Orchestrateur formateur
**Confirmé :** élicitation API.  
**PARTIEL :** atelier front V0.  
**CIBLE :** script F1–F4 complet.

### 60 — Orchestrateur tuteur
**Confirmé :** B1-01 API.  
**PARTIEL :** surfaces `/app/tutor`.  
**CIBLE :** validation terminale tuteur générique.

### 70 — Évaluation / traces / preuves
**Confirmé :** branche terminale, guards CTA, modèles Trace/Evidence.  
**PARTIEL :** EvaluationTrace pivot, payload trace.  
**CIBLE :** certification autonome (interdit — ALIGNE).

### 80 — Observabilité
**Confirmé :** signaux, analytics_state (tests observabilité).  
**CIBLE :** catalogue canonique, dashboards.

### 90 — Confidentialité
**Confirmé :** partage explicite, IDOR, verbatim masqué (cluster 3 + D2-M07).  
**A_VÉRIFIER :** RLS prod ; COORDO absent.

### 100 — Exports
**Confirmé :** bundle tenant, permissions, EXIF (cluster 3 D1-02 + D2-M06).  
**A_VÉRIFIER :** Encoors.

### 110 — Interfaces formateur/tuteur
**Confirmé :** apprenant prod ; formateur validation + élicitation + usage_stats ; posture UI.  
**PARTIEL :** tuteur prod ; IFT-042 choix profil cohorte.  
**CIBLE :** parcours encadrants bout-en-bout prod.

### 120 — Intercalaires
**Confirmé absent :** audit code + tests N/A.  
**CIBLE :** intégralité.

---

## 4. Promotions documentaires effectuées (V4 matrice)

| Objet | Avant | Après | Preuve |
|-------|-------|-------|--------|
| Sélecteur posture UI | CIBLE / ABSENT | **PARTIEL** | `PostureSelector.vue`, `test_cluster15_interfaces_apprenant.py` |
| set-posture + UIState cohérent | PARTIEL (progress stale) | **IMPLÉMENTÉ** | fix `views_sessions.py`, test_a2 posture |
| Panneau mémoire apprenant | CIBLE / absent prod | **PARTIEL** | `LearnerMemoryPanel.vue`, memory tests |
| Workflow trainer validate/reject/provisional | PARTIEL | **PARTIEL+** (API+UI) | `test_cluster15_interfaces_formateur.py` |
| Atelier élicitation C1 | CIBLE | **PARTIEL** | API + `ProdTrainerElicitationView.vue` |
| usage_stats trainer | absent | **PARTIEL** | `_usage_stats_for_item`, test_c1 list |
| D2-M03 set-posture | Ouvert | **Partiel livré** | POST + UI + sync progress |

---

## 5. Manques résiduels mis à jour

**Retirés / réduits :**
- Sélecteur posture « totalement absent » → PARTIEL livré (31/110).
- set-posture « UI absente » → UI branchée ; D2-M03 partiellement clos.

**Ajoutés :**
- Playwright C15 (posture, mémoire, trainer) — non exécuté auto.
- Compteur usage RAG réel par TrainerKnowledgeItem (`usage_count` null).
- Parité Encoors post-cluster 15.

---

## 6. Commande pytest de référence

```bash
cd hugo_back && python -m pytest \
  apps/hugo/tests/test_cluster3_oracles.py \
  apps/hugo/tests/test_cluster4_surface_contracts.py \
  apps/hugo/tests/test_cluster15_interfaces_apprenant.py \
  apps/hugo/tests/test_cluster15_interfaces_formateur.py \
  apps/hugo/tests/test_session_memory_contract.py \
  apps/hugo/tests/test_memory_summary_smoke.py \
  apps/hugo/tests/test_posture_modes.py \
  apps/hugo/tests/test_trainer_knowledge.py \
  apps/hugo/tests/test_request_evaluation_guard.py \
  apps/hugo/tests/test_d2_m07_confidentiality_oracles.py \
  apps/hugo/tests/test_d2_m06_d2_m11_exports_and_analytics.py \
  apps/hugo/tests/test_rag_support_tracing.py \
  apps/hugo/tests/test_cta_synthesis_contract.py \
  apps/hugo/tests/test_cta_evaluation_contract.py \
  -v
```

---

## 7. Prochains chantiers suggérés (vague 2.1)

1. **Domaines très CIBLE :** 120 intercalaires, RAG vectoriel (30/31 couronne), orchestrateurs 50/60 bout-en-bout UX.
2. **Qualification prod :** Encoors oracle posture + mémoire + trainer (A_VÉRIFIER).
3. **E2E :** Playwright C15 + smokes tuteur B1.
4. **Doc :** IFT-026/041/042 recalés dans ecarts-110 ; D2-M02 tableau posture→RAG→CTA.
5. **Backend :** traçage usage RAG ↔ TrainerKnowledgeItem (B3 complet).

---

## 8. Fichiers modifiés dans cette passe documentaire

| Fichier | Nature mise à jour |
|---------|-------------------|
| `cluster2_matrice_runtime_vs_cible.md` | V4 — statuts 10/20/31/110, §18 cluster 15, manques |
| `cluster2_oracles_test_par_persona.md` | Oracles validés localement C15 |
| `cluster3_validation_courte_personae.md` | Extension cluster 15 |
| `cluster15_interfaces_apprenant_formateur_resultats.md` | Campagne pytest 39+90 |
| `protocole_tests_interfaces_apprenant_formateur_v1.md` | Résultats auto |
| `ecarts — *.md` (13 domaines) | Bandeau post-tests 2026-06-18 |
| `spec_canonique_hugo_2_0.md` | Mentions statut impl partielle |
| `specs interface 2.0.md` | Mentions statut impl partielle |
