# 00_rapport_ecarts — 80_observabilite_qualite_conversationnelle

## Domaine

- `DOMAINE_CODE = 80_observabilite_qualite_conversationnelle`
- `DOMAINE_LABEL = observabilité et qualité conversationnelle`

---

## 1. Objet du rapport

Ce rapport qualifie, pour le seul domaine **observabilité et qualité conversationnelle** de Hugo cœur, l’écart entre :
- la **cible 2.0** décrite par la spec canonique 2.0 et le `complement_unique_specs_2_0` ;
- le **réel observable** décrit par les audits du corpus Hugo réel, en particulier `02_ETAT_MOTEUR_REEL`, `03_ETAT_PRODUIT_REEL`, `07_RUNTIME_DEMO_REFERENCE`, `10_FICHE_RUNTIME_PROD_ENCOORS` et `05_ECARTS_DOC_CODE_PRODUIT` ;
- le **pont de vocabulaire** fourni par `glossaire_alignement_hugo_reel_vs_spec`.

Le rapport reste strictement centré sur **Hugo cœur**. Il ne traite ni Hugo & Cie, ni une gouvernance analytics générale hors périmètre, ni une refonte transverse du moteur.

---

## 2. Règles de lecture et de vérité appliquées sur ce domaine

### 2.1 Corpus mobilisé

Pour parler du **réel**, ce rapport s’appuie en priorité sur :
- `02_ETAT_MOTEUR_REEL` pour les services backend, hooks post-conversation, objets et signaux observés ;
- `03_ETAT_PRODUIT_REEL` pour les surfaces produit effectivement exposées ;
- `07_RUNTIME_DEMO_REFERENCE` pour ce qui est démontrable sans sur-interprétation ;
- `10_FICHE_RUNTIME_PROD_ENCOORS` pour les écarts potentiels entre local audité et runtime distant ;
- `05_ECARTS_DOC_CODE_PRODUIT` pour les contradictions confirmées entre documentation, code local, front et runtime supposé.

Pour parler de la **cible**, ce rapport mobilise :
- `spec_canonique_hugo_2_0` ;
- `complement_unique_specs_2_0` ;
- les rappels de doctrine consolidés sur l’observabilité, les signaux qualité, la progression, les traces structurées et les garde-fous de confidentialité.

Le `glossaire_alignement_hugo_reel_vs_spec` est utilisé comme **pont de vocabulaire** pour raccorder les noms doctrinaux 2.0 aux noms réellement observés dans Hugo développé. Il ne vaut jamais preuve d’implémentation à lui seul.

### 2.2 Garde-fous de lecture

- La cible 2.0 décrit un **état visé**, pas un état livré.
- Le réel doit être établi à partir du **croisement** des audits, du code décrit dans les audits, des surfaces produit observées et du glossaire d’alignement.
- Une classe, un fichier ou un nom de service ne prouve pas à lui seul un comportement produit complet.
- Toute affirmation dépendant du runtime distant Encoors, de flags ou d’une variante non auditée localement est marquée `A_VERIFIER`.
- L’observabilité et la qualité conversationnelle ne doivent jamais être relues comme un droit à exposer les champs bruts P0, le verbatim non partagé ou une lecture libre des données apprenant.

---

## 3. Périmètre cible 2.0 du domaine

### 3.1 Ce que la cible 2.0 fixe déjà

Dans la cible Hugo 2.0, le domaine **observabilité et qualité conversationnelle** est une couche backend gouvernée, au service :
- de la lisibilité de la progression conversationnelle ;
- de l’analyse de qualité à partir de signaux structurés ;
- de vues cohorte et d’aides d’interprétation pour les rôles autorisés ;
- de la préparation de synthèses, recommandations ou actions terminales sans faire dériver Hugo vers un scoring opaque.

La spec canonique 2.0 et le `complement_unique_specs_2_0` fixent déjà plusieurs points structurants :
- l’existence de **ConversationQualitySignal** comme objet doctrinal légitime ;
- l’existence d’un service de type **QualityTracker** dans la matrice backend ;
- le fait que les signaux qualité doivent être nourris par la progression, les traces structurées, les reason codes et autres indicateurs de qualité, sans exposition brute du moteur ;
- l’idée que l’observabilité doit rester compatible avec la confidentialité-first, le partage explicite et l’interdiction d’accès libre au verbatim non partagé ;
- le fait que les signaux peuvent servir aux vues tuteur et cohorte, mais ne doivent pas devenir un système de notation opaque ou une logique parallèle pilotant le moteur.

### 3.2 Ce que la cible 2.0 laisse encore ouvert

La cible 2.0 est déjà nette sur la fonction du domaine, mais elle laisse encore ouverts :
- le **catalogue canonique complet** des signaux de qualité conversationnelle ;
- le mapping détaillé entre reason codes, progression, états de blocage et recommandations produit ;
- la forme exacte des vues cohorte et leur niveau de granularité ;
- le contrat fin entre signaux backend, surfaces tuteur et éventuelles agrégations de cohorte.

Autrement dit, la cible 2.0 fixe solidement la **fonction** du domaine, mais pas encore son **catalogue exhaustif** ni tous ses contrats d’exposition.

---

## 4. Photo du réel observé

### 4.1 Services et objets réellement observés

Le corpus audité montre que le domaine n’est pas théorique. Le glossaire d’alignement mentionne explicitement :
- `qualitytracker.py` comme nom réel observé pour le service doctrinal **QualityTracker** ;
- `ConversationQualitySignal` comme objet déjà cohérent entre doctrine 2.0 et réel audité ;
- `analyticscohortdashboard.py` comme composant ou vue réelle liée à l’analytics cohorte.

Le domaine apparaît donc dans le réel comme une **couche backend existante**, avec une nomenclature déjà partiellement alignée avec la doctrine 2.0.

### 4.2 Position dans le pipeline réel

Le `complement_unique_specs_2_0` situe doctrinalement les signaux de qualité dans la partie post-traitement, persistance et activation éventuelle de vues terminales. Cette lecture est cohérente avec le réel audité, où `05_ECARTS_DOC_CODE_PRODUIT` confirme que des enregistrements de qualité sont déclenchés dans les hooks post-conversation, notamment via `postconversationhooks` et `recordsessionsignal`.

Le réel audité confirme donc un point important : les signaux qualité ne sont pas calculés côté front, et ils ne constituent pas une boucle parallèle qui piloterait la décision tutorale principale. Ils vivent dans la logique backend, en continuité avec progression, mémoire, synthèse et évaluation.

### 4.3 Correction importante apportée par l’audit croisé

`05_ECARTS_DOC_CODE_PRODUIT` corrige explicitement une ancienne affirmation documentaire selon laquelle le snapshot qualité ne serait pas post-session. L’audit croisé confirme au contraire que `recordsessionsignal` est bien appelé dans `postconversationhooks`, avec appui de tests associés de type `testqualitysignals`.

