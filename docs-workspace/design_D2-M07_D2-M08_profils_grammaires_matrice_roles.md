# Design D2‑M07 + D2‑M08 — 3 grammaires apprenant & matrice rôles / confidentialité

**Workspace :** `/Users/machin/Desktop/Zone de travail Hugo`  
**Date :** 2026-06-18  
**Lots :** D2‑M07 (domaine 90) · D2‑M08 (domaine 110)  
**Méthode :** backend-first, contrat UIState unique, oracles comme preuve avant promotion doc

---

## Sources mobilisées

| Source | Usage |
|--------|--------|
| `cluster2_matrice_runtime_vs_cible.md` | §6 (90), §8 (110), backlog D2‑M07 / D2‑M08 |
| `cluster2_oracles_test_par_persona.md` | DSP, INV, A1, B1, D1, G3, F1 |
| `cluster3_validation_courte_personae.md` | B1‑01 patch, 8/8 oracles cluster 3 |
| `cluster4_surface_contracts.md` | Contrats `conversation_mode` + `learner_display_profile` |
| `cluster4_front_A1_learner_display_profile_conversation_mode.md` | Implémentation partielle front + persistance groupe/org |
| `ecarts — 90_confidentialite_partage_multitenant_roles.md` | CONF‑07, matrice tuteur post C3 |
| `ecarts — 110_interfaces_formateur_tuteur.md` | IFT‑041/042, timeline B1‑01 |
| `specs interface 2.0.md` | § profils d’affichage (3 grammaires, UIState unique) |
| Code `hugo_back` | `ui_state_builder.py`, `views_dashboard.py`, `test_cluster3_oracles.py`, `test_cluster4_surface_contracts.py` |
| Code `hugo-hugolucia/frontend_1.8` | `engagementUiModel.js`, `displayProfilePresets.js`, `ProdLearnerWorkspace.vue`, `ConversationModeBanner.vue` |

---

## Synthèse exécutive

| Volet | Réel local | Cible lot | Reste après lot |
|-------|------------|-----------|-----------------|
| **D2‑M08 — contrat backend** | **IMPLÉMENTÉ** — enum, query param, cascade groupe/org | Verrouillé | Skins cosmétiques |
| **D2‑M08 — rendu 3 grammaires front** | **PARTIEL** — socle livré (youth), adult/professional peu différenciés | 3 grammaires sécurisées + tests | Sélecteur posture UI (G2‑02) |
| **D2‑M07 — B1‑01 timeline** | **IMPLÉMENTÉ** — patch `views_dashboard.py` | Ne pas rouvrir | — |
| **D2‑M07 — matrice rôles doc** | Amorcée §6.2 matrice cluster 2 | Matrice complète + décisions | RLS prod, COORDO |
| **D2‑M07 — pack pytest confidentialité** | 5 oracles dans `test_cluster3_oracles.py` | Pack dédié 8+ oracles | Prod Encoors |

**Décision de convergence :** considérer **livré** le contrat backend + persistance groupe/org + socle front (modèle d’engagement, bandeau mode, presets youth). Considérer **CIBLE** le sélecteur posture interactif, les skins, la configuration profil par formateur sans admin groupe, et toute preuve RLS Postgres prod.

---

# A — Profils d’affichage : 3 grammaires apprenant (D2‑M08)

## A.1 Réel confirmé

### Backend (IMPLÉMENTÉ)

- `GET /hugo/sessions/{id}/ui-state/` expose `conversation_mode` et `learner_display_profile`.
- Résolution : `query param` > `Group.learner_display_profile` > `Organisation.default_learner_display_profile` > `professional` (`resolve_learner_display_profile_for_session` dans `ui_state_builder.py`).
- Même paramètre sur `request-synthesis` / `request-evaluation`.
- Preuve : `test_cluster4_surface_contracts.py` (11 tests incl. cascade groupe / override).

### Front (PARTIEL — socle en place)

