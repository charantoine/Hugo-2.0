
## 1. Orchestrateur formateur

### Bloc F1 — Objectif conversationnel et finalité métier

- **Source** : Contextualisation 1.9, section LOT 5 — Base de connaissances formateur.[^1]
- **Extrait** : Finalité : “permettre au formateur d’uploader des documents, d’éliciter des connaissances, puis de les structurer dans une base de connaissance exploitable par Hugo avec validation humaine”.[^1]
- **Domaine** : orchestrateur formateur.
- **Ce que ça précise** :
    - **Objectif conversationnel** : amener le formateur à expliciter et structurer son savoir métier (documents, règles, critères, erreurs fréquentes, raisonnements attendus/à éviter).[^2][^1]
    - **Finalité métier** : produire une base de connaissances gouvernée, exploitable par les orchestrateurs apprenant (révision, évaluation, réflexif), sans se substituer à la vérité réglementaire ni à la validation humaine.[^1]

***

### Bloc F2 — Structure de dialogue et matériaux manipulés

- **Source** : Contextualisation 1.9 (LOT 5), Contexte/extraction précédente sur interface formateur.[^2][^1]
- **Extrait** : Ajouts : `TrainerKnowledgeItem`, `documentingestor.py`, “questionnaire dialogique formateur”, “vues trainer”, validation humaine explicite.[^1]
- **Domaine** : orchestrateur formateur.
- **Ce que ça précise** :
    - **Structure de dialogue** :
        - un **questionnaire dialogique** où Hugo pose des questions au formateur pour qu’il explicite contenus, critères, erreurs, raisonnements ;
        - ingestion de documents (upload) puis transformation en items structurés (via documentingestor + orchestrateur).[^2][^1]
    - **Matériaux manipulés** :
        - documents source ;
        - critères de maîtrise ;
        - erreurs fréquentes ;
        - raisonnements attendus / à éviter ;
        - éléments de référentiel (compétences, situations, tâches) ;
        - entrées/sorties destinées au RAG (chunks, meta) ;
        - statuts `KnowledgeItemStatus` (declared, derived_provisional, validated_trainer).[^2][^1]
- **Ambiguïté** : la séquence exacte des questions (ordre du questionnaire, relances, reprises) n’est pas décrite en détail.[^2]
- **Lecture à privilégier** : orchestrateur formateur comme **dialogue d’élaboration** (pas simple formulaire), avec ingestion documentaire et explicitations guidées.[^1][^2]
- **Ce qu’il manque pour finaliser la spec** :
    - script conversationnel plus précis (ou au moins une liste de sections/questions types) ;
    - règles de relance quand le formateur reste vague, incohérent ou incomplet.

***

### Bloc F3 — Règles de validation, objets produits, impact sur système apprenant

- **Source** : Contextualisation 1.9 (LOT 5, règles fortes), bloc 10 et 11 du Contexte.[^2][^1]
- **Extrait** :
    - “rien ne doit passer `validated_trainer` sans validation humaine” ;
    - la base de connaissance n’est pas la source primaire de vérité réglementaire ;
    - distinction declared / derived_provisional / validated_trainer ;
    - les objets intermédiaires incluent `TrainerKnowledgeItem`, referentiel, memory-summary, synthesisservice, etc.[^1][^2]
- **Domaine** : orchestrateur formateur + validation humaine.
- **Ce que ça précise** :
    - **Règles de validation** :
        - chaque item dérivé (résumé, règle, critère, erreur type) doit rester en `derived_provisional` jusqu’à validation explicite par un humain (formateur ou instance responsable) ;
        - aucun auto‑upgrade vers `validated_trainer`;
        - la base formateur reste subordonnée au référentiel métier primaire.[^1]
    - **Objets produits** :
        - items de connaissance structurés, avec contenu texte, type (règle, critère, erreur), liens référentiel, statut ;
        - corpus RAG “formateur” validé, consommable par orchestrateurs ;
        - éventuellement capsules (explications, exemples) prêtes à être utilisées.[^2][^1]
    - **Effets sur système apprenant** :
        - enrichit les appuis fiables pour révision/évaluation ;
        - permet des ajustements plus fins des feedbacks apprenant ;
        - ne change pas la logique P0, mais influence ce que `userag`/`useoverlayfirst` peuvent exploiter.[^2][^1]
