# Inventaire des variables consommables par les templates de prompt Hugo

> **Document maître (consommables + écriture LLM + relations) :** [`variables_prompting.md`](variables_prompting.md)

**Date :** 2026-06-18  
**Sources mobilisées :** `hugo_back/apps/hugo/services/prompt_renderer.py`, `prompt_renderer_v17.py`, `context_builder.py`, `hugo_orchestrator.py`, `teaching_plan_builder.py`, `turn_state_analyzer.py`, `decision_engine*.py`, `p0_classifier.py`, `synthesis_service.py`, `evaluation_service.py`, `conduct_profile_resolver.py`, `domain/schemas.py`, `docs/TUTOR_PROMPT_PLACEHOLDERS.md`.

**Réel confirmé :** les templates `TutorPrompt.system_template` / `user_template` sont des chaînes **Python `str.format`** avec placeholders `{nom}`. Le dictionnaire est produit par `_base_vars()` puis complété dans `render_with_tutor_prompt()`.

**Cible 2.0 :** mémoire gouvernée intra-conversation — **non injectée** dans les templates tutoriels au rendu actuel (`session_memory` absent de `prompt_renderer`).

**AVERIFIER :** parité prod si flag P0 v1.7 actif (bloc `_v17_guidance_block` **concaténé** au system prompt, pas exposé comme variable template).

---

## 0. Syntaxe et règles d’usage

| Règle | Détail |
|-------|--------|
| Format | `{cle}` pour une clé du `vars_dict` |
| Accès dict | `{focus_competence[label]}`, `{turn_state[current_phase]}` — syntaxe `str.format` Python |
| Objets dataclass | `{teaching_plan}`, `{competence_brief}` → représentation `repr` dataclass (peu lisible) ; préférer champs dédiés |
| Valeurs vides | Clés toujours présentes ; chaîne `""`, dict `{}`, liste `[]` si absent |
| Double emploi | `base_system_intro` **agrège déjà** état, décision, posture, fil ; les blocs séparés permettent de les repositionner |
| Risque KeyError | `{posture}`, `{max_questions}` etc. **ne sont pas** des clés top-level TutorPrompt — réservées au sous-template `TutorConductProfile.system_template` (voir §12) |

**Chemin d’appel :** `build_hugo_turn()` → `render_tutor_prompt_v17()` ou `render_with_tutor_prompt()` → `.format(**vars_dict)`.

---

## 1. Identité session et tenant

| Variable | Type | Signification | Calcul | Usage Hugo | Usage prompting |
|----------|------|---------------|--------|------------|-----------------|
| `organisation_id` | `str` (UUID) | Organisation propriétaire de la session | `str(session.organisation_id)` | Multi-tenant, traces, RLS | Rarement utile dans le discours ; traçabilité interne |
| `session_id` | `str` (UUID) | Identifiant unique de la conversation | `str(session.id)` | Logs, mémoire, UIState | Éviter en prompt apprenant ; utile debug interne |

---

## 2. Entrée apprenant et fil conversationnel

### 2.1 Message du tour courant

| Variable | Type | Signification | Calcul | Usage Hugo | Usage prompting |
|----------|------|---------------|--------|------------|-----------------|
| `situation_content` | `str` | Verbatim du message apprenant **du tour en cours**, balisé | `"Message apprenant (verbatim):\n<<<APPRENANT\n{content}\nAPPRENANT>>>"` où `content` = `user_input["content"]` | Corps principal user prompt ; base P0 | **Cœur** du user template ; ancrage factuel obligatoire |
| `history_block` | `str` | Historique des tours **précédents** (Hugo + apprenant) | `_build_history_block(session)` : messages ORM triés par `created_at`, **exclut** le dernier message si role=LEARNER ; max 48 messages, 14 000 car., troncature 4 000 car./message | Continuité conversationnelle sans re-envoyer le tour courant | `{history_block}` en system ou user pour mémoire implicite du fil ; complète (mais ne remplace pas) la mémoire gouvernée |