| Fichier | Rôle | Statut |
|---------|------|--------|
| `displayProfilePresets.js` | Presets youth / adult / professional | **IMPLÉMENTÉ** |
| `engagementUiModel.js` | Fusion preset × gamification ; `conversationMode` | **IMPLÉMENTÉ** |
| `ConversationModeBanner.vue` | Pill `conversation_mode.label` + `switch_warning` | **IMPLÉMENTÉ** |
| `ProdLearnerWorkspace.vue` | Classe `prod-workspace--{profile}`, badges, query ui-state | **IMPLÉMENTÉ** |
| `HugoProgressPanel.vue` | Rail scène, CTA backend-driven | **IMPLÉMENTÉ** (rendu piloté par modèle) |
| `GroupAdminDetailView.vue` | PATCH `learner_display_profile` sur groupe | **IMPLÉMENTÉ** (DSP‑06 partiel ORGADMIN) |
| `style.css` | Tokens `.prod-workspace--youth` uniquement | **PARTIEL** |

### Oracles — état actuel

| Oracle | Attente | Statut local |
|--------|---------|--------------|
| DSP‑01 | `youth` — interface graphique, texte réduit | Contrat API **OK** ; rendu UI **PARTIEL** |
| DSP‑02 | `adult` — équilibre texte/visuel | Contrat API **OK** ; rendu UI **CIBLE** |
| DSP‑03 | `professional` — texte explicite (défaut) | **OK** (≈ UX historique) |
| DSP‑04 | Même UIState JSON, rendu seul varie | API **OK** ; front à prouver par tests clés métier identiques |
| DSP‑05 | Formateur choisit profil cohorte | **CIBLE** (pas de surface formateur dédiée) |
| DSP‑06 | ORGADMIN choisit profil org/groupe | **PARTIEL** — PATCH groupe livré ; défaut org sans UI admin dédiée |
| DSP‑07 | CTA éligibilité identique entre profils | API **OK** ; test front **PARTIEL** |
| INV‑07 | `conversation_mode` dans UIState | API **OK** ; bandeau **OK** |
| INV‑08 | Profil affichage ≠ `gamification_profile` | API **OK** ; badges « Style » vs « Engagement » **OK** |
| A1‑08 | Label posture visible (`conversation_mode.label`) | API **OK** ; bandeau **OK** ; sélecteur **CIBLE** |
| G2‑02 | Sélecteur posture UI | **CIBLE** (hors lot immédiat) |

## A.2 Design des 3 grammaires

### Principe invariant (DSP‑04)

Un seul contrat `UIState` pour A1/A2/A3. Le front **ne recalcule jamais** :

- éligibilité CTA (`cta_synthesis`, `cta_evaluation`) ;
- posture (`conversation_mode` vient du backend) ;
- progression (`scene_*`, `quest_*`, `maturity_color`).

La grammaire ne modifie que : **densité texte**, **visibilité de badges**, **hints du rail**, **tokens CSS**, **copy d’aide** — jamais les labels CTA (`cta_*.ui.button_label`).

### Matrice de rendu par persona

| Dimension | `youth` (A1, 16–20) | `adult` (A2, reconversion) | `professional` (A3, ingénieur) |
|-----------|---------------------|----------------------------|-------------------------------|
| **Densité texte** | Phrases courtes, tutoiement | Phrases moyennes, registre neutre | Texte explicite, repères conceptuels |
| **Rail scène** | Icônes + numéros, hints simplifiés | Icônes modérées, hints standards | Rail sobre, hints backend ou génériques |
| **Badge maturité** | Masqué (`showMaturityBadge: false`) | Visible | Visible (selon gamification) |
| **Barre progression** | Large, toujours visible | Visible | Pilotée par `gamification_profile` si null |
| **Bandeau `conversation_mode`** | Pill visible, libellé backend tel quel | Idem | Idem |
| **`switch_warning`** | Alerte warning non bloquante | Idem | Idem |
| **Header badges** | « Style : Jeune » distinct de « Engagement : … » | Idem | « Style : Standard » |
| **Copy panneaux** | `progressPanelIntro` court | Intro standard | Intro actuelle (référence produit) |
| **CTA** | Labels + `helper_text` **backend uniquement** | Idem | Idem |

### Fusion preset × gamification (INV‑08)

```
presentation = merge(displayProfilePresets[learner_display_profile], GAMIFICATION_PROFILES[gamification_profile])
```