Ce point est important pour le domaine : il montre que le réel local audité est **plus avancé** que certaines docs obsolètes, et qu’il faut prendre garde à ne pas reconduire un faux diagnostic de manque sur ce sujet.

### 4.4 Exposition produit réellement observable

Le réel produit observable ne montre pas, à ce stade, une exposition large et frontalisée des signaux qualité conversationnelle côté apprenant. La doctrine produit 2.0 rappelle d’ailleurs que le front doit consommer des états dérivés propres, pas des champs P0 ni des traces techniques.

Le glossaire et la spec canonique convergent pour situer ces signaux plutôt :
- dans les vues tuteur ou cohorte ;
- dans les services backend de synthèse, de suivi de progression ou de recommandation ;
- et dans des surfaces internes gouvernées plutôt que dans l’interface apprenant standard.

Autrement dit, le réel observable suggère un domaine surtout **backend et internal-facing**, même s’il peut nourrir indirectement l’UIState, la progression ou certaines vues métier.

### 4.5 Local audité versus runtime distant

Comme pour les autres domaines transverses, `05_ECARTS_DOC_CODE_PRODUIT` rappelle que la démo courante pointe par défaut vers `hugoback.encoors.com`, et que l’équivalence entre local audité et runtime distant n’est pas garantie. Cela vaut aussi pour les signaux qualité, les vues cohorte et les comportements de persistance ou d’agrégation.

En conséquence, tout ce qui relève :
- du comportement exact en production distante ;
- des flags éventuels ;
- du niveau réel de disponibilité des dashboards cohorte sur Encoors ;
reste `A_VERIFIER` tant qu’une inspection runtime spécifique n’est pas menée.

---

## 5. Analyse narrative des écarts

### 5.1 Zone de bon alignement

Le domaine est globalement **bien aligné** entre doctrine 2.0 et réel observé sur son principe.

La spec canonique 2.0 fixe l’existence de signaux de qualité conversationnelle, d’un service de type `QualityTracker`, de vues cohorte et d’un usage gouverné de ces signaux. Le glossaire d’alignement montre que ces notions ont déjà un ancrage réel crédible dans Hugo développé, via `qualitytracker.py`, `ConversationQualitySignal` et `analyticscohortdashboard.py`.

Il ne s’agit donc pas d’un domaine purement cible ou théorique. Le socle métier paraît réellement présent.

### 5.2 Écart principal : catalogue doctrinal plus stabilisé que le catalogue réel documenté

L’écart principal n’est pas l’absence du domaine, mais le fait que la **doctrine est plus claire que la documentation du réel** sur le catalogue exact des signaux.

La cible 2.0 dit clairement :
- qu’il existe des signaux de qualité ;
- qu’ils peuvent nourrir les vues cohorte et les lectures tuteur ;
- qu’ils doivent rester non opaques et gouvernés.

En revanche, le réel audité, tel qu’il est documenté ici, ne livre pas encore un catalogue suffisamment stabilisé de type :
- liste canonique des signaux ;
- définition métier de chacun ;
- producteur exact ;
- consommateur exact ;
- projection produit ou cohorte associée.

L’écart à traiter est donc surtout un **écart de formalisation documentaire et contractuelle**, pas un constat d’absence.

### 5.3 Écart de maturité documentaire : anciennes docs contredites par le réel local

Le domaine souffre aussi d’un problème classique dans ce workspace : certaines docs plus anciennes ou intermédiaires sous-estiment le niveau réel atteint localement. Le cas du snapshot qualité “non post-session” en est un exemple direct, contredit par l’audit croisé et par la présence de hooks et tests associés.

Cela implique une conséquence pratique forte : sur ce domaine, il ne faut pas relancer un chantier en partant d’une doc obsolète qui décrirait une absence. La priorité doit aller au **recalage documentaire** avant toute décision technique lourde.

### 5.4 Écart de projection produit : fonction backend réelle, exposition métier encore partiellement sous-spécifiée

La cible 2.0 suppose que les signaux qualité servent au tuteur, aux vues cohorte et à certaines recommandations. Le réel confirme la présence du backend et de l’analytics cohorte, mais la projection exacte vers les surfaces produit reste, dans le corpus mobilisé ici, moins stabilisée que la couche moteur.

Autrement dit :
- le backend qualité semble exister ;
- l’objet doctrinal `ConversationQualitySignal` est déjà bien raccordé ;
- mais la grammaire produit, les écrans métier et les contrats d’exposition restent encore partiellement ouverts ou insuffisamment documentés.

L’écart se situe donc moins sur le **moteur** que sur la **lisibilité contractuelle des sorties**.

### 5.5 Écart de preuve sur le distant

Le domaine est également affecté par le même garde-fou que le reste de Hugo cœur : ce qui est vrai sur le local audité n’est pas automatiquement prouvé sur Encoors. Le `05_ECARTS_DOC_CODE_PRODUIT` insiste sur le fait que plusieurs comportements prod restent à vérifier, notamment lorsque les flags ou le déploiement distant ne sont pas inspectés directement.

Il faut donc éviter d’écrire que :
- les dashboards cohorte distants sont identiques au local ;
- les signaux qualité sont exposés de la même manière partout ;
- ou que la chaîne complète analytics → cohorte → surface tuteur est démontrée en production.

Sur ces points, la bonne qualification reste `A_VERIFIER`.

---

## 6. Lecture de synthèse par niveau de vérité

### 6.1 Implémenté / observable

À ce stade, le corpus permet d’affirmer comme **implémenté ou observable** dans Hugo cœur :
- l’existence d’un service réel de type `qualitytracker.py` ;
- la présence d’un objet ou concept réel `ConversationQualitySignal` déjà bien raccordé au vocabulaire 2.0 ;
- la présence d’une composante d’analytics cohorte de type `analyticscohortdashboard.py` ;
- l’enregistrement de signaux qualité dans les hooks post-conversation du réel local audité ;
- la cohérence du domaine avec une logique backend-first, non front-driven.

### 6.2 Cible 2.0

Relèvent de la **cible 2.0** au sens strict :
- un catalogue canonique plus complet et mieux défini des signaux qualité ;
- un mapping stabilisé entre signaux, progression, blocages, reason codes et recommandations ;
- un contrat plus précis de projection vers les surfaces tuteur et cohorte ;
- une documentation suffisamment claire pour préparer ensuite des variables backend stables consommables par les futurs prompts, sans remettre les prompts au centre de la vérité comportementale.

### 6.3 Écarts confirmés

Les écarts confirmés sur ce domaine sont principalement :
- un **catalogue documentaire encore trop flou** des signaux qualité réels ;
- une **projection produit insuffisamment formalisée** dans le corpus mobilisé ici ;
- la présence de **docs obsolètes** contredites par le réel local sur le caractère post-conversation des signaux qualité.

