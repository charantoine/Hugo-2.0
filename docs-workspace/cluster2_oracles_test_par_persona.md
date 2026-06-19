# Cluster 2 — Oracles de test par persona

**Workspace :** `/Users/machin/Desktop/Zone de travail Hugo`  
**Version :** 3 (alignement 13 domaines — 2026-06-18)  
**Sources :** `Bibliothèque canonique de personae Hugo 2.0.md`, `cluster2_matrice_runtime_vs_cible.md` (V3), `cluster2_prompts_audit_runtime_et_memoire.md`, `plan_documentation_cto_convergence_hugo.md`, `synthese_globale_ecarts_par_domaine.md`

> **Rattachement plan CTO :** oracles A1/B1/D1/G3 couvrent surtout 10/20/31/70/90/100/110 ; extensions C1 et parcours encadrants étendus visent 40/50/60/120 (Vague 3). Prioriser les vagues 1–3 avant la couronne (D9bis, intercalaires v1).

### Légende

| Résultat | Signification |
|----------|---------------|
| **SUCCÈS** | Critère observable conforme (réel local ou cible explicitement livrée) |
| **ÉCHEC** | Violation confirmée |
| **A_VERIFIER** | Encoors, flag, ou capacité `[CIBLE]` non testable comme livrée |
| **N/A** | Oracle `[CIBLE]` alors que capacité absente — noter écart doc, ne pas compter en succès |

**Type de test suggéré :** `UI` | `API` | `export` | `permission` | `doc` | `pytest`

---

## 0. Invariants transverses (tous apprenants)

| ID | Oracle | Contrat | Type | SUCCÈS si | ÉCHEC si |
|----|--------|---------|------|-----------|----------|
| INV-01 | Pas de P0 dans UIState prod | UIState | API+UI | `GET /ui-state/` sans clés p0/turn_state/reason_codes | Champs techniques exposés |
| INV-02 | Verbatim tiers invisible | Confidentialité | permission | Session non partagée → tuteur sans contenu | Verbatim lisible |
| INV-03 | CTA backend-driven | cta_* | API+UI | disabled cohérent avec blocking_reasons | Bouton actif sans éligibilité |
| INV-04 | Pas de discours « mémoire profil » | Copy produit | UI | Pas de « ce que Hugo sait de vous » | Wording mémoire persistante |
| INV-05 | Évaluation ≠ posture | Posture | doc+API | 3 postures enum ; éval = CTA | Mode « évaluation » dans posture |
| INV-06 | memory-summary structuré | memory-summary | API | `memory_scope: intra_conversation` ; 2 blocs distincts | Verbatim dans contract |
| INV-07 | conversation_mode UIState | UIState | API+UI | Champ présent, label cohérent posture | Absent ou P0 exposé | **SUCCÈS local C4** · `test_cluster4_surface_contracts.py` |
| INV-08 | Profil affichage ≠ gamification | UIState | doc+API | `learner_display_profile` distinct de `gamification_profile` | Confusion libellés | **SUCCÈS local C4** · idem |

---

## 1. Profils d'affichage — oracles transverses `[CIBLE]`

| ID | Persona type | Oracle | Contrat | Type | Note |
|----|--------------|--------|---------|------|------|
| DSP-01 | Jeune 16–20 (A1) | UI graphique, texte réduit | learner_display_profile=youth | API | **SUCCÈS contrat** ; rendu UI `[CIBLE]` | `test_cluster4_surface_contracts.py` |
| DSP-02 | Adulte reconversion (A2) | Équilibre texte/visuel | learner_display_profile=adult | API | **SUCCÈS contrat** ; rendu UI `[CIBLE]` | idem |
| DSP-03 | Ingénieur / sup. (A3) | Texte explicite, repères conceptuels | learner_display_profile=professional | API | **SUCCÈS** (défaut) | idem |
| DSP-04 | Tous | Même UIState, rendu différent | UIState canonique | API | **SUCCÈS** — un seul contrat JSON | idem |
| DSP-05 | Formateur C1 | Choix profil cohorte | API org/groupe | permission | `[CIBLE]` endpoint absent → A_VERIFIER |
| DSP-06 | ORGADMIN D1 | Choix profil organisation | API | permission | `[CIBLE]` |
| DSP-07 | Tous | CTA éligibilité identique | cta_* | API | Seul rendu graphique varie `[CIBLE]` |

