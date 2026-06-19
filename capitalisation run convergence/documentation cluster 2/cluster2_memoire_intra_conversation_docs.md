# Mise à jour docs cluster 2 – mémoire intra‑conversation

## 1. Patch à ajouter dans `ecarts — 20_memoire_gouvernee.md`

### 3.4 Cible d’implémentation retenue pour le lot courant

Conformément à l’addendum méthodologique de juin 2026 et au plan de convergence CTO, la cible d’implémentation retenue pour le lot courant du domaine mémoire est volontairement réduite à la mémoire gouvernée intra‑conversation. Cette réduction de périmètre ne remplace pas la cible 2.0 complète ; elle fixe la cible praticable et sécurisable à court terme pour le développement local.

Dans ce lot, la mémoire utile doit se comporter comme une mémoire de conversation courante : synthétique, discrète, pilotée backend, utile à la continuité tutorale du fil et non comme un historique brut ou un profil durable apprenant. L’inter‑sessions reste préparée dans les objets, les modèles et les contrats, mais elle ne doit pas être décrite comme déjà active dans la conduite du tour courant sans preuve d’audit complémentaire.

Le contrat JSON minimal à retenir pour cette mémoire intra‑conversation est le suivant :

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
      "label": "objectif pédagogique courant",
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
        "label": "action à faire dans ce fil",
        "due_in_turns": 3
      }
    ],
    "memory_scope": "session"
  }
}
```

Ce contrat doit être lu comme un contrat de convergence : assez précis pour guider les ajustements backend, UIState et tests, mais sans transformer la cible lot courant en fait déjà prouvé dans tous les artefacts runtime existants.

Les garde‑fous applicables sur ce sous‑bloc sont les suivants :

- pas de verbatim brut dans la mémoire gouvernée ;
- pas de champs P0 bruts exposés au front produit via session memory ou ses projections ;
- pas de description de `LearnerThemeMemory` comme mémoire active du fil courant tant que ce point n’est pas démontré ;
- pas de glissement documentaire où `memory-summary` serait automatiquement lu comme preuve suffisante d’une mémoire thématique complète déjà stabilisée ;
- séparation explicite entre mémoire de session intra‑conversation et mémoire thématique inter‑sessions dans tous les futurs contrats et prompts Cursor.

Cette cible lot courant permet de relire plus proprement les écarts du domaine : le socle mémoire réel n’est plus absent, mais encore partiellement canonisé. Le bon geste n’est donc pas d’ouvrir immédiatement un grand chantier inter‑sessions, mais de figer d’abord le contrat minimal de session memory, ses surfaces de projection, ses interdits et ses tests.

---

## 2. Bloc à insérer dans `specs-interface-2.0.md`

### Session memory — contrat minimal lot courant

Dans la trajectoire locale de convergence, la mémoire visible ou relisible dans l’expérience apprenant doit d’abord converger vers une mémoire gouvernée intra‑conversation, utile à la continuité du fil courant. Cette section décrit le contrat cible minimal de cette mémoire pour le lot courant ; elle ne prouve pas que toutes les rubriques sont déjà livrées dans le runtime local.

#### Principes

- La mémoire utile du fil courant est un résumé gouverné et non un verbatim brut.
- Elle est produite et mise à jour côté backend, puis projetée via UIState ou un objet dérivé ; le front ne la calcule jamais lui‑même.
- Elle doit aider à la continuité du fil, à la reprise du thème actif et à la lisibilité des points ouverts, sans exposer la mécanique interne du moteur.
- Elle ne doit pas être décrite comme une mémoire inter‑sessions déjà active dans ce lot.

#### Contrat cible minimal

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
      "label": "objectif pédagogique courant",
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
        "label": "action à faire dans ce fil",
        "due_in_turns": 3
      }
    ],
    "memory_scope": "session"
  }
}
```

#### Interdits

- Ne jamais exposer de verbatim brut ou d’historique complet comme pseudo‑mémoire gouvernée.
- Ne jamais exposer de champs P0 bruts dans `session_memory` ou dans les blocs UI qui le consomment.
- Ne pas dériver un profil apprenant durable à partir de cette mémoire de fil dans le lot courant.
- Ne pas présenter `LearnerThemeMemory` comme équivalent direct de cette structure tant que l’audit code ne le prouve pas pour la conduite du tour courant.

#### Raccord avec l’inter‑sessions

L’inter‑sessions peut exister dans le backend sous forme de modèles, de consolidateurs et de points d’extension, mais elle doit être documentée séparément. Dans le lot courant, `session_memory` décrit uniquement la continuité gouvernée du fil courant.

---

## 3. Prompt Cursor — audit / convergence mémoire intra‑conversation

### Contexte

Projet local : `~/Desktop/zone de travail hugo/` avec au moins :

- `hugo_back/` (backend Django, orchestrateur, mémoire)
- `hugo-hugolucia/` (front apprenant)
- `docs-workspace/` (docs d’audit réel et docs de convergence)

Dans ce lot, la mémoire gouvernée cible est réduite à une mémoire intra‑conversation utile à la continuité du fil courant. L’inter‑sessions est préparée doctrinalement et contractuellement, mais reste hors périmètre d’implémentation immédiat. Aucun verbatim brut ni champ P0 brut ne doit être exposé au front comme mémoire gouvernée.

Le contrat ci‑dessous est un contrat de convergence pour le lot courant, pas une description automatique du runtime actuel.

