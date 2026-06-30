# B0 — Monographie scientifique Hugo réel

**Date de photo :** 22 juin 2026  
**Workspace :** Zone de travail Hugo  
**Objet :** description rigoureuse et autoportante du système Hugo tel qu'observé localement, avec limites de validité explicites.

---

# Section 1 — Objet, méthode, corpus, limites

## 1.1 Objet du document

Ce document décrit l'application Hugo dans son état **réel audité** au 22 juin 2026 : finalité, architecture, parcours utilisateurs, noyau conversationnel, variables pédagogiques (notamment P0), objets structurants et frontières de confidentialité. Il est destiné à une exploitation scientifique (analyse, comparaison, modélisation) sans présupposer la livraison de la cible Hugo 2.0.

## 1.2 Question de recherche documentaire implicite

*Qu'est-ce que Hugo fait réellement aujourd'hui, avec quelles preuves, quelles limites, et où s'arrête le réel observable par rapport à la doctrine 2.0 ?*

## 1.3 Sources mobilisées

### Socle réel (priorité 1)

- `docs-workspace/00_HIERARCHIE_DOCUMENTAIRE.md`
- `docs-workspace/01_CARTOGRAPHIE_WORKSPACE_REEL.md`
- `docs-workspace/02_ETAT_MOTEUR_REEL.md`
- `docs-workspace/03_ETAT_PRODUIT_REEL.md`
- `docs-workspace/04_INDEX_DOCUMENTAIRE_QUALIFIE.md`
- `docs-workspace/05_ECARTS_DOC_CODE_PRODUIT.md`
- `docs-workspace/07_RUNTIME_DEMO_REFERENCE.md`
- `docs-workspace/08_FLAGS_ET_ENVIRONNEMENT_DEMO.md`
- `docs-workspace/09_PARCOURS_DEMO_ET_SCENARIOS.md`
- `docs-workspace/10_FICHE_RUNTIME_PROD_ENCOORS.md`

### Méthode et vocabulaire

- `docs-workspace/DOC_METHODO_REFERENCE_CONVERGENCE_HUGO_REVISE.md`
- `docs-workspace/glossaire_alignement_hugo_reel_vs_spec.md`
- `docs-workspace/plan_documentation_cto_convergence_hugo.md`
- `docs-workspace/REFERENCE_OBJECTIFS_CIBLE_HUGO_REVISE.md` (si mobilisé pour comparaison)

### Audits récents (priorité sur constats anciens si plus fins)

- `docs-workspace/cluster2_matrice_runtime_vs_cible.md` (v6, 20/06/2026)
- `docs-workspace/cluster15_interfaces_apprenant_formateur_resultats.md`
- `docs-workspace/cluster16_interface_apprenant_spec_conformite_resultats.md`
- `docs-workspace/variables_prompting.md`
- Fichiers `docs-workspace/ecarts — <domaine>.md`

### Code (vérité comportementale)

- `hugo_back/apps/hugo/` (orchestrateur, services, domaine, modèles)
- `hugo-hugolucia/frontend_1.8/` (consommation API)

### Cible 2.0 (comparaison uniquement)

- `docs-workspace/spec_canonique_hugo_2_0.md`
- `docs-workspace/complements_spec_2_0_depuis_anterieurs.md`
- `docs-workspace/specs Orchestrateur diagnostic 2.0.md`
- `docs-workspace/specs formateur + tuteur 2.0.md`
- `docs-workspace/specs interface 2.0.md`

## 1.4 Hiérarchie des sources

1. Code `hugo_back/` et tests pytest  
2. Front `hugo-hugolucia/frontend_1.8/`  
3. Docs-workspace 02–03, cluster 2 v6  
4. Docs 07–10 (runtime)  
5. Écarts par domaine  
6. Spec 2.0 (CIBLE, jamais preuve)  
7. Archives (MEMO CTO, audits mai 2026, spec 1.6.2)

## 1.5 Règles de vérité

| Tag | Usage |
|-----|-------|
| **RÉEL OBSERVÉ** | Code + tests ou audit produit vérifiable |
| **RÉEL OBSERVÉ PARTIEL** | Existe mais couverture ou profondeur incomplète |
| **CIBLE** | Spec 2.0 — non prouvé livré |
| **ÉCART CONFIRMÉ** | Divergence recoupée doc + code |
| **A_VERIFIER** | Prod, flags, RLS, runtime non inspecté |
| **HYPOTHÈSE** | Recommandation non démontrée |

