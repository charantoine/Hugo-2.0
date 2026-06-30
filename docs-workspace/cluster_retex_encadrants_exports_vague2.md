# Retex cluster encadrants & exports — vague 2 (dev + tests)

> Capitalisation CTO — chaîne audit → dev → tests → doc  
> Sources : `cluster2_encadrants_roles_audit_reel_vs_cible.md`, `cluster_dev_encadrants_exports_vague2_resultats.md`, `cluster_tests_encadrants_exports_post_vague2_resultats.md`, `cluster2_matrice_runtime_vs_cible.md` V3, écarts 90/100/110/70, `plan_documentation_cto_convergence_hugo.md`.

**Date de clôture :** 2026-06-18  
**Environnement prouvé :** local (SQLite, pytest, tests front unitaires) — **prod Encoors / RLS Postgres = A_VÉRIFIER**.

---

## 1. Objet et périmètre du cluster

### Objectif doctrinal (plan CTO)

Converger le **noyau Vague 2–3** sur les domaines **90** (confidentialité / rôles / multi-tenant), **100** (exports / preuves / Qualiopi lite), **110** (interfaces encadrants), avec les liens nécessaires vers **70** (évaluation / traces / preuves), sans ouvrir la **Couronne** (D9bis analytics LLM, intercalaires v1, observabilité 80 avancée).

Alignement plan CTO étapes 5–8 :
- **Vague 2** : confidentialité & exports minimaux (D2-M07, D2-M11), guards rôles, EXIF Evidence.
- **Vague 3** : parcours encadrants minimaux (B1/C1 partiels), surfaces prod tuteur/formateur.

### Périmètre réel du cluster dev

**Retenu et livré (P0 + P1 structurants) :**
- Guards `can_manage_trainer_knowledge` sur APIs trainer (elicitation, ingest, validate, list).
- Alignement front/back exports (`isOrgAdminLike` ↔ `is_admin_like` backend).
- Strip EXIF + GPS meta opt-in sur Evidence.
- Surfaces prod minimales : `/app/tutor/*`, `/app/trainer/knowledge`.
- Router guards LEARNER vs routes encadrants/admin.
- Mises à jour doc ciblées (écarts 90/100/110/70, matrice, specs interface, plan CTO).

**Explicitement hors scope :** D9bis, bundle enrichi, D2-M12 (ORGADMIN vs SUPERADMIN), UI éval tuteur, ingest formateur prod, RLS prod, oracle Encoors.

### Périmètre réel de la campagne de tests

Blocs **T** (gardes rôles), **E** (EXIF / bundles lite), **S** (surfaces prod encadrants), **X** (CTA éval → trace → export), **R** (synthèse doc).

**51 tests verts** (43 pytest campagne + 3 CTA éval + 5 front unitaires), **0 échec**, environnement local uniquement.

---

## 2. Résultats atteints (réel confirmé)

### 2.1 Niveau code / tests

#### P0 effectivement corrigés

| Écart P0 (audit initial) | Correction | Preuve |
|---|---|---|
| Décalage UI exports vs backend 403 | `GroupView` + `roleGuards.isOrgAdminLike` | 5 tests front + code review |
| Endpoints trainer sans garde rôle | `can_manage_trainer_knowledge` | `test_encadrants_role_guards.py` (9) |
| Tests négatifs rôles manquants | Pack pytest dédié | 9 + E3/E4 exports |
| EXIF annoncé non implémenté | `evidence_media.py` + Pillow | `test_evidence_exif.py` (2) |
| Bundle sur-vendu comme riche | Doc + tests shape lite | `test_d2_m06_*` bundle |

#### Volume et portée des tests

