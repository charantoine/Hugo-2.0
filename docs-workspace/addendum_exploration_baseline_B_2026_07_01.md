# Addendum — exploration baseline B (30/06 → 01/07/2026)

**Version :** 1.0  
**Date :** 2026-07-01  
**Baseline :** B locale — `config.settings.sqlite_test`, `test.sqlite3`, `HUGO_P0_V17_ENABLED=false`, front `frontend_1.8` + `hugo_back` (`localhost:5173` → `:8000`)  
**Périmètre :** consolidé depuis explorations, patches tests-only, cartographie pipes par rôle, Pass 2 persona (partiel), lots A+B+C front.  
**Ne remplace pas** R0–R7 ; complète `addendum_front_chats_lots_ABC_2026_07_01.md` et `plan_tests_chats_tuteur_formateur.md`.

---

## Sources mobilisées

- Rejeux pytest / Playwright (01/07/2026)
- Cartographie front/back pipes apprenant / tuteur / formateur (01/07/2026)
- `memo_cto_2026-06-30.md`, R2/R4/R5/R6
- Code : `useHugoSessionChat.js`, `persona_session.py`, `sqlite_schema_patches.py`, specs Playwright cluster16 / smoke_tutor

---

## 1. Réel confirmé (01/07/2026)

### 1.1 Backend pytest (sqlite_test)

| Gate | Résultat | Tag |
|------|----------|-----|
| Lot convergence combiné (clusters 3/15/16, tenant, morning baseline B, persona pass2, etc.) | **148/148 PASS** | **REL OBSERV** |
| `test_cluster3_oracles.py` + `test_cluster15_*` + `test_cluster16_interface_apprenant_backend.py` | **33/33 PASS** (rejeu ciblé 01/07) | **REL OBSERV** |
| `test_persona_conversation_pass2.py` (9 tests, dont patch sqlite) | **PASS** | **REL OBSERV** |

### 1.2 Playwright (baseline B, backend `:8000` requis)

| Spec | Résultat (post-patch 01/07) | Tag |
|------|-----------------------------|-----|
| `e2e/cluster16_learner_interface.spec.ts` | **8/8 PASS** (UI v2 + wait `/ui-state/`) | **REL OBSERV** |
| `test_smoke_tutor.spec.ts` | **1/1 PASS** (copy UX corrigée) | **REL OBSERV** |
| `test_learner_chat_non_regression_after_tutor_trainer_changes.spec.ts` | **2/2 PASS** | **REL OBSERV** |

**Prérequis E2E :** `hugo_back` actif sur `:8000` ; Vite `:5173` (démarré par `playwright.config.ts` ou `run_local_hugo.sh`).

### 1.3 Persona admin (sqlite_test)

| Étape | Résultat | Tag |
|-------|----------|-----|
| `POST /hugo/persona-conversation-profiles/` | **201** (après `ensure_sqlite_persona_schema`) | **REL OBSERV** |
| `POST .../preview-render/` | **200** | **REL OBSERV** |
| 2ᵉ exécution `ensure_persona_schema()` | idempotent (`[]`) | **REL OBSERV** |

Cause initiale 500 : colonne `tutor_prompt.persona_scope` / table `persona_conversation_profile` absente sur `test.sqlite3` stale (`MIGRATION_MODULES` désactivé en sqlite_test).

### 1.4 Front apprenant — Lot C

- Extraction `useHugoSessionChat.js` : plumbing session/messages/SSE uniquement ; CTA, traces, partage, posture restent dans `ProdLearnerWorkspace.vue`.
- Contrats API inchangés ; smoke apprenant **PASS** (01/07).
- Échecs cluster16 **avant** patch = tests legacy UI v1 + course `/ui-state/`, **pas** régression métier Lot C.

---

## 2. Partiel / infra / écarts inchangés

| Sujet | Statut | Tag |
|-------|--------|-----|
| Gate Postgres `config.settings.dev` — ~41 ERROR parallèle | **Infra** (`DuplicateDatabase` / `ObjectInUse` sur `hugo_poc_test`) ; séquentiel cluster3 → **5/5 PASS** | **REL OBSERV** |
| INC-02 — `GET /dashboard/groups/{id}/learners/` → `[]` pour TRAINER | **Écart produit ouvert** ; tests figés ; pas de patch ACL | **ÉCART CONFIRMÉ** |
| Parité Encoors post-16/06 | Non re-oraclisé | **À VÉRIFIER** |
| Surfaces persona admin E2E complètes | CRUD HTTP OK ; campagne Playwright admin persona limitée | **REL OBSERV PARTIEL** |

