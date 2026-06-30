# Retour d’expérience — Clusters 5 à 7 (profils, rôles, exports)

**Workspace :** `/Users/machin/Desktop/Zone de travail Hugo`  
**Date :** 2026-06-18  
**Public :** CTO / pilotage convergence  
**Question directrice :** après les clusters 1–4 et D2‑M05, la « seconde vague » locale (surfaces apprenant, confidentialité, exports) a-t-elle convergé proprement — et que rejouer si l’on repart d’un workspace neuf ?

---

## 0. Périmètre et posture

Ce document synthétise la trajectoire **locale** des clusters 5 à 7, tels qu’exécutés après la convergence des clusters 1–4 et le lot documentaire D2‑M05 (mapping EvaluationTrace).

| Cluster | Lots / objets | Périmètre réel du Retex |
|---------|---------------|-------------------------|
| **C5 — Surfaces apprenant** | D2‑M08 (complément cluster 4) | 3 grammaires `learner_display_profile` (youth / adult / professional), exploitation de `conversation_mode`, CTA et éligibilité **backend-driven** côté front |
| **C6 — Rôles / confidentialité** | D2‑M07 | Matrice rôles × surfaces, oracles B1 / D1 / G3 / F1, pack pytest dédié, recalibrage B1‑02 |
| **C7 — Exports & analytics** | D2‑M06 + D2‑M11 | Taxonomie E1–E6, photo des exports réels, D9bis laissé **CIBLE**, durcissement permissions E3/E4 |

**Hors périmètre explicite :** refonte orchestrateur P0, implémentation D9bis, migrations RLS Postgres, parité prod Encoors (marquée **A_VÉRIFIER**), sélecteur posture interactif (G2‑02).

**Distinction systématique utilisée :**

| Tag | Signification |
|-----|---------------|
| **CIBLE** | État visé Hugo 2.0 |
| **RÉEL OBSERVÉ** | Code, tests ou audits locaux vérifiables |
| **ÉCART CONFIRMÉ** | Divergence recoupée et documentée |
| **A_VÉRIFIER** | Dépend prod, RLS, flags, UI non rejouée |
| **HYPOTHÈSE** | Recommandation de replay, non prouvée par audit |

---

## 1. Sources mobilisées

### 1.1 Documents

| Document | Nature dominante | Rôle dans les clusters 5–7 |
|----------|------------------|------------------------------|
| `Retex_cluster_1-4.md` | Synthèse | Template méthodo, erreurs structurantes clusters 1–4 à ne pas répéter |
| `cluster2_matrice_runtime_vs_cible.md` | RÉEL + CIBLE + ÉCARTS | Domaines 70, 80, 90, 100, 110 ; backlog D2‑M05 à D2‑M11 ; statuts post‑C4 |
| `mapping_EvaluationTrace_runtime_local.md` | RÉEL + CIBLE | D2‑M05 — photo endpoints traces/éval/exports avant cluster 7 ; frontière EvaluationTrace vs dispersion runtime |
| `design_D2-M07_D2-M08_profils_grammaires_matrice_roles.md` | Synthèse + CIBLE | Design et plan d’exécution C5/C6 : 3 grammaires, matrice §B.2, batteries pytest/front |
| `design_D2-M06_D2-M11_exports_analytics.md` | Synthèse + RÉEL | Design et exécution C7 : taxonomie E1–E6, photo routes, décision D9bis, plan tests |
| `cluster4_surface_contracts.md` | RÉEL + CIBLE | Contrats `conversation_mode` / `learner_display_profile` (socle C5 backend) |
| `cluster4_front_A1_learner_display_profile_conversation_mode.md` | CIBLE → RÉEL partiel | Design front initial cluster 4 ; base du complément D2‑M08 |
| `ecarts — 90_confidentialite_partage_multitenant_roles.md` | ÉCARTS | Doctrine confidentialité, B1‑01, matrice tuteur — ancrage C6 |
| `ecarts — 70_evaluation_traces_preuves.md` | ÉCARTS | Branche terminale, traces — contexte exports E1/E2 |
| `ecarts — 100_exports_preuves_qualiopi_lite.md` | ÉCARTS | Doctrine exports / preuves — contexte E3/E4 |
| `ecarts — 110_interfaces_formateur_tuteur.md` | ÉCARTS | Interfaces encadrants — lien C5 (profils cohorte) et C6 (timeline) |