## 1.6 Limites

- **Périmètre code :** `hugo_back` local juin 2026 ; pas d'exhaustivité ligne par ligne.
- **Périmètre produit :** `frontend_1.8` hugolucia ; pas `hugo-main`.
- **Prod :** inspection HTTP Encoors du 12/06/2026 sans parcours authentifié complet.
- **Formules :** décrites uniquement si prouvées par code nommé ; sinon rôle + emplacement + niveau de preuve.
- **Extensions Hugo & Cie :** hors périmètre.

## 1.7 Distinction local / distant / cible / audits récents

| Couche | Statut |
|--------|--------|
| Moteur local `hugo_back` | **RÉEL OBSERVÉ** — doc 02 |
| Produit local front 1.8 | **RÉEL OBSERVÉ** — doc 03, clusters 15–16 |
| API `hugoback.encoors.com` | **RÉEL OBSERVÉ PARTIEL** — doc 10 ; flags **A_VERIFIER** |
| Hugo 2.0 spec | **CIBLE** |
| MEMO CTO 1.9 | Partiellement **obsolète** vs local (doc 05) |

---

# Section 2 — Vue d'ensemble du système

## 2.1 Finalité applicative

Hugo est un moteur de tutorat conversationnel orienté formation (AFEST, compétences métier). Il accompagne un apprenant dans un fil dialogue structuré par phases et postures, avec progression mesurable, actions terminales (synthèse, évaluation), traces et preuves, sous gouvernance multi-tenant.

**Statut :** **RÉEL OBSERVÉ** — parcours `/app` et backend associé.

## 2.2 Briques principales

| Brique | Rôle | Statut |
|--------|------|--------|
| Moteur Django | Orchestration, P0, persistence | **RÉEL OBSERVÉ** |
| LLM (Ollama/OVH) | Réponses tuteur, classifieurs, synthèse/éval | **RÉEL OBSERVÉ** |
| Front Vue 3 | Parcours apprenant, admin testeur | **RÉEL OBSERVÉ** |
| Bibliothèque / RAG | Documents groupe, sélection lexical | **RÉEL OBSERVÉ** |
| Exports / Qualité | CSV/JSON, bundle evidence | **RÉEL OBSERVÉ** |
| Analytics | Signaux qualité, vues cohorte partielles | **RÉEL OBSERVÉ PARTIEL** |

## 2.3 Articulation des rôles

```
Apprenant (/app) ──► sessions, chat, ui-state, CTA
Tuteur (/app/tutor) ──► timeline, éléments partagés uniquement
Formateur (/app/trainer) ──► base connaissances, élicitation
Testeur (mode tester) ──► calibration P0, admin
ORGADMIN / SUPERADMIN ──► users, groupes, exports, profils globaux
```

**Doctrine :** validation humaine finale évaluation — **RÉEL OBSERVÉ** (pas de certification autonome exposée).

---

# Section 3 — Architecture logique détaillée

## 3.1 Backend

- Django 5.2+, DRF, apps `hugo`, `accounts`, `referentials`, `library`, `exports`, `quality`.
- Point d'entrée tour : `build_hugo_turn()` (`hugo_orchestrator.py`).
- Settings défaut : `config.settings.dev` ; flags dans `base.py`.

## 3.2 API (préfixes)

| Préfixe | Rôle |
|---------|------|
| `/auth/` | JWT |
| `/hugo/` | Sessions, messages, prompts, analytics |
| `/groups/` | Groupes, membres |
| `/documents/` | Library |
| `/exports/` | Export synchrone |
| `/quality/` | Evidence bundle |
| `/internal/` | Debug, RAG search, observability |
| `/learners/` | Traces, evidence apprenant |

## 3.3 Front

- `hugo-hugolucia/frontend_1.8/` — référence produit.
- Consommation `ui-state` sans heuristique P0 locale en `/app`.
- SSE + fallback POST messages.

## 3.4 Surfaces techniques vs métier

- **Métier :** ui-state, CTA, chat, panneaux progression/mémoire.
- **Technique :** turn-review, modales TurnState (testeur), internal observability.

## 3.5 Persistance

