# Plan de tests automatisés — chats tuteur et formateur (baseline B)

## Mise à jour post lots A + B + C (2026-07-01)

### Réel confirmé — routes et shells front

| Persona | Home / entrée | Session chat | Workspace | Assertion anti-legacy |
|---------|---------------|--------------|-----------|------------------------|
| Apprenant | `/app` | `/app/session/:sessionId` | `ProdLearnerWorkspace.vue` | N/A (blocs posture/CTA/quêtes attendus) |
| Tuteur | `/app/tutor`, fiche `/app/tutor/group/:g/learner/:l` | `/app/tutor/chat/:sessionId` | `ProdTutorChatWorkspace.vue` | `expectNoLearnerWorkspaceBlocks` |
| Formateur | `/app/trainer/chat` | `/app/trainer/chat/:sessionId` | `ProdTrainerChatWorkspace.vue` | `expectNoLearnerWorkspaceBlocks` |

**Obsolète après A+B+C :** ouvrir le chat tuteur via `/app/session/:id?tutor_ctx=1` ou le chat formateur via `/app/session/:id` seul. Les tests doivent utiliser `tutorChatUrl()` et `trainerChatUrl()` (`tests_playwright/helpers.ts`).

Composable partagé `useHugoSessionChat.js` : tests de non-régression apprenant doivent vérifier que posture, synthèse, évaluation et traces restent dans `ProdLearnerWorkspace` uniquement.

### Scénarios E2E prioritaires (cible réelle)

#### Ouverture et reprise session

- **Tuteur — création** : `openTutorWorkspaceCta(page, fx, profileCode)` → URL `/app/tutor/chat/` + query contexte
- **Tuteur — reprise** : navigation directe `tutorChatUrl(sessionId, fx, profileCode)`
- **Formateur — création** : login TRAINER → `/app/trainer/chat` → sélection profil formateur → nouvelle session → `/app/trainer/chat/:id`
- **Formateur — reprise** : `trainerChatUrl(sessionId)` depuis la liste sessions home

#### Zéro bloc legacy apprenant

Sur **chaque** test tuteur/formateur en session active, appeler :

```typescript
await expectNoLearnerWorkspaceBlocks(page)
```

Vérifie : pas de `session-posture-badge`, pas de bouton synthèse/évaluation, pas de `.prod-quest-card`.

#### Boutons métier persona

- **Tuteur** : barre import fixe (`tutor-import-toolbar`) — 1 kind par profil ; modale `TutorImportConfirmModal`
- **Formateur** : barre import fixe (`trainer-import-toolbar`) — provisional / explication / justification selon profil
- **Apprenant** : CTA trace, synthèse, évaluation, partage — **absents** des URLs tuteur/formateur

#### Non-régression apprenant

- `test_learner_chat_non_regression_after_tutor_trainer_changes` : `/app/session/:id` — pas de fuite P0 DOM (**2/2 PASS**, 01/07)
- `e2e/cluster16_learner_interface` : panneaux UI v2 + profils display ; wait `/ui-state/` (**8/8 PASS** post-patch 01/07) — voir `addendum_exploration_baseline_B_2026_07_01.md`
- Redirect TUTOR/TRAINER depuis `/app` vers routes dédiées (pas de session apprenant créée par erreur)

#### Décision B — `GET /ui-state/` (doc / tests)

Contract **owner** API, contract **engagement apprenant** produit ; persona `loadUiState: false`. Détail : `addendum_exploration_baseline_B_2026_07_01.md` §3, **R4** §3.

#### Gate Phase TEST (baseline B, `config.settings.dev`)

Avant tout lot front (C) ou persona (Pass 2), exécuter séquentiellement (éviter courses PostgreSQL sur `hugo_poc` / `hugo_poc_test`) :

| Suite | Fichier | Rôle |
|-------|---------|------|
| cluster3_oracles | `apps/hugo/tests/test_cluster3_oracles.py` | Contrat `GET /ui-state/`, pas de fuite P0 |
| cluster16_interface | `apps/hugo/tests/test_cluster16_interface_apprenant_backend.py` | CTA, progression, UIState engagement |
| cluster15_interfaces | `apps/hugo/tests/test_cluster15_interfaces_apprenant.py` | Mémoire, RAG lexical, panneaux |
| tenant_ui_campaign | `apps/accounts/tests/test_tenant_ui_campaign.py` | Multi-tenant UI superadmin |