### 1.2 Tests backend et front

| Fichier | Cluster(s) | Objet principal | Nature |
|---------|------------|-----------------|--------|
| `test_cluster4_surface_contracts.py` | C5 | `conversation_mode`, `learner_display_profile`, cascade groupe/org | **RÉEL OBSERVÉ** — 11 tests |
| `test_cta_synthesis_contract.py` | C5 (socle C1) | CTA synthèse dans UIState | **RÉEL OBSERVÉ** — 2 tests |
| `test_cta_evaluation_contract.py` | C5 (socle C1) | CTA évaluation dans UIState | **RÉEL OBSERVÉ** — 1 test |
| `test_session_memory_contract.py` | Socle C1 | Mémoire intra, garde-fou verbatim | **RÉEL OBSERVÉ** — 5 tests |
| `test_d2_m07_confidentiality_oracles.py` | C6 | B1, D1, G3, F1, INV‑01 multi-rôles | **RÉEL OBSERVÉ** — 10 tests |
| `test_cluster3_oracles.py` | C6 (héritage C3) | INV‑01, A1‑04, B1‑01, G3‑01, D1‑02 bundle | **RÉEL OBSERVÉ** — 5 tests |
| `test_tutor_access_control.py` | C6 | Accès tuteur, recalibrage B1‑02 (`pilotage`) | **RÉEL OBSERVÉ** — 7 tests |
| `test_d2_m06_d2_m11_exports_and_analytics.py` | C7 | E3/E4 forme, rôles, D9bis absent, E2 partagé | **RÉEL OBSERVÉ** — 13 tests |
| `apps/exports/tests/test_exports_run.py` | C7 | ExportRun CSV/JSON, scoping tenant, audit | **RÉEL OBSERVÉ** — 12 tests |
| `test_p0_non_regression.py` | Transversal | UIState sans champs P0 | **RÉEL OBSERVÉ** — 4 tests |
| `frontend_1.8/src/utils/displayProfilePresets.test.js` | C5 | Presets youth/adult/professional, DSP‑02/04/07 | **RÉEL OBSERVÉ** — 4 tests |
| `frontend_1.8/src/utils/engagementUiModel.test.js` | C5 | Modèle engagement, CTA backend-driven, INV‑07/08 | **RÉEL OBSERVÉ** — 10 tests |

**Statut d’exécution local (2026-06-18, runtime Postgres + venv `hugo_back` + Node `frontend_1.8`) :**

| Batterie | Commande / périmètre | Résultat |
|----------|----------------------|----------|
| **Backend intégré clusters 5–7** | `pytest` sur mémoire, CTA, cluster3, cluster4, D2‑M07, D2‑M06/M11, P0, exports, tutor_access | **70/70 passés** |
| **Backend clôture C7 seule** (référence design) | `test_d2_m06_d2_m11` + exports + D2‑M07 + cluster3/4 + P0 | **55/55 passés** (sous-ensemble) |
| **Front profils / engagement** | `npm test` — `displayProfilePresets.test.js` + `engagementUiModel.test.js` | **14/14 passés** |
| **Test composant Vue** (`ConversationModeBanner`, `ProdLearnerWorkspace`) | — | **ÉCART CONFIRMÉ** — non livré ; couverture unitaire JS uniquement |

---

## 2. Ce qui a bien fonctionné — cluster par cluster

### 2.1 Cluster 5 — Surfaces apprenant (3 grammaires + conversation_mode)

**Objectif réellement poursuivi :** compléter le socle cluster 4 en rendant exploitables les **trois grammaires** `learner_display_profile` sur le parcours apprenant A1/A2/A3, sans recalculer CTA ni posture côté front, et en exposant `conversation_mode` comme libellé produit unique.

**Ce qui a marché :**