- **Ambiguïté** : attribution exacte du rôle de validation (formateur vs coordo vs orgadmin) n’est pas tranchée dans ce fil.[^1][^2]
- **Lecture à privilégier** :
    - orchestrateur formateur **prépare et propose** des items ;
    - validation humaine peut être par formateur lui‑même ou par autre rôle habilité (défini au niveau produit).[^1]
- **Ce qu’il manque pour finaliser la spec** :
    - matrice claire rôle → actions de validation ;
    - modèle JSON complet de `TrainerKnowledgeItem`.

***

### Bloc F4 — Ce que l’orchestrateur lit / crée / propose / fait valider

- **Source** : LOT 5 + bloc 10–11 contexte.[^2][^1]
- **Extrait** : base formateur interagit avec mémoire gouvernée, référentiel, RAG, exports ; items ont plusieurs statuts ; consolidation post‑conversation pour mémoire thématique, etc.[^2][^1]
- **Domaine** : orchestrateur formateur.
- **Ce que ça précise** :
    - **Lit** :
        - documents sources ;
        - référentiel (compétences, situations) pour ancrer les items ;
        - éventuellement traces d’usage de contenus (mais pas verbatim privé non partagé).[^1][^2]
    - **Crée** :
        - items de connaissance structurés (TrainerKnowledgeItem) ;
        - métadonnées RAG (chunks, tags, liens référentiel) ;
        - propositions de critères et erreurs fréquentes.[^2][^1]
    - **Propose** :
        - reformulations plus claires ;
        - regroupements ;
        - hiérarchisations ;
        - suggestions de liens avec référentiel ou situations types.[^2]
    - **Fait valider** :
        - chaque item ou groupe d’items via des écrans/états de validation (tableau de validation, workflow de statut).[^1][^2]
    - **Interaction mémoire / référentiel / RAG / exports** :
        - base formateur alimente un RAG gouverné, consultable par orchestrateurs apprenant ;
        - certains éléments peuvent se retrouver dans des exports (base, preuves d’ingénierie pédagogique).[^1][^2]
- **Ambiguïté** : on ne sait pas si l’orchestrateur formateur peut lui‑même déclencher des mises à jour de mémoire thématique apprenant (il n’y a pas de lien explicite dans ce fil).[^2][^1]
- **Lecture à privilégier** :
    - orchestrateur formateur agit **en amont** du parcours apprenant, sur la qualité et la structure du matériau, pas sur les traces individuelles de séance.[^1][^2]
- **Ce qu’il manque pour finaliser la spec** :
    - description d’un éventuel lien “formateur → calibration de mémoire thématique” ;
    - schéma de flux des données entre base formateur, mémoire apprentissage, et exports.

***

## 2. Orchestrateur tuteur

### Bloc T1 — Objectif conversationnel et finalité d’accompagnement

- **Source** : Contextualisation 1.9 (rôles, observabilité/cohorte LOT 6), Contexte bloc 10 (interface formateur/tuteur).[^2][^1]
- **Extrait** :
    - Rôles : LEARNER, TUTOR, TRAINER, COORDO, ORGADMIN, SUPERADMIN ; webapp unique, desktop‑first côté tuteur ; tuteur lit les traces partageables, la progression, diagnostics, etc.[^1][^2]
    - LOT 6 ajoute `ConversationQualitySignal`, `qualitytracker.py`, `analytics/cohortdashboard.py`.[^1]
- **Domaine** : orchestrateur tuteur.
- **Ce que ça précise** :
    - **Objectif conversationnel** : aider le tuteur à lire la progression des apprenants, repérer besoins/difficultés/blocages, et préparer des actions d’accompagnement humain (aménagements de situations de travail, choix de focus, etc.).[^2][^1]
    - **Finalité d’accompagnement** : soutenir la pratique tutorale, non la remplacer ; fournir des signaux qualitativement exploitables, pas un scoring opaque.[^2][^1]

***

### Bloc T2 — Nature des signaux suivis, lecture des besoins / difficultés

- **Source** : LOT 1 (ConversationProgress), LOT 6 (ConversationQualitySignal), contextualisation sur observabilité/cohorte.[^1]
- **Extrait** :
    - ConversationProgress calcule maturité globale, branches actives, priority_branch, dispersion_risk, éligibilité synthèse/évaluation, missing_for_next_level, reasoncodes.[^1]
    - LOT 6 prévoit des signaux de qualité conversationnelle et des metrics cohorte.[^1]