### 2.2 Contenu implicite non exposé en template

| Élément | Statut |
|---------|--------|
| `session_memory` / `SessionMemoryContract` | Construit par `build_session_memory()` **après** rendu prompt — **non injecté** dans `vars_dict` |
| Messages assistant complets hors `history_block` | Inclus dans `history_block` uniquement |

---

## 3. Contexte référentiel et focalisation pédagogique

### 3.1 Blocs texte agrégés

| Variable | Type | Signification | Calcul | Usage Hugo | Usage prompting |
|----------|------|---------------|--------|------------|-----------------|
| `referential_block` | `str` | Référentiel + items à travailler / couverts + **fusion** `focus_guidance_block` | `_build_blocks(ctx)` puis concaténation conditionnelle avec `focus_guidance_block` | System prompt : ancrage compétences | Bloc unique « tout le référentiel utile » |
| `focus_guidance_block` | `str` | Focalisation **du tour** (compétence, critère, tâche, couverture, anti-boucle) | `_build_focus_guidance_block(ctx, teaching_plan)` | Pilotage fin du tour | Utiliser seul si on veut séparer référentiel statique / focus dynamique |

**Construction `referential_block` (via `HugoContext`) :**

| Sous-élément | Source | Calcul |
|--------------|--------|--------|
| Nom référentiel | `ReferentialConfig` + `Referential` du groupe | `ctx.referential_name`, `ctx.referential_source_ref` |
| Items à travailler | `ReferentialItem` non entièrement couverts | Max **3** items ; par item : code, titre, bloc, 2 premiers critères, 2 preuves attendues |
| Items déjà travaillés | Critères tous `COVERED` | Max **3** items ; code + titre |
| Partition couverture | `TraceCriterionAssessment` apprenant/groupe | `_partition_items_by_coverage()` |

**Construction `focus_guidance_block` (nécessite `teaching_plan`) :**

| Ligne générée | Source |
|---------------|--------|
| Compétence focus | `teaching_plan.focus_competence.label` + match `ItemSummary` par `item_id` |
| Critère focus | `criterion_code`, `criterion_label` |
| Tâche primaire / activité | `primary_task_*`, `activity_*` dans `focus_competence` |
| Critères prioritaires | 1–2 labels depuis `ItemSummary.criteria` ou `evaluation_criteria` |
| Preuve attendue | 1 entrée `expected_evidence` |
| Critères déjà couverts + règle anti-boucle | `covered_criteria_codes` |
| Couverture | `teaching_plan.coverage_status` |
| Axe de réflexion | Clé max de `regulation_targets` |
| Action ouverte | 1er élément `open_action_items` |

### 3.2 Champs structurés du focus (template)

| Variable | Type | Signification | Calcul | Usage Hugo | Usage prompting |
|----------|------|---------------|--------|------------|-----------------|
| `focus_competence` | `dict` | Focus compétence/critère/tâche du tour | `build_teaching_plan()` → `_select_focus_candidate()` ou fallback `learning_stage.item_id` | Progression, UI focus | `{focus_competence[label]}`, `{focus_competence[criterion_label]}` pour ciblage explicite |

**Clés usuelles de `focus_competence` :** `item_id`, `label`, `item_code`, `block_code`, `block_label`, `criterion_id`, `criterion_code`, `criterion_label`, `covered_criteria_codes`, `coach_questions`, `common_mistakes`, `example_situations`, `example_evidence`, `linked_documents`, `tasks`, `primary_task_code`, `primary_task_label`, `activity_code`, `activity_label`.

| Variable | Type | Signification | Calcul | Usage Hugo | Usage prompting |
|----------|------|---------------|--------|------------|-----------------|
| `regulation_targets` | `dict[str, float]` | Poids task / reasoning / metacognition | `_derive_regulation_targets()` selon `conversation_profile` et `pedagogical_move` | Axe dominant dans `focus_guidance_block` | Ajuster ton : `{regulation_targets[reasoning]}` ou logique métier dans template |
| `ui_focus_label` | `str` | Libellé focus affiché UI / discours | `_derive_ui_focus_label(turn_state, decision, user_input, profile)` | UIState, bandeau scène | Phrase d’accroche pédagogique dans system prompt |