Règle : pour chaque flag `show*`, si le preset vaut `null`, le cosmétique gamification décide ; sinon le preset **borne** (gamification ne peut pas réactiver ce que le profil d’affichage masque — ex. maturité en youth).

### Bandeau `conversation_mode` (A1‑08, G2‑02)

| Profil | Visibilité | Comportement |
|--------|------------|--------------|
| youth / adult / professional | **Toujours** si `conversation_mode.label` présent | Afficher `label` sans retraduction locale |
| `switch_warning` | Tous profils | Alerte au-dessus du composer (déjà dans `ConversationModeBanner`) |
| `can_switch` | Tous profils | **Lecture seule** ce lot — pas d’appel `POST set-posture` (G2‑02 CIBLE) |

### Copy contextualisée (à ajouter — rendu seul)

Fichier cible : `displayProfileCopy.js` (ou extension de `displayProfilePresets.js`)

| Zone | youth | adult | professional |
|------|-------|-------|--------------|
| Sous-titre session header | 1 phrase courte | 2 phrases | Texte actuel |
| Placeholder composer | Inchangé (déjà adaptatif questions) | Idem | Idem |
| Légende objectif actif | « Ce que tu dois faire maintenant » | « Objectif en cours » | Texte actuel « Affiché tel quel depuis le contrat » |

**Interdit :** reformuler `active_quest_label` ou `cta_*.helper_text` côté front.

## A.3 Écarts confirmés / A_VERIFIER (D2‑M08)

| ID | Écart | Statut | Action |
|----|-------|--------|--------|
| DSP‑02 UI | Preset `adult` peu visible vs `professional` | ÉCART | Enrichir preset + CSS `.prod-workspace--adult` |
| DSP‑04 preuve front | Pas de test « clés métier identiques » sur 3 profils | ÉCART | Étendre `engagementUiModel.test.js` |
| DSP‑05 | Formateur sans surface dédiée | CIBLE | Hors lot — documenter seulement |
| G2‑02 | Sélecteur posture | CIBLE | Sprint ultérieur |
| Prod Encoors | Parité UIState / rendu | A_VERIFIER | Fiche runtime prod |

## A.4 Plan de patch front + tests (D2‑M08)

### Fichiers — ordre d’exécution

| # | Fichier | Modification |
|---|---------|--------------|
| 1 | `src/utils/displayProfilePresets.js` | Enrichir preset `adult` (hints, `compactCopy: false`, maturité visible) ; documenter invariant DSP‑04 en tête de fichier |
| 2 | `src/utils/displayProfileCopy.js` | **Créer** — copy header / légendes par profil (rendu seul) |
| 3 | `src/utils/engagementUiModel.js` | Exposer `headerCopy`, `sectionCopy` depuis copy layer ; aucune logique métier ajoutée |
| 4 | `src/utils/displayProfilePresets.test.js` | **Créer** — normalisation enum, presets complets |
| 5 | `src/utils/engagementUiModel.test.js` | Ajouter cas `adult`, `professional`, INV‑08 explicite, DSP‑04 (mêmes clés CTA), A1‑08 |
| 6 | `src/components/learner/ProdLearnerWorkspace.vue` | Consommer `headerCopy` ; masquer badge « Style » en `professional` si redondant (option UX) |
| 7 | `src/style.css` | Tokens `.prod-workspace--adult`, `.prod-workspace--professional` (espacement, typo) |
| 8 | `src/components/learner/HugoProgressPanel.vue` | Classe racine `prod-panel--{learnerDisplayProfile}` pour ciblage CSS |
| 9 | `src/components/learner/ConversationModeBanner.test.js` | **Créer** (optionnel) — rendu label + warning |

**Ne pas modifier :** logique CTA, fetch ui-state (déjà conforme), `frontendConfig.gamification_profile` (orthogonal).

### Tests front cibles (`npm test`)

```bash
cd hugo-hugolucia/frontend_1.8
npm test -- src/utils/displayProfilePresets.test.js src/utils/engagementUiModel.test.js
```

