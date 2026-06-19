

> **Statut implémentation locale (2026-06-18)** — Interface apprenant : UIState, CTA (`ui.advisory`), posture/scène (`PostureSelector`, `LearnerSceneContextBar`), mémoire (`LearnerMemoryPanel`), profils `learner_display_profile` = **PARTIEL+ livré** (clusters 15–16 ; 15 backend + 10 Playwright PASS). Interface formateur : **PARTIEL**. Orchestrateurs complets, intercalaires, RAG vectoriel = **CIBLE**. Détail : `cluster2_matrice_runtime_vs_cible.md` V5.

## Interface apprenant

### Structure visible de la conversation

- L’interface doit être construite à partir d’un **UIState propre** (et non des champs P0) qui expose au minimum : scène (phase de séance), progression, quête ou branche active, couleur de maturité, état des boutons synthèse/évaluation, objets persistants éventuels, profil d’engagement.[^2][^1]
- La scène suit une grammaire simple type “Raconter / Comprendre / Décider”, couplée à la **branch principale** et à la progression calculée (ConversationProgress : maturité RED/ORANGE/GREEN, priority_branch, dispersion_risk).[^1][^2]
- Le **mode actif** (diagnostic / réflexif / révision / évaluation) doit être perceptible : la présence de ConversationPosture, d’un endpoint `set-posture`, de postureselector et de posturetransitions implique un **état de posture affichable** côté UI.[^3][^2][^1]

En pratique, tu as donc au minimum, côté apprenant :

- un **panneau de progression** (HugoProgressPanel) lisant `/ui-state` ;
- un affichage de la **scène** (phase de séance) et de la **branche/objectif courant** ;
- un indicateur de **maturité** (code couleur ou label) ;
- un affichage du **mode** ou au moins de la posture (diagnostic / réflexif / révision).[^2][^3][^1]


### Commandes et contrôle utilisateur

- Un **sélecteur de posture**/mode est prévu : endpoint PATCH `/sessions/{id}/posture/`, bloqué après un certain nombre de messages et de phase (pas de changement en séance avancée).[^3]
- Les **actions terminales** (synthèse / évaluation) apparaissent comme boutons ou CTA dont l’état dépend de l’éligibilité calculée (via ConversationProgress + P0 `optionalevaluationeligible`).[^1][^2]
- La reprise de fil, bifurcation, clôture sont articulées sur le concept de **ConversationBranch** (branche principale, branches secondaires limitées, risque de dispersion).[^2][^1]

Ce qui est clair :

- L’apprenant peut **choisir une posture en début de fil**, dans des conditions sûres (phase d’ouverture, peu de messages).[^3]
- Il voit **s’il peut lancer une synthèse ou une évaluation** (boutons actifs/inactifs d’après /ui-state).[^1][^2]

Ce qui manque encore :

- La palette exacte d’actions “relance / reprise de fil / demande de bascule” n’est pas listée exhaustivement.
- Le statut visuel “déconseillé / forcé” pour l’évaluation est seulement suggéré (via notion d’éligibilité + reasoncodes) mais pas spécifié UI.


### Grammaire UI fine

- Le fil insiste sur une **structure front lisible** plutôt que sur des micro‑composants nommés, mais on voit émerger :
    - un **panneau de progression** (ProgressPanel) ;
    - des **labels de scène** et de **quête active** ;
    - des **boutons synthèse / évaluation** avec états (actif / grisé / caché) ;
    - des **objets persistants** dans UIState pour porter les éléments durables (mémos, capsules, traces à confirmer).[^2][^1]
- Il est explicitement interdit de montrer des **signaux techniques P0** (scores, variables internes) dans le front : UIState est le seul modèle produit montrable.[^1]
- Certains objets (mémoire thématique, verbatim interne, reasoncodes détaillés) doivent rester **implicites** pour l’apprenant, même si le moteur les utilise pour décider.[^2][^1]

En résumé, la grammaire UI apprenant doit rendre explicites :

- “où j’en suis” (scène, progression, branche active, maturité) ;
- “dans quel régime je suis” (diagnostic / réflexif / révision / évaluation) ;
- “ce que je peux faire maintenant” (parler, demander, synthétiser, évaluer) ;

…sans exposer P0 brut ni la mécanique interne de mémoire.

### ### Session memory — contrat minimal lot courant

Dans la trajectoire locale de convergence, la mémoire visible ou relisible dans l’expérience apprenant doit d’abord converger vers une mémoire gouvernée intra‑conversation, utile à la continuité du fil courant. Cette section décrit le contrat cible minimal de cette mémoire pour le lot courant ; elle ne prouve pas que toutes les rubriques sont déjà livrées dans le runtime local.