**Décision :** 4/4 PASS requis pour autoriser Lot C ou extensions persona ; 1 FAIL = STOP.

### Gate Postgres (`config.settings.dev`) — note OPS (2026-07-01)

**Constat :** les ~41 ERROR observées sur une gate parallèle (ex. `test_hugo_poc` / `hugo_poc_test`) relèvent de **l’infra** (`DuplicateDatabase`, `ObjectInUse`), pas de régressions fonctionnelles. Relance **séquentielle** de `test_cluster3_oracles.py` → **5/5 PASS** (juillet 2026).

**Recommandation :**

- exécuter les suites Postgres critiques dans **une seule commande pytest** (pas de workers parallèles sur la même DB de test) ;
- si la DB de test est sale : `dropdb hugo_poc_test` puis `createdb hugo_poc_test` (ou équivalent local) avant rejoue.

```bash
cd hugo_back
# optionnel — nettoyer la DB de test
dropdb hugo_poc_test 2>/dev/null; createdb hugo_poc_test

DJANGO_SETTINGS_MODULE=config.settings.dev .venv/bin/python -m pytest \
  apps/hugo/tests/test_cluster3_oracles.py \
  apps/hugo/tests/test_cluster16_interface_apprenant_backend.py \
  apps/hugo/tests/test_cluster15_interfaces_apprenant.py \
  apps/accounts/tests/test_tenant_ui_campaign.py \
  --tb=short -q
```

**Tag :** erreurs de parallélisme = **infra** ; ne pas les interpréter comme FAIL métier sans relance séquentielle.

### Persona admin — schéma sqlite vs Postgres (2026-07-01)

| Contexte | Mécanisme |
|----------|-----------|
| **Postgres / dev** | migration Django `0022_persona_conversation_profile.py` (`persona_scope`, table `persona_conversation_profile`, FK session) |
| **sqlite_test** | `MIGRATION_MODULES` désactivé → patch idempotent `ensure_sqlite_persona_schema` via `run_local_hugo.sh` (`apps/hugo/services/sqlite_schema_patches.py`) |

**État vérifié (baseline B) :**

- `POST /hugo/persona-conversation-profiles/` → **201**
- `POST .../preview-render/` → **200**
- `apps/hugo/tests/test_persona_conversation_pass2.py` → **PASS** (dont `test_ensure_sqlite_persona_schema_recreates_missing_persona_table`)

**Bordure OPS :** toute nouvelle colonne/modèle sur `sqlite_test` doit avoir un patch sqlite idempotent **en plus** de la migration Postgres ; ne pas s’appuyer sur `migrate` seul sur une `test.sqlite3` réutilisée.

### INC-02 — ACL formateur dashboard learners (inchangé)

**Écart produit ouvert** (voir `memo_cto_2026-06-30.md`, R2/R5/R6) : `GET /dashboard/groups/{id}/learners/` → `{"learners": []}` pour `TRAINER` sans `TutorLearnerLink`, malgré les memberships groupe.

- **Pas de patch code** tant qu’aucune décision CTO (options A/B/C du memo) n’est tranchée.
- Les tests figent l’état présent : `test_trainer_dashboard_group_learners_inc02_current_behavior`, `test_trainer_dashboard_learners_empty_without_tutor_link`.
- Toute évolution ACL formateur = ADR + mise à jour explicite de ces tests.

---

## Sources mobilisées

- `R0_README_ACTUALISATION_ET_MODE_D_EMPLOI.md`
- `R1_ETAT_REEL_ACTUALISE.md`
- `R2_CARTOGRAPHIE_FONCTIONNELLE_ACTUALISEE.md`
- `R3_ARCHITECTURE_ET_PIPELINES_ACTUALISES.md`
- `R4_CONTRATS_ET_PREUVES_RUNTIME.md`
- `modelisation_activite_tuteur.md`
- `spec_reconfiguration_chats_tuteur_formateur.md`
- `addendum_front_chats_lots_ABC_2026_07_01.md`
- `P1_plan_chat_tuteur.md`
- documents P1 formateur et P1 tuteur validés dans le fil

