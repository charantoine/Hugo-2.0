# Rapport d'audit Hugo 1.9

Date: 2026-05-19

Perimetre audite:
- depot `C:\hugo`
- etat du working tree courant
- branche courante observee: `hugolucia`
- fronts examines: `frontend_1.8` en priorite, `frontend` en comparaison

Statuts utilises:
- `conforme`
- `non conforme`
- `partiel`
- `non observable`
- `hors perimetre documentaire`
- `a arbitrer`

Types d'enonces utilises:
- `spec explicite`
- `spec implicite raisonnable`
- `consigne contextuelle du fil`
- `interpretation prudente`

## 1. Sources et hierarchie

### Tableau sources / priorites / hierarchie

| Source | Niveau hierarchique | Zone couverte | Ce que la source fixe vraiment | Ce qu'elle ne fixe pas | Priorite de lecture |
|---|---:|---|---|---|---|
| `SPEC_POC_v1.5.md` | 1 | produit, roles, RLS, endpoints MVP, doctrine, tests minimaux | doctrine multi-tenant, comptes manuels POC, roles, confidentialite, stack Django/DRF, `TutorPrompt`, endpoints MVP, RLS `app.organisation_id` | le detail fin des lots 0 a 6, la branche front ergonomique exacte, les ecrans admin produits exhaustifs | critique |
| `SPEC Hugo 1.6.2 – Noyau d'etat prioritaire et decision conversationnelle.md` | 2 de fait dans le depot | doctrine comportementale, P0, decision locale | gel conceptuel P0, priorites de regulation, variables P0, decision locale, guardrails cognitifs/relationnels | la sequence d'implementation lotisee 1.9, le detail UI LOT2, les ecrans admin | critique |
| `specs_old-1.9/README_CURSOR(3).md` | 3 | decoupage lots 0 a 6 | sequence stricte des lots, invariants d'implementation, fichiers attendus, checkpoints inter-lots | l'etat reel livre, la branche front de reference au sens du fil | tres haute |
| `specs_old-1.9/LOT0...md` a `LOT6...md` | 4 | exigences lot par lot | contrats cibles, endpoints, tests, migrations, posture, memoire, base trainer, analytics | l'integration effective, la visibilite UI reelle, la priorite entre conflits documentaires | tres haute |
| `specs/README_PACK_CURSOR.md` | 6 | cadre d'audit | ordre de lecture, hiérarchie de decision, livrables attendus, rappel d'attention maximale front | ne remplace pas la spec racine ni les lots | haute |
| `specs/CONTEXTUALISATION_COMPLETE_HUGO_1_9.md` | 6 | consolidation d'intention produit | intention 1.9, qualification des enonces, rappel de la consigne de branche ergonomique, articulation lots/spec/code | ne peut pas ecraser la spec racine | haute |
| `specs/HORS_PERIMETRE_GAPS_ROADMAP.md` | 6 | zones a ne pas surinterpreter | hors perimetre, gaps comptes/admin, qualification "a arbitrer" ou "consigne du fil" | ne rend pas obligatoires des fonctions absentes des sources hautes | haute |
| code, branches, migrations, tests, UI | 5 | etat reel implemente | ce qui est reellement present, branche, observable, branche, execute, expose | ne fixe pas seul la conformite spec | critique |
| `specs-old-1.8/Hugo 1.8 – branche prod montrable V1.md` et docs 1.8 associees | source secondaire utile | base ergonomique / prod_showable | split `tester` / `prod_showable`, existence d'une variante montrable | ne vaut pas a elle seule spec explicite des lots 1.9 | moyenne |

### Ambiguites documentaires constatees

| Point | Qualification | Effet sur l'audit |
|---|---|---|
| La mention `SPEC POC v1.5 update 27/03/2026` n'est pas attestee telle quelle dans le fichier | `a arbitrer` | l'audit s'appuie sur `SPEC_POC_v1.5.md` present dans le depot |
| Le document nomme exactement `Hugo 1.6 Cadrage Transformation du comportement` est absent du depot | `non observable` | le cadrage 1.6.2 a ete utilise comme meilleur substitut documentaire disponible |
| La contrainte "brancher les changements front sur la branche deja ergonomiquement montrable" n'est pas formalisée dans les lots eux-memes | `consigne contextuelle du fil` | elle reste un critere d'audit valide mais pas une spec explicite lot par lot |
| Les lots 1.9 documentent un front React/JSX sous `frontend/src/hugo/*` alors que le code reel divergent est en Vue dans `frontend_1.8` | `tension documentaire a qualifier` | l'audit regarde l'equivalence fonctionnelle et la realite du branchement, pas l'alignement literal des chemins |

### Regles de decision retenues pour cet audit

1. La spec racine et le cadrage P0 priment sur les documents consolides.
2. Les lots sont lus en sequence et jamais isoles.
3. Un element n'est dit "implemente" que s'il est present, branche et observable.
4. Toute demande du fil non ecrite dans les sources hautes est etiquetee `consigne contextuelle du fil`.
5. Toute zone insuffisamment balisee est classee `a arbitrer` ou `hors perimetre documentaire`.

