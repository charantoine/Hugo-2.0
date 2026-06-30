# Audit front formateur — réel observé (juin 2026)

> **Mise à jour 30/06/2026 — navigation prod :** entrée TRAINER → `/app/trainer/knowledge` (`resolveAuthenticatedHome`) ; routes référentiels globales en shell prod ; topbar « Chat apprenant » (droite). **Limite :** `/group/:id/referential` reste testeur.

**Date :** juin 2026  
**Périmètre :** surfaces UI accessibles au rôle **TRAINER** ; pilotage profils comportementaux ; base de connaissances ; navigation prod/tester.  
**Méthode :** code front + API backend + tests ; doc workspace en indice uniquement (recoupée au code).  
**Domaines liés :** `ecarts — 40_base_connaissances_formateur.md`, `ecarts — 50_orchestrateur_formateur.md`, `ecarts — 110_interfaces_formateur_tuteur.md`.

**Suite documentaire :** [matrice](audit_front_formateur_01_matrice.md) · [backlog](audit_front_formateur_03_backlog.md)

---

## Sources mobilisées

| Couche | Fichiers / preuves |
|--------|-------------------|
| Router / rôles | `frontend_1.8/src/router/index.js`, `roleGuards.js`, `ProdLearnerLayout.vue`, `TesterLayout.vue` |
| Surfaces formateur prod | `ProdTrainerKnowledgeView.vue`, `ProdTrainerElicitationView.vue` |
| Surfaces tuteur héritées | `ProdTutorHomeView.vue`, `ProdTutorGroupView.vue`, `ProdTutorLearnerView.vue`, `TutorLearnerView.vue` |
| Admin (hors TRAINER) | `TrainerOrchestratorAdminView.vue`, `LearnerConversationProfilesView.vue`, `ConductProfilesView.vue`, `GroupAdminDetailView.vue` |
| API formateur | `hugo_back/apps/hugo/views_trainer.py`, `urls.py` |
| API library (écriture TRAINER) | `hugo_back/apps/library/views.py` |
| Résolution profils runtime | `learner_profile_resolver.py`, `conduct_profile_resolver.py`, `hugo_orchestrator.py` |
| Consommation knowledge | `evaluation_service.py` (pas `context_builder` ni `hugo_orchestrator`) |
| RAG conversation | `rag_support.py` → `DocumentChunk` / `GroupDocument` |
| Tests | `test_cluster15_interfaces_formateur.py`, `test_smoke_trainer.spec.ts`, `admin_trainer_creation.spec.ts` |
| Doc (indice, recoupée) | `03_ETAT_PRODUIT_REEL.md` §formateur |

---

## Réel confirmé

### 1. Routes réellement accessibles au TRAINER

**Layout prod** (`ProdLearnerLayout`) — entrée TRAINER via `resolveAuthenticatedHome()` → **`/app/trainer/knowledge`** (y compris si `VITE_FRONTEND_MODE=tester`) :

| Route | Garde | Actions formateur |
|-------|-------|-------------------|
| `/app/trainer/knowledge` | `requiresTrainerLike` | **Hub** — knowledge items ; liens bibliothèque, référentiels, élicitation |
| `/app/trainer/library` | idem | Bibliothèque de cours / RAG ; bouton **« Retour orchestrateur »** → `/app/trainer/knowledge` |
| `/app/trainer/referentials` | idem | Liste référentiels org (shell prod) ; **« Retour orchestrateur »** → hub |
| `/app/trainer/referentials/import` | idem | Import référentiel (shell prod) |
| `/app/trainer/elicitation` | idem | Atelier d'élicitation ; **« Retour orchestrateur »** → hub |
| `/app/tutor/*` | `requiresTutorLike` (TRAINER inclus) | Groupes filtrés ; timeline apprenants liés |
| `/app`, `/app/session/:id` | authentifié | **Chat apprenant** (topbar) |