---

## 2. PERSONA A1 — Karim, apprenti alternance (LEARNER)

**Rôles :** LEARNER · **Profil affichage cible :** youth `[CIBLE]` · **Postures :** diagnostic → reflective → knowledge_review → éval terminale

| ID | Oracle | Contrat | Type | SUCCÈS | ÉCHEC |
|----|--------|---------|------|--------|-------|
| A1-01 | Scène lisible | UIState scene_label, rail | UI | Labels Raconter/Explorer… | Écran vide dégradé permanent |
| A1-02 | Maturité discrète profil B | maturity_color, gamification B | UI | Badge maturité si profil B l'active | Jargon P0 |
| A1-03 | CTA synthèse ORANGE+ | cta_synthesis | API | eligible → bouton actif | eligible mais disabled |
| A1-04 | CTA éval GREEN | cta_evaluation | API | evaluation_eligible + helper si prudent | 200 request sans éligibilité |
| A1-05 | memory-summary sans verbatim | memory-summary | API | facts/open_points gouvernés (**validé C15**) | Verbatim dans session_memory |
| A1-06 | Partage synthèse seule | share_* | permission | Tuteur voit synthèse si share_summary | Verbatim visible sans share_verbatim |
| A1-07 | Posture API | set-posture | API | POST diagnostic → session.posture | 500 ou valeur invalide |
| A1-08 | Posture UI | conversation_mode | UI | Label + sélecteur + message verrou | — | **Validé C16** — Playwright U16-S1 ; transitions backend B16-P |
| A1-09 | RAG badge Appui | rag_citations | UI | « Appui : {titre} » si sélection | Wording « mémoire » |
| A1-10 | Diagnostic ≤2 questions | DecisionContract | pytest/doc | move clarify ; max_questions posture | 3+ questions tour 1 `[CREDIBLE]` |

**Scénarios API (référence prompts §B, §F) :**
- S1 diagnostic : message flou → maturité RED, synthesis locked
- S4 éval : GREEN + faible charge → request-evaluation 200 ou blocking explicite

---

## 3. PERSONA A2 — Nadège, reconversion (LEARNER)

**Rôles :** LEARNER · **Profil affichage cible :** adult `[CIBLE]`

| ID | Oracle | Contrat | Type | SUCCÈS | ÉCHEC |
|----|--------|---------|------|--------|-------|
| A2-01 | Quête active visible | active_quest_label | UI | Texte objectif si profil B/C | — |
| A2-02 | Règle transfert reflective | ConversationProgress | API | missing transfert si reflective RED | GREEN reflective sans transfert |
| A2-03 | Synthèse avant éval | cta_synthesis + cta_evaluation | API | synthesis eligible avant eval full | Eval « Demander » sans synthèse possible |
| A2-04 | memory objective | SessionMemoryContract | API | learning_objective renseigné après tours | Toujours vide |
| A2-05 | Densité UI intermédiaire | learner_display_profile=adult | UI | Mêmes blocs que youth/pro | — | **PARTIEL C16** — U16-P1/P2 E2E |

---

## 4. PERSONA A3 — Ibrahima, technicien senior (LEARNER)

**Rôles :** LEARNER · **Profil affichage cible :** professional `[CIBLE]`