## Réel confirmé

- Baseline de travail : **B** uniquement (front 1.8 + `hugo_back` local). Le pipeline actif par défaut est **P0 legacy** ; la branche v17 ne doit pas être supposée active sans flag explicite.[file:5]
- Le contrat `GET /ui-state/` repose sur `build_contract_ui_state`, distinct des payloads tour `POST`/`SSE` construits par `build_ui_state`.[file:5][file:7]
- `GET /memory-summary/` expose une mémoire calculée et attachée à la session, mais cette mémoire n’est pas injectée dans le prompt LLM du tour.[file:5][file:7]
- Le RAG observé dans le chemin actif est lexical uniquement ; aucune sélection vectorielle n’est prouvée dans le runtime actif.[file:5]
- Les surfaces tuteur (`/app/tutor`, `/app/tutor/chat/:id`) et formateur (`/app/trainer/chat`, `/app/trainer/chat/:id`) sont **REL OBSERV** en baseline B locale après lots A+B+C ; les profils et prompts restent configurables côté admin/superadmin de manière partielle en local.[file:5][file:7]

## Cible de ce plan

Valider de bout en bout, côté utilisateur, front, backend et administration, la reconfiguration des chats tuteur et formateur cadrée ce matin, sans régression sur le chat apprenant, sans modification de la chaîne d’évaluation, sans nouvelle ACL, et sans persistance durable nouvelle pour les brouillons tutoraux P1.[file:5][file:7]

## Principes de test

- Tous les tests sont écrits et exécutés en **baseline B**.
- Les assertions doivent toujours distinguer explicitement :
  - `GET /ui-state/` / `build_contract_ui_state`
  - payloads tour `POST`/`SSE` / `build_ui_state`
- Les tests mémoire doivent vérifier l’absence d’injection mémoire dans le prompt et l’absence de verbatim brut dans `memory-summary`.[file:5][file:7]
- Les tests RAG doivent rester compatibles avec un RAG lexical uniquement.[file:5]
- Les tests tuteur et formateur ne doivent jamais casser les parcours apprenant existants.[file:5][file:7]

## Matrice générale

| Couche | Objectif | Outils | Résultat attendu |
|---|---|---|---|
| Fixtures / seeds | Préparer organisation, rôles, groupes, profils, sessions | bootstrap + fixtures pytest | Données de référence stables |
| Backend API | Vérifier routes, ACL, contrats, résolution profils | pytest Django/DRF | Contrats et permissions conformes |
| Front unitaire | Vérifier labels, composants, imports, rendering | Vitest/Jest | UI cohérente par rôle |
| E2E Playwright | Vérifier les parcours utilisateurs bout en bout | Playwright | Parcours tuteur, formateur, admin, apprenant PASS |
| Audit transversal | Vérifier isolement des prompts, non-régression, sécurité | scripts + assertions ciblées | Aucun bleed inter-chat |

## Fixtures de référence

Créer une fixture commune `morning_reconf_baseline_B` contenant :

- 1 organisation active ;
- 1 superadmin, 1 orgadmin, 1 trainer, 1 tutor, 1 learner, 1 coordo ;
- 1 groupe relié aux bons memberships ;
- 1 `TutorLearnerLink` valide ;
- 2 ou 3 sessions apprenant avec timeline, traces, mémoire et documents ;
- les profils tuteur P1 `tutor_workspace_prep`, `tutor_workspace_diagnostic`, `tutor_workspace_coreflex`, `tutor_workspace_journal` ;
- les profils / policies formateur utiles au lot ;
- un cas avec verbatim non partagé et un cas avec partage autorisé.[file:5][file:7]

## Suite backend — pytest

### Configuration admin et profils

Créer ou compléter :

- `test_superadmin_can_list_conduct_profiles`
- `test_superadmin_can_edit_tutor_prompt_profiles`
- `test_superadmin_can_edit_trainer_related_profiles`
- `test_tutor_workspace_profiles_bootstrap_exist`
- `test_tutor_workspace_profile_resolves_prompt_and_conduct`
- `test_trainer_profiles_do_not_override_tutor_profiles`
- `test_learner_profiles_do_not_override_tutor_or_trainer_profiles`

