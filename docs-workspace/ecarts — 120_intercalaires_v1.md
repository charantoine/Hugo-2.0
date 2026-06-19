# 00_rapport_ecarts — 120_intercalaires_v1

> **Mise à jour post-cluster 16 — 2026-06-18** · **Cluster 16 :** pas d'impact direct. Domaine **CIBLE** inchangé.

## Domaine

- `DOMAINE_CODE = 120_intercalaires_v1`
- `DOMAINE_LABEL = intercalaires pédagogiques V1`

---

## 1. Objet du rapport

Ce rapport qualifie, pour le seul domaine **intercalaires pédagogiques V1** de Hugo cœur, l’écart entre :

- la **cible 2.0** décrite par la documentation projet récente ;
- le **réel observable** documenté dans les audits Hugo réel ;
- le **pont de vocabulaire** fourni par le glossaire d’alignement.

Le rapport ne porte ni sur Hugo & Cie, ni sur une extension produit générale, ni sur une refonte du moteur conversationnel. Il vise uniquement à établir une lecture propre de ce domaine : ce qui relève d’une capacité cible cadrée, ce qui est effectivement observable dans Hugo cœur, et ce qui reste encore absent, ambigu ou à vérifier.

---

## 2. Règles de lecture appliquées sur ce domaine

### 2.1 Distinction des niveaux de vérité

Pour ce domaine, les documents sont lus selon quatre niveaux distincts :

- **cible** : ce que fixent la spec canonique Hugo 2.0, ses compléments et les documents projet récents ;
- **réel observable** : ce que décrivent les audits du workspace Hugo réel, en particulier `02_ETAT_MOTEUR_REEL.md`, `03_ETAT_PRODUIT_REEL.md`, `07_RUNTIME_DEMO_REFERENCE.md`, `09_PARCOURS_DEMO_ET_SCENARIOS.md` et `05_ECARTS_DOC_CODE_PRODUIT.md` ;
- **pont de vocabulaire** : ce que rapproche le `glossaire_alignement_hugo_reel_vs_spec.md` ;
- **à vérifier** : tout ce qui dépend d’un runtime distant, de flags, ou de variantes non auditées localement.

### 2.2 Garde-fous méthodologiques

Ce rapport applique les garde-fous suivants :

- la spec 2.0 décrit un **état cible**, jamais une preuve d’implémentation ;
- le glossaire d’alignement sert à **raccorder des noms**, pas à démontrer qu’un objet ou une feature existe réellement ;
- le réel ne doit jamais être déduit d’un seul document isolé ;
- l’absence d’un nom dans le glossaire ne suffit pas à prouver une absence code, mais l’absence d’observation croisée dans les audits et documents produit empêche d’affirmer la présence réelle ;
- toute dépendance au runtime distant ou à des flags non relus reste marquée `A_VERIFIER`.

---

## 3. Périmètre cible 2.0 du domaine

### 3.1 Nature des intercalaires V1

Dans la cible Hugo 2.0, les **intercalaires pédagogiques V1** sont une capacité **dérivée, additive et non souveraine**. Ils ne constituent ni un nouveau régime conversationnel, ni une seconde couche de pilotage tutoriel, ni un mini-LMS embarqué.

Ils doivent être compris comme une sortie secondaire, légère et contextualisée, produite à partir d’artefacts backend déjà structurés, pour aider l’apprenant ponctuellement sans concurrencer la conduite principale du moteur.

### 3.2 Place doctrinale dans l’architecture

La doctrine 2.0 impose plusieurs contraintes fortes sur ce domaine :

- les intercalaires arrivent **après le tour principal** ;
- ils sont idéalement préparés **après persistance**, via une tâche asynchrone ou équivalent ;
- ils n’influent pas en retour sur la décision tutorale principale ni sur le noyau P0 ;
- ils consomment des artefacts structurés du backend plutôt qu’un raisonnement autonome front ;
- ils restent compatibles avec une architecture **backend Django orchestrée**, avec **TutorPrompt** comme pivot runtime et un front consommant des états dérivés.

Autrement dit, l’intercalaire V1 est une **capacité dérivée de restitution**, pas une nouvelle couche de gouvernance du dialogue.

### 3.3 Périmètre fonctionnel minimal attendu

Le périmètre V1 est volontairement restreint :

- au plus **un intercalaire par tour** ;
- `NONE` doit rester fréquent ;
- les types minimaux attendus sont de l’ordre de `NONE`, `NOTION`, `CONTRAST` ;
- le composant doit être **visible côté apprenant uniquement** ;
- il doit rester **passif**, **non interactif**, **non évaluatif** ;
- il doit être **débrayable par flag**.

Cette cible ne décrit donc pas une couche pédagogique riche ou adaptive complète, mais un **complément pédagogique bref et borné**.

### 3.4 Contraintes produit et sécurité

Le domaine doit rester compatible avec les invariants Hugo cœur :

- pas d’exposition des états P0 bruts ;
- pas de pilotage front-driven ;
- pas d’accès supplémentaire à du verbatim non partagé ;
- pas d’architecture parallèle au backend existant ;
- pas de confusion avec un système d’évaluation autonome ou de remédiation lourde.

Les intercalaires sont donc une **surcouche de lisibilité ou d’éclairage**, jamais une nouvelle autorité produit ou pédagogique.

---

## 4. Photo du réel observable

### 4.1 Ce que montre le corpus d’audit du réel

À partir des audits du réel utilisés comme base de vérité — notamment `02_ETAT_MOTEUR_REEL.md`, `03_ETAT_PRODUIT_REEL.md`, `07_RUNTIME_DEMO_REFERENCE.md`, `09_PARCOURS_DEMO_ET_SCENARIOS.md` et `05_ECARTS_DOC_CODE_PRODUIT.md` — il n’existe pas, dans le corpus consulté ici, de preuve positive d’un sous-système **intercalaires V1** réellement implémenté et observable dans Hugo cœur.

Les audits du réel décrivent en détail :

- le pipeline moteur ;
- les objets de progression ;
- `UIState` ;
- la mémoire gouvernée ;
- les services de synthèse, d’évaluation et de qualité ;
- les surfaces front montrables ;
- les écarts doc / code / produit.

Mais ils ne documentent pas un composant ou un service d’intercalaires pédagogiques comme capacité active du runtime local observé.

### 4.2 Ce que montre le glossaire d’alignement

