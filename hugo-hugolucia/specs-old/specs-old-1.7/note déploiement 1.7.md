
***

# Note synthétique – Déploiement Hugo P0 1.7

## 1. Objet

Déployer une évolution **Hugo P0 1.7** qui corrige les défauts de l’état actuel (ÉTAT_1) et rapproche le runtime de la cible Hugo 1.6 : moteur de régulation tutorale piloté par état, un seul objectif de régulation par message, 0–2 questions brèves cohérentes.[^1][^2]

## 2. Problèmes adressés

P0 1.7 vise à corriger, sans changer le périmètre AFEST ni les invariants de sécurité :[^3][^1]

- Demandes d’aide explicites mal traitées ou trop tard.
- Questions répétées sur des points déjà stabilisés (boucles).
- Passage raté vers récap / texte pour formateur / compétences alors que la scène est mûre.
- Décision backend correcte mais forme de réponse LLM non alignée (trop interrogative, listes, réouverture).


## 3. Principes d’implémentation

On **ne réécrit pas** l’architecture, on renforce le P0 existant :[^4][^1]

- Pipeline conservé : `context → analyze_turn_state → classify_p0_turn_state → decide_conversation → phase_decider → teaching_plan → prompt → LLM → guardrails`.
- Backend déterministe reste le pilote : le LLM n’a pas la main sur le but du tour, seulement sur la réalisation.
- Nouveau schéma d’état (`TurnStateV17`) et de décision (`ConversationDecisionV17`) en **snake_case**, testables unitairement, avec adaptateur de compatibilité.


## 4. Évolutions clés

1. **État de tour enrichi** (`TurnStateV17`)
    - Regroupe les signaux actuels + nouveaux booléens de maturité : `reflective_minimum_reached`, `recap_evaluation_eligible`, `closure_eligible`, etc.
    - Reste compatible avec les champs P0 existants via un wrapper.[^1]
2. **Décision explicite** (`ConversationDecisionV17`)
    - `primary_intent`, `pedagogical_move`, `response_mode`, `target_question_count` (0–2), `reason_codes`.
    - `response_mode` pilote la forme de sortie (assist / reflect / recap / evaluation / closure).[^1]
3. **Lecture des actes de langage apprenant**
    - Nouveau classifieur `learner_speech_act` + `last_learner_act` (aide, récap, texte tuteur, compétences, clôture, confusion, etc.).
    - Règle forte : une demande explicite (aide, bilan, compétences, clôture) **ne peut plus être noyée** dans la logique générique.[^4][^1]
4. **Pré‑routage “speech‑act first”**
    - Fonctions d’override qui forcent la décision dans les cas clairs :
        - Texte pour formateur → `response_mode = recap`, `metadata.audience = tutor`.
        - Vue compétences mûre → `response_mode = evaluation`, `metadata.evaluation_kind = recap_with_competencies`.
        - Clôture → `response_mode = closure`, 0 question.[^1]
5. **Hiérarchie décisionnelle explicite**
    - Ordre obligatoire :

6. Demandes explicites (aide / récap / compétences / rapport / clôture).
7. Sécurité / qualité.
8. Répétition / risque de boucle.
9. Maturité de couverture (`recap_evaluation_eligible`).
10. Fallback P0 historique.[^4][^1]
1. **Guardrails de sortie réalistes**
    - `response_mode` et `target_question_count` sont appliqués jusqu’au post‑traitement :
        - `target_question_count = 0` → aucune question dans la sortie finale.
        - Modes recap / evaluation / closure → texte continu, **sans listes ni checklists**, pas de batteries de questions.
    - Les anciens formats trop interrogatifs sont neutralisés s’ils contredisent la décision.[^4][^1]

## 5. Plan de déploiement

- Implémentation dans des modules `*_v17.py` activés par **feature flag** pour comparaison old vs new.[^4]
- Jeux de tests d’acceptation dérivés des verbatims (aide explicite, priorité, répétition, scène mûre, récap/rapport/compétences, respect de `target_question_count`).[^1][^4]
- Aucune modification des invariants sécurité / multi‑tenant / RAG / posture AFEST d’Hugo 1.6.[^2]

***