---

## 4. Contexte apprenant (progression trans-session légère)

| Variable | Type | Signification | Calcul | Usage Hugo | Usage prompting |
|----------|------|---------------|--------|------------|-----------------|
| `learner_block` | `str` | Synthèse progression + traces récentes | `_build_blocks(ctx)` | System prompt | Personnalisation sans verbatim |
| — synthèse | interne | Résumé gouverné apprenant | `LearnerState.summary` (dernier par org/learner/groupe), tronqué 300 car. | Mémoire inter-sessions **préparée**, injection prompt **partielle** | Rappeler parcours antérieur |
| — traces | interne | 3 dernières traces | `Trace` learner/groupe : id tronqué, date, statut validée/en cours | Continuité évaluation | Éviter reposer ce qui est déjà validé |

---

## 5. Documents de classe et RAG lexical

| Variable | Type | Signification | Calcul | Usage Hugo | Usage prompting |
|----------|------|---------------|--------|------------|-----------------|
| `documents_block` | `str` | Titres documents actifs (+ RAG si présent) | Max 3 titres `GroupDocument` ACTIVE ; **si** `rag_chunks` : concat avec `rag_chunks_block` | Appui documentaire | Citer sources autorisées |
| `rag_chunks_block` | `str` | Extraits documentaires sélectionnés | Lignes `- Doc N : {snippet}` si `rag_chunks` passé à `render_with_tutor_prompt` | RAG lexical gouverné (`select_rag_chunks`) | Formulations « Appui : … » côté modèle |
| `rag_chunks` | `list[str]` | Snippets bruts | `[selection.prompt_snippet() for selection in rag_selections]` | Traçabilité RAG | Boucle manuelle impossible en `format` — utiliser `rag_chunks_block` |

**Mode RAG :** piloté par `teaching_plan.rag_mode` (`none` / actif) dans l’orchestrateur ; le renderer ne remplit `rag_chunks_block` que si la liste est non vide.

---

## 6. Posture et profil conversationnel

| Variable | Type | Signification | Calcul | Usage Hugo | Usage prompting |
|----------|------|---------------|--------|------------|-----------------|
| `conversation_profile` | `str` | Posture active : `diagnostic`, `reflective_afest`, `knowledge_review` | `teaching_plan.conversation_profile` ou défaut `reflective_afest` ; résolu par `resolve_conversation_profile()` + override session/posture | UIState `conversation_mode`, PostureSelector | Adapter registre : `{conversation_profile}` |
| `posture_block` | `str` | Contraintes de conduite de la posture | `_build_posture_block(turn_state.posture_constraints)` ; alimenté depuis `resolve_conduct_profile()` dans orchestrateur | System prompt | Règles de conduite explicites |
| `thread_guidance_block` | `str` | Directives anti-boucle, aide, clôture, questions | Texte fixe si `turn_state` présent | Régulation qualité conversationnelle | Renforcer garde-fous sans dupliquer P0 |

**Résolution `conversation_profile` (priorité) :**

1. `session.conversation_profile_override`
2. `tutor_prompt.conversation_profile`
3. Heuristiques : speech act (`ask_help`…), mots-clés révision, `episode_clarity=low`, `learner_help_request=explicit`
4. Défaut : `reflective_afest`

**Intro posture dans `base_system_intro` :** libellé français via `conversation_profile_label()` + phrase de priorité selon profil (diagnostic / knowledge_review / réflexif).

---

## 7. Plan pédagogique du tour (`TeachingPlan`)

Variables **exposées** au template (si `teaching_plan` non `None`) :

