<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# on y va

On part sur un cluster “multi‑postures”.

***

Tu travailles dans le workspace local suivant :

- `~/Desktop/zone de travail hugo/docs-workspace`
- `~/Desktop/zone de travail hugo/hugo_back`
- `~/Desktop/zone de travail hugo/hugo-hugolucia`
- `~/Desktop/zone de travail hugo/hugo-main`


## 0. Contexte et documents à lire

Lis d’abord, sans modifier :

- `docs-workspace/00_HIERARCHIE_DOCUMENTAIRE.md`
- `docs-workspace/DOC_METHODO_REFERENCE_CONVERGENCE_HUGO_REVISE.md`
- `docs-workspace/specs Orchestrateur diagnostic 2.0.md`
- `docs-workspace/specs formateur + tuteur 2.0.md`
- `docs-workspace/specs-interface-2.0.md` (sections posture / mode / UIState)
- `docs-workspace/03_ETAT_PRODUIT_REEL.md`
- `docs-workspace/05_ECARTS_DOC_CODE_PRODUIT.md`
- `docs-workspace/ecarts — 70_evaluation_traces_preuves.md` (pour le lien mode ↔ évaluation)[^1][^2]

Rappels :

- Toujours distinguer : réel observé, cible 2.0, écarts confirmés, `A_VERIFIER`, hypothèses.[^1]
- Backend‑first : partir du code Django (orchestrateur, services, modèles), puis seulement regarder UIState et front.[^1]
- Les 4 modes (diagnostic / réflexif / “bûchage” / évaluation) sont des **postures moteur**, pas juste des labels UI.


## 1. Objectif du cluster “multi‑postures”

Auditer et documenter le comportement réel des **modes/postures conversationnels** dans Hugo local, en couvrant :

- comment les modes sont représentés côté backend (modèles, enums, `ConversationPosture`, `teaching_plan`) ;
- comment ils sont choisis, changés et utilisés dans l’orchestrateur ;
- l’impact concret des modes sur : progression, mémoire, RAG, CTA synthèse/éval ;
- ce que le front montre réellement comme “mode” ou “posture” ;
- les écarts par rapport à la cible 2.0 multi‑postures.[^2][^1]

L’objectif n’est pas encore de refactorer, mais de préparer un **lot modes** exploitable par un CTO (contrats minimaux, backlogs).

## 2. Tâches Backend — postures \& orchestrateur

### 2.1 Cartographier les objets / enums de posture

1. Localiser dans `hugo_back` :
    - les enums / choix qui décrivent les postures ou modes (diagnostic, réflexif, révision/bûchage, évaluation) ;
    - les modèles ou structures qui les portent (`ConversationPosture`, `TeachingPlan`, `ConversationProfile`, etc.).
2. Pour chaque objet / enum trouvé, produire une fiche :
    - fichier + chemin ;
    - valeurs possibles et leur signification (telle que le code la laisse voir) ;
    - champs ou méthodes associés (ex : `allowed_pedagogical_moves`, flags RAG, flags de mémoire).[^2][^1]

### 2.2 Endpoint et logique `set-posture` / choix de mode

1. Localiser l’endpoint ou le service qui permet de **changer de posture** (ex : `PATCH /hugo/sessions/{id}/posture/` ou équivalent) dans `views_sessions.py` ou services associés.
2. Décrire pour ce flux :
    - route exacte, méthode HTTP, payload attendu ;
    - contrôles backend (phases où le changement est autorisé, garde sur la maturité ou le nombre de tours) ;
    - effet persistant : comment la posture est enregistrée dans la session / state.[^2][^1]
3. Identifier aussi comment la posture initiale est choisie au début de la conversation (paramètre de création de session, default, profil, etc.).

### 2.3 Impact des modes sur orchestrateur, mémoire, RAG, CTA

Dans `hugo_orchestrator.py` / services de décision :

1. Décrire comment la posture influe sur :
    - le **teaching_plan** ou `pedagogical_move` (types de tours possibles) ;
    - le gating RAG (`should_use_rag` selon posture / move) ;
    - le calcul de progression et d’éligibilité à la synthèse / évaluation ;
    - l’écriture de mémoire (`build_session_memory`) si des comportements spécifiques par mode existent.[^3][^4][^1]
2. Noter explicitement les cas où :
    - certains moves sont autorisés / interdits selon le mode (ex : pas d’évaluation en mode pur “bûchage”) ;
    - les CTA sont censés changer de sens ou de message selon la posture (même si pas encore bien exploité).[^5][^2]

