# Retour d’expérience — Clusters 1 à 4 (trajectoire locale Hugo 2.0)

**Workspace :** `/Users/machin/Desktop/Zone de travail Hugo`  
**Date :** 2026-06-16  
**Public :** CTO / pilotage convergence  
**Question directrice :** si l’on reprenait le développement à partir d’une étape antérieure, que conserver, corriger ou refaire pour converger proprement vers Hugo 2.0 ?

---

## 0. Périmètre et posture

Ce document synthétise la trajectoire **locale** des clusters 1 à 4 tels qu’ils ont été menés dans `docs-workspace` et `hugo_back` / `hugo-hugolucia`, sans rouvrir les débats doctrinaux généraux (AFEST, refonte moteur complète).

**Distinction systématique utilisée :**

| Tag | Signification |
|-----|---------------|
| **CIBLE** | État visé Hugo 2.0 |
| **RÉEL OBSERVÉ** | Code, tests ou audits locaux vérifiables |
| **ÉCART CONFIRMÉ** | Divergence documentée et recoupée |
| **A_VÉRIFIER** | Dépend prod Encoors, RLS, flags ou UI non rejouée |
| **HYPOTHÈSE** | Recommandation de replay, non prouvée par audit |

---

## 1. Sources mobilisées

### 1.1 Documents

| Document | Nature dominante | Rôle dans les clusters |
|----------|------------------|------------------------|
| `00_HIERARCHIE_DOCUMENTAIRE.md` | Méthode / hiérarchie de vérité | Règle code > tests > front ; statuts IMPLÉMENTÉ / CIBLE / A_VÉRIFIER |
| `DOC_METHODO_REFERENCE_CONVERGENCE_HUGO_REVISE.md` | Méthode | Patron réel / cible / écarts / A_VÉRIFIER ; backend-first |
| `plan_documentation_cto_convergence_hugo.md` | CIBLE + plan CTO | Lot courant = mémoire intra ; ordre contrats mémoire → CTA → RAG → EvaluationTrace |
| `20_memoire_gouvernee_note_lot_courant_memoire_intra_conversation.md` | RÉEL + CIBLE + ÉCARTS | Cluster 1 — audit mémoire, contrat intra, limites inter-sessions |
| `cluster2_matrice_runtime_vs_cible.md` | RÉEL + CIBLE + ÉCARTS | Cluster 2 — matrice domaines 10–110, statuts doc, lacunes |
| `cluster2_oracles_test_par_persona.md` | CIBLE + RÉEL (oracles) | Catalogue oracles INV / A1 / B1 / DSP par persona |
| `Cluster 2 — Oracles de test par persona + validation courte.md` | Synthèse | Fermeture cycles 2–4, smoke commands |
| `cluster3_validation_courte_personae.md` | RÉEL (validation) | Cluster 3 — 8 oracles, patch B1-01, hors scope C4 |
| `cluster4_surface_contracts.md` | RÉEL + CIBLE | Contrats `conversation_mode` / `learner_display_profile` |
| `cluster4_front_A1_learner_display_profile_conversation_mode.md` | CIBLE → RÉEL | Design puis implémentation front A1 + persistance groupe/org |
| `ecarts — 20_memoire_gouvernee.md` (référencé par note lot 1) | ÉCARTS | Domaine mémoire |
| `ecarts — 90_confidentialite_partage_multitenant_roles.md` | ÉCARTS | Confidentialité, B1-01 |
| `ecarts — 110_interfaces_formateur_tuteur.md` | ÉCARTS | Interfaces encadrants |

### 1.2 Tests pytest et front (pack cluster 4 + garde-fous)