#### Principes

- La mémoire utile du fil courant est un résumé gouverné et non un verbatim brut.
- Elle est produite et mise à jour côté backend, puis projetée via UIState ou un objet dérivé ; le front ne la calcule jamais lui‑même.
- Elle sert à reprendre le thème actif, l’objectif, les faits établis, les points ouverts et les actions à venir, sans exposer la mécanique interne du moteur.
- Elle ne doit pas être décrite comme une mémoire inter‑sessions déjà active dans ce lot.

#### Contrat cible minimal

```json
{
  "session_memory": {
    "session_id": "<uuid>",
    "updated_at": "ISO-8601 datetime",
    "theme": "string",
    "learning_objective": "string",
    "facts_confirmed": ["string"],
    "open_points": ["string"],
    "pending_actions": ["string"],
    "memory_scope": "intra_conversation"
  }
}
```

#### Interdits

- Ne jamais exposer de verbatim brut ou d’historique complet comme pseudo‑mémoire gouvernée.
- Ne jamais exposer de champs P0 bruts dans `session_memory` ou dans les blocs UI qui le consomment.
- Ne pas dériver un profil apprenant durable à partir de cette mémoire de fil dans le lot courant.
- Ne pas présenter `LearnerThemeMemory` comme équivalent direct de cette structure tant que l’audit code ne le prouve pas pour la conduite du tour courant.

### Endpoint `GET /hugo/sessions/{id}/memory-summary/` — lot courant

Dans le lot courant, l’endpoint `GET /hugo/sessions/{id}/memory-summary/` renvoie une projection structurée qui distingue le fil courant et la préparation inter‑sessions. Cette projection ne doit pas être relue comme « mémoire unique du fil », ni comme preuve que la mémoire inter‑sessions est déjà injectée dans le runtime.

#### Contrat cible minimal

```json
{
  "session_memory": {
    "session_id": "<uuid>",
    "updated_at": "ISO-8601 datetime",
    "theme": "string",
    "learning_objective": "string",
    "facts_confirmed": ["string"],
    "open_points": ["string"],
    "pending_actions": ["string"],
    "memory_scope": "intra_conversation"
  },
  "theme_memories": [
    {
      "theme_key": "string",
      "stabilised": ["string"],
      "open_loops": ["string"],
      "difficulties": ["string"],
      "status": "DERIVED_PROVISIONAL",
      "last_session": "<uuid>",
      "updated_at": "ISO-8601 datetime"
    }
  ]
}
```

#### Lecture doctrinale

- `session_memory` correspond à la mémoire gouvernée du fil courant.
- `theme_memories` correspond à une mémoire inter‑sessions **préparée** (LearnerThemeMemory / MemoryConsolidator), mais non injectée dans l’orchestrateur dans ce lot.
- La documentation doit éviter de présenter `memory-summary` comme « la mémoire du fil » seule : elle expose à la fois fil courant et consolidation thématique préparée.



### Profils d’affichage apprenant (cible 2.0)

Dans la cible 2.0, l’affichage apprenant repose toujours sur un même contrat UIState canonique (scène, progression, quête ou branche active, couleur de maturité, posture ou mode, état des CTA terminales, objets persistants). Les variantes d’interface ne doivent jamais recalculer localement la progression, la posture, ni exposer P0 ou TurnState : elles lisent et restituent des champs dérivés côté backend, dans des grammaires visuelles différentes.

On distingue au minimum trois **profils d’affichage** apprenant, utilisables par les organisations selon leurs publics :
- un profil orienté jeunes en formation pro initiale (ordre de grandeur 16–20 ans), avec une interface plus graphique, des repères visuels explicites et une densité textuelle réduite ;
- un profil orienté adultes en reconversion intermédiaire (ordre de grandeur 20–35 ans) avec un équilibre texte/visuels adapté à une littératie numérique moyenne et à des usages alternant mobile et desktop ;
- un profil orienté ingénieurs / professions supérieures, plus proche de l’affichage discursif intermédiaire actuel, avec davantage de texte explicite et de repères conceptuels.

Ces profils d’affichage restent responsive, sobres et doux visuellement ; ils se différencient principalement par la densité textuelle, le registre graphique et les aides visuelles, pas par la logique pédagogique ni par les objets backend lus. Le choix d’un profil d’affichage peut être fait à l’échelle d’une organisation, d’un groupe, d’une cohorte ou d’un apprenant, selon des règles produit à préciser, mais il ne crée jamais trois moteurs différents ni trois contrats UIState concurrents.

