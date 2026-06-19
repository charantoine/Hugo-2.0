# Cluster 12 — UX apprenant & postures 2.0 (plan & cadrage)

> Date : 2026-06-18  
> Scope : domaine **31** (front apprenant), appui **10** (UIState/CTA) et **30** (RAG visible UI uniquement)  
> Garde-fou : `REFERENCE_CONVERGENCE_HUGO_REEL_VS_2_0_GARDEFOU.md`  
> Prérequis : runtime convergé clusters 1–11 — **aucune modification moteur** dans ce cluster

---

## 1. Introduction

Le cluster 12 porte le **front apprenant** au niveau « Hugo 2.0 lot courant » : sélecteur de posture (G2-02), trois grammaires d’affichage apprenant, et alignement minimal **CTA × posture × RAG** côté produit. Le moteur (P0, TurnState, mémoire, évaluation, exports) est considéré **verrouillé** ; seuls l’**exposition**, la **grammaire UX** et la **cohérence visuelle** des contrats backend existants sont concernés.

Le front apprenant doit continuer à consommer **uniquement** `UIState` et endpoints dérivés (`set-posture`, synthèse, évaluation, messages). Aucune logique de progression, d’éligibilité CTA ou de posture ne doit être recalculée localement.

**Sources mobilisées :** garde-fou §3.1/3.4, `specs interface 2.0.md`, `cluster2_matrice_runtime_vs_cible.md` (domaines 10/31), `ecarts — 31_front_apprenant_postures_et_bascule.md`, code `frontend_1.8` + tests cluster 4/5, `test_posture_modes.py`.

---

## 2. Cible 2.0 locale « lot courant » pour le domaine 31

### 2.1 Sélecteur de posture (G2-02)

- L’apprenant **voit** la posture active (`conversation_mode.label`) et, lorsque le backend autorise (`conversation_mode.can_switch === true`), peut **demander** un changement parmi les postures autorisées par `can_transition` :
  - `diagnostic` — Séance de diagnostic
  - `reflective_afest` — Entretien réflexif AFEST
  - `knowledge_review` — Révision / bâchage
- Action UI → `POST /hugo/sessions/{id}/set-posture/` body `{ "posture": "<code>" }` (réel observé ; spec interface mentionne PATCH — **écart documentaire D2-M03**, pas bloquant lot courant).
- États UI minimaux : **idle**, **pending**, **success** (rechargement `ui-state`), **refused** (`400 transition_not_allowed`), **error** (réseau).
- Affichage de `conversation_mode.switch_warning` si présent (déjà supporté par `ConversationModeBanner.vue`).
- **Interdit :** édition directe de P0, TurnState, prompts, ou contournement des règles `can_transition`.

### 2.2 Trois profils d’affichage apprenant

Même contrat `UIState` ; rendu différent via `learner_display_profile` (`youth` | `adult` | `professional`) :

| Profil | Public cible | Variations UX lot courant |
|--------|--------------|---------------------------|
| **youth** | 16–20 ans, formation initiale | Copy tutoiement, hints scène explicites, barre progression, icônes étapes, maturité masquée, densité réduite |
| **adult** | 20–35 ans, reconversion | Copy vouvoiement équilibré, badge maturité, hints contextualisés |
| **professional** | Ingénieur / pro | Rendu discursif sobre (référence actuelle), moins d’ornementation |

Résolution backend (déjà livrée cluster 4) : cascade **query param** → **groupe** → **organisation** → défaut `professional`. Le lot courant **ne crée pas** trois contrats UIState ; il consolide le rendu front des presets existants (`displayProfilePresets.js`, `displayProfileCopy.js`).

Pilotage profil lot courant : **ORGADMIN** via groupe (existant `GroupAdminDetailView`) ; pas de nouveau endpoint apprenant obligatoire. Prévisualisation démo possible via `?learner_display_profile=` sur rechargement `ui-state` (déjà supporté backend).

### 2.3 CTA × posture × RAG (alignement minimal produit)

- **CTA** : éligibilité et visibilité restent **100 % backend** (`cta_synthesis`, `cta_evaluation`). Lot courant : variation **présentationnelle** autorisée (libellés d’aide contextuelle ou placement) selon `conversation_mode.code` et `learner_display_profile`, **sans** recalcul d’éligibilité front.
- **Posture** : le sélecteur ne remplace pas les CTA ; il modifie le régime conversationnel via API bornée.
- **RAG lexical** : badge « Appui : … » sur messages assistant (`rag_citations`) reste **complémentaire** — jamais panneau principal, jamais source de progression. Variation lot courant : ton du libellé « Appui » selon profil d’affichage (copy only).

