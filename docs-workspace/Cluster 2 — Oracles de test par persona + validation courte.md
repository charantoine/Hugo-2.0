# Cluster 2 — Oracles de test par persona + validation courte

**Workspace :** `/Users/machin/Desktop/Zone de travail Hugo`  
**Version :** 3 (alignement 13 domaines — 2026-06-18)  
**Documents liés :** `cluster2_oracles_test_par_persona.md` · `cluster3_validation_courte_personae.md` · `cluster4_surface_contracts.md` · `cluster2_matrice_runtime_vs_cible.md`

---

## Synthèse exécutive

| Élément | Statut |
|---------|--------|
| Cluster 2 (matrice, oracles, prompts) | **Livré** |
| Cluster 3 court (8 oracles) | **8/8 verts** |
| Cluster 4 (surface UIState) | **Livré backend** — `conversation_mode` + `learner_display_profile` |
| Smoke tests | `test_cluster3_oracles.py` + `test_cluster4_surface_contracts.py` |

**Prochain move :** parcours encadrants Vague 3 (B1/C1/D1) — sélecteur posture G2-02 et intercalaires v1 restent couronne.

---

## Rattachement au plan de convergence

Les oracles et validations de ce document s’inscrivent dans la trajectoire décrite par `plan_documentation_cto_convergence_hugo.md` (Vagues 1–3 + couronne optionnelle) et la synthèse `synthese_globale_ecarts_par_domaine.md`.

| Périmètre oracle | Domaines principaux | Vague plan CTO |
|------------------|---------------------|----------------|
| INV, A1, DSP, G2 | 10, 20, 31, 70 | Vague 1–2 (noyau apprenant) |
| B1, G3, F1, D1 | 90, 100, 110 | Vague 2–3 (confidentialité, exports) |
| Scénarios futurs C1, B1 étendu | 40, 50, 60, 120 | Vague 3 + couronne |

**Règle de priorisation :** ne pas ouvrir de nouveaux oracles sur la couronne (D9bis, intercalaires v1, RAG vectoriel) tant que la Vague 3 encadrants n’est pas arbitrée. Les oracles existants (clusters 3–7, ~70 tests backend + 14 front) restent la baseline de non-régression.

---

## Cluster 4 — contrats de surface

```bash
cd hugo_back && .venv/bin/python -m pytest apps/hugo/tests/test_cluster4_surface_contracts.py -q
# 9 passed
```

| Champ UIState | Statut | Preuve |
|---------------|--------|--------|
| `conversation_mode` | **IMPLÉMENTÉ** | INV-07, A1-08 (API) |
| `learner_display_profile` | **IMPLÉMENTÉ** (enum + query param) | INV-08, DSP-01..04 (contrat) |

Détail : `cluster4_surface_contracts.md`

---

## Cluster 3 — oracles prioritaires (rappel)

8/8 verts · commande : `pytest apps/hugo/tests/test_cluster3_oracles.py -q`

---

## Recommandation CTO

**Démontrable maintenant :** contrat UIState enrichi, testé, sans fuite P0 — prêt pour le front apprenant.

**Reste CIBLE :** sélecteur posture UI, rendu visuel jeune/adulte/pro, endpoints configuration profil par formateur/ORGADMIN, D9bis, EvaluationTrace.

---

**Références :** `cluster2_oracles_test_par_persona.md` §19–20 · `cluster4_surface_contracts.md`