Les profils d’affichage peuvent être enrichis par des « skins » cosmétiques optionnelles (thèmes graphiques, variations de couleur ou d’iconographie) proposées comme goodies produit. Ces skins ne modifient ni la structure de l’UI, ni les informations visibles minimales, ni les garde‑fous de confidentialité ; elles restent un niveau purement esthétique ajouté au‑dessus du profil d’affichage choisi.

Dans tous les cas :
- UIState reste l’unique modèle produit montrable côté apprenant ;
- aucun champ P0 brut, TurnState ou reason code technique n’est exposé ;
- les CTA terminales (synthèse, évaluation) gardent le même contrat d’éligibilité et de blocage, seul leur rendu graphique varie (libellés, icônes, aide contextuelle) ;
- les profils d’affichage ne doivent pas être décrits comme des « modes pédagogiques » concurrents, mais comme des présentations différenciées d’un même état produit.

> Niveau de vérité – Profils d’affichage apprenant  
> - Statut : CIBLE 2.0 (aucun multi-profil d’UI apprenant n’est démontré comme livré dans le runtime actuel).  
> - Lecture : cette section décrit des profils d’affichage cibles, lisant un UIState commun. Elle ne doit pas être relue comme preuve que plusieurs interfaces apprenant coexistent déjà en production.  
> - Dérivés : toute implémentation devra rester compatible avec les invariants existants (backend orchestré, P0 non exposé, UIState comme seule source UI montrable).

### Évaluation côté apprenant

- L’évaluation est présentée comme une **action terminale facultative**, éligible seulement lorsque certains critères sont réunis (maturité séance, charge/risk, base structurée) : cet état d’éligibilité doit être reflété par l’UI (bouton d’évaluation activable vs inactif).[^1][^2]
- Le fil suggère implicitement trois états :
    - non éligible (bouton absent/grisé) ;
    - éligible (bouton actif, éventuellement avec message “possible maintenant”) ;
    - éligible mais **déconseillé** si l’utilisateur force malgré un warning (scénario évoqué dans ta doctrine cible, pas explicitement détaillé dans les docs).[^2]

Manques :

- pas de description formelle des messages de prudence (“c’est un peu tôt pour évaluer”) ;
- pas de code couleur précis (genre vert = recommandé, orange = possible mais déconseillé).

### CTA synthèse / évaluation — contrat minimal lot courant

Dans le lot courant, les actions terminales de synthèse et d’évaluation sont pilotées par le backend via des champs dédiés dans `ui_state`. Ce contrat vise à standardiser les états, les raisons de blocage et les endpoints associés, sans prétendre que toute la chaîne d’évaluation 2.0 est déjà livrée.

#### Principes

- Les CTA sont des **actions terminales facultatives** pour l’apprenant.
- L’**éligibilité** et les **raisons de blocage** sont calculées côté backend et projetées dans `ui_state`.
- Le front ne recalcule pas l’éligibilité : il lit `ui_state.cta_evaluation` et `ui_state.cta_synthesis` et affiche les boutons en conséquence.
- Aucune formulation produit ne doit laisser entendre que Hugo délivre une **certification autonome** : la validation finale reste humaine.

#### Contrat cible minimal (UIState)

```json
{
  "cta_evaluation": {
    "evaluation_ready_status": "eligible | blocked_min_turns_not_reached | blocked_context_incomplete | blocked_missing_data | blocked_other",
    "blocking_reasons": ["liste courte de raisons lisibles, non P0"],

    "endpoints": {
      "request_evaluation": "/hugo/sessions/{session_id}/request-evaluation/",
      "finalize_evaluation": "/hugo/sessions/{session_id}/finalize-evaluation/",
      "evaluation_readiness": "/hugo/sessions/{session_id}/evaluation-readiness/"
    },

    "ui": {
      "show_evaluation_button": true,
      "button_label": "Demander une évaluation",
      "button_disabled": false,
      "helper_text": null
    },

    "last_evaluation": {
      "status": "none | completed | failed",
      "completed_at": "ISO-8601 datetime ou null"
    }
  },

  "cta_synthesis": {
    "synthesis_ready_status": "eligible | blocked_not_enough_content | blocked_context_incomplete | blocked_other",
    "blocking_reasons": ["liste courte de raisons lisibles, non P0"],

    "endpoints": {
      "request_synthesis": "/hugo/sessions/{session_id}/request-synthesis/"
    },

    "ui": {
      "show_synthesis_button": true,
      "button_label": "Obtenir une synthèse",
      "button_disabled": false,
      "helper_text": null
    }
  }
}
```

#### Contraintes