| Variable | Type | Signification | Calcul | Usage Hugo | Usage prompting |
|----------|------|---------------|--------|------------|-----------------|
| `session_phase` | `str` | Phase séance : `opening`, `exploration`, `deepening`, `potential_closure` | `turn_state.session_phase` → `teaching_plan.session_phase` ; `decide_next_phase()` met à jour `next_session_phase` | Progression UI, verrou posture | Adapter profondeur : exploration vs clôture |
| `max_questions_this_turn` | `int` | Plafond questions **effectif** ce tour | `min(posture.max_questions_per_turn, decision.number_of_questions)` borné orchestrateur | CTA, qualité (≤2 diagnostic) | `{max_questions_this_turn}` = contrainte dure |
| `teaching_plan` | `TeachingPlan` | Objet complet | `build_teaching_plan()` + éventuellement `apply_v17_decision_to_teaching_plan()` | Métadonnées tour | **Déconseillé** en template brut |

**Champs `TeachingPlan` non exposés individuellement** (accessibles seulement via l’objet ou logique interne) :

| Champ | Signification | Calcul (résumé) |
|-------|---------------|-----------------|
| `conversation_profile` | Posture (doublon clé top-level) | Normalisé |
| `learning_stage` | Stade parcours item | `LearningStage.stage` |
| `expected_level_now` / `current_level` | Niveau attendu / estimé | Stage + heuristique `concept_clarity` |
| `coverage_status` | `ok`, `partial`, `needs_clarification`, `action_missing`, `fragile`, `covered` | `_derive_coverage_status()` / v1.7 |
| `open_action_items` | Actions ouvertes apprenant | `LearnerStateSlice.open_action_items` |
| `critical_mistakes` | Erreurs fréquentes overlay + profil | Merge overlay / `PedagogicalProfile` |
| `coach_questions_candidates` | Amorces questions coach | Overlay + profil, max 3 |
| `rag_mode` | `none` ou actif | `_derive_rag_mode()` |
| `next_session_phase` | Phase suggérée tour suivant | `_derive_next_phase_from_state()` / v1.7 |
| `primary_intent`, `pedagogical_move`, `question_style` | Copie décision | `ConversationDecision` |
| `should_recap`, `should_encourage`, `should_reframe`, `should_close` | Flags comportement | Décision |
| `response_constraints` | Contraintes textuelles | Décision |
| `phase_source` | Origine décision phase | `phase_decider` |

---

## 8. Brief compétence (`CompetenceBrief`)

| Variable | Type | Signification | Calcul | Usage Hugo | Usage prompting |
|----------|------|---------------|--------|------------|-----------------|
| `competence_brief` | `CompetenceBrief` | Fiche compacte compétence focus | Construit orchestrateur si focus résolu | Enrichissement prompt optionnel | `{competence_brief}` peu lisible — champs : |

| Champ | Signification |
|-------|---------------|
| `item_id` | ID item référentiel |
| `label` | Libellé compétence |
| `key_criteria` | Critères clés (liste) |
| `expected_evidence` | Preuves attendues |
| `critical_mistakes` | Erreurs critiques |
| `typical_situations` | Situations types |
| `preferred_coach_questions` | Questions coach préférées |

---

## 9. État conversationnel P0 (`turn_state`)

### 9.1 Formes disponibles

| Variable | Type | Usage |
|----------|------|-------|
| `turn_state` | `dict` | `TurnState.to_dict()` — accès champ par champ |
| `turn_state_block` | `str` | Sous-ensemble **lisible** formaté pour le LLM |
| (inclus dans) `base_system_intro` | `str` | Même contenu que `turn_state_block` + décision + posture + fil |

**Calcul global :** `analyze_turn_state()` (heuristiques regex + signaux tour précédent) → fusion éventuelle `classify_p0_turn_state()` (LLM JSON sur 8 champs P0_LLM_FIELDS) → réconciliation v1.7 si flag actif.

### 9.2 Champs P0 — noyau (`turn_state` / `turn_state.p0`)