## 2. Base de decision documentaire exhaustive

| ID | Theme | Formulation consolidee | Verbatim utile | Source principale | Sources secondaires | Type | Impact back | Impact front | Methode d'audit associee |
|---|---|---|---|---|---|---|---|---|---|
| DOC-001 | Multi-tenant | Toutes les tables metier doivent etre scopees tenant et la transaction doit poser `SET LOCAL app.organisation_id` | `SET LOCAL app.organisation_id` | `SPEC_POC_v1.5.md` | `.cursorrules`, `README_CURSOR(3).md` | spec explicite | modele, middleware, RLS, tests cross-tenant | aucun effet securite ne doit reposer sur l'UI | lire middleware, migrations, tests RLS |
| DOC-002 | Comptes POC | Les comptes sont crees manuellement dans le POC, sans invitations email | `Comptes: creation manuelle` | `SPEC_POC_v1.5.md` | `CONTEXTUALISATION_COMPLETE_HUGO_1_9.md` | spec explicite | bootstrap CLI, Django admin, endpoints admin/users | ecrans de creation possibles mais pas obligatoirement riches | cartographier commandes, endpoints, UI |
| DOC-003 | Doctrine Hugo | Hugo reste un moteur de regulation tutorale pilote par etat, pas un simple prompt | `moteur de regulation tutorale pilote par etat` | `SPEC Hugo 1.6.2...md` | `SPEC_POC_v1.5.md` | spec explicite | orchestrateur, decision, TutorPrompt | l'UI ne doit pas recalculer la pedagogie | lire orchestrateur, decision engine, front adapters |
| DOC-004 | Gel P0 | Les champs P0 existants ne doivent pas etre modifies directement et l'orchestrateur/prompt renderer ne doivent recevoir que des patches additifs | `Aucun champ P0 modifie` | `README_CURSOR(3).md` | `CHECKLIST_AUDIT_BACKEND.md` | spec explicite | `turn_state_v17.py`, `decision_engine_v17.py`, orchestrateur, prompt renderer | aucun | comparer contrats, tests NR, structure runtime |
| DOC-005 | Enums canoniques | `ConversationPosture`, `SessionMaturityLevel`, `KnowledgeItemStatus` doivent avoir une source canonique unique dans `conversation_profile.py` | `source de verite unique des enums` | `README_CURSOR(3).md` | `LOT0` | spec explicite | imports, models, tests | coherence des labels derives | lire `conversation_profile.py` et tests NR |
| DOC-006 | UIState | `UIState` doit etre un contrat produit, sans exposition de champs P0 bruts | `UIState ne doit jamais exposer un champ P0 brut` | `LOT0` | `CHECKLIST_AUDIT_BACKEND.md`, `CHECKLIST_AUDIT_FRONTEND.md` | spec explicite | endpoint `/ui-state`, adaptateur | l'ecran ne doit pas lire les signaux P0 bruts | lire dataclass, endpoint, adaptateur front |
| DOC-007 | Progression conversationnelle | `ConversationProgress` doit etre calcule apres la decision, persiste en JSONB et deserialise explicitement | `never use ConversationProgress(**raw)` | `LOT1` | `README_CURSOR(3).md` | spec explicite | calculateur, persistance, endpoints `/progress` et `/ui-state` | la progression visible doit venir de ce contrat ou d'un derive equivalent | lire calculateur, orchestrateur, tests endpoints |
| DOC-008 | Front LOT2 | LOT2 doit rendre visible la progression produit et ne pas laisser le front calculer la pedagogie | `Le front ne calcule rien` | `LOT2` | `CONTEXTUALISATION_COMPLETE_HUGO_1_9.md` | spec explicite | fournir `/ui-state`, endpoints synthese/evaluation | panneau visible, actions branchees, pas de P0 brut | lire `frontend_1.8`, routes, adaptateur, reseau |
| DOC-009 | Branche ergonomique | Les changements front de cette serie devaient etre appliques sur la branche deja ameliorée ergonomiquement et montrable | `branche deja retravaillee ergonomiquement` | `CONTEXTUALISATION_COMPLETE_HUGO_1_9.md` | `PROMPT_CURSOR_AUDIT_LONG.md` | consigne contextuelle du fil | faible | critique sur la base front auditee | comparer branches `main` / `hugolucia` et `frontend` / `frontend_1.8` |
| DOC-010 | Postures LOT3 | Les trois postures explicites et leurs transitions doivent exister et passer avant P0 sans le casser | `DIAGNOSTIC`, `REFLECTIVE_AFEST`, `KNOWLEDGE_REVIEW` | `LOT3` | `CHECKLIST_AUDIT_BACKEND.md` | spec explicite | posture selector, transitions, prompt renderer, endpoint `set-posture` | eventuelle lecture/changement posture si expose | lire services et tests LOT3 |
| DOC-011 | Synthese / evaluation | La synthese et l'evaluation doivent etre reelles, conditionnees par l'eligibilite et reliees a `synthesisservice.py` | `request-synthesis`, `request-evaluation` | `LOT3` | `CHECKLIST_AUDIT_FRONTEND.md` | spec explicite | endpoint, service, orchestration | boutons visibles et fonctionnels quand pertinents | lire endpoints, chercher service, verifier UI |
| DOC-012 | Memoire thematique | La memoire inter-session doit etre thematique, post-conversation, sans verbatim brut et sans auto-upgrade de `derived_provisional` | `post-conversation uniquement` | `LOT4` | `CHECKLIST_AUDIT_BACKEND.md` | spec explicite | modele, consolidator, feature flag, injection contexte | eventuelle exposition via `memory-summary` seulement | lire modele, consolidator, orchestrateur, tests |
| DOC-013 | Base de connaissance formateur | `TrainerKnowledgeItem` et sa validation humaine doivent exister; l'UI trainer peut etre absente mais doit alors etre signalee | `validation humaine obligatoire` | `LOT5` | `HORS_PERIMETRE_GAPS_ROADMAP.md` | spec explicite + qualification de perimetre | modele, ingestion, endpoints trainer | UI trainer a cartographier si presente | lire models, services, routes, front |
| DOC-014 | Observabilite cohorte | Les signaux qualite/cohorte doivent etre produits sans verbatim brut et etre consommables par analytics | `ConversationQualitySignal` | `LOT6` | `CHECKLIST_AUDIT_BACKEND.md` | spec explicite | quality tracker, analytics, tests | pas d'exposition brute sensible | lire modeles, service, dashboard, tests |
| DOC-015 | Roles/admin | ORGADMIN administre users, groups et exports; SUPERADMIN est une administration technique globale qui ne doit pas devenir un acces metier libre | `ORGADMIN peut administrer users, groups et exports` | `SPEC_POC_v1.5.md` | `CONTEXTUALISATION_COMPLETE_HUGO_1_9.md`, `HORS_PERIMETRE_GAPS_ROADMAP.md` | spec explicite + gaps documentaires | permissions, endpoints, bootstrap, Django admin | ecrans admin ou absence a signaler | lire accounts/referentials/front admin |