Le `glossaire_alignement_hugo_reel_vs_spec.md` est particulièrement clair sur ce domaine : il mentionne un objet doctrinal de type **`SessionInterstitial` ou équivalent** comme **objet dérivé cible**, mais précise qu’**aucun nom réel observé** n’a été identifié dans Hugo développé pour cette capacité.

Le glossaire recommande explicitement de **ne pas introduire cet objet comme objet du réel tant que le chantier n’est pas implémenté**. Cela confirme que, dans l’état actuel du corpus, le domaine intercalaires relève d’abord de la cible doctrinale et non du réel observé.

### 4.3 Ce que montre la couche produit observable

Les documents d’état produit et de démo, ainsi que les écarts doc / code / produit, décrivent des surfaces comme :

- `UIState` ;
- panneau de progression ;
- actions de synthèse / évaluation ;
- vues testeur ;
- surfaces tuteur / formateur ;
- consommation front de contrats backend dérivés.

En revanche, le corpus utilisé ici ne montre pas de composant apprenant explicitement identifié comme **intercalaire pédagogique V1**. Aucun bloc produit stabilisé de type “mini-cartouche pédagogique inter-tour” n’est décrit comme réellement livré dans les surfaces montrables auditées.

### 4.4 Ce qu’on peut en conclure sur le réel

Au niveau de vérité strictement admissible, le réel observable autorise seulement les constats suivants :

- Hugo cœur dispose déjà de plusieurs **artefacts backend structurés** qui pourraient servir de base à un intercalaire additif futur : `TurnState`, contrat de décision, `ConversationProgress`, `UIState`, mémoire gouvernée, sorties de synthèse et signaux qualité ;
- le front consomme déjà des **états dérivés backend**, ce qui est cohérent avec l’idée d’un futur intercalaire passif ;
- mais le corpus d’audit consulté ici **ne prouve pas** que la capacité “intercalaires V1” soit effectivement implémentée comme service, contrat ou composant actif du produit actuel.

---

## 5. Analyse narrative des écarts

### 5.1 Alignement doctrinal fort sur la manière de faire

Même si le domaine n’est pas observé comme livré, la doctrine 2.0 est déjà très alignée avec l’architecture réelle de Hugo cœur sur la **manière correcte de l’implémenter**.

Le réel montre en effet un backend Django orchestré, un moteur piloté par état, un front alimenté par `UIState`, une logique de progression calculée côté serveur et des enrichissements additifs déjà présents autour du pipeline principal. Sous cet angle, les intercalaires V1 sont bien pensés comme une **extension naturelle de Hugo cœur**, et non comme une rupture d’architecture.

### 5.2 Écart principal : capacité cible cadrée, mais non observée comme livrée

L’écart principal sur ce domaine est simple : **la cible existe doctrinalement, mais le réel observable ne montre pas encore la capacité comme implémentée**.

Autrement dit, on n’est pas face à une feature présente mais mal nommée ; on est face à un domaine dont la doctrine est déjà bornée, mais dont le corpus d’audit du réel ne fournit pas de preuve positive d’existence runtime ou produit.

Le bon statut narratif n’est donc ni “aligné”, ni “contradictoire”, mais plutôt : **capacité cible cadrée, non observée comme livrée à ce stade**.

### 5.3 Écart de vocabulaire : objet conceptuel sans nom réel raccordé

Le glossaire d’alignement mentionne le domaine via un objet doctrinal du type `SessionInterstitial`, tout en signalant qu’aucun nom réel observé n’est disponible dans le Hugo développé audité.

Cela crée un écart de vocabulaire typique :

- la doctrine possède déjà un nom conceptuel utile ;
- le réel n’offre pas encore de backing model, de service ou de composant observable permettant de raccorder ce nom à une implémentation.

Il faut donc éviter deux erreurs :
1. faire comme si `SessionInterstitial` était déjà un objet réel ;
2. supprimer le concept doctrinal au motif qu’il n’est pas encore observé dans le code audité.

### 5.4 Écart de formalisation technique : contrat encore à produire

Le domaine est cadré sur le plan doctrinal, mais plusieurs contrats restent à formaliser proprement avant un futur chantier :

- source backend exacte des artefacts d’entrée ;
- point précis de déclenchement post-tour ;
- forme minimale du contrat de sortie ;
- règles de sélection `NONE` / `NOTION` / `CONTRAST` ;
- drapeau de désactivation ;
- rattachement exact à `UIState` ou à une projection dérivée voisine ;
- stratégie de persistance ou de non-persistance.

Le réel existant fournit une base de travail, mais pas encore un contrat observable prêt à documenter comme implémenté.

### 5.5 Écart produit : absence de surface montrable identifiée

L’autre écart important est côté produit. Le corpus audité décrit plusieurs surfaces apprenant et testeur, mais pas de composant intercalaires V1 montré comme élément stabilisé de l’expérience apprenant.

Cela signifie que, même si le backend pouvait un jour produire un artefact d’intercalaire, il resterait encore à clarifier :

- son insertion dans l’expérience de lecture ;
- sa non-confusion avec les messages du moteur ;
- son statut passif ;
- son déclenchement rare ;
- sa cohérence avec la grammaire produit existante.

Sur ce point, le domaine reste donc clairement **cible** plutôt que **réel observé**.

---

## 6. Lecture de synthèse par niveau de vérité

### 6.1 Cible 2.0

Relèvent clairement de la **cible 2.0** pour ce domaine :

- des intercalaires pédagogiques V1 additifs ;
- préparés après le tour principal ;
- idéalement en asynchrone ;
- non interactifs ;
- non évaluatifs ;
- visibles côté apprenant seulement ;
- limités à un petit ensemble de types (`NONE`, `NOTION`, `CONTRAST`) ;
- sans effet de retour sur P0 ni sur la décision tutorale principale.

### 6.2 Réel observable

Relèvent du **réel observable** :

- un moteur backend déjà structuré autour d’artefacts compatibles avec un futur enrichissement additif ;
- un front déjà piloté par des états dérivés (`UIState`, progression, synthèse, évaluation) ;
- l’absence, dans le corpus audité ici, d’un service, contrat ou composant d’intercalaires pédagogiques V1 décrit comme réellement actif.

### 6.3 Pont de vocabulaire

Relève du **pont de vocabulaire** :