| Test | Oracle |
|------|--------|
| `youth` → `compactCopy`, pas maturité, hints courts | DSP‑01 |
| `adult` → maturité visible, hints ≠ youth | DSP‑02 |
| `professional` → défaut, `showStepIcons: false` | DSP‑03 |
| Mêmes `synthesisButton` / `evaluationButton` sur 3 profils | DSP‑04, DSP‑07 |
| `gamification_profile` change thème, pas `learnerDisplayProfile` | INV‑08 |
| `conversationMode.label` propagé | INV‑07, A1‑08 |

---

# B — Matrice rôles / confidentialité (D2‑M07)

## B.1 Réel confirmé

- Doctrine confidentialité-first alignée avec le code local (UIState filtré, pas de P0 en `/app`).
- **B1‑01 corrigé** : timeline tuteur vide (`messages[]` + `first_learner_message`) si `share_verbatim=false`.
- Sous partage : résumé **`pilotage`** agrégé — pas de `turn_state` brut dans la réponse timeline (`views_dashboard.py`).
- **Écart test legacy** : `test_tutor_access_control.py::test_dashboard_timeline_includes_p0_debug_without_prompt_leak` attend encore `p0_debug` alors que le code expose `pilotage` (oracle B1‑02 à recaler).
- Evidence bundle filtré par `organisation_id` (D1‑02 / G3‑02).
- Pas de route `export-md` dans le backend local (G3‑03 / D1‑04 satisfaits par absence).
- Pas de modèle `ConversationTurnLLMAnalysis` (D1‑06 / F1‑02 / G3‑04).
- RLS Postgres prod : **A_VERIFIER** (tests SQLite).

## B.2 Matrice rôles × visibilité (mise à jour)

Légende : **V** = visible selon contrat · **P** = partage explicite requis · **—** = non accessible · **T** = surface technique (testeur/superadmin)

### Surfaces apprenant

| Donnée / surface | LEARNER | TUTOR | TRAINER | ORGADMIN | SUPERADMIN |
|------------------|---------|-------|---------|----------|------------|
| `GET .../ui-state/` (sa session) | **V** | — | — | — | T |
| `conversation_mode` | **V** (UIState) | — | — | — | — |
| `learner_display_profile` | **V** (UIState) | — | — | Config groupe/org | Bornes plateforme CIBLE |
| Verbatim session (messages) | **V** (sa session) | **P** (`share_verbatim`) | **P** | — | T |
| P0 / TurnState brut | — | — | — | — | T (debug) |
| `memory-summary` | **V** (résumé gouverné) | — | — | — | T |
| CTA synthèse / éval | **V** (UIState) | — | — | — | — |
| `gamification_profile` | **V** (cosmétique) | — | — | — | — |

### Surfaces tuteur

| Donnée / surface | LEARNER | TUTOR | TRAINER | ORGADMIN | SUPERADMIN |
|------------------|---------|-------|---------|----------|------------|
| `GET .../timeline/` | — | **V** (apprenants liés) | — | — | T |
| `messages[]` verbatim | — | **P** | — | — | — |
| `first_learner_message` | — | **P** (B1‑01) | — | — | — |
| `pilotage` sur message | — | **P** (agrégat produit-safe) | — | — | — |
| `p0_debug` / `turn_state` brut | — | **—** (interdit B1‑02) | — | — | T |
| Traces session | — | **V** (métadonnées) | — | — | T |
| Validation trace `POST /traces/{id}/validate/` | — | **V** (lié) | — | — | — |

### Exports & bundles

| Donnée / surface | LEARNER | TUTOR | TRAINER | ORGADMIN | SUPERADMIN |
|------------------|---------|-------|---------|----------|------------|
| `EvidenceBundleView` ZIP | — | — | — | **V** (son tenant) | A_VERIFIER |
| `traces.json` contenu | — | — | — | Métadonnées traces tenant | A_VERIFIER richesse |
| `ExportRun` CSV/JSON | — | — | Partiel | **V** | T |
| `export-md` / debug P0 | — | — | — | **—** (D1‑04, G3‑03) | T CIBLE |
| ConversationTurnLLMAnalysis | — | — | — | **—** (D1‑06) | Export debug CIBLE |