- **Domaine** : orchestrateur tuteur.
- **Ce que ça précise** :
    - **Signaux suivis** :
        - progression par branche ;
        - maturité (RED/ORANGE/GREEN) ;
        - dispersion_risk ;
        - motifs d’alerte (reasoncodes : p.ex. “clarification manquante”, “boucle”, etc.) ;
        - dans LOT 6, signaux de qualité de conversation (fréquence de micro‑explications, longueur de réponses, temps passé, etc. — suggéré, pas listé).[^1]
    - **Lecture des besoins / blocages** :
        - blocage si maturité stagne, dispersion_risk élevé, répétition de reasoncodes “clarification low” ;
        - besoin de soutien si signaux de charge ou de risque relationnel fréquents ;
        - besoin de bûchage si la progression sur certains contenus reste en retard.[^2][^1]
- **Ambiguïté** : détail exact des `ConversationQualitySignal` non donné (liste des signaux), donc la lecture reste qualitative.[^1]
- **Lecture à privilégier** : orchestrateur tuteur exploite ces signaux pour **proposer des interprétations** au tuteur humain (apprenant à tel endroit, dispersion à tel moment), pas pour prendre des décisions à sa place.[^2][^1]
- **Ce qu’il manque pour finaliser la spec** :
    - liste canonique des signaux de qualité avec définitions ;
    - mapping explicite “signal → recommandation type”.

***

### Bloc T3 — Suggestions d’aménagement du travail, rôle dans synthèse/évaluation, limites

- **Source** : Contexte bloc 10 (interface formateur/tuteur), contextualisation (observabilité, preuves, exports).[^2][^1]
- **Extrait** : le tuteur doit pouvoir lire la progression, les traces partageables, recevoir de l’aide à l’interprétation, et utiliser ces informations pour adapter les situations de travail ou l’accompagnement ; la confidentialité impose qu’il ne voie que ce qui est explicitement partagé.[^2][^1]
- **Domaine** : orchestrateur tuteur + validation humaine.
- **Ce que ça précise** :
    - **Suggestions** :
        - aménagements de situations de travail (donner plus de temps sur tel type de tâche, proposer d’autres situations, organiser un debrief ciblé) ;
        - indications sur moments pertinents pour proposer une synthèse ou une évaluation (séance mûre, signaux positifs).[^2][^1]
    - **Rôle dans synthèse/évaluation** :
        - peut recommander une synthèse ou une évaluation quand les signaux le justifient ;
        - peut valider la mise en circulation de certaines synthèses comme preuves ou traces partagées ;
        - n’a pas, dans ce fil, le pouvoir de déclencher unilatéralement une évaluation automatique sur l’apprenant.[^1][^2]
    - **Limites strictes** :
        - pas d’accès au verbatim non partagé ;
        - pas de pilotage direct du moteur de conversation (pas de modification de P0, pas de forcing d’orchestrateur apprenant au niveau serveur) ;
        - agit par recommandations, validations de traces et aménagements dans la réalité de travail.[^2][^1]
- **Ambiguïté** : ce fil ne précise pas si le tuteur peut, via l’UI, demander explicitement une bascule de mode (par ex. suggérer à l’apprenant de passer en révision).[^2]
- **Lecture à privilégier** :
    - tuteur recommande, apprenant et système acceptent ou non dans le cadre des garde‑fous P0 ;
    - l’orchestrateur tuteur produit surtout des **vues et messages d’aide au jugement humain**.[^1][^2]
- **Ce qu’il manque pour finaliser la spec** :
    - description d’actions UI explicites côté tuteur (boutons “suggérer bascule”, “recommander synthèse”) ;
    - statut du tuteur dans le workflow de validation des évaluations (peut‑il valider des évaluations ou seulement les lire ?).

***

## 3. Interfaces formateur \& tuteur (rappel ciblé)

### Bloc IF1 — Surface formateur : vues et actions

- **Source** : LOT 5 + Contexte bloc 10–11.[^1][^2]
- **Domaine** : interface formateur.
- **Surface concernée** :
    - “vues trainer”, questionnaire dialogique, tableau de validation, vue de lecture pédagogique, éventuellement panneau de configuration bornée.[^2][^1]
- **Éléments visibles** :
    - liste de documents ;
    - liste d’items de connaissance avec statut (declared / derived_provisional / validated) ;
    - champs de description, critère, erreur type, lien référentiel ;
    - état de validation, responsable, date ;
    - éventuellement aperçu de la manière dont ces items sont utilisés dans les conversations (usage stats).[^1][^2]
- **Actions autorisées** :
    - uploader ;
    - répondre au questionnaire ;
    - créer/modifier des items ;
    - valider/rejeter/corriger ;
    - rattacher au référentiel ;
    - exporter.[^2][^1]