| Fichier | Cluster | Objet principal | Nature |
|---------|---------|-----------------|--------|
| `apps/hugo/tests/test_session_memory_contract.py` | 1 | Contrat mémoire intra, absence verbatim | **RÉEL OBSERVÉ** |
| `apps/hugo/tests/test_cta_synthesis_contract.py` | 1 | CTA synthèse dans UIState | **RÉEL OBSERVÉ** |
| `apps/hugo/tests/test_cta_evaluation_contract.py` | 1 | CTA évaluation dans UIState | **RÉEL OBSERVÉ** |
| `apps/hugo/tests/test_p0_non_regression.py` | 1 | UIState sans champs P0 | **RÉEL OBSERVÉ** |
| `apps/hugo/tests/test_p0_v17_flow.py` | 1 | `memory_scope` gouverné (référencé note lot 1) | **RÉEL OBSERVÉ** |
| `apps/hugo/tests/test_conversation_progress.py` | 1 | Progression + endpoint UIState | **RÉEL OBSERVÉ** |
| `apps/hugo/tests/test_request_evaluation_guard.py` | 1 / 3 | Garde évaluation (INV-03, réf. cluster 3) | **RÉEL OBSERVÉ** |
| `apps/hugo/tests/test_cluster3_oracles.py` | 3 | INV-01, A1-04, B1-01, G3-01, D1-02 | **RÉEL OBSERVÉ** |
| `apps/hugo/tests/test_cluster4_surface_contracts.py` | 4 | `conversation_mode`, `learner_display_profile`, cascade groupe | **RÉEL OBSERVÉ** |
| `frontend_1.8/src/utils/engagementUiModel.test.js` | 4 | Presets affichage, CTA backend-driven | **RÉEL OBSERVÉ** |

**Statut d’exécution local (2026-06-16, runtime Postgres 17 + venv + Node 26) :**

- Pack backend garde-fous : **24/24 passés**
- `test_cluster4_surface_contracts.py` seul : **11/11 passés**
- `engagementUiModel.test.js` : **6/6 passés**
- Pas de test composant dédié `ConversationModeBanner` : **ÉCART CONFIRMÉ** (couverture front partielle)

---

## 2. Ce qui a bien fonctionné — cluster par cluster

### 2.1 Cluster 1 — Socle P0, progression, UIState, CTA, mémoire intra-conversation

**Objectif réellement poursuivi :** stabiliser le socle produit local sans refondre le moteur — mémoire **intra-conversation** bornée, CTA synthèse/évaluation standardisés côté backend, UIState comme surface unique, P0 gardé hors front prod.

**Ce qui a marché :**

- **Réduction de périmètre explicite** (plan CTO + note lot 1) : mémoire inter-sessions doctrinale mais hors implémentation tour courant → a évité un refactor `LearnerThemeMemory` prématuré.
- **Backend-first** : les CTA et la progression sont calculés côté `ui_state_builder` / `cta_ui_state`, consommés par le front via `engagementUiModel.js` sans recalcul local d’éligibilité.
- **Contrats testables** : `test_cta_*`, `test_session_memory_contract.py`, `test_p0_non_regression.py` ancrent des invariants réutilisés ensuite en clusters 3 et 4.
- **Séparation engagement vs affichage** posée tôt dans la doc (même si le front a mis du temps à la respecter).

**Exemples concrets :**

1. **INV-01 / non-exposition P0** — `test_p0_non_regression.py` + garde-fous cluster 3 : UIState prod sans `turn_state` / champs P0.
2. **CTA backend-driven (INV-03)** — blocs `cta_synthesis` / `cta_evaluation` testés ; le front ne fait que projeter `button_label` / `button_disabled`.
3. **Mémoire sans verbatim (A1-05)** — `test_session_memory_contract.py` vérifie `memory_scope: intra_conversation` et l’absence de contenu verbatim dans le contrat.

---

### 2.2 Cluster 2 — Matrice runtime vs cible 2.0

**Objectif réellement poursuivi :** produire une **cartographie exploitable** entre noms doctrinaux 2.0 et réel local (domaines 10, 20, 30, 70, 80, 90, 100, 110), avec statuts documentaires et actions, puis en déduire des oracles par persona.

**Ce qui a marché :**

- **Taxonomie des statuts** (`IMPLÉMENTÉ`, `ABSENT_NOUVEAU_CONTRAT`, `A_VÉRIFIER`, etc.) — lisible par un CTO sans lire tout le code.
- **Matrice + oracles + prompts d’audit** — chaîne doc → critères de test → fichiers pytest ciblés.
- **Identification honnête des doubles stacks** (ex. `build_ui_state` engagement vs `build_contract_ui_state` produit) — réduit les fausses convergences.
- **Séparation des surfaces** (état produit, export métier, debug technique, artefact LLM D9bis) — évite de vendre du debug comme du produit.

