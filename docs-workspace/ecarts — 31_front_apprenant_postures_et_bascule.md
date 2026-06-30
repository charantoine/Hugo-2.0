# 00_rapport_ecarts — 31_front_apprenant_postures_et_bascule

> **Mise à jour post-cluster 16 — 2026-06-18** · **PARTIEL+ livré local :** `PostureSelector` (transitions backend, verrou), `LearnerSceneContextBar`, profils CSS homogènes (mêmes blocs), CTA advisory. **Tests :** cluster 16 (15 backend + 10 Playwright). **CIBLE :** matrice SW-xx.  
> **Mise à jour juin 2026 — 30/06 :** layout apprenant **v2** (`VITE_LEARNER_UI_V2`, défaut ON) — affichage uniquement ; voir `03_ETAT_PRODUIT_REEL.md` §2.1.

## Domaine

- `DOMAINE_CODE = 31_front_apprenant_postures_et_bascule`
- `DOMAINE_LABEL = front apprenant — posture visible, bascule de régime et CTA de conduite`

---

## 1. Objet du rapport

Ce rapport qualifie, pour le seul domaine **front apprenant / visibilité de posture / bascule de régime conversationnel / CTA de conduite**, l’écart entre :
- la **cible 2.0** décrite par la spec canonique, son complément et la spec interface ;
- le **réel observable** décrit par les audits produit et les documents de démonstration ;
- le **pont de vocabulaire** fourni par le glossaire d’alignement.

Le périmètre est strictement **Hugo cœur**. Ce document ne traite ni Hugo & Cie, ni les vues tuteur/formateur, ni les prompts détaillés. Il vise à établir :
- ce que la cible 2.0 fixe déjà pour le front apprenant ;
- ce que le réel audité montre effectivement dans `frontend_1.8` ;
- où se situent les écarts, en particulier sur les **boutons / contrôles de bascule entre régimes conversationnels**.

---

## 2. Règles de vérité appliquées

### 2.1 Sources mobilisées

Pour parler du **réel**, ce rapport s’appuie d’abord sur :
- `03_ETAT_PRODUIT_REEL.md` pour la surface montrable du front apprenant, ses routes, composants et contrats API réellement consommés ;
- `09_PARCOURS_DEMO_ET_SCENARIOS.md` pour ce qui est démontrable côté apprenant sans sur-vendre ;
- le glossaire d’alignement pour raccorder le vocabulaire cible 2.0 aux noms réellement observés.

Pour parler de la **cible**, ce rapport s’appuie sur :
- `spec_canonique_hugo_2_0.md` ;
- `complement_unique_specs_2_0.md` ;
- `specs-interface-2.0.md`.

### 2.2 Garde-fous

- La spec 2.0 décrit une **cible** ; elle ne prouve jamais qu’une fonctionnalité est livrée.
- Le glossaire est un **pont de vocabulaire** ; il n’est pas une preuve d’implémentation.
- Le réel n’est pas déduit d’un seul fichier : il est lu à partir du croisement entre surface produit auditée, parcours de démo et points de vocabulaire alignés.
- Toute affirmation portant sur un endpoint ou un comportement runtime non confirmé dans les audits du réel reste marquée `A_VERIFIER`.
- La doctrine 2.0 reste prioritaire : le front apprenant **consomme** des états backend (`UIState`, progression, états CTA, posture si exposée) et ne pilote jamais la conduite tutorale réelle.

---

## 3. Périmètre cible 2.0 du domaine

### 3.1 Ce que la cible 2.0 fixe déjà

Dans la cible 2.0, le front apprenant doit être un **front dérivé d’états**, non un front pilote.

La base 2.0 fixe déjà les points suivants :
- le front consomme un `UIState` propre, sans exposition de `TurnState`, des champs P0 bruts, des prompts complets ni du verbatim interne non partagé ;
- la progression conversationnelle doit être rendue visible sous une forme produit lisible : scène, quête active, maturité, branche prioritaire, actions terminales ;
- la **posture active** peut être visible côté produit si le produit l’assume ;
- les **transitions de posture** peuvent être exposées à l’utilisateur, mais uniquement comme actions bornées sur contrat backend ;
- l’apprenant peut, dans la cible, demander une posture en début de séance via un endpoint de type `PATCH sessions/{id}/posture`, avec refus possible si la séance est trop avancée ;
- la synthèse et l’évaluation sont des **CTA terminales** pilotées côté backend par l’éligibilité calculée.

La cible fixe donc bien une architecture front apprenant capable de montrer :
- où en est la séance ;
- dans quel régime elle se situe ;
- quelles actions sont possibles maintenant ;
- sans jamais transformer le front en source de vérité comportementale.

### 3.2 Ce que la cible 2.0 laisse encore ouvert

La base 2.0 reconnaît explicitement que plusieurs éléments restent **ouverts cadrés** sur ce domaine :
- la chorégraphie UX exacte des transitions de posture ;
- la verbalisation précise des messages de transition ou de refus ;
- la granularité des états visuels des boutons de bascule ;
- la palette détaillée des commandes de reprise / relance / changement de mode ;
- la maquette logique complète des états de boutons en cas de transition autorisée, refusée, déconseillée ou déjà verrouillée.

Autrement dit, la doctrine et le contrat conceptuel sont largement posés, mais la **spec UI fine** de la bascule de régime reste incomplète.

---

## 4. Photo du réel observable

### 4.1 Surface apprenant réellement auditée

Le réel produit audité montre une surface apprenant claire et montrable dans `hugo-hugoluciafrontend1.8` :
- routes `login`, `app`, `app/session/:sessionId` ;
- layout `ProdLearnerLayout` ;
- composants principaux `ProdLearnerWorkspace.vue`, `ProdLearnerSessionView.vue`, `HugoProgressPanel.vue`.

Le parcours produit observable côté apprenant comprend :
- authentification ;
- historique et création de session ;
- chat avec streaming SSE ou fallback ;
- rechargement de `ui-state` après chaque tour ;
- actions de synthèse, évaluation, génération de trace et partage.

### 4.2 Contrat UI réellement consommé

Le réel montre une consommation claire du contrat `GET .../ui-state` par le front apprenant.

Le front produit consomme notamment, via `engagementUiModel.js` et `HugoProgressPanel.vue` :
- scène ;
- progression ;
- quête active ;
- couleur de maturité ;
- état des boutons synthèse / évaluation ;
- objets persistants éventuels.

Le réel confirme donc fortement l’alignement sur une logique **backend-first** du front apprenant.

### 4.3 Ce que le panneau de progression montre vraiment

Le corpus d’audit et le document de démo montrent que `HugoProgressPanel` rend visible :
- une progression en macro-scènes lisibles côté apprenant ;
- des CTA de synthèse et d’évaluation pilotées par le backend ;
- une grammaire UI simple, sans heuristique P0 recalculée localement.

Le parcours de démo insiste d’ailleurs sur le fait que :
- le panneau apprenant consomme un contrat `ui-state` ;
- les boutons de synthèse et d’évaluation sont réellement branchés ;
- le front ne recalcule pas localement les conditions de disponibilité de ces actions.

### 4.4 Ce que le réel ne montre pas clairement

En revanche, le réel audité ne montre pas explicitement, dans la surface produit apprenant décrite :
- un **sélecteur visible de posture** dans `ProdLearnerWorkspace` ;
- un composant front apprenant documenté pour choisir entre `diagnostic`, `réflexif` et `révision` ;
- une chorégraphie UI explicitée de la bascule de mode pendant la séance ;
- un ensemble de messages UI détaillés pour succès, refus, blocage ou verrouillage d’une bascule de posture.

Le glossaire d’alignement confirme en outre que l’endpoint cible `PATCH sessions/{id}/posture` reste **A_VERIFIER** côté réel observé. Il ne faut donc pas affirmer, sur le seul corpus audité, que cette commande est déjà démontrée comme livrée dans le parcours apprenant prod.

### 4.5 CTA terminales : oui ; bascule de posture : non démontrée

Le réel observable documente bien :
- `request-synthesis` ;
- `request-evaluation` ;
- `generate-trace` ;
- `share`.

Ces actions sont visibles dans le workspace apprenant ou son panneau de progression. En revanche, le même niveau de preuve n’existe pas, dans ce corpus, pour une **action apprenant explicite de changement de posture**.

Le domaine présente donc une dissymétrie nette :
- les **CTA terminales** sont réelles, documentées et branchées ;
- la **bascule de posture** est doctrinalement prévue et partiellement spécifiée côté cible, mais non documentée comme composant produit livré dans le réel observable.

---

## 5. Analyse narrative des écarts

### 5.1 Zone d’alignement solide

Le domaine est bien aligné sur un point essentiel : le front apprenant est déjà pensé et implémenté comme une **surface dérivée d’états backend**.

Le réel confirme plusieurs invariants 2.0 :
- consommation d’un `UIState` propre ;
- présence d’un panneau de progression ;
- visibilité d’une progression de séance ;
- CTA terminales pilotées côté backend ;
- absence d’exposition des champs P0 bruts dans le parcours prod.

Sur ces points, il n’y a pas de refonte doctrinale à lancer. Le socle produit est cohérent avec Hugo 2.0.

### 5.2 Premier écart : posture visible encore incomplètement contractualisée

La cible 2.0 dit que la posture active peut être visible si le produit l’assume, et la spec interface dit qu’un affichage du mode ou de la posture est attendu côté apprenant.

Mais le réel audité ne documente pas clairement, dans la surface apprenant prod montrable, un rendu explicite et stabilisé de cette posture. On peut donc dire :
- la **visibilité de posture** est bien une exigence cible ;
- elle n’est pas suffisamment prouvée comme élément produit stabilisé dans le réel audité.