- Les champs `evaluation_ready_status` et `synthesis_ready_status` sont des **énums fermés**, pas des chaînes libres.
- `blocking_reasons` contient des messages lisibles destinés à l’apprenant, sans dumps techniques ni champs P0.
- Les endpoints listés correspondent aux routes réelles de ce lot (`/hugo/sessions/{id}/request-synthesis/`, pas `generate-synthesis`).
- Les textes définitifs (`button_label`, `helper_text`) peuvent varier, mais la structure et les états doivent rester conformes à ce contrat.

#### Effets côté front

- Bouton d’évaluation :
  - affiché si `cta_evaluation.ui.show_evaluation_button == true` ;
  - désactivé si `cta_evaluation.ui.button_disabled == true` ;
  - les messages d’aide proviennent de `cta_evaluation.ui.helper_text` ou, à défaut, d’une interprétation simple de `blocking_reasons`.
- Bouton de synthèse :
  - piloté de la même manière par `cta_synthesis.ui.*`.
- L’UI ne lit pas directement les endpoints d’évaluation ou les signaux P0 : elle passe par `ui_state.cta_*` uniquement.

### Fin de fil — EvaluationTrace pivot (lot vague 3)

Le runtime local expose un **pivot minimal** `evaluation_trace_pivot_v1` (builder backend), distinct de l’agrégat doctrinal EvaluationTrace 2.0 complet. Ce pivot relie session, `LearnerEvaluationRecord`, `Trace`, preuves `Evidence` et statut de validation humaine.

- **Producteur** : `generate-trace`, ExportRun JSON (`trace_rich_v1`).
- **Consommateurs autorisés** : encadrants via exports / traces partagées — pas de nouvelle UI apprenant dans ce lot.
- **Non exposé** : UIState apprenant, EvidenceBundle lite (métadonnées seulement).
- **Disclaimer** : artefact de suivi pédagogique — validation humaine requise ; non certifiant.

### Observabilité de base (non frontalisée)

Signaux techniques backend (compteurs CTA bloqués, tours, `ConversationQualitySignal`) accessibles via endpoint admin `/internal/hugo/sessions/{id}/observability/` — **hors UX apprenant**. ORGADMIN et SUPERADMIN.

### D9bis & observabilité avancée v1 (canal technique SUPERADMIN)

Depuis la vague 4, le backend expose un canal analytics LLM **séparé des exports métier** :

- Build : `POST /internal/hugo/sessions/{id}/d9bis/build/`
- Export JSON : `GET /internal/hugo/sessions/{id}/d9bis/export/` (`d9bis_session_export_v1`)
- Agrégats org : `GET /internal/hugo/analytics/conversation-summary/` (`conversation_summary_v1`)

**Réservé SUPERADMIN.** Données dérivées uniquement (tags, buckets, métriques) — jamais verbatim ni P0. Absent de UIState, EvidenceBundle, ExportRun et surfaces `/app`.

***

## Interface formateur

### Vues et objets

- Le formateur manipule une **base de connaissances métier gouvernée**, avec des `TrainerKnowledgeItem` et un `documentingestor`, plus une **interface dialogique d’explicitation** (questionnaire où il raconte, explicite, structure).[^1][^2]
- Les **objets** sont marqués par statuts `declared`, `derived_provisional`, `validated_trainer`, avec l’interdiction explicite de passer à “validé” sans validation humaine.[^2][^1]
- Il voit :
    - documents importés ;
    - critères de maîtrise ;
    - erreurs fréquentes ;
    - raisonnements attendus ou à éviter ;
    - objets en attente de validation ;
    - structures référentielles/RAG prêtes à être exploitées par Hugo.[^1][^2]


### Actions

- Apporter des documents, expliciter des savoirs, structurer un référentiel, enrichir le matériau pédagogique, **valider / rejeter / corriger** des connaissances dérivées, rattacher des connaissances à des référentiels ou compétences, préparer des corpus utilisables par les orchestrateurs apprenant.[^2][^1]
- Configurer certains paramètres dans des bornes prévues (profils, processus, éventuellement curseurs) sans éditer la doctrine centrale ni les prompts SoT.[^2]


### Pilotage

- Le formateur peut orienter le système en **préparant le matériau** (documents, critères, erreurs, raisonnements) et en **validant** les connaissances que les orchestrateurs pourront exploiter en sécurité.[^1][^2]
- Il ne pilote pas la conversation apprenant au tour par tour, mais influence :
    - ce que les orchestrateurs de révision et d’évaluation peuvent utiliser ;
    - la qualité des suggestions ;
    - la couverture référentiel/critères.[^1][^2]

Manques sur l’interface formateur :

- L’ordre exact des écrans (workspace, tableau de validation, vue de lecture, panneau de configuration) n’est pas détaillé.
- On ne sait pas encore si le formateur voit des **capsules d’usage** montrant comment ses contenus ont été utilisés par les orchestrateurs.