**Exemples concrets :**

1. **Domaine 90** — doctrine confidentialité claire avant le patch code B1-01 ; la matrice a servi de checklist au cluster 3.
2. **Oracles INV-07 / INV-08 / DSP-04** — définis dans `cluster2_oracles_test_par_persona.md` avant l’implémentation cluster 4 ; ont guidé les tests sans ambiguïté.
3. **D2-M01 / D2-M08** — identifiés comme `ABSENT_NOUVEAU_CONTRAT` dans la matrice V1, ce qui a légitimé le cluster 4 sans confondre cible et livré.

---

### 2.3 Cluster 3 court — Validation opérationnelle légère

**Objectif réellement poursuivi :** exécuter une **validation automatisée** sur 8 oracles prioritaires (personae A1, B1, D1) sans ouvrir D9bis, profils d’affichage ou prod Encoors.

**Ce qui a marché :**

- **Périmètre court et fermable** — 8 oracles, smoke `test_cluster3_oracles.py`, clôture explicite dans `cluster3_validation_courte_personae.md`.
- **Correction ciblée B1-01** — fuite `first_learner_message` quand `share_verbatim=false` ; patch `views_dashboard.py` + test dédié.
- **Réutilisation des tests cluster 1** — INV-03, INV-06, A1-05 couverts par fichiers préexistants, pas tout réécrit.
- **Séquence logique** — validation confidentialité / multi-tenant avant d’enrichir la surface UIState (cluster 4).

**Exemples concrets :**

1. **B1-01** — écart doc 90 déjà connu → test oracle → patch minimal → doc `ecarts — 90/110` mise à jour.
2. **G3-01** — isolation inter-org testée avant d’élargir les exports.
3. **8/8 verts** — critère de « cycle fermé » utilisable en CI locale.

---

### 2.4 Cluster 4 — Contrats surface UIState + front A1

**Objectif réellement poursuivi :** exposer `conversation_mode` et `learner_display_profile` dans **un seul contrat UIState**, les tester, puis les consommer côté parcours apprenant A1 avec persistance groupe/org — sans toucher P0, D9bis ni EvaluationTrace.

**Ce qui a marché :**

- **Contrat minimal additive** — enrichissement UIState sans casser CTA / progression / tests cluster 1.
- **Séparation INV-08** — `gamification_profile` (A/B/C) distinct de `learner_display_profile` (youth/adult/professional) côté API et front.
- **Couche `displayProfilePresets.js`** — un JSON UIState, rendu variable (DSP-04).
- **Résolution cascade** — query param > groupe > organisation > défaut `professional`.
- **Pack de non-régression** — 24 tests backend + 6 tests front verts sur runtime local actuel.

**Exemples concrets :**

1. **`conversation_mode`** dérivé de `ConversationProgress.posture`, pas de `session.current_phase` — suppression de `phaseLabel` parallèle dans `ProdLearnerWorkspace.vue`.
2. **`test_cluster4_surface_contracts.py`** — cas groupe, override query param, non-fuite P0.
3. **Bandeau lecture seule** — `ConversationModeBanner.vue` + badges header « Style » vs « Engagement ».

---

## 3. Ce qui n’a pas été comme prévu

### 3.1 Cluster 1

| Dérive | Type | Détail | Visible quand ? |
|--------|------|--------|-----------------|
| Mélange intra / inter sur `memory-summary` | **Code + doc** | **RÉEL OBSERVÉ** : endpoint exposait `LearnerThemeMemory` (inter) alors que le lot visait l’intra ; nom trompeur. Note lot 1 §2.3. | Dès l’audit note lot 1 ; **ÉCART CONFIRMÉ** avant contrat `SessionMemoryContract` |
| `build_session_memory` cross-sessions | **Code** | Agrégation messages hors `session_id` ; fuite inter-session dans un service « fil courant ». | Audit note lot 1 §2.1 |
| Tests mémoire tardifs | **Tests** | Pas de `test_session_memory.py` au départ ; contrat arrivé après la doc d’écarts. | Note lot 1 §2.5 |
| Double builder UIState | **Code + doc** | `build_ui_state` (orchestrateur) vs `build_contract_ui_state` (endpoint prod) — risque de divergence. | Matrice cluster 2 §1.5 |
| P0 encore dans réponse message | **Code** | `turn_state` complet exposé au client sur le flux message. | Note lot 1 §2.4 — **ÉCART CONFIRMÉ** partiel |