---

## 3. Décision doctrinale provisoire — **Décision B** (`GET /ui-state/`)

**Date :** 2026-07-01  
**Contexte :** endpoint partagé au niveau HTTP (`HugoSession.learner = request.user` pour tuteur/formateur en session persona), mais consommation front différenciée via `loadUiState`.

| Niveau | Position |
|--------|----------|
| **API / ACL** | `GET /hugo/sessions/{id}/ui-state/` reste un **contract owner** : le propriétaire de session (y compris tuteur/formateur sur **sa** session persona) *peut* l'appeler techniquement. **Pas de garde `is_persona_session` → 404** à ce stade. |
| **Produit / front** | Ce contract est un **contract d'engagement réservé au front apprenant** : posture UI, CTA synthèse/évaluation, progression engagement via `buildEngagementUiModel(sessionUiState)`. |
| **Persona (tuteur / formateur)** | `ProdTutorChatWorkspace` / `ProdTrainerChatWorkspace` : `loadUiState: false` ; feed via `buildPersonaConversationFeedModel()` (`sessionUiState: null`). **Ne doit pas consommer** `/ui-state/` pour piloter l'UI. |
| **Tests / doc** | Ne pas documenter l'endpoint comme « interdit backend persona » ; documenter l'**interdiction de consommation produit** côté workspaces persona. Vérifier via `expectNoLearnerWorkspaceBlocks` + absence d'appel front. |

**Dette à surveiller :** un client persona activant `loadUiState: true` réactiverait CTAs/progression apprenant sur session persona (non bloqué server-side). Option future : garde backend ou test contract explicite — **hors périmètre 01/07**.

**Références code :** `useHugoSessionChat.js` (options), `conversationFeedModel.js`, `views_sessions.SessionUiStateView`, `views_sessions` blocage CTA persona sur `request-synthesis` / `request-evaluation` (404).

---

## 4. Cartographie pipes — synthèse (01/07)

### 4.1 Séparation réelle

- **HTTP partagé** : `/hugo/sessions/{id}/messages/`, `.../stream/` — même orchestrateur `build_hugo_turn` ; différenciation prompt via `resolve_persona_prompt_for_session` (persona) vs résolveurs apprenant.
- **Engagement apprenant** : `GET /ui-state/`, `POST .../request-synthesis/`, `.../request-evaluation/`, `GET .../memory-summary/` (session apprenant tierce → ACL owner).
- **Tuteur** : dashboard timeline, traces validate, chat persona ; pas d'appel front `/ui-state/`.
- **Formateur** : `/hugo/trainer/knowledge-items/*`, chat persona ; pas d'appel front `/ui-state/` ni memory-summary learner.

### 4.2 Composants front partagés — dette nommage

| Artefact | Risque | Statut doc |
|----------|--------|------------|
| `useHugoSessionChat` | Noyau transport partagé ; flags séparent métier | **À surveiller** |
| `LearnerConversationFeed` | Visuel + toolbars import persona ; nom `learner/` | **À surveiller** |
| `buildPersonaConversationFeedModel` | Neutralise UIState apprenant | **OK** |

Détail : voir exploration cartographie 01/07 (non dupliqué ici).

---

## 5. Patches appliqués (tests + doc OPS, 01/07)

| Fichier | Nature |
|---------|--------|
| `tests_playwright/e2e/cluster16_learner_interface.spec.ts` | Sélecteurs UI v2 ; `waitForResponse` `/ui-state/` via « Actualiser » header v2 |
| `tests_playwright/test_smoke_tutor.spec.ts` | Copy home tuteur actuelle |
| `plan_tests_chats_tuteur_formateur.md` | Gate Postgres, persona sqlite, INC-02, prérequis E2E |

**Non modifié :** `access_control.py` (INC-02), code métier Lot C, orchestrateur P0.

---

## 6. Prochaine sortie utile

- Campagne Playwright admin persona (CRUD UI) si priorité produit.
- ADR CTO sur INC-02 avant évolution specs formateur cohorte.
- Option garde backend `SessionUiStateView` + persona — seulement si la Décision B est révisée.

---

## 7. Matrice endpoint × rôle

Voir **`matrice_endpoint_role.md`** (v1.0, 2026-07-01) — vue croisée statuts OK / Owner-only / Interdit produit / Écart / Non concerné par rôle.

---

*Addendum v1.0 — 2026-07-01 — baseline B exploration / tests / Décision B ui-state.*