- **États UI** :
    - items en attente ;
    - items validés ;
    - items rejetés ;
    - items en cours de révision.[^1][^2]
- **Limites** :
    - pas d’édition de la doctrine centrale (P0, SoT, architecture) ;
    - accès limité au contenu apprenant (seulement ce qui est explicitement partagé comme traces ou exemples anonymisés).[^2][^1]

***

### Bloc IT1 — Surface tuteur : vues et actions

- **Source** : LOT 1, LOT 6, Contexte bloc 10–12.[^1][^2]
- **Domaine** : interface tuteur.
- **Surface concernée** :
    - tableaux ou dashboards de progression ;
    - vues de cohorte et de conversation (cohortdashboard, analytics) ;
    - écrans de détails pour un apprenant particulier, montrant progression, synthèses, évaluations.[^2][^1]
- **Éléments visibles** :
    - état de séance (scène) ;
    - mode courant (posture) si exposé ;
    - maturité ;
    - progression par branche ;
    - signaux de dispersion, de qualité ;
    - synthèses partagées ;
    - traces d’évaluation partageables.[^1][^2]
- **Actions autorisées** :
    - lire et commenter les traces ;
    - préparer des recommandations d’accompagnement ;
    - éventuellement marquer des cas à suivre ou à approfondir ;
    - lancer des exports dédiés (pack Qualiopi lite).[^2][^1]
- **États UI** :
    - apprenant sans traces ;
    - apprenant avec progression “normale” ;
    - apprenant signalé (blocage, dispersion, surcharge) ;
    - cohorte avec indicateurs agrégés.[^1][^2]
- **Limites** :
    - aucun accès libre au verbatim non partagé ;
    - pas de contrôle direct sur le moteur : il ne peut pas changer P0 ni forcer les orchestrateurs ; il agit via accompagnement humain, recommandations, validations de traces.[^2][^1]

***

## Synthèse Tour 3 — B. Orchestrateur formateur

### Ce que le fil permet de fixer

- Orchestrateur dédié, distinct des modes apprenant, centré sur **élaboration du savoir métier** (documents, critères, erreurs, raisonnements).[^1][^2]
- Fonctionne via un **questionnaire dialogique** + ingestion documentaire (documentingestor), produisant des `TrainerKnowledgeItem` structurés.[^1]
- Repose sur une **validation humaine stricte** (pas d’auto‑upgrade vers `validated_trainer`), et ne remplace pas le référentiel professionnel primaire.[^2][^1]
- Impacte les orchestrateurs apprenant via un **RAG gouverné** et des contenus validés, sans toucher au noyau P0 ni à la doctrine de conduite.[^2][^1]


### Ce qui reste à préciser

- Script conversationnel détaillé (sections, types de questions, relances).
- Workflow UI complet : ordre des écrans, visualisation de l’impact des connaissances sur les parcours apprenants.
- Répartition précise des responsabilités de validation (formateur vs coordo vs orgadmin).

***

## Synthèse Tour 3 — C. Orchestrateur tuteur

### Ce que le fil permet de fixer

- Orchestrateur propre, orienté **lecture de progression**, suivi des besoins/difficultés/blocages, et **propositions d’accompagnement** (aménagement de situations de travail, rythme, etc.).[^1][^2]
- Consomme `ConversationProgress`, `ConversationQualitySignal` et autres signaux pour produire des vues cohorte et apprenant, sans exposer P0 brut ni verbatim privé.[^2][^1]
- Permet au tuteur de **recommander synthèses/évaluations** et de valider certaines traces comme partageables, dans le respect strict de la confidentialité.[^1][^2]


### Ce qui reste à préciser

- Catalogue canonique des signaux de qualité et mapping signal → recommandation.
- Actions UI explicites (boutons, commandes) pour exprimer recommandations et aménagements.
- Rôle exact du tuteur dans la **validation d’évaluations** (lecture seule vs pouvoir de promotion/statut).

***

Si tu veux, on peut maintenant faire un dernier tour “Contrat orchestrateur / P0 / interface / validation humaine”, en consolidant les quatre orchestrateurs + trois surfaces dans un tableau unique de responsabilités.
<span style="display:none">[^3]</span>

<div align="center">⁂</div>

[^1]: CONTEXTUALISATION_COMPLETE_HUGO_1_9.md

[^2]: Contexte_Ce-fil-contient-des-elements-de-conceptio.md

[^3]: LOT3_multi_postures_cursor-2.md