### 2.4 Invariants de confidentialité / runtime

- Pas de P0, TurnState, verbatim interne, diagnostics techniques dans le DOM apprenant.
- Pas de `VITE_P0_DEBUG_ENABLED` en parcours prod montrable.
- UIState rechargé après `set-posture`, synthèse, évaluation, envoi message.
- Mémoire / exports / évaluation : **hors scope** — vérification non-régression seulement.

---

## 3. Design fonctionnel léger (front apprenant)

### 3.1 Écrans impliqués

| Écran / zone | Fichier | Rôle cluster 12 |
|--------------|---------|-----------------|
| Workspace session | `ProdLearnerWorkspace.vue` | Orchestration : ui-state, posture, profil, chat, CTA |
| Bannière mode | `ConversationModeBanner.vue` | **Étendre** → panneau mode + sélecteur posture |
| Progression & CTA | `HugoProgressPanel.vue` | Rendu profil (`prod-panel--{profile}`), boutons synthèse/éval |
| Layout apprenant | `ProdLearnerLayout.vue` | En-tête navigation — badge profil optionnel |
| Admin groupe | `GroupAdminDetailView.vue` | **Inchangé** — pilotage `learner_display_profile` groupe |

### 3.2 Sélecteur de posture — conditions d’apparition

```
ui-state chargé
  └─ conversation_mode présent
       ├─ label affiché (toujours si présent)
       └─ can_switch === true
            └─ afficher contrôle sélection (3 options, posture courante disabled/highlighted)
       └─ can_switch === false
            └─ lecture seule + helper « Changement indisponible en phase avancée »
```

- Emplacement proposé : **sous l’en-tête session**, remplacer/étendre `ConversationModeBanner` en `ConversationModePanel.vue`.
- Refus serveur : message utilisateur générique + conserver posture affichée ; re-fetch `ui-state`.
- Succès : toast discret + `loadWorkspace({ silent: true })`.

### 3.3 Trois profils — lecture du même UIState

Flux inchangé :

1. `GET /hugo/sessions/{id}/ui-state/?gamification_profile=B&learner_display_profile=<résolu>`
2. `buildEngagementUiModel({ sessionUiState })` → flags présentation + CTA + copy
3. `HugoProgressPanel` + sections conversation appliquent `profileCopy`, `stepHints`, classes CSS

Aucune branche métier locale sur `scene_progress`, `posture`, ou `cta_*`.

### 3.4 RAG visible

- Conserver rendu inline `Appui : {document_title}` sur bulles assistant.
- Lot courant : wrapper copy par profil (`displayProfileCopy.js` — clé `ragSupportLabel` à ajouter).

---

## 4. État actuel (RÉEL OBSERVÉ)

### 4.1 Déjà aligné

| Élément | Preuve |
|---------|--------|
| Consommation UIState backend-first | `ProdLearnerWorkspace.vue`, `engagementUiModel.js` |
| CTA synthèse/évaluation pilotés serveur | `HugoProgressPanel.vue`, tests `engagementUiModel.test.js` |
| `conversation_mode` exposé | `ui_state_builder._build_conversation_mode`, tests cluster 4 |
| Affichage mode lecture seule | `ConversationModeBanner.vue` |
| API `set-posture` | `SessionSetPostureView`, `test_set_posture_endpoint_updates_session` |
| `learner_display_profile` cascade | `resolve_learner_display_profile_for_session`, tests cluster 4 |
| Presets 3 profils (logique) | `displayProfilePresets.js`, `displayProfileCopy.js`, tests unitaires |
| Classe CSS profil sur panneau | `HugoProgressPanel` : `prod-panel--{profile}` |
| RAG citations apprenant | `ProdLearnerWorkspace` — badge Appui |
| ORGADMIN change profil groupe | `GroupAdminDetailView.vue` |
| Smokes Playwright encadrants | clusters 8 — **pas de smoke apprenant posture** |

### 4.2 Gaps principaux vs cible lot courant