Attendus : résolution par session, cloisonnement des profils, absence de bleed entre chats.[file:5][file:7]

### ACL tuteur

Créer ou compléter :

- `test_tutor_can_get_group_learners_when_linked`
- `test_tutor_cannot_get_unlinked_learner_timeline`
- `test_tutor_timeline_filters_unshared_verbatim`
- `test_tutor_can_validate_trace_on_authorized_learner`
- `test_tutor_cannot_validate_trace_outside_scope`

Attendus : visibilité limitée au périmètre lié, aucun verbatim non partagé, validation de trace inchangée.[file:5]

### ACL formateur et base connaissances

Créer ou compléter :

- `test_trainer_knowledge_item_crud`
- `test_trainer_elicitation_routes_work`
- `test_trainer_group_context_panel_payload_contains_memberships`
- `test_trainer_dashboard_group_learners_inc02_current_behavior`

Attendus : la base connaissances et l’élicitation restent fonctionnelles ; le comportement actuel INC-02 est figé comme comportement observé, non réécrit implicitement.[file:5]

### Sessions, UIState, mémoire

Créer ou compléter :

- `test_get_ui_state_uses_contract_builder_fields_only`
- `test_post_turn_payload_ui_state_differs_from_get_ui_state`
- `test_memory_summary_contains_sessionmemory_without_prompt_injection`
- `test_memory_summary_contains_no_raw_verbatim`
- `test_set_posture_updates_session_without_cross_chat_effect`

Attendus : distinction stricte des deux UIState, mémoire lecture seule, aucun effet inter-chat.[file:5][file:7]

### Chat tuteur P1

Créer ou compléter :

- `test_tutor_session_can_be_created_with_tutor_workspace_prep`
- `test_tutor_session_can_be_created_with_tutor_workspace_diagnostic`
- `test_tutor_session_can_be_created_with_tutor_workspace_coreflex`
- `test_tutor_session_can_be_created_with_tutor_workspace_journal`
- `test_tutor_import_draft_stays_non_persistent_in_p1`
- `test_tutor_memory_panel_is_read_only`
- `test_tutor_session_does_not_trigger_evaluation_chain`

Attendus : la création de session tuteur et les brouillons P1 fonctionnent sans déclencher ni modifier la chaîne évaluation.[file:7]

### Chat formateur P1

Créer ou compléter :

- `test_trainer_chat_session_uses_trainer_profile_not_learner_profile`
- `test_trainer_import_flow_requires_human_confirmation`
- `test_trainer_import_meta_payload_matches_contract`
- `test_trainer_document_actions_do_not_break_chat_session`

### Contrats et non-régression

Créer ou compléter :

- `test_contract_ui_state_fields_stable`
- `test_contract_memory_summary_fields_stable`
- `test_contract_conduct_profiles_crud_stable`
- `test_contract_profile_resolution_no_cross_role_bleed`
- `test_no_prompt_bleed_tutor_to_trainer_or_learner`
- `test_no_prompt_bleed_trainer_to_tutor_or_learner`
- `test_no_prompt_bleed_learner_to_tutor_or_trainer`
- `test_tutor_never_receives_unshared_verbatim`
- `test_memory_summary_has_no_raw_message_content`
- `test_trainer_cannot_access_tutor_private_drafts_if_p1_non_persistent`
- `test_share_endpoint_behavior_unchanged`

## Suite front — tests unitaires

Créer ou compléter :

- `tutorUiLabels.spec`
- `trainerUiLabels.spec`
- `roleAwareTopbarLabels.spec`
- `tutorNavigation.spec`
- `trainerNavigation.spec`
- `TutorWorkspaceProfileSelector.spec`
- `TrainerWorkspaceProfileSelector.spec`
- `TutorImportConfirmModal.spec`
- `TrainerImportConfirmModal.spec`
- `TutorDraftArtifactsPanel.spec`
- `MemorySummaryPanelReadOnly.spec`
- `tutorChatImport.spec`
- `trainerChatImport.spec`
- `sessionProfileResolution.spec`
- `roleScopedPromptConfig.spec`