### Configuration profils d’affichage

| Action | LEARNER | TUTOR | TRAINER | ORGADMIN | SUPERADMIN |
|--------|---------|-------|---------|----------|------------|
| Lire profil effectif | UIState | — | — | GET groupe | CIBLE |
| PATCH `Group.learner_display_profile` | — | — | A_VERIFIER | **V** (livré) | T |
| PATCH org `default_learner_display_profile` | — | — | — | API **PARTIEL** (pas UI) | CIBLE |

### Surfaces techniques (hors produit)

| Surface | Rôles | Note |
|---------|-------|------|
| `LearnerDetailView` + modales P0 | Testeur | Hors `/app` |
| `views_internal` / turn-review | Calibration | F1‑05 |
| Django admin global | Superadmin | ≠ lecture applicative libre |

## B.3 Alignement code vs matrice

| Point | Aligné | Patch nécessaire |
|-------|--------|------------------|
| B1‑01 verbatim timeline | **Oui** | — |
| B1‑02 pas P0 brut timeline | **Oui** (`pilotage`) | Mettre à jour test legacy `p0_debug` → `pilotage` |
| D1‑02 / G3‑02 bundle tenant | **Oui** | Ajouter test G3‑02 explicite (alias) |
| G3‑01 IDOR session | **Oui** | — |
| G3‑03 export-md ORGADMIN | **Oui** (404) | Test négatif route absente |
| D1‑06 / F1‑02 LLM analysis | **Oui** (absent) | Test grep / UIState négatif |
| F1‑03 lecture masse verbatim | **Partiel** | Test tuteur non lié + ORGADMIN |
| RLS Postgres | — | **A_VERIFIER** — hors lot |
| COORDO | — | **CIBLE** |

## B.4 Plan de patch backend + tests (D2‑M07)

### Fichiers — ordre d’exécution

| # | Fichier | Modification |
|---|---------|--------------|
| 1 | `apps/hugo/tests/test_tutor_access_control.py` | Renommer/recaler test `p0_debug` → assertions sur `pilotage` ; vérifier absence `turn_state`, `system_prompt` (B1‑02) |
| 2 | `apps/hugo/tests/test_d2_m07_confidentiality_oracles.py` | **Créer** — pack multi-rôles (voir §C) |
| 3 | `apps/hugo/views_dashboard.py` | **Aucun patch fonctionnel** B1‑01 déjà livré — documenter seulement |
| 4 | `apps/referentials/tests/test_group_display_profile.py` | **Créer** si absent — PATCH groupe cross-tenant, rôle ORGADMIN |
| 5 | `ecarts — 90_confidentialite_partage_multitenant_roles.md` | Intégrer matrice §B.2 (extrait) + référence pack pytest |

**Ne pas modifier :** RLS migrations, orchestrateur, P0 classifier.

---

# C — Plan d’exécution global & batteries de tests

## C.1 Séquencement conseillé

```
Phase 1 — Stabiliser preuves confidentialité (backend)
  └─ test_d2_m07_confidentiality_oracles.py + fix test_tutor_access_control (B1-02)

Phase 2 — Compléter 3 grammaires (front)
  └─ displayProfilePresets + copy + CSS adult + tests DSP/INV

Phase 3 — Documentation & promotion
  └─ Mettre à jour cluster2_matrice §8 (IFT-041 → PARTIEL rendu)
  └─ ecarts 90 §3.4 matrice complète
```

## C.2 Pack pytest « confidentialité multi-rôles »

**Fichier proposé :** `hugo_back/apps/hugo/tests/test_d2_m07_confidentiality_oracles.py`

```bash
cd hugo_back
.venv/bin/python -m pytest \
  apps/hugo/tests/test_d2_m07_confidentiality_oracles.py \
  apps/hugo/tests/test_cluster3_oracles.py \
  apps/hugo/tests/test_tutor_access_control.py \
  apps/hugo/tests/test_cluster4_surface_contracts.py \
  -q
```

