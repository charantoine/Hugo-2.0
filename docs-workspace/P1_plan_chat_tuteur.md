# P1 — Chat tuteur d’orchestration (baseline B)

> **BASELINE HISTORIQUE** — document d’exécution P1 (2026-07-01).  
> Ne pas utiliser comme spec active : la cible courante et le refactor front sont dans  
> [`spec_reconfiguration_chats_tuteur_formateur.md`](spec_reconfiguration_chats_tuteur_formateur.md)  
> et l’addendum [`addendum_front_chats_lots_ABC_2026_07_01.md`](addendum_front_chats_lots_ABC_2026_07_01.md).

**Date :** 2026-07-01  
**Baseline :** B (front 1.8 + `hugo_back` local)  
**Pipeline actif par défaut :** P0 legacy (`HUGO_P0_V17_ENABLED=false`)  
**Décision :** réalisation autorisée — brouillons volatiles, pas de persistance durable nouvelle

---

## 1. Sources mobilisées

- R0–R4 (`recalage_actualisation_2026_07_01/`)
- `modelisation_activite_tuteur.md` (8 familles, invariants)
- `spec_reconfiguration_chats_tuteur_formateur.md`
- `P1_plan_import_chat_formateur.md` (patron formateur livré)
- Code : `tutor_workspace_bootstrap.py`, `tutorWorkspaceProfiles.js`, `tutorChatImport.js`, `ProdTutorChatWorkspace.vue`

## 2. Réel confirmé utile P1

| Élément | Tag | Preuve |
|---------|-----|--------|
| Surface `/app/tutor` + fiche apprenant | **REL OBSERV** | `ProdTutorHomeView`, routes tuteur |
| 4 profils globaux `tutor_workspace_*` seedés | **REL OBSERV** | `ensure_tutor_workspace_profiles`, bootstrap smoke |
| Chat tuteur sur route dédiée `/app/tutor/chat/:id` | **REL OBSERV** (lots A+B) | `ProdTutorChatSessionView`, `ProdTutorChatWorkspace` |
| Imports = brouillon Pinia volatile, relecture humaine | **REL OBSERV** | `useTutorWorkspaceStore`, pas de POST métier durable P1 |
| Chaîne évaluation apprenant inchangée | **REL OBSERV** | pas d’appel `request-evaluation` côté tuteur |
| `memory-summary` lecture seule côté tuteur | **REL OBSERV PARTIEL** | panneau mémoire read-only si présent |

## 3. Cible P1 tuteur

Chat d’**orchestration tutorale** : préparation, diagnostic prudent, réflexion, journal — sans clone du shell apprenant.

### 3.1 Quatre profils `tutor_workspace_*`

| Code profil | Posture primaire | CTA depuis fiche apprenant | Import unique (1 par profil) |
|-------------|------------------|----------------------------|------------------------------|
| `tutor_workspace_prep` | `reflective_afest` | « Préparer mon entretien » | `tutor_session_prep` — Enregistrer la préparation |
| `tutor_workspace_diagnostic` | `diagnostic` | « Aide au diagnostic » | `tutor_diagnostic_notes` — Enregistrer les hypothèses |
| `tutor_workspace_coreflex` | `reflective_afest` | « Préparer des questions » | `tutor_reflection` — Enregistrer les questions préparées |
| `tutor_workspace_journal` | `knowledge_review` | « Noter un point-clé » | `tutor_journal_entry` — Enregistrer le point-clé |

Fichiers de référence :

- `src/utils/tutorWorkspaceProfiles.js` — codes, postures, libellés CTA
- `src/utils/tutorChatImport.js` — kinds et payloads structurés
- `src/utils/tutorWorkspaceSession.js` — création session + navigation vers `/app/tutor/chat/:sessionId`

### 3.2 CTA d’entrée depuis la fiche apprenant

Depuis `/app/tutor/group/:groupId/learner/:learnerId` :

- 4 boutons `data-testid="tutor-cta-{profile_code}"`
- Contexte propagé en query : `learner_id`, `group_id`, `profile_code`, `source_session_id` (si applicable)
- Store Pinia `tutorWorkspace` : contexte volatile pour reprise navigation

**Tag réel :** **REL OBSERV** après implémentation P1 + lots A/B.

### 3.3 Brouillons Pinia volatiles

- Store : `src/stores/tutorWorkspace.js`
- Panneau : `TutorSessionDraftsPanel.vue`
- Comportement P1 : les brouillons confirmés restent **en mémoire front uniquement** ; rechargement page = perte attendue (test `test_tutor_reload_no_durable_draft`)
- `human_validation_required: true` dans les drafts ; pas d’écriture backend objet tutorale durable

### 3.4 Un import par profil

Règle produit P1 : **exactement un** `import_kind` actif par profil workspace (barre fixe sous le fil en `compactHeader`, pas les CTA apprenant).

Mapping implémenté : `importKindForWorkspaceProfile()` dans `tutorWorkspaceSession.js`.

## 4. Exclusions explicites P1

- Pas de persistance durable des brouillons tuteur (pas de nouveau modèle backend)
- Pas de modification ACL ni de `TutorLearnerLink`
- Pas de chaîne `request-synthesis` / `request-evaluation` / `generate-trace` côté tuteur
- Pas de transmission structurée tuteur → formateur (bouton 6 spec maîtresse) : **CIBLE P2+**
- Pas de note tutorale privée persistée (bouton 4 spec) : remplacé en P1 par brouillon volatile
- Pas d’injection `memory-summary` dans le prompt LLM
- Pas de refactor pipeline P0 / v17
- Pas de réutilisation de `ProdLearnerWorkspace` comme shell tuteur (interdit après lots A+B+C)

## 5. Fichiers front principaux (réel baseline B)

| Fichier | Rôle |
|---------|------|
| `ProdTutorChatWorkspace.vue` | Shell chat tuteur |
| `ProdTutorChatSessionView.vue` | Vue route session |
| `TutorImportConfirmModal.vue` | Confirmation import |
| `TutorWorkspaceContextPanel.vue` | Contexte apprenant/groupe |
| `LearnerConversationFeed.vue` | Fil partagé (mode `personaMode=tutor`) |
| `useHugoSessionChat.js` | Noyau conversationnel mutualisé (lot C) |

## 6. Critères d’acceptation P1

- Ouverture session depuis chaque CTA des 4 profils → URL `/app/tutor/chat/:sessionId`
- Zéro bloc legacy apprenant sur le chat tuteur (`expectNoLearnerWorkspaceBlocks`)
- Import par profil : modale, draft structuré, enregistrement volatile store
- Rechargement page : brouillon non durable
- Parcours apprenant `/app/session/:id` non régressé

## 7. À VÉRIFIER

- Parité Encoors des profils `tutor_workspace_*` et conduct prompts
- Comportement timeline tuteur avec verbatim non partagé (ACL existante, hors ce lot front)

## 8. Prochaine sortie utile

Lot P2 tuteur (si validé produit) : persistance légère ou objets `tutor_note` / transmission formateur — **non démarré** à la date de cet addendum.