| Suite | N | Portée réelle |
|---|---|---|
| `test_encadrants_role_guards.py` | 9 | LEARNER/TUTOR/TRAINER/ORGADMIN × trainer + ExportRun |
| `test_evidence_exif.py` | 2 | EXIF strip, GPS opt-in meta |
| `test_d2_m06_d2_m11_exports_and_analytics.py` | 14 | Bundle lite, cross-tenant, absence D9bis |
| `test_d2_m07_confidentiality_oracles.py` | 10 | B1-01/B1-02, G3, F1 |
| `test_tutor_access_control.py` | 7 | Links tuteur, pilotage sans P0 |
| `test_trainer_knowledge.py` | 1 | Flow elicitation → validate |
| CTA évaluation | 3 | UIState contract, request-evaluation guards |
| `roleGuards.test.js` | 5 | Alignement getters front |

**Ce que les tests ne prouvent pas :** E2E navigateur multi-rôles, SUPERADMIN explicite, prod Encoors, RLS Postgres.

#### Domaines × statut (local)

| Domaine | ALIGNE | PARTIEL | ABSENT | A_VÉRIFIER |
|---|---|---|---|---|
| **90** | Guards trainer ; exports org ; B1-01/B1-02 ; router LEARNER | SUPERADMIN pytest ; matrice D2-M07 complète | Frontière ORGADMIN/SUPERADMIN (D2-M12) | RLS prod ; Encoors timeline |
| **100** | EXIF/GPS ; bundle lite ; cross-tenant ; permissions exports | Formats image exotiques | EvaluationTrace dans ZIP ; D9bis | ZIP prod Encoors |
| **110** | Timeline backend tuteur ; routes prod + guards code | Surfaces prod sans E2E ; ingest formateur prod | UI éval partagée tuteur ; orchestrateurs 50/60 UX | Parité Encoors `/app/tutor` |
| **70** | CTA contract ; generate-trace → export JSON ; eval export filtré | Chaîne UI prod bout-en-bout | EvaluationTrace agrégat 2.0 | Prod distante éval |

**Lecture CTO :** les **P0 domaines 90 et 100 sont couverts localement** (code + tests). **110 et 70 restent partiellement ouverts** sur le plan produit/E2E.

### 2.2 Niveau produit / parcours

#### TUTEUR

**Peut faire (réel local) :**
- Accéder à `/app/tutor/*` (layout prod) : liste groupes → apprenants liés → timeline.
- Lire traces (métadonnées), verbatim et `pilotage` **uniquement si** `share_verbatim=true` (B1-01).
- Valider une trace si `TutorLearnerLink` + membership groupe.

**Ne peut pas / n’a pas :**
- Export org-wide (403 backend, boutons masqués front).
- Lire P0 / TurnState brut (B1-02).
- Recommandations moteur, CTA tuteur, commentaires structurés éval (cible non livrée).

#### FORMATEUR

**Peut faire :**
- `/app/trainer/knowledge` : liste `TrainerKnowledgeItem`, validation humaine.
- APIs trainer (elicitation, ingest, validate) si TRAINER/ORGADMIN/SUPERADMIN.

**Ne peut pas / n’a pas :**
- Ingest documentaire en UI prod (reste API / shell tester).
- Accès timeline apprenant non partagé (pas de route dédiée).
- Orchestrateur formateur complet (domaine 50 — cible).

#### ORGADMIN / SUPERADMIN

**Peut faire :**
- `ExportRun` CSV/JSON `trace_rich_v1`, `EvidenceBundle` Qualiopi lite (tenant-scoped).
- Boutons export sur `GroupView` et pages admin (route `requiresOrgAdmin`).
- Knowledge trainer (ORGADMIN inclus dans `can_manage_trainer_knowledge`).

**Limites :**
- Code : `is_admin_like` = ORGADMIN + SUPERADMIN **identiques** sur exports (D2-M12 ouvert).
- SUPERADMIN non couvert par pytest dédié (**PARTIEL**).
- Pas de lecture verbatim masse apprenant via exports (bundle lite = métadonnées).

#### Absent côté UI (explicitement reporté)

- Évaluations partagées visibles tuteur (`ENC-CODE-10`).
- Ingest formateur prod (C1).
- Coordinateur : rôle sans surface dédiée (traité tuteur-like).

---

## 3. Écarts et limites identifiés

### Par bloc de test