L’écart est donc un écart de **preuve produit** et de **spécification d’exposition**, plus qu’un désalignement doctrinal.

### 5.3 Deuxième écart : bouton de bascule prévu en cible, pas démontré en réel

La spec interface 2.0 dit explicitement qu’un **sélecteur de posture / mode** est prévu, bloqué après un certain nombre de messages et de phase, et que l’apprenant peut choisir une posture en début de fil.

Mais le corpus du réel audit ne montre pas, au même niveau de précision :
- le composant exact ;
- son emplacement ;
- ses états ;
- son branchement ;
- sa présence effective dans `ProdLearnerWorkspace`.

Le glossaire demande d’ailleurs de ne pas présenter `PATCH sessions/{id}/posture` comme acquis du réel sans relecture complémentaire. Cet écart est donc **confirmé documentairement** :
- cible : oui, la bascule est prévue ;
- réel observable : pas assez de preuve pour la considérer comme livrée dans le parcours apprenant prod.

### 5.4 Troisième écart : CTA terminales bien spécifiées, CTA de conduite insuffisamment détaillées

La synthèse et l’évaluation disposent déjà, côté cible et côté réel, d’un niveau de formalisation convenable :
- conditions d’éligibilité côté backend ;
- présence UI ;
- états pilotés par le serveur ;
- visibilité dans le panneau de progression.

À l’inverse, les CTA de **conduite conversationnelle** — et en premier lieu la bascule de régime — restent incomplètement décrites :
- états visuels absents ou sous-spécifiés ;
- messages d’aide / de refus non fixés ;
- différence entre posture visible, posture sélectionnable, posture suggérée et posture verrouillée non suffisamment documentée ;
- absence de matrice d’états comparable à celle des CTA terminales.

Le manque documentaire est donc particulièrement net sur la **micro-spécification front** de la bascule.

### 5.5 Quatrième écart : confusion potentielle entre régime, posture et geste

La canonique 2.0 distingue clairement :
- **régime conversationnel** comme politique globale ;
- **posture active** comme valeur runtime ;
- **geste tutoral** comme mouvement local interne au régime.

Or dès qu’on parle de boutons de bascule, le risque documentaire est de faire glisser l’interface vers une logique :
- “changement de mode” trop large ;
- ou pire, “choix de geste” par l’apprenant.

Le domaine a donc besoin d’un travail documentaire précis pour éviter une dérive front-driven. Les boutons de bascule doivent rester formulés comme **demande bornée de posture globale** au backend, pas comme pilotage fin de la conduite par l’apprenant.

### 5.6 Cinquième écart : spécification UI fine insuffisante

La base actuelle couvre bien :
- le front apprenant comme surface dérivée ;
- les panneaux et CTA terminales ;
- l’existence potentielle d’un sélecteur de posture.

Mais elle ne couvre pas encore, au niveau nécessaire pour une implémentation propre :
- la matrice des états du contrôle de bascule ;
- les textes UI ;
- les raisons de blocage ;
- le comportement de verrouillage après avancement de séance ;
- la place exacte du contrôle dans `ProdLearnerWorkspace` et `HugoProgressPanel` ;
- la distinction entre affichage passif de posture et action active de demande de changement.

L’écart principal du domaine est donc un **écart de documentation produit fine**, pas un écart de doctrine globale.

---

## 6. Lecture par niveau de vérité

### 6.1 Implémenté / observable

Le réel audité permet d’affirmer comme **observable** :
- un front apprenant prod montrable ;
- un workspace apprenant branché au backend ;
- un `UIState` réellement consommé ;
- un panneau de progression lisible ;
- des CTA terminales de synthèse et d’évaluation branchées ;
- une logique backend-first sans heuristique P0 locale côté front prod.

### 6.2 Cible 2.0

Relèvent clairement de la **cible 2.0** :
- l’exposition éventuelle de la posture active ;
- un sélecteur de posture / mode en début de séance ;
- une action backend de changement de posture bornée ;
- l’idée que certaines transitions de posture peuvent être exposées à l’utilisateur ;
- une grammaire front montrant scène, progression, posture, actions possibles.

### 6.3 Écarts confirmés

À ce stade, les écarts confirmés sont principalement :
- manque de preuve du **sélecteur de posture** dans le réel apprenant prod audité ;
- manque de documentation fine sur les **boutons de bascule** et leurs états ;
- absence de matrice stable des messages UI associés à la bascule ;
- couverture documentaire plus forte sur les CTA terminales que sur les CTA de conduite conversationnelle.

### 6.4 A_VERIFIER

Restent explicitement `A_VERIFIER` :
- l’existence réellement branchée du `PATCH sessions/{id}/posture` dans le runtime observé de référence ;
- la présence d’un contrôle de bascule dans `ProdLearnerWorkspace` côté prodshowable ;
- les variantes éventuelles entre runtime local et runtime distant Encoors sur ce sujet ;
- le niveau réel de visibilité de la posture active côté front apprenant dans toutes les variantes de démo.

---

## 7. Garde-fous documentaires pour la suite

### 7.1 Ce qu’il ne faut pas faire

Il faut éviter :
1. de conclure que la bascule de posture est livrée parce qu’elle est décrite dans la spec interface ;
2. de conclure qu’un endpoint `set-posture` est réel parce qu’il apparaît dans la cible ou le glossaire ;
3. de transformer le front apprenant en pilote de la conduite tutorale ;
4. de confondre posture globale et gestes tutoraux locaux ;
5. de documenter un bouton de bascule comme un “choix libre de stratégie moteur” côté apprenant.

### 7.2 Ce qu’il faut privilégier

La bonne trajectoire documentaire sur ce domaine est :
- stabiliser un **contrat cible** de visibilité de posture ;
- séparer clairement **affichage de posture**, **demande de bascule**, **transition backend automatique** et **suggestion de changement** ;
- produire une **matrice UI des états** du contrôle de bascule ;
- rattacher explicitement chaque élément soit à la cible, soit au réel observable, soit à `A_VERIFIER` ;
- conserver l’invariant backend-first : le bouton demande, le backend arbitre.

---

## 8. Conclusion opérationnelle du domaine

Le domaine `31_front_apprenant_postures_et_bascule` est doctrinalement bien posé, mais insuffisamment couvert au niveau documentaire fin.

Le réel audité montre un front apprenant solide sur la progression, le `UIState` et les CTA terminales. En revanche, la **bascule entre régimes conversationnels côté apprenant** reste une zone incomplètement documentée :
- bien cadrée dans la cible ;
- non suffisamment démontrée dans le réel ;
- non suffisamment spécifiée au niveau interaction produit.

La suite logique pour ce domaine est donc :
- documenter proprement les écarts ;
- produire une matrice d’états de la bascule ;
- fixer les décisions documentaires ;
- limiter ensuite le backlog à des actions d’alignement contrat / vocabulaire / spec UI, sans dérive vers une refonte front-driven.

# Hugo — matrice de bascule front apprenant et matrice maquettée détaillée

## Statut du document

Ce document consolide, dans un seul support, deux niveaux d’analyse sur la bascule entre régimes conversationnels côté apprenant : une **matrice de couverture documentaire et produit** puis une **matrice maquettée de comportement UI** destinée à servir de base de spécification produit et de chantier CTO.[1][2][3]

Il décrit un **état cible/documentaire consolidé** et ses écarts avec le **réel audité** ; il ne doit pas être relu comme une preuve d’implémentation déjà livrée dans Hugo cœur.[1][4][3]

## Cadre de lecture

La doctrine 2.0 fixe que Hugo est un moteur tutoriel multi-postures piloté par état, avec backend Django orchestré, TutorPrompt comme pivot runtime, P0 comme noyau de régulation locale, et un front apprenant strictement dérivé d’objets produit comme `UIState`, sans exposition brute des champs P0 ni pilotage conversationnel par le front.[1][4]

Dans ce cadre, la posture active est une valeur runtime globale par tour, sélectionnée ou maintenue côté backend ; le front peut au plus **restituer un état produit** et déclencher des **actions bornées** comme une demande de changement de posture ou une action terminale, mais il ne doit jamais piloter la conduite tutorale en autonomie.[1][4]

Le corpus 2.0 reconnaît explicitement que l’existence d’un état de posture, d’un sélecteur et de règles de transition backend est déjà cadrée, mais que la **chorégraphie UX détaillée**, la verbalisation exacte et la granularité des messages de transition restent encore ouvertes ou sous-spécifiées.[1]

## Hypothèses structurantes

Les régimes principaux explicitement fixés par la canonique sont : **réflexif**, **diagnostic** et **révision de savoirs** ; l’évaluation n’est pas un quatrième régime principal permanent mais une branche terminale spécialisée de fin de scénario, soumise à des conditions d’éligibilité et à une validation humaine finale hors autonomie certificative.[1]

Le front apprenant doit rendre perceptibles au minimum la scène de séance, la progression, la quête ou branche active, la couleur de maturité, la posture active si le produit choisit de l’exposer, ainsi que l’état des actions terminales de synthèse et d’évaluation.[1][4][2]

La spec interface 2.0 ajoute qu’un sélecteur de posture/mode est prévu côté apprenant, qu’il peut être utilisé en début de fil, puis bloqué après un certain nombre de messages ou une phase trop avancée ; en revanche, la palette exacte des actions, les messages détaillés et la spécification UI exhaustive ne sont pas encore listés.[2]