| ID | Oracle | Contrat | Type | SUCCÈS | ÉCHEC |
|----|--------|---------|------|--------|-------|
| A3-01 | knowledge_review 1 branche | ConversationProgress | API | max 1 branche active | 3 branches actives |
| A3-02 | RAG docs métier | rag_citations | API | Citations si docs + termes | Jamais avec docs évidents |
| A3-03 | Pas project en révision | posture constraints | doc | forbidden_moves prompt | — |
| A3-04 | Texte explicite | professional UI | UI | Mêmes blocs ; style pro | — | **PARTIEL C16** — U16-P1/P2 E2E |

---

## 5. PERSONA B1 — Fabienne, tutrice entreprise (TUTOR)

**Rôles :** TUTOR

| ID | Oracle | Contrat | Type | SUCCÈS | ÉCHEC |
|----|--------|---------|------|--------|-------|
| B1-01 | Pas verbatim privé | Confidentialité | permission | Timeline sans messages **ni** `first_learner_message` si `share_verbatim=false` | Contenu session non partagée visible | **SUCCÈS local** · `test_cluster3_oracles.py::test_b1_01_*` |
| B1-02 | Pas P0 dashboard | Pilotage | API+UI | Pas turn_state dans API tuteur | P0 exposé |
| B1-03 | Badges pilotage | timeline conversation_profile | UI | diagnostic/savoirs/réflexif | — |
| B1-04 | Valide trace si habilité | Trace | API | 200 validation si rôle OK | 403 incohérent |
| B1-05 | Ne change pas posture | set-posture | permission | Pas d'API tuteur posture | Modification posture |

---

## 6. PERSONA B2 — Mehdi, formateur-tuteur (TUTOR / TRAINER)

| ID | Oracle | Contrat | Type | SUCCÈS | ÉCHEC |
|----|--------|---------|------|--------|-------|
| B2-01 | Cohort sans P0 | analytics/cohort-metrics | API | Pas verbatim/p0 | Fuite contenu |
| B2-02 | QualitySignal interne | ConversationQualitySignal | pytest | record après session | — |
| B2-03 | Signaux pas apprenant | UIState | UI | Absents /app | Signaux qualité visibles |

---

## 7. PERSONA C1 — Amélie, formatrice conceptrice (TRAINER)

| ID | Oracle | Contrat | Type | SUCCÈS | ÉCHEC |
|----|--------|---------|------|--------|-------|
| C1-01 | Valide TrainerKnowledgeItem | trainer/knowledge validate | API | Statut validated_trainer (**validé C15**) | — |
| C1-02 | Ingest document | trainer/documents/ingest | API | Items structurés (API ; UI file_path V0) | Échec silencieux |
| C1-03 | Pas session non partagée | Confidentialité | permission | 403/empty (**validé C15**) | Fuite verbatim |
| C1-04 | Conduct profile | conduct-profiles API | API | Sauvegarde par posture | — |
| C1-05 | Choix profil cohorte `[CIBLE]` | learner_display_profile | API | N/A | — |

---

## 8. PERSONA C2 — Bernard, expert métier (TRAINER)

| ID | Oracle | Contrat | Type | SUCCÈS | ÉCHEC |
|----|--------|---------|------|--------|-------|
| C2-01 | UI sans jargon P0 | Interface formateur | UI | Libellés métier | TurnState visible |
| C2-02 | Valide évaluation | trainer evaluation validate | API | 200 sur record | — |

---

## 9. PERSONA D1 — Sylvie, ORGADMIN (ORGADMIN)

| ID | Oracle | Contrat | Type | SUCCÈS | ÉCHEC |
|----|--------|---------|------|--------|-------|
| D1-01 | Isolation tenant users | auth | permission | Pas user autre org | Fuite |
| D1-02 | Evidence bundle filtré | EvidenceBundleView | export | traces.json que son org | UUID autre org |
| D1-03 | Bundle non certifiant | doc | doc | Pas libellé certification | « Certifié Hugo » |
| D1-04 | Pas export debug | export-md `[CIBLE]` | permission | 404/403 pour ORGADMIN | ZIP P0 accessible |
| D1-05 | Choix profil org `[CIBLE]` | learner_display_profile | API | N/A | — |
| D1-06 | Pas LLM analysis | D9bis `[CIBLE]` | permission | Absent | Analyse LLM téléchargeable |