### Fichiers à ouvrir dans Cursor

Avant de répondre, ouvre systématiquement :

- `docs-workspace/ecarts — 20_memoire_gouvernee.md`
- `docs-workspace/20_memoire_gouvernee_note_lot_courant_memoire_intra_conversation.md`
- `docs-workspace/specs-interface-2.0.md`
- `hugo_back/apps/hugo/services/session_memory.py`
- `hugo_back/apps/hugo/domains/schemas.py`
- `hugo_back/apps/hugo/services/hugo_orchestrator.py`
- `hugo_back/apps/hugo/views/sessions.py`
- les tests existants liés à la mémoire de session (par ex. `test_p0_v17_flow.py`, `test_session_memory_contract.py` si présent)

### Contrat cible minimal — mémoire intra‑conversation

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
        "label": "action à faire dans ce fil",
        "due_in_turns": 3
      }
    ],
    "memory_scope": "session"
  }
}
```

### Mission

1. Lire le réel observé

Dans `hugo_back`, audite au minimum :

- le service de mémoire de session (`build_session_memory`, `session_memory.py` ou équivalent) ;
- `domains/schemas.py` pour `SessionMemorySummary`, `SessionMemoryContract` ou objets voisins ;
- `hugo_orchestrator.py` pour le point d’appel dans `build_hugo_turn` ;
- `views/sessions.py` pour l’endpoint `GET /hugo/sessions/{session_id}/memory-summary` ;
- les tests existants liés à la mémoire de session ;
- les points d’injection ou de consommation de `session_memory` dans la construction de UIState.

Décris précisément :

- la signature du service mémoire ;
- la structure JSON réellement produite pour la mémoire de session ;
- la manière dont elle est injectée dans le tour et dans UIState ;
- le contrat JSON réel de `memory-summary` ;
- l’état réel de `LearnerThemeMemory` et `MemoryConsolidator` dans ce lot.

2. Comparer le réel au contrat cible lot courant

Pour chaque rubrique du contrat (`session_id`, `updated_at`, `theme`, `learning_objective`, `facts_confirmed`, `open_points`, `pending_actions`, `memory_scope`) :

- indique si elle est **ALIGNE** ;
- **ALIGNE DOC PARTIEL** ;
- **AMBIGU** ;
- **A_VERIFIER** ;
- ou **ABSENT / NOUVEAU CONTRAT**.

3. Vérifier les interdits et garde‑fous

Vérifie explicitement, dans le code et dans les JSON exposés :

- qu’aucun verbatim brut `message.content` n’est traité comme mémoire principale ;
- qu’aucun champ P0 brut n’est projeté dans `session_memory` ou dans `memory-summary` comme surface mémoire destinée au produit ;
- que l’inter‑sessions n’est pas sur‑affirmée comme source active de la conduite du tour courant ;
- que la mémoire visible reste backend‑first et projetée par objets dérivés, non calculée côté front.

4. Proposer des diffs backend additifs

Propose des patchs backend additifs pour :

- structurer `session_memory` selon le contrat cible minimal ;
- garantir la séparation propre entre résumé de session et mémoire thématique inter‑sessions ;
- sécuriser l’absence de verbatim brut et de P0 dans les surfaces mémoire gouvernées ;
- adapter si besoin `memory-summary` pour qu’il ne soit plus ambigu sur le lot courant ;
- ajouter les schémas et sérialisations nécessaires sans casser les compatibilités utiles.

Ne pas ouvrir dans ce lot un chantier de consolidation inter‑sessions ou de refonte générale du store mémoire. `LearnerThemeMemory` et `MemoryConsolidator` restent des points d’extension future.

5. Proposer les tests à ajouter

Prépare ou complète des tests backend vérifiant au minimum :

- la conformité du JSON `session_memory` au contrat minimal ;
- l’absence de verbatim brut dans les surfaces mémoire ;
- l’absence de champs P0 bruts dans les blocs mémoire destinés au produit ;
- l’évolution correcte de `facts_confirmed`, `open_points` et `pending_actions` après plusieurs tours ;
- la séparation explicite entre `session_memory` et mémoire inter‑sessions si `memory-summary` expose les deux.

6. Structurer la réponse

Structure ta réponse avec exactement les sections suivantes :

- `## Sources mobilisées`
- `## Réel confirmé`
- `## Cible lot courant`
- `## Écarts confirmés`
- `## Points A_VERIFIER`
- `## Diffs backend proposés`
- `## Tests proposés`
- `## Backlog DOC / CODE / OPS`

7. Backlog DOC / CODE / OPS

Dans la section `## Backlog DOC / CODE / OPS`, liste les actions sous forme de tableau Markdown avec les colonnes suivantes :

- `ID` (préfixé MEM‑, ex. `MEM‑C01`)
- `Type` (`DOC`, `CODE`, `OPS`)
- `Pri` (`P0`, `P1`, `P2`)
- `Source` (référence à une section de ta réponse)
- `Intitulé court`
- `Livrable attendu`

8. Discipline de méthode

Dans toute la réponse :

- distingue explicitement réel observé, cible spécifiée, écarts confirmés, points A_VERIFIER et hypothèses ;
- ne présente jamais la cible 2.0 comme déjà livrée ;
- ne recentre pas la vérité comportementale sur le front ;
- ne réintroduis pas le verbatim brut comme mémoire principale ;
- ne présente pas `LearnerThemeMemory` comme moteur actif du tour courant sans preuve complémentaire.