- l’existence d’un nom doctrinal de type `SessionInterstitial` ou équivalent dans le glossaire ;
- le rappel explicite qu’aucun nom réel observé n’est raccordé aujourd’hui à cet objet dans Hugo développé.

### 6.4 À vérifier

Doivent rester marqués `A_VERIFIER` :

- toute affirmation selon laquelle des intercalaires V1 seraient déjà actifs sur un runtime distant ;
- toute présence éventuelle derrière un flag non audité ;
- toute variante de démo non recoupée par les audits du réel ;
- toute hypothèse d’implémentation partielle non visible dans le corpus utilisé ici.

---

## 7. Garde-fous pour la suite

### 7.1 Ce qu’il ne faut pas faire

Pour ce domaine, il faut éviter les dérives suivantes :

- présenter les intercalaires V1 comme déjà livrés parce qu’ils sont bien décrits dans la cible ;
- traiter le glossaire comme preuve d’implémentation ;
- réinterpréter les états backend existants comme s’ils démontraient déjà la feature complète ;
- transformer l’intercalaire en couche de pilotage tutoriel supplémentaire ;
- faire porter au front une logique pédagogique autonome.

### 7.2 Ce qu’il faut privilégier

La bonne trajectoire documentaire et technique consiste à :

- conserver le concept cible, car il est cohérent avec Hugo 2.0 ;
- marquer explicitement son absence d’observation dans le réel audité ;
- préparer un futur contrat **additif** et **backend-first** ;
- raccorder ce futur contrat à des artefacts déjà existants (`ConversationProgress`, `UIState`, signaux structurés), sans dupliquer le moteur ni contourner le P0.

---

## 8. Conclusion opérationnelle du domaine

Le domaine `120_intercalaires_v1` est, à ce stade, un **domaine cible cadré mais non observé comme livré** dans Hugo cœur.

La doctrine 2.0 le borne de manière assez propre : capacité additive, passive, rare, apprenant-only, sans effet retour sur la conduite tutorale. Le réel observable, quant à lui, montre une architecture compatible avec ce type d’enrichissement, mais ne fournit pas de preuve positive d’un service, d’un contrat ou d’un composant intercalaires déjà actif dans le Hugo développé audité.

La lecture correcte du domaine est donc la suivante :

- **bonne compatibilité doctrinale avec l’architecture réelle** ;
- **pas de preuve d’implémentation observable à ce stade** ;
- **objet de cible à documenter et cadrer proprement**, sans le sur-vendre comme une capacité déjà livrée ;
- **priorité future au contrat, au vocabulaire et à l’intégration additive backend-first**, plutôt qu’à une projection produit spéculative.


# 01_matrice_ecarts — 120_intercalaires_v1

## Domaine

- `DOMAINE_CODE = 120_intercalaires_v1`
- `DOMAINE_LABEL = intercalaires pédagogiques V1`

---

## 1. Règle de lecture

Cette matrice croise trois niveaux distincts :

- la **cible 2.0** telle qu’elle est cadrée dans la spec canonique Hugo 2.0 et les documents projet récents ;
- le **réel observable** tel qu’il apparaît dans les audits Hugo réel, notamment `02_ETAT_MOTEUR_REEL.md`, `03_ETAT_PRODUIT_REEL.md`, `05_ECARTS_DOC_CODE_PRODUIT.md`, `07_RUNTIME_DEMO_REFERENCE.md` et `09_PARCOURS_DEMO_ET_SCENARIOS.md` ;
- le **glossaire d’alignement**, utilisé comme pont de vocabulaire et non comme preuve d’implémentation.

Les statuts utilisés sont :

- `ALIGNE`
- `ALIGNE_DOC_PARTIEL`
- `RENOMMER_DANS_DOC`
- `AMBIGU`
- `A_VERIFIER`
- `ABSENT / NOUVEAU_CONTRAT`

---

## 2. Matrice des écarts

