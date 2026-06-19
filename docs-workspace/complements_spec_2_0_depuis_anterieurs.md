> Niveau de vérité – Document `specs interface 2.0`  
> - Statut global : CIBLE 2.0. Ce document décrit une cible d’interface Hugo 2.0 (apprenant, formateur, tuteur, ORGADMIN, superadministration technique). Il ne doit jamais être relu comme preuve que toutes les surfaces et workflows décrits sont déjà livrés dans le runtime courant.  
> - Hiérarchie de vérité : pour décrire l’existant, le code hugoback, les audits moteur (02_ETAT_MOTEUR_REEL.md), produit (03_ETAT_PRODUIT_REEL.md) et les rapports d’écarts de domaine priment. Pour décrire la cible, la présente spec et la spec canonique 2.0 font foi.  
> - Lecture attendue : sauf mention contraire locale (IMPLÉMENTÉ, A_VERIFIER…), chaque capacité ou écran décrit ici relève de la cible. Toute dépendance à un runtime distant (Encoors) ou à un flag non audité doit rester marquée A_VERIFIER, conformément à 00_HIERARCHIE_DOCUMENTAIRE.md.

# Compléments exploitables de la spec Hugo 2.0 à partir des specs antérieures

## Statut et règle d'usage

Ce document complète la base 2.0 de travail en mobilisant **uniquement** des éléments antérieurs qui restent compatibles avec les arbitrages des quatre documents 2.0 désormais prioritaires.[file:21][file:22][file:23][file:24] Les documents 2.0 décrivent un **état cible spécifié** et imposent la doctrine de référence ; les specs antérieures ne sont utilisées ici que comme réservoir de précision secondaire pour combler des zones sous-spécifiées, jamais comme source d'arbitrage concurrente.[file:21][file:5]

Le document suit donc une règle stricte : un complément ancien n'est retenu que s'il **prolonge** la charpente 2.0 sans réintroduire une doctrine devenue caduque, comme Hugo mono-posture, la règle stricte « une question par message », une logique front-pilotée, ou une centralité excessive du prompt.[file:21][file:26][file:25]

## Cadre de filtrage

Les quatre documents 2.0 fixent déjà les invariants structurants : backend Django orchestré, TutorPrompt comme pivot runtime, P0 comme régulation locale commune, mémoire gouvernée, front dérivé d'états produit, confidentialité-first, partage explicite et multi-tenant strict.[file:21][file:22][file:23][file:24] Les documents antérieurs ne peuvent être retenus que s'ils renforcent un de ces invariants ou détaillent un composant encore ouvert, sans les contredire.[file:5][file:26]

Le filtre de compatibilité retenu est le suivant :

- **Acceptable** : détail de schéma, hiérarchie de contexte, séquencement runtime, contrats de services, statuts, garde-fous techniques, tant qu'ils restent compatibles avec le multi-postures 2.0.[file:21][file:26]
- **À neutraliser** : toute formulation qui recadre Hugo comme simple assistant AFEST mono-posture, ou qui remet le prompt au centre du système.[file:25][file:26]
- **À exclure** : anciennes hypothèses produit ou UX devenues incompatibles avec UIState, ConversationProgress, posture active visible, base formateur gouvernée, couche tuteur et évaluation facultative.[file:21][file:24][file:25]

## Compléments retenables

### 1. Pipeline runtime et séquencement des services

La spec canonique 2.0 décrit déjà la chaîne cible en six temps, mais les specs antérieures apportent un niveau de séquencement plus exploitable pour l'implémentation backend.[file:21] Le cadrage 1.6 décrit un pipeline en sept étapes distinguant chargement du contexte structuré, analyse du tour, mise à jour des états, décision du prochain geste, récupération ciblée du contexte complémentaire, génération du message et traçabilité/évaluation facultative.[file:26]

Ce complément est compatible avec 2.0 à condition d'être **reformulé** en vocabulaire actuel :