| Test proposé | Oracle | Rôle | Assertion |
|--------------|--------|------|-----------|
| `test_b1_01_*` (existant) | B1‑01 | TUTOR | Pas verbatim si `share_verbatim=false` |
| `test_timeline_pilotage_not_p0_debug` | B1‑02 | TUTOR | `pilotage` présent ; pas `turn_state` / `p0_debug` |
| `test_d1_02_*` (existant) | D1‑02 | ORGADMIN | Bundle = traces tenant |
| `test_g3_02_bundle_excludes_other_org` | G3‑02 | ORGADMIN | Alias D1‑02 — 0 trace org B |
| `test_g3_01_*` (existant) | G3‑01 | LEARNER | 404 session autre org |
| `test_g3_03_orgadmin_no_export_md` | G3‑03 | ORGADMIN | 404 sur route debug inexistante |
| `test_d1_06_ui_state_no_llm_analysis` | D1‑06 | LEARNER | Pas clé LLM analysis dans ui-state |
| `test_f1_02_no_llm_analysis_in_api` | F1‑02 | SUPERADMIN | grep modèle / endpoint absent |
| `test_f1_03_tutor_unlinked_no_timeline` | F1‑03 | TUTOR | 403 timeline apprenant non lié |
| `test_inv01_*` (existant) | INV‑01 | LEARNER | UIState sans P0 |

## C.3 Pack front (`npm test`)

```bash
cd hugo-hugolucia/frontend_1.8
npm test -- \
  src/utils/displayProfilePresets.test.js \
  src/utils/engagementUiModel.test.js
```

| Test | Oracle |
|------|--------|
| Trois profils → mêmes labels CTA | DSP‑04, DSP‑07 |
| youth compact / no maturity | DSP‑01 |
| adult ≠ youth hints | DSP‑02 |
| professional défaut | DSP‑03 |
| gamification ≠ display profile | INV‑08 |
| conversationMode.label | INV‑07, A1‑08 |

## C.4 Batterie intégrée lot (validation de clôture)

```bash
# Backend
cd hugo_back && .venv/bin/python -m pytest \
  apps/hugo/tests/test_d2_m07_confidentiality_oracles.py \
  apps/hugo/tests/test_cluster3_oracles.py \
  apps/hugo/tests/test_cluster4_surface_contracts.py \
  apps/hugo/tests/test_tutor_access_control.py \
  apps/hugo/tests/test_p0_non_regression.py \
  apps/hugo/tests/test_cta_evaluation_contract.py \
  apps/hugo/tests/test_cta_synthesis_contract.py \
  -q

# Front
cd hugo-hugolucia/frontend_1.8 && npm test
```

## C.5 Décisions de convergence (récap)

| Élément | Décision |
|---------|----------|
| Contrat UIState + `conversation_mode` + `learner_display_profile` | **LIVRÉ** (backend) |
| Persistance profil groupe/org | **LIVRÉ** (backend + admin groupe) |
| Socle front 3 grammaires (modèle + bandeau + youth) | **LIVRÉ** (partiel) |
| Différenciation adult complète | **CIBLE** lot — patches §A.4 |
| Pack pytest confidentialité étendu | **CIBLE** lot — §C.2 |
| B1‑01 | **LIVRÉ** — ne pas rouvrir |
| B1‑02 test legacy | **ÉCART** — recaler sur `pilotage` |
| Sélecteur posture (G2‑02) | **CIBLE** — sprint ultérieur |
| DSP‑05 formateur | **CIBLE** |
| RLS prod / Encoors | **A_VERIFIER** |
| D9bis / LLM analysis | **HORS LOT** |

---

## Prochaine sortie utile

1. Implémenter les patches §A.4 et §B.4 dans l’ordre Phase 1 → 2.
2. Exécuter la batterie §C.4 et consigner les résultats dans `cluster2_oracles_test_par_persona.md` § validation D2‑M07/M08.
3. Mettre à jour `cluster2_matrice_runtime_vs_cible.md` : IFT‑041 (rendu PARTIEL → IMPLÉMENTÉ), D2‑M07 (matrice documentée), D2‑M08 (enum + rendu).

---

**Références :** `cluster4_front_A1_learner_display_profile_conversation_mode.md` · `mapping_EvaluationTrace_runtime_local.md` · `Retex_cluster_1-4.md`