***

## Interface tuteur

### Ce que le tuteur voit

- Il a une **vue de progression apprenant** construite sur ConversationProgress et UIState : branches, maturité, dispersion, état des actions terminales.[^2][^1]
- Il voit des **signaux gouvernés** : qualité de conversation (via future `ConversationQualitySignal`), traces, synthèses, évaluations, mais **pas le verbatim privé** non explicitement partagé.[^1][^2]
- Il devrait voir (doctrine) : état de séance, mode courant, maturité, besoins/difficultés déduits des signaux P0/Progress (par exemple blocages, dispersion, manque de preuves).[^2]


### Actions et limites

- Le tuteur peut **recommander des aménagements** des situations de travail, **suggérer des bascules de mode** ou des cadences différentes, préparer ou recommander une synthèse ou évaluation, mais sans accès libre au verbatim privé et sans pouvoir re‑piloter directement la conversation en place de l’apprenant.[^1][^2]
- Les accès sont **strictement filtrés** par le partage explicite : il ne voit que ce qui a été partagé comme synthèse, capsule, trace ou preuve.[^2][^1]

Manques sur l’interface tuteur :

- La différence exacte de vue entre tuteur et formateur n’est pas listée point par point (par exemple, tuteur ne manipule pas la base de connaissances, seulement les traces de conversation).
- La palette précise de commandes tuteur (“recommander une bascule”, “demander une synthèse”, “ajouter un commentaire pédagogique”) n’est pas décrite.

### Réel observé — cluster dev vague 2 encadrants (local)

| Surface | Route / API | Statut |
|---|---|---|
| Espace tuteur prod | `/app/tutor`, `/app/tutor/group/:id`, timeline via `TutorLearnerView` | **PARTIEL** — lecture timeline, validation trace ; pas de commandes moteur |
| Garde verbatim | `share_verbatim` + B1-01 | **IMPLÉMENTÉ** local |
| Exports groupe | Boutons visibles **ORGADMIN/SUPERADMIN** seulement (`isOrgAdminLike`) | **ALIGNÉ** local |

***

## Interface formateur — réel observé (cluster dev vague 2)

| Surface | Route / API | Statut |
|---|---|---|
| Espace formateur prod | `/app/trainer/knowledge` | **PARTIEL** — liste + validation `TrainerKnowledgeItem` |
| APIs knowledge | `/hugo/trainer/knowledge-items/`, elicitation, ingest, validate | **IMPLÉMENTÉ** — garde `TRAINER/ORGADMIN/SUPERADMIN` |
| Orchestrateur formateur complet (50) | — | **CIBLE** — script UX dialogique non livré |

***

## Interface administrateur d’organisation (ORGADMIN) — lot courant

Dans la cible 2.0, l’administrateur d’organisation agit au niveau d’un organisme de formation ou d’un établissement de rattachement, dans un contexte multi‑tenant strict. Il dispose d’une administration métier minimale pour son organisation, sans accès libre au contenu apprenant non partagé ni aux champs P0 bruts ou au verbatim interne.

### Capacités visées

- Gestion des comptes et rattachements dans les bornes prévues :
    - création et édition d’utilisateurs rattachés à l’organisation ;
    - rattachement des utilisateurs à des groupes et cohortes propres à l’organisation ;
    - attribution de rôles locaux (apprenant, tuteur, formateur) selon une matrice d’habilitations définie au niveau produit.

- Administration minimale de l’organisation :
    - consultation et mise à jour des métadonnées de l’organisation (nom, identifiants, paramètres généraux non sensibles) ;
    - accès à certains indicateurs agrégés (par exemple volumes de sessions, usage de synthèse/évaluation), sans verbatim ni champs P0 bruts.

- Exports filtrés par organisation :
    - déclencher des exports structurés (CSV, JSON) portant sur des traces ou agrégats rattachés à l’organisation, dans le respect des règles de confidentialité et de partage explicite ;
    - ne recevoir que des données filtrées par tenant, sans lecture inter‑tenant et sans exposition de contenu apprenant non partagé.

### Limites et garde‑fous

- L’ORGADMIN ne voit pas :
    - le verbatim apprenant non partagé ;
    - TurnState ou les variables P0 brutes ;
    - les prompts complets, les reason codes techniques détaillés ou les traces internes du moteur.

- L’ORGADMIN ne pilote pas directement :
    - la décision tutorale locale (P0 reste côté moteur backend) ;
    - le contrat de décision ou la sélection de posture à l’échelle d’une session ;
    - l’architecture de progression ou la mémoire gouvernée.