| Élément du domaine | Cible 2.0 | Réel observable Hugo cœur | Source(s) mobilisée(s) | Statut | Lecture / écart constaté | Action documentaire recommandée |
|---|---|---|---|---|---|---|
| Intercalaire pédagogique V1 comme capacité additive | Oui, capacité dérivée additive de Hugo cœur | Pas de preuve positive d’une capacité active documentée dans les audits du réel | Spec canonique Hugo 2.0 ; glossaire d’alignement ; audits réel | ABSENT / NOUVEAU_CONTRAT | Le domaine est bien cadré côté cible, mais non observé comme feature livrée | Documenter explicitement qu’il s’agit d’un objet cible non encore observé dans le réel |
| Objet doctrinal de type `SessionInterstitial` ou équivalent | Oui, nom conceptuel utile pour porter le domaine | Aucun nom réel observé raccordé dans Hugo développé audité | Glossaire d’alignement | A_VERIFIER | Le glossaire signale le concept, mais refuse d’en faire un objet réel | Garder le nom conceptuel dans la doc cible, avec mention explicite “objet cible, non observé dans le réel” |
| Production post-tour principal | Oui, après le tour principal | Aucun service réel identifié comme producteur d’un intercalaire post-tour | Spec canonique Hugo 2.0 ; audits réel | ABSENT / NOUVEAU_CONTRAT | Le point d’insertion cible est clair, mais aucun chaînage réel n’est observé | Introduire ce point d’insertion comme contrat cible backend, sans le présenter comme déjà branché |
| Préparation après persistance / en async | Oui, idéalement après persistance via tâche asynchrone | Pas de preuve d’une tâche dédiée intercalaires ; existence générale de workers async dans l’architecture | Spec canonique Hugo 2.0 ; SPEC POC v1.5 ; audits réel | ALIGNE_DOC_PARTIEL | L’architecture réelle permet ce mode d’implémentation, mais le domaine lui-même n’est pas branché | Documenter cela comme contrainte de mise en œuvre compatible avec le réel, pas comme existant |
| Effet nul sur P0 et décision tutorale principale | Oui, aucun effet retour sur P0 ni sur la décision locale | Rien dans le réel n’indique une couche concurrente ; absence de feature observée | Spec canonique Hugo 2.0 ; audits réel | ALIGNE_DOC_PARTIEL | Le garde-fou doctrinal est cohérent avec l’architecture réelle backend-first | Conserver ce garde-fou comme invariant de design du domaine |
| Composant apprenant passif | Oui | Aucun composant identifié comme tel dans les surfaces produit auditées | Spec canonique Hugo 2.0 ; état produit réel ; parcours démo | ABSENT / NOUVEAU_CONTRAT | Pas de preuve d’un composant produit stabilisé correspondant | Décrire un futur composant passif cible, sans le raccorder artificiellement à une UI existante |
| Non interactif | Oui | Aucun composant réel correspondant observé | Spec canonique Hugo 2.0 ; audits produit | ABSENT / NOUVEAU_CONTRAT | L’exigence est cible uniquement | Garder la propriété dans le contrat cible minimal |
| Non évaluatif | Oui | Aucun mécanisme intercalaire réel observé ; l’évaluation réelle reste sur sa branche dédiée | Spec canonique Hugo 2.0 ; glossaire d’alignement ; audits réel | ALIGNE_DOC_PARTIEL | Bon alignement de doctrine : l’intercalaire ne doit pas se confondre avec l’évaluation | Ajouter un garde-fou explicite contre toute confusion avec la branche terminale d’évaluation |
| Visible côté apprenant uniquement | Oui | Pas de surface observée permettant de confirmer une exposition réelle | Spec canonique Hugo 2.0 ; état produit réel | ABSENT / NOUVEAU_CONTRAT | Règle cible claire, non démontrée dans le réel | Garder comme contrainte UI/produit pour futur contrat |
| `NONE` fréquent | Oui | Aucun système réel observé permettant de mesurer la fréquence | Spec canonique Hugo 2.0 ; documents projet intercalaires | ABSENT / NOUVEAU_CONTRAT | Règle de comportement cible, non testable dans le réel actuel | Documenter comme règle de parcimonie du domaine |
| Typologie minimale `NONE / NOTION / CONTRAST` | Oui | Aucune énumération réelle observée dans le code ou la doc d’audit | Documents projet ; glossaire d’alignement ; audits réel | ABSENT / NOUVEAU_CONTRAT | Les types relèvent encore du contrat cible | Formaliser cette enum dans la doc de domaine, sans prétendre qu’elle existe déjà en code |
| Un seul intercalaire maximum par tour | Oui | Pas de producteur réel observé | Documents projet ; audits réel | ABSENT / NOUVEAU_CONTRAT | Règle cible claire, sans observation runtime | Documenter cette contrainte comme invariant de non-invasion UX |
| Source backend = artefacts structurés existants | Oui, dérivation depuis états et objets backend | Le réel dispose bien de `TurnState`, contrat de décision, `ConversationProgress`, `UIState`, mémoire gouvernée, signaux qualité | Spec canonique Hugo 2.0 ; glossaire d’alignement ; audits réel | ALIGNE | Le socle backend requis existe déjà de manière cohérente | Citer explicitement ces artefacts comme base technique du futur domaine |
| Intégration backend-first, pas front-driven | Oui | Oui, le réel montre un front consommant des états dérivés et non une logique tutorale frontale | Spec canonique Hugo 2.0 ; état moteur réel ; état produit réel ; écarts doc/code/produit | ALIGNE | Très bon alignement de doctrine et d’architecture | Faire de ce point un invariant d’implémentation du domaine |
| Appui sur `UIState` ou projection dérivée | Oui, plausible doctrinalement | `UIState` est réel et stable, mais aucun sous-contrat “intercalaire” n’est observé | Spec canonique Hugo 2.0 ; glossaire d’alignement ; audits réel | AMBIGU | La base produit existe, mais le rattachement exact du futur domaine à `UIState` n’est pas fixé | Laisser ce point ouvert et expliciter qu’il faudra arbitrer entre champ `UIState` et projection sœur |
| Nom de backing model / service réel | Attendu à terme mais non fixé doctrinalement | Aucun nom réel observé dans le corpus audité | Glossaire d’alignement ; audits réel | ABSENT / NOUVEAU_CONTRAT | Pas de modèle, service ou endpoint clairement documenté sur ce domaine | Éviter d’inventer un nom de code ; garder le besoin au niveau contrat |
| Endpoint dédié de lecture d’intercalaire | Non imposé explicitement | Aucun endpoint observé | Audits réel ; glossaire d’alignement | ABSENT / NOUVEAU_CONTRAT | Aucun contrat serveur observable aujourd’hui | Ne pas postuler d’endpoint tant que l’arbitrage produit/backend n’est pas fait |
| Présence en démo montrable | Non indispensable doctrinalement | Non documentée comme capacité montrée dans les parcours de démo audités | État produit réel ; runtime démo ; parcours démo | ABSENT / NOUVEAU_CONTRAT | La démo actuelle ne prouve pas le domaine | Ne pas inclure cette capacité dans la description du montrable réel |
| Présence derrière flags runtime | Possible en théorie | Non prouvée dans le corpus utilisé ici | Écarts doc/code/produit ; runtime distant non entièrement recoupé | A_VERIFIER | Toute affirmation d’activation derrière flag resterait spéculative | Marquer explicitement ce point `A_VERIFIER` tant qu’aucune relecture code/runtime ne le confirme |
| Compatibilité avec confidentialité-first et non-exposition du verbatim | Oui, exigence impérative | Rien dans le réel n’indique un contournement ; la doctrine générale du produit va dans ce sens | Spec canonique Hugo 2.0 ; SPEC POC v1.5 ; audits réel | ALIGNE_DOC_PARTIEL | Le domaine n’existe pas encore comme feature observée, mais son futur cadrage doit rester pleinement compatible avec les invariants existants | Ajouter un garde-fou spécifique : aucun intercalaire ne doit exposer verbatim brut ni signaux sensibles bruts |
| Compatibilité multi-tenant stricte | Oui | L’architecture réelle est multi-tenant stricte, mais aucun contrat intercalaire réel n’est audité | Spec canonique Hugo 2.0 ; SPEC POC v1.5 ; audits réel | ALIGNE_DOC_PARTIEL | Le domaine devra s’inscrire dans ce cadre, sans preuve d’implémentation actuelle | Noter la contrainte sans sur-affirmer une implémentation spécifique |

---

## 3. Lecture synthétique des statuts

### 3.1 Zones `ALIGNE`

Les points réellement **alignés** portent surtout sur le **socle d’architecture** nécessaire au domaine :