- **Contrat backend déjà vert (cluster 4)** — `resolve_learner_display_profile_for_session` et `conversation_mode` dérivé de `ConversationProgress.posture` ; 11 tests `test_cluster4_surface_contracts.py` stables après enrichissement front.
- **Séparation INV‑08 respectée** — `gamification_profile` (A/B/C) distinct de `learner_display_profile` ; badges « Style » vs « Engagement » dans `ProdLearnerWorkspace.vue`.
- **Couche présentation pure** — `displayProfilePresets.js` + `engagementUiModel.js` : la grammaire ne modifie que densité, hints, badges cosmétiques ; les labels CTA viennent de `cta_*.ui.button_label`.
- **Tests front ciblés** — DSP‑04/DSP‑07 (mêmes CTA sur les 3 profils), DSP‑01/02/03 (différences de rendu), INV‑07/A1‑08 (`conversation_mode.label`).

**Exemples concrets :**

1. **DSP‑04 / DSP‑07** — `engagementUiModel.test.js` : pour un même `BASE_UI_STATE`, les trois profils produisent des `button_label` identiques (`Obtenir une synthèse`, `Évaluation possible`) ; seuls hints et visibilité maturité varient.
2. **Cascade groupe** — `test_cluster4_surface_contracts.py` : `Group.learner_display_profile=youth` se propage dans UIState sans override query ; `?learner_display_profile=adult` prime sur le groupe.
3. **Adult vs youth** — `displayProfilePresets.test.js` : preset `adult` avec `showMaturityBadge: true` et hints distincts (`Décrivez la situation de départ.` vs tutoiement youth) ; aligné sur `ADULT_STEP_HINTS` dans `displayProfilePresets.js`.

---

### 2.2 Cluster 6 — Rôles / confidentialité

**Objectif réellement poursuivi :** stabiliser les accès multi-rôles sur timeline, UIState, bundles et surfaces sensibles ; formaliser la matrice rôles × données ; verrouiller par oracles pytest reproductibles (B1, D1, G3, F1).

**Ce qui a marché :**

- **Pack dédié D2‑M07** — `test_d2_m07_confidentiality_oracles.py` (10 tests) complète cluster 3 sans rouvrir l’orchestrateur.
- **B1‑01 déjà patché (C3), B1‑02 recalibré** — timeline tuteur expose `pilotage` (agrégat produit-safe), pas `p0_debug` / `turn_state` brut ; `test_tutor_access_control.py` aligné.
- **Isolation tenant avant exports** — G3‑01 (404 cross-org ui-state), D1‑02/G3‑02 (bundle scoped), F1‑03 (tuteur non lié → 403).
- **Frontière D9bis / LLM analysis** — D1‑06 et F1‑02 : absence de tokens `llm_analysis` / modèles dédiés dans UIState et EvidenceBundle (amorcé ici, renforcé en C7).

**Exemples concrets :**

1. **B1‑01** — `test_b1_01_timeline_hides_private_verbatim` : avec `share_verbatim=false`, la timeline tuteur n’expose pas le verbatim privé.
2. **G3‑03 / D1‑04** — `test_g3_03_d1_04_orgadmin_has_no_export_md_endpoint` : `GET .../debug/export-md/` → 404 (route absente, pas de surface debug déguisée en export métier).
3. **Matrice doc** — `design_D2-M07` §B.2 intégrée comme référence ; `ecarts — 90` reste la doctrine, le design sert de pont exécutable vers les tests.

---

### 2.3 Cluster 7 — Exports & analytics

**Objectif réellement poursuivi :** cartographier les exports réels (E1–E6), documenter la taxonomie, laisser D9bis en **CIBLE**, durcir les permissions ORGADMIN/SUPERADMIN sur E3/E4, verrouiller forme et non-fuite par tests.

**Ce qui a marché :**

- **Photo des exports sans survente** — EvidenceBundle = métadonnées traces ; ExportRun = `trace_rich_v1` + `payload_structured` tel que persisté ; `turn-review` classé E5 (debug), pas D9bis.
- **Décision D9bis « absence verrouillée »** — pas de nouveau modèle ni endpoint ; tests `test_no_d9bis_models_registered`, grep LLM analysis, frontière `turn-review` hors ZIP/ExportRun.
- **Durcissement permissions E3/E4** — `is_admin_like` sur `EvidenceBundleView`, `ExportRunView`, `ExportDownloadView` ; LEARNER → 403 ; scoping données inchangé (`organisation_id`).
- **Réutilisation des tests existants** — `test_exports_run.py` (12 tests) inchangé côté attentes (déjà ORGADMIN) ; cluster 3 D1‑02 complété par pack C7.