- L’interface ORGADMIN n’est pas :
    - un cockpit de pilotage libre du moteur ;
    - une surface de debug technique ou de lecture brute des logs ;
    - un substitut à la superadministration technique (rôle distinct d’exploitation et de supervision).

Les interfaces existantes de saisie de templates système et utilisateur, et de paramètres associés aux modes conversationnels (par exemple écrans de configuration de system prompt + paramètres) restent possibles pour des rôles habilités, dans le respect de ces garde‑fous : elles configurent les prompts et profils, mais ne deviennent pas un accès brut à P0 ou au verbatim ni un contournement de la logique moteur.

### État actuel et zones ouvertes

- Le runtime réel audit montre une administration observable partielle :
    - gestion d’utilisateurs (création/édition) rattachés à une organisation ;
    - capacités encore limitées sur certains aspects (par exemple suppression, matrice exhaustive des permissions, cartographie complète des écrans).

- Restent à préciser dans des specs dédiées :
    - la liste détaillée des écrans (gestion des utilisateurs, groupes, exports, paramètres d’organisation) et leur chorégraphie ;
    - la matrice fine des droits par rôle (apprenant, tuteur, formateur, coordinateur, ORGADMIN) ;
    - la frontière explicite entre interface ORGADMIN et surfaces de superadministration technique (debug, observabilité, configuration avancée), afin d’éviter de requalifier des vues de test comme interface d’organisation stabilisée.

***

## Interface superadministration technique — pilotage et observabilité (cible 2.0)

La superadministration technique est un rôle d’exploitation et de supervision globale de la plateforme. Elle couvre principalement la configuration technique bornée, l’observabilité avancée et certains outils de debug, sans se transformer en droit applicatif libre au contenu apprenant non partagé.

Cette section décrit une cible 2.0 pour ce rôle ; elle ne doit pas être relue comme preuve que toutes ces capacités sont déjà livrées dans le runtime courant.

### Principes généraux

- Multi‑tenant strict et confidentialité d’abord : aucune capacité de superadmin technique ne doit contourner l’isolation par organisation ni l’interdiction de lecture libre du verbatim non partagé.
- P0, TurnState et l’architecture interne restent du côté moteur ; la superadmin n’édite pas la logique centrale de décision ni ne duplique le pipeline P0.
- Les surfaces de debug et d’observabilité sont distinctes de l’UX apprenant, formateur, tuteur et ORGADMIN, et clairement marquées comme telles (mode test, environnement de démo, sessions de test).

Les interfaces existantes de saisie de templates système et utilisateur, et de paramètres associés aux modes conversationnels (par exemple écrans de configuration d’un couple system prompt / user prompt plus curseurs) restent possibles pour des rôles habilités. Elles sont considérées comme des surfaces de configuration contrôlée : elles configurent les prompts et profils de conduite, mais ne doivent pas devenir un accès brut au P0, au verbatim interne ou un moyen de contourner la logique moteur centrale.

Les écrans existants de gestion de system prompt + user prompt par mode conversationnel, avec leurs paramètres actuels, restent compatibles avec ces principes : ils configurent les templates et curseurs de conduite, mais ne doivent pas introduire de nouvelles voies d’accès direct au P0 brut ou au verbatim non partagé.

### Bloc 1 – Pilotage des orchestrateurs (paramètres bornés)

Objectif : permettre à un rôle technique habilité de visualiser et de régler, dans des bornes strictes, certains paramètres de conduite des orchestrateurs apprenant et de la branche d’évaluation terminale, sans modifier le noyau P0 ni la structure globale de la doctrine.

#### Postures apprenant

- Visualiser les postures principales (par exemple diagnostic, réfléxif AFEST, révision de savoirs) avec leur description et leur mission pédagogique.
- Pour chaque posture, permettre :
    - le choix de profils de conduite pré‑définis (par exemple via des profils de type TutorConductProfile) ;
    - un réglage borné de l’usage du RAG (par exemple activer/désactiver un mode de RAG de renfort pour une posture donnée) ;
    - le paramétrage de seuils recommandés pour la synthèse et l’évaluation (cases à cocher, enums, pas de règles libres).

Contraintes :

- Les réglages modulent des profils ou curseurs existants, sans changer la logique P0 ni réécrire la doctrine de fond.
- Les valeurs sont bornées (enums, booléens, plages limitées) et journalisées (qui, quoi, quand).

#### Branche d’évaluation terminale

- Activer ou désactiver l’accès à l’évaluation terminale pour une organisation ou un environnement de test.
- Choisir un profil d’évaluation par défaut dans une liste fermée (par exemple default, diagnostic, early_trigger).
- Encadrer l’early trigger dans des bornes strictes (par exemple autoriser en maturité intermédiaire avec un avertissement explicite à l’utilisateur).