| Champ | Valeurs | Signification | Calcul (heuristique) |
|-------|---------|---------------|----------------------|
| `episode_clarity` | low / medium / high | Clarté de la situation décrite | Patterns longueur, actions, contexte |
| `has_concrete_actions` | bool | Actions concrètes mentionnées | Regex `ACTION_PATTERNS` + sticky session |
| `problem_salience` | none / low / high | Saillance du problème | Patterns problème |
| `reflection_phase` | description / analysis / projection | Phase réflexive du discours | `_compute_reflection_phase()` |
| `affect_valence` | negative / neutral / positive | Valence affective | Patterns affect |
| `cognitive_load` | low / medium / high | Charge cognitive perçue | Patterns charge |
| `interaction_risk` | low / medium / high | Risque relationnel / frustration | Patterns risque |
| `session_phase` | opening … potential_closure | Phase séance | `user_input` / session |

### 9.3 Champs P0 — extension (dict complet)

| Champ | Signification | Calcul (résumé) |
|-------|---------------|-----------------|
| `reflective_depth` | Profondeur réflexive | Texte + phase |
| `self_efficacy_signal` | Confiance en soi | Patterns efficacité |
| `epistemic_balance` | Équilibre épistémique | Heuristique |
| `zpd_estimate` | Zone proximale développement | Heuristique |
| `session_maturity` | Maturité séance | Agrégation progression |
| `evidence_strength` | Force des preuves exprimées | Heuristique contenu |
| `intervention_necessity` | Besoin d’intervention | Dérivé risques / clarté |
| `contradiction_status` | Contradictions détectées | Analyse contenu |
| `concept_clarity` | Clarté conceptuelle | Heuristique |
| `available_material` | Matériel disponible évoqué | Heuristique |
| `conversation_goal` | Objectif conversationnel | `_derive_conversation_goal()` |
| `current_phase` | Phase courante (miroir) | Aligné session_phase |
| `emotional_state` | État émotionnel | Dérivé affect |
| `action_feasibility` | Faisabilité actions | Heuristique |
| `autonomy_level` | Autonomie perçue | Heuristique |
| `recent_progress` | Progression récente | Signaux session |
| `need_recap` / `need_encouragement` / `need_reframing` | Besoins pédagogiques | Flags dérivés |
| `can_close_for_now` | Clôture possible | Signaux clôture + profondeur |
| `last_tutorial_move` | Dernier move Hugo | Message assistant précédent |
| `consecutive_clarify_turns` | Tours de clarification consécutifs | Compteur session |
| `sticky_has_concrete_actions` | Actions déjà vues en session | Mémoire intra-session P0 |
| `tech_representation_level` | implicit / explicit | Niveau technique discours |
| `technical_criterion_focus` | Critère technique ciblé | Alignement référentiel |
| `safety_or_quality_risk_level` | Risque sécurité/qualité | Heuristique métier |
| `covered_points` | Points déjà couverts (liste) | Suivi fil |
| `remaining_open_points` | Points ouverts | Suivi fil |
| `learner_help_request` | none / implicit / explicit | Demande d’aide |
| `closure_signal` | none / implicit / explicit | Signal clôture |
| `repetition_signal` | none / implicit / explicit | Signal répétition |
| `loop_risk` | low / medium / high | Risque boucle |
| `assistant_meta_leak_risk` | Risque fuite meta-instructions | Heuristique |
| `debug_signals` | dict | Debug interne — **ne pas exposer apprenant** |

**Usage prompting :** préférer `turn_state_block` pour le LLM tutoriel ; `{turn_state[episode_clarity]}` pour conditions fines ; **ne jamais** recopier `debug_signals` vers l’apprenant.

---

## 10. Décision tutorale (`conversation_decision`)

### 10.1 Formes disponibles

| Variable | Type | Usage |
|----------|------|-------|
| `conversation_decision` | `dict` | `ConversationDecision.to_dict()` |
| `decision_block` | `str` | Format lisible |
| `response_constraints_block` | `str` | `"Contraintes de réponse : " + "; ".join(...)` |
| (inclus dans) `base_system_intro` | `str` | Agrégation |