| Complément exploitable | Apport | Condition de reprise |
|---|---|---|
| Pipeline en 7 étapes inspiré 1.6 [file:26] | Donne un ordre opératoire plus précis que la chaîne 6 temps de la canonique [file:21] | Remplacer les anciens noms d'objets par la terminologie 2.0 (P0, contrat de décision, PostureSelector, ConversationProgress, UIState) |
| Étape dédiée de récupération ciblée du contexte [file:26] | Clarifie où interviennent mémoire, verbatim interne, overlay référentiel et RAG [file:26] | Respecter la hiérarchie mémoire 2.0 et l'interdiction d'exposer le verbatim [file:21] |
| Étape distincte de persistance/traçabilité post-tour [file:26] | Aide à séparer runtime conversationnel et consolidation analytique | Maintenir la règle 2.0 de consolidation post-conversation pour mémoire et analytics [file:21] |

Décision proposée : intégrer dans la future 2.1 un **schéma de séquence logique** du runtime inspiré de 1.6, mais réécrit entièrement selon les arbitrages 2.0.[file:21][file:26]

### 2. Hiérarchie de contexte et ordre de récupération

La canonique 2.0 fixe déjà une hiérarchie générale : état apprenant, mémoire thématique, verbatim interne ponctuel si nécessaire, overlay référentiel, puis documentaire en renfort situé.[file:21] Le cadrage 1.6 explicite cette hiérarchie avec davantage de netteté et confirme que le documentaire ne doit pas devenir le pilote principal du dialogue.[file:26]

Cette précision peut être reprise presque telle quelle, car elle est doctrinalement cohérente avec 2.0 :

- contexte structuré comme base de pilotage immédiat ;
- mémoire thématique inter-session comme couche durable ;
- verbatim interne seulement en récupération ciblée ;
- overlay/référentiel avant le RAG documentaire ;
- RAG en renfort situé, jamais comme mémoire principale.[file:21][file:26]

Décision proposée : intégrer ce point dans la spec canonique sous forme de **matrice de récupération du contexte** ou de pseudo-algorithme de priorité, sans réimporter les formulations historiques sur le SoT central.[file:21][file:26]

### 3. Contrats backend minimaux et services nominaux

La canonique 2.0 contient déjà une matrice des services backend minimaux : analyse du tour, décision locale, PostureSelector, PromptRenderer, ProgressionCalculator, UIStateBuilder, MemoryConsolidator, DocumentIngestor, SynthesisService, QualityTracker.[file:21] Le cadrage 1.6 et les docs antérieurs permettent de compléter leur rôle opérationnel avec des entrées/sorties plus concrètes, notamment pour la mémoire, les contradictions et la récupération ciblée.[file:21][file:26]

Les compléments utiles sont :

- distinction plus nette entre **mise à jour d'état** et **récupération de contexte complémentaire** ;
- possibilité d'un objet métier de contradiction, traité avant réinterrogation du verbatim ;
- séparation entre génération du message et consolidation durable de mémoire/qualité.[file:26]

Décision proposée : conserver la matrice 29.4/29.5 de la canonique comme charpente et la compléter avec :