**Exemples concrets :**

1. **E3 forme** — `test_evidence_bundle_traces_json_shape` : chaque entrée `traces.json` = exactement `{trace_id, session_id, learner_id, validated_at, created_at}` ; `payload_structured` absent même si présent en DB.
2. **E4 rôles** — `test_learner_forbidden_on_evidence_bundle` et `test_learner_forbidden_on_export_run` : 403 après patch ; confirme matrice design §2.2 (ORGADMIN seul sur E3/E4).
3. **E2 export formateur** — `test_trainer_eval_export_only_shared_records` : `GET /hugo/trainer/evaluation-records/export/` ne retourne que les `LearnerEvaluationRecord` avec `shared_with_tutor=True`.

---

## 3. Ce qui n’a pas été comme prévu

### 3.1 Cluster 5 — Surfaces apprenant

| Dérive | Type | Détail | Visible quand ? |
|--------|------|--------|-----------------|
| Grammaires adult/professional peu différenciées au design | **Produit + doc** | Design D2‑M08 annonçait rendu **PARTIEL** (youth seul travaillé) ; complément front a enrichi adult, professional reste proche de l’historique | `design_D2-M07_D2-M08` §A.1 avant exécution |
| Décalage design ↔ tests front sur badge maturité | **Tests** | Test adult `showMaturityBadge` nécessitait aussi `gamification_profile: 'A'` (fusion preset × gamification) — échec initial avant correction | Exécution `displayProfilePresets.test.js` / `engagementUiModel.test.js` |
| Pas de test composant Vue | **Tests** | A1‑08 (bandeau mode) couvert en unitaire JS, pas en test `ConversationModeBanner.vue` | Même **ÉCART CONFIRMÉ** que Retex cluster 4 |
| CSS tokens inégaux | **Code** | `.prod-workspace--youth` plus travaillé que adult/professional au départ ; enrichissement CSS adult en lot D2‑M08 | Audit `style.css` design cluster 4 |
| DSP‑05 / G2‑02 toujours CIBLE | **Doc** | Formateur ne configure pas la cohorte ; pas de sélecteur posture UI — écart assumé, pas retard « surprise » | Matrice cluster 2 §8, design D2‑M08 |

### 3.2 Cluster 6 — Rôles / confidentialité

| Dérive | Type | Détail | Visible quand ? |
|--------|------|--------|-----------------|
| B1‑02 recalibré tard dans `test_tutor_access_control` | **Tests + séquencement** | Test legacy attendait `p0_debug` ; le code exposait déjà `pilotage` — bruit dans batterie élargie avant D2‑M07 | Retex cluster 1–4 §3.3 ; exécution D2‑M07 |
| Oracles dispersés sur plusieurs fichiers | **Tests + méthode** | B1‑01/D1‑02 dans cluster3 **et** D2‑M07 ; lisible mais index oracle → test non unique | Production pack D2‑M07 |
| Permissions exports E3/E4 non traitées en C6 | **Code + séquencement** | Matrice §B.2 listait ORGADMIN sur bundle ; code n’avait que `IsAuthenticated` — **ÉCART CONFIRMÉ** reporté au design C7 | Audit `quality/views.py` / `exports/views.py` avant cluster 7 |
| RLS Postgres / COORDO | **Doc** | Matrice et écarts 90 marquent RLS et rôle COORDO **A_VÉRIFIER** / **CIBLE** — hors lot | Design D2‑M07 §B.3 |
| `test_group_display_profile.py` prévu, non livré | **Tests** | Design D2‑M07 §B.4 item 4 — PATCH groupe cross-tenant couvert indirectement par cluster 4 | Plan design vs exécution |

### 3.3 Cluster 7 — Exports & analytics

