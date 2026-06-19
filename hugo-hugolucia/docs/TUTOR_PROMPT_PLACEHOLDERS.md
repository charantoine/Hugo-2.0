# Clés de template `TutorPrompt` (Hugo)

Les champs `system_template` et `user_template` du modèle `TutorPrompt` sont des **chaînes au format Python** (`str.format`), avec des **placeholders nommés** `{nom}`.

Implémentation : `backend/apps/hugo/services/prompt_renderer.py` (`_base_vars`, `render_with_tutor_prompt`).

---

## Clés toujours fournies au rendu

Ces clés existent dans le dictionnaire passé à `.format(**vars_dict)` pour chaque tour où `render_with_tutor_prompt` est appelé (valeurs parfois vides : chaîne `""`, dict `{}`, liste vide).

| Clé | Type / forme | Description |
|-----|----------------|-------------|
| `base_system_intro` | `str` | Intro fixe Hugo + blocs état / décision / contraintes lorsque `TurnState` et `ConversationDecision` sont présents. |
| `referential_block` | `str` | Contexte référentiel (items à travailler / déjà travaillés) + **fusion** avec `focus_guidance_block` selon les cas (voir code). |
| `learner_block` | `str` | Synthèse progression apprenant, traces récentes. |
| `documents_block` | `str` | Titres des documents de classe actifs ; **si RAG** : concaténation avec `rag_chunks_block` (voir ci‑dessous). |
| `focus_guidance_block` | `str` | Bloc « focalisation pédagogique du tour » (focus, critères, couverture, etc.). Peut aussi être recollé dans `referential_block`. |
| `situation_content` | `str` | Texte du message apprenant du tour courant. |
| `organisation_id` | `str` | UUID organisation. |
| `session_id` | `str` | Identifiant de session. |
| `turn_state` | `dict` | État P0 / tour (`TurnState.to_dict()`), ou `{}` si absent. |
| `conversation_decision` | `dict` | Décision locale (`ConversationDecision.to_dict()`), ou `{}` si absent. |
| `turn_state_block` | `str` | Texte formaté « État conversationnel synthétique » (sous-ensemble lisible), ou vide. |
| `decision_block` | `str` | Texte formaté « Décision tutorale locale », ou vide. |
| `response_constraints_block` | `str` | Contraintes de réponse agrégées, ou vide. |
| `rag_chunks_block` | `str` | Bloc RAG formaté ; vide par défaut, rempli lorsque des `rag_chunks` sont fournis à `render_with_tutor_prompt`. |

---

## Clés conditionnelles : `TeachingPlan`

Ajoutées uniquement si `teaching_plan` n’est pas `None`.

| Clé | Type / forme | Description |
|-----|----------------|-------------|
| `teaching_plan` | `TeachingPlan` | Instance dataclass (attention au rendu direct dans le template : préférer des champs explicites). |
| `session_phase` | `str` | Phase de session issue du plan. |
| `focus_competence` | `dict` | Focus compétence / critère courant. |
| `regulation_targets` | `dict` | Cibles de régulation. |
| `max_questions_this_turn` | `int` | Nombre max de questions pour ce tour. |
| `ui_focus_label` | `str` | Libellé focus pour l’UI / le discours. |

---

## Clé conditionnelle : `CompetenceBrief`

| Clé | Type / forme | Description |
|-----|----------------|-------------|
| `competence_brief` | `CompetenceBrief` | Brief compétence ; présent seulement si l’argument `competence_brief` est fourni au renderer. |

---

## Clés RAG (extraits documentaires)

Ajoutées / mises à jour lorsque `rag_chunks` est une liste **non vide** passée à `render_with_tutor_prompt`.

| Clé | Type / forme | Description |
|-----|----------------|-------------|
| `rag_chunks` | `list[str]` | Liste des snippets (texte) issus de la sélection RAG. |
| `rag_chunks_block` | `str` | Bloc « Appuis documentaires situés : » + lignes par extrait. |
| `documents_block` | `str` | **Réécrit** : contenu documents de classe + `rag_chunks_block`, ou seulement `rag_chunks_block` s’il n’y a pas de titres classe. |

---

## Notes d’usage

1. **Format Python** : `{cle}` pour un nom simple ; pour un dictionnaire ou objet, utiliser l’indexation ou les attributs supportés par `str.format` (ex. éviter `{turn_state}` seul si la représentation par défaut ne convient pas — préférer `turn_state_block` ou des champs dédiés).
2. **Redondance** : `base_system_intro` peut déjà inclure des extraits présents dans `turn_state_block` / `decision_block` / `response_constraints_block` ; les blocs séparés servent à les injecter aussi ailleurs dans le template.
3. **Référence code** : `backend/apps/hugo/services/prompt_renderer.py` (fonctions `_build_blocks`, `_build_focus_guidance_block`, `_base_vars`, `render_with_tutor_prompt`).

4. **RAG documentaire** : alimentation des extraits via documents liés au groupe — voir [RAG_GROUP_LIBRARY.md](RAG_GROUP_LIBRARY.md).