### 6.4 À vérifier

Restent explicitement `A_VERIFIER` :
- l’équivalence exacte entre local audité et runtime distant Encoors sur ce domaine ;
- les flags ou variantes pouvant affecter l’enregistrement ou l’exposition des signaux ;
- la disponibilité réelle et le périmètre précis des vues cohorte sur le distant ;
- le comportement exact des rôles métiers hors ce qui est prouvé par les audits locaux mobilisés ici.

---

## 7. Garde-fous pour la suite documentaire et technique

### 7.1 Ce qu’il ne faut pas faire

Pour ce domaine, il faut éviter :
1. de relire la cible 2.0 comme si elle prouvait déjà un catalogue complet, stabilisé et exposé partout ;
2. de conclure à une absence du domaine à partir d’anciennes docs obsolètes ;
3. de transformer les signaux qualité en scoring opaque ou en moteur de pilotage parallèle ;
4. d’exposer des traces techniques, reason codes bruts, champs P0 ou verbatim non partagé sous prétexte d’observabilité ;
5. de confondre cohorte, observabilité technique, analytics métier et surveillance libre de l’apprenant.

### 7.2 Ce qu’il faut privilégier

Pour ce domaine, la bonne suite consiste à :
- clarifier le **vocabulaire** entre doctrine 2.0 et noms réels observés ;
- documenter proprement le **catalogue minimal réellement observé** ;
- expliciter la place des signaux qualité dans la chaîne backend post-conversation ;
- distinguer clairement ce qui est **implémenté localement**, ce qui est **documenté comme cible**, et ce qui reste **A_VERIFIER** sur le runtime distant ;
- préparer des contrats backend et des projections produit **additifs**, sans recréer une architecture analytics parallèle.

---

## 8. Conclusion opérationnelle du domaine

Le domaine `80_observabilite_qualite_conversationnelle` est un domaine **réel, structurant et déjà partiellement bien aligné** entre doctrine 2.0 et Hugo développé.

Le réel audité montre que Hugo cœur dispose déjà d’un socle crédible : service qualité, signaux conversationnels, hooks post-conversation et analytics cohorte. La cible 2.0 ne doit donc pas être lue ici comme une injonction à inventer le domaine, mais comme un cadre pour **mieux formaliser ce qui existe déjà**.

L’écart principal n’est pas l’absence de capacité, mais l’insuffisance actuelle de **formalisation documentaire, de catalogue canonique et de projection produit explicitée**, avec en plus un risque de confusion entretenu par des docs intermédiaires obsolètes. La suite logique pour ce domaine n’est donc pas une refonte lourde, mais un travail rigoureux de clarification, d’alignement de vocabulaire, de bornage des contrats et de marquage honnête des zones `A_VERIFIER`.

# 01_matrice_ecarts — 80_observabilite_qualite_conversationnelle

- `DOMAINE_CODE = 80_observabilite_qualite_conversationnelle`
- `DOMAINE_LABEL = observabilité et qualité conversationnelle`

Légende des statuts :
- `ALIGNE`
- `ALIGNE_DOC_PARTIEL`
- `RENOMMER_DANS_DOC`
- `AMBIGU`
- `A_VERIFIER`
- `ABSENT / NOUVEAU_CONTRAT`

---

## 1. Objets de domaine et services backend

| Élément doctrinal 2.0               | Nom(s) réel(s) observé(s)                  | Description / rôle                                                                                           | Statut                 | Commentaire d’écart                                                                                           |
|-------------------------------------|--------------------------------------------|--------------------------------------------------------------------------------------------------------------|------------------------|--------------------------------------------------------------------------------------------------------------|
| ConversationQualitySignal           | ConversationQualitySignal                  | Objet de signal de qualité conversationnelle au niveau cohorte / session.                                    | ALIGNE                 | Très bon alignement concept / nom ; rôle fixé doctrinalement, objet réel mentionné dans le glossaire.       |
| QualityTracker                      | qualitytracker.py                          | Service backend qui calcule et enregistre des signaux de qualité à partir des artefacts de session.         | ALIGNE_DOC_PARTIEL     | Service réel bien observé ; manque un catalogue canonique de signaux et une doc 2.0 plus détaillée.         |
| Analytics cohorte (vues)           | analyticscohortdashboard.py                | Composant / service pour vues cohorte et analytics conversationnels.                                         | ALIGNE_DOC_PARTIEL     | Alignement de principe bon ; projection produit et périmètre des vues cohorte restent peu documentés.       |
| Hooks post-conversation qualité    | postconversationhooks, recordsessionsignal | Enregistrement de signaux qualité après persistance du tour.                                                | ALIGNE_DOC_PARTIEL     | Réel local confirme un enregistrement post-conversation ; plusieurs docs anciennes restent contradictoires. |
| Signaux de progression comme entrée qualité | ConversationProgress, maturité, dispersion, reason codes | Utilisation de la progression et des indicateurs pour nourrir les signaux de qualité.                      | AMBIGU                 | Cible claire, mais articulation précise entre progression et signaux qualité reste peu formalisée.          |

---

## 2. Catalogue de signaux et métriques

| Élément doctrinal 2.0                            | Nom(s) réel(s) observé(s)                  | Description / rôle                                                                                                   | Statut                 | Commentaire d’écart                                                                                                       |
|--------------------------------------------------|--------------------------------------------|----------------------------------------------------------------------------------------------------------------------|------------------------|--------------------------------------------------------------------------------------------------------------------------|
| Catalogue canonique de ConversationQualitySignal | n/a (liste détaillée non observée ici)     | Liste stabilisée de types de signaux, définitions, conditions de calcul, usages produits.                            | ABSENT / NOUVEAU_CONTRAT | La doctrine acte l’existence des signaux mais pas un catalogue exhaustif ; à spécifier proprement pour 2.0.              |
| Signaux de blocage / risque interactionnel       | reason codes P0 + signaux qualité dérivés  | Indicateurs de difficultés, blocages, risques pour la conduite de séance.                                            | AMBIGU                 | Rôle doctrinal clair, mais mapping exact entre P0, progression et signaux qualité n’est pas documenté dans le réel.     |
| Signaux de dispersion / dérive de branches       | dispersion, branches actives               | Indicateurs de dispersion de la conversation, risque de perte de focus.                                              | AMBIGU                 | Progression fournit déjà dispersion, mais la façon dont elle nourrit QualityTracker n’est pas détaillée.               |
| Signaux de maturité pour synthèse / évaluation   | sessionmaturity, eligibility synthèse/éval | Indicateurs permettant de juger si une séance est mûre pour synthèse ou évaluation terminale.                        | ALIGNE_DOC_PARTIEL     | Alignement doctrinal bon ; manque un contrat documenté explicitant clairement le lien entre ces signaux et le domaine.  |
| Signaux de qualité de réponses (micro-niveau)    | n/a explicite dans l’audit utilisé         | Indicateurs de pertinence locale des tours (ex. respect des garde-fous P0).                                          | A_VERIFIER             | Doctrine suggère des signaux riches ; aucune preuve suffisante dans le corpus utilisé pour conclure sur leur présence.  |