PostgreSQL ; modèles centraux : `HugoSession`, `HugoMessage`, `Trace`, `Evidence`, `LearnerThemeMemory`, `LearnerEvaluationRecord`, `TutorPrompt`, `TutorConductProfile`, `TrainerKnowledgeItem`, `ConversationQualitySignal`.

## 3.6 LLM

- Providers : Ollama (défaut), OVH AI (groupe/session).
- Appels : tuteur principal, classifieurs P0/phase (si activés), synthèse, évaluation.

## 3.7 Tâches asynchrones

- `index_document` (library) — **RÉEL OBSERVÉ** sans embeddings.
- `recalc_learner_state` — **RÉEL OBSERVÉ PARTIEL** (placeholder).

## 3.8 Couches de confidentialité

- `organisation_id` sur entités.
- `TenantRLSMiddleware` — **RÉEL OBSERVÉ** code ; RLS Postgres prod **A_VERIFIER**.
- Partage explicite session → tuteur (flags share).
- Verbatim tuteur masqué si non partagé (B1-01) — **RÉEL OBSERVÉ** tests.

---

# Section 4 — Parcours utilisateurs types

## 4.1 Apprenant

| Dimension | Détail | Preuve |
|-----------|--------|--------|
| Intention | Dialogue tutoré, progression, synthèse/éval | doc 09 |
| Entrée | `/login` → JWT → `/app` | router, auth.js |
| Routes | `/app`, `/app/session/:sessionId` | **RÉEL OBSERVÉ** |
| Actions | Créer session, chatter, posture, synthèse, éval, trace, partage | ProdLearnerWorkspace |
| États visibles | ui-state, messages, panneau progression, mémoire | **RÉEL OBSERVÉ** |
| Endpoints | voir annexe routes | doc 03 |
| Exposé | Scène, quêtes, CTA, citations RAG, mémoire résumée | |
| Caché | TurnState, P0, décision brute | **RÉEL OBSERVÉ** |
| Limites | Dépend API cible ; 3 scènes UI ≠ 5 jalons moteur | doc 09 |

## 4.2 Tuteur

| Dimension | Détail | Statut |
|-----------|--------|--------|
| Intention | Suivre apprenants, éléments partagés | **PARTIEL** |
| Entrée | `/app/tutor` | cluster 3 |
| Actions | Timeline, lecture synthèse/éval si partagées | B1-01 |
| Caché | Verbatim non partagé | **RÉEL OBSERVÉ** |
| Limites | Surface prod vs cible orchestrateur tuteur 2.0 | **ÉCART** |

## 4.3 Formateur

| Dimension | Détail | Statut |
|-----------|--------|--------|
| Intention | Base connaissances, validation, élicitation | **PARTIEL+** |
| Routes | `/app/trainer/knowledge`, élicitation | C15 |
| Actions | CRUD knowledge, validate/reject/provisional | **RÉEL OBSERVÉ** local |
| Limites | Script F1–F4 incomplet ; lien RAG **A_VERIFIER** | |

## 4.4 Testeur

| Dimension | Détail | Statut |
|-----------|--------|--------|
| Activation | `VITE_FRONTEND_MODE=tester` | doc 03 |
| Routes | `/dashboard`, groupes, admin, conduct-profiles | **RÉEL OBSERVÉ** |
| Spécificité | LearnerDetailView, P0 debug, overrides phase | Hors démo client |

## 4.5 Administrateur

- Users (sans DELETE), groupes, référentiels, OVH LLMs, profils globaux apprenant (`/admin/conversation/learner/profiles`).
- Exports via `POST /exports/run/` (testeur).
- **RÉEL OBSERVÉ** — completude vs cible 2.0 **PARTIEL**.

## 4.6 Organisation / groupe

- Multi-tenant : org, groupes, memberships.
- Affectation profil conversationnel global au groupe (20/06).
- SUPERADMIN : `OrgTenantSwitcher`, `X-Organisation-Id`.
- **RÉEL OBSERVÉ** local — Playwright tenant 11/11 (archive 18–20/06).

---

# Section 5 — Fonctions implémentées et usages