Le glossaire d’alignement demande enfin de distinguer soigneusement ce qui relève d’un **contrat cible encore projeté** — par exemple `PATCH sessions/{id}/posture` — de ce qui est déjà **observable dans le réel audité** — par exemple `GET .../ui-state`, `POST .../request-synthesis` ou `POST .../request-evaluation`.[3]

## Matrice de bascule documentaire et produit

### Objet de la matrice

La matrice suivante répond à quatre questions : ce qui est déjà fixé dans la cible 2.0, ce qui est observable dans le réel audité, ce qui manque dans la documentation front apprenant, et le niveau de vérité à retenir pour préparer un chantier d’implémentation ou de respecification.[1][2][3]

| Élément | Cible 2.0 consolidée | Réel audité / observable | Statut | Conséquence documentaire |
|---|---|---|---|---|
| Exposition de la posture active | La posture active peut être exposée dans `UIState` si le produit l’assume, comme état produit compréhensible.[1][4] | Les audits et parcours de démo documentent surtout scène, progression, maturité, synthèse et évaluation, sans preuve solide d’un affichage stabilisé du mode actif dans le workspace prod apprenant.[5][6] | Alignement partiel | Spécifier explicitement où et comment la posture active apparaît dans le workspace. |
| Sélecteur de posture/mode apprenant | Un sélecteur de posture/mode est prévu ; l’apprenant peut choisir une posture en début de fil dans des conditions sûres.[2][1] | Le corpus d’audit réel utilisé ne confirme pas formellement ce sélecteur comme livré dans le front montrable.[3][5] | À vérifier | Ne pas présenter le composant comme déjà livré ; le traiter comme cible produit à formaliser. |
| Endpoint de demande de bascule | `PATCH sessions/{id}/posture` est fixé comme endpoint minimal de changement de posture en début de séance, avec refus motivé si séance trop avancée.[1] | Le glossaire classe cet endpoint comme non confirmé dans le réel audité mobilisé.[3] | À vérifier | Garder l’endpoint comme contrat cible, pas comme fait du réel. |
| Fenêtre temporelle autorisée pour la bascule | Sélection explicite possible surtout en début de séance ; ensuite maintien ou ajustement backend selon règles de transition.[1] | Aucun scénario de démo produit n’exhibe une bascule manuelle apprenant en cours de séance avancée.[5] | Alignement partiel | Détailler le verrouillage temporel côté UI et côté message utilisateur. |
| Boutons explicites de régime dans le workspace | La cible permet d’exposer les transitions de posture si le produit choisit de les exposer.[1] | Le parcours apprenant réel documenté ne décrit pas de groupe de boutons “Diagnostic / Réflexif / Révision”.[5][6] | Absent dans l’audit | Produire une quasi-maquette dédiée des contrôles de bascule. |
| État verrouillé de la bascule | Le refus backend si séance trop avancée est prévu doctrinalement ; la spec interface mentionne un blocage après un certain nombre de messages ou de phase.[1][2] | Les docs réelles ne décrivent pas précisément disabled, locked, hidden, warning, ni texte d’aide associé.[5][6] | Sous-spécifié | Créer une matrice d’états UI complète. |
| Motif visible de refus | Le serveur doit pouvoir répondre “appliqué” ou “refus motivé”.[1] | Aucun wording précis de refus n’est documenté dans l’UI apprenant actuelle.[2][5] | Sous-spécifié | Spécifier bannière, toast, inline helper, et niveau de détail du motif. |
| Distinction posture visible / posture sélectionnable / transition automatique | La canonique distingue explicitement posture active runtime, sélection de session et ajustement backend ultérieur.[1] | Cette distinction n’est pas clarifiée finement dans la grammaire UI apprenant existante.[2][6] | Friction documentaire | Séparer ces trois niveaux dans la doc et dans les composants. |
| Front backend-first | Le front consomme `UIState` et actions bornées ; il ne doit pas consommer les objets P0 bruts.[1][4] | Le réel 1.8 documente précisément une logique de front branchée sur `ui-state` et des CTA de synthèse/évaluation pilotés par le back.[5][6] | Aligné | Réutiliser ce pattern pour la bascule de posture. |
| CTA terminales comme modèle de référence | L’état des actions terminales est dérivé côté backend et restitué au front.[1][2] | Les boutons synthèse/évaluation sont décrits comme déjà branchés et gouvernés côté serveur dans le parcours de démo.[5] | Aligné | Utiliser la même grammaire d’état pour les contrôles de bascule. |
| Chorégraphie UX détaillée des transitions | L’existence des transitions est fixée, mais la chorégraphie UX et les messages détaillés restent ouverts mais cadrés.[1] | Aucun audit produit ne couvre cette chorégraphie finement.[5][6] | Ouvert cadré | Sujet prioritaire de respecification front apprenant. |

## Diagnostic consolidé

Le socle doctrinal est **suffisamment solide** pour justifier une spécification front détaillée de la bascule : posture active, sélection bornée en ouverture, refus motivé, front piloté par `UIState`, backend gardien des règles, et distinction stricte entre régime conversationnel et gestes locaux.[1][4]

En revanche, le corpus actuel ne fournit pas encore un contrat produit satisfaisant sur la **micro-interaction** : composition visuelle du sélecteur, états visibles, libellés, niveau d’explication, modalités de refus, comportement lors d’un succès, et rapport entre demande utilisateur et ajustement ultérieur du backend.[2][1]

Le manque n’est donc pas doctrinal ; il est principalement **produit / interface / contrat d’état**.[2][3]

## Principes de conception retenus pour la matrice maquettée

La matrice maquettée ci-dessous adopte cinq principes compatibles avec la doctrine 2.0 :

- Le front apprenant ne choisit jamais librement une logique moteur ; il **demande** une posture dans un cadre borné.[1][4]
- Une seule posture globale est active par tour ; le composant de bascule ne doit jamais suggérer un multi-mode simultané.[1]
- Le contrôle doit être le plus simple possible pour l’apprenant : vocabulaire non technique, lisibilité immédiate, absence de reason codes bruts, et pas d’exposition de variables moteur.[1][2]
- Le backend reste source de vérité pour l’autorisation, l’application, le refus, et l’état post-transition.[1][3]
- Les CTA terminales existantes de synthèse/évaluation fournissent la bonne analogie de comportement : **états dérivés côté serveur, lecture claire côté UI**.[5][1]

## Matrice maquettée détaillée

### 1. Architecture UI cible minimale

Le composant recommandé côté apprenant est un bloc unique de type **Mode de travail** placé dans le workspace conversationnel, dans une zone stable et lisible, idéalement au-dessus du fil ou dans le panneau de progression, mais jamais comme barre flottante autonome pilotant la séance.[1][2]

Ce bloc comporte quatre sous-parties :

1. un titre court, par exemple `Mode de travail` ;
2. un état visible `Mode actuel` ;
3. un groupe d’actions bornées pour demander une bascule ;
4. une zone d’aide / statut expliquant pourquoi l’action est possible, indisponible ou refusée.[2][1]

### 2. Palette visible recommandée

Le vocabulaire visible recommandé côté apprenant doit rester compréhensible et éviter le jargon moteur. Une formulation sobre peut être :

| Régime doctrinal | Libellé UI recommandé | Description d’aide courte |
|---|---|---|
| Réflexif | Réfléchir à une situation | Partir d’une situation vécue pour comprendre ce qui s’est joué.[1] |
| Diagnostic | Analyser un problème | Clarifier un problème et explorer ses causes plausibles.[1] |
| Révision de savoirs | Réviser une notion | Revoir un contenu, une règle ou une méthode sans partir en cours magistral.[1] |
| Évaluation facultative | Faire le point / s’évaluer | Action terminale, non régime permanent, déjà couverte par les CTA d’évaluation.[1][2] |

L’évaluation ne doit pas être affichée comme un bouton pair des trois autres régimes, car la canonique fixe qu’il ne s’agit pas d’un régime principal continu mais d’une branche terminale spécialisée.[1]

### 3. États de haut niveau du bloc de bascule

| Code d’état UI | Visibilité | Action possible | Sens produit | Source de vérité attendue |
|---|---|---|---|---|
| `HIDDEN` | Bloc absent | Non | Le produit ne choisit pas d’exposer la bascule dans ce contexte.[1] | `UIState` ou configuration produit backend.[4] |
| `VISIBLE_READONLY` | Bloc visible | Non | Le mode actuel est montré, sans possibilité de demande de changement.[1] | `UIState` dérivé côté backend.[1] |
| `VISIBLE_SWITCHABLE` | Bloc visible | Oui | L’apprenant peut demander une bascule car la séance est encore dans une zone autorisée.[2][1] | `UIState` + endpoint de changement cible.[1] |
| `VISIBLE_LOCKED` | Bloc visible | Non | La bascule existe conceptuellement mais n’est plus autorisée à ce stade de la séance.[2][1] | Backend ; ne jamais inférer localement dans le front.[1] |
| `VISIBLE_PENDING` | Bloc visible | Temporairement non | Une demande de bascule a été envoyée et attend une réponse serveur.[1] | État de requête client + retour serveur. |
| `VISIBLE_REFUSED` | Bloc visible | Variable | La demande a été rejetée avec motif montrable et retour à l’état précédent.[1] | Réponse serveur. |
| `VISIBLE_APPLIED` | Bloc visible | Variable | La demande a été appliquée et l’état produit a été rafraîchi avec nouvelle posture active.[1] | Réponse serveur + nouveau `UIState`. |

### 4. États détaillés par bouton

Chaque bouton de régime visible doit pouvoir être lu à travers une grammaire homogène inspirée des CTA terminales existantes.[5][1]