| Dérive | Type | Détail | Visible quand ? |
|--------|------|--------|-----------------|
| Guards rôle trop laxistes à la photo initiale | **Code** | Tout utilisateur authentifié du tenant pouvait déclencher E3/E4 ; scoping données OK, rôle **PARTIEL** | Design C7 §1.1 avant patch |
| Confusion « Qualiopi lite » vs certification | **Doc + méthode** | EvidenceBundle nommé Qualiopi mais contenu minimal (métadonnées) — risque de sur-interprétation métier | `ecarts — 100`, design C7 §1.2 |
| Discussion D9bis pendant le design | **Méthode** | Modèles `ConversationTurnLLMAnalysis` absents mais `turn-review` et `llm_*_payload` présents — frontière à expliciter | Design C7 §1.6–1.7 |
| Risque de doublons de tests | **Tests** | D1‑02, F1‑02, D1‑06 recoupent D2‑M07 et C7 ; assumé comme renforcement, pas factorisation P3 | Plan design §5.1 (factorisation P3 non faite) |
| `test_export_run_json_no_p0_in_standard_trace` — périmètre | **Tests** | Première version greppait tout l’export (incluant trace fixture avec P0 en DB) ; corrigé en ciblant uniquement la trace `generate-trace` | Exécution pack C7 |
| Richesse bundle / prod | **A_VÉRIFIER** | Pas de `LearnerEvaluationRecord`, preuves binaires, ni EvaluationTrace doctrinal dans le ZIP local | `mapping_EvaluationTrace_runtime_local.md` §1.6 |

---

## 4. Erreurs structurantes à ne pas reproduire (vague 5–7)

| # | Erreur / fragilité | Visible dès | Aurait fallu | Impact |
|---|-------------------|-------------|--------------|--------|
| 1 | **Rôles exports E3/E4 = `IsAuthenticated` seul** malgré matrice doc ORGADMIN | Photo code `quality/views.py`, `exports/views.py` | Garde `is_admin_like` **dans le même lot** que les tests D1‑02 bundle, ou dès D2‑M07 §B.2 | Fenêtre où un LEARNER du tenant pouvait exporter ; correction seulement en C7 |
| 2 | **Confondre Qualiopi lite et export certifiant** | Écarts 100, naming endpoint | Libellé doc explicite « métadonnées non certifiantes » + test de forme `traces.json` dès le premier bundle test | Attentes métier/audit gonflées |
| 3 | **D9bis discuté sans tests d’absence** | Matrice domaines 70/80 | Décision binaire lot 0 : CIBLE + grep modèles + frontière E5 **avant** tout design export enrichi | Tentation d’ouvrir modèles LLM analysis prématurément |
| 4 | **Design front 3 grammaires sans tests DSP dans le même PR** | Cluster 4 (socle API seul) | Lot API + `displayProfilePresets.test.js` + au moins un test INV‑08 composant | Retard visible sur adult/professional ; itérations tests gamification |
| 5 | **Oracles confidentialité dupliqués sans index** | Cluster 3 + D2‑M07 + C7 | Tableau versionné « oracle → fichier → statut » (déjà recommandé Retex 1–4) | Onboarding CTO, risque de supprimer un test « doublon » utile |
| 6 | **B1‑02 laissé en test `p0_debug`** alors que produit expose `pilotage` | Cluster 3 hors scope | Recalibrage **dans** le lot confidentialité, pas après | Bruit CI, fausse alerte régression P0 |
| 7 | **ExportRun test P0 sur export global** au lieu de la trace squelette | Exécution C7 | Assertion ciblée sur l’objet `generate-trace` uniquement | Faux négatif si fixture DB contient P0 dans `payload_structured` |

---

## 5. Replay propre pour le CTO

### 5.1 Scénario A — Reprise après clusters 1–4 (rejouer 5–7)

**Point d’ancrage :** mémoire intra, CTA, UIState de base, cluster 4 API (`conversation_mode`, `learner_display_profile`) verts ; mapping D2‑M05 **optionnel** mais recommandé avant exports.

#### Cluster 5 — Surfaces apprenant

| Action | Contenu |
|--------|---------|
| **Garder tel quel** | Contrats cluster 4 backend ; `displayProfilePresets.js` / `engagementUiModel.js` ; tests DSP/INV front ; principe INV‑08 |
| **Re-séquencer** | API + presets front + **4 tests front minimum** dans **un seul lot** ; ne pas clore D2‑M08 sans `npm test` vert |
| **Renforcer** | 1 test composant bandeau A1‑08 ; tokens CSS pour les 3 profils |
| **Simplifier / jeter** | Designs UX cosmétiques (skins) avant DSP‑05 formateur |