---

## 10. PERSONA D2 — Jean-Louis, ORGADMIN petit CFA (ORGADMIN)

| ID | Oracle | Contrat | Type | SUCCÈS | ÉCHEC |
|----|--------|---------|------|--------|-------|
| D2-01 | Admin biblio RAG | GroupAdminDetailView | UI | Index + liaison groupe | — |
| D2-02 | Export période | EvidenceBundleView | export | traces.json cohérent période | Cross-org |
| D2-03 | Parcours démo baseline A | doc 07 | doc | Scénario reproductible | — |

---

## 11. PERSONA E1 — Hélène, coordinatrice (COORDO) `[CIBLE]`

**Rôle non livré — oracles préparatoires uniquement.**

| ID | Oracle | Type | Statut |
|----|--------|------|--------|
| E1-01 | Rôle COORDO distinct | doc | A_VERIFIER |
| E1-02 | Validation traces coordination | API | `[CIBLE]` |
| E1-03 | Agrégat multi-groupes sans verbatim | API | `[CIBLE]` |

---

## 12. PERSONA F1 — Romain, superadmin technique (SUPERADMIN)

| ID | Oracle | Contrat | Type | SUCCÈS | ÉCHEC |
|----|--------|---------|------|--------|-------|
| F1-01 | export-md `[CIBLE]` | debug export | API | Endpoint réservé superadmin | Accessible ORGADMIN |
| F1-02 | ConversationTurnLLMAnalysis `[CIBLE]` | D9bis | export | Objet + export marqué non produit | Dans UIState |
| F1-03 | Pas lecture libre apprenant | Doctrine | permission | Accès session sans garde share | Lecture masse verbatim |
| F1-04 | Surfaces ≠ /app | Routes | UI | tester/admin séparés | Debug dans /app |
| F1-05 | turn-review / internal | views_internal | API | Réservé calibration | Exposé prod |

---

## 13. PERSONA G1 — Faible littératie numérique (EDGE LEARNER)

| ID | Oracle | Contrat | Type | SUCCÈS | ÉCHEC |
|----|--------|---------|------|--------|-------|
| G1-01 | Mode dégradé lisible | engagementModel.isDegraded | UI | Message clair si pas ui-state | Écran cassé |
| G1-02 | Pas jargon technique | INV-01, INV-04 | UI | — | reason_codes visibles |
| G1-03 | UI jeune guidée `[CIBLE]` | DSP-01 | UI | N/A | — |
| G1-04 | CTA helper_text | cta_* | UI | Texte si disabled | Bouton sans explication |

---

## 14. PERSONA G2 — Apprenant autonome (EDGE LEARNER)

| ID | Oracle | Contrat | Type | SUCCÈS | ÉCHEC |
|----|--------|---------|------|--------|-------|
| G2-01 | set-posture API | POST set-posture | API | 200 + posture persistée | 400 transition |
| G2-02 | Sélecteur UI `[CIBLE]` | conversation_mode | UI | N/A | — |
| G2-03 | early_trigger éval | EvaluationPolicy | API | Éval avec warning si policy | Sans garde |
| G2-04 | dispersion_risk | ConversationProgress | API | reason si trop branches | — |

---

## 15. PERSONA G3 — ORGADMIN limites confidentialité (EDGE)

| ID | Oracle | Contrat | Type | SUCCÈS | ÉCHEC |
|----|--------|---------|------|--------|-------|
| G3-01 | IDOR session | multi-tenant | permission | 404/403 autre org | 200 + data |
| G3-02 | IDOR bundle | EvidenceBundleView | export | Filtrage strict | Traces autre org |
| G3-03 | Pas debug P0 | export-md | permission | Refus ORGADMIN | ZIP P0 |
| G3-04 | Pas LLM analysis | D9bis | permission | Absent | Export analytics |