| Fonction | Implémentation | Statut | Limites |
|----------|----------------|--------|---------|
| Conversation | `build_hugo_turn` | **RÉEL OBSERVÉ** | legacy défaut |
| Progression | `build_conversation_progress` | **RÉEL OBSERVÉ** | |
| UIState | `build_contract_ui_state` | **RÉEL OBSERVÉ** | double builder |
| Posture | resolve + set-posture + profils globaux | **RÉEL OBSERVÉ PARTIEL+** | |
| Synthèse | `synthesis_service` + CTA | **RÉEL OBSERVÉ** | prompt admin absent |
| Évaluation | workflow + guards maturité | **RÉEL OBSERVÉ** | |
| Traces | generate-trace | **PARTIEL** | payload minimal |
| Evidence | upload, EXIF | **RÉEL OBSERVÉ** | |
| Partage | share flags | **RÉEL OBSERVÉ** | |
| Mémoire intra | session_memory + API + panneau | **RÉEL OBSERVÉ** | pas prompt |
| Mémoire inter | LTM consolidator | **PARTIEL** | pas injection tour |
| RAG | lexical | **RÉEL OBSERVÉ** | pas vectoriel |
| Base formateur | TrainerKnowledgeItem | **PARTIEL+** | |
| Analytics qualité | signals + internal | **PARTIEL** | |
| Administration | voir §4.5 | **PARTIEL** | |
| Exports | CSV/JSON, bundle | **RÉEL OBSERVÉ** local | Encoors **A_VERIFIER** |

---

# Section 6 — Noyau conversationnel détaillé

## 6.1 Chaîne confirmée (legacy, défaut)

**RÉEL OBSERVÉ** — séquence dans `hugo_orchestrator.py` :

1. Contexte (`build_hugo_context`)
2. Posture + conduct profile
3. `analyze_turn_state` → TurnState
4. `classify_p0_turn_state` (si flag/config)
5. `decide_conversation` (ou v17)
6. `build_teaching_plan`
7. `decide_next_phase`
8. `select_rag_chunks`
9. `build_session_memory`
10. `build_conversation_progress` + contrat
11. `build_contract_ui_state`
12. Rendu prompt → LLM → guardrails → save
13. Hooks : consolidation + qualité

## 6.2 Dépendant de flag

- Stack v17 entière : `HUGO_P0_V17_ENABLED=true` — **CREDIBLE** code, **A_VERIFIER** prod.
- Classifieur P0 LLM : `HUGO_P0_CLASSIFIER_ENABLED` ou override session.
- Classifieur phase : `HUGO_PHASE_CLASSIFIER_ENABLED=true` défaut.

## 6.3 Dépendant runtime non audité

- Qualité/latence LLM prod.
- SSE effectif Encoors.
- Comportement si `ENABLE_EXTERNAL_LLM=false`.

## 6.4 Garde-fous

- Post-traitement réponse : `_apply_reply_guardrails` (legacy) ou v17.
- Contraintes depuis `ConversationDecision.response_constraints`.
- Non-exposition P0 au front prod.

---

# Section 7 — P0 et variables pédagogiques / conversationnelles

## 7.1 Rôle de P0

**RÉEL OBSERVÉ :** P0 est la couche de régulation locale du tour. Elle transforme le message apprenant et le contexte en signaux (`TurnState`), puis en décision structurée (`ConversationDecision`), qui pilote le plan pédagogique, la phase, le rendu prompt et les garde-fous — sans être exposée au front produit standard.

**CIBLE 2.0 :** même rôle doctrinal ; coexistence legacy/v17 mieux documentée en spec qu'en code.

## 7.2 Place de TurnState

| Aspect | Détail | Preuve |
|--------|--------|--------|
| Producteur principal | `analyze_turn_state()` heuristique | `turn_state_analyzer.py` |
| Surclassement | `classify_p0_turn_state()` JSON 8 champs si classifieur | `p0_classifier.py` |
| Structure | Dataclass ~30+ champs + sous-objet `p0` dans `to_dict()` | `domain/schemas.py` |
| Persistance tour | Payload debug message / turn-review | **RÉEL OBSERVÉ** testeur |
| Exposition prod | Absente `/app` | doc 03, cluster 2 |

### Champs TurnState significatifs (échantillon)

**RÉEL OBSERVÉ** — liste non exhaustive : `episode_clarity`, `has_concrete_actions`, `problem_salience`, `cognitive_load`, `interaction_risk`, `reflection_phase`, `covered_points`, `remaining_open_points`, `learner_help_request`, `closure_signal`, `repetition_signal`, `session_phase`, `session_maturity`, `last_tutorial_move`, `consecutive_clarify_turns`.