#### Cluster 6 — Rôles / confidentialité

| Action | Contenu |
|--------|---------|
| **Garder tel quel** | `test_d2_m07_confidentiality_oracles.py` ; matrice §B.2 design D2‑M07 ; B1‑01 patch C3 |
| **Re-séquencer** | B1‑02 + `test_tutor_access_control` **avant** le pack 10 oracles ; inclure **permissions E3/E4** dès la matrice exports est rédigée |
| **Renforcer** | Test PATCH groupe cross-tenant dédié ; mise à jour `ecarts — 90` dans le même mouvement que les patches |
| **Simplifier / jeter** | Doublon doc entre design D2‑M07 et écarts 90 sans extrait matrice intégré |

#### Cluster 7 — Exports & analytics

| Action | Contenu |
|--------|---------|
| **Garder tel quel** | Taxonomie E1–E6 ; `test_d2_m06_d2_m11_exports_and_analytics.py` ; `test_exports_run.py` ; décision D9bis CIBLE |
| **Re-séquencer** | Design photo routes → patch permissions E3/E4 → pack tests (pas l’inverse) |
| **Renforcer** | Test forme bundle + test rôle LEARNER 403 dans le même PR que `is_admin_like` |
| **Simplifier / jeter** | Factorisation helpers bundle P3 si elle retarde la clôture ; tout nouveau export LLM (D9bis) |

**Mini-plan replay 5–7 (3 lots fermables) :**

```
Lot 1 — Front 3 grammaires + tests DSP/INV (C5)
Lot 2 — Confidentialité multi-rôles + permissions exports org (C6+C7 permissions)
Lot 3 — Taxonomie exports + pack D2-M06/M11 + D9bis absence (C7)
```

---

### 5.2 Scénario B — Reprise après cluster 5 seulement (front 3 grammaires déjà convergé)

**Point d’ancrage :** `test_cluster4_surface_contracts.py` + 14 tests front verts ; CTA et `conversation_mode` exploités.

| Volet | Replay recommandé |
|-------|-------------------|
| **C6** | Enchaîner directement `test_d2_m07_confidentiality_oracles.py` + recalibrage B1‑02 ; **ne pas** rouvrir les presets front |
| **C7** | Partir du mapping D2‑M05 (1 lecture) → design taxonomie E1–E6 → patch E3/E4 → pack C7 ; réutiliser oracles bundle D1‑02/F1‑02 existants |
| **Garde-fous** | Interdire tout changement `ui_state_builder` / `engagementUiModel` pendant C6–C7 sauf bug bloquant |
| **CI smoke** | `pytest` cluster3 + D2‑M07 + D2‑M06/M11 + `npm test` profils — batterie < 2 min idéale |

---

## 6. Synthèse transversale (clusters 5–7)

| Volet | RÉEL OBSERVÉ local | CIBLE / ÉCART | A_VÉRIFIER |
|-------|-------------------|---------------|------------|
| **Surfaces apprenant — contrat API** | `conversation_mode`, `learner_display_profile`, cascade groupe/org ; 11 tests cluster 4 | DSP‑05 formateur, G2‑02 sélecteur posture, UI admin défaut org | Parcours A2/A3 en démo réelle |
| **Surfaces apprenant — rendu front** | 3 presets, CTA backend-driven, bandeau mode, badges Style/Engagement ; 14 tests JS | Skins cosmétiques, test composant Vue, différenciation professional poussée | Accessibilité / mobile non audités |
| **Rôles / confidentialité** | B1‑01/02, G3‑01, D1‑02, F1‑02/03, INV‑01 ; 22 tests (D2‑M07 + cluster3 + tutor) | RLS Postgres, COORDO, lecture masse ORGADMIN | Prod Encoors, flags debug |
| **Exports E1 — apprenant** | `generate-trace`, `/learners/traces`, `/learners/evidence` | Payload trace riche post-éval dans `payload_structured` | EXIF/GPS preuves prod |
| **Exports E2 — formateur** | `evaluation-records/export` filtré `shared_with_tutor` | Validation humaine doctrine (non auto-certifiant) | Volume records en prod |
| **Exports E3 — EvidenceBundle** | ZIP métadonnées ; ORGADMIN/SUPERADMIN ; tests forme + P0 | Records éval, preuves binaires, lien EvaluationTrace | Richesse bundle prod |
| **Exports E4 — ExportRun** | `trace_rich_v1`, scoping tenant, ORGADMIN ; 12 + tests C7 | Filtrage P0 si payload enrichi côté moteur | Perf gros exports |
| **Exports E5 — debug** | `turn-review`, `pilotage`, `verbatim-window` ; `export-md` absent (404) | Surface technique bornée | `HUGO_DEBUG_TRACING` prod |
| **Exports E6 — D9bis** | **Absent** — tests registry + grep | Modèles et exports analytiques LLM dédiés | — |