Contraintes :

- Impossible de transformer l’évaluation en certification autonome : la validation finale reste humaine.
- Les garde‑fous existants côté moteur ne peuvent être ni supprimés ni contournés par ces réglages.

#### Règles globales de prudence

- Exposer des options globales (toggles) telles que :
    - interdiction d’évaluer avant un nombre minimal de tours ;
    - activation d’un état “évaluation déconseillée mais possible” avec message de prudence.

Effet : ces options ajoutent des contraintes supplémentaires au moteur, elles ne suppriment jamais les garde‑fous existants.

### Bloc 2 – Exports techniques de traces (mode test et debug)

Objectif : offrir, pour les besoins de test, d’audit et de convergence, des exports techniques hors UX métier permettant d’observer finement le comportement du moteur, y compris les données P0 et variables calculées mais non utilisées, sans les introduire dans les interfaces apprenant, formateur, tuteur ou ORGADMIN.

#### 2.1 Export complet d’une conversation en Markdown

Endpoint technique (exemple) :  
`GET /hugo/sessions/{id}/debug/export-md/`

Effet attendu :

- Produire un fichier Markdown horodaté contenant, pour chaque tour :
    - l’index du tour et les timestamps ;
    - le rôle (apprenant ou Hugo) ;
    - le contenu visible du message ;
    - un snapshot sérialisé de l’état P0 / TurnState (scores, reason codes, signaux) ;
    - le contrat de décision (objectif principal, geste tutorale retenu, mode, nombre cible de questions, autorisations de bundling, usage de mémoire thématique, verbatim, overlay, RAG, éligibilité éventuelle à l’évaluation, etc.) ;
    - les éléments de progression pertinents (branche active, maturité, dispersion, éligibilité synthèse / évaluation) ;
    - les variables calculées mais non utilisées dans la décision finale, explicitement marquées comme telles.

Garde‑fous :

- L’export porte une mention explicite du type “Debug export — données internes non montrables produit”.
- Il peut contenir du verbatim interne et des champs P0 bruts : l’accès doit être strictement réservé à des environnements de test ou de démonstration, ou à des sessions marquées avec un consentement explicite, pour des rôles techniques habilités.
- En production multi‑tenant, cette fonction doit être désactivée ou fortement restreinte.

#### 2.2 Export partiel sur une plage de tours

Endpoint technique (exemple) :  
`GET /hugo/sessions/{id}/debug/export-md/?from_turn=…&to_turn=…`

Effet attendu :

- Même format que l’export complet, mais restreint à une plage de tours (par exemple du tour 5 au tour 12).
- L’en‑tête du fichier rappelle :
    - l’identifiant de session ;
    - la plage de tours exportée ;
    - l’existence éventuelle de tours antérieurs ou postérieurs non inclus.

Garde‑fous :

- Validation des bornes (from_turn et to_turn) dans la plage de la session et with from_turn ≤ to_turn.
- Sans bornes, le comportement revient au mode “export complet”.
- Même politique de rôles, d’environnements et de consentement que pour l’export complet.

#### 2.3 Analyse LLM par tour et par conversation (ConversationTurnLLMAnalysis / ConversationLLMAnalysis)

> Niveau de vérité – Analyse LLM par tour / par conversation  
> - Statut : CIBLE 2.0 (aucune couche d’objets ConversationTurnLLMAnalysis / ConversationLLMAnalysis n’est démontrée comme stabilisée dans le runtime audit actuel).  
> - Lecture : cette sous-section fixe une cible d’export analytique réservé à la superadministration technique. Elle ne prouve ni la présence ni l’activation de tels exports dans les environnements de démo ou de production.  
> - Dérivés : ces objets restent documentés comme artefacts de debug et de recherche, hors surfaces apprenant, tuteur, formateur et ORGADMIN, et ne modifient pas la doctrine P0 / UIState existante.

En complément des exports de debug incluant P0 et TurnState, la cible 2.0 prévoit une couche analytique optionnelle, produite par le LLM lui‑même à partir du verbatim brut et de l’état visible d’une conversation. Cette couche vise des usages de démarche qualité, de recherche ou d’analyse fine, sans devenir une mémoire principale ni un nouveau régulateur de la conversation.

Deux objets analytiques sont distingués :
- `ConversationTurnLLMAnalysis` : analyse d’un tour de conversation individuel (un message apprenant / une réponse Hugo), calculée à partir du verbatim brut et d’un prompt d’analyse dédié ;
- `ConversationLLMAnalysis` : agrégat optionnel des analyses de tous les tours d’une session, structurant les `ConversationTurnLLMAnalysis` associées à une même session.