## 7.3 ConversationDecision

**RÉEL OBSERVÉ** — `decide_conversation(state: TurnState)` dans `decision_engine.py` :

| Champ réel | Rôle | Preuve emplacement |
|------------|------|-------------------|
| `primary_intent` | Objectif régulation tour | règles if/elif L10+ |
| `pedagogical_move` | Geste tutoral (clarify, analyze, close, repair, assist…) | idem |
| `number_of_questions` | 0–2 typiquement | `protected_mode`, closure cases |
| `question_style` | simple_open, no_question, single_safe… | idem |
| `should_explain_briefly` | Micro-explication autorisée | `explicit_help_request_case` L93+ |
| `should_recap/encourage/reframe/close` | Flags comportementaux | branches décision |
| `response_constraints` | Contraintes prompt/guardrails | listes string |
| `reason_codes` | Traçabilité décision | append dans branches |

**Mapping cible :** `primary_goal` ↔ `primary_intent` ; `tutorial_move` ↔ `pedagogical_move` ; `target_question_count` ↔ `number_of_questions` ; `micro_explain_allowed` ↔ `should_explain_briefly`.

**Niveau de preuve formules :** **RÉEL OBSERVÉ** pour `decision_engine.py` legacy — règles explicites dans le code, pas inférées. v17 : **CREDIBLE** fichier séparé, flag off par défaut.

## 7.4 Coexistence legacy / v17

| Composant | Legacy (défaut) | v17 |
|-----------|-----------------|-----|
| Décision | `decision_engine.py` | `decision_engine_v17.py` |
| TurnState | heuristique (+ classifieur optionnel) | `reconcile_turn_state_v17` |
| Prompt | `prompt_renderer.py` | `prompt_renderer_v17.py` |
| Tests | `conftest.py` force v17 off | `test_p0_v17_flow.py` opt-in |

**Statut :** **RÉEL OBSERVÉ** double stack — **A_VERIFIER** activation prod.

## 7.5 Flags associés

| Flag | Défaut local | Effet |
|------|--------------|-------|
| `HUGO_P0_V17_ENABLED` | false | Bascule stack v17 |
| `HUGO_P0_CLASSIFIER_ENABLED` | false | Classifieur LLM P0 |
| `HUGO_P0_CLASSIFIER_MIN_CONFIDENCE` | 0.60 | Seuil acceptation overrides |
| `HUGO_PHASE_CLASSIFIER_ENABLED` | true | Phase LLM |

Override session possible — **RÉEL OBSERVÉ** `resolve_p0_classifier_runtime_config`.

## 7.6 Articulation heuristique / classifieur / décision

```
Message → heuristique (TurnState base)
       → [option] classifieur LLM JSON → fusion si confiance ≥ seuil
       → [option] reconcile v17
       → decide_conversation → ConversationDecision
       → teaching plan + phase + prompt
```

**RÉEL OBSERVÉ** — `variables_prompting.md` §I.

## 7.7 Variables glossaire / cible

| Variable | Statut réel | Emplacement / preuve |
|----------|-------------|---------------------|
| `primary_goal` | **RÉEL OBSERVÉ** as `primary_intent` | ConversationDecision |
| `tutorial_move` | **RÉEL OBSERVÉ** as `pedagogical_move` | idem |
| `mode` | **PARTIEL** | protected_mode, posture — pas champ unique homonyme |
| `target_question_count` | **RÉEL OBSERVÉ** as `number_of_questions` | idem |
| `micro_explain_allowed` | **RÉEL OBSERVÉ** as `should_explain_briefly` | idem |
| `use_theme_memory` | **ÉCART CONFIRMÉ** | Décision/metadata ; LTM non injectée |
| `use_verbatim_retrieval` | **PARTIEL** | Contexte/history_block ; gouverné partage |
| `use_rag` | **RÉEL OBSERVÉ** | `rag_allowed` + `select_rag_chunks` |
| `optional_evaluation_eligible` | **RÉEL OBSERVÉ** | `evaluation_eligible` progression |
| `reason_codes` | **RÉEL OBSERVÉ** | TurnState, Decision, Progress |

## 7.8 Progression et maturité