**Calcul :** `decide_conversation(turn_state)` ou `decide_conversation_v17()` → adaptateur legacy.

### 10.2 Champs

| Champ | Signification | Calcul |
|-------|---------------|--------|
| `primary_intent` | Intention principale | Moteur décision (clarify, analyze, close…) |
| `pedagogical_move` | Move pédagogique | Règles sur P0 + phase |
| `number_of_questions` | Questions cibles | Moteur décision |
| `question_style` | `simple_open`, `no_question`, `double_same_goal`… | Dérivé count + move |
| `should_explain_briefly` | Micro-explication autorisée | Flags dérivés |
| `should_recap` | Récapitulatif | Éligibilité recap |
| `should_encourage` | Encouragement | Affect / efficacité |
| `should_reframe` | Reformulation | Confusion / contradiction |
| `should_close` | Clôture | Signaux clôture |
| `response_constraints` | Liste contraintes textuelles | Agrégation moteur + v1.7 |
| `reason_codes` | Codes raison | Traçabilité |
| `metadata` | dict | `conversation_profile`, v1.7, signaux |

**Dans `decision_block` :** `max_questions_this_turn` affiché = `teaching_plan.max_questions_this_turn` si présent, sinon `number_of_questions`.

**Usage prompting :** `{decision_block}` + `{response_constraints_block}` pour **obéissance** stricte ; combiner avec `{max_questions_this_turn}`.

---

## 11. Blocs pré-assemblés (macros textuelles)

| Variable | Contenu agrégé | Quand rempli |
|----------|----------------|--------------|
| `base_system_intro` | Intro Hugo + posture + `turn_state_block` + `decision_block` + `response_constraints_block` + `posture_block` + `thread_guidance_block` | Toujours (parties conditionnelles si turn_state/decision) |
| `referential_block` | Référentiel + focus (fusion) | Si contexte référentiel ou teaching_plan |
| `learner_block` | Progression + traces | Si données apprenant |
| `documents_block` | Docs + RAG | Si documents / chunks |
| `focus_guidance_block` | Focus tour | Si teaching_plan |
| `history_block` | Historique | Si messages antérieurs |
| `posture_block` | Conduite posture | Si `posture_constraints` sur turn_state |
| `thread_guidance_block` | Régulation fil | Si turn_state |
| `turn_state_block` | P0 synthétique | Si turn_state |
| `decision_block` | Décision locale | Si conversation_decision |
| `response_constraints_block` | Contraintes | Si conversation_decision |

**Usage prompting :** `{base_system_intro}` = template minimal viable ; découper si besoin de réordonner (ex. mettre `{situation_content}` avant `{referential_block}` en user).

---

## 12. Variables nested — `TutorConductProfile.system_template`

Ces placeholders **ne sont pas** dans `vars_dict` global. Ils sont résolus **à l’intérieur** de `posture_block` via `.format()` secondaire :

| Variable | Signification | Source |
|----------|---------------|--------|
| `{posture}` | Code posture **MAJUSCULES** | `posture_constraints.posture` |
| `{max_questions}` | Max questions / tour posture | `TutorConductProfile.max_questions_per_turn` ou statique |
| `{forbidden_moves}` | Moves interdits (liste CSV) | Profil conduct |
| `{description}` | Description posture | Profil conduct |

**Usage :** éditer le `system_template` du **profil de conduite** (admin), pas du TutorPrompt — sauf duplication manuelle des valeurs.

---

## 13. Extension P0 v1.7 (non template — append system)

Si `P0_V17_ENABLED`, bloc **concaténé** après rendu TutorPrompt (`_v17_guidance_block`) :

| Information | Source |
|-------------|--------|
| `conversation_profile` | metadata décision |
| `response_mode` | reflect / assist / closure / recap / evaluation |
| `target_question_count` | Décision v1.7 bornée |
| `coverage_status` | `TurnStateV17.derived_signals` |
| `learner_speech_act` | Classifieur acte de parole |
| `last_learner_act` | Dérivé signaux |
| `blocked_question_topics` | Points déjà couverts |