- backend Django orchestré ;
- front drivé par états dérivés ;
- existence de `UIState`, `ConversationProgress`, contrat de décision et autres artefacts backend compatibles ;
- logique générale backend-first cohérente avec un enrichissement additif.

### 3.2 Zones `ALIGNE_DOC_PARTIEL`

Les points **partiellement alignés documentairement** concernent surtout les **garde-fous** :

- pas d’effet retour sur P0 ;
- compatibilité confidentialité-first ;
- non-confusion avec l’évaluation ;
- possibilité d’un traitement post-persistance / async ;
- inscription dans la discipline multi-tenant stricte.

Ici, le problème n’est pas une contradiction du réel, mais l’absence d’un contrat de domaine encore explicité.

### 3.3 Zones `ABSENT / NOUVEAU_CONTRAT`

Les écarts principaux sont dans cette catégorie :

- pas de feature réellement observée ;
- pas de composant produit identifié ;
- pas de service ni modèle documenté ;
- pas d’enum réelle observée ;
- pas de contrat serveur explicite ;
- pas de présence démontrée dans la démo.

Le domaine est donc, à ce stade, essentiellement un **nouveau contrat à documenter**, pas un simple renommage d’existant.

### 3.4 Zones `AMBIGU` et `A_VERIFIER`

Deux types d’incertitude restent distincts :

- `AMBIGU` quand la **base technique existe**, mais que le point de raccord exact n’est pas encore arbitré, par exemple le rattachement précis à `UIState` ou à une projection dérivée ;
- `A_VERIFIER` quand une affirmation dépendrait d’un runtime distant, de flags ou d’une variante non auditée localement.

---

## 4. Décision de lecture pour la suite

Pour le domaine `120_intercalaires_v1`, la lecture correcte est la suivante :

- **la doctrine cible est suffisamment cadrée pour écrire un contrat propre** ;
- **le réel observable n’offre pas de preuve d’implémentation active** ;
- **le socle technique de Hugo cœur est compatible avec une implémentation additive correcte** ;
- **le travail à faire est d’abord documentaire et contractuel**, avant d’être un chantier de refonte.

En conséquence, la suite logique n’est pas de “reconnaître” une feature cachée, mais de :
1. fixer les décisions documentaires minimales du domaine ;
2. borner précisément le contrat cible ;
3. préparer ensuite un backlog d’actions additif, backend-first, sans sur-vendre le réel.
# 02_decisions_documentaires — 120_intercalaires_v1

## Domaine

- `DOMAINE_CODE = 120_intercalaires_v1`
- `DOMAINE_LABEL = intercalaires pédagogiques V1`

---

## 1. Objet du document

Ce document fixe les **décisions documentaires** à retenir pour le domaine **intercalaires pédagogiques V1** dans Hugo cœur, à partir de la cible 2.0, des audits du réel et du glossaire d’alignement.

Il ne décrit ni un chantier code détaillé, ni une preuve d’implémentation déjà livrée. Son rôle est de stabiliser une manière correcte d’écrire ce domaine dans la documentation, sans sur-promesse, sans collision de vocabulaire et sans régression doctrinale.

---

## 2. Décision-cadre

### D1 — Le domaine est maintenu comme **capacité cible**, pas comme capacité livrée

Les intercalaires pédagogiques V1 sont conservés dans la documentation Hugo cœur comme une **capacité cible cadrée**. Ils ne doivent pas être décrits comme une fonctionnalité déjà observable dans le Hugo audité.

**Conséquence documentaire :**
- toute formulation du type “Hugo affiche déjà des intercalaires pédagogiques” est interdite ;
- la formulation correcte est : **capacité cible prévue / cadrée / à contractualiser**, non **feature déjà livrée**.

---

## 3. Décisions de vocabulaire

### D2 — Conserver un nom doctrinal de domaine, sans l’ériger en objet réel

Le domaine garde un nom doctrinal explicite de type **intercalaires pédagogiques V1**. Le nom conceptuel `SessionInterstitial` ou équivalent peut être conservé comme **nom de travail cible**, mais il ne doit pas être présenté comme un objet réel déjà observé dans Hugo développé.

**Conséquence documentaire :**
- on peut écrire : “objet cible de type `SessionInterstitial` ou équivalent” ;
- on ne doit pas écrire : “le modèle `SessionInterstitial` existe dans le réel” ;
- tant qu’aucun backing model, service ou contrat réel n’est audité, le terme reste marqué **objet cible / nom conceptuel**.

### D3 — Ne pas inventer de nom réel de service, modèle ou endpoint

Aucun nom réel de service, de table, de serializer, de champ `UIState` ou d’endpoint ne doit être introduit par anticipation pour ce domaine.

**Conséquence documentaire :**
- pas de pseudo-réalité du type `interstitials.py`, `session_interstitial`, `GET /interstitial`, ou équivalent ;
- si un nom technique est proposé plus tard, il devra être introduit dans un document de décision technique ou d’implémentation, pas dans la documentation d’écarts comme s’il était déjà établi.

---

## 4. Décisions de positionnement architectural

### D4 — Documenter les intercalaires comme **surcouche additive backend-first**

Le domaine doit être décrit comme une **surcouche additive** produite à partir d’artefacts backend déjà structurés, et non comme une logique pédagogique autonome portée par le front.

**Conséquence documentaire :**
- toute formulation front-driven est à proscrire ;
- la documentation doit rappeler que le domaine consomme des sorties structurées du moteur et s’inscrit dans la continuité de l’architecture backend Django orchestrée.

### D5 — Documenter explicitement l’absence d’effet retour sur le moteur principal

Les intercalaires V1 doivent être décrits comme **sans effet retour** sur :
- le noyau P0 ;
- la décision tutorale locale ;
- la posture active ;
- le contrat de décision principal.

**Conséquence documentaire :**
- l’intercalaire n’est pas une seconde décision tutorale ;
- il n’est pas une couche de pilotage concurrente ;
- il n’est pas un mini-régime conversationnel secondaire.

### D6 — Documenter le déclenchement comme **post-tour**, idéalement **post-persistance**

Le point d’insertion documentaire du domaine est fixé comme suit :
- après le tour principal ;
- idéalement après persistance ;
- si possible via une logique asynchrone légère.

**Conséquence documentaire :**
- ce point doit être décrit comme **contrat cible de bonne architecture** ;
- il ne doit pas être écrit comme un comportement réellement audité dans Hugo cœur.

---