### 3.2 Cluster 2

| Dérive | Type | Détail | Visible quand ? |
|--------|------|--------|-----------------|
| Matrice V1 avec champs C4 encore « ABSENT » | **Doc** | `conversation_mode` / profils d’affichage en `ABSENT_NOUVEAU_CONTRAT` alors que oracles INV-07/08 déjà rédigés — nécessité matrice V2 post-C4. | Matrice cluster 2 avant mise à jour juin 2026 |
| Complexité documentaire | **Méthode** | Overlap matrice ↔ `ecarts — NN` ↔ oracles ↔ synthèse courte — 4 entrées pour un même fait. | Dès production cluster 2 |
| Oracles `[CIBLE]` comptés comme succès potentiels | **Méthode** | Légende oracles : N/A si capacité absente — discipline nécessaire pour ne pas sur-vendre. | `cluster2_oracles_test_par_persona.md` |
| D9bis / EvaluationTrace sur-documentés en cible, peu en tests | **Doc** | Présents en matrice comme `ABSENT_NOUVEAU_CONTRAT` sans backlog CODE court associé. | Domaines 70, 100 |

### 3.3 Cluster 3 court

| Dérive | Type | Détail | Visible quand ? |
|--------|------|--------|-----------------|
| B1-01 corrigé en C3, pas en C1/C2 | **Séquencement** | Doctrine confidentialité claire dans `ecarts — 90` avant le patch ; code traînait jusqu’au test persona B1. | Écarts 90 avant cluster 3 |
| 8 oracles / 5 tests dans `test_cluster3_oracles.py` | **Tests** | INV-03, INV-06, A1-05 validés via **autres fichiers** — lisible mais dispersé. | Rapport cluster 3 |
| Test legacy `p0_debug` vs `pilotage` | **Code + tests** | Échec hors périmètre 8 oracles ; bruit dans batterie élargie. | Batterie 26 tests cluster 3 |
| Hors scope C4 déclaré après C3 | **Cadre** | Cluster 3 exclut explicitement `conversation_mode` — alors que matrice les listait comme prochain move. | `cluster3_validation_courte_personae.md` §7 |

### 3.4 Cluster 4

| Dérive | Type | Détail | Visible quand ? |
|--------|------|--------|-----------------|
| Contrat API avant front (délai) | **Séquencement** | INV-07/08 verts en API avant exploitation front — fenêtre où la matrice disait « livré » côté backend seulement. | `cluster4_surface_contracts.md` vs design front |
| Persistance profil après contrat query-only | **Séquencement** | DSP-05/06 en CIBLE dans matrice ; persistance groupe/org livrée dans le même lot front, pas en micro-lot API seul. | Design cluster 4 front |
| Pas de test composant bandeau | **Tests** | A1-08 (UI) partiellement couvert par tests unitaires modèle, pas par test Vue. | Audit tests front juin 2026 |
| Compteurs doc obsolètes | **Doc** | `cluster4_surface_contracts.md` indique 9/9 et 22/22 ; **RÉEL OBSERVÉ** local : 11 et 24. | Après ajout tests cascade groupe |
| Grammaires adult/professional peu différenciées | **Produit** | **CIBLE** partielle — seul `youth` réellement travaillé (choix assumé). | Design cluster 4 front §1.2 |

---

## 4. Erreurs structurantes à ne pas reproduire