## 3. Matrice de criteres auditables

| ID | Intitule court | Nature | Source | Methode de verification | Preuve attendue | Resultat observe | Statut | Criticite |
|---|---|---|---|---|---|---|---|---|
| CRIT-001 | RLS transactionnel `app.organisation_id` | securite | DOC-001 | lire middleware et tests | middleware + test cross-tenant | `TenantRLSMiddleware` pose `SET LOCAL app.organisation_id`; test cross-tenant existe | partiel | bloquant |
| CRIT-002 | Isolation cross-tenant executee | securite/tests | DOC-001 | executer `tests/test_cross_tenant.py` | test vert sous Postgres | sous SQLite: un test bloque car `SET LOCAL` n'existe pas; un autre retourne `403` au lieu de `404`; sous Postgres non observable localement car pas de service 5432 | non observable | bloquant |
| CRIT-003 | Gel P0 direct | backend | DOC-004 | lecture structurelle + historique dispo | absence de modif directe prouvable | fichiers P0 presents mais l'historique n'est pas suffisamment audite ici pour affirmer "non modifies" | a arbitrer | majeur |
| CRIT-004 | Enums canoniques | backend | DOC-005 | lire code + test NR | imports canoniques + test | `conversation_profile.py` porte les enums; `test_enums_are_imported_from_canonical_module` passe | conforme | majeur |
| CRIT-005 | UIState sans P0 brut | backend/front | DOC-006 | lire dataclass + test NR + adapter front | contrat propre + test vert | dataclass propre; test NR vert; fallback front continue toutefois a lire `turn_state` | partiel | majeur |
| CRIT-006 | Deserialisation explicite JSONB | backend | DOC-007 | lire `conversation_profile.py`, calculateur, endpoints | fonction explicite utilisee partout | `deserialize_conversation_progress()` existe et est utilisee | conforme | majeur |
| CRIT-007 | Endpoint `/progress` coherent | API | DOC-007 | test endpoint | JSON coherent | test endpoint passe | conforme | majeur |
| CRIT-008 | Endpoint `/ui-state` coherent | API/front | DOC-006/DOC-008 | test endpoint + front | JSON produit + consommation front | backend renvoie un contrat coherent; frontend courant le charge au chargement de session | conforme | majeur |
| CRIT-009 | Front ne lit que `/ui-state` | frontend | DOC-008 | lire `engagementUiModel.js` | aucune heuristique pedagogique locale | le front charge `/ui-state` mais garde un fallback complet sur `turn_state` et `conversation_decision` | non conforme | bloquant |
| CRIT-010 | Panneau progression visible et branche | UX/frontend | DOC-008 | lire composant + routes + UI | panneau visible en parcours montrable | progression/scenes/quetes visibles dans `ProdLearnerWorkspace.vue` | conforme | majeur |
| CRIT-011 | Synthese visible et branchee | frontend/API | DOC-011 | lire vues + routes + endpoints | boutons + appels reseau | endpoint backend existe mais aucun bouton ni appel front trouves | non conforme | majeur |
| CRIT-012 | Evaluation visible et branchee | frontend/API | DOC-011 | idem | boutons + appels reseau | endpoint backend existe mais aucun bouton ni appel front trouves | non conforme | majeur |
| CRIT-013 | `set-posture` reel | API/backend | DOC-010 | tests LOT3 + route | endpoint + transitions | route presente; test API passe | conforme | majeur |
| CRIT-014 | `synthesisservice.py` reel | backend | DOC-011 | recherche fichier/service | service present et branche | aucun `synthesis_service.py` observe; endpoints renvoient `*_queued` seulement | non conforme | majeur |
| CRIT-015 | Memoire thematique post-conversation | backend | DOC-012 | lire modele + tests + points d'appel | consolidation appelee fin de conversation | modele, tests et `memory-summary` presents; appel reel seulement dans `GenerateTraceView`, pas dans le flux normal | partiel | majeur |
| CRIT-016 | Injection memoire dans le contexte | backend | DOC-012 | lire orchestrateur/settings | feature flag + injection | aucune injection `LearnerThemeMemory` ni feature flag explicite constatee | non conforme | majeur |
| CRIT-017 | Validation humaine trainer knowledge | backend | DOC-013 | lire endpoints + test | validate/reject/edit + test | present; test passe | conforme | majeur |
| CRIT-018 | UI trainer de co-construction | frontend | DOC-013 | lire routes/front | vue ou absence qualifiee | endpoints trainer presents, aucune UI trainer dediee reperee | partiel | mineur |
| CRIT-019 | Signaux qualite/cohorte | backend | DOC-014 | lire modeles/tests + point d'appel | modeles, service, analytics, tests | modeles et tests presents; production complete surtout lors de `generate-trace` | partiel | majeur |
| CRIT-020 | ORGADMIN admin users/groups/exports | roles/admin | DOC-015 | lire permissions/endpoints/UI | capacites reelles scopees | users/groups/prompts/OVH visibles; exports aussi, mais certaines permissions sont trop larges et l'UI users est limitee | partiel | majeur |
| CRIT-021 | SUPERADMIN technique non metier | roles/admin | DOC-015 | lire API/Django admin/front | capacites techniques identifiables sans UI metier libre | pas d'UI produit dediee; Django admin et endpoints org existent; pas d'API front cross-org complete | partiel | mineur |
| CRIT-022 | Branche front ergonomique correcte | frontend/methode | DOC-009 | comparer `main`, `hugolucia`, `frontend`, `frontend_1.8` | travaux sur base montrable | `frontend_1.8` est clairement la variante prod_showable; pas de branche nommee distinctement pour la base ergonomique du fil | partiel | ambigu |
| CRIT-023 | Tests executables front | tests | plan de tests + repo | lancer tests front | tests verts | `npm test` dans `frontend_1.8` passe: 14/14 | conforme | majeur |
| CRIT-024 | Tests executables backend | tests | plan de tests + repo | lancer tests cibles | tests verts ou blocages qualifies | 19/21 verts sous SQLite; RLS/404 restent a confirmer sous Postgres non disponible localement | partiel | majeur |
| CRIT-025 | Chromium / Playwright | tests/UX | plan de tests | rechercher config puis executer | suite e2e ou campagne manuelle outillee | aucune config Playwright versionnee; campagne Chromium seulement documentee | non conforme | majeur |

