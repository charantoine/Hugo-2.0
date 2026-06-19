# Cluster 3 court — Validation opérationnelle personae prioritaires

**Workspace :** `/Users/machin/Desktop/Zone de travail Hugo`  
**Date :** 2026-06-16 (cluster 3) · **Extension 2026-06-18** (cluster 15 — voir §8)  
**Fermeture cycle :** voir aussi `Cluster 2 — Oracles de test par persona + validation courte.md`

### Sources mobilisées

- `docs-workspace/00_HIERARCHIE_DOCUMENTAIRE.md`, `DOC_METHODO_REFERENCE_CONVERGENCE_HUGO_REVISE.md`, `plan_documentation_cto_convergence_hugo.md`
- `cluster2_matrice_runtime_vs_cible.md`, `cluster2_oracles_test_par_persona.md`, `cluster2_prompts_audit_runtime_et_memoire.md`
- `ecarts — 90_confidentialite_partage_multitenant_roles.md`, `ecarts — 100_exports_preuves_qualiopi_lite.md`, `ecarts — 110_interfaces_formateur_tuteur.md`
- Code : `hugo_back/apps/hugo/`, `hugo_back/apps/quality/views.py`
- Tests : `hugo_back/.venv/bin/python -m pytest` (settings `config.settings.test`)

### Légende statuts de vérification

| Statut | Signification |
|--------|---------------|
| **Déjà couvert** | Test pytest pré-existant |
| **Testé cette passe** | Exécuté localement, résultat consigné |
| **Préparé pour test** | Script/test ajouté, exécutable sans manip humaine |
| **A_VERIFIER** | Dépendance prod / flag / UI non rejouée localement |

---

## 1. Périmètre du cluster 3 court

Objectif : validation opérationnelle **légère** et **automatisée** sur runtime local Django.

**In scope :** personae **A1, B1, D1** · oracles **INV-01, INV-03, INV-06, A1-04, A1-05, B1-01, D1-02, G3-01**

**Hors scope :** `conversation_mode`, profils d'affichage, LLM analysis, mémoire inter-sessions, RAG, prod Encoors.

**Statut global :** **clôturé** — 8/8 oracles verts en local après patch B1-01.

---

## 2. Personae et oracles retenus

| Persona | Rôle | Oracles |
|---------|------|---------|
| **A1** | LEARNER | INV-01, INV-03, INV-06, A1-04, A1-05 |
| **B1** | TUTOR | B1-01 |
| **D1** | ORGADMIN | D1-02, G3-01 |

---

## 3. Tableau oracle → mode de vérification

| Oracle | Mode | Preuve | Résultat local |
|--------|------|--------|----------------|
| **INV-01** | Testé | `test_cluster3_oracles.py::test_inv01_*`, `test_p0_non_regression.py` | **OK** |
| **INV-03** | Testé | `test_request_evaluation_guard.py`, `test_cta_*` | **OK** |
| **INV-06** | Testé | `test_session_memory_contract.py` | **OK** |
| **A1-04** | Testé | `test_cluster3_oracles.py::test_a1_04_*` | **OK** |
| **A1-05** | Testé | `test_session_memory_contract.py` | **OK** |
| **B1-01** | Testé + **patch appliqué** | `test_cluster3_oracles.py::test_b1_01_*` | **OK** — `messages[]` et `first_learner_message` vides si `share_verbatim=false` |
| **D1-02** | Testé | `test_cluster3_oracles.py::test_d1_02_*` | **OK** |
| **G3-01** | Testé | `test_cluster3_oracles.py::test_g3_01_*` | **OK** |

**Hors périmètre 8 oracles :** `test_dashboard_timeline_includes_p0_debug_without_prompt_leak` (legacy `p0_debug` vs `pilotage`) — non traité dans cette passe.

---

## 4. Résultats constatés sur local

### Smoke cluster 3

```bash
cd hugo_back && .venv/bin/python -m pytest apps/hugo/tests/test_cluster3_oracles.py -q
# 5 passed
```

### Batterie élargie (26 tests)

25/26 passés ; 1 échec legacy `p0_debug` (hors oracles prioritaires).

### Synthèse métier

| Statut | Oracles |
|--------|---------|
| **Validé local (OK)** | **Tous** — INV-01, INV-03, INV-06, A1-04, A1-05, **B1-01**, D1-02, G3-01 |
| **A_VERIFIER prod** | RLS Postgres, parité Encoors |

---

## 5. Scripts / tests produits

`hugo_back/apps/hugo/tests/test_cluster3_oracles.py` — 5 tests (INV-01, A1-04, B1-01, G3-01, D1-02).

---

## 6. Écarts documentaires ou techniques

| ID | Statut post-patch |
|----|-------------------|
| **B1-01** | **Corrigé** — `views_dashboard.py` ; docs `ecarts — 90/110`, matrice §6.2 |
| **Tuteur pilotage** | Test legacy obsolète — hors C3 |
| **D2-M01, D2-M08, D9bis, D2-M05** | **Ouverts** — prochain chantier contrats |

---

## 7. Recommandation unique — prochain move

**Patch B1-01 appliqué et validé** — cycle cluster 2 + cluster 3 court **fermé** côté oracles prioritaires.

**Prochaine étape :** contrats cibles, sans autres correctifs immédiats :
1. **D2-M01** — `conversation_mode` dans UIState ;
2. **D2-M08** — `learner_display_profile` ;
3. **D9bis** — `ConversationTurnLLMAnalysis` ;
4. **D2-M05** — mapping `EvaluationTrace`.

Smoke CI : `pytest apps/hugo/tests/test_cluster3_oracles.py -q`.

---

## 8. Extension cluster 15 (2026-06-18) — non clôture du cluster 3

Le cluster 3 court reste **clôturé** sur ses 8 oracles d’origine. Le cluster 15 ajoute une couverture **A1/A2/A3/C1** sans rouvrir le périmètre B1/D1.

| Fichier tests | Tests | Résultat |
|---------------|-------|----------|
| `test_cluster15_interfaces_apprenant.py` | 13 | PASS |
| `test_cluster15_interfaces_formateur.py` | 8 | PASS |
| Campagne consolidée (90 tests) | — | PASS — `rapport_mise_a_jour_doc_post_tests_2026-06-18.md` |

**Prochaine étape post-C15 :** Playwright check-lists §4 protocole interfaces ; Encoors A_VÉRIFIER.