| Bloc | Écart résiduel | Statut |
|---|---|---|
| **T** | SUPERADMIN non testé pytest | PARTIEL |
| **T** | `GET elicitation-questions` guard non testé isolément | PARTIEL |
| **T** | E2E navigateur 5 rôles × exports | A_VÉRIFIER |
| **E** | Formats image exotiques (HEIC…) | PARTIEL / hors scope |
| **E** | ZIP prod Encoors | A_VÉRIFIER |
| **S** | Surfaces `/app/tutor`, `/app/trainer/knowledge` sans E2E | PARTIEL |
| **S** | Ingest formateur prod | ABSENT |
| **X** | Chaîne UI prod session → éval → export même session | A_VÉRIFIER |
| **X** | EvaluationTrace dans bundle | ABSENT (voulu — doctrine lite) |

### Limites méthodologiques

**Ce que le cluster dev a bien préparé pour les tests :**
- Fichiers `test_encadrants_role_guards.py` et `test_evidence_exif.py` co-livés avec le code.
- `roleGuards.js` testable unitairement.
- Rapports `cluster_dev_*` et `cluster_tests_*` structurés blocs T/E/S/X/R.

**Ce qui aurait dû être anticipé :**
- Scénarios E2E Playwright dès la conception des routes prod (bloc S reste code-only).
- Tests SUPERADMIN dans le design initial des guards (évite PARTIEL post-campagne).
- Oracle Encoors planifié en amont du statut « surfaces prod livrées » (risque sur-promesse).

**Tests tardifs / manquants :**
- Pas de campagne navigateur dans ce cluster.
- Pas de test bout-en-bout ORGADMIN cliquant export après patch front (confiance code + pytest API).

---

## 4. Décisions de convergence prises

### Décisions techniques confirmées

| Décision | Justification |
|---|---|
| **EXIF strip + GPS meta opt-in** = invariant backend domaine 100 | CONF-22 ; tests `test_evidence_exif.py` |
| **`isAdminLike` front = ORGADMIN/SUPERADMIN** (TRAINER exclu) | Alignement `is_admin_like` backend ; fin des 403 cachés |
| **`can_manage_trainer_knowledge`** = TRAINER + ORGADMIN + SUPERADMIN | Cohérent avec `_can_manage_evaluations` ; LEARNER/TUTOR exclus |
| **EvidenceBundle reste lite** | 5 fichiers métadonnées ; pas EvaluationTrace 2.0 ; non certifiant |
| **`/app/tutor/*` et `/app/trainer/knowledge`** = socle encadrants prod minimal | Vague 3 amorcée ; compléments C1/D1 ultérieurs |
| **B1-01/B1-02** inchangés et re-validés | 17 tests confidentialité/tuteur verts |

### Décisions documentaires

| Domaine | Statut doc post-cluster |
|---|---|
| **90** | **ALIGNE local** sur P0 (guards, exports, B1) ; RLS/Encoors **A_VÉRIFIER** |
| **100** | **ALIGNE local** sur P0 (EXIF, permissions, bundle lite) |
| **110** | **PARTIEL** — surfaces prod code-only ; E2E ouvert |
| **70** | **PARTIEL** — chaîne trace→export backend OK ; EvaluationTrace doctrinal floue |

### Décisions de pilotage

- **Couronne inchangée :** D9bis, intercalaires v1 (120), observabilité 80 avancée, bundle enrichi.
- **Vague 3 reportée :** D2-M12 (ORGADMIN ≠ SUPERADMIN), UI éval tuteur, ingest formateur prod, oracle Encoors.
- **Ne pas promouvoir « IMPLÉMENTÉ prod »** sans run Encoors dédié (garde-fou méthodo maintenu).

---

## 5. Enseignements et recommandations pour les prochains clusters

### 5.1 Sur la méthode dev + test

#### Ce qui a bien fonctionné

1. **Chaîne audit → backlog ENC → dev P0 → campagne tests blocs T/E/S/X → retex** : traçabilité CTO lisible.
2. **Écarts de domaine + matrice cluster2** comme checklist : évite la dérive scope Couronne.
3. **Backend-first** : 46 pytest avant conclusion front — détecte guards sans E2E.
4. **Fichiers `cluster_*` satellites** : résultats dev et tests séparés, retex capitalisable.
5. **Bornage explicite « non retenu »** dans le rapport dev : limite les attentes.