## 5. Décisions de périmètre fonctionnel

### D7 — Fixer un périmètre V1 volontairement minimal

La documentation de domaine doit retenir un périmètre V1 minimal et fermé :

- au plus **un intercalaire par tour** ;
- `NONE` fréquent ;
- typologie minimale : `NONE`, `NOTION`, `CONTRAST` ;
- composant **passif** ;
- composant **non interactif** ;
- composant **non évaluatif** ;
- visibilité **apprenant uniquement** ;
- capacité **débrayable par flag**.

**Conséquence documentaire :**
- ne pas élargir la V1 à du quiz, du drill, de la remédiation pilotée, du feedback adaptatif riche ou une logique de parcours autonome ;
- ne pas présenter les intercalaires comme une “couche pédagogique complète”.

### D8 — Insister sur la rareté et la parcimonie

Le document de domaine doit acter que `NONE` est fréquent et que l’absence d’intercalaire est un comportement normal.

**Conséquence documentaire :**
- l’intercalaire est une exception utile, pas une sortie systématique ;
- il ne doit pas devenir un bruit visuel ou un second canal permanent de conduite.

---

## 6. Décisions de raccord avec le réel

### D9 — S’appuyer explicitement sur les artefacts backend déjà observés comme base de compatibilité

Même si la capacité n’est pas observée comme livrée, la documentation peut affirmer qu’elle est **compatible** avec le socle réel existant, notamment avec :
- `TurnState` ;
- le contrat de décision ;
- `ConversationProgress` ;
- `UIState` ;
- la mémoire gouvernée ;
- les signaux qualité et autres artefacts dérivés backend.

**Conséquence documentaire :**
- on documente une **compatibilité d’architecture**, pas une implémentation existante ;
- cela permet d’éviter la dérive “nouvelle architecture parallèle”.

### D10 — Ne pas affirmer le point de rattachement exact tant qu’il n’est pas arbitré

La documentation ne doit pas trancher prématurément entre plusieurs options de projection produit :
- champ dans `UIState` ;
- projection sœur de `UIState` ;
- objet produit dérivé séparé mais servi dans le même cycle.

**Conséquence documentaire :**
- le bon niveau de formulation est : **rattachement produit à préciser** ;
- il faut éviter toute pseudo-précision technique non encore décidée.

### D11 — Ne pas décrire d’endpoint dédié tant qu’aucun contrat n’est stabilisé

Le domaine ne doit pas être documenté avec un endpoint propre tant que cette décision n’a pas été prise et reliée à une implémentation.

**Conséquence documentaire :**
- pas d’ajout spéculatif dans les matrices d’endpoints ;
- pas de faux alignement avec un endpoint “à venir” présenté comme quasi acquis.

---

## 7. Décisions de sécurité et de non-régression

### D12 — Ajouter un garde-fou explicite sur la confidentialité

La documentation du domaine doit rappeler qu’aucun intercalaire ne peut :
- exposer du verbatim non partagé ;
- exposer des champs P0 bruts ;
- contourner les règles de partage explicite ;
- créer un nouveau canal de fuite de données sensibles.

**Conséquence documentaire :**
- les intercalaires sont compatibles avec la doctrine confidentialité-first, mais ne bénéficient d’aucune exception.

### D13 — Ajouter un garde-fou explicite sur le multi-tenant

Le domaine doit être décrit comme soumis sans exception aux règles multi-tenant strictes déjà en vigueur.

**Conséquence documentaire :**
- aucun stockage, calcul, projection ou cache lié à ce domaine ne doit être formulé hors de l’isolation tenant ;
- aucune formulation ne doit laisser penser à une logique transversale hors cloisonnement.

### D14 — Ajouter un garde-fou explicite contre la dérive “mini-LMS”

La documentation doit interdire toute lecture du domaine comme :
- mini-cours ;
- moteur d’exercice autonome ;
- outil de remédiation structurée complet ;
- seconde interface de progression indépendante.

**Conséquence documentaire :**
- l’intercalaire reste un **appoint bref**, non une expérience pédagogique concurrente au moteur principal.

---

## 8. Décisions de rédaction dans les specs transverses

### D15 — Introduire le domaine dans la doc 2.0 comme **objet cible non observé dans le réel**

Dans les specs transverses et matrices canoniques, le domaine doit apparaître avec un marquage explicite du type :
- **objet cible** ;
- **capacité additive prévue** ;
- **non observée dans le réel audité à ce stade**.

**Conséquence documentaire :**
- on évite à la fois l’effacement du domaine et la sur-affirmation de livraison.

### D16 — Ajouter une règle de rédaction spécifique au domaine

La règle de rédaction à appliquer est :

> “Conserver le concept doctrinal d’intercalaire V1 ; ne pas l’introduire comme objet réel ; le raccorder aux artefacts backend réellement observés seulement au titre de compatibilité architecturale.”

**Conséquence documentaire :**
- cette règle doit guider les futures mises à jour des specs 2.0, des matrices backend et des prompts Cursor.

### D17 — Marquer tout point dépendant d’un runtime distant ou d’un flag en `A_VERIFIER`

Toute affirmation du type :
- “présent en prod” ;
- “activable derrière flag” ;
- “visible dans telle démo” ;
- “déjà branché dans telle variante”

doit rester explicitement marquée `A_VERIFIER` tant qu’elle n’est pas recoupée par un audit probant.

**Conséquence documentaire :**
- le domaine reste protégé contre les extrapolations depuis Encoors, des flags ou des variantes non relues.

---

## 9. Décisions de non-régression doctrinale

### D18 — Ne pas faire glisser le domaine vers une logique prompt-first

La documentation doit rappeler que les intercalaires V1 ne sont pas un “prompt bonus” autonome. Ils s’inscrivent dans une architecture où la vérité comportementale reste portée par :
- la spec ;
- l’orchestrateur backend ;
- le P0 ;
- le contrat de décision ;
- TutorPrompt ;
- la progression et les états dérivés.

### D19 — Ne pas faire glisser le domaine vers une logique front-first

Le front ne décide ni de l’opportunité, ni du type, ni du contenu moteur de l’intercalaire. Il ne fait, au mieux, que restituer un artefact dérivé déjà décidé côté backend.

### D20 — Ne pas faire glisser le domaine vers une logique “nouveau sous-produit”

