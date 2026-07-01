# Addendum — front réel après lots A + B + C (baseline B)

**Date :** 2026-07-01  
**Baseline :** front `frontend_1.8` + `hugo_back` local, pipeline **P0 legacy** actif par défaut  
**Périmètre :** séparation des chats apprenant / tuteur / formateur et mutualisation limitée au noyau conversationnel

---

## Sources mobilisées

- Code `frontend_1.8` après lots A, B, C
- `spec_reconfiguration_chats_tuteur_formateur.md` (copie versionnée dans `docs-workspace`)
- Tests Playwright `tests_playwright/helpers.ts`

## Réel confirmé (front baseline B)

### Séparation des shells

| Persona | Route session | Composant workspace | Shell apprenant réutilisé ? |
|---------|---------------|---------------------|----------------------------|
| Apprenant | `/app/session/:sessionId` | `ProdLearnerWorkspace.vue` | Non (shell dédié apprenant) |
| Tuteur | `/app/tutor/chat/:sessionId` | `ProdTutorChatWorkspace.vue` | Non |
| Formateur | `/app/trainer/chat/:sessionId` | `ProdTrainerChatWorkspace.vue` | Non |

Routes home dédiées :

- Tuteur : `/app/tutor` (+ fiche apprenant `/app/tutor/group/:groupId/learner/:learnerId`)
- Formateur : `/app/trainer/chat` (home création / reprise session)

Un utilisateur TUTOR ou TRAINER pur redirigé vers `/app` ou `/app/session/:id` est renvoyé vers ses routes dédiées (`ProdLearnerHomeView`, `ProdLearnerSessionView`, topbar `ProdLearnerLayout`).

### Mutualisation limitée (lot C)

Composable partagé : `src/composables/useHugoSessionChat.js`

- Charge session, messages, envoi, stream SSE, états loading/erreur, refresh minimal
- Options : `loadUiState`, `loadLearnerArtifacts`, `streamingPersona`, `onSessionLoaded`, `getUiStateParams`
- **Sans** posture, progression, CTA synthèse/évaluation, traces, imports persona

Utilisation réelle :

- `ProdLearnerWorkspace.vue` : `loadUiState: true`, `loadLearnerArtifacts: true`, `streamingPersona: 'learner'`
- `ProdTutorChatWorkspace.vue` / `ProdTrainerChatWorkspace.vue` : noyau seul ; modèle feed minimal via `buildPersonaConversationFeedModel()` (`conversationFeedModel.js`)

### Blocs legacy apprenant absents des chats persona

Sur tuteur et formateur, les assertions Playwright `expectNoLearnerWorkspaceBlocks` vérifient l’absence de :

- badge posture (`session-posture-badge`)
- boutons synthèse / évaluation
- carte quête (`.prod-quest-card`)

## Cible 2.0 (non entièrement livrée)

- Objets métier tuteur durables (notes, transmissions inter-rôles) : **CIBLE**, hors P1
- Surfaces cohorte / capitalisation formateur complètes : **CIBLE**
- Parité Encoors des routes et profils : **À VÉRIFIER**

## Écarts

- Le fil UI `LearnerConversationFeed.vue` reste un composant visuel partagé ; seul le **shell workspace** et la **logique conversationnelle** sont séparés
- Les imports P1 (tuteur/formateur) s’appuient sur des barres d’outils persona dans le fil, pas sur les CTA apprenant

## Prochaine sortie utile

Exécuter le plan de tests mis à jour (`plan_tests_chats_tuteur_formateur.md`) avec serveur Vite + backend local pour obtenir un audit PASS/FAIL consolidé.

---

## Complément 2026-07-01 (v1.1 — exploration + Décision B)

**Ne remplace pas** les sections ci-dessus.

### Playwright apprenant (UI v2)

- `e2e/cluster16_learner_interface.spec.ts` aligné shell `learnerUiV2` (sélecteurs `Modes de conversation`, panneaux Actions / Progression / Mémoire).
- Attente explicite `GET /ui-state/` (via bouton « Actualiser » header v2) avant assertions engagement.
- **8/8 PASS** (01/07, baseline B, backend `:8000`).

### Décision B — `GET /ui-state/`

Voir `addendum_exploration_baseline_B_2026_07_01.md` §3 et **R4** §3.

- Persona : `loadUiState: false` dans `ProdTutorChatWorkspace` / `ProdTrainerChatWorkspace` — **ne pas consommer** ce contract pour l'UI.
- API : endpoint reste callable par owner session ; pas de 404 persona documenté à ce stade.

### Référence croisée

- Cartographie pipes par rôle, persona sqlite, gate Postgres, INC-02 : `addendum_exploration_baseline_B_2026_07_01.md`.