| # | Erreur / fragilité | Visible dès | Aurait fallu | Impact |
|---|-------------------|-------------|--------------|--------|
| 1 | **Mélange mémoire intra / inter** sur `memory-summary` et dans `build_session_memory` | Note lot 1 / écarts 20 | Renommer ou scinder l’endpoint **avant** cluster 2 ; test contrat mémoire en **premier** lot CODE | Confiance mémoire, risque fuite sémantique, retards tests A1-05 |
| 2 | **`conversation_mode` / profils d’affichage absents d’UIState** alors que matrice et oracles les posaient comme prérequis produit | Matrice cluster 2 §1.4–1.5 | Livrer contrats d’état **juste après** CTA (ordre plan CTO : mémoire → CTA → **états produit manquants**) | Front a imité `current_phase` ; dette INV-07 |
| 3 | **B1-01 corrigé tard** malgré écarts 90 explicites | Écarts 90 | Test permission tuteur + patch **dans le lot confidentialité**, pas après matrice complète | 1 cycle cluster 3 dédié à un écart déjà documenté |
| 4 | **Écarts 90/110 non répercutés immédiatement** après patch code | Cluster 3 | Règle : **aucun merge sans mise à jour** du fichier `ecarts — NN` concerné | Doc et code désalignés temporairement |
| 5 | **Sur-documentation transverse vs sous-documentation exécutable** | Cluster 2 | Une **fiche contrat** courte par champ UIState (schema + test + consommateur front) | CTO doit lire 300+ lignes de matrice pour un champ |
| 6 | **Double stack UIState** peu gouvernée | Audit moteur / matrice | Décision unique : quel builder fait foi pour `/ui-state/` ; l’autre marqué legacy | Risque divergence engagement / produit |
| 7 | **Oracles répartis sur plusieurs fichiers** sans index unique | Cluster 3 | Fichier `test_oracles_smoke.py` ou tableau CI « oracle → test » versionné | Onboarding et CI moins lisibles |
| 8 | **D9bis / EvaluationTrace en cible** sans garde-fou « ne pas ouvrir avant surface prod stable » | Matrice domaines 70/100 | Branche terminale **explicitement en étape 5** du plan replay | Tentation d’ouvrir trop tôt |
| 9 | **Compteurs et statuts doc non tenus à jour** après ajout de tests | Cluster 4 | Mise à jour systématique des docs `clusterN_*` dans le même PR que les tests | Fausse lecture « 9/9 » pour un CTO |
| 10 | **Front badge « Profil » = gamification** malgré INV-08 dans oracles | Cluster 2 oracles | Dès cluster 4 API : **tâche front obligatoire** dans le même lot, pas design séparé | Confusion produit jusqu’au patch A1 |

---

## 5. Replay propre pour le CTO

### 5.1 Scénario A — Reprise après cluster 1

**Point d’ancrage :** mémoire intra + CTA + UIState de base livrés ; matrice cluster 2 **pas encore** produite.

#### Garder tel quel

- Note lot 1 mémoire et plan CTO (`plan_documentation_cto_convergence_hugo.md`).
- Tests : `test_session_memory_contract.py`, `test_cta_*`, `test_p0_non_regression.py`, `test_conversation_progress.py` (contrat UIState).
- Réduction périmètre inter-sessions (doctrine, pas injection orchestrateur).

#### Refaire / re-séquencer

1. **Avant toute matrice large** : corriger `memory-summary` (scinder intra vs inter ou renommer) + test B1-01 / confidentialité tuteur.
2. **Immédiatement après CTA** : contrats `conversation_mode` + `learner_display_profile` (cluster 4 API) — pas attendre cluster 3.
3. **Matrice cluster 2** : produire une **V1 courte** (20 lignes critiques) puis enrichir, au lieu d’une matrice complète avant les patches CODE prioritaires.

#### Renforcer

- Fiche par champ UIState (JSON, producteur, test, fichier front consommateur).
- CI smoke unique : mémoire + CTA + P0 + 3 oracles confidentialité.

#### Simplifier / jeter

- Doublons entre note lot 1 et écarts 20 avant alignement.
- Prompts d’audit cluster 2 tant que les 5 écarts CODE P0 ne sont pas verts.

#### Mini-plan (5 étapes)