| État du bouton | Apparence recommandée | Clic | Sens | Message d’aide recommandé |
|---|---|---|---|---|
| `ACTIVE_CURRENT` | Bouton plein ou accentué, non ambigu | Non | C’est le mode actuellement actif.[1] | `Mode actuel` |
| `AVAILABLE` | Bouton secondaire normal | Oui | La demande de bascule est autorisée maintenant.[2][1] | `Disponible maintenant` |
| `DISCOURAGED` | Bouton visible avec warning léger | Oui, avec confirmation | Changement possible mais peu recommandé selon état de séance ; ce statut n’est pas explicitement fixé dans la canonique mais est cohérent comme extension produit prudente, à formaliser comme choix UX et non comme vérité doctrinale.[2][1] | `Possible, mais cela risque de casser le fil` |
| `LOCKED` | Bouton grisé ou neutralisé | Non | Changement non autorisé car séance trop avancée ou contexte non compatible.[2][1] | `Indisponible à ce stade` |
| `HIDDEN` | Bouton absent | Non | Le régime n’est pas exposé dans ce contexte produit.[1] | Aucun |
| `PENDING` | Bouton avec loader | Non | Une requête est en cours ; éviter les doubles clics. | `Changement en cours…` |
| `ERROR` | Retour à l’état précédent + erreur | Variable | Échec technique, sans préjuger du droit fonctionnel. | `Le changement n’a pas pu être appliqué` |

### 5. États de session recommandés pour la bascule

La matrice suivante traduit la doctrine en une logique produit montrable, sans prétendre décrire un état déjà implémenté dans le réel audité.[1][3]

| Moment de séance | Bloc visible ? | Mode actuel visible ? | Bascule autorisée ? | Comportement recommandé |
|---|---|---|---|---|
| Ouverture / très début de séance | Oui | Oui | Oui | L’apprenant peut choisir ou réorienter le mode de travail.[2][1] |
| Début encore exploratoire, peu de messages | Oui | Oui | Oui ou semi-oui | Autorisation possible si la progression ne rend pas la bascule incohérente.[1] |
| Séance installée, branche prioritaire claire | Oui | Oui | Plutôt non | Afficher le mode actuel et verrouiller la bascule avec explication simple.[1][2] |
| Séance avancée proche synthèse / évaluation | Oui | Oui | Non | La cohérence du fil et les CTA terminales priment.[1][5] |
| Évaluation terminale ouverte | Oui ou lecture seule | Oui | Non | Ne pas autoriser un retour ad hoc qui brouillerait la lecture produit de la fin de parcours.[1] |

### 6. Motifs de verrouillage recommandés

La doctrine évoque un refus lorsque la séance est “trop avancée” et une sélection explicite surtout en début de séance ; la spec interface parle de blocage après un certain nombre de messages ou de phase.[1][2] À partir de là, la couche produit peut stabiliser les motifs montrables suivants :

| Code produit recommandé | Cause métier simplifiée | Message UI court | Message UI développé |
|---|---|---|---|
| `SESSION_TOO_ADVANCED` | La séance a déjà trop progressé | `Le mode ne peut plus être changé maintenant.` | `Le fil est déjà trop avancé pour changer de mode sans casser la progression en cours.` |
| `BRANCH_TOO_MATURE` | Une branche prioritaire est déjà suffisamment structurée | `Le travail en cours est déjà bien engagé.` | `Le travail actuel est assez avancé ; il vaut mieux aller au bout avant de repartir sur un autre mode.` |
| `TERMINAL_ACTION_NEAR` | Une synthèse ou une évaluation est proche / ouverte | `La séance est déjà en phase de conclusion.` | `Le changement de mode n’est plus proposé car la séance est déjà proche d’une synthèse ou d’une évaluation.` |
| `SERVER_POLICY_BLOCK` | Politique runtime / configuration qui ne permet pas la bascule | `Ce changement n’est pas disponible ici.` | `Ce mode n’est pas disponible dans le contexte actuel de cette séance.` |
| `REQUEST_FAILED` | Erreur technique | `Le changement n’a pas abouti.` | `Le changement n’a pas pu être appliqué. L’échange reste dans son mode actuel.` |

Ces codes sont proposés comme **codes produit de surface**, non comme reason codes moteur bruts à exposer tels quels.[1][2]

### 7. Scénarios de rendu du composant

#### Cas A — ouverture de séance, bascule pleinement disponible

- Titre : `Mode de travail`
- Sous-ligne : `Choisissez la manière dont Hugo vous accompagne au début de cet échange.`
- Boutons visibles : `Réfléchir à une situation`, `Analyser un problème`, `Réviser une notion`
- État courant : un seul bouton en état `ACTIVE_CURRENT`, les deux autres en `AVAILABLE`.[2][1]

#### Cas B — séance engagée, mode visible mais non modifiable

- Titre : `Mode de travail`
- Sous-ligne : `Analyser un problème`
- Boutons visibles : le mode courant en `ACTIVE_CURRENT`, les autres en `LOCKED`
- Aide inline : `Le mode ne peut plus être changé maintenant, car la séance est déjà bien engagée.`[2][1]

#### Cas C — demande de bascule refusée par le serveur

- Pendant la requête : bouton cible en `PENDING`, autres neutralisés.
- Après refus : retour à l’état précédent + bannière ou helper inline de niveau warning.
- Message recommandé : `Le mode n’a pas été modifié. Le fil est déjà trop avancé pour changer de mode maintenant.`[1]

#### Cas D — produit minimaliste sans bascule exposée

- Le bloc ne montre qu’un label type `Mode actuel : Réfléchir à une situation`.
- Aucun bouton de bascule n’est visible.
- Ce cas reste conforme à la canonique, puisque l’exposition des transitions n’est pas obligatoire tant qu’elle reste pilotée par `UIState` et non par le front seul.[1]

### 8. Contrat d’état UI recommandé

Sans figer prématurément un JSON exhaustif, la base 2.0 et son complément demandent un contrat d’état suffisamment stable pour les objets montrables.[4][1] Pour la zone de bascule, une projection produit cohérente pourrait prendre la forme logique suivante :

```json
{
  "conversation_mode": {
    "visible": true,
    "current": "DIAGNOSTIC",
    "display_label": "Analyser un problème",
    "switch_state": "VISIBLE_LOCKED",
    "helper_text": "Le mode ne peut plus être changé maintenant.",
    "options": [
      {
        "key": "REFLEXIVE",
        "label": "Réfléchir à une situation",
        "button_state": "LOCKED"
      },
      {
        "key": "DIAGNOSTIC",
        "label": "Analyser un problème",
        "button_state": "ACTIVE_CURRENT"
      },
      {
        "key": "REVISION",
        "label": "Réviser une notion",
        "button_state": "LOCKED"
      }
    ]
  }
}
```

Ce pseudo-contrat respecte trois invariants : exposition d’un objet produit montrable, absence de champs P0 bruts, et possibilité de piloter toute la lisibilité front depuis le backend.[1][4]

### 9. Contrat d’action recommandé

L’action de bascule ne doit pas être décrite comme “le front change le mode”, mais comme “le front demande une autre posture et le backend applique ou refuse”.[1][4]

| Étape | Action client | Attendu serveur | Effet UI |
|---|---|---|---|
| 1 | Clic sur un bouton `AVAILABLE` | Reçoit la demande de posture cible.[1] | Passage local en `PENDING`. |
| 2 | Envoi de `PATCH sessions/{id}/posture` ou équivalent cible | Vérifie phase, progression, contraintes de session.[1][3] | Aucun changement définitif avant retour serveur. |
| 3a | Réponse appliquée | Retourne posture active appliquée + état dérivé mis à jour.[1] | Nouveau bouton `ACTIVE_CURRENT`, helper de confirmation discret. |
| 3b | Réponse refusée | Retourne refus motivé.[1] | Retour à l’état antérieur + message de refus. |
| 3c | Échec technique | Timeout / erreur réseau | Message d’erreur technique, sans modifier le mode courant. |

### 10. Règles de copywriting UI recommandées

La grammaire visible côté apprenant doit rester non technique et ne pas faire émerger les catégories internes du moteur.[1][2] Les formulations suivantes sont recommandées :

| Situation | Formulation recommandée | Formulation à éviter |
|---|---|---|
| Affichage du mode courant | `Mode actuel : Analyser un problème` | `Posture active : DIAGNOSTIC` |
| Bascule disponible | `Vous pouvez changer de mode pour démarrer autrement.` | `Posture switch allowed` |
| Bascule verrouillée | `Le mode ne peut plus être changé maintenant.` | `Transition refused by policy` |
| Refus motivé | `Le fil est déjà trop avancé pour changer de mode.` | `Reason code: SESSION_TOO_ADVANCED` |
| Succès discret | `Mode mis à jour.` | `ConversationPosture successfully patched` |

### 11. Positionnement dans le workspace

Au regard du front 1.8 audité, deux emplacements sont cohérents :

- **dans le panneau de progression** si l’on veut traiter le mode comme une dimension de lecture d’état au même titre que la scène, la quête active et la maturité ;[5][6]
- **dans l’en-tête du workspace conversationnel** si l’on veut rendre l’action plus immédiatement disponible en ouverture de séance, tout en évitant qu’elle ressemble à une barre de pilotage continue.[2][1]

L’option la plus sûre doctrinalement est un composant **proche du panneau de progression**, car il inscrit la bascule dans la logique `UIState` et non dans une logique de pilotage flottant permanent.[1][5]

### 12. États d’accessibilité et d’ergonomie

Une spec détaillée doit aussi fixer les comportements d’accessibilité, même si le corpus 2.0 ne les énumère pas explicitement pour ce composant spécifique.[1][2]