Attendus : labels corrects par rôle, navigation cohérente, imports corrects, rendu lecture seule mémoire, aucun partage de configuration inter-rôle.[file:5]

## Suite E2E — Playwright

### Admin / superadmin

Créer ou compléter :

- `test_superadmin_edit_tutor_prompt_is_scoped.spec.ts`
- `test_superadmin_edit_trainer_prompt_is_scoped.spec.ts`
- `test_admin_profiles_list_and_filter_by_role.spec.ts`

Attendus : un changement admin sur un prompt tuteur n’impacte pas trainer/apprenant, et réciproquement.[file:5][file:7]

### Formateur

Créer ou compléter :

- `test_smoke_trainer_workspace_labels.spec.ts`
- `test_trainer_elicitation_to_chat_flow.spec.ts`
- `test_trainer_import_confirm_flow.spec.ts`
- `test_trainer_knowledge_validation_non_regression.spec.ts`

### Tuteur

Créer ou compléter :

- `test_smoke_tutor_workspace_labels.spec.ts`
- `test_tutor_prep_flow.spec.ts`
- `test_tutor_diagnostic_flow.spec.ts`
- `test_tutor_coreflex_flow.spec.ts`
- `test_tutor_journal_flow.spec.ts`
- `test_tutor_memory_readonly_panel.spec.ts`
- `test_tutor_reload_no_durable_draft.spec.ts`

### Apprenant non-régression

Créer ou compléter :

- `test_learner_chat_non_regression_after_tutor_trainer_changes.spec.ts`
- `test_learner_evaluation_chain_non_regression.spec.ts`

Attendus : aucun impact sur les parcours apprenant, les CTA d’évaluation/synthèse et la posture conversationnelle.[file:5][file:7]

## Audit transversal

Prévoir un mini-audit automatisé final qui vérifie :

- le cloisonnement des prompts par rôle et par session ;
- la stabilité des contrats `ui-state` et `memory-summary` ;
- l’absence de verbatim brut dans les surfaces tuteur ;
- la non-régression du workflow formateur base documentaire ;
- la non-régression du workflow apprenant ;
- l’absence de persistance durable nouvelle pour les brouillons tuteur P1.[file:5][file:7]

## Critères d’acceptation

Le chantier est validé si :

- tous les tests P1 tuteur et P1 formateur passent en baseline B ;
- les parcours apprenant restent PASS ;
- les prompts restent isolés par session/profil ;
- `memory-summary` reste lecture seule et non injectée ;
- le RAG reste lexical ;
- aucune nouvelle ACL ni nouvelle chaîne d’évaluation n’ont été introduites ;
- les brouillons tuteur P1 ne sont pas présentés comme persistés durablement.[file:5][file:7]

## Commandes de lancement recommandées

### Backend

- `./scripts/run_pytest_local.sh`
- ou ciblé : `pytest -k "tutor or trainer or conduct_profiles or memory_summary or ui_state"`

### Front unit

- commande habituelle du front pour les tests unitaires (`vitest`, `npm test`, ou équivalent selon le workspace)

### Playwright

- Prérequis baseline B : `hugo_back` sur `:8000` (`run_local_hugo.sh` ou `runserver` sqlite_test) + Vite `:5173` (démarré par `playwright.config.ts` si absent).
- lancer d’abord les smoke tuteur/formateur sur routes dédiées (`/app/tutor/chat/*`, `/app/trainer/chat/*`) ;
- vérifier `expectNoLearnerWorkspaceBlocks` sur chaque parcours persona ;
- puis la non-régression apprenant sur `/app/session/:id` ;
- enfin la suite admin/superadmin.

## À VÉRIFIER

- parité Encoors non incluse dans ce plan ; elle reste hors scope tant qu’aucun oracle authentifié récent n’est rejoué.[file:7]
- comportement exact des surfaces admin conversation profils / orchestrateurs selon la branche courante du front.[file:5]
- support backend éventuel pour une persistance légère future des brouillons tuteur, explicitement hors P1 actuel.

## Prochaine sortie utile

Utiliser ce plan comme cahier de charge pour un lot Cursor dédié “tests automatisés tuteur/formateur P1”, puis produire un audit PASS/FAIL avec les trous restants et les points à recalibrer.[file:5][file:7]