Pour chaque tour, `ConversationTurnLLMAnalysis` est produit via un appel LLM avec un template du type « donne ton analyse du contenu de ce tour en priorisant le verbatim brut, sans ré‑interpréter les signaux P0 ni les reason codes internes ». La réponse du LLM est sérialisée dans l’objet d’analyse, indépendante des champs P0, même si certains signaux ou métadonnées techniques peuvent y être associés en back‑office.

Ces objets analytiques :
- sont strictement réservés aux exports techniques de debug superadmin (endpoint d’export Markdown ou équivalent, avec possibilité de choisir d’inclure ou non les blocs d’analyse LLM) ;
- ne sont jamais projetés dans UIState, ni dans les surfaces apprenant, formateur, tuteur ou ORGADMIN ;
- ne constituent pas une mémoire gouvernée visible produit, ni une nouvelle base de décision ; ils restent des artefacts d’analyse et de recherche, hors UX métier.

Garde‑fous :
- l’activation de cette couche analytique doit être restreinte aux environnements de test, de démonstration ou à des sessions marquées avec un consentement explicite, pour des rôles techniques habilités ;
- la présence éventuelle de verbatim brut dans ces analyses ne modifie pas la politique générale : elles ne doivent pas être exposées dans les interfaces métier, seulement dans des exports techniques clairement marqués comme non montrables produit ;
- l’association de champs P0 ou d’autres signaux internes à ces analyses ne change pas la doctrine : P0 et TurnState restent côté moteur, non exposés au front, et ces analyses ne doivent pas être interprétées comme une nouvelle source de vérité produit.

### Bloc 3 – Garde‑fous spécifiques superadmin

- La superadministration technique ne doit jamais être documentée ou implémentée comme un droit générique de lecture applicative du contenu apprenant non partagé.
- Les surfaces décrites ici (pilotage borné des orchestrateurs, exports de debug) sont des outils de chantier et d’exploitation :
    - hors parcours apprenant, formateur, tuteur et ORGADMIN ;
    - explicitement marqués comme non destinés aux utilisateurs finaux.
- Toute activation de ces capacités doit être accompagnée d’une documentation de contexte (environnement, organisation concernée, finalité de test) et de contrôles d’accès robustes.

Les interfaces de saisie de templates système et utilisateur, ainsi que les écrans de paramétrage des modes conversationnels, doivent être raccordées à ces garde‑fous : elles restent des surfaces de configuration contrôlée, pas un moyen de court‑circuiter la séparation entre logique moteur, surfaces produit et données sensibles.

***

## Granularité présente vs manquante

- **Présent** :
    - architecture de front basée sur `/ui-state` + `/progress` ;
    - invariants de confidentialité (verbatim privé, partage explicite, pas de P0 brut) ;
    - existence d’un sélecteur de mode côté apprenant, d’une progression lisible, de boutons synthèse/évaluation dépendants de l’état serveur ;
    - base formateur gouvernée avec statuts et validation humaine ;
    - vues tuteur basées sur signaux et traces partagées.[^3][^1][^2]
- **Manquant ou sous‑spécifié** :
    - maquettes logiques plus fines (composition exacte du ProgressPanel, des bandeaux de mode, des cartes d’état) ;
    - messages UI pour l’évaluation (déconseillée / forcée) ;
    - chorégraphie détaillée des workflows formateur et tuteur (ordre des écrans, interactions fines) ;
    - découpe explicite des droits tuteur vs formateur vs orgadmin dans l’UI métier ;
    - périmètre détaillé d’interface pour l’administrateur d’organisation (ORGADMIN) au‑delà de l’administration minimale déjà observée ;
    - contractualisation précise d’une interface de superadministration technique (pilotage borné des orchestrateurs, observabilité avancée, exports techniques) distincte des surfaces orgadmin et des vues de test.



### RAG documentaire — lot courant

Dans l’état actuel, le comportement documentaire de Hugo repose sur un RAG lexical backend, gouverné par des règles explicites (types de documents, statuts, filtres métier) et déclenché à la demande en fonction des questions ou contextes pédagogiques. Le RAG fonctionne comme un renfort documentaire situé : il propose des ressources ou extraits pertinents pour la situation, mais il ne constitue ni la mémoire principale du fil, ni un moteur autonome de construction de cours. L’état et la mémoire gouvernée intra‑conversation priment, le RAG vient en support ; toute évolution ultérieure (vectorisation, hiérarchie de contexte plus riche) devra rester additive et ne pourra pas être documentée comme livrée sans preuve runtime.