## 3. Tâches Backend — UIState

1. Dans `ui_state_builder.py` / `conversation_profile.py`, identifier :
    - quels champs UIState portent aujourd’hui le **mode / posture** visibles côté apprenant (labels, codes, scènes, etc.) ;
    - comment ces champs sont dérivés de la posture réelle (ou si c’est encore partiel).[^5][^2]
2. Décrire :
    - ce qui est **déjà exposé** (ex : scène, mode, bannière) ;
    - ce qui manque pour un contrat clair “mode courant” (ex : enum explicite `conversation_mode`).
3. Lier à ce qui existe sur les CTA :
    - préciser si les CTA synthèse/éval actuels dépendent du mode (ou pas encore).[^5][^2]

## 4. Tâches Front — projection des modes

Dans `hugo-hugolucia/frontend_1.8` :

1. Localiser dans le front apprenant :
    - les composants qui affichent la **posture / mode** (ex : bandeau, selecteur de mode, labels type “Diagnostic”, “Révision”, etc.) ;
    - les composants qui permettent à l’apprenant de **changer de mode** (sélecteur, boutons).[^2]
2. Décrire :
    - quels champs du `/ui-state` sont lus pour afficher ce mode ;
    - comment le front appelle le backend pour changer de mode (endpoint, payload) ;
    - si certains textes UI varient en fonction du mode (ex : CTA évaluation présenté différemment en mode éval).
3. Si tu ne peux pas lancer Chromium, base-toi sur la lecture statique du code et des libellés.

## 5. Synthèse à produire

Ta réponse doit avoir ces sections :

1. `## Sources mobilisées`
    - fichiers backend (orchestrateur, services, modèles de posture) ;
    - endpoints mode/posture ;
    - fichiers UIState ;
    - fichiers front ;
    - docs `docs-workspace` utilisées.[^1][^2]
2. `## Réel confirmé`
    - comment les 3–4 modes existent réellement (noms, enums, champs) ;
    - comment ils sont choisis / changés ;
    - ce qu’ils changent effectivement dans le comportement (RAG, mémoire, CTA, progression) ;
    - ce que l’apprenant voit concrètement.[^3][^1][^2]
3. `## Cible 2.0 minimale pour les modes`
    - 1–2 paragraphes : modes comme postures moteur pilotées par état, multi‑postures réelles (diag / réflexion / bûchage / éval), articulées à la mémoire, au RAG et aux CTA.[^6][^7][^1]
4. `## Écarts confirmés`
    - par thème : représentation des postures, logique de changement, impact sur orchestrateur / RAG / mémoire / CTA, projection produit ;
    - avec statuts (ALIGNE, ALIGNE DOC PARTIEL, PARTIEL, A_VERIFIER, ABSENT / NOUVEAU CONTRAT).[^1]
5. `## Points A_VERIFIER`
    - flags runtime ou variantes non visibles en local ;
    - comportements éventuels en prod distante (ex : organisations avec modes spécifiques).[^1]
6. `## Prochaine sortie utile (DOC / CODE / OPS)`
    - DOC : contrat minimal “conversation_mode / posture” dans UIState + spec orchestrateur (qui fait quoi par mode) ;
    - CODE : petits ajustements possibles (ex : exposer explicitement `conversation_mode` dans UIState, durcir garde sur certains moves) ;
    - OPS : un ou deux scénarios de test (API / UI) pour vérifier les modes.[^1]

## 6. Garde-fous

- Ne pas déduire qu’un mode est “livré” parce qu’il apparaît dans la spec : vérifier son usage réel dans le code.
- Ne pas qualifier un mode de “profil psychologique” : rester sur posture pédagogique.
- Ne pas attribuer à un mode des effets sur RAG, mémoire ou CTA sans preuve dans le code (ou marquer clairement comme cible / hypothèse).

***

Quand tu auras la réponse de Cursor, colle-moi surtout les sections “Réel confirmé”, “Écarts confirmés” et “Prochaine sortie utile” et on les transformera en lot “modes” exploitable (contrat UIState + petits patches à prioriser).

<div align="center">⁂</div>

[^1]: plan_documentation_cto_convergence_hugo.md

[^2]: specs-interface-2.0.md

[^3]: 30_cursorops_templates.md

[^4]: 20_cursorops_templates.md

[^5]: 10_runtime_p0_progression_uistate_note_lot_courant_cta_synthese_evaluation.md

[^6]: specs Orchestrateur diagnostic 2.0.md

[^7]: specs formateur + tuteur 2.0.md