#### Ce qui doit évoluer

1. **E2E Playwright/Cypress en parallèle du dev front** (routes prod, exports visibility) — pas en post-campagne seule.
2. **Matrice rôle × endpoint incluant SUPERADMIN dès le design** — tests pytest symétriques ORGADMIN/SUPERADMIN.
3. **Critères de clôture cluster** : distinguer « code livré » vs « parcours prouvé E2E » vs « prod A_VÉRIFIER ».
4. **Oracle Encoors** planifié comme gate optionnel avant statut ALIGNE prod (OPS-05).
5. **Liste Couronne figée en tête de cluster** — relue à la clôture pour éviter scope creep.

### 5.2 Impact sur le plan de convergence

#### Rapport au noyau convergé

| Vague plan CTO | Avancement post-cluster |
|---|---|
| **Vague 2** (confidentialité & exports) | **P0 local couvert** — guards, EXIF, exports alignés ; D2-M11 partiellement clos |
| **Vague 3** (encadrants B1/C1/D1) | **Amorcé** — surfaces prod minimales ; workflows bout-en-bout **PARTIEL** |
| **Couronne** | **Non entamée** — D9bis, intercalaires, observabilité 80 |

#### Domaines restant à traiter

| Domaine / lot | Contenu restant |
|---|---|
| **90** | D2-M12 ; RLS prod ; Encoors |
| **100** | D9bis ; bundle enrichi (Couronne) |
| **110** | E2E prod ; ingest formateur ; UI éval tuteur ; orchestrateurs 50/60 |
| **70** | EvaluationTrace agrégat ; chaîne UI prod complète |
| **120** | Intercalaires v1 (Couronne) |
| **80** | Observabilité / analytics LLM (Couronne) |

---

## 6. Suites concrètes (backlog haut niveau)

| ID | Type | Description | Lot |
|---|---|---|---|
| RETEX-01 | OPS | Campagne E2E Playwright : 5 rôles × exports + `/app/tutor` | Vague 3 |
| RETEX-02 | CODE | Tests pytest SUPERADMIN (exports + trainer) + `GET elicitation-questions` | Vague 2–3 |
| RETEX-03 | CODE | D2-M12 : frontière ORGADMIN vs SUPERADMIN sur exports sensibles | Vague 3 |
| RETEX-04 | OPS | Oracle Encoors : timeline B1-01 + exports ORGADMIN (gate prod) | Vague 3 |
| RETEX-05 | CODE | UI tuteur : `LearnerEvaluationRecord` partagés (lecture seule) | Vague 3 |
| RETEX-06 | CODE | Ingest formateur prod minimal (sans orchestrateur 50 complet) | Vague 3 |
| RETEX-07 | DOC | EvaluationTrace : mapping enrichi vs bundle lite (sans survente) | Vague 2–3 |
| RETEX-08 | CODE | D9bis analytics LLM export (si priorisation CTO) | **Couronne** |
| RETEX-09 | DOC/CODE | Intercalaires v1 + front multi-postures avancé | **Couronne** |
| RETEX-10 | DOC/CODE | Catalogue signaux observabilité 80 | **Couronne** |

---

## Synthèse exécutive (3 lignes)

1. **P0 domaines 90/100 : couverts localement** (code + 51 tests) — guards rôles, exports alignés, EXIF, bundle lite confirmé.  
2. **Domaines 110/70 : PARTIEL** — socle prod encadrants livré en code, sans E2E ni parcours C1/D1 complets ; EvaluationTrace hors bundle.  
3. **RLS / Encoors / prod distante : A_VÉRIFIER durable** — D9bis, intercalaires v1, observabilité 80 : **Couronne**, non négociée dans ce cluster.

---

*Retex produit pour la bibliothèque CTO Hugo convergence — cluster encadrants & exports vague 2.*