**Verdicts par volet :**

| Volet | Verdict |
|-------|---------|
| Surfaces apprenant (3 grammaires) | **Fondation à garder** — contrat + presets + tests unitaires ; cosmétique et composants à compléter |
| Rôles / confidentialité | **Prêt local** pour oracles persona B1/D1/G3/F1 ; **A_VÉRIFIER** infra prod |
| Exports & analytics | **Prêt local** pour taxonomie et garde-fous E3/E4 ; **CIBLE** pour richesse Qualiopi et D9bis |

---

## 7. Message CTO — enseignements clusters 5–7

### Enseignements positifs

1. **Enchaînement design → exécution → batterie fermable** — chaque cluster a produit un design daté, un pack de tests nommé et un critère de clôture chiffré (70 backend, 14 front).
2. **Taxonomie E1–E6** — réduit les collisions entre export apprenant, bundle audit, debug et D9bis ; décision D9bis **décidable** sans implémentation.
3. **Tests d’absence** — efficaces pour D9bis et LLM analysis : registry Django, grep sérialisation, frontière `turn-review` vs E3/E4.
4. **3 grammaires sans fork UIState** — DSP‑04 tenu : un JSON backend, rendu variable front ; CTA inchangés (preuve test).
5. **Réutilisation des socles C1–C4** — mémoire, CTA, cluster3 n’ont pas été réécrits ; les nouveaux packs les complètent.

### Fragilités à surveiller

1. **Permissions rôle vs scoping tenant** — filtre `organisation_id` nécessaire mais **insuffisant** ; pattern à généraliser sur tout export org.
2. **Oracles éparpillés** — cluster3, D2‑M07, C7, exports : risque de régression silencieuse si la batterie CI n’est pas la batterie intégrée 70 tests.
3. **Qualiopi lite sur-vendu** — le nom invite à l’audit certifiant ; le ZIP local reste métadonnées.
4. **`payload_structured` hétérogène** — squelette `generate-trace` propre, mais traces DB peuvent porter P0 si injecté ailleurs ; ExportRun reflète la DB telle quelle.
5. **Couverture front composants** — même pattern que cluster 4 : logique JS verte, Vue non testée.

### Recommandation et priorités

| Option | Recommandation |
|--------|----------------|
| **Continuer depuis l’état actuel** | **Oui** — socle 5–7 vert localement ; enchaîner stabilisation doc (matrice §0 E1–E6, écarts 100) plutôt qu’un replay complet |
| **Replay documentaire partiel** | Mettre à jour `cluster2_matrice_runtime_vs_cible.md` (D2‑M07/M08/M11, permissions E3/E4 **IMPLÉMENTÉ**) et encarts écarts 90/100 |
| **Priorités A_VÉRIFIER avant démo / industrialisation** | (1) Parité Encoors exports et flags debug ; (2) RLS Postgres ; (3) richesse EvidenceBundle prod ; (4) parcours UI A2/A3 non rejoués en E2E ; (5) toute ouverture D9bis **uniquement** après garde-fous E5/E6 et décision CTO explicite |

**HYPOTHÈSE de suite :** un lot « D9bis minimal » ultérieur pourrait ajouter modèles + export SUPERADMIN **sans** modifier EvidenceBundle ni UIState, en réutilisant les tests d’absence actuels comme garde-fou de non-régression — non prouvé, à cadrer par décision produit.

---

**Références :** `Retex_cluster_1-4.md` · `design_D2-M07_D2-M08_profils_grammaires_matrice_roles.md` · `design_D2-M06_D2-M11_exports_analytics.md` · `mapping_EvaluationTrace_runtime_local.md`