## 4. Rapport backend

### 4.1 Dataclasses et enums canoniques

Constat:
- `backend/apps/hugo/domain/conversation_profile.py` contient bien `ConversationPosture`, `SessionMaturityLevel`, `KnowledgeItemStatus`, `ConversationBranch`, `ConversationProgress`, `UIState`.
- Les enums sont serialisees en `.value` via `to_dict()`.
- `deserialize_conversation_progress()` et `deserialize_ui_state()` recastent explicitement les enums.

Conclusion:
- conforme sur la canonicalisation des enums et la deserialisation JSONB.

### 4.2 Respect du gel P0

Constat:
- les fichiers P0 attendus existent, notamment `turn_state_v17.py` et `decision_engine_v17.py`.
- le flux principal observable du repo passe encore majoritairement par le chemin non-v17, avec un flag `HUGO_P0_V17_ENABLED`.
- sans audit git plus profond, l'affirmation "aucun champ P0 modifie directement" n'est pas prouvable a 100 % dans ce rapport.

Conclusion:
- `a arbitrer` sur le gel historique strict.
- le repo montre toutefois une intention additive credible autour de l'orchestrateur et du renderer.

### 4.3 Migrations et modeles ajoutes

Constats principaux:
- `conversation_progress` est persiste sur `HugoSession`.
- `LearnerThemeMemory`, `TrainerKnowledgeItem`, `ConversationQualitySignal` sont presents.
- les champs sont scopes organisationnellement via `organisation` / `organisation_id`.