| Sujet | Règle recommandée |
|---|---|
| Focus clavier | Chaque bouton visible doit être tabulable sauf état `LOCKED` réellement inactif. |
| Lecture écran | Le bouton actif doit annoncer `mode actuel` et les boutons verrouillés doivent annoncer `indisponible`. |
| Pending | Ajouter un feedback de chargement visible et non seulement coloriel. |
| Refus | Le message de refus doit être lu par les technologies d’assistance via zone live ou bannière accessible. |
| Couleur | Ne jamais coder l’état uniquement par la couleur ; ajouter texte, icône ou libellé d’état. |

### 13. Cas à ne pas maqueter comme tels

Plusieurs anti-patterns doivent être évités car ils contredisent la doctrine 2.0 :

- une barre de modes toujours disponible laissant croire que l’apprenant pilote librement le moteur à tout moment ;[1]
- un sélecteur qui expose les noms internes `ConversationPosture`, `reasonCodes`, `P0`, `DecisionContract` ou des variables de debug ;[1][2]
- un traitement de l’évaluation comme quatrième onglet symétrique des autres régimes ;[1]
- un changement de mode purement local côté front, sans revalidation serveur ;[1][4]
- une UX qui ferait croire qu’un simple clic de mode change la vérité comportementale hors progression de séance.[1]

## Proposition de matrice finale d’implémentation

La table suivante peut servir de base de spec produit + contrat CTO pour la V1 de cette zone.[1][2][3]

| ID | Précondition produit | Rendu | Action utilisateur | Réponse attendue | Notes |
|---|---|---|---|---|---|
| `SW-01` | Produit n’expose pas la bascule | Bloc caché | Aucune | Aucune | Cas conforme à la canonique. |
| `SW-02` | Produit expose seulement le mode courant | Bloc lecture seule | Aucune | Aucune | Variante simple et sûre. |
| `SW-03` | Ouverture de séance, changement autorisé | 3 boutons visibles, un actif, 2 disponibles | Clic sur un bouton disponible | Passage pending puis application | Cas nominal de bascule. |
| `SW-04` | Début de séance mais régime cible déconseillé | Bouton visible avec warning léger | Clic puis confirmation | Application ou refus | Option produit, pas encore explicitement figée doctrinalement. |
| `SW-05` | Séance avancée | Boutons alternatifs verrouillés | Aucun clic effectif | Aucune requête ou refus immédiat piloté serveur | Préférer motif simple et lisible. |
| `SW-06` | Requête envoyée | Bouton cible en loader | Attente | Application ou refus | Interdire le double submit. |
| `SW-07` | Refus métier serveur | Retour à l’état initial + message | Lecture du message | Aucun changement du mode actuel | Refus motivé obligatoire côté produit. |
| `SW-08` | Erreur technique | Retour à l’état initial + erreur technique | Relecture / retry éventuel | Aucun changement du mode actuel | Ne jamais afficher un faux succès. |
| `SW-09` | Session proche synthèse / évaluation | Bascule verrouillée, CTA terminales visibles | Pas de changement | Le fil continue vers la fin de parcours | Cohérence avec la progression. |
| `SW-10` | Évaluation ouverte | Contrôle lecture seule ou masqué | Pas de changement | Stabilité de la branche terminale | Ne pas mélanger régime permanent et branche terminale. |

## Recommandations de chantier

Pour fermer proprement cette zone documentaire, il faut produire quatre artefacts cohérents :

1. une **annexe de spec interface 2.0** dédiée au composant de bascule ;[2]
2. un **quasi-contrat `UIState`** pour la zone `conversation_mode` ou équivalent ;[4][1]
3. une **matrice backend/front de refus motivés** séparant reason codes internes et messages produits montrables ;[1][2]
4. une **vérification code/runtime** pour confirmer ou infirmer l’existence réelle de l’endpoint et d’un début de composant dans le front 1.8 ou dans la branche cible.[3][5]

## Conclusion opérationnelle

La documentation existante couvre déjà correctement le **principe** de la bascule de posture côté apprenant, mais pas encore sa **traduction produit détaillée**.[1][2] Le chantier pertinent n’est donc pas de réinventer la doctrine, mais de stabiliser un **contrat UI backend-first** avec états, messages, emplacements et refus, en restant strictement compatible avec les invariants Hugo cœur : backend Django orchestré, TutorPrompt pivot runtime, P0 conservé, front dérivé d’états et absence totale de pilotage conversationnel front-driven.[1][4]

# Hugo — Décisions documentaires
## Front apprenant — bascule entre régimes conversationnels

## 1. Objet

Ce document fixe les **décisions documentaires** à retenir pour la zone *front apprenant — bascule entre régimes conversationnels*. Il accompagne le document de matrice de bascule et de matrice maquettée détaillée, et a pour fonction de stabiliser le cadre de rédaction, le niveau de vérité, le vocabulaire, la portée et les arbitrages de structuration à conserver dans la documentation Hugo.

Il ne décrit pas une implémentation livrée. Il sert à garantir que les prochains documents, prompts Cursor, analyses d’écart et travaux CTO parlent de cette zone de manière homogène, sans confusion entre doctrine cible, réel audité et contrat produit recommandé.

## 2. Position du document

### Décision 1 — Nature du document

Le document sur la bascule entre régimes conversationnels côté apprenant est classé comme **document transversal de spécification produit**.

Il n’est :

- ni une nouvelle spec canonique autonome ;
- ni un audit du réel ;
- ni une simple note de design UI ;
- ni une preuve d’implémentation.

### Décision 2 — Rattachement documentaire

Ce document est rattaché en priorité à la zone **spec interface 2.0**, tout en restant explicitement articulé avec :

- la spec canonique 2.0 ;
- le complément unique 2.0 ;
- le glossaire d’alignement réel vs cible ;
- les audits du réel sur le front apprenant.

### Décision 3 — Fonction du document

Sa fonction officielle est celle d’un **addendum ciblé “front apprenant — bascule de régime conversationnel”**.

Il doit servir à :

- combler une sous-spécification côté interface ;
- produire un vocabulaire propre et stable ;
- préparer un futur contrat `UIState` de la zone ;
- préparer les vérifications code/runtime correspondantes.

## 3. Niveaux de vérité

### Décision 4 — Triple niveau obligatoire

Tout document sur cette zone doit distinguer explicitement trois niveaux de vérité :

1. **cible 2.0 consolidée** ;
2. **réel audité observable** ;
3. **contrat produit recommandé V1**.

### Décision 5 — Interdiction de relecture abusive

Le document ne doit jamais relire un élément cible comme une fonctionnalité déjà livrée.

Les formulations à retenir sont :

- `la cible prévoit` ;
- `la doctrine fixe` ;
- `le réel audité confirme` ;
- `le réel audité ne confirme pas` ;
- `la V1 recommandée propose`.

Les formulations à éviter sont :

- `le bouton existe déjà` ;
- `l’endpoint est là` ;
- `la feature est livrée` ;
- `le front gère déjà la bascule`, tant qu’aucune preuve auditable solide ne l’établit.

### Décision 6 — Hiérarchie de référence

Pour cette zone, la hiérarchie documentaire à respecter est la suivante :

1. spec canonique 2.0 pour la doctrine et les invariants ;
2. complément unique 2.0 pour les consolidations et garde-fous ;
3. spec interface 2.0 pour la traduction produit cible ;
4. glossaire d’alignement pour les ponts de vocabulaire ;
5. audits du réel pour ce qui peut être dit comme observable ;
6. document de décisions documentaires et document de matrice comme outils d’alignement et de travail.

## 4. Vocabulaire verrouillé

### Décision 7 — Vocabulaire doctrinal

Le document retient :

- **régime conversationnel** pour la doctrine de haut niveau ;
- **posture active** pour la valeur runtime ;
- **geste tutoral** pour la conduite locale interne.

### Décision 8 — Vocabulaire produit visible

Le document retient côté apprenant :

- **Mode de travail** comme libellé principal de composant ;
- **Mode actuel** comme libellé de lecture de l’état courant.

### Décision 9 — Vocabulaire explicitement écarté du front

Les termes suivants ne doivent pas être utilisés comme libellés visibles côté apprenant :

- `P0` ;
- `DecisionContract` ;
- `ConversationPosture` ;
- `reasonCodes` ;
- tout autre nom technique backend ou debug.

### Décision 10 — Distinctions à maintenir

Le document impose de séparer explicitement :

- le **régime conversationnel** ;
- la **posture active runtime** ;
- le **mode de travail montré à l’apprenant** ;
- les **gestes tutoraux locaux** ;
- les **actions terminales** comme synthèse et évaluation.

## 5. Portée fonctionnelle

### Décision 11 — Ce que le document couvre

Le document de bascule couvre exclusivement :

- l’affichage du mode actuel ;
- la demande de bascule par l’apprenant ;
- les états UI du bloc et des boutons ;
- les messages de disponibilité, verrouillage, succès et refus ;
- l’articulation avec la progression de séance ;
- l’articulation avec synthèse et évaluation.

### Décision 12 — Ce que le document ne couvre pas

Le document n’a pas vocation à couvrir :

- la logique algorithmique détaillée du `PostureSelector` ;
- les reason codes bruts du moteur ;
- le détail de la sélection de posture côté backend ;
- la maquette complète du workspace apprenant ;
- le workflow tuteur ou formateur ;
- les gestes tutoraux internes ;
- la preuve de livraison réelle.

## 6. Décisions de doctrine produit

### Décision 13 — Backend source de vérité

La bascule de régime doit toujours être décrite comme une **demande utilisateur bornée**, traitée côté backend.