---

## 16. Grille campagne (personae × domaines × prompts)

| Domaine | Personae | Prompt cluster2 | Priorité auto |
|---------|----------|-----------------|---------------|
| 10 UIState/CTA/posture | A1, A2, G1, G2 | §C, §B | pytest + API |
| 20 Mémoire | A1, A2 | §D | API memory-summary |
| 30 RAG | A3, A1 | §E | API + UI badge |
| 70 Éval/traces | A1, G2 | §F | pytest CTA guards |
| 90 Confidentialité | A1, B1, G3 | §I.1 | permission tests |
| 100 Exports | D1, D2, F1 | §G, §H | export ZIP |
| 110 Interfaces | C1, B1, D1 | §J | UI + doc |
| Profils affichage `[CIBLE]` | A1, A2, A3, C1, D1 | §C.1 | doc jusqu'à code |

---

## 17. Fiche exécution (template)

```markdown
# ORACLE RUN — [PERSONA] — [DATE]

- Runtime : [local | Encoors]
- Session : [uuid]
- gamification_profile : [A|B|C]
- learner_display_profile : [N/A | CIBLE]
- Posture : [code]

| ID | Type test | Résultat | Preuve |
|----|-----------|----------|--------|
| … | API/UI/… | SUCCÈS/ÉCHEC/A_VERIFIER | curl, screenshot, test name |

Écarts → D2-Mxx
```

---

## 18. Priorités d'exécution (V2)

**Cluster 3 court — exécuté (2026-06-16) :**
1. ~~INV-01, INV-03, INV-06, A1-04, A1-05, B1-01, D1-02, G3-01~~ → **8/8 verts** en local (`test_cluster3_oracles.py` + tests existants)
2. ~~B1-01 patch `first_learner_message`~~ → **corrigé** (`views_dashboard.py`)

**Immédiat (pytest + curl, sans Chromium) — reliquat :**
1. B1-02 pilotage vs P0 (test legacy `p0_debug` à recaler sur `pilotage` — hors cluster 3)
2. F1-02 négatif : grep → doc ABSENT

**Moyen terme (UI / parcours) — mise à jour 2026-06-18 :**
1. ~~A1 posture UI~~ → **PARTIEL+ livré C16** (`PostureSelector`, Playwright U16-S1)
2. ~~C1 validation workflow~~ → **PARTIEL+ livré C15** (tableau + élicitation)
3. Parcours tuteur UI bout-en-bout (au-delà de B1-01 API) — **ouvert**
4. ~~Playwright C15/C16 apprenant~~ → **PASS C16** (10 tests U16-S/P)

---

## 19. Oracles validés localement — campagne post-tests (2026-06-18)

| Oracle / persona | Test(s) | Statut |
|------------------|---------|--------|
| A1-05 memory-summary | `test_cluster15_interfaces_apprenant.py`, smoke | **OK** |
| A1-07 set-posture API | cluster 15, `test_posture_modes.py` | **OK** |
| A1-08 posture UI | `PostureSelector.vue`, cluster16 Playwright | **OK** |
| A2-05 / A3-04 profils affichage | cluster 16 U16-P1/P2 | **PARTIEL** — E2E structure ; ressenti manuel S16-A4/A5 |
| A2/A3 profils + CTA | cluster 15 + 16 apprenant | **OK** |
| C1-01 validate/provisional/reject | cluster 15 formateur (8 tests) | **OK** |
| C1-03 confidentialité trainer | cluster 15 formateur | **OK** |
| Élicitation C1 | `test_c1_elicitation_*` | **OK** |
| INV-01, A1-04, B1-01, D1-02, G3-01 | cluster 3 | **OK** (2026-06-16) |
| conversation_mode + display profile | cluster 4 | **OK** |