Conclusion:
- conforme sur la presence des modeles et des migrations attendues.

### 4.4 Endpoints nouveaux ou modifies

Endpoints observes dans `backend/apps/hugo/urls.py`:
- `/sessions/<id>/progress/`
- `/sessions/<id>/ui-state/`
- `/sessions/<id>/set-posture/`
- `/sessions/<id>/request-synthesis/`
- `/sessions/<id>/request-evaluation/`
- `/sessions/<id>/memory-summary/`
- routes trainer et analytics

Conclusion:
- conforme sur la presence de la surface API cible.
- partiel sur la profondeur fonctionnelle reelle de synthese/evaluation.

### 4.5 Deserialisation JSONB

Constat:
- le contrat `ConversationProgress` utilise une deserialisation explicite.
- les tests `test_deserialize_conversation_progress_recovers_enums` et l'endpoint `/progress` confirment le comportement.

Conclusion:
- conforme.

### 4.6 Stockage canonique des enums `.value`

Constat:
- `ConversationProgress.to_dict()` et `UIState.to_dict()` serialisent les enums en `.value`.
- `KnowledgeItemStatus` est stocke en `.value` dans la memoire et la base trainer.

Conclusion:
- conforme.

### 4.7 Memoire thematique post-conversation

Constats:
- `memory_consolidator.py` existe et le test LOT4 passe.
- `normalize_knowledge_status()` existe.
- pas d'auto-upgrade `derived_provisional` vers `validated_trainer`.
- mais `consolidate_session()` n'est appele de maniere visible que dans `GenerateTraceView`, pas dans le flux ordinaire de conversation.
- aucune injection conditionnelle de `LearnerThemeMemory` dans l'orchestrateur n'a ete observee.

Conclusion:
- presence conforme
- branchement reel partiel
- observabilite partielle via `/memory-summary`

### 4.8 Base de connaissance formateur

Constats:
- `TrainerKnowledgeItem` est present.
- `document_ingestor.py` est present.
- questionnaire d'elicitation present via endpoints trainer.
- validation humaine explicite presente et testee.
- pas d'UI trainer dediee observee dans le front actuel.

Conclusion:
- backend globalement conforme
- front et usage produit partiels

### 4.9 Observabilite / analytics

Constats:
- `ConversationQualitySignal`, `quality_tracker.py`, `analytics/cohort_dashboard.py`, `views_analytics.py` existent.
- les tests qualite passent.
- la production complete du snapshot qualite est surtout visible sur `generate-trace`, pas comme un flux post-seance normal systematique.

Conclusion:
- partiel

### 4.10 RLS / `organisation_id`

Constats:
- le middleware pose bien `SET LOCAL app.organisation_id`.
- un test cross-tenant existe.
- l'execution locale sous SQLite ne permet pas d'observer le comportement RLS Postgres.
- le port 5432 local etait indisponible au moment de l'audit.

Conclusion:
- conformite documentaire et structurelle credible
- verification executee partielle seulement

### 4.11 Conformite des tests backend

Commandes executees:

```powershell
cd C:\hugo\backend
$env:DJANGO_SETTINGS_MODULE='config.settings.sqlite_test'
.\venv\Scripts\python.exe -m pytest tests\test_auth.py tests\test_cross_tenant.py apps\hugo\tests\test_p0_non_regression.py apps\hugo\tests\test_conversation_progress.py apps\hugo\tests\test_posture_modes.py apps\hugo\tests\test_memory_consolidation.py apps\hugo\tests\test_trainer_knowledge.py apps\hugo\tests\test_quality_signals.py
```

Resultat:
- 19 tests passes
- 2 echecs
  - un echec attendu sous SQLite pour `SET LOCAL app.organisation_id`
  - un ecart d'assertion `403` observe vs `404` attendu

Tentative Postgres:
- execution bloquee, puis abandonnee proprement
- `Test-NetConnection localhost:5432` => `TcpTestSucceeded: False`

Conclusion:
- bonne couverture logique
- verification RLS Postgres non observable localement pendant l'audit

## 5. Rapport frontend

### 5.1 Branche reellement auditee

Constats:
- branche courante: `hugolucia`
- variante front montrable effective: `frontend_1.8`
- variante legacy/testeur comparee: `frontend`

Conclusion:
- l'audit front porte d'abord sur `frontend_1.8`, ce qui est coherent avec la trajectoire 1.8/1.9 montrable.

### 5.2 Lien avec la branche ergonomique montrable

Constats:
- les docs 1.8 decrivent une separation `tester` / `prod_showable`.
- `frontend_1.8` implemente justement cette separation.
- aucune branche git distincte explicitement nommee comme "base ergonomique" n'a ete retrouvee au-dela de `main` et `hugolucia`.

Conclusion:
- critere partiellement satisfait
- classification: `consigne contextuelle du fil` partiellement respectee, reste `a arbitrer` sur la reference git nominale exacte