Le front :

- demande ;
- attend ;
- affiche ;
- rafraîchit.

Le backend :

- autorise ;
- refuse ;
- applique ;
- recalcule l’état produit.

### Décision 14 — UIState comme ancrage

Le point d’ancrage documentaire principal pour cette zone est `UIState` ou sa future projection équivalente.

Le document ne doit jamais faire reposer la spécification front sur des champs P0 bruts, des structures de décision internes ou des objets de debug.

### Décision 15 — Une seule posture globale visible

La documentation doit toujours rappeler qu’une seule posture globale est active par tour.

Le composant de bascule ne doit donc jamais être décrit comme un système multi-sélection, ni comme une couche de mixage de modes.

### Décision 16 — Évaluation hors symétrie des modes

L’évaluation reste une **branche terminale** et non un quatrième mode permanent équivalent aux trois régimes principaux.

Elle demeure documentée avec les CTA terminales et non dans le cœur du composant de bascule.

### Décision 17 — Front non pilotant

Le document doit explicitement interdire toute interprétation front-driven :

- pas de changement de régime purement local ;
- pas de sélection souveraine de conduite par le front ;
- pas de logique de vérité comportementale déplacée dans l’UI.

## 7. Décisions de structuration du document principal

### Décision 18 — Structure type à conserver

Le document principal sur la bascule doit suivre, sauf raison forte contraire, la structure suivante :

1. statut du document ;
2. règle de lecture ;
3. vocabulaire retenu ;
4. portée du document ;
5. constat consolidé ;
6. matrice de bascule documentaire et produit ;
7. décisions documentaires ;
8. principes de conception retenus ;
9. matrice maquettée détaillée ;
10. contrat d’état UI recommandé ;
11. contrat d’action recommandé ;
12. règles de copywriting UI ;
13. accessibilité et ergonomie ;
14. anti-patterns ;
15. matrice finale d’implémentation ;
16. points à vérifier côté code et runtime ;
17. sorties attendues.

### Décision 19 — Niveau de granularité attendu

Le document principal doit être rédigé à un niveau **quasi-maquetté** pour les états UI, mais sans prétendre fournir une maquette graphique pixel-perfect.

Il doit être assez détaillé pour qu’un CTO, un product designer ou un développeur front puisse :

- comprendre les états ;
- comprendre les transitions ;
- comprendre les interdits ;
- préparer un chantier d’implémentation.

### Décision 20 — Style rédactionnel

Le style doit rester :

- précis ;
- non jargonnant côté produit ;
- ferme sur les invariants ;
- explicite sur ce qui est ouvert ou non confirmé.

## 8. Décisions de modélisation UI

### Décision 21 — Nom du composant

Le composant est documenté comme bloc **Mode de travail**.

### Décision 22 — Positionnement produit recommandé

Le positionnement recommandé est **proche du panneau de progression** ou dans une zone de lecture d’état du workspace, et non comme barre flottante de pilotage continu.

### Décision 23 — Typologie d’états à documenter

Le document principal doit obligatoirement décrire :

- les états de haut niveau du bloc ;
- les états détaillés des boutons ;
- les motifs de verrouillage ;
- les cas de succès ;
- les cas de refus ;
- les cas d’erreur technique.

### Décision 24 — Codes produit de surface

Le document peut définir des **codes produit de surface** pour stabiliser la logique documentaire et l’implémentation future.

Ces codes sont acceptés pour :

- les états du bloc ;
- les états des boutons ;
- les motifs de verrouillage.

Mais ils ne doivent jamais être confondus avec des reason codes moteur bruts.

### Décision 25 — Cas minimaliste admis

Le document doit reconnaître comme valide une variante produit minimaliste où seule l’information `mode actuel` est visible, sans sélecteur de bascule exposé.

Cette variante reste doctrinalement acceptable tant que le produit reste piloté par état et n’expose pas de logique moteur brute.

## 9. Décisions de copywriting

### Décision 26 — Lisibilité apprenant

Le copywriting du composant doit être formulé dans une langue compréhensible pour l’apprenant, sans termes runtime ou backend.

### Décision 27 — Refus simples, non techniques

Les messages de refus ou de verrouillage doivent expliquer la situation sans exposer la mécanique interne.

Exemples de formes acceptables :

- `Le mode ne peut plus être changé maintenant.`
- `Le travail en cours est déjà bien engagé.`
- `La séance est déjà en phase de conclusion.`

### Décision 28 — Interdiction des messages techniques

Les formulations techniques de type :

- `policy refused` ;
- `reason code` ;
- `posture patch failed` ;
- `mode transition denied by runtime`

sont interdites dans la surface apprenant.

## 10. Décisions d’audit et de chantier

### Décision 29 — Vérifications à prévoir

Tout usage du document doit être suivi d’une vérification sur cinq points :

1. existence réelle ou non de l’endpoint de changement de posture ;
2. existence réelle ou non d’un début de composant dans le front ;
3. modalités actuelles de projection de la posture dans l’état produit ;
4. possibilité réelle de dériver un verrouillage à partir de la progression existante ;
5. écarts exacts entre contrat cible et code observable.

### Décision 30 — Usage CTO / Cursor

Le document est autorisé comme base de travail pour :

- un prompt Cursor d’audit ;
- un prompt Cursor de respecification ;
- un prompt Cursor de création ou modification de composant ;
- une checklist d’implémentation backend/front.

### Décision 31 — Usage interdit

Le document ne doit pas être utilisé seul pour affirmer qu’une feature est déjà en production ou livrée dans Hugo cœur.

## 11. Sorties documentaires attendues

### Décision 32 — Livrables dérivés attendus

Ce document doit déboucher sur trois livrables :

1. une annexe ciblée à `specs interface 2.0` ;
2. un quasi-contrat `UIState` pour la zone `conversation_mode` ou équivalent ;
3. une checklist d’écarts cible / réel sur cette zone.

### Décision 33 — Compatibilité avec le futur chantier

Le document doit rester assez stable pour servir de référence lors du chantier 1.9 / 2.0, tout en restant révisable si une relecture du code ou du runtime révèle un écart important.

## 12. Formule de clôture

La décision de fond est la suivante : le sujet **“bascule de régime conversationnel côté apprenant”** dispose désormais d’un cadre documentaire autonome, mais subordonné à la doctrine 2.0 pour les invariants et au corpus d’audit pour la description du réel.

Autrement dit :

- la doctrine 2.0 fixe le **cadre** ;
- les audits fixent le **réel** ;
- le document de matrice fixe la **traduction produit recommandée** ;
- le présent document fixe les **règles de rédaction, de vérité et de structuration** à appliquer durablement sur cette zone.
EOF && ls -l output/decisions_documentaires_bascule_front_apprenant.md


# Hugo — Backlog d’actions
## Front apprenant — bascule entre régimes conversationnels

## 1. Objet

Ce document transforme le travail déjà produit sur la bascule entre régimes conversationnels côté apprenant en **backlog d’actions opérationnel**. Il est conçu pour servir de pont entre produit, audit, spécification et implémentation.

Le backlog est volontairement organisé pour distinguer :

- les actions de **clarification documentaire** ;
- les actions de **vérification du réel** ;
- les actions de **spécification produit** ;
- les actions de **préparation backend / front** ;
- les actions de **sécurisation de non-régression**.

Il ne suppose pas que la fonctionnalité soit déjà livrée. Il part d’un constat simple : la doctrine 2.0 cadre bien la bascule, mais la couverture front apprenant détaillée reste incomplète et doit être fermée proprement.

## 2. Principes d’usage du backlog

### Règle 1 — Toujours distinguer cible, réel et V1 produit

Chaque action doit expliciter si elle vise :

- à confirmer le **réel observé** ;
- à stabiliser la **cible produit** ;
- à préparer une **V1 d’implémentation**.

### Règle 2 — Pas de spéculation sur le livré

Aucune action ne doit présupposer que :

- le sélecteur existe déjà côté front prod ;
- l’endpoint de bascule est confirmé côté backend ;
- la posture active est déjà projetée sous forme stable dans l’état produit affiché.

### Règle 3 — Backend-first

Toutes les actions de conception et d’implémentation doivent conserver l’invariant suivant :

- le backend reste source de vérité ;
- le front lit un état dérivé ;
- le front demande une bascule mais ne pilote pas la conduite.

## 3. Lecture des priorités

Le backlog utilise quatre niveaux de priorité :

- **P0** : nécessaire pour éviter un faux cadrage ou une mauvaise implémentation ;
- **P1** : nécessaire pour produire une V1 propre ;
- **P2** : utile pour durcir la qualité et la maintenabilité ;
- **P3** : amélioration ultérieure ou confort produit.

## 4. Backlog — Clarification documentaire

### BA-001 — Classer officiellement le document de matrice

- **Priorité** : P0
- **Type** : documentation
- **Objectif** : rattacher formellement le document de matrice comme addendum ciblé à la spec interface 2.0
- **Action** : ajouter une mention explicite dans l’index documentaire et dans la logique de lecture des specs
- **Livrable** : positionnement documentaire stabilisé
- **Critère de done** : le document est lisible comme annexe ciblée et non comme spec autonome concurrente

### BA-002 — Ajouter une règle de vérité explicite

- **Priorité** : P0
- **Type** : documentation
- **Objectif** : imposer la distinction cible / réel / V1 recommandée dans tous les textes sur cette zone
- **Action** : injecter cette règle dans le document principal et dans les prochains prompts Cursor
- **Livrable** : cadre de rédaction stabilisé
- **Critère de done** : chaque document produit sur cette zone reprend explicitement ces trois niveaux