| Étape | Contenu |
|-------|---------|
| 1 | Stabiliser mémoire intra (`SessionMemoryContract`), scinder `memory-summary`, tests verbatim + scope |
| 2 | CTA + garde confidentialité (B1-01, G3-01) + `test_cluster3_oracles` minimal |
| 3 | Contrats UIState manquants : `conversation_mode`, `learner_display_profile` + tests cluster 4 |
| 4 | Matrice runtime vs cible **alignée sur le réel déjà vert** + oracles persona |
| 5 | Front A1 (presets + bandeau) ; D9bis / EvaluationTrace **interdits** avant étape 4 verte |

---

### 5.2 Scénario B — Reprise après cluster 2

**Point d’ancrage :** matrice + oracles persona livrés ; cluster 3 et 4 **pas encore** exécutés.

#### Garder tel quel

- `cluster2_matrice_runtime_vs_cible.md` (base de vérité doc).
- `cluster2_oracles_test_par_persona.md` (catalogue INV / DSP / A1).
- Hiérarchie documentaire et méthodo révisée.

#### Refaire / re-séquencer

1. **Cluster 3 = exécution oracles CODE**, pas un nouveau document — priorité B1-01, INV-01, G3-01.
2. **Cluster 4 = API + front A1 dans le même lot** — pas de doc « surface contracts » sans PR front.
3. Mettre à jour la matrice **dans le même temps** que chaque champ passe de `ABSENT` à `IMPLÉMENTÉ`.

#### Renforcer

- Tableau « oracle → fichier pytest → statut » dans `Cluster 2 — Oracles… validation courte.md`.
- Test composant minimal pour A1-08 (bandeau mode).

#### Simplifier / jeter

- `cluster2_prompts_audit_runtime_et_memoire.md` comme livrable bloquant si les tests pytest couvrent déjà le même terrain.
- Relances documentaires sur D9bis tant que DSP-01..04 ne sont pas verts.

#### Mini-plan (5 étapes)

| Étape | Contenu |
|-------|---------|
| 1 | Exécuter pack confidentialité + P0 (cluster 3 court) — **zéro nouveau doc** |
| 2 | Implémenter D2-M01 + D2-M08 (API) + `test_cluster4_surface_contracts.py` |
| 3 | Front : `displayProfilePresets` + `ConversationModeBanner` + tests engagement |
| 4 | Persistance `learner_display_profile` groupe/org + admin groupe |
| 5 | Matrice V2 + fermeture cycle ; ouvrir D9bis / D2-M05 seulement si étapes 1–4 vertes en CI |

---

## 6. Synthèse transversale

### Bilan par cluster

| Cluster | Bilan | Verdict |
|---------|-------|---------|
| 1 | Socle utile, dette mémoire / double UIState | **Fondation à garder**, avec 2 corrections structurelles (memory-summary, message P0) |
| 2 | Excellente cartographie, lourdeur doc | **Garder la matrice**, alléger les doublons |
| 3 | Validation efficace, B1-01 tardif | **Garder la méthode « court »**, déplacer les oracles sécurité plus tôt |
| 4 | Bon livrable additive, doc/compteurs à jour | **Prêt local** sur contrats + front A1 ; adult/pro/DSP-05 formateur **A_VÉRIFIER** |

### État actuel (RÉEL OBSERVÉ local)

- Pack garde-fous backend : **24/24**
- Cluster 4 surface : **11/11**
- Front `engagementUiModel` : **6/6**
- Prod Encoors, RLS Postgres, parcours tuteur UI bout-en-bout : **A_VÉRIFIER**

---

## 7. Message pour CTO — enseignements clusters 1–4 et recommandations

### Enseignements positifs

1. **Réduction de périmètre** (mémoire intra seulement, pas de refonte moteur) a permis d’avancer sans casser le POC local.
2. **Backend-first + UIState unique** : les clusters 1 et 4 montrent qu’on peut enrichir le produit de façon additive et testable.
3. **Matrice cluster 2 + oracles** : bon outil de pilotage — à condition de la tenir alignée avec le code après chaque lot.
4. **Cluster 3 court** : format « 8 oracles / smoke pytest » fermable et reproductible — à généraliser en CI.
5. **Séparation gamification / profil d’affichage** : décision claire, enfin reflétée côté front (INV-08).