### 5.3 Composants crees ou modifies

Composants/fichiers structurants observes:
- `frontend_1.8/src/components/learner/ProdLearnerWorkspace.vue`
- `frontend_1.8/src/utils/engagementUiModel.js`
- `frontend_1.8/src/utils/engagementUiModel.test.js`
- `frontend_1.8/src/utils/messageStream.js`
- layouts `ProdLearnerLayout.vue` et `TesterLayout.vue`

Constat important:
- le repo actuel ne contient pas les chemins React/JSX litteraux du LOT2 (`frontend/src/hugo/progressionLabels.js`, `HugoProgressPanel.jsx`).
- l'equivalent fonctionnel est en Vue dans `frontend_1.8`.

Conclusion:
- equivalent fonctionnel partiel plutot qu'alignement litteral a la documentation LOT2.

### 5.4 Usage effectif de UIState

Constats:
- `ProdLearnerWorkspace.vue` charge bien `/hugo/sessions/{id}/ui-state/` au chargement de la session.
- `engagementUiModel.js` sait adapter ce contrat.
- mais le modele garde un fallback riche sur `turn_state`, `conversation_decision` et des heuristiques derivees.

Conclusion:
- consommation de `/ui-state` reelle
- non conformite au principe LOT2 "le front ne calcule rien"

### 5.5 Integration reelle du panneau de progression

Constats:
- une progression visible de scene est effectivement presente dans `ProdLearnerWorkspace.vue`.
- quetes et objets persistants sont egalement visibles.
- le panneau n'est pas encapsule dans un composant `HugoProgressPanel` dedie.

Conclusion:
- conforme sur la visibilite produit
- partiel sur l'implementation attendue par la doc LOT2

### 5.6 Synthese / evaluation visibles et branchees

Constats:
- backend: endpoints `/request-synthesis/` et `/request-evaluation/` presents.
- frontend: aucun appel a ces endpoints detecte.
- aucun bouton utilisateur completement branche n'a ete identifie dans le parcours montrable.

Conclusion:
- non conforme

### 5.7 Regression ou stagnation visuelle eventuelle

Constats:
- le front montrable n'est pas "quasi inchange": progression, quetes, objets, streaming et variantes sont bien visibles.
- en revanche, la promesse 1.9 d'un produit pilote par `UIState` pur, avec synthese/evaluation branchees, n'est pas atteinte.
- le build/déploiement documente continue de viser `frontend/dist`, pas clairement `frontend_1.8/dist`.

Conclusion:
- pas de stagnation totale
- mais un LOT2 seulement partiellement livre et potentiellement mal aligne entre code, build et documentation

### 5.8 Exposition interdite eventuelle de champs P0

Constats:
- l'ecran apprenant montrable n'affiche pas explicitement les champs P0 bruts.
- le fallback `engagementUiModel.js` lit pourtant `covered_points`, `remaining_open_points`, `episode_clarity`, `can_close_for_now`, etc.
- les vues testeur/tuteur affichent des signaux plus techniques, ce qui est coherent avec leur nature debug/technique.

Conclusion:
- conforme en exposition visuelle apprenant
- non conforme au contrat d'adaptation strict LOT2

### 5.9 Fonctionnement reel en navigation simulee

Observables sans navigateur E2E complet:
- chargement session
- chargement messages
- chargement `/ui-state`
- flux streaming avec fallback non streaming

Non observables faute de campagne Chromium outillee:
- captures d'ecran et reseau role par role
- preuve navigateur sur synthese/evaluation

Conclusion:
- partiel

## 6. Rapport comptes / roles / administration

### 6.1 Qui peut creer quels comptes

Etat reel:
- CLI/bootstrap et Django admin: ORGADMIN / SUPERADMIN, plus creation manuelle viable
- API admin/users: creation de comptes possible
- UI `UsersView.vue`: creation limitee surtout a `LEARNER` et `TUTOR`

Conclusion:
- comptes manuels POC conformes
- back-office comptes complet non livre

### 6.2 Endpoints existants

Presence observee:
- `POST /auth/login/`
- `GET /auth/me/`
- `GET/POST /admin/organisations/`
- `POST /admin/users/`
- `GET/POST /users/`
- `GET/PATCH /groups/{id}/`, `GET/POST /groups/`
- tutor prompts, OVH LLM, trainer knowledge, exports

Conclusion:
- surface backend relativement riche
- namespace exact `admin/groups` absent, mais fonctionnalite couverte via `/groups/`

### 6.3 Ecrans existants

Observe dans `frontend_1.8`:
- `UsersView.vue`
- `GroupsAdminListView.vue`
- `GroupAdminDetailView.vue`
- `TutorPromptsView.vue`
- `OvhLlmView.vue`
- ecrans apprenant montrables

Absents ou non identifies:
- UI produit SUPERADMIN dediee
- UI trainer dediee pour elicitation/validation
- UI metier complete tuteur pour administration des comptes

### 6.4 Ce qui releve de Django admin ou d'une interface technique