### BA-003 — Stabiliser le vocabulaire de référence

- **Priorité** : P0
- **Type** : documentation
- **Objectif** : verrouiller les couples de termes doctrine / produit / runtime
- **Action** : fixer noir sur blanc `régime conversationnel`, `posture active`, `mode de travail`
- **Livrable** : mini glossaire local de la zone
- **Critère de done** : les nouveaux documents n’emploient plus ces termes de manière flottante

### BA-004 — Acter la place de l’évaluation

- **Priorité** : P0
- **Type** : documentation
- **Objectif** : empêcher la dérive qui ferait de l’évaluation un quatrième mode symétrique
- **Action** : inscrire explicitement dans les docs que l’évaluation reste une branche terminale séparée
- **Livrable** : arbitrage documentaire stabilisé
- **Critère de done** : aucune future maquette ou spec de cette zone ne met l’évaluation dans le groupe central de bascule

### BA-005 — Intégrer les décisions documentaires à la bibliothèque

- **Priorité** : P1
- **Type** : documentation
- **Objectif** : faire du document “décisions documentaires” une référence active et non un texte isolé
- **Action** : lier ce document dans les parcours de travail, les prompts et l’index de lecture
- **Livrable** : document de gouvernance documentaire opérationnel
- **Critère de done** : le document est cité comme règle de lecture dans les prochains travaux de cette zone

## 5. Backlog — Vérification du réel

### BA-006 — Vérifier l’existence réelle de l’endpoint de bascule

- **Priorité** : P0
- **Type** : audit code / runtime
- **Objectif** : confirmer ou infirmer l’existence effective d’un endpoint de changement de posture
- **Action** : auditer code backend, routes, serializers, vues et traces runtime
- **Livrable** : note d’audit courte “confirmé / absent / partiel / ambigu”
- **Critère de done** : statut clair du endpoint, avec nom réel observé si présent

### BA-007 — Vérifier l’existence réelle d’un composant front de bascule

- **Priorité** : P0
- **Type** : audit front
- **Objectif** : confirmer ou infirmer l’existence d’un composant ou d’un embryon de composant dans le front 1.8
- **Action** : relire composants du workspace apprenant, routes, panneaux de progression et états UI associés
- **Livrable** : note de constat front
- **Critère de done** : statut clair “absent / partiel / caché / prototype / branché”

### BA-008 — Vérifier la projection actuelle de la posture active

- **Priorité** : P0
- **Type** : audit backend/front
- **Objectif** : savoir si la posture active est déjà projetée ou projectable proprement dans l’état produit
- **Action** : relire `UIState`, builders, contracts, payloads consommés par le front
- **Livrable** : cartographie minimale des champs utiles
- **Critère de done** : compréhension claire de ce qui est déjà disponible, manquant ou instable

### BA-009 — Vérifier les signaux existants de verrouillage

- **Priorité** : P1
- **Type** : audit fonctionnel
- **Objectif** : identifier si le verrouillage de bascule peut être dérivé de signaux déjà présents (phase, maturité, progression, nombre de messages)
- **Action** : relire progression, `UIState`, services de décision et structures de session
- **Livrable** : note “signaux réutilisables pour V1”
- **Critère de done** : liste courte des signaux backend disponibles pour autoriser / refuser la bascule

### BA-010 — Vérifier les divergences entre local et runtime distant

- **Priorité** : P1
- **Type** : audit runtime
- **Objectif** : éviter une vérité double entre code local et environnement distant observable
- **Action** : comparer ce qui existe dans le code et ce qui est réellement exposé côté démo / Encoors si accessible
- **Livrable** : note d’écart local / distant
- **Critère de done** : les différences importantes sont documentées avant toute annonce produit

## 6. Backlog — Spécification produit

### BA-011 — Finaliser l’annexe ciblée à la spec interface 2.0

- **Priorité** : P0
- **Type** : spécification produit
- **Objectif** : transformer la matrice actuelle en annexe normative légère
- **Action** : produire une version plus serrée et plus normative du document principal
- **Livrable** : annexe “front apprenant — bascule de régime conversationnel”
- **Critère de done** : document relisible comme spec interface complémentaire

### BA-012 — Stabiliser la liste des états UI du bloc

- **Priorité** : P0
- **Type** : spécification produit
- **Objectif** : figer la liste canonique des états du bloc de bascule
- **Action** : valider les états `HIDDEN`, `VISIBLE_READONLY`, `VISIBLE_SWITCHABLE`, `VISIBLE_LOCKED`, `VISIBLE_PENDING`, `VISIBLE_REFUSED`, `VISIBLE_APPLIED`
- **Livrable** : mini-catalogue d’états produit
- **Critère de done** : la liste est stable et réutilisable dans front, backend et tests

### BA-013 — Stabiliser la liste des états de boutons

- **Priorité** : P0
- **Type** : spécification produit
- **Objectif** : figer la grammaire des boutons dans tous les cas visibles
- **Action** : valider `ACTIVE_CURRENT`, `AVAILABLE`, `DISCOURAGED`, `LOCKED`, `HIDDEN`, `PENDING`, `ERROR`
- **Livrable** : matrice canonique des états de boutons
- **Critère de done** : absence d’ambiguïté dans les futures implémentations

### BA-014 — Fixer la politique de visibilité minimale

- **Priorité** : P1
- **Type** : spécification produit
- **Objectif** : arbitrer si la V1 expose seulement le mode courant ou aussi la bascule complète
- **Action** : décider entre trois niveaux de surface : caché, lecture seule, bascule active
- **Livrable** : arbitrage produit V1
- **Critère de done** : une seule option retenue pour la première implémentation montrable

### BA-015 — Fixer les messages de verrouillage et refus

- **Priorité** : P1
- **Type** : copywriting produit
- **Objectif** : éviter des formulations techniques ou incohérentes
- **Action** : valider un jeu court de messages UI simples et non techniques
- **Livrable** : mini-catalogue de copywriting
- **Critère de done** : les messages de refus sont stables et validés

### BA-016 — Fixer l’emplacement du composant dans le workspace

- **Priorité** : P1
- **Type** : UX produit
- **Objectif** : éviter une bascule présentée comme outil de pilotage libre
- **Action** : arbitrer entre intégration au panneau de progression ou en-tête du workspace
- **Livrable** : emplacement produit décidé
- **Critère de done** : la spec front ne laisse plus cette zone flottante

### BA-017 — Décider du statut `DISCOURAGED`

- **Priorité** : P2
- **Type** : arbitrage produit
- **Objectif** : décider si la V1 inclut un état “possible mais déconseillé” ou reste binaire “possible / verrouillé”
- **Action** : trancher explicitement sur cette finesse UX
- **Livrable** : décision produit claire
- **Critère de done** : la matrice finale supprime l’ambiguïté sur ce point

## 7. Backlog — Contrat d’état et backend

### BA-018 — Produire le quasi-contrat `UIState` de la zone

- **Priorité** : P0
- **Type** : spécification backend / produit
- **Objectif** : formaliser une projection stable pour la zone `conversation_mode`
- **Action** : produire un pseudo-JSON canonique V1 avec champs obligatoires et champs optionnels
- **Livrable** : contrat d’état V1
- **Critère de done** : backend, front et tests parlent du même objet

### BA-019 — Définir les enums / constantes canoniques

- **Priorité** : P1
- **Type** : spécification technique
- **Objectif** : éviter la prolifération de chaînes libres et divergentes
- **Action** : lister les enums côté backend et les équivalents côté front
- **Livrable** : catalogue minimal des constantes
- **Critère de done** : toutes les valeurs d’état sont centralisées

### BA-020 — Définir la réponse serveur attendue en cas d’application

- **Priorité** : P1
- **Type** : contrat API
- **Objectif** : clarifier ce que le client reçoit après une bascule réussie
- **Action** : définir si la réponse renvoie la posture appliquée seule, ou la posture + projection produit mise à jour
- **Livrable** : règle de réponse API
- **Critère de done** : le front sait sans ambiguïté quoi rafraîchir

### BA-021 — Définir la réponse serveur attendue en cas de refus

- **Priorité** : P1
- **Type** : contrat API
- **Objectif** : formaliser le refus motivé sans exposer les reason codes bruts
- **Action** : définir le schéma produit de refus montrable
- **Livrable** : mini-contrat d’erreur métier
- **Critère de done** : le front peut afficher un message propre sans traductions improvisées

### BA-022 — Réutiliser les signaux existants plutôt que créer un pipeline parallèle

- **Priorité** : P0
- **Type** : architecture
- **Objectif** : respecter les invariants 2.0 et éviter une logique ad hoc
- **Action** : dériver autorisation et verrouillage à partir de la progression, de la posture et des signaux déjà disponibles autant que possible
- **Livrable** : proposition technique backend cohérente
- **Critère de done** : aucune architecture parallèle front-driven n’est introduite

## 8. Backlog — Implémentation front

### BA-023 — Lister les composants front touchés

- **Priorité** : P1
- **Type** : préparation implémentation
- **Objectif** : préparer un chantier propre côté front
- **Action** : identifier les composants, stores, hooks, routes et contrats impactés
- **Livrable** : cartographie front de modification
- **Critère de done** : le chantier front a un périmètre clair

### BA-024 — Créer ou modifier le composant “Mode de travail”

- **Priorité** : P1
- **Type** : implémentation front
- **Objectif** : rendre la zone visible dans le workspace selon l’arbitrage produit retenu
- **Action** : développer le composant et son rendu d’états
- **Livrable** : composant fonctionnel V1
- **Critère de done** : tous les états retenus sont rendables sans hack local