### Fragilités structurantes

1. **Écarts documentés tôt, code corrigé tard** (B1-01, `conversation_mode`, memory-summary).
2. **Multiplication des documents** pour un même fait (matrice, écarts, cluster N, synthèse courte).
3. **Couverture front inégale** (modèle JS testé, composants Vue non testés).
4. **Branches terminales (D9bis, EvaluationTrace)** toujours en CIBLE — risque d’ouverture prématurée si on ne verrouille pas d’abord la surface apprenant.
5. **Runtime prod / RLS** non tranchés — toute démo CTO doit rester étiquetée local vs Encoors.

### Faut-il repartir plus tôt ou continuer ?

**HYPOTHÈSE recommandée : continuer depuis l’état actuel**, sans rewind code, **à condition** d’appliquer les garde-fous du replay (CI smoke 24+6, mise à jour doc synchrone, pas d’ouverture D9bis avant fermeture DSP/formateur).

Un **rewind documentaire** (pas un rewind code) au point **« après cluster 2 »** suffirait si l’équipe veut simplifier : archiver les doublons, ne garder qu’une matrice V2 + un fichier oracle→test.

Repartir **après cluster 1 uniquement** n’est rentable que si l’on doit **refondre la couche mémoire** (scission endpoints, injection prompt) — ce n’est pas nécessaire pour démontrer Hugo 2.0 en parcours A1 aujourd’hui.

### Trois risques majeurs si on continue en l’état sans garde-fous

1. **Réouverture moteur** (D9bis, EvaluationTrace) avant stabilisation complète des parcours encadrants et prod A_VÉRIFIER.
2. **Nouvelle dérive front** (logique parallèle type `phaseLabel`) sur les prochains champs UIState.
3. **Dette mémoire** (`memory-summary`, cross-session dans `build_session_memory`) qui resurfacerait en démo multi-sessions.

### Trois gains majeurs si on applique les apprentissages maintenant

1. **CI locale reproductible** (24 + 6 tests) comme barrière de merge sur tout lot surface produit.
2. **Un contrat = un test = un consommateur front** — fin des champs « livrés API » longtemps invisibles.
3. **Matrice tenue à jour** — le CTO lit un seul tableau pour savoir ce qui est démo-able vs CIBLE.

### Options pour le CTO

| Option | Description | Quand la choisir |
|--------|-------------|------------------|
| **Option 1 — Continuer** | État actuel + smoke CI 24/6 ; prochains lots : DSP-05 formateur, grammaires adult/pro, D9bis/D2-M05 en dernier | Démo A1 imminente, équipe petite |
| **Option 2 — Replay documentaire post-C2** | Garder tout le code ; refondre la doc en 3 fichiers (matrice V2, oracle→test, retex) ; exécuter checklist confidentialité avant tout nouveau champ UIState | Équipe qui reprend le pilotage, onboarding |
| **Option 3 — Hybride (recommandée)** | **Conserver** code clusters 3–4 et tests ; **refaire** synchro doc/compteurs + test composant A1-08 ; **repousser** D9bis/EvaluationTrace ; **corriger** memory-summary dans un micro-lot dédié avant multi-session | Équilibre vitesse / propreté |

---

## 8. Prochaine sortie utile (HYPOTHÈSE)

1. Mettre à jour `cluster4_surface_contracts.md` (compteurs 11/24, persistance groupe livrée).
2. Ajouter une ligne CI documentée dans `Cluster 2 — Oracles… validation courte.md` (commande unique 24+6).
3. Micro-lot **mémoire** : scinder ou renommer `memory-summary` + test d’intégration — sans toucher P0.

---

**Références internes :** `00_HIERARCHIE_DOCUMENTAIRE.md` · `DOC_METHODO_REFERENCE_CONVERGENCE_HUGO_REVISE.md` · `plan_documentation_cto_convergence_hugo.md` · `cluster2_matrice_runtime_vs_cible.md` · `cluster3_validation_courte_personae.md` · `cluster4_surface_contracts.md` · `cluster4_front_A1_learner_display_profile_conversation_mode.md`