Le domaine ne doit pas être documenté comme un nouveau module autonome d’Hugo cœur. Il reste une extension bornée du moteur tutoriel principal.

---

## 10. Synthèse opérationnelle des décisions

Les décisions documentaires retenues pour `120_intercalaires_v1` sont les suivantes :

1. Le domaine est **maintenu comme capacité cible** et non comme capacité livrée.
2. Le nom doctrinal est **conservé**, mais sans création fictive d’objet réel.
3. Le domaine est décrit comme **backend-first**, **additif**, **post-tour**, **sans effet retour sur P0**.
4. Le périmètre V1 est **minimal, passif, non interactif, non évaluatif, apprenant-only, débrayable**.
5. La documentation peut affirmer une **compatibilité forte avec l’architecture réelle**, mais pas une implémentation effective.
6. Les points techniques encore non arbitrés — notamment projection produit exacte, endpoint éventuel, persistance précise — restent **ouverts**.
7. Toute dépendance à une variante distante ou à un flag reste **`A_VERIFIER`**.
8. Le domaine doit être protégé contre trois dérives : **prompt-first**, **front-first**, **mini-LMS**.

---

## 11. Formulation canonique recommandée

La formulation canonique recommandée pour ce domaine est :

> Les intercalaires pédagogiques V1 constituent une capacité cible additive de Hugo cœur. Ils correspondent à un appoint pédagogique bref, passif, non interactif et non évaluatif, produit côté backend à partir d’artefacts structurés du moteur après le tour principal, sans effet retour sur le noyau P0 ni sur la décision tutorale. À ce stade, cette capacité est doctrinalement cadrée mais non observée comme feature livrée dans le Hugo cœur audité.

# 03_backlog_actions — 120_intercalaires_v1

## Domaine

- `DOMAINE_CODE = 120_intercalaires_v1`
- `DOMAINE_LABEL = intercalaires pédagogiques V1`

---

## 1. Objet du backlog

Ce backlog recense les actions à mener pour le domaine **intercalaires pédagogiques V1** dans Hugo cœur, en cohérence avec :
- la cible 2.0 ;
- les audits du réel ;
- les décisions documentaires déjà retenues sur ce domaine.

Il s’agit d’un backlog **borné**, priorisé et centré d’abord sur le **contrat**, le **vocabulaire**, le **raccord avec l’architecture réelle**, puis seulement sur la préparation d’une implémentation additive éventuelle.

---

## 2. Règles de priorisation

Les priorités retenues sont :
- `P0_DOC` : indispensable pour éviter les erreurs de lecture et de cadrage ;
- `P1_CONTRAT` : nécessaire pour rendre le domaine implémentable proprement ;
- `P2_PREP_TECH` : préparation technique limitée, sans refonte ;
- `P3_IMPL` : implémentation éventuelle, seulement après stabilisation documentaire et contractuelle ;
- `P4_VERIF` : vérifications dépendant d’un audit complémentaire ou d’un runtime non encore recoupé.

Le backlog ne présume pas que tout doit être codé immédiatement. Sur ce domaine, la priorité est de **ne pas confondre cible cadrée et feature livrée**.

---

## 3. Backlog priorisé