**Run consolidé C15 :** 90 passed — voir `rapport_mise_a_jour_doc_post_tests_2026-06-18.md`.  
**Run cluster 16 :** 15 backend + 10 Playwright PASS — voir `cluster16_interface_apprenant_resultats_tests.md`.

**Reste `[CIBLE]` / manuel :** IFT-042, S16-A2/A3 advisory UX, Encoors, intercalaires 120, RAG vectoriel.

**Long terme (`[CIBLE]`) :**
1. DSP-01..07 profils affichage
2. F1-01, F1-02 artefacts LLM
3. E1 COORDO

---

## 19. Cluster 3 court — bilan et fermeture cycle

**Catalogue oracles complet :** sections 0–17 ci-dessus · **Rapport détaillé :** `cluster3_validation_courte_personae.md`

### Oracles prioritaires — statut final (local)

| Oracle | Persona | Statut | Preuve |
|--------|---------|--------|--------|
| INV-01 | A1 | **SUCCÈS** | `test_cluster3_oracles.py`, `test_p0_non_regression.py` |
| INV-03 | A1 | **SUCCÈS** | `test_request_evaluation_guard.py`, `test_cta_*` |
| INV-06 | A1 | **SUCCÈS** | `test_session_memory_contract.py` |
| A1-04 | A1 | **SUCCÈS** | `test_cluster3_oracles.py::test_a1_04_*` |
| A1-05 | A1 | **SUCCÈS** | `test_session_memory_contract.py` (verbatim exclu) |
| **B1-01** | B1 | **SUCCÈS** (post-patch) | `test_cluster3_oracles.py::test_b1_01_*` |
| D1-02 | D1 | **SUCCÈS** | `test_cluster3_oracles.py::test_d1_02_*` |
| G3-01 | G3 | **SUCCÈS** | `test_cluster3_oracles.py::test_g3_01_*` |

### B1-01 — correction documentée

- **Avant :** `messages: []` mais `first_learner_message` exposait un extrait du 1er message apprenant.
- **Après patch :** `first_learner_message` vide si `share_verbatim=false`, aligné sur `messages[]`.
- **Fichier code :** `hugo_back/apps/hugo/views_dashboard.py` (`DashboardTimelineView`).
- **Écarts alignés :** `ecarts — 90` §4.6, `ecarts — 110` §4.6, `cluster2_matrice_runtime_vs_cible.md` §6.2.

### Recommandation unique — prochain move

**Patch B1-01 appliqué et validé** — ne pas rouvrir ce correctif.

**Prochaine étape :** ~~D2-M01 / enum backend D2-M08~~ **fait C4** — enchaîner sur **front** (rendu 3 grammaires) puis **D9bis** / **D2-M05** si priorisés.

Smoke CI suggérée : `pytest apps/hugo/tests/test_cluster3_oracles.py -q`.

---

## 20. Cluster 4 — contrats de surface (bilan)

**Livré backend :** `conversation_mode` + `learner_display_profile` dans UIState (`test_cluster4_surface_contracts.py` — 9/9 OK).

**Reste CIBLE :** rendu front 3 grammaires, persistance profil org/groupe (DSP-05/06), sélecteur posture UI.

**Prochain move :** consommation front + endpoints persistance profil — voir `cluster4_surface_contracts.md`.

---

## 21. Cluster 16 — interface apprenant spec 2.0 (bilan)

**Livré local :** polish apprenant — `allowed_posture_transitions`, `dispersion_risk`, CTA `ui.advisory`, bandeau scène, profils homogènes, mémoire tronquée.

**Tests :** 15 backend (`test_cluster16_interface_apprenant_backend.py`) + 10 Playwright (`cluster16_learner_interface.spec.ts`) — **PASS**.

**PARTIEL restant :** verrou posture par phase/tours, IFT-042, Encoors, scénarios manuels S16-A1→A5.

**Références :** `cluster16_interface_apprenant_spec_conformite_resultats.md`, `cluster16_interface_apprenant_resultats_tests.md`.

---