**RÉEL OBSERVÉ** — `SessionMaturityLevel` : RED, ORANGE, GREEN.

- `build_conversation_progress_contract()` produit branches, `overall_maturity`, `missing_for_next_level`, `reason_codes`.
- Éligibilité synthèse : `can_summarize`, codes `synthesis_eligible` / `synthesis_blocked_maturity` (tests CTA).
- Éligibilité évaluation : `evaluation_eligible`, `evaluation_blocked_maturity` (tests B16-C2).
- Dispersion : `dispersion_risk`, `priority_branch_label` — cluster 16.

**Formule exacte maturité :** **RÉEL OBSERVÉ PARTIEL** — logique dans calculator/progression services ; détail ligne par ligne non reproduit ici — voir `conversation_progress` modules et tests `test_conversation_progress.py`.

## 7.9 États produit dérivés

| État | Source | Statut |
|------|--------|--------|
| `scene_label`, `scene_progress` | ui-state | **RÉEL OBSERVÉ** |
| `quest_progress`, `active_quest_label` | ui-state | **RÉEL OBSERVÉ** |
| `maturity_color` | ui-state | **RÉEL OBSERVÉ** |
| `synthesis_button_state` | cta_ui_state | **RÉEL OBSERVÉ** |
| `evaluation_button_state` + `ui.advisory` | cta_ui_state + C16 | **RÉEL OBSERVÉ** |
| `persistent_objects` | ui-state | **RÉEL OBSERVÉ** |
| `conversation_mode` | ui-state | **RÉEL OBSERVÉ** |
| `allowed_posture_transitions` | ui-state | **RÉEL OBSERVÉ** |
| `learner_display_profile` | ui-state + query param | **RÉEL OBSERVÉ** |
| Posture visible | PostureSelector | **PARTIEL+** |

## 7.10 Synthèse section 7

Le noyau P0 est **implémenté et testé** en legacy. Les variables de décision ont un mapping stable vers le glossaire. Les principaux écarts sont : double stack v17 non arbitrée, `use_theme_memory` sans injection réelle LTM, et distinction UI 3 scènes / 5 jalons moteur.

---

# Section 8 — Objets, états dérivés et confidentialité

## 8.1 Objets persistés

Sessions, messages, traces, evidence, LTM, evaluation records, prompts, conduct profiles, trainer knowledge, quality signals, profils globaux apprenant.

## 8.2 Objets dérivés (non persistés tels quels)

TurnState, ConversationDecision (tour courant), UIState, SessionMemoryContract (recalculé), progression contrat.

## 8.3 Exposé au front

ui-state, messages, memory-summary (API), traces/evidence filtrées, citations RAG, CTA états.

## 8.4 Backend only

P0 complet, TurnState brut (sauf debug), turn-review, observability internal, D9bis exports.

## 8.5 UIState

Traduction produit — **ne pas confondre avec moteur** — **RÉEL OBSERVÉ** aligné doctrine 2.0.

## 8.6 Mémoire

- Intra : panneau + API — pas verbatim brut comme mémoire.
- Inter : endpoint — consolidation sans relecture tour suivant — **ÉCART CONFIRMÉ** vs cible injection.

## 8.7 Traces, preuves, exports

- Trace generate : minimal — **PARTIEL**.
- Pivot evaluation_trace_v1 : enrichit exports — **PARTIEL** local.
- Bundle Qualiopi : **RÉEL OBSERVÉ** tests.

## 8.8 Confinement P0 / verbatim

- Parcours `/app` : conforme — **RÉEL OBSERVÉ**.
- Partage verbatim : opt-in explicite — **RÉEL OBSERVÉ**.

## 8.9 Multi-tenant et rôles

- Modèle org + RLS middleware — **RÉEL OBSERVÉ** / Postgres **A_VERIFIER**.
- Matrice rôle × visibilité — **PARTIEL** (10 tests D2-M07).
- COORDO — **CIBLE** absent.

**Cible 2.0** (spec canonique) : frontière rôles, non-exposition P0, UIState dérivé — **alignement doctrinal** avec réel partiel sur matrice complète.

---

# Section 9 — Limites, ambiguïtés, menaces de validité

## 9.1 Documentation vs code

- MEMO CTO : écarts obsolètes — menace sur priorités si non recalé.
- Chemins `backend/apps/` dans vieilles docs — menace navigation.
- Spec 1.6.2 lue comme implémentation — menace doctrine.