| Gap | Statut | Impact |
|-----|--------|--------|
| **Sélecteur posture interactif** | **ABSENT** | Écart confirmé G2-02 — API OK, UI absente |
| **Brancher `set-posture` depuis front apprenant** | **ABSENT** | Aucun appel API posture dans `frontend_1.8` |
| **Profils adult/pro — différenciation visuelle CSS** | **PARTIEL** | Presets JS OK ; styles `prod-panel--adult/youth` à renforcer |
| **CTA libellés × posture** | **ABSENT** | `cta_ui_state.py` — libellés identiques toutes postures (D2-M02) |
| **CTA copy × profil affichage** | **PARTIEL** | Tests imposent labels backend identiques ; seul le copy entourage varie |
| **Matrice états bascule SW-xx** | **CIBLE DOC** | Annexe spec interface non implémentée front |
| **Playwright B1 apprenant** | **ABSENT** | Pas de spec posture/profil dans `tests_playwright/` |
| **Learner self-service profil affichage** | **HORS LOT COURANT** | Spec ouvre apprenant ; réel = org/groupe — acceptable si documenté |

### 4.3 Non-régression mémoire (domaine 20 — vérification)

- `memory-summary` non consommé par le front apprenant prod — **OK**.
- Pas d’injection mémoire verbatim dans workspace — **OK**.
- Cluster 12 ne touche pas aux endpoints mémoire.

---

## 5. Plan de mise en œuvre

### 5.1 Changements front (prioritaires)

| # | Fichier / composant | Action |
|---|---------------------|--------|
| F1 | `PostureSelector.vue` (**nouveau**) | Radio/segmented control 3 postures ; props `conversationMode`, `busy` ; emit `select-posture` |
| F2 | `ConversationModePanel.vue` (**nouveau**) ou extension banner | Intègre label, warning, `PostureSelector` si `canSwitch` |
| F3 | `ProdLearnerWorkspace.vue` | `setPosture(code)` → POST set-posture → reload ui-state ; remplacer import banner |
| F4 | `assets/styles` ou scoped CSS prod | Thèmes `prod-panel--youth`, `--adult`, `--professional` (typo, espacement, couleurs) |
| F5 | `displayProfileCopy.js` | Ajouter `ragSupportLabel`, éventuellement `postureHelper` par profil |
| F6 | `ProdLearnerWorkspace.vue` | Appliquer `profileCopy` au placeholder composer et empty state (quelques chaînes encore génériques) |
| F7 | `HugoProgressPanel.vue` | Optionnel : micro-copy CTA helper depuis `profileCopy` si backend helper null |

### 5.2 Ajustements backend (petits, optionnels)

| # | Fichier | Action | Priorité |
|---|---------|--------|----------|
| B1 | `cta_ui_state.py` | Mapper `helper_text` ou suffixe label selon `progress.posture` (ex. knowledge_review → « Prépare une trace de révision ») | P1 |
| B2 | `ui_state_builder.py` | Exposer `conversation_mode.available_targets[]` (postures autorisées) pour simplifier le front | P2 |
| B3 | Tests | `test_cluster4_surface_contracts.py` + test CTA×posture si B1 | P1 |

**Pas de changement** : orchestrateur, P0, mémoire, exports, RAG moteur.

### 5.3 Scénarios Playwright B1 (à ajouter)

| ID | Scénario | Assertions |
|----|----------|------------|
| **B1-01** | Posture visible | LEARNER ouvre session ; `[aria-label="Mode conversationnel"]` ou badge « Mode » affiche label (ex. Réflexif) |
| **B1-02** | Changement posture autorisé | Session jeune phase (`can_switch` true) ; sélection « Diagnostic » ; POST set-posture 200 ; label mis à jour après reload |
| **B1-03** | Refus posture | Session mature simulée (`can_switch` false) ; sélecteur absent ou disabled ; pas d’appel set-posture |
| **B1-04** | Profil affichage youth | Groupe bootstrap profil `youth` ; panneau progression avec classe `prod-panel--youth` ; hint tutoiement visible |
| **B1-05** | CTA sans fuite P0 | DOM ne contient pas `turn_state`, `p0_`, `verbatim` ; boutons synthèse/éval présents si ui-state eligible |
| **B1-06** | RAG Appui | Message avec citation → badge « Appui » visible ; pas de panneau RAG autonome |

Fichiers cibles :

- `tests_playwright/test_b1_learner_posture.spec.ts`
- `tests_playwright/test_b1_learner_display_profile.spec.ts`
- Extension `bootstrap_smoke_playwright.py` : groupe `smoke_youth` profil youth, session early-phase pour B1-02

