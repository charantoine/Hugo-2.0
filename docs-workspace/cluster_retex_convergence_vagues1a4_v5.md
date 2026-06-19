# Retex convergence Hugo cœur — vagues 1 à 4 + audit vague 5

> Photo de convergence locale vs plan CTO  
> Date : 2026-06-18  
> Sources : rapports cluster v2–v5, matrice cluster 2, écarts domaines, `cluster_tests_e2e_et_encoors_vague5_resultats.md`

---

## 1. Rappel objectifs plan CTO (noyau Hugo cœur)

Le plan CTO (`plan_documentation_cto_convergence_hugo.md`) vise l’alignement progressif du runtime local sur Hugo 2.0 pour :

- **Noyau apprenant** : P0/progression/UIState, mémoire intra, CTA synthèse/évaluation, RAG lexical borné.
- **Fin de fil** : traces, preuves, exports structurés, validation humaine — sans certification autonome.
- **Rôles & sécurité** : multi-tenant, partage explicite, guards encadrants, exports ORGADMIN.
- **Encadrants** : surfaces tuteur/formateur minimales prod.
- **Observabilité** : signaux backend techniques, canal D9bis séparé.

**Couronne explicitement hors noyau :** intercalaires v1, dashboards analytics produit, RAG vectoriel, D2-M12 fin, mémoire inter-sessions injection tour, équivalence prod Encoors non prouvée.

---

## 2. Ce qui est convergé localement (par vague)

| Vague | Livrable | Domaines | Preuve |
|---|---|---|---|
| **1** | Mémoire intra, CTA, RAG lexical | 20, 10, 30 | tests lot 1 |
| **2** | Guards rôles, EXIF, exports alignés, surfaces prod encadrants | 90, 100, 110 | 51 tests, retex v2 |
| **3** | Pivot EvaluationTrace, observabilité base, squelettes D9bis | 70, 80, 100 | 58 tests |
| **4** | D9bis backend, observabilité avancée v1 SUPERADMIN | 80, 100 | 68 tests |
| **5** | Photo E2E API + oracle Encoors | transversal | 8 E2E + 24 front |

---

## 3. Convergence par domaine (état vague 5)

| Domaine | Statut local | Preuves clés | Reste ouvert |
|---|---|---|---|
| **90** Confidentialité / rôles | **ALIGNE** (P0) | B1-01, guards exports/trainer, router | RLS prod, Encoors |
| **100** Exports / Qualiopi lite | **ALIGNE local** | bundle lite, ExportRun+pivot, cross-tenant | ZIP prod Encoors |
| **70** Évaluation / traces | **PARTIEL** | chaîne EVAL1 ALIGNE, pivot v1 | EvaluationTrace 2.0, criteria riches |
| **80** Observabilité | **PARTIEL** | base ORGADMIN + summary/D9bis SUPERADMIN | dashboards produit, catalogue signaux |
| **110** Interfaces encadrants | **PARTIEL** | routes `/app/*`, APIs timeline/knowledge | E2E browser, C1 dialogique |
| **60** Orchestrateur tuteur | **ALIGNE_DOC_PARTIEL+** | timeline, validation trace | prod Encoors |
| **40/50** Formateur | **PARTIEL** | knowledge list/validate | ingest prod, orchestrateur C1 |
| **30** RAG | **PARTIEL** | lexical | vectoriel Couronne |
| **120** Intercalaires | **CIBLE** | — | Couronne |

---

## 4. Couronne — non convergé (volontaire)

- Intercalaires v1 (120)
- Dashboards / analytics exposées produit (80/100)
- D9bis consommé par UX métier (interdit)
- RAG vectoriel (30)
- D2-M12 frontière ORGADMIN/SUPERADMIN fine
- Mémoire inter-sessions injection tour (20)
- Playwright E2E complet (OPS)
- Certification autonome (interdit doctrine)

---

## 5. Encoors / prod — A_VÉRIFIER systématique

**Fait vague 5 :**
- Routes v3/v4 (`observability`, `d9bis`, `conversation-summary`) → **404** sur Encoors (2026-06-18).
- `/exports/run/` → 401 sans JWT (route présente).

**Non fait (credentials absents) :**
- Comparaison payload generate-trace / ExportRun / bundle authentifié.
- RLS Postgres effective.

**Règle de lecture :** convergence locale **≠** parité Encoors. La démo distante ne prouve pas le local, ni l’inverse (`10_FICHE_RUNTIME_PROD_ENCOORS`).

---

## 6. Métriques tests cumulées (local)

| Campagne | Tests | Résultat |
|---|---|---|
| Vague 2 encadrants | 51 | 51/51 |
| Vague 3 fin de fil | 58 | 58/58 |
| Vague 4 D9bis | 68 | 68/68 |
| Vague 5 E2E + front | 32 | 32/32 |
| **Total cumulé indicatif** | **~209** | **vert local** |

*(Chevauchements possibles entre campagnes ; les suites v4 incluent déjà une large régression.)*

---

## 7. Recommandations prochains clusters

### Priorité UX / OPS
1. **Playwright smoke** multi-rôles (T1/F1/O1 manuel → automatisé).
2. **Deploy Encoors** ou branche staging alignée v3/v4 pour oracle authentifié.
3. Scénario manuel encadrants documenté dans `09_PARCOURS_DEMO_ET_SCENARIOS.md`.

### Priorité produit (si CTO valide)
4. Enrichissement payload trace (criteria) — valeur tuteur.
5. Parcours formateur C1 (ingest dialogique prod) — domaine 50.
6. D2-M12 — séparation ORGADMIN vs SUPERADMIN exports/UI.

### Priorité infra
7. Audit RLS Postgres prod.
8. Désactiver DEBUG Encoors (ops sécurité).

### Priorité clients / Couronne
9. Intercalaires v1, dashboards analytics — lots séparés.

---

## 8. Déclaration de convergence locale (bornée)

**Le noyau Hugo cœur local peut être déclaré convergent au sens du plan CTO pour :**

- Guards rôles et exports org (90/100)
- Surfaces encadrants minimales et APIs associées (110/60)
- Chaîne fin de fil CTA → évaluation → trace → pivot → export (70/100)
- Observabilité technique backend non frontalisée (80)
- Canal D9bis SUPERADMIN isolé (80/100)

**Sous réserve explicite :**

- Pas de parité Encoors prouvée.
- Pas de E2E navigateur automatisé.
- Couronne et enrichissements métier (criteria, C1, dashboards) restent ouverts.

---

## 9. Fichiers de référence

| Artefact | Rôle |
|---|---|
| `cluster_tests_e2e_et_encoors_vague5_resultats.md` | E2E + Encoors |
| `cluster2_matrice_runtime_vs_cible.md` | statuts domaines |
| `cluster_dev_*_vague*_resultats.md` | livrables dev |
| `cluster_tests_*_vague*_resultats.md` | campagnes pytest |
| `ecarts — *.md` | vérité par domaine |