## 9.2 Local vs distant

- Démo défaut = Encoors ; code local peut diverger (routes conduct-profiles, evaluation-readiness).
- CORS bloque dev local → distant — menace reproductibilité démo.

## 9.3 Flags

- Comportement démo non reproductible si flags prod inconnus.

## 9.4 Limites de test

- Pas Playwright dans repo initial ; campagnes juin 2026 locales non garanties sur Encoors.
- Tests RLS sur SQLite — validité Postgres limitée.

## 9.5 Ambiguïtés lexicales

- DecisionContract vs ConversationDecision.
- EvaluationTrace vs records dispersés.
- PersistentObjects vs champ ui-state.

## 9.6 Trous de preuve

- Formules complètes maturité/branches (nécessite relecture `conversation_progress` calculator).
- Lien TrainerKnowledge → RAG runtime.
- Version git déployée Encoors.

## 9.7 Zones relecture code utile

- `decision_engine_v17.py` si activation v17 envisagée.
- `ui_state_builder.py` fusion builders.
- `memory_consolidator.py` structure LTM.

---

# Section 10 — Annexes

## 10.1 Glossaire réel ↔ cible (extrait)

| Doctrinal 2.0 | Réel observé | Statut |
|---------------|--------------|--------|
| TurnState | TurnState, analyze_turn_state | ALIGNÉ |
| Contrat décision | ConversationDecision | RENOMMER_DANS_DOC |
| ConversationProgress | build_conversation_progress_contract | ALIGNÉ |
| UIState | build_contract_ui_state, ui-state/ | ALIGNÉ |
| LearnerThemeMemory | LearnerThemeMemory + consolidator | PARTIEL |
| EvaluationTrace | pivot + LearnerEvaluationRecord + Trace | PARTIEL |
| TutorPrompt | TutorPrompt + profils globaux | ALIGNÉ_DOC_PARTIEL |
| SessionInterstitial | — | CIBLE |

Source complète : `glossaire_alignement_hugo_reel_vs_spec.md`.

## 10.2 Index endpoints observés (parcours principal)

**Auth :** `POST /auth/login/`, `GET /auth/me/`, `POST /auth/refresh/`

**Sessions :** `GET/POST /hugo/sessions/`, `GET/PATCH /hugo/sessions/{id}/`

**Messages :** `GET/POST .../messages/`, `POST .../messages/stream/`

**Produit :** `GET .../ui-state/`, `POST .../set-posture/`, `GET .../memory-summary/`

**CTA :** `POST .../request-synthesis/`, `POST .../request-evaluation/`, `GET .../evaluation-readiness/`, `POST .../finalize-evaluation/`

**Preuves :** `POST .../generate-trace/`, `POST .../share/`, `GET /learners/traces/`, `GET /learners/evidence/`

**Admin :** `/hugo/tutor-prompts/`, `/hugo/conduct-profiles/`, `/exports/run/`, `/internal/...`

## 10.3 Index objets

HugoSession, HugoMessage, TurnState, ConversationDecision, ConversationProgress, UIState, TutorPrompt, TutorConductProfile, LearnerConversationGlobalProfile, SessionMemoryContract, LearnerThemeMemory, Trace, Evidence, LearnerEvaluationRecord, TrainerKnowledgeItem, ConversationQualitySignal.

## 10.4 Index fichiers corpus

| Fichier | Rôle |
|---------|------|
| 00–10 docs-workspace | Socle réel |
| cluster2_matrice v6 | Matrice domaines |
| ecarts — *.md | Écarts par domaine |
| variables_prompting.md | Variables P0/prompt |
| spec_canonique_hugo_2_0.md | Cible |

## 10.5 Domaines encore ouverts

10 (v17, double UIState), 20 (injection prompt/inter), 30 (vectoriel, hiérarchie contexte), 31 (SW-xx), 40–50 (workflow formateur), 60 (tuteur prod), 70 (trace riche), 80 (catalogue signaux), 90 (RLS prod, D2-M12), 100 (Encoors exports), 110 (IFT-042), 120 (intercalaires).

---

*Monographie établie le 22 juin 2026. Aucune affirmation CIBLE présentée comme livrée. Runtime Encoors : inspection partielle 12/06/2026.*