Releve surtout de Django admin / technique:
- creation d'organisation
- vision technique globale SUPERADMIN
- edition plus complete des objets users/orgs

Conclusion:
- la surface produit admin existe, mais elle reste partielle et completee par Django admin.

### 6.5 Capacites reelles ORGADMIN

Observe:
- peut lister/creer des users
- peut administrer groupes, prompts, OVH LLM
- peut lancer des exports
- ne dispose pas d'une UI comptes exhaustive ni d'edition/suppression complete des users

Qualification:
- `partiel`

### 6.6 Capacites reelles SUPERADMIN

Observe:
- peut administrer les organisations et comptes globalement via API/Django admin
- aucune UI produit dediee
- pas d'API front cross-org complete type back-office fini

Qualification:
- `partiel`

### 6.7 Existence ou non cote tuteur / formateur

Observe:
- tuteur: dashboard, learners, traces, certaines operations via groupes/liens
- formateur: endpoints trainer presents, UI dediee absente
- rattachements/groupe: presents via `GroupMembership` et `TutorLearnerLink`
- consignes pedagogiques: pilotage surtout via `TutorPrompt`, admin-like

Qualification:
- tuteur: `partiel`
- formateur UI: `absent` / `hors perimetre documentaire` selon le cas d'usage
- gestion metier complete comptes/tuteurs/apprenants/rattachements: `partiellement specifiee` et `partielle` en code

### 6.8 Ecarts spec / code / fil

Ecarts principaux:
- certaines permissions groupes/membres/exports sont plus larges que l'intention "ORGADMIN administre"
- UI users limitee
- pas de UI SUPERADMIN produit
- pas de UI trainer dediee

## 7. Rapport tests API + Chromium

### 7.1 Tests executes

Frontend execute:

```powershell
cd C:\hugo\frontend_1.8
npm test
```

Resultat:
- 14 tests passes / 14

Backend execute:

```powershell
cd C:\hugo\backend
$env:DJANGO_SETTINGS_MODULE='config.settings.sqlite_test'
.\venv\Scripts\python.exe -m pytest tests\test_auth.py tests\test_cross_tenant.py apps\hugo\tests\test_p0_non_regression.py apps\hugo\tests\test_conversation_progress.py apps\hugo\tests\test_posture_modes.py apps\hugo\tests\test_memory_consolidation.py apps\hugo\tests\test_trainer_knowledge.py apps\hugo\tests\test_quality_signals.py
```

Resultat:
- 19 passes
- 2 echecs
  - incompatibilite SQLite / `SET LOCAL app.organisation_id`
  - `403` observe au lieu de `404`

### 7.2 Tests API fonctionnels

Observables via tests existants:
- login / me
- `/progress`
- `/ui-state`
- `set-posture`
- trainer knowledge
- quality signals

Non observes par campagne executee aujourd'hui:
- `request-synthesis`
- `request-evaluation`
- `memory-summary`
- campagne roles/admin complete

### 7.3 Tests d'integration back/front

Partiellement observes:
- adaptateur `engagementUiModel` teste
- consommation de `session ui-state` testee en unit front

Non observes:
- campagne navigateur complete front + backend local aligne

### 7.4 Chromium / Playwright

Constat:
- aucune configuration Playwright versionnee dans le repo
- la campagne Chromium est seulement documentee dans `specs/PLAN_TESTS_API_CHROMIUM.md`

Qualification:
- `non conforme` a l'attendu "si possible executer" en mode automatise
- `non observable` pour les captures et preuves navigateur role par role pendant cet audit

### 7.5 Captures d'ecran et preuves d'execution

Preuves collectees pendant cet audit:
- sorties de commandes de tests
- lecture de code et routes
- lecture des terminaux montrant build Vite reussi pour `frontend_1.8`
- verification reseau locale `localhost:5432` echouee

Preuves non obtenues:
- captures navigateur
- HAR/reseau Chromium
- campagne Playwright

### 7.6 Conclusion sur le lot tests

- bon niveau de preuve unitaire et backend cible
- faible niveau de preuve navigateur
- verification RLS executee incomplète faute service Postgres local disponible pendant l'audit

## 8. Ecarts critiques et recommandations

### Bloquants

1. `CRIT-009` - Front encore pilote par heuristiques locales P0
- source de la regle: LOT2 / `Le front ne calcule rien`
- constat observe: `engagementUiModel.js` continue de lire `turn_state` et `conversation_decision` en fallback riche
- preuve: `frontend_1.8/src/utils/engagementUiModel.js`
- niveau de confiance: eleve
- proposition d'action: basculer vers `UIState` comme contrat unique ou reduire le fallback a un mode de degradation minimal non pedagogique

2. `CRIT-002` - Verification RLS Postgres non finalisee en execution
- source de la regle: SPEC POC v1.5 + plan de tests
- constat observe: tests RLS impossibles a valider sous SQLite; port Postgres 5432 indisponible localement au moment de l'audit
- preuve: echec `SET LOCAL app.organisation_id`; `Test-NetConnection localhost -Port 5432` -> echec
- niveau de confiance: eleve sur le blocage d'environnement, moyen sur la conformite runtime finale
- proposition d'action: relancer `tests/test_cross_tenant.py` contre un vrai Postgres actif, puis fixer l'attendu `403`/`404` si necessaire