### 5.4 Documentation à mettre à jour

| Document | Action |
|----------|--------|
| `ecarts — 31_front_apprenant_postures_et_bascule.md` | § cluster 12 — gaps fermés / restants |
| `specs interface 2.0.md` | POST set-posture réel ; annexe états bascule SW-xx V1 |
| `cluster2_matrice_runtime_vs_cible.md` | Domaine 31 : sélecteur + profils → statut post-C12 |
| `REFERENCE_CONVERGENCE...` | Cluster B = cluster 12 ouvert |
| `plan_documentation_cto_convergence_hugo.md` | Entrée cluster 12 |

---

## 6. Tableau d’actions cluster 12

| Axe | Type | Domaine | Priorité | Fichier(s) impacté(s) |
|-----|------|---------|----------|------------------------|
| Sélecteur posture G2-02 | **CODE** | 31 | **P0** | `PostureSelector.vue`, `ConversationModePanel.vue`, `ProdLearnerWorkspace.vue` |
| Brancher API set-posture | **CODE** | 31 / 10 | **P0** | `ProdLearnerWorkspace.vue`, `api/client.js` (si helper) |
| Styles 3 profils UX | **CODE** | 31 | **P0** | CSS prod, `HugoProgressPanel.vue`, `displayProfilePresets.js` |
| Copy profil / RAG | **CODE** | 31 / 30 | **P1** | `displayProfileCopy.js`, `ProdLearnerWorkspace.vue` |
| CTA helper × posture | **CODE** | 10 | **P1** | `cta_ui_state.py`, tests backend |
| `available_targets` UIState | **CODE** | 10 | **P2** | `ui_state_builder.py` |
| Annexe états bascule SW-xx | **DOC** | 31 | **P0** | `specs interface 2.0.md` ou note annexe |
| Écarts domaine 31 | **DOC** | 31 | **P0** | `ecarts — 31_...md` |
| POST vs PATCH posture | **DOC** | 10/31 | **P1** | D2-M03 — aligner spec sur réel |
| Playwright B1-01 → B1-06 | **OPS** | 31 | **P0** | `tests_playwright/test_b1_*.spec.ts`, bootstrap |
| Bootstrap groupes profils | **OPS** | 31 | **P1** | `bootstrap_smoke_playwright.py` |
| Non-régression smokes C8 | **OPS** | 31/90 | **P1** | `npm run test:smoke` après changements |

---

## 7. Garde-fous de non-régression (checklist clôture)

Avant de clôturer le cluster 12, vérifier systématiquement :

- [ ] **UIState seule source** — aucun calcul local d’éligibilité synthèse/évaluation/posture.
- [ ] **Pas de fuite P0/TurnState** — grep front + assertion Playwright B1-05 ; `VITE_P0_DEBUG_ENABLED=false` en prod.
- [ ] **Pas de verbatim interne** — parcours apprenant inchangé sur confidentialité (smokes cluster 8 toujours PASS).
- [ ] **Posture ≠ télécommande moteur** — UI n’envoie que `posture` enum ; pas d’édition prompts/profils conducteur côté apprenant.
- [ ] **set-posture respecte refus serveur** — UI gère `400 transition_not_allowed` sans état optimiste incohérent.
- [ ] **RAG complémentaire** — badge Appui seulement ; pas de liste documents, pas de recherche RAG apprenant.
- [ ] **Profils = présentation** — même `cta_*`, même progression ; variations copy/CSS uniquement (sauf B1 CTA helper doc-validé).
- [ ] **Mémoire / exports / eval intouchés** — diff limité à `frontend_1.8` + éventuellement `cta_ui_state.py` / `ui_state_builder.py`.
- [ ] **Tests** — unitaires existants PASS ; nouveaux B1 Playwright PASS ; `test_posture_modes.py` + cluster 4 PASS.

---

## 8. Prochaine sortie utile

1. **Implémenter P0** : F1–F3 (sélecteur + branchement API) + B1 Playwright B1-01/B1-02.
2. **Consolider profils** : F4–F6 + B1-04.
3. **DOC** : annexe SW-xx + mise à jour écarts 31.
4. **P1 optionnel** : CTA×posture backend (B1) si arbitrage produit validé.

Le cluster 13 (couronne : RAG vectoriel, COORDO, dashboards, taxonomie exports) reste **hors scope** de ce plan.