**Écart :** non disponible comme `{response_mode}` dans TutorPrompt — **AVERIFIER** si migration template souhaitée.

---

## 14. Autres pipelines LLM (hors `TutorPrompt.format`)

Ces prompts **n’utilisent pas** le dictionnaire template TutorPrompt.

### 14.1 Classifieur P0 (`p0_classifier.py`)

| Entrée | Rôle |
|--------|------|
| `phase_session` | Phase heuristique |
| `heuristique_reference` | JSON 8 champs P0_LLM_FIELDS |
| `contexte` | resume_apprenant, traces_recentes, documents_classe |
| `dernier_message_apprenant` | Verbatim tronqué |

**Sortie attendue :** JSON strict 8 champs + `confidence`.

### 14.2 Synthèse scène (`synthesis_service.py`)

| Entrée user prompt | Source |
|--------------------|--------|
| Posture, maturité | `progress.posture`, `progress.overall_maturity` |
| Fils actifs | `progress.active_branches` |
| Dernier repère | Dernier message learner (280 car.) |
| Points ouverts | `progress.missing_for_next_level` |
| Historique récent | 6 derniers messages |

### 14.3 Évaluation (`evaluation_service.py`)

| Entrée | Source |
|--------|--------|
| `prompt_frame`, `prompt_judgement_guide`, `prompt_output_guide` | `EvaluationPromptProfile` |
| Directives formateur | `EvaluationContext.trainer_directives` |
| Critères ciblés | `referential_items` |
| Connaissances formateur | `trainer_knowledge_items` validées |
| Indices conversationnels | `conversation_evidence` |
| `is_early_trigger` | Maturité orange/rouge |
| Historique | 10 derniers messages |

---

## 15. Matrice rapide — quelle variable pour quel besoin prompting

| Besoin | Variables recommandées |
|--------|------------------------|
| Ancrer le verbatim tour | `{situation_content}` |
| Continuité multi-tours | `{history_block}` |
| Compétences / critères | `{referential_block}` ou `{focus_guidance_block}` |
| Personnalisation parcours | `{learner_block}` |
| Appui documentaire | `{documents_block}`, `{rag_chunks_block}` |
| Posture / ton | `{conversation_profile}`, `{posture_block}`, `{base_system_intro}` |
| Régulation questions | `{max_questions_this_turn}`, `{decision_block}`, `{thread_guidance_block}` |
| État apprenant (sans debug) | `{turn_state_block}` |
| Phase séance | `{session_phase}` |
| Focus UI / discours | `{ui_focus_label}` |
| Contraintes dures | `{response_constraints_block}` |

---

## 16. Écarts confirmés et prochaines sorties utiles

| Écart | Statut | Action suggérée |
|-------|--------|-----------------|
| `session_memory` non injectée prompt tutoriel | **Réel** | Contrat `{memory_summary_block}` si lot mémoire prompt |
| Champs `TeachingPlan` partiellement exposés | **Réel** | Exposer `coverage_status`, `rag_mode`, `coach_questions_candidates` |
| v1.7 `response_mode` non template | **Réel** | Ajouter clés v1.7 à `vars_dict` ou documenter append only |
| `TUTOR_PROMPT_PLACEHOLDERS.md` incomplet | **Doc** | Pointer vers ce fichier ; ajouter `history_block`, `conversation_profile`, `thread_guidance_block`, `posture_block` |

---

## 17. Exemple de template minimal conforme

**System :**
```
{base_system_intro}

{referential_block}

{learner_block}

{documents_block}

{history_block}
```

**User :**
```
{situation_content}

Phase: {session_phase}
Focus: {ui_focus_label}
Questions max ce tour: {max_questions_this_turn}
```

---

*Inventaire ancré code backend `hugo_back` — 2026-06-18. Ne pas inférer l’implémentation depuis la spec 2.0 seule.*