### Majeurs

3. `CRIT-011` - Synthese non branchee cote front
- source: LOT3 + checklist frontend
- constat: endpoint present, aucun bouton/appel front observe
- preuve: `backend/apps/hugo/urls.py`, recherche dans `frontend_1.8/src`
- confiance: elevee
- action: brancher un vrai parcours utilisateur pour synthese

4. `CRIT-012` - Evaluation non branchee cote front
- source: LOT3 + checklist frontend
- constat: meme situation que synthese
- preuve: idem
- confiance: elevee
- action: brancher evaluation et ses etats UI

5. `CRIT-014` - Absence de `synthesis_service.py` reel
- source: LOT3
- constat: endpoints renvoient seulement `synthesis_queued` / `evaluation_queued`
- preuve: `views_sessions.py`
- confiance: elevee
- action: implementer ou documenter explicitement le hors-perimetre; ne pas compter la fonctionnalite comme livree

6. `CRIT-015` - Memoire thematique branchee seulement partiellement
- source: LOT4
- constat: consolidation appelee dans `GenerateTraceView`, pas dans le flux conversation standard
- preuve: `views_sessions.py`, `memory_consolidator.py`
- confiance: elevee
- action: decider le vrai point d'appel post-conversation et le tester

7. `CRIT-016` - Aucune injection reelle de `LearnerThemeMemory` dans le contexte
- source: LOT4
- constat: pas de feature flag/injection observee dans l'orchestrateur
- preuve: `hugo_orchestrator.py`
- confiance: elevee
- action: soit brancher proprement, soit requalifier le lot comme partiellement livre

8. `CRIT-019` - Observabilite cohorte partielle
- source: LOT6
- constat: modeles/tests presents, mais snapshot qualite surtout alimente a la generation de trace
- preuve: `views_sessions.py`, `quality_tracker.py`
- confiance: moyenne a elevee
- action: choisir un vrai moment de consolidation qualite et l'instrumenter

9. `CRIT-020` - Administration ORGADMIN partielle et permissions parfois trop larges
- source: SPEC POC v1.5
- constat: UI users limitee; certains endpoints groupes/membres/exports sont plus ouverts que l'intention spec
- preuve: `views_groups.py`, front admin
- confiance: elevee
- action: resserrer les permissions et clarifier le perimetre ORGADMIN reel

10. `CRIT-025` - Pas de campagne Chromium/Playwright outillee
- source: plan de tests API + Chromium
- constat: aucune config Playwright dans le repo
- preuve: recherche repo
- confiance: elevee
- action: soit accepter un mode manuel documente, soit ajouter une vraie suite E2E

### Mineurs

11. `CRIT-018` - UI trainer dediee absente
- source: LOT5 + roadmap gaps
- constat: endpoints presents, UI dediee absente
- preuve: routes/front
- confiance: elevee
- action: classer explicitement comme partiel / hors perimetre selon la cible produit retenue

12. `CRIT-021` - SUPERADMIN surtout technique
- source: SPEC + contextualisation
- constat: capacité technique presente, UI produit absente
- preuve: accounts/admin/API
- confiance: elevee
- action: documenter l'etat reel au lieu de supposer un back-office complet

### Ambigus

13. `CRIT-003` - Gel P0 historique strict non prouve par cet audit
- source: README lots
- constat: pas d'audit git historique complet sur chaque ligne P0
- preuve: lecture structurelle seulement
- confiance: moyenne
- action: ajouter une verification git ciblée si la decision depend de ce point

14. `CRIT-022` - Reference exacte de la branche ergonomique du fil
- source: consigne contextuelle du fil
- constat: `frontend_1.8` est bien la variante montrable, mais la branche git nominale de reference du fil n'est pas explicitement tracee dans le repo
- preuve: comparaison `main` / `hugolucia`, docs 1.8
- confiance: moyenne
- action: classer `a arbitrer` tant qu'aucun nom de branche de reference explicite n'est fourni

## Synthese courte

L'audit montre un noyau backend Hugo 1.9 solide sur les contrats, la progression, les postures, la memoire et la base trainer, avec de bons tests cibles. En revanche, plusieurs briques 1.9 restent seulement partiellement branchees ou seulement presentes: front encore derive en partie des signaux P0, synthese/evaluation non livrees comme fonctionnalites completes, memoire thematique non injectee dans le flux normal, analytics cohorte incomplets, et campagne navigateur non outillee.

Le front n'est pas "presque inchange": la variante `frontend_1.8` montre bien une progression visible et une base ergonomique montrable. Mais il n'est pas conforme au LOT2 strict tel que documente, car il n'a pas encore bascule completement sur `UIState` comme contrat unique et il ne branche pas les actions synthese/evaluation.