| ID | Priorité | Action | Type | Résultat attendu | Dépendances | Statut initial |
|---|---|---|---|---|---|---|
| INT-001 | P0_DOC | Ajouter dans les docs de domaine et matrices transverses la mention explicite “capacité cible non observée dans le réel audité” | Documentation | Toute lecture du domaine devient non ambiguë sur cible vs livré | Aucune | À faire |
| INT-002 | P0_DOC | Ajouter une règle de rédaction interdisant de présenter `SessionInterstitial` comme objet réel observé | Documentation | Le vocabulaire doctrinal est conservé sans fausse preuve d’implémentation | INT-001 | À faire |
| INT-003 | P0_DOC | Ajouter un garde-fou documentaire “intercalaire != mini-LMS != branche d’évaluation != moteur parallèle” | Documentation | Le domaine est borné contre les dérives d’interprétation | INT-001 | À faire |
| INT-004 | P0_DOC | Ajouter un garde-fou documentaire “backend-first, sans effet retour sur P0 ni sur la décision locale” | Documentation | Le domaine est arrimé aux invariants Hugo cœur | INT-001 | À faire |
| INT-005 | P1_CONTRAT | Rédiger un mini-contrat canonique du domaine avec périmètre V1 minimal : `NONE`, `NOTION`, `CONTRAST`, au plus un par tour, composant passif, non interactif, non évaluatif | Contrat | Une fiche de contrat courte et réutilisable existe | INT-001 à INT-004 | À faire |
| INT-006 | P1_CONTRAT | Définir précisément les entrées backend autorisées pour dériver un intercalaire, à partir d’artefacts déjà observés (`TurnState`, contrat de décision, `ConversationProgress`, `UIState` ou projection sœur, mémoire gouvernée) | Contrat backend | Le domaine peut être branché sans architecture parallèle | INT-005 | À faire |
| INT-007 | P1_CONTRAT | Définir explicitement ce que le domaine n’a pas le droit de consommer ou d’exposer : verbatim non partagé, champs P0 bruts, prompts complets, données cross-tenant | Contrat sécurité | Les limites de sécurité et de confidentialité sont figées | INT-005 | À faire |
| INT-008 | P1_CONTRAT | Arbitrer au niveau documentaire le point de projection produit : champ dans `UIState`, projection sœur, ou objet dérivé séparé | Contrat produit | Le point d’attache côté produit est clarifié sans sur-spécification | INT-006 | À faire |
| INT-009 | P1_CONTRAT | Décider si le domaine doit rester sans endpoint dédié en V1 ou disposer d’une restitution incluse dans un contrat existant | Contrat API/produit | Pas de spéculation sur un endpoint futur | INT-008 | À faire |
| INT-010 | P1_CONTRAT | Écrire la matrice de non-régression spécifique au domaine : pas de duplication P0, pas de logique front, pas de boucle pédagogique autonome, pas d’auto-promotion de statut | Gouvernance technique | Le domaine est protégé avant toute implémentation | INT-005 à INT-009 | À faire |
| INT-011 | P2_PREP_TECH | Identifier dans le pipeline réel le meilleur point d’insertion technique post-tour / post-persistance / async pour une production additive | Préparation technique | Une note d’implantation réaliste alignée sur Hugo cœur existe | INT-006 | À faire |
| INT-012 | P2_PREP_TECH | Préparer un mapping “nom doctrinal / nom réel observé” pour les artefacts que le domaine pourrait consommer | Alignement vocabulaire | Les prompts Cursor futurs évitent les collisions de noms | INT-006 | À faire |
| INT-013 | P2_PREP_TECH | Définir une structure de payload minimale du domaine, purement dérivée et sérialisable, sans champs sensibles | Contrat technique | Un schéma minimal de sortie existe pour tests et UI | INT-008 à INT-010 | À faire |
| INT-014 | P2_PREP_TECH | Définir la stratégie de flag du domaine : off par défaut, débrayable, sans effet secondaire sur le pipeline principal | Gouvernance runtime | Activation maîtrisée et réversible | INT-010 | À faire |
| INT-015 | P2_PREP_TECH | Définir les critères d’émission de `NONE` comme comportement normal et majoritaire | Logique métier | La parcimonie du domaine est explicitée | INT-005 | À faire |
| INT-016 | P2_PREP_TECH | Définir les critères minimaux d’émission de `NOTION` | Logique métier | Le type `NOTION` n’est pas laissé à une intuition vague | INT-015 | À faire |
| INT-017 | P2_PREP_TECH | Définir les critères minimaux d’émission de `CONTRAST` | Logique métier | Le type `CONTRAST` est borné proprement | INT-015 | À faire |
| INT-018 | P3_IMPL | Produire un prompt Cursor d’audit ciblé pour repérer les points de branchement existants les plus compatibles avec une surcouche intercalaire | Pré-implémentation | Un audit technique exploitable par le CTO est prêt | INT-011 à INT-014 | À faire |
| INT-019 | P3_IMPL | Produire un prompt Cursor de mise en œuvre backend additive, sans modification du cœur P0 ni refonte d’API large | Pré-implémentation | Une première proposition de chantier code est encadrée | INT-013 à INT-018 | À faire |
| INT-020 | P3_IMPL | Produire un prompt Cursor de projection produit minimale pour affichage passif apprenant-only | Pré-implémentation produit | La couche front est bornée avant tout code | INT-008, INT-013, INT-019 | À faire |
| INT-021 | P3_IMPL | Préparer un plan de tests minimal : tests de non-régression moteur, tests de sérialisation, tests de confidentialité, tests de parcimonie `NONE` | Qualité | Le domaine devient testable sans fragiliser Hugo cœur | INT-013 à INT-020 | À faire |
| INT-022 | P4_VERIF | Vérifier si une variante runtime distante ou un flag existant porte déjà un artefact proche du domaine | Vérification | Toute affirmation sur l’existant distant sort du spéculatif | Aucune, mais audit complémentaire requis | A_VERIFIER |
| INT-023 | P4_VERIF | Vérifier si des maquettes, branches ou documents hors corpus audité décrivent déjà un composant produit proche | Vérification documentaire | Les artefacts d’archive sont triés sans contaminer le réel | Aucune | A_VERIFIER |
| INT-024 | P4_VERIF | Vérifier si le domaine peut se raccorder proprement à `UIState` sans dégrader la lisibilité de la grammaire produit existante | Vérification produit | Le choix de projection est confirmé ou rejeté sur base concrète | INT-008, audit produit complémentaire | A_VERIFIER |

---

## 4. Ordre recommandé d’exécution

### Phase 1 — Sécurisation documentaire

Actions à faire en premier :
- `INT-001`
- `INT-002`
- `INT-003`
- `INT-004`

But : empêcher toute mauvaise lecture du domaine dans les specs, audits dérivés et prompts futurs.

### Phase 2 — Contrat minimal du domaine

Actions à enchaîner ensuite :
- `INT-005`
- `INT-006`
- `INT-007`
- `INT-008`
- `INT-009`
- `INT-010`

But : transformer un concept doctrinal en **contrat cible minimal, propre et implémentable**.

### Phase 3 — Préparation technique légère

Actions à lancer après stabilisation du contrat :
- `INT-011`
- `INT-012`
- `INT-013`
- `INT-014`
- `INT-015`
- `INT-016`
- `INT-017`

But : rendre possible une intervention technique additive sans dérive d’architecture.

### Phase 4 — Pré-implémentation encadrée

Actions à lancer seulement après les trois phases précédentes :
- `INT-018`
- `INT-019`
- `INT-020`
- `INT-021`

But : produire un chantier CTO exploitable, avec prompts Cursor et plan de test, sans partir d’une base floue.

### Phase 5 — Vérifications externes ou complémentaires

Actions à exécuter seulement si nécessaire :
- `INT-022`
- `INT-023`
- `INT-024`

But : lever les ambiguïtés dépendant d’archives, de variantes distantes ou d’un audit produit complémentaire.

---

## 5. Actions à ne pas lancer tout de suite

Les actions suivantes sont explicitement **hors priorité immédiate** pour ce domaine :

- création directe d’un modèle Django sans contrat stabilisé ;
- ajout d’un endpoint dédié par défaut ;
- implémentation front avant arbitrage du point de projection produit ;
- enrichissement V1 vers des interactions, quiz, correction ou remédiation ;
- intégration d’une logique LLM parallèle au pipeline principal ;
- requalification du domaine en sous-produit autonome.

Ces actions seraient prématurées et risqueraient de casser les invariants Hugo cœur.

---

## 6. Résultat cible du backlog

À l’issue de ce backlog, le domaine `120_intercalaires_v1` doit aboutir à un état beaucoup plus propre :

- la doc sait dire clairement ce qui est **cible** et ce qui est **réel** ;
- le domaine dispose d’un **contrat minimal stable** ;
- le vocabulaire doctrinal est conservé sans fiction d’implémentation ;
- le point de raccord à l’architecture Hugo cœur est clarifié ;
- une éventuelle implémentation additive devient possible sans refonte du moteur.

---

## 7. Décision de pilotage

La bonne stratégie pour ce domaine est :

1. **sécuriser la documentation** ;
2. **figer le contrat minimal** ;
3. **préparer le branchement technique** ;
4. **n’implémenter qu’ensuite**, de manière additive et testable.

Le domaine 120 ne doit donc pas partir en “dev first”. Il doit d’abord passer par un **cadrage documentaire et contractuel strict**, cohérent avec la doctrine Hugo 2.0 et avec le réel audité.