**Layout tester** (legacy — **plus** point d'entrée TRAINER par défaut) :

| Route | Garde | Actions |
|-------|-------|---------|
| `/dashboard` | `requiresEncadrant` | Mode testeur tuteur/coordo ; TRAINER redirigé vers hub prod si accès direct |
| `/group/:id`, `/group/:id/learner/:lid` | aucune orgadmin | Calibration encadrant |
| `/group/:id/referential` | `requiresEncadrant` | **Config référentiel par groupe** — shell testeur uniquement (**limite connue**) |
| `/referentials/*` (navbar testeur) | org admin | ORGADMIN via navbar ; formateur utilise `/app/trainer/referentials` |

**Inaccessibles au TRAINER** (redirect `/app`) : tout `/admin/*`, `/groups-admin/*`, `/conduct-profiles`, `/tutor-prompts`, `/users`, etc. (`requiresOrgAdmin`).

**Navigation prod :** lien « Espace formateur » → `/app/trainer/knowledge` ; **« Chat apprenant »** (droite) → `/app` ; pas de lien Administration pour TRAINER pur. **Retour secondaire :** sur bibliothèque, élicitation et référentiels (shell prod), bouton **« Retour orchestrateur »** → `/app/trainer/knowledge` (`TrainerBackToOrchestratorLink.vue`).

### 2. Profils comportementaux — zéro pilotage formateur en UI

Le TRAINER **ne peut ni consulter ni modifier** depuis le front :

- `LearnerConversationGlobalProfile` (CRUD `/admin/conversation/learner/profiles`)
- `TutorConductProfile` (`/conduct-profiles`)
- `TutorPrompt` (`/tutor-prompts`)
- Attribution profil → groupe (`/groups-admin/:id`, `PATCH /groups/{id}/`)
- `EvaluationPolicy.trainer_directives` (`/admin/conversation/learner/closing`)

**Backend :** écriture réservée `IsOrgAdminOrSuperadmin` sur profils conversationnels et conduct profiles.

**Consommation moteur (confirmée code) :**

- Chaque tour : `resolve_learner_conversation_global_profile` → prompts + `resolve_conduct_profile` dans `hugo_orchestrator`.
- Configuré par orgadmin ; **lu** en runtime ; **non pilotable** par le formateur.

`TrainerOrchestratorAdminView` (orgadmin) indique : *« configuration conversationnelle héritée (prompts formateur) n’existe pas encore en backend »*.

### 3. Base de connaissances formateur

**UI :** `ProdTrainerKnowledgeView` + `ProdTrainerElicitationView`.

| Opération | UI | API |
|-----------|-----|-----|
| Lister | Oui | `GET /hugo/trainer/knowledge-items/` |
| Créer | Via élicitation ou ingest (pas de POST direct sur la liste) | `POST …/elicitation-answers/`, `POST /hugo/trainer/documents/ingest/` |
| Valider / rejeter / provisoire / éditer | Oui | `POST …/knowledge-items/{id}/validate/` |
| Tags / scènes / domaines structurés | Non | seul `referential_item_id` (texte libre) |

**Statuts :** `declared`, `derived_provisional`, `validated_trainer` (aligné `KnowledgeItemStatus`).

**Consommation moteur :**

- Items `validated_trainer` → `_validated_trainer_items()` → prompt **évaluation** uniquement (`evaluation_service.build_evaluation_prompt`).
- **Pas** d’injection dans le tour conversationnel courant ni dans `rag_support`.
- RAG conversation = `Document` / `GroupDocument` (bibliothèque admin), système **parallèle**.

**Écart back/front documenté :** `library/views.py` autorise TRAINER sur `POST /documents/`, index, liaison groupe (`IsOrgAdminSuperadminOrTrainer`) — **aucune vue prod formateur** pour ces endpoints.

**API sans UI :** `GET/POST /hugo/trainer/evaluation-records/*` (validation évaluations partagées).

### 4. Structure et incohérences UX

1. **Hub formateur partiel** — routes prod reliées (knowledge, library, référentiels globaux, élicitation) ; config référentiel **par groupe** encore testeur.
2. ~~**Atterrissement prod `/app`**~~ — **corrigé 30/06** : entrée `/app/trainer/knowledge` (`resolveAuthenticatedHome`).
3. **`isTrainerLike` inclut orgadmin** — même écran knowledge sans distinction de rôle.
4. **Double base** — `TrainerKnowledgeItem` vs bibliothèque RAG ; pas de pont UI.
5. **Mode testeur** — pas de calibration chat complète sur autrui (`TutorLearnerView` = timeline, pas `LearnerDetailView`).
6. **Hub `/admin/conversation/trainer`** — carte de liens orgadmin, pas le shell métier formateur.

---

## Cible 2.0 (rappel, non preuve de livraison)

- Orchestrateur formateur distinct : élaboration + validation savoir métier.
- `TrainerKnowledgeItem` gouvernés, validation humaine obligatoire.
- Enrichissement orchestrateurs apprenant via RAG / contenus validés.
- Interfaces formateur branchées sur objets backend, sans pilotage direct du P0.
- Voir `ecarts — 40`, `ecarts — 50`, `ecarts — 110` pour le détail doctrinal.

---

## Écarts confirmés (synthèse)

| # | Écart | Gravité |
|---|-------|---------|
| E1 | Aucune UI formateur sur profils comportementaux / attribution groupe | Élevée (rupture parcours métier) |
| E2 | Knowledge formateur consommé **évaluation seulement**, pas chat | Élevée (attente produit souvent inverse) |
| E3 | API library/RAG ouverte TRAINER, UI uniquement orgadmin | Moyenne |
| E4 | API evaluation-records sans écran | Moyenne |
| E5 | Parcours formateur unifié (navigation / hub) | **Partiellement adressé** (entrée + référentiels globaux prod ; config groupe testeur) |
| E6 | Élicitation V0 (ID référentiel manuel, ingest chemin serveur) | Moyenne |
| E7 | Confusion rôle TRAINER / tuteur / apprenant sur `/app` | Moyenne |
| E8 | Hub admin « orchestrateur formateur » inaccessible au TRAINER pur | Faible (nommage) |

---

## A_VERIFIER

- Comportement runtime distant (`hugoback.encoors.com`, flags `.env`) non rejoué dans cet audit.
- Parcours démo avec comptes `smoke_trainer` / formateur melec si mots de passe non documentés.
- Volume réel d’items knowledge exploités en évaluation en prod (métrique `usage_count` toujours `null` côté API).

---

## Prochaine sortie utile

1. Valider la proposition de restructuration (hub `/app/trainer`, lecture profil groupe, UI library formateur).
2. Mettre à jour `03_ETAT_PRODUIT_REEL.md` §surfaces formateur (hub admin ≠ formateur pur).
3. Exécuter le backlog [audit_front_formateur_03_backlog.md](audit_front_formateur_03_backlog.md) par priorité P0→P3.

---

*Audit ancré code juin 2026 — complète les rapports d’écarts domaine 40 / 50 / 110 sans les remplacer.*
