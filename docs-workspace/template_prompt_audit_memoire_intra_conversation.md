Prompt Cursor — audit / convergence mémoire intra‑conversation (lot courant)

Contexte (ne pas modifier dans la réponse)

    Projet local : ~/Desktop/zone de travail hugo/ avec au moins :

        hugo_back/ (Django, orchestrateur, mémoire)

        hugo-hugolucia/ (front apprenant)

        docs-workspace/ (docs d’audit réel et docs de convergence).

    Dans ce lot, la mémoire gouvernée cible est réduite à une mémoire intra‑conversation utile pour la continuité du fil courant, sans inter‑sessions activée, pas de verbatim brut, pas de P0 exposé au front.

    Le contrat ci‑dessous est un contrat de convergence pour ce lot, pas une description du runtime actuel.

Fichiers à ouvrir avant d’analyser

Avant de répondre, ouvre systématiquement :

- docs-workspace/ecarts — 20_memoire_gouvernee.md
- docs-workspace/20_memoire_gouvernee_note_lot_courant_memoire_intra_conversation.md
- docs-workspace/specs-interface-2.0.md
- hugo_back/apps/hugo/services/session_memory.py
- hugo_back/apps/hugo/domains/schemas.py
- hugo_back/apps/hugo/services/hugo_orchestrator.py
- hugo_back/apps/hugo/views/sessions.py
- les tests existants liés à la mémoire de session (par ex. test_p0_v17_flow.py, test_session_memory_contract.py si présent)

1. Contrat cible minimal — mémoire intra‑conversation (lot courant)

Objectif : décrire la mémoire utile du fil courant que le backend produit et consomme, et qui peut être projetée proprement (via UIState ou endpoint dédié) sans verbatim brut.

```json
{
  "session_memory": {
    "session_id": "<uuid>",
    "updated_at": "ISO datetime",

    "theme": {
      "label": "texte court lisible",
      "tags": ["string"]
    },

    "learning_objective": {
      "label": "objectif pédagogique courant (phrase courte)",
      "status": "in_progress | reached | abandoned"
    },

    "facts_confirmed": [
      {
        "label": "fait ou décision confirmé dans le fil",
        "confirmed_at": "ISO datetime"
      }
    ],

    "open_points": [
      {
        "label": "question ou point encore ouvert",
        "priority": "normal | blocking"
      }
    ],

    "pending_actions": [
      {
        "label": "action à faire dans ce fil (par l'apprenant ou le tuteur)",
        "due_in_turns": 3
      }
    ],

    "memory_scope": "session"
  }
}
```

Contraintes :

    Cette mémoire est intra‑conversation uniquement : elle ne prétend pas être la mémoire inter‑session LearnerThemeMemory.

    Elle est générée et mise à jour côté backend (par ex. build_session_memory / session_memory.py), jamais par le front.

    Elle ne contient aucun verbatim brut ni champs P0 bruts, seulement des résumés gouvernés et partageables.

2. Ta mission dans le code

2.1 Repérer les points clés du backend

À partir des fichiers ouverts :

- Localiser et décrire :

  - le service de mémoire de session (build_session_memory, session_memory.py ou équivalent) ;
  - les objets de schéma associés (SessionMemorySummary, SessionMemoryContract ou équivalents) ;
  - le point d’appel dans build_hugo_turn (hugo_orchestrator.py) ;
  - l’endpoint GET /hugo/sessions/{session_id}/memory-summary (views/sessions.py).

- Décrire précisément, sans extrapolation :

  - la signature du service mémoire ;
  - la structure réelle de la mémoire de session (champs, types, valeurs par défaut) ;
  - la manière dont elle est injectée dans HugoTurn et dans UiState ;
  - le contrat JSON réel de memory-summary.

2.2 Analyse alignement vs contrat intra‑conversation

Comparer le contrat JSON ci‑dessus avec :

- la structure réelle retournée par la mémoire de session ;
- ce qui est éventuellement exposé par memory-summary pour le fil courant.

Pour chaque rubrique du contrat (session_id, updated_at, theme, learning_objective, facts_confirmed, open_points, pending_actions, memory_scope) :

- indiquer si elle est :

  - ALIGNE
  - ALIGNE_DOC_PARTIEL
  - AMBIGU
  - A_VERIFIER
  - ABSENT / NOUVEAU CONTRAT

2.3 Vérifier les interdits

Vérifier explicitement, dans le code et les structures JSON :

- qu’aucun message.content (verbatim brut) n’est traité comme mémoire principale dans session_memory ou memory-summary ;
- qu’aucun champ P0 brut n’est projeté dans session_memory ou dans memory-summary comme surface mémoire destinée au produit ;
- que LearnerThemeMemory et MemoryConsolidator ne sont pas présentés comme moteurs actifs de la conduite du tour courant dans build_hugo_turn pour ce lot (sauf preuve claire inverse).

2.4 Proposer des diffs backend (additifs)

Proposer des patchs additifs pour :

- structurer session_memory selon le contrat ci‑dessus dans la couche qui produit la mémoire intra‑session ;
- garantir la séparation propre entre mémoire de session (fil courant) et mémoire thématique inter‑session exposée par memory-summary ;
- s’assurer que rien de ce qui est projeté comme mémoire intra‑conversation ne contient de verbatim brut ni de champs P0 ;
- si memory-summary est utilisé pour la session courante, expliquer comment l’adapter pour qu’il expose uniquement ce résumé gouverné, pas l’historique brut.

Ne pas activer/modifier la logique de consolidation inter‑session dans ce lot : MemoryConsolidator et LearnerThemeMemory restent des points de convergence pour plus tard.

2.5 Tests

Proposer des tests backend qui vérifient au minimum :

- que la structure session_memory respecte le contrat JSON minimal (champs obligatoires, types) ;
- que la mémoire de session ne contient jamais de verbatim brut de message utilisateur/tuteur ;
- que l’ajout de nouveaux tours met bien à jour facts_confirmed, open_points et pending_actions sans casser la compatibilité avec le contrat ;
- que memory_scope vaut bien "session" dans le contexte de ce lot.

3. Structure de réponse attendue

Structure ta réponse avec EXACTEMENT les sections suivantes :

- ## Sources mobilisées
- ## Réel confirmé
- ## Cible lot courant
- ## Écarts confirmés
- ## Points A_VERIFIER
- ## Diffs backend proposés
- ## Tests proposés
- ## Backlog DOC / CODE / OPS

4. Backlog DOC / CODE / OPS

Dans la section « Backlog DOC / CODE / OPS », liste les actions sous forme de tableau Markdown avec les colonnes suivantes :

- ID (préfixé MEM‑, ex. MEM‑C01)
- Type (DOC, CODE, OPS)
- Pri (P0, P1, P2)
- Source (référence à une section de ta réponse)
- Intitulé court
- Livrable attendu

5. Discipline de méthode

Dans toute ta réponse :

- distingue explicitement réel observé, cible spécifiée, écarts confirmés, points A_VERIFIER et hypothèses ;
- ne présente jamais la cible 2.0 complète comme déjà livrée ;
- ne recentre pas la vérité comportementale sur le front : la source reste le backend, la mémoire, l’orchestrateur et UIState ;
- ne réintroduis pas le verbatim brut comme mémoire principale ;
- ne présentes pas la mémoire inter‑session comme livrée ou injectée dans le runtime du tour tant que le code ne le prouve pas.