### BA-025 — Brancher le pending et le retour serveur

- **Priorité** : P1
- **Type** : implémentation front
- **Objectif** : garantir une UX fiable pendant la requête
- **Action** : ajouter gestion loader, disable temporaire, succès et refus
- **Livrable** : flux d’action complet
- **Critère de done** : aucune double requête ni faux succès visible

### BA-026 — Intégrer les messages produit validés

- **Priorité** : P1
- **Type** : implémentation front
- **Objectif** : éviter les textes “temporaires” ou techniques
- **Action** : brancher les messages validés dans le composant
- **Livrable** : copywriting V1 en place
- **Critère de done** : aucun texte debug ou placeholder n’apparaît à l’écran

### BA-027 — Gérer la variante lecture seule

- **Priorité** : P2
- **Type** : implémentation front
- **Objectif** : permettre un déploiement progressif ou un feature flag de surface minimale
- **Action** : prévoir un rendu `mode actuel` sans boutons actifs
- **Livrable** : fallback produit minimaliste
- **Critère de done** : le composant reste utile même sans bascule active

## 9. Backlog — Tests et non-régression

### BA-028 — Produire une matrice de tests d’états UI

- **Priorité** : P0
- **Type** : qualité
- **Objectif** : garantir que chaque état documenté est réellement testable
- **Action** : dériver des cas de test à partir de la matrice produit
- **Livrable** : tableau de cas de test
- **Critère de done** : chaque état du bloc et des boutons a au moins un cas de validation

### BA-029 — Tester la cohérence avec synthèse / évaluation

- **Priorité** : P1
- **Type** : qualité fonctionnelle
- **Objectif** : vérifier que la bascule ne brouille pas la logique des CTA terminales
- **Action** : construire des scénarios de séance proche synthèse / proche évaluation
- **Livrable** : jeux de tests fonctionnels ciblés
- **Critère de done** : pas de contradiction visible entre bascule et CTA terminales

### BA-030 — Tester les refus et erreurs techniques

- **Priorité** : P1
- **Type** : qualité
- **Objectif** : sécuriser les cas les plus fragiles
- **Action** : tester refus métier, timeout, erreur réseau et retour à l’état précédent
- **Livrable** : cas de test négatifs
- **Critère de done** : le composant garde un état cohérent dans tous les cas de refus/erreur

### BA-031 — Vérifier l’accessibilité du composant

- **Priorité** : P2
- **Type** : qualité UX
- **Objectif** : éviter un composant lisible uniquement visuellement
- **Action** : tester tabulation, focus, annonces, pending et messages accessibles
- **Livrable** : checklist accessibilité
- **Critère de done** : le composant respecte les règles minimales fixées dans la spec

## 10. Backlog — Gouvernance et intégration documentaire

### BA-032 — Ajouter le sujet dans la cartographie d’écarts cible / réel

- **Priorité** : P1
- **Type** : gouvernance documentaire
- **Objectif** : faire de cette zone un écart qualifié, et non un flou persistant
- **Action** : créer une entrée spécifique dans la future matrice d’écarts
- **Livrable** : écart documenté et traçable
- **Critère de done** : le sujet apparaît comme zone autonome dans les travaux d’écart

### BA-033 — Préparer un prompt Cursor d’audit ciblé

- **Priorité** : P1
- **Type** : préparation opérationnelle
- **Objectif** : vérifier rapidement code et contrats réels
- **Action** : produire un prompt Cursor orienté endpoint, `UIState`, composants front et signaux de verrouillage
- **Livrable** : prompt prêt à l’emploi
- **Critère de done** : le prompt permet un audit ciblé sans ambiguïté de vocabulaire

### BA-034 — Préparer un prompt Cursor d’implémentation ciblé

- **Priorité** : P2
- **Type** : préparation opérationnelle
- **Objectif** : enchaîner après audit si la feature doit être construite
- **Action** : produire un prompt Cursor structuré pour backend + front + tests + doc
- **Livrable** : prompt d’implémentation
- **Critère de done** : le prompt suit les invariants Hugo et la matrice d’états stabilisée

## 11. Ordonnancement recommandé

### Phase A — Sécuriser la vérité

À lancer en premier :

- BA-001
- BA-002
- BA-003
- BA-004
- BA-006
- BA-007
- BA-008

**Objectif de phase** : savoir exactement de quoi on parle, sans confusion entre cible et réel.

### Phase B — Fermer la spécification produit

À lancer ensuite :

- BA-011
- BA-012
- BA-013
- BA-014
- BA-015
- BA-016
- BA-018
- BA-021

**Objectif de phase** : disposer d’une V1 produit et d’un quasi-contrat d’état suffisamment fermes.

### Phase C — Préparer et lancer l’implémentation

À lancer après arbitrage :

- BA-019
- BA-020
- BA-022
- BA-023
- BA-024
- BA-025
- BA-026
- BA-028
- BA-029
- BA-030

**Objectif de phase** : transformer la spec en chantier exécutable.

### Phase D — Durcir et gouverner

À lancer ensuite :

- BA-005
- BA-009
- BA-010
- BA-017
- BA-027
- BA-031
- BA-032
- BA-033
- BA-034

**Objectif de phase** : améliorer la robustesse, la gouvernance documentaire et la réutilisabilité opérationnelle.

## 12. Version backlog synthétique

| ID | Priorité | Domaine | Action courte |
|---|---|---|---|
| BA-001 | P0 | Doc | Classer officiellement le document de matrice |
| BA-002 | P0 | Doc | Imposer la règle cible / réel / V1 |
| BA-003 | P0 | Doc | Stabiliser le vocabulaire |
| BA-004 | P0 | Doc | Acter que l’évaluation n’est pas un mode symétrique |
| BA-005 | P1 | Doc | Intégrer les décisions documentaires à la bibliothèque |
| BA-006 | P0 | Audit | Vérifier l’endpoint de bascule |
| BA-007 | P0 | Audit | Vérifier le composant front réel |
| BA-008 | P0 | Audit | Vérifier la projection actuelle de posture |
| BA-009 | P1 | Audit | Vérifier les signaux existants de verrouillage |
| BA-010 | P1 | Audit | Vérifier les divergences local / distant |
| BA-011 | P0 | Spec | Finaliser l’annexe ciblée à la spec interface |
| BA-012 | P0 | Spec | Stabiliser les états du bloc |
| BA-013 | P0 | Spec | Stabiliser les états des boutons |
| BA-014 | P1 | Spec | Fixer le niveau de visibilité V1 |
| BA-015 | P1 | Spec | Fixer les messages de verrouillage / refus |
| BA-016 | P1 | Spec | Fixer l’emplacement du composant |
| BA-017 | P2 | Spec | Décider du statut `DISCOURAGED` |
| BA-018 | P0 | API / État | Produire le quasi-contrat `UIState` |
| BA-019 | P1 | Tech | Définir les enums / constantes |
| BA-020 | P1 | API | Définir la réponse serveur en succès |
| BA-021 | P1 | API | Définir la réponse serveur en refus |
| BA-022 | P0 | Archi | Réutiliser les signaux existants |
| BA-023 | P1 | Front | Lister les composants touchés |
| BA-024 | P1 | Front | Créer ou modifier le composant |
| BA-025 | P1 | Front | Brancher pending et retour serveur |
| BA-026 | P1 | Front | Intégrer les messages validés |
| BA-027 | P2 | Front | Gérer la variante lecture seule |
| BA-028 | P0 | Test | Produire la matrice de tests d’états |
| BA-029 | P1 | Test | Tester la cohérence avec synthèse / évaluation |
| BA-030 | P1 | Test | Tester refus et erreurs techniques |
| BA-031 | P2 | Test | Vérifier l’accessibilité |
| BA-032 | P1 | Gouvernance | Ajouter le sujet à la cartographie d’écarts |
| BA-033 | P1 | Ops | Préparer un prompt Cursor d’audit |
| BA-034 | P2 | Ops | Préparer un prompt Cursor d’implémentation |

## 13. Décision d’ensemble

La logique de ce backlog est simple :

1. **sécuriser ce qui est vrai** ;
2. **fermer ce qui manque dans la spec** ;
3. **préparer un contrat d’état et d’action propre** ;
4. **implémenter sans contourner les invariants Hugo** ;
5. **tester et documenter l’écart réel / cible**.

Le backlog doit donc être lu non comme une liste de tickets isolés, mais comme une séquence de fermeture propre d’une zone aujourd’hui bien cadrée doctrinalement, mais encore incomplète sur son versant front apprenant.

---

## 14. Mise à jour cluster 12 — plan UX apprenant & postures

**Sources :** `cluster12_ux_apprenant_postures_plan_resultats.md` · audit code `frontend_1.8` (2026-06-18).

| Point | Statut cluster 12 |
|---|---|
| UIState backend-first apprenant | **ALIGNE** — inchangé |
| `conversation_mode` affiché (lecture seule) | **ALIGNE** — `ConversationModeBanner.vue` |
| API `POST .../set-posture/` | **ALIGNE** backend — `test_posture_modes.py` |
| Sélecteur posture G2-02 front | **PARTIEL+ livré** — `PostureSelector.vue` + transitions C16 |
| 3 profils `learner_display_profile` | **PARTIEL+** — presets JS ; E2E U16-P1/P2 PASS |
| Bandeau scène / dispersion | **PARTIEL+ livré** — `LearnerSceneContextBar.vue` |
| CTA éval advisory | **IMPLÉMENTÉ** — `ui.advisory` + rendu front C16 |

**Prochaine sortie :** matrice SW-xx ; verrou posture par phase/tours ; scénarios manuels S16-A2/A3.

---