- les préconditions et postconditions de chaque service ;
- les objets lus/écrits ;
- les interdits de chaque service (par exemple UIStateBuilder ne lit jamais P0 brut pour l'exposer, QualityTracker ne lit pas le verbatim non partagé comme surface métier).[file:21][file:26]

### 4. Objets mémoire, contradiction et consolidation

La base 2.0 fixe la doctrine mémoire, mais reste légère sur les objets techniques précis.[file:21] Le cadrage 1.6 propose un découpage plus fin : `ThemeMemory`, liens souples avec le référentiel, événements de thème, consolidation, et un objet explicite de contradiction avec statuts distincts.[file:26]

Ces éléments peuvent être repris **comme patrons de modélisation**, sous réserve de renommer et de simplifier si nécessaire :

| Objet ancien utile | Valeur pour 2.0 | Risque de dérive |
|---|---|---|
| Mémoire thématique inter-session par thème [file:26] | Donne une structure durable compatible avec la mémoire gouvernée [file:21] | Faible, si on garde la gouvernance et l'absence de verbatim brut |
| Lien entre thème émergent et référentiel [file:26] | Aide à conserver la doctrine référentiel-first mais extensible [file:21][file:26] | Faible |
| Objet de contradiction avec statuts distincts [file:26] | Complète utilement la gestion des contradictions déjà mentionnée par P0 [file:21] | Moyen, si la complexité dépasse le besoin produit réel |
| Références minimales de preuve de contradiction sans texte brut [file:26] | Très cohérent avec confidentialité-first [file:21][file:26] | Faible |

Décision proposée : reprendre la **logique métier** de ces objets dans la future spec “Hugo projet actuel”, mais ne pas figer trop tôt le nom exact des tables tant que le chantier code n'est pas ouvert.[file:21][file:26]

### 5. Champs de décision et variables backend disponibles

Tu as précisé que les prompts ne doivent pas encore être dans la spec, ce qui est cohérent à ce stade.[file:21] En revanche, les specs antérieures aident à mieux lister les **variables backend disponibles ou plausibles** qu'une future couche prompt pourrait consommer sans devenir source de vérité.[file:21][file:26]

Les éléments robustes à conserver sont :

- côté décision locale : `primarygoal`, `tutorialmove`, `mode`, `targetquestioncount`, `questionbundlingallowed`, `microexplainallowed`, `usethemememory`, `useverbatimretrieval`, `useoverlayfirst`, `userag`, `optionalevaluationeligible`, `reasoncodes`.[file:21][file:26]
- côté progression : branches actives, branche prioritaire, maturité globale, dispersion_risk, missing_for_next_level, éligibilité synthèse, éligibilité évaluation.[file:21]
- côté UI produit : scène, quête active, couleur de maturité, posture active si exposée, CTA terminales, objets persistants.[file:21][file:24]
- côté connaissance formateur : statut, type, provenance, rattachements référentiels, métadonnées d'usage documentaire/RAG.[file:21][file:23]

Décision proposée : ne pas écrire les prompts maintenant, mais préparer dans la 2.1 ou dans un appendice une **liste canonique des variables backend exposables au PromptRenderer**.[file:21][file:26]

### 6. Endpoints et API d'état minimales

La matrice 29.5 de la canonique fournit déjà les endpoints minimaux : messages, posture, progress, ui-state, memory-summary, actions de synthèse, actions d'évaluation, vues/actions trainer.[file:21] Les specs antérieures n'imposent pas d'autres endpoints de doctrine supérieure, mais elles confortent la nécessité d'une lecture backend-first avec états dérivés côté serveur.[file:21][file:26]

Ce qui peut être ajouté utilement à la spec sans dérive :

- distinguer ce qui relève d'un **endpoint runtime** (message, changement de posture) ;
- ce qui relève d'un **endpoint de lecture produit** (`/ui-state`, `/progress`, mémoire résumée) ;
- ce qui relève d'actions **conditionnelles et gouvernées** (synthèse, évaluation, validation humaine) ;
- ce qui relève d'interfaces métier distinctes (trainer, tutor, cohorte).[file:21][file:23][file:24]

Décision proposée : ajouter dans la future version canonique une mini-spécification d'API d'état avec statuts de réponse attendus et garde-fous de refus, mais sans figer encore tous les payloads JSON.[file:21]

### 7. UIState et grammaire produit

Les docs 2.0 d'interface sont déjà la source principale sur ce sujet.[file:24] Les specs antérieures utiles n'apportent pas une doctrine supérieure, mais confirment que la couche produit doit être construite à partir d'états dérivés et non depuis P0 brut, avec progression visible, scène, objets persistants et actions terminales.[file:21][file:26]

Une seule reprise ancienne paraît exploitable : la logique de **composition produit explicite** issue du cadrage 1.6, qui insistait déjà sur une couche produit dérivée du runtime au lieu d'un front conversationnel passif.[file:26] Cette reprise renforce la doctrine 2.0 sans la contredire.[file:21][file:24]

Décision proposée : ne rien reprendre des anciennes maquettes ou formulations 1.5 ; se limiter à renforcer dans 2.1 l'idée d'un **adaptateur produit backend** stable vers UIState.[file:21][file:24][file:25]

### 8. Règles techniques transverses

La canonique 2.0 est déjà assez forte sur les non-régressions techniques : enrichissement additif, enums centralisées, `.value` pour Django, désérialisation explicite JSONB, pas d'usage brut d'objets JSON, UIState sans champs P0, analytics post-conversation, pas d'auto-upgrade du provisoire vers le validé humainement.[file:21] L'index documentaire qualifié et le cadrage 1.6 renforcent utilement l'importance de ces règles comme filtre de robustesse.[file:5][file:26]

Décision proposée : reprendre explicitement deux formulations de garde-fou dans la future doc de chantier :

- ne jamais considérer une vieille spec cible comme preuve de runtime observé ;[file:5]
- ne jamais transformer un besoin de précision technique en retour arrière doctrinal.[file:21][file:26]

### 9. Personae et couverture d’usage pour la validation 2.0

> Niveau de vérité – Personae 2.0  
> - Statut : CIBLE 2.0 (les personae sont un outil de validation de la cible, pas une description du runtime livré).  
> - Lecture : la galerie de personae sert à éprouver et couvrir la diversité des usages projetés ; elle ne doit pas être relue comme photographie de l’existant ni comme preuve d’implémentation.  
> - Dérivés : toute utilisation de ces personae doit rester compatible avec les invariants 2.0 (multi-postures, backend orchestré, UIState, mémoire gouvernée, confidentialité-first, partage explicite).

Les documents antérieurs et les cadrages AFEST fournissent déjà des éléments de contexte utilisateur, mais ils restent trop polarisés sur un seul usage (assistant réflexif AFEST) pour couvrir la cible Hugo 2.0. La cible 2.0 impose au contraire un moteur multi-postures, multi-rôles et multi-contextes, avec des interfaces distinctes pour apprenant, tuteur, formateur, coordinateur, ORGADMIN et superadministration technique.

Complément retenable :
- construire une galerie de personae 2.0 riche, structurée et documentée, couvrant l’ensemble des rôles et contextes visés (formation initiale, reconversion, montée en compétences, usages qualité, usages admin, usages techniques), destinée à la fois au design produit et à l’industrialisation des tests et audits ;
- utiliser ces personae comme base de scénarios systématiques de test (conversations, navigation UI, partage, évaluation, exports, gouvernance), sans les confondre avec des preuves de runtime livré.

Garde-fous :
- ne pas réimporter des formulations qui recadreraient Hugo comme simple assistant AFEST mono-posture ;
- ne pas faire des personae une nouvelle source de vérité qui contredirait la doctrine 2.0 ; ils servent à éprouver la cible, pas à la re-définir ;
- rattacher explicitement chaque persona aux invariants 2.0 (backend orchestré, P0 préservé, UIState côté front, mémoire gouvernée, confidentialité-first, partage explicite, validation humaine).

Décision proposée :
- produire une galerie canonique de personae Hugo 2.0 dans un document séparé, référencé par la spec canonique, structurée pour être réutilisable par les suites de tests, gabarits de d’évaluation UX et scripts d’audit automatique.

## Éléments anciens à ne pas réimporter

Les specs antérieures contiennent aussi des formulations désormais dangereuses si elles sont relues sans filtre.[file:5] Elles ne doivent pas compléter la 2.0, même si elles semblent détaillées.

### 1. Hugo comme simple assistant AFEST mono-posture

La version 1.5 et certains synopsis présentent Hugo comme assistant réflexif AFEST, centré sur une question à la fois, au sein d'une famille d'assistants dont Hugo & Cie est structurante.[file:25] Cette représentation est incompatible avec la doctrine 2.0, où Hugo cœur est un moteur tutoriel multi-postures piloté par état, et où Hugo & Cie relève d'extensions séparées du cœur.[file:21]

### 2. Le prompt comme source unique de vérité comportementale

Le cadrage 1.6 rappelait encore une hiérarchie où les prompts restaient un artefact central de comportement conversationnel.[file:26] Cette idée doit être **refondue** à la lumière de 2.0 : le prompt n'est plus la source de vérité comportementale, mais un composant de rendu gouverné par architecture, état, progression, mémoire et sécurité produit.[file:21]

### 3. Règle stricte « une question par message »

Les documents 1.5 la posaient comme contrainte structurante.[file:25] Elle est explicitement remplacée depuis le pivot 1.6 puis 2.0 par la règle “un seul micro-objectif de régulation par message”, avec possibilité de plusieurs questions brèves si elles restent cohérentes et sûres.[file:21][file:26]

### 4. Front passif ou quasi inchangé

Les anciennes couches produit étaient beaucoup plus faibles, voire debug-first.[file:25][file:26] Elles ne doivent pas être utilisées pour minimiser l'ambition UIState/front déjà fixée par la base 2.0 et par `specs-interface-2.0`.[file:21][file:24]

## Risques de régression ou de dérive

### Régression doctrinale

Le premier risque est de relire des specs anciennes comme si elles décrivaient encore le cadre produit courant.[file:5] Concrètement, cela ferait retomber Hugo vers un assistant réflexif mono-posture, centré AFEST uniquement, alors que les documents 2.0 ont déjà arbitré un moteur multi-postures à charpente commune.[file:21][file:22]

### Régression d'architecture

Le second risque est de re-survaloriser les prompts, ou d'importer des formulations où la conduite semblerait principalement portée par un SoT textuel.[file:26] La doctrine 2.0 impose au contraire une architecture orchestrée où P0, contrat de décision, progression, mémoire gouvernée, TutorPrompt et UIState coopèrent sans que le prompt devienne le pilote unique.[file:21]

### Régression produit

Le troisième risque est de minimiser le front 2.0 en se référant à des descriptions anciennes de POC ou de surfaces partielles.[file:25] Or l'interface apprenant, la lecture tuteur, la base formateur gouvernée et les états de synthèse/évaluation font désormais partie du périmètre cible consolidé.[file:21][file:23][file:24]

### Régression confidentialité

Le quatrième risque est de réintroduire, par excès de pragmatisme, du verbatim brut dans les logs, traces, exports, vues métier ou analytics.[file:26] Les documents compatibles convergent pourtant sur l'inverse : verbatim interne possible comme ressource gouvernée, mais jamais comme surface libre d'exposition ni comme mémoire principale.[file:21][file:26]

## Garde-fous à inscrire noir sur blanc

Pour éviter ces dérives, les chantiers 2.1 et “Hugo projet actuel” devraient intégrer explicitement les garde-fous suivants :

1. **Primauté des docs 2.0** : en cas de divergence, `spec_canonique_hugo_2_0` et ses trois annexes 2.0 arbitrent toujours.[file:21][file:22][file:23][file:24]
2. **Réutilisation secondaire des docs antérieurs** : un ancien document ne peut compléter qu'un point sous-spécifié, jamais redéfinir la doctrine.[file:5]
3. **Réécriture obligatoire** : tout élément repris d'une ancienne spec doit être reformulé en vocabulaire 2.0 avant intégration.[file:21][file:26]
4. **Test de non-régression doctrinale** : toute reprise doit répondre “oui” aux questions suivantes : multi-postures ? backend orchestré ? P0 intact ? UIState dérivé ? mémoire gouvernée ? confidentialité-first ? validation humaine maintenue ?[file:21][file:22][file:23][file:24]
5. **Aucune spéculation compensatoire** : si un point manque encore après croisement 2.0 + anciens docs compatibles, il reste ouvert et doit être explicitement demandé, pas inventé.[file:21][file:5]

## Ce que ce traitement permet réellement de compléter

Après relecture contrôlée des specs antérieures, les compléments robustes portent surtout sur :

- le **séquencement runtime** plus fin ;[file:26]
- la **hiérarchie de récupération du contexte** ;[file:21][file:26]
- la **forme de certains objets backend** pour mémoire et contradictions ;[file:26]
- le **niveau de détail des services** et des pré/postconditions ;[file:21][file:26]
- la préparation d'une future **liste de variables backend consommables par PromptRenderer**, sans encore écrire les prompts.[file:21][file:26]

En revanche, les anciens docs ne permettent pas de compléter proprement sans arbitrage neuf :

- les matrices d'entrée / maintien / sortie exhaustives par régime dans un formalisme final ;[file:22]
- le catalogue canonique des `ConversationQualitySignal` ;[file:23]
- la matrice détaillée rôles × permissions de validation ;[file:23][file:24]
- le pseudo-modèle complet de `UIState` et des payloads API ;[file:24]
- le rôle exact du tuteur dans la validation terminale des évaluations ;[file:23]
- le script conversationnel détaillé de l'orchestrateur formateur ;[file:23]
- le format canonique des traces d'évaluation, synthèses et exports structurés.[file:22][file:21]

**Note convergence locale (vague 3–4)** : pivot runtime `evaluation_trace_pivot_v1` pour exports encadrants ; **D9bis backend** (`ConversationTurnLLMAnalysis`, `ConversationLLMAnalysis`) livré en canal SUPERADMIN séparé — voir `cluster_dev_d9bis_observabilite_vague4_resultats.md`. Exposition produit analytics et dashboards restent **Couronne**.

## Questions restantes à trancher

Après ce traitement, les points qui demandent encore ton arbitrage explicite sont les suivants :

1. Veux-tu que la future 2.1 **intègre formellement** un objet métier de contradiction, ou seulement une logique de contradiction sans objet dédié ?[file:21][file:26]
2. Veux-tu figer dans la 2.1 une **matrice de récupération du contexte** quasi-algorithmique, ou garder cela pour une spec technique de chantier ?[file:21][file:26]
3. Souhaites-tu que la future spec “Hugo projet actuel” contienne déjà un **pseudo-schéma des objets backend** (ThemeMemory, EvaluationTrace, TrainerKnowledgeItem, ConversationQualitySignal, etc.) ou seulement des responsabilités fonctionnelles ?[file:21][file:23][file:26]
4. Sur le tuteur, veux-tu acter dès maintenant un rôle limité à **lecture + recommandation + validation de certaines traces**, ou ouvrir la possibilité qu'il valide aussi certaines évaluations terminales ?[file:23][file:24]
5. Sur l'API d'état, veux-tu aller jusqu'à un **contrat quasi-JSON** dans la prochaine étape, ou rester au niveau des champs obligatoires et invariants de lecture ?[file:21][file:24]
6. Pour l'orchestrateur formateur, veux-tu qu'on pousse maintenant un **workflow détaillé par sections de questionnaire**, ou qu'on le laisse explicitement sous-spécifié jusqu'au chantier dédié ?[file:23]
7. Veux-tu que la prochaine étape contienne déjà le **récapitulatif des variables backend à disposition des futurs prompts**, ou qu'on le réserve au moment où l'architecture 2.1 sera figée ?[file:21][file:26]