---

## 3. Exposition produit, vues et rôles

| Élément doctrinal 2.0                       | Nom(s) réel(s) observé(s)        | Description / rôle                                                                                                       | Statut                 | Commentaire d’écart                                                                                                    |
|---------------------------------------------|----------------------------------|--------------------------------------------------------------------------------------------------------------------------|------------------------|-------------------------------------------------------------------------------------------------------------------------|
| Vues cohorte conversationnelle             | analyticscohortdashboard.py      | Vues agrégées par cohorte pour lire signaux qualité et progression.                                                     | ALIGNE_DOC_PARTIEL     | Existence réelle plausible, mais périmètre, rituels d’usage et exposition précise restent peu documentés.             |
| Surfaces tuteur pour lecture des signaux   | Vues tuteur (nom à préciser)     | Surfaces permettant au tuteur de lire progression, signaux qualité et blocages.                                         | AMBIGU                 | Doctrine claire ; le mapping précis aux écrans tuteur réels n’est pas encore assez décrit dans les audits mobilisés.  |
| Exposition des signaux dans UIState        | UIState, éventuels champs dérivés| Projection éventuelle d’une partie des signaux vers l’interface, via état dérivé compréhensible.                        | AMBIGU                 | Cible logique, mais non documentée explicitement dans le réel audité ; à cadrer dans la spec interface.               |
| Accès apprenant aux signaux qualité        | n/a spécifique                   | Ce que l’apprenant voit en termes de qualité / progression, sans exposer P0 ou signaux techniques.                      | ALIGNE_DOC_PARTIEL     | Doctrine produit claire (UIState, progression) ; la part exacte attribuée au domaine qualité reste sous-spécifiée.    |
| Accès tuteur / formateur au verbatim non partagé | aucun accès direct attendu      | Interdiction d’accès au verbatim non partagé sous prétexte d’analytics ou qualité.                                     | ALIGNE                 | Invariant 2.0 net, cohérent avec la doctrine et sans contradiction dans le réel mobilisé ici.                         |

---

## 4. Local audité vs runtime distant

| Élément doctrinal 2.0 / attente             | Nom(s) réel(s) observé(s) | Description / rôle                                                                              | Statut      | Commentaire d’écart                                                                                           |
|--------------------------------------------|---------------------------|-------------------------------------------------------------------------------------------------|-------------|--------------------------------------------------------------------------------------------------------------|
| Comportement QualityTracker en prod distante | n/a (Encoors non auditée) | Application des mêmes règles et signaux sur `hugoback.encoors.com` que sur le local audité.     | A_VERIFIER  | Aucun audit direct de la prod distante dans ce corpus ; ne pas supposer l’alignement sans vérification.     |
| Disponibilité des vues cohorte en prod     | n/a (Encoors non auditée) | Présence et périmètre des dashboards cohorte sur l’instance distante.                          | A_VERIFIER  | Même contrainte : à vérifier via inspection runtime distante ou logs produits, pas par simple analogie.     |
| Flags éventuels sur enregistrement qualité | n/a (Encoors, settings)   | Feature flags ou settings pouvant activer/désactiver l’enregistrement ou l’exposition des signaux. | A_VERIFIER  | Le corpus ne donne pas un état complet des flags liés à la qualité ; ne pas préjuger de la configuration.   |

---

## 5. Vocabulaire et documentation

| Élément doctrinal 2.0                 | Nom(s) réel(s) observé(s)   | Description / rôle                                                                                         | Statut             | Commentaire d’écart                                                                                         |
|---------------------------------------|-----------------------------|------------------------------------------------------------------------------------------------------------|--------------------|------------------------------------------------------------------------------------------------------------|
| QualityTracker (nom doctrinal)        | qualitytracker.py           | Service métier de calcul de signaux qualité.                                                               | RENOMMER_DANS_DOC  | Conserver le nom doctrinal 2.0 mais documenter explicitement `qualitytracker.py` comme implémentation réelle. |
| ConversationQualitySignal (doctrine)  | ConversationQualitySignal   | Objet de signal cohorte.                                                                                   | ALIGNE             | Pas de renommage nécessaire ; rappeler dans la doc que le nom réel correspond déjà au nom doctrinal.      |
| Vues cohorte (concept doctrine)       | analyticscohortdashboard.py | Vues analytics conversationnelles.                                                                         | RENOMMER_DANS_DOC  | Doc 2.0 doit mentionner `analyticscohortdashboard.py` comme backing réel de la couche cohorte actuelle.    |
| Observabilité / analytics qualité     | QualityTracker, analyticscohortdashboard | Domaine qualité / cohorte au sens backend.                                                         | ALIGNE_DOC_PARTIEL | Domaine bien présent ; manque une section dédiée dans la spec 2.0 explicitant le couple service + vues.    |
| Catalogue canonique de signaux        | n/a                         | Nom, définition et statut des signaux qualité conversationnelle.                                           | ABSENT / NOUVEAU_CONTRAT | À introduire comme nouvelle section documentaire, sans supposer une implémentation complète déjà en place. |

---

## 6. Règles et garde-fous spécifiques

| Règle / garde-fou doctrinal 2.0                               | Constats sur le réel        | Description / rôle                                                                                   | Statut             | Commentaire d’écart                                                                                                      |
|---------------------------------------------------------------|-----------------------------|------------------------------------------------------------------------------------------------------|--------------------|-------------------------------------------------------------------------------------------------------------------------|
| Pas de scoring opaque sur les apprenants                      | Aucun scoring opaque observé dans ce corpus | Interdiction de transformer les signaux qualité en notation arbitraire ou non transparente. | ALIGNE             | Rien dans les audits ne va à l’encontre de cette règle ; la doc doit simplement continuer à l’affirmer clairement.      |
| Observabilité post-conversation, pas en front moteur          | recordsessionsignal post-conversation | Signaux qualité calculés après le tour, côté backend.                                   | ALIGNE_DOC_PARTIEL | Réel local confirme la post-conversation, certaines docs anciennes affirment l’inverse et doivent être corrigées.       |
| Respect de la confidentialité-first et du partage explicite   | Invariants respectés dans la doctrine ; pas de contre-exemple explicite observé ici | Signaux fondés sur artefacts structurés, pas sur lecture libre du verbatim.            | ALIGNE             | Alignement doctrinal fort ; la doc 2.0 doit continuer à rendre cette contrainte explicite pour le domaine.             |
| Hiérarchie de contexte respectée pour les signaux qualité     | P0, progression, mémoire, puis signaux qualité | Les signaux se basent sur états structurés et traces gouvernées, pas sur historique brut. | ALIGNE_DOC_PARTIEL | Hiérarchie bien définie dans la doctrine ; implémentation locale cohérente mais pas encore décrite finement.           |

---

## 7. Synthèse rapide des écarts par type

- **ALIGNE**
  - ConversationQualitySignal
  - Interdiction d’accès au verbatim non partagé via observabilité
  - Règles de confidentialité-first appliquées au domaine
  - Interdiction de scoring opaque (dans la doctrine, sans contre-exemple observé)

- **ALIGNE_DOC_PARTIEL**
  - QualityTracker / qualitytracker.py
  - Analytics cohorte / analyticscohortdashboard.py
  - Hooks post-conversation qualité (recordsessionsignal)
  - Utilisation des signaux de maturité pour synthèse / évaluation
  - Observabilité post-conversation (réel > docs anciennes)
  - Concept global d’observabilité et de qualité conversationnelle

- **RENOMMER_DANS_DOC**
  - Associer explicitement QualityTracker ↔ qualitytracker.py
  - Associer explicitement vues cohorte ↔ analyticscohortdashboard.py
  - Nommer clairement la famille “observabilité / qualité conversationnelle” comme domaine structurant backend

- **AMBIGU**
  - Articulation fine entre progression (ConversationProgress, dispersion) et signaux qualité
  - Surfaces tuteur exactes consommant les signaux
  - Projection des signaux dans UIState ou autres états produits
  - Usage détaillé des reason codes P0 à des fins de qualité, au-delà de la doctrine

- **A_VERIFIER**
  - Comportement de QualityTracker sur `hugoback.encoors.com`
  - Disponibilité effective et périmètre des vues cohorte en prod distante
  - Influence des flags et settings sur l’activation / exposition des signaux qualité
  - Existence éventuelle de signaux micro-niveau non visibles dans le corpus audité

- **ABSENT / NOUVEAU_CONTRAT**
  - Catalogue canonique détaillé des ConversationQualitySignal (types, définitions, usages)
  - Contrat stabilisé entre signaux qualité, recommandations tuteur et surfaces produit (au-delà des principes généraux)

  # 02_decisions_documentaires — 80_observabilite_qualite_conversationnelle

- `DOMAINE_CODE = 80_observabilite_qualite_conversationnelle`
- `DOMAINE_LABEL = observabilité et qualité conversationnelle`

---

## 1. Objet du document

Ce document fixe les **décisions documentaires** à appliquer pour le domaine **observabilité et qualité conversationnelle** dans Hugo cœur.

Il ne décide ni d’une refonte du moteur, ni d’un chantier analytics autonome. Il cadre la manière correcte de documenter :
- la cible 2.0 ;
- le réel audité ;
- les écarts confirmés ;
- les zones encore ouvertes ou `A_VERIFIER`.

---

## 2. Principes de rédaction retenus

### D1 — Maintenir la distinction stricte cible / réel / glossaire

Toutes les futures rédactions du domaine doivent séparer explicitement :
- la **cible 2.0** issue de `spec_canonique_hugo_2_0` et du `complement_unique_specs_2_0` ;
- le **réel observable** issu des audits (`02_ETAT_MOTEUR_REEL`, `03_ETAT_PRODUIT_REEL`, `05_ECARTS_DOC_CODE_PRODUIT`, `07_RUNTIME_DEMO_REFERENCE`, `10_FICHE_RUNTIME_PROD_ENCOORS`) ;
- le **pont de vocabulaire** issu du `glossaire_alignement_hugo_reel_vs_spec`.

Conséquence documentaire :
- le glossaire ne doit jamais être cité comme preuve d’implémentation ;
- une formulation du type “le glossaire montre que c’est implémenté” est interdite ;
- toute phrase sur le réel doit être adossée à un audit ou à un constat croisé audit/code/produit.

### D2 — Ne pas relire la cible 2.0 comme une absence du réel

La documentation du domaine doit partir du principe suivant :
- Hugo cœur dispose déjà d’un socle réel sur ce domaine ;
- la cible 2.0 sert à **clarifier** et **stabiliser** la doctrine, pas à réécrire artificiellement le réel comme si tout restait à faire.

Conséquence documentaire :
- éviter les formulations du type “Hugo 2.0 devra introduire l’observabilité qualité” ;
- préférer “la cible 2.0 stabilise et clarifie un domaine déjà partiellement observable dans le réel”.

### D3 — Employer le vocabulaire doctrinal 2.0, mais raccorder les noms réels

La doctrine conserve les noms structurants :
- `QualityTracker`
- `ConversationQualitySignal`
- vues cohorte
- signaux de qualité conversationnelle

Mais les documents doivent maintenant faire apparaître, quand utile, les noms réels observés :
- `qualitytracker.py`
- `analyticscohortdashboard.py`
- `recordsessionsignal`
- `postconversationhooks`

Conséquence documentaire :
- les documents 2.0 gardent le nom canonique pour raisonner juste ;
- ils ajoutent ensuite le nom réel observé pour parler juste du code.

---

## 3. Décisions sur le vocabulaire du domaine

### D4 — Conserver `ConversationQualitySignal` comme nom canonique central

`ConversationQualitySignal` est retenu comme **nom doctrinal principal** du domaine.

Justification :
- le nom est déjà cohérent entre cible 2.0 et réel audité ;
- il n’y a pas de raison documentaire de le rebaptiser ;
- il constitue un bon pivot pour la suite des matrices objets et des vues tuteur/cohorte.

Conséquence documentaire :
- tous les futurs documents du domaine doivent utiliser `ConversationQualitySignal` comme entrée canonique ;
- si un nom réel complémentaire est utile, il vient en second, jamais à la place.

### D5 — Conserver `QualityTracker` comme nom de service canonique, en ajoutant `qualitytracker.py`

`QualityTracker` est retenu comme **nom doctrinal de service**.

Conséquence documentaire :
- dans les matrices backend 2.0 et documents de domaine, la formulation recommandée devient :
  - `QualityTracker` — implémentation réelle observée : `qualitytracker.py`
- on évite de rebaptiser la doctrine directement en nom de fichier Python.

### D6 — Introduire explicitement `analyticscohortdashboard.py` comme backing réel des vues cohorte observées

Les vues cohorte restent un concept doctrinal produit / analytics, mais la documentation doit désormais faire apparaître `analyticscohortdashboard.py` comme nom réel observé utile.

Conséquence documentaire :
- la doc ne doit plus parler des “vues cohorte” comme d’une abstraction sans ancrage ;
- elle ne doit pas non plus sur-affirmer qu’un dashboard final complet est déjà stabilisé en produit ;
- la bonne formule est : “vues cohorte prévues doctrinalement, avec une base réelle observée via `analyticscohortdashboard.py`”.

---

## 4. Décisions sur le récit du réel

### D7 — Documenter explicitement le caractère post-conversation des signaux qualité dans le réel local audité

Le domaine doit désormais être documenté en indiquant clairement que, dans le réel local audité :
- l’enregistrement de signaux qualité est post-conversation ;
- il passe par `postconversationhooks` ;
- `recordsessionsignal` est effectivement appelé ;
- ce point est confirmé par l’audit croisé `05_ECARTS_DOC_CODE_PRODUIT`.

Conséquence documentaire :
- toute ancienne formulation laissant entendre que le snapshot qualité n’est pas post-session doit être corrigée ou déclassée ;
- cette correction doit être considérée comme un recalage documentaire acté.

### D8 — Ne pas écrire que le front calcule les signaux qualité

La documentation du domaine doit expliciter que la qualité conversationnelle est traitée côté **backend**, dans la continuité du moteur, de la progression et des hooks post-conversation.

Conséquence documentaire :
- il faut éviter toute phrase qui laisserait croire que le front reconstruit ou calcule les signaux qualité ;
- les surfaces produit ne doivent être décrites que comme des **consommatrices d’états dérivés** ou de projections gouvernées.

### D9 — Décrire le domaine comme backend-first, avec surfaces métier dérivées

La ligne documentaire retenue est la suivante :
- le domaine qualité / observabilité est d’abord un domaine **backend-first** ;
- il peut nourrir les surfaces tuteur, cohorte, progression ou recommandations ;
- il n’est pas un sous-produit autonome, ni un front analytics indépendant, ni un pipeline parallèle au moteur.

Conséquence documentaire :
- toutes les docs du domaine doivent rappeler que l’observabilité qualité s’inscrit dans la chaîne runtime gouvernée de Hugo cœur ;
- aucune doc ne doit faire de ce domaine un système externe à la logique moteur.

---

## 5. Décisions sur les zones ouvertes

### D10 — Assumer explicitement qu’un catalogue canonique complet des signaux reste ouvert

La documentation doit maintenant dire clairement que :
- l’existence des signaux est fixée ;
- leur rôle doctrinal est fixé ;
- mais le **catalogue canonique complet** des `ConversationQualitySignal` reste encore ouvert.

Conséquence documentaire :
- on ne fige pas artificiellement une liste exhaustive si le corpus ne la prouve pas ;
- on crée au besoin une section “catalogue à stabiliser” plutôt qu’une pseudo-liste définitive.

### D11 — Maintenir la projection produit exacte comme sujet partiellement ouvert

Le corpus permet de dire que les signaux qualité nourrissent potentiellement les vues tuteur et cohorte, et plus indirectement la lecture de progression. En revanche, la projection produit exacte reste encore partiellement sous-spécifiée.

Conséquence documentaire :
- la doc ne doit pas affirmer qu’un contrat UI complet est déjà fixé pour toutes les surfaces ;
- elle doit distinguer :
  - ce qui est certain sur le backend ;
  - ce qui est plausible côté métier ;
  - ce qui reste à stabiliser côté projection produit.

### D12 — Marquer systématiquement le runtime distant comme `A_VERIFIER`

Pour ce domaine comme pour les autres, le comportement sur `hugoback.encoors.com` ne doit pas être supposé identique au local audité.

Conséquence documentaire :
- toute mention sur les dashboards cohorte, signaux qualité ou hooks qualité en prod distante doit être marquée `A_VERIFIER` si elle n’est pas directement auditée ;
- il faut éviter toute phrase du type “en production, le système fait déjà X” sans preuve runtime dédiée.

---

## 6. Décisions de non-régression doctrinale

### D13 — Interdire toute dérive vers un scoring opaque

La documentation du domaine doit réaffirmer que les signaux qualité :
- servent à lire, interpréter, recommander et aider ;
- ne constituent pas une note opaque sur les apprenants ;
- ne doivent pas devenir un substitut à l’accompagnement humain.

Conséquence documentaire :
- bannir les formulations évoquant un “score de qualité global” non expliqué ;
- préférer les termes “signal”, “indicateur”, “lecture de qualité”, “aide à l’interprétation”.

### D14 — Interdire toute dérive vers une exposition du verbatim non partagé

La doc doit rappeler que l’observabilité qualité n’autorise pas :
- l’accès libre au verbatim non partagé ;
- l’usage du verbatim brut comme source d’observabilité par défaut ;
- l’ouverture libre de données apprenant sensibles aux rôles non autorisés.

Conséquence documentaire :
- toute surface décrite pour tuteur, formateur, coordinateur ou admin doit rappeler le filtre de partage explicite et de confidentialité-first ;
- le domaine qualité ne crée aucun régime d’exception sur ce point.

### D15 — Interdire toute réécriture front-driven du domaine

La documentation doit rappeler que :
- le front ne pilote pas la logique de qualité conversationnelle ;
- il ne calcule pas le cœur des signaux ;
- il consomme des états ou projections backend.

Conséquence documentaire :
- ne pas présenter les dashboards ou vues tuteur comme des composants “intelligents” indépendants du backend ;
- ne pas rebasculer vers une lecture UI-first du domaine.

---

## 7. Décisions de mise à jour documentaire concrète

### D16 — Ajouter une section dédiée “observabilité et qualité conversationnelle” dans les docs 2.0 concernées

Le domaine mérite désormais une section documentaire dédiée, qui rappelle au minimum :
- l’objet du domaine ;
- les noms doctrinaux ;
- les noms réels observés ;
- la place du domaine dans la chaîne post-conversation ;
- les garde-fous de confidentialité et de non-scoring opaque ;
- les zones encore ouvertes.

Conséquence documentaire :
- éviter de laisser le sujet dispersé uniquement dans des matrices ou des allusions transverses ;
- créer une base de lecture stable pour les futurs prompts Cursor et analyses CTO.

### D17 — Ajouter une colonne “nom réel observé” dans les matrices concernées

Dans les matrices 2.0 ou documents de domaine, il faut désormais faire apparaître explicitement, pour ce domaine :
- `QualityTracker` → `qualitytracker.py`
- vues cohorte → `analyticscohortdashboard.py`
- enregistrement des signaux → `recordsessionsignal`, `postconversationhooks`

Conséquence documentaire :
- réduction des collisions de vocabulaire ;
- meilleure continuité entre doctrine, audit et code.

### D18 — Corriger ou déclasser les documents obsolètes sur le snapshot qualité

Les documents anciens contredits par `05_ECARTS_DOC_CODE_PRODUIT` sur le sujet du snapshot qualité doivent être :
- soit corrigés ;
- soit annotés comme obsolètes ;
- soit sortis du corpus de vérité active.

Conséquence documentaire :
- ne plus laisser circuler une affirmation fausse sur l’absence de post-conversation quality snapshot dans le réel local.

---

## 8. Formulation de référence à retenir

Pour les futures docs, la formulation de référence recommandée sur ce domaine est :

> Hugo cœur 2.0 prévoit une couche d’observabilité et de qualité conversationnelle backend-first, gouvernée, nourrie par la progression, les traces structurées et les signaux post-conversation, exposée au produit sous forme de vues et d’aides d’interprétation gouvernées, sans scoring opaque, sans exposition des champs P0 bruts, et sans accès libre au verbatim non partagé.

Cette formulation peut être reprise comme base, puis complétée par :
- les noms réels observés (`qualitytracker.py`, `analyticscohortdashboard.py`, `recordsessionsignal`, `postconversationhooks`) ;
- les garde-fous `A_VERIFIER` sur le runtime distant ;
- les zones encore ouvertes sur le catalogue complet des signaux.

---

## 9. Clôture documentaire de cette étape

À l’issue de cette étape, les décisions suivantes sont considérées comme actées pour le domaine :
- le domaine est **réel et déjà partiellement aligné**, pas simplement projeté ;
- `ConversationQualitySignal` reste le nom canonique central ;
- `QualityTracker` reste le nom doctrinal de service, avec raccord explicite à `qualitytracker.py` ;
- `analyticscohortdashboard.py` doit être visible dans la doc comme backing réel observé des vues cohorte ;
- l’enregistrement post-conversation des signaux qualité est documenté comme **réel local confirmé** ;
- le catalogue canonique complet des signaux reste **ouvert** ;
- tout ce qui dépend du runtime distant reste **A_VERIFIER** ;
- aucune documentation future ne doit faire dériver ce domaine vers un scoring opaque, une exposition libre du verbatim ou une architecture front-driven.

# 03_backlog_actions — 80_observabilite_qualite_conversationnelle

- `DOMAINE_CODE = 80_observabilite_qualite_conversationnelle`
- `DOMAINE_LABEL = observabilité et qualité conversationnelle`

---

## 1. Objet du backlog

Ce backlog liste les actions à mener pour **recaler, clarifier et stabiliser** le domaine observabilité / qualité conversationnelle dans Hugo cœur.

Il ne constitue pas un backlog produit global ni un plan de refonte moteur. Il est limité :
- à la documentation de référence ;
- au raccord vocabulaire cible / réel ;
- aux contrats minimaux du domaine ;
- aux vérifications nécessaires avant toute extension plus ambitieuse.

---

## 2. Règles de priorisation

Les priorités sont définies selon les critères suivants :
- **P1** : action nécessaire pour éviter une contre-vérité documentaire ou une mauvaise lecture du réel ;
- **P2** : action importante de stabilisation des contrats, du vocabulaire ou des surfaces ;
- **P3** : action utile mais non bloquante, à mener après recalage documentaire principal.

Les types d’action utilisés ici sont :
- `DOC` : mise à jour documentaire ;
- `AUDIT` : vérification ciblée du réel ;
- `SPEC` : formalisation cible / contrat ;
- `PROMPT_CURSOR` : préparation d’un prompt Cursor de vérification ou de mise à jour ;
- `A_VERIFIER` : action dépendante d’un runtime ou d’une variante non encore auditée.

---

## 3. Backlog priorisé

| ID | Priorité | Type | Action | Résultat attendu | Dépendances |
|---|---|---|---|---|---|
| OBSQ-01 | P1 | DOC | Corriger les documents encore ambigus ou faux sur le caractère post-conversation du snapshot qualité. | Plus aucun document actif ne laisse entendre que les signaux qualité ne sont pas enregistrés via `postconversationhooks` / `recordsessionsignal` dans le réel local audité. | `05_ECARTS_DOC_CODE_PRODUIT`, corpus docs actifs |
| OBSQ-02 | P1 | DOC | Ajouter dans la documentation 2.0 du domaine une formulation standard “backend-first, post-conversation, sans scoring opaque”. | Une base de formulation stable existe pour toutes les futures docs du domaine. | `spec_canonique_hugo_2_0`, `complement_unique_specs_2_0` |
| OBSQ-03 | P1 | DOC | Ajouter le couple doctrinal / nom réel observé pour le service qualité : `QualityTracker` → `qualitytracker.py`. | Les collisions de vocabulaire diminuent entre spec, audits et code. | glossaire d’alignement |
| OBSQ-04 | P1 | DOC | Ajouter le backing réel observé des vues cohorte : mention explicite de `analyticscohortdashboard.py` dans les docs de domaine. | Les vues cohorte ne sont plus documentées comme abstraction sans ancrage réel. | glossaire d’alignement |
| OBSQ-05 | P1 | DOC | Ajouter une note standard `A_VERIFIER` pour tout ce qui concerne le runtime distant Encoors sur ce domaine. | La doc ne sur-affirme plus le comportement prod distant à partir du local audité. | `05_ECARTS_DOC_CODE_PRODUIT`, `10_FICHE_RUNTIME_PROD_ENCOORS` si mobilisé ensuite |

| ID | Priorité | Type | Action | Résultat attendu | Dépendances |
|---|---|---|---|---|---|
| OBSQ-06 | P2 | SPEC | Formaliser un mini-catalogue canonique provisoire des familles de signaux qualité déjà légitimes doctrinalement : progression, maturité, dispersion, reason codes, blocages, éligibilités terminales. | Une base commune existe sans prétendre figer le catalogue complet des `ConversationQualitySignal`. | `spec_canonique_hugo_2_0`, `complement_unique_specs_2_0` |
| OBSQ-07 | P2 | SPEC | Définir le statut documentaire exact du domaine : “catalogue ouvert mais rôle doctrinal fixé”. | Les futurs documents cessent d’hésiter entre flou total et pseudo-contrat exhaustif. | `spec_canonique_hugo_2_0`, `complement_unique_specs_2_0` |
| OBSQ-08 | P2 | DOC | Ajouter une colonne `nom réel observé` dans les matrices concernées pour ce domaine. | Les matrices 2.0 affichent au minimum `QualityTracker`, `qualitytracker.py`, `analyticscohortdashboard.py`, `recordsessionsignal`, `postconversationhooks`. | glossaire d’alignement |
| OBSQ-09 | P2 | SPEC | Décrire plus proprement la relation entre `ConversationProgress`, signaux qualité, vues tuteur et vues cohorte. | Le domaine qualité est replacé dans la chaîne de consommation backend → projections métier, sans glisser vers une logique analytics autonome. | `spec_canonique_hugo_2_0` |
| OBSQ-10 | P2 | DOC | Ajouter dans la spec formateur/tuteur ou annexe associée une phrase claire sur l’usage des signaux qualité par le tuteur : lecture, interprétation, recommandation, sans contrôle moteur direct. | Le lien entre qualité conversationnelle et rôle tuteur devient explicite. | `spec_canonique_hugo_2_0`, `complement_unique_specs_2_0` |

| ID | Priorité | Type | Action | Résultat attendu | Dépendances |
|---|---|---|---|---|---|
| OBSQ-11 | P2 | AUDIT | Vérifier, dans le code réel, la structure exacte produite par `qualitytracker.py` et les objets persistés ou calculés associés. | Une base factuelle existe pour documenter le service sans extrapolation. | accès code local |
| OBSQ-12 | P2 | AUDIT | Vérifier le niveau exact de couplage entre `qualitytracker.py`, `postconversationhooks` et `analyticscohortdashboard.py`. | On sait mieux distinguer production des signaux, persistance éventuelle et projection cohorte. | accès code local |
| OBSQ-13 | P2 | PROMPT_CURSOR | Préparer un prompt Cursor dédié “cartographier les signaux qualité conversationnelle réellement calculés, persistés et exposés”. | Audit CTO exécutable et borné sur ce domaine. | glossaire + audits existants |
| OBSQ-14 | P2 | PROMPT_CURSOR | Préparer un prompt Cursor dédié “identifier les endpoints, serializers, views ou dashboards qui consomment les signaux qualité”. | Vision plus nette des surfaces réellement branchées. | accès code local |
| OBSQ-15 | P2 | A_VERIFIER | Vérifier si la variante distante Encoors expose le même comportement qualité que le local audité. | Le statut prod distant du domaine cesse d’être supposé. | accès runtime distant / inspection HTTP ciblée |

| ID | Priorité | Type | Action | Résultat attendu | Dépendances |
|---|---|---|---|---|---|
| OBSQ-16 | P3 | SPEC | Préparer une annexe légère “pseudo-schéma” pour `ConversationQualitySignal` : rôle, producteur principal, consommateurs, exposition front éventuelle, zones ouvertes. | Le domaine qualité rejoint le niveau de précision pseudo-schéma attendu par la base 2.0. | `complement_unique_specs_2_0` |
| OBSQ-17 | P3 | SPEC | Préparer un mapping non exhaustif “signal → usage tuteur/cohorte/recommandation” sans figer encore une taxonomie finale. | Le domaine devient plus exploitable pour la suite produit sans sur-spécifier. | OBSQ-06, OBSQ-09 |
| OBSQ-18 | P3 | DOC | Ajouter une section “anti-dérives” rappelant explicitement : pas de scoring opaque, pas d’exposition du verbatim, pas de pilotage front. | Les garde-fous de non-régression sont visibles dans le domaine lui-même. | `spec_canonique_hugo_2_0`, `complement_unique_specs_2_0` |
| OBSQ-19 | P3 | AUDIT | Vérifier s’il existe des tests dédiés qualité au-delà de `testqualitysignals.py` dans le réel local. | Meilleure visibilité sur la robustesse réelle du domaine. | accès code local |
| OBSQ-20 | P3 | DOC | Ajouter un court encadré de vérité documentaire : “ce domaine est partiellement réel, partiellement ouvert, non intégralement prouvé en prod distante”. | Les prochaines lectures restent propres et non spéculatives. | rapport d’écarts + matrice + décisions |

---

## 4. Séquencement recommandé

### Sprint documentaire 1 — recalage minimal obligatoire

Actions à mener en premier :
- `OBSQ-01`
- `OBSQ-02`
- `OBSQ-03`
- `OBSQ-04`
- `OBSQ-05`

Objectif :
- supprimer les contre-vérités documentaires ;
- rendre le domaine lisible ;
- fixer le bon couple doctrine / noms réels ;
- empêcher toute confusion entre local audité et runtime distant.

### Sprint documentaire 2 — stabilisation du contrat minimal

Actions à mener ensuite :
- `OBSQ-06`
- `OBSQ-07`
- `OBSQ-08`
- `OBSQ-09`
- `OBSQ-10`

Objectif :
- stabiliser le périmètre canonique du domaine ;
- mieux relier signaux qualité, progression, tutorat et vues cohorte ;
- rendre les futures specs plus cohérentes.

### Sprint d’audit ciblé — consolidation CTO

Actions à mener ensuite :
- `OBSQ-11`
- `OBSQ-12`
- `OBSQ-13`
- `OBSQ-14`
- `OBSQ-15`

Objectif :
- sortir d’une lecture seulement documentaire ;
- produire un audit borné, exécutable et utile pour le CTO ;
- distinguer clairement calcul, persistance, exposition et variante distante.

### Sprint d’approfondissement — non bloquant

Actions à mener après recalage :
- `OBSQ-16`
- `OBSQ-17`
- `OBSQ-18`
- `OBSQ-19`
- `OBSQ-20`

Objectif :
- donner au domaine une forme quasi stable sans sur-spécifier ;
- préparer la suite produit/tuteur/cohorte ;
- renforcer les garde-fous documentaires.

---

## 5. Points explicitement hors backlog de ce domaine

Les sujets suivants sont volontairement exclus de ce backlog, car hors périmètre du domaine ou trop larges à ce stade :
- refonte générale de l’orchestrateur ;
- redesign complet des vues tuteur ;
- refonte globale des analytics produit ;
- chantier infra RLS / Postgres au sens large ;
- backlog Hugo & Cie ;
- catalogues transverses d’évaluation, mémoire ou documentaire hors lien direct avec les signaux qualité.

---

## 6. Critère de clôture du domaine documentaire

Le domaine pourra être considéré comme **documentairement recalé** lorsque les conditions suivantes seront remplies :
1. les docs actives ne diffusent plus de contre-vérité sur les hooks qualité post-conversation ;
2. le couple `QualityTracker` / `qualitytracker.py` et l’ancrage `analyticscohortdashboard.py` sont visibles dans les docs de référence ;
3. le domaine est décrit comme backend-first, sans scoring opaque, sans exposition du verbatim non partagé ;
4. le catalogue des signaux est explicitement décrit comme **ouvert mais cadré** ;
5. le runtime distant reste proprement marqué `A_VERIFIER` tant qu’il n’a pas été confirmé ;
6. un prompt Cursor d’audit ciblé existe pour cartographier calcul, persistance et exposition des signaux.

---

## 7. Priorité exécutable immédiate

Si une seule séquence doit partir maintenant, la séquence recommandée est :

1. `OBSQ-01` Corriger les docs obsolètes sur le snapshot qualité.
2. `OBSQ-03` Ajouter `QualityTracker` → `qualitytracker.py`.
3. `OBSQ-04` Ajouter `analyticscohortdashboard.py` dans la doc du domaine.
4. `OBSQ-06` Fixer un mini-catalogue provisoire des familles de signaux.
5. `OBSQ-13` Préparer le prompt Cursor d’audit du domaine.

Cette séquence donne rapidement :
- un domaine documenté proprement ;
- un vocabulaire stabilisé ;
- une base d’audit exploitable pour le CTO ;
- sans engager une refonte ni sur-promettre la prod.
