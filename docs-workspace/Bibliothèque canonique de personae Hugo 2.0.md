# Bibliothèque canonique de personae Hugo 2.0

> **Doctrine de lecture.** Ce document distingue systématiquement : **réel observé** (audits 00–10), **cible spécifiée** (spec canonique 2.0 + compléments), **écarts confirmés** (fichiers `ecarts—*.md`), **zones à vérifier** (AVERIFIER), **hypothèses** (inféré fort / hypothèse). Aucune spec cible n'est présentée comme preuve d'une fonctionnalité livrée.

***

## PARTIE I — INVENTAIRE DES FRAGMENTS EXPLOITABLES

### 1. Taxonomie des rôles produit (source : spec canonique 2.0, specs interface 2.0)

Les rôles minimaux fixés par la cible 2.0 sont : **LEARNER, TUTOR, TRAINER, COORDO, ORGADMIN, SUPERADMIN**. À ces rôles s'ajoutent des rôles transverses : **auditeur qualité** (usage Qualiopi lite), **testeur/back-office** (surfaces de démo), **développeur** (superadmin technique).[^1][^2]

La spec canonique distingue explicitement ce que chaque rôle voit, peut faire, et ne voit pas. Le réel audité montre une couverture partielle : le parcours apprenant est le plus démontré, les surfaces formateur et tuteur existent mais restent partiellement back-office, le rôle coordinateur est **ABSENT NOUVEAU CONTRAT** dans le réel observable.[^2][^3]

### 2. Fragments sur l'apprenant (sources : specs orchestrateurs diagnostic 2.0, spec canonique, runtime démo)

| Fragment | Source | Niveau de preuve |
|---|---|---|
| Postures : réflexif, diagnostic, révision de savoirs, évaluation facultative | specs-Orchestrateur-diagnostic-2.0.md | Explicite cible 2.0 |
| Progression RED/ORANGE/GREEN, branches actives, dispersionRisk, reasoncodes | specs-Orchestrateur-diagnostic-2.0.md | Explicite cible 2.0 |
| P0 pilote : charge cognitive, risque interactionnel, ZPD, clarté épisode | specs-Orchestrateur-diagnostic-2.0.md | Explicite cible 2.0 |
| Apprenant ne voit pas P0 brut, prompts complets, verbatim interne non partagé | spec_canonique_hugo_2_0.md | Explicite cible 2.0 |
| L'apprenant peut déclencher synthèse/évaluation si éligible (UIState) | spec_canonique_hugo_2_0.md | Explicite cible 2.0 |
| UIState dérivé d'états backend : scène, quête, maturité, CTA terminales | specs-interface-2.0.md | Explicite cible 2.0 |
| Sélection de posture possible en début de séance (PATCH posture) | specs-Orchestrateur-diagnostic-2.0.md | Cible 2.0 — AVERIFIER réel |
| Intercalaires pédagogiques (notion, contraste) préparés entre tours | dernier-run-intercallaire.docx | Cible V1, contrat en cours |
| Mémoire thématique LearnerThemeMemory inter-sessions, résumée, sans verbatim brut | spec_canonique_hugo_2_0.md | Explicite cible 2.0 |

L'apprenant type du corpus est situé en **situation professionnelle réelle** — il décrit une expérience de travail, l'analyse, la révise ou s'évalue dessus. La spec diagnostic fixe : « mission — aider l'apprenant explorer une situation professionnelle, identifier ce qui s'est passé, cartographier les causes possibles ». Il n'est pas contraint à l'AFEST : toute situation de travail réelle est valide.[^4][^5]

### 3. Fragments sur le tuteur (sources : specs-formateur-tuteur-2.0.md, spec canonique)

| Fragment | Source | Niveau de preuve |
|---|---|---|
| Lit progression, blocages, traces partagées, synthèses, signaux cohorte | specs-formateur-tuteur-2.0.md | Explicite cible 2.0 |
| Peut recommander synthèse/évaluation, commenter, valider traces partageables | specs-formateur-tuteur-2.0.md | Explicite cible 2.0 |
| Pas d'accès verbatim non partagé, pas de contrôle direct P0 | specs-formateur-tuteur-2.0.md | Explicite cible 2.0 |
| ConversationQualitySignal, analyticsCohortDashboard (LOT 6) | specs-formateur-tuteur-2.0.md | Cible 2.0 — AVERIFIER réel |
| Statut exact tuteur dans validation des évaluations (lecture seule vs promotion) | specs-formateur-tuteur-2.0.md | Zone ouverte |
| Surface desktop-first, webapp unique | specs-formateur-tuteur-2.0.md | Explicite cible 2.0 |

### 4. Fragments sur le formateur (sources : specs-formateur-tuteur-2.0.md, ecarts-40, ecarts-50)

| Fragment | Source | Niveau de preuve |
|---|---|---|
| Orchestre la base de connaissances via questionnaire dialogique | specs-formateur-tuteur-2.0.md | Explicite cible 2.0 |
| TrainerKnowledgeItem : déclaré, dérivé provisoire, validé humainement | ecarts-40_base_connaissances_formateur.md | ALIGNÉ réel/cible |
| DocumentIngestor transforme docs en items structurés | ecarts-50_orchestrateur_formateur.md | ALIGNÉ DOC PARTIEL |
| Upload, édition, validation, rattachement référentiel, export | specs-formateur-tuteur-2.0.md | Explicite cible 2.0 |
| Pas d'accès libre au contenu apprenant non partagé | spec_canonique_hugo_2_0.md | Explicite cible 2.0 |
| Script conversationnel détaillé et chorgraphie UI fine | specs-formateur-tuteur-2.0.md | Zone ouverte — AVERIFIER |
| Rôle exact de validation : formateur vs coordo vs orgadmin | ecarts-50_orchestrateur_formateur.md | Zone ouverte |

### 5. Fragments sur l'ORGADMIN (sources : specs-interface-2.0.md, ecarts-90)

| Fragment | Source | Niveau de preuve |
|---|---|---|
| Gestion création/édition utilisateurs rattachés à l'organisation | specs-interface-2.0.md | ALIGNÉ DOC PARTIEL réel |
| Exports filtrés par tenant (CSV/JSON), déclenchement pack Qualiopi lite | specs-interface-2.0.md | Cible 2.0 — AVERIFIER réel complet |
| Pas de lecture libre verbatim apprenant non partagé | ecarts-90_confidentialite_partage_multitenant_roles.md | Explicite cible 2.0 |
| Multi-tenant strict, RLS Postgres active | ecarts-90_confidentialite_partage_multitenant_roles.md | Cible ferme — AVERIFIER prod |
| Suppression de comptes non visible dans le réel audité | specs-interface-2.0.md | AVERIFIER |
| Indicateurs agrégés (volumes sessions, synthèse/évaluation) sans P0 brut | specs-interface-2.0.md | Cible 2.0 |

### 6. Fragments sur le superadmin technique (sources : specs-interface-2.0.md, spec canonique)

| Fragment | Source | Niveau de preuve |
|---|---|---|
| Pilotage borné des orchestrateurs (profils, curseurs, seuils) | specs-interface-2.0.md | Cible 2.0 — non livré réel |
| Export debug complet d'une conversation en Markdown (hors prod multitenant) | specs-interface-2.0.md | Cible 2.0 |
| Pas de droit applicatif libre sur contenu apprenant | specs-interface-2.0.md | Explicite cible 2.0 |
| Surfaces distinctes des vues apprenant, formateur, tuteur, ORGADMIN | specs-interface-2.0.md | Explicite cible 2.0 |

### 7. Fragments sur les exports / auditeur qualité (sources : ecarts-100, spec canonique)

| Fragment | Source | Niveau de preuve |
|---|---|---|
| Trace, Evidence, EvidenceBundleView comme objets réels observés | ecarts-100_exports_preuves_qualiopi_lite.md | ALIGNÉ réel |
| Bundle Qualiopi lite : ZIP CSV/JSON + validations + preuves + audit log filtré | ecarts-100_exports_preuves_qualiopi_lite.md | POC historique — AVERIFIER richesse réelle |
| Suppression EXIF par défaut, GPS opt-in | ecarts-100_exports_preuves_qualiopi_lite.md | ALIGNÉ réel et cible |
| Le bundle n'est pas certifiant : aide à l'audit, pas acte de certification | ecarts-100_exports_preuves_qualiopi_lite.md | Explicite cible 2.0 |
| Permissions fines par rôle sur téléchargement/consultation — AVERIFIER | ecarts-100_exports_preuves_qualiopi_lite.md | AVERIFIER |

***

## PARTIE II — TENSIONS STRUCTURANTES REPÉRÉES

Les tensions suivantes traversent le corpus et conditionnent la construction des personae :[^6][^5][^3][^4]

1. **Novice vs expert métier** : un apprenti BTP vs un salarié expérimenté en reconversion ; le moteur doit adapter ZPD, microexplication, directivité.
2. **Jeune en alternance vs adulte en reconversion** : rapport différent à l'explicitation, au temps, à la preuve, à la validation.
3. **Faible vs forte aisance numérique** : l'apprenant peu à l'aise avec le numérique a besoin d'une UI dérivée d'états clairs, sans jargon technique exposé.
4. **Usage individuel vs organisationnel** : un apprenant isolé vs une cohorte suivie par un tuteur entreprise dans un OF multi-tenant.
5. **Posture réflexive vs révision de savoirs vs diagnostic** : le moteur est multi-postures ; un persona ne correspond pas à une seule posture.
6. **Surface apprenant vs surface encadrants** : le formateur et le tuteur ne pilotent pas la conversation mais lisent des projections filtrées.
7. **Usage métier vs audit/qualité** : l'ORGADMIN et l'auditeur Qualiopi n'interagissent pas avec Hugo de la même façon qu'un apprenant.
8. **Confidentialité forte vs besoin de partage** : tension entre verbatim priv par défaut et besoins de traçabilité / preuve Qualiopi.

***

## PARTIE III — BIAIS HISTORIQUES À CORRIGER

| Biais | Description | Correction dans la galerie |
|---|---|---|
| **AFEST-centrisme** | Réduire Hugo à un outil AFEST único, séquences de situations de travail analysées | Hugo sert toute situation professionnelle réelle : alternance, CFA, GRETA, OF, reconversion, tutorat, bilan |
| **Mono-posture réflexive** | Traiter Hugo comme un chatbot réflexif unique | La galerie couvre les 4 postures (réflexif, diagnostic, révision, évaluation) et leurs combinaisons |
| **Survalorisation du verbatim** | Confondre le verbatim interne avec la mémoire principale | La mémoire est thématique, résumée, gouvernée ; le verbatim est priv et ponctuel |
| **Confusion front / moteur** | Croire que l'UI pilote la décision tutorale | Le moteur reste backend Django orchestré ; le front consomme UIState |
| **Confusion cible / livré** | Présenter une spec 2.0 comme preuve d'une fonctionnalité déjà livrée | Chaque persona indique le niveau de preuve de chaque scénario |
| **Réduction à l'apprenant** | Ne construire des personae que pour les apprenants | La galerie couvre 6 rôles distincts avec leurs surfaces propres |

***

## PARTIE IV — TROUS DOCUMENTAIRES RESTANTS

Les éléments suivants ne sont pas suffisamment documentés dans le corpus pour être couverts sans hypothèse forte :[^7][^3][^8][^6]

- **Coordinateur (COORDO)** : rôle doctrinal cible, ABSENT NOUVEAU CONTRAT dans le réel observable. Aucune surface stabilisée. La galerie le traite comme **hypothèse crédible**.
- **Script conversationnel détaillé de l'orchestrateur formateur** : l'ordre des sections, les relances, la chorgraphie fine restent ouverts.
- **Matrice précise des rôles de validation** (formateur vs coordo vs orgadmin) : non tranchée dans le corpus.
- **Catalogue canonique des ConversationQualitySignal** (LOT 6) : non listé précisément.
- **RLS Postgres effective en prod** : tests sur SQLite localement, pas de preuve runtime distant.
- **Richesse réelle des traces locales** : generate-trace local produit un payload minimal ; certains exports peuvent être moins riches qu'attendu.
- **Parcours tuteur complet bout en bout** : surfaces partielles, pas de démonstration complète.

***

## PARTIE V — GALERIE CANONIQUE DES PERSONAE HUGO 2.0

***

### PERSONA A1 — APPRENANT CŒUR : Karim, apprenti en alternance

**Noyau stable**

| Champ | Valeur |
|---|---|
| **Identité synthétique** | Karim, 20 ans, apprenti électricien en 2e année de CAP/BTS, alternance entreprise + CFA |
| **Contexte** | Rentre de sa semaine en entreprise, a vécu une situation de chantier qui l'a bloqué (câblage d'une armoire, il n'a pas su interpréter le schéma) |
| **Objectif** | Comprendre ce qui s'est passé, progresser sur la lecture de schémas, préparer les situations futures |
| **Irritants** | Relances trop abstraites ("qu'as-tu appris ?"), manque de retour concret, impression que l'outil "ne comprend pas le métier" |
| **Contraintes** | Peu de temps (entre deux séances), téléphone ou ordi en centre, connexion parfois instable |
| **Rôle produit** | LEARNER |
| **Attentes de confidentialité** | Ne veut pas que son tuteur d'entreprise voie ce qu'il dit de ses erreurs sans qu'il l'ait décidé |

**Modules de variation**

| Module | Valeur nominale | Variantes disponibles |
|---|---|---|
| Niveau de langage | Oral, direct, phrases courtes, vocabulaire métier basique | Soutenu (lycée général) / très familier |
| Niveau numérique | Moyen (smartphone aisé, ordi occasionnel) | Faible (débutant) / fort (gameur) |
| Autonomie | Faible (attend qu'on lui dise quoi faire) | Moyenne / forte (initiative) |
| Rapport à l'évaluation | Anxieux (peur du jugement) | Neutre / demandeur |
| Rapport au partage | Méfiant (ne veut pas exposer ses lacunes) | Ouvert si confiance établie |
| Sensibilité à la preuve | Faible (ne pense pas en termes de traces) | Forte (comprend l'enjeu portfolio) |
| Technicité métier | Débutant BTP | Expert / reconversion / tertiaire |
| Rapport à l'explicitation | Difficile (ne trouve pas les mots) | Fluide |

**Comportements conversationnels typiques**
- « Je sais pas trop comment expliquer… on était sur le chantier et… »
- Répond par oui/non si la question est trop ouverte
- Se décourage si Hugo pose deux questions en même temps
- Reprend confiance si Hugo reformule ce qu'il a dit (geste `reassure`)
- A tendance à switcher de sujet si un blocage dure trop longtemps (dispersionRisk élevé)

**Attentes UI**
- Scène de séance claire ("on est en train d'explorer ta situation")
- Maturité visible mais non anxiogène (barre discrète, pas de note)
- Bouton synthèse accessible quand éligible, grisé avec explication sinon
- Aucun jargon technique exposé (reasoncodes, P0, branches…)
- Interface réactive, pas de temps d'attente anxiogène

**Scénarios de conversation à jouer**
1. Séance 1 — Diagnostic : situation floue, épisode peu clair. Hugo doit clarifier avant d'analyser. Attente : 1 question par tour, pas de verdict.
2. Séance 2 — Réflexif : problème nommé, causes identifiées. Hugo aide à formuler ce qui a été appris.
3. Séance 3 — Révision de savoirs : Karim veut tester sa compréhension des schémas. Hugo pose des défis, microexplications courtes.
4. Séance 4 — Évaluation facultative : maturité verte, charge faible. Hugo propose l'évaluation, Karim accepte.

**Scénarios de navigation UI**
- Ouverture de session → sélection de posture possible en début de séance
- Mid-session : maturité passe ORANGE → GREEN, bouton synthèse s'active
- Tentative d'évaluation hors éligibilité → message bloquant explicatif

**Scénarios de partage / export / validation**
- Karim partage une synthèse avec son tuteur d'entreprise (action explicite)
- Karim refuse de partager le verbatim → vérifié : le tuteur ne voit que la synthèse partagée
- Karim génère une preuve photo d'une réalisation (EXIF supprimés, GPS opt-in)

**Cas limites et anti-cas**
- Anti-cas : Karim arrive avec "j'ai rien à dire aujourd'hui" → Hugo doit gérer episodeClarity low sans boucle absurde
- Cas limite : dispersionRisk très élevé, Hugo doit recentrer sans forcer
- Anti-cas : Hugo fait cours magistral → INTERDIT (reasonCode `magistral_detected`)

**Critères d'oracle pour audit automatique**
- P0 ne double pas les questions si `cognitiveLoad` élevé
- `UIState` ne contient aucun champ P0 brut
- Synthèse non accessible si `optionalEvaluationEligible = false`
- Verbatim non partagé invisible en vue tuteur
- Posture active visible dans UIState si exposée

**Niveau de preuve** : Noyau — explicite cible 2.0. Modules variation — inférés forts sur base de spec P0 et orchestrateurs.

***

### PERSONA A2 — APPRENANT ADULTE EN RECONVERSION : Nadège, aide-soignante se reconvertissant en infirmière

**Noyau stable**

| Champ | Valeur |
|---|---|
| **Identité synthétique** | Nadège, 38 ans, aide-soignante, en formation en alternance pour devenir infirmière, région rurale |
| **Contexte** | Reprend des études après 12 ans de terrain. Connaissance métier forte, lacunes théoriques réglementaires importantes |
| **Objectif** | Consolider les contenus réglementaires (décrets, protocoles), articuler savoir pratique et savoirs formels |
| **Irritants** | Sentiment d'être traitée comme une débutante alors qu'elle a de l'expérience, exercices trop scolaires |
| **Contraintes** | Temps très contraint (famille, trajets), uniquement sur mobile le soir, peut être fatiguée |
| **Rôle produit** | LEARNER |
| **Attentes de confidentialité** | Ne veut absolument pas que ses collègues ou sa hiérarchie voient ses difficultés |

**Modules de variation**

| Module | Valeur nominale | Variantes |
|---|---|---|
| Niveau de langage | Professionnel, argot soignant, parfois manque vocab théorique | Académique / très familier |
| Niveau numérique | Moyen-faible (smartphone, pas ordi) | Fort |
| Autonomie | Forte dans le métier, faible dans le cadre scolaire | Variable selon le sujet |
| Rapport à l'évaluation | Ambivalent (veut prouver, craint l'échec) | Demandeur / réticent |
| Rapport au partage | Très réservé | Ouvert avec le tuteur de formation uniquement |
| Sensibilité à la preuve | Forte (comprend l'enjeu diplôme) | — |
| Technicité métier | Élevée pratique, faible théorie réglementaire | — |
| Rapport à l'explicitation | Facile sur le pratique, difficile sur le réglementaire | — |

**Comportements conversationnels typiques**
- « En pratique on fait jamais comme ça dans le service, mais le texte dit… »
- Résiste aux relances trop théoriques, répond mieux aux questions ancrées dans ses situations réelles
- Utilise l'orchestrateur de révision pour les protocoles réglementaires
- Peut tester Hugo sur un contenu qu'elle maîtrise ("dis voir si tu sais ça toi aussi")

**Scénarios de test prioritaires**
1. Révision de savoirs sur un protocole réglementaire : Hugo doit pouvoir s'appuyer sur TrainerKnowledgeItem validé si disponible
2. Réflexif sur une situation de soins difficile : Hugo doit respecter la charge émotionnelle (risque interactionnel)
3. Évaluation en fin de séance mature : trace exploitable pour portfolio diplôme

**Critères d'oracle**
- Mode révision de savoirs : microexplication ≤ 1 phrase, 1 par tour
- Risque interactionnel élevé → fallback single-question obligatoire
- Aucun TrainerKnowledgeItem `derivedProvisional` injecté sans validation humaine préalable

**Niveau de preuve** : Noyau — explicite cible 2.0. Tension adulte en reconversion — inféré fort (formation pro, OF, GRETA). TrainerKnowledgeItem dans révision — ALIGNÉ DOC PARTIEL réel.[^9][^10]

***

### PERSONA A3 — APPRENANT EXPERT TECHNIQUE EN MONTÉE EN COMPÉTENCE : Ibrahima, technicien senior

**Noyau stable**

| Champ | Valeur |
|---|---|
| **Identité synthétique** | Ibrahima, 45 ans, technicien de maintenance industrielle, forte expérience terrain, en formation managériale (prise de poste chef d'équipe) |
| **Contexte** | Maîtrise parfaitement le technique, découvre la dimension managériale, situations de management complexes à analyser |
| **Objectif** | Analyser des situations managériales nouvelles, nommer ce qui se passe, gagner en posture de leadership |
| **Irritants** | Condescendance implicite, microexplications sur des points techniques qu'il maîtrise, relances trop basiques |
| **Rôle produit** | LEARNER |

**Comportements conversationnels typiques**
- Décrit des situations complexes avec précision technique mais difficulté à nommer le problème managérial
- Orchestre le diagnostic pour identifier la dimension humaine ou organisationnelle
- Peut vouloir basculer lui-même vers l'évaluation alors que la séance n'est pas suffisamment mûre

**Cas limites**
- Demande d'évaluation prématurée → `optionalEvaluationEligible = false`, Hugo explique pourquoi
- Situation très peu claire malgré expertise : Hugo reste en diagnostic, ne court-circuite pas vers réflexif

**Niveau de preuve** : Inféré fort sur base spec P0 (ZPD, niveau expertise, directivité adaptée).

***

### PERSONA B1 — TUTEUR ENTREPRISE : Fabienne, tutrice en CFA de la grande distribution

**Noyau stable**

| Champ | Valeur |
|---|---|
| **Identité synthétique** | Fabienne, 52 ans, responsable de rayon, tutrice de 3 alternants en CFA commerce |
| **Contexte** | Suit ses alternants entre les séances, ne peut pas lire ce qu'ils ont dit à Hugo (verbatim priv), mais voit la progression et les traces partagées |
| **Objectif** | Comprendre où en est chaque apprenant, adapter les situations de travail, recommander une synthèse ou une évaluation quand le moment est bon |
| **Irritants** | Dashboard illisible, données trop techniques, ne comprend pas ce que signifie "maturité ORANGE", confond lecture de trace et accès à la conversation |
| **Contraintes** | Accès uniquement sur les moments creux (midi, soir), desktop entreprise |
| **Rôle produit** | TUTOR |
| **Attentes de confidentialité** | Comprend ne pas avoir accès au verbatim ; veut des signaux clairs, pas un scoring opaque |

**Modules de variation**

| Module | Valeur nominale | Variantes |
|---|---|---|
| Littératie numérique | Faible-moyenne (office, email, mais pas de dashboard complexe) | Forte (RH digital) |
| Rapport à l'évaluation | Veut valider les traces, pas les produire seule | Veut initier lui-même une évaluation |
| Rapport à la preuve | Fonctionnel (portfolio, Qualiopi) | Sceptique |
| Technicité métier | Forte commerce, faible pédagogie formelle | Pédagogue expert |

**Comportements conversationnels typiques**
- Consulte le dashboard cohorte, regarde les apprenants signalés "blocage"
- Lit la synthèse partagée, peut la commenter
- Recommande un débrief ciblé à l'apprenant hors Hugo
- Ne comprend pas pourquoi un bouton "évaluation" est grisé → besoin d'explication

**Attentes UI**
- Vue cohorte lisible sans jargon technique (pas de "dispersionRisk 0.8", mais "attention : cet apprenant s'éparpille")
- Signaux qualitatifs, pas de score opaque
- Accès clair aux traces partagées uniquement
- Bouton "recommander une synthèse" visible et compréhensible
- Pas d'accès à la vue debug/P0

**Scénarios de test**
1. Fabienne ouvre la vue tuteur → voit la cohorte avec 3 apprenants → identifie Karim en blocage
2. Elle lit la synthèse partagée par Karim → peut commenter, ne peut pas modifier le verbatim
3. Elle recommande une évaluation → signal transmis, mais l'apprenant reste maître du déclenchement
4. Elle tente d'accéder au verbatim non partagé → bloqué (test de non-régression)

**Critères d'oracle**
- Vue tuteur : aucun champ P0 brut affiché
- Verbatim non partagé inaccessible depuis la route tuteur
- Recommandation tuteur enregistrée mais non forcée sur le moteur

**Niveau de preuve** : Noyau — explicite cible 2.0. Signaux cohorte (LOT 6) — AVERIFIER réel.[^6][^7]

***

### PERSONA B2 — TUTEUR PÉDAGOGUE EXPÉRIMENTÉ : Mehdi, formateur-tuteur en GRETA

**Noyau stable**

| Champ | Valeur |
|---|---|
| **Identité synthétique** | Mehdi, 41 ans, formateur au GRETA, suit 8 adultes en reconversion, à l'aise avec les outils numériques pédagogiques |
| **Contexte** | Utilise Hugo comme outil de suivi entre les regroupements, lit les progressions, ajuste ses contenus de formation |
| **Objectif** | Détecter les apprenants qui stagnent, préparer les regroupements, valider les traces exploitables pour Qualiopi |
| **Irritants** | Manque de granularité sur ce qui bloque réellement, ne peut pas distinguer blocage cognitif vs blocage relationnel vs manque de temps |
| **Rôle produit** | TUTOR |

**Différences avec B1**
- Comprend les signaux techniques (maturité, dispersion), veut des données plus précises
- Initie des exports pack Qualiopi lite pour ses audits pédagogiques
- Peut identifier des tendances de cohorte et adapter son programme

**Scénarios de test**
1. Export pack Qualiopi lite pour un apprenant → vérifier richesse artefacts, périmètre, mention "non certifiant"
2. Vue cohorte agrégée → signaux de qualité sans accès verbatim individuel

**Critères d'oracle**
- Export bundle : mention explicite que c'est une aide à l'audit, pas une certification automatique
- GPS opt-in respecté sur les preuves photo incluses dans le bundle

**Niveau de preuve** : Inféré fort (profil formateur OF/GRETA avec usage Qualiopi). Bundle Qualiopi lite — POC historique observable.[^8]

***

### PERSONA C1 — FORMATEUR CONCEPTEUR : Amélie, formatrice en ingénierie pédagogique

**Noyau stable**

| Champ | Valeur |
|---|---|
| **Identité synthétique** | Amélie, 36 ans, ingénieure pédagogique, responsable de la conception des parcours pour un OF industriel |
| **Contexte** | Construit la base de connaissances formateur dans Hugo : upload de référentiels, questionnaire dialogique, validation des items |
| **Objectif** | Alimenter Hugo en savoir métier structuré, valider les items dérivés, s'assurer que la base n'introduit pas d'erreurs dans les parcours apprenant |
| **Irritants** | Items dérivés auto-promus (invariant fondamental : aucun auto-upgrade), impossibilité de voir comment les items sont réellement utilisés dans les conversations, workflow de validation opaque |
| **Contraintes** | Travail en desktop uniquement, besoin de traçabilité des décisions de validation, temps disponible en dehors des cours |
| **Rôle produit** | TRAINER |
| **Attentes de confidentialité** | Ne doit pas accéder au contenu apprenant non partagé ; base formateur distincte des traces de conversation |

**Modules de variation**

| Module | Valeur nominale | Variantes |
|---|---|---|
| Littératie numérique | Forte | Moyenne (formateur "terrain") |
| Technicité métier | Élevée (ingénierie pédagogique) | Faible (expert métier pur) |
| Rapport à la preuve | Fort (Qualiopi, certification) | Fonctionnel |
| Rapport à l'explicitation | Expert (produit facilement des critères, erreurs types) | Réticent |
| Rapport à la validation | Veut comprendre le statut de chaque item | Délègue à l'orgadmin |

**Comportements conversationnels typiques (orchestrateur formateur)**
- Répond au questionnaire dialogique avec précision : « le critère de maîtrise ici c'est que l'apprenant puisse… »
- Upload un référentiel compétences, attend que Hugo propose des items dérivés
- Revient plusieurs fois sur le tableau de validation pour promouvoir des items après relecture
- Peut être frustrée si l'interface ne lui montre pas l'impact de ses items sur les parcours

**Attentes UI (surfaces trainer)**
- Liste d'items avec statuts clairs (déclaré / dérivé provisoire / validé)
- Actions explicites : valider, rejeter, corriger, rattacher au référentiel
- Tableau de validation filtragle par statut
- Pas d'exposition du contenu apprenant non partagé dans ses vues

**Scénarios de test**
1. Upload d'un document référentiel → DocumentIngestor → items dérivés provisoires générés
2. Amélie valide manuellement un item → statut passe à `validatedTrainer` (jamais auto)
3. Amélie tente de voir le verbatim d'un apprenant → bloqué (non partagé)
4. Export de la base formateur pour audit interne

**Cas limites**
- Tentative d'auto-promotion : système doit refuser tout passage automatique `derivedProvisional → validatedHuman`
- Item déclaré sans rattachement référentiel : Hugo doit alerter

**Critères d'oracle**
- Aucun item `derivedProvisional` auto-promu vers `validatedHuman` sans acte explicite
- TrainerKnowledgeItem affiché avec statut, type, provenance
- Vue trainer : aucun accès libre au contenu apprenant non partagé

**Niveau de preuve** : TrainerKnowledgeItem — ALIGNÉ réel/cible. Orchestrateur formateur complet — ALIGNÉ DOC PARTIEL (workflow fin non prouvé bout en bout).[^10][^9]

***

### PERSONA C2 — FORMATEUR EXPERT MÉTIER NON PÉDAGOGUE : Bernard, artisan couvreur expert

**Noyau stable**

| Champ | Valeur |
|---|---|
| **Identité synthétique** | Bernard, 58 ans, artisan couvreur-zingueur, maître d'apprentissage, peu à l'aise avec le numérique |
| **Contexte** | On lui demande d'alimenter Hugo avec son savoir métier. Il sait très bien ce qui est bien ou mal fait sur un toit, mais n'a jamais formalisé de critères |
| **Objectif** | Transmettre ses critères de maîtrise, ses erreurs types, ses raisonnements — sans avoir à écrire un référentiel |
| **Irritants** | Interface trop complexe, questions trop abstraites ("quels sont vos indicateurs de maîtrise ?"), sentiment que la machine ne comprend pas le métier physique |
| **Contraintes** | Accès uniquement sur tablette/smartphone, peu de temps, préfère l'oral au texte |
| **Rôle produit** | TRAINER |
| **Attentes de confidentialité** | Ne comprend pas bien les enjeux de confidentialité, besoin de pédagogie |

**Différences avec C1**
- Besoin d'un orchestrateur formateur avec questions très concrètes et ancrées dans les gestes métier
- Items déclarés verbalement, pas par upload de documents
- Peut avoir du mal à valider des items dérivés formulés de façon trop abstraite

**Critères d'oracle**
- Orchestrateur formateur ne pose pas de questions trop abstraites sans ancrage métier
- Items dérivés reformulés dans le langage métier de Bernard, pas en jargon pédagogique

**Niveau de preuve** : Inféré fort. Le questionnaire dialogique formateur est explicitement prévu pour ce cas.[^7][^6]

***

### PERSONA D1 — ORGADMIN RESPONSABLE DE FORMATION : Sylvie, responsable formation d'un groupe industriel

**Noyau stable**

| Champ | Valeur |
|---|---|
| **Identité synthétique** | Sylvie, 47 ans, responsable formation d'un groupe industriel, gère 3 sites, 200 salariés en formation |
| **Contexte** | Déploie Hugo pour plusieurs dispositifs de formation. Crée les comptes, configure les groupes, déclenche les exports pour les audits Qualiopi |
| **Objectif** | Administrer efficacement son organisation dans Hugo, produire les preuves d'ingénierie pédagogique, préparer les audits |
| **Irritants** | Interface admin incomplète (pas de suppression de comptes), pas de vue agrégée claire, confond son rôle avec un accès debug |
| **Contraintes** | Desktop uniquement, tenant strict (3 sites = 3 organisations ou 1 avec sous-groupes ?) |
| **Rôle produit** | ORGADMIN |
| **Attentes de confidentialité** | Ne veut surtout pas accéder au verbatim des apprenants sans leur accord — exposition légale. Multi-tenant strict requis |

**Modules de variation**

| Module | Valeur nominale | Variantes |
|---|---|---|
| Littératie numérique | Forte (SaaS RH, SIRH) | Moyenne |
| Rapport à l'audit | Qualiopi expert | Fonctionnel |
| Technicité RH | Forte | Faible |
| Taille organisation | Grande (multi-sites) | Petite (CFA local) |

**Attentes UI**
- Gestion utilisateurs : création, édition, rattachement groupes/cohortes
- Indicateurs agrégés : volumes sessions, usage synthèse/évaluation, sans contenu apprenant
- Déclenchement exports filtrés par organisation
- Interface séparée de la superadmin technique

**Scénarios de test**
1. Création d'un nouveau compte apprenant rattaché à l'organisation → vérifier isolation tenant
2. Export CSV agrégé pour audit → périmètre tenant strict, pas de données cross-tenant
3. Tentative de lecture du verbatim apprenant → bloqué (test de non-régression)
4. Tentative de suppression de compte → AVERIFIER (non documenté dans réel audité)

**Critères d'oracle**
- Aucune donnée cross-tenant visible depuis l'interface ORGADMIN
- Export filtré uniquement par `organizationId`
- Verbatim apprenant non partagé inaccessible

**Niveau de preuve** : Noyau — cible 2.0 explicite. Suppression comptes — AVERIFIER réel. RLS prod effective — AVERIFIER.[^3][^1]

***

### PERSONA D2 — ORGADMIN PETIT OF : Jean-Louis, directeur d'un CFA artisanal

**Noyau stable**

| Champ | Valeur |
|---|---|
| **Identité synthétique** | Jean-Louis, 60 ans, directeur d'un CFA de 40 apprentis, cumule les rôles (direction, formateur, admin) |
| **Contexte** | Faible ressource numérique, découvre Hugo, a besoin d'une interface admin simple |
| **Objectif** | Créer les comptes de ses apprentis, suivre globalement la progression, produire un document pour son audit Qualiopi annuel |
| **Irritants** | Trop de paramètres, ne comprend pas la différence ORGADMIN/SUPERADMIN, interface pensée pour des grandes structures |
| **Contraintes** | Petit budget, peu de temps, parfois le seul utilisateur non apprenant |

**Différences avec D1**
- A besoin d'une interface admin ultra-simplifiée
- Peut cumuler les rôles ORGADMIN et TRAINER dans la pratique (tension à gérer dans le produit)
- Test de dépassement de droits : tente d'accéder à des fonctions superadmin

**Niveau de preuve** : Inféré fort (OF, CFA, petit établissement).[^3]

***

### PERSONA E1 — COORDINATEUR PÉDAGOGIQUE : Hélène, coordinatrice pédagogique OF régional

**Noyau stable**

| Champ | Valeur |
|---|---|
| **Identité synthétique** | Hélène, 44 ans, coordinatrice pédagogique d'un OF régional, interface entre formateurs, tuteurs et direction |
| **Contexte** | Supervise plusieurs dispositifs, coordonne les validations de TrainerKnowledgeItem, valide certaines traces avant export |
| **Objectif** | Avoir une vue transversale, coordonner les workflows de validation, préparer les audits |
| **Rôle produit** | COORDO |
| **Attentes de confidentialité** | Mêmes que ORGADMIN — pas d'accès libre au verbatim apprenant |

> ⚠️ **AVERTISSEMENT — NIVEAU DE PREUVE FAIBLE** : Le rôle COORDO est un rôle doctrinal cible (**ABSENT NOUVEAU CONTRAT** dans le réel observable). Ce persona est construit sur une **hypothèse crédible** à partir de la logique des rôles 2.0. Aucune surface stabilisée n'est documentée dans le corpus audité.[^2][^3]

**Scénarios hypothétiques**
- Hélène valide des TrainerKnowledgeItem proposés par des formateurs (si ce rôle lui est attribué)
- Elle lance un export cohorte multi-formateurs
- Elle configure des groupes et rattache des tuteurs à des cohortes

***

### PERSONA F1 — SUPERADMIN TECHNIQUE : Romain, CTO/développeur Hugo

**Noyau stable**

| Champ | Valeur |
|---|---|
| **Identité synthétique** | Romain, 32 ans, développeur backend, gère l'infrastructure Hugo multi-tenant |
| **Contexte** | Accède aux surfaces de pilotage borné (profils orchestrateurs, seuils, exports debug) pour les chantiers de convergence |
| **Objectif** | Piloter les paramètres des orchestrateurs, observer le comportement du moteur, débugger une session test |
| **Irritants** | Pas assez de visibilité sur les raisons d'un comportement moteur, difficile de distinguer environnement local/distant |
| **Contraintes** | Accès uniquement en environnement de test ou dédié, hors prod multitenant grand public |
| **Rôle produit** | SUPERADMIN |
| **Attentes de confidentialité** | Comprend les règles : l'export debug contient du verbatim, donc strictement réservé aux sessions de test avec consentement |

**Scénarios de test**
1. Export debug complet d'une conversation test (Markdown avec P0 brut) → vérifie la mention "données internes non montrables produit"
2. Modification d'un profil d'orchestrateur (curseurs, seuils) → journalisé, borné, sans toucher à la logique P0 centrale
3. Tentative d'accès à une session d'un vrai apprenant → bloqué (garde-fou)

**Critères d'oracle**
- Export debug : accès uniquement sur sessions marquées test ou avec consentement
- Toute modification de paramètre superadmin journalisée (qui, quoi, quand)
- Désactivation de l'export debug en prod multitenant

**Niveau de preuve** : Cible 2.0 explicite. Réel — surfaces back-office testeur partielles observées.[^1]

***

### PERSONA G1 — EDGE CASE : L'apprenant à très faible littératie numérique

**Identité** : Rachid, 25 ans, apprenti maçon, smartphone uniquement, jamais utilisé d'outil conversationnel, lit peu.

**Risques spécifiques**
- Interface trop dense → abandon immédiat
- Questions trop longues → incompréhension
- Synthèse non demandée → perd le fil
- Icônes non comprises → erreurs de navigation

**Critères d'oracle**
- UIState expose des labels texte, pas uniquement des icônes
- Relances courtes (2-4 phrases max confirmées)
- Synthèse accessible en un tap depuis la conversation

**Niveau de preuve** : Inféré fort (public alternance artisanat, accessibilité numérique).

***

### PERSONA G2 — EDGE CASE : L'apprenant très autonome qui veut tout contrôler

**Identité** : Sandra, 30 ans, ingénieure, suit une formation continue volontairement, connait bien les outils numériques.

**Comportements atypiques**
- Tente de forcer une évaluation prématurée
- Veut changer de posture à chaque tour
- Demande à voir ses scores P0 (demande bloquée)
- Remet en question la pertinence des questions de Hugo

**Critères d'oracle**
- Évaluation forcée avant éligibilité : UIState affiche un message explicatif, pas une erreur technique
- Changement de posture mid-session : PATCH posture → refus motivé si séance trop avancée
- Aucun champ P0 brut exposé même si demandé explicitement

**Niveau de preuve** : Inféré fort.

***

### PERSONA G3 — EDGE CASE : L'ORGADMIN qui teste les limites de confidentialité

**Identité** : Thierry, 50 ans, DSI d'un groupe, habituellement habitué à avoir accès à tout.

**Comportements atypiques**
- Tente une injection SQL dans les exports
- Tente un accès cross-tenant via manipulation d'URL
- Demande un export global de tous les verbatims de l'organisation

**Critères d'oracle**
- Isolation RLS : requête cross-tenant retourne 0 résultats, pas une erreur technique révélatrice
- Export verbatim global : bloqué si non partagé par les apprenants
- Tests cross-tenant de non-régression (test unitaire `testCrossTenant`)

**Niveau de preuve** : Inféré fort. RLS middleware cross-tenant observé dans le réel local.[^3]

***

## PARTIE VI — MODULES DE VARIATION RÉUTILISABLES

Les modules suivants s'appliquent à tout persona pour générer des variantes de test sans recréer une galerie entière.

| Module | Valeurs possibles | Impact moteur |
|---|---|---|
| **Niveau de langage** | [familier / professionnel / académique] | Style des relances, vocabulaire des reformulations |
| **Niveau numérique** | [faible / moyen / fort] | Complexité UI tolérée, jargon acceptable |
| **Autonomie** | [faible / moyenne / forte] | ZPD, directivité, gestes tutoriaux |
| **Rapport à l'évaluation** | [anxieux / neutre / demandeur / prématuré] | Gestion de `optionalEvaluationEligible` |
| **Rapport au partage** | [fermé / sélectif / ouvert] | Déclenchement partage explicite |
| **Sensibilité à la preuve** | [nulle / fonctionnelle / experte Qualiopi] | Usage exports, bundle, EvidenceBundleView |
| **Technicité métier** | [débutant / intermédiaire / expert] | Niveau des questions P0 (ZPD), usage TrainerKnowledgeItem |
| **Rapport à l'explicitation** | [difficile / normal / fluide] | Durée en mode diagnostic, relances clarification |
| **Charge cognitive séance** | [faible / moyenne / élevée] | Fallback single-question, blocage microexplication |
| **Risque interactionnel** | [faible / moyen / élevé] | Gestes reassure, repair, fallback |
| **Maturité de séance** | [RED / ORANGE / GREEN] | Accessibilité synthèse, évaluation facultative |
| **Taille organisation** | [individuel / PME / grand groupe] | Multi-tenant, cohortes, coordination |

***

## PARTIE VII — MATRICE PERSONA × FONCTIONS HUGO 2.0 × SCÉNARIOS × RISQUES

| Persona | Orchestrateur réflexif | Orchestrateur diagnostic | Révision savoirs | Évaluation facultative | Base formateur | Observabilité tuteur | Exports / Qualiopi | Confidentialité / RLS | Intercalaires |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **A1 Karim (alternant)** | ✅ cœur | ✅ prioritaire | ✅ | ✅ éligibilité | — | — | — | ✅ partage | ⚠️ V1 |
| **A2 Nadège (reconversion)** | ✅ | ✅ | ✅ prioritaire | ✅ | — | — | ✅ portfolio | ✅ | ⚠️ |
| **A3 Ibrahima (expert)** | ✅ | ✅ prioritaire | ✅ | ✅ forcé (test) | — | — | — | ✅ | — |
| **B1 Fabienne (tutrice)** | — | — | — | — | — | ✅ prioritaire | ⚠️ | ✅ verbatim | — |
| **B2 Mehdi (formateur-tuteur)** | — | — | — | — | — | ✅ | ✅ Qualiopi | ✅ | — |
| **C1 Amélie (formatrice)** | — | — | — | — | ✅ prioritaire | — | ✅ base formateur | ✅ | — |
| **C2 Bernard (expert métier)** | — | — | — | — | ✅ questionnaire | — | — | ✅ | — |
| **D1 Sylvie (ORGADMIN)** | — | — | — | — | — | — | ✅ prioritaire | ✅ RLS | — |
| **D2 Jean-Louis (petit OF)** | — | — | — | — | ⚠️ | — | ✅ simple | ✅ | — |
| **E1 Hélène (COORDO)** | — | — | — | — | ⚠️ hypothèse | — | ⚠️ hypothèse | ✅ | — |
| **F1 Romain (superadmin)** | — | — | — | — | — | ⚠️ debug | ✅ debug | ✅ test | — |
| **G1 Faible littératie** | ✅ accessibilité | ✅ | ✅ | ✅ | — | — | — | ✅ | — |
| **G2 Autonome exigeante** | ✅ | ✅ | ✅ | ✅ forcé (test) | — | — | — | ✅ | — |
| **G3 ORGADMIN limite** | — | — | — | — | — | — | ✅ cross-tenant | ✅ prioritaire | — |

**Légende** : ✅ scénario couvert — ⚠️ scénario partiel ou AVERIFIER — — non applicable

***

## PARTIE VIII — COUVERTURE DE LA GALERIE

### Ce que la galerie couvre bien

- L'ensemble des **6 rôles doctrinaux** de la cible 2.0 (LEARNER, TUTOR, TRAINER, COORDO, ORGADMIN, SUPERADMIN)
- La **diversité des apprenants** : jeune alternant, adulte en reconversion, expert technique — couvrant des niveaux de langage, de technicité métier et d'aisance numérique très différents
- Les **4 postures conversationnelles** (réflexif, diagnostic, révision, évaluation facultative) et leurs conditions de déclenchement/sortie
- Les **invariants de confidentialité** : verbatim privé, partage explicite, multi-tenant, aucun champ P0 brut en front
- Les **surfaces encadrants** : tuteur lecture-seule sur traces partagées, formateur sur base de connaissances, ORGADMIN sur administration bornée
- Les **edge cases** critiques : littératie faible, autonomie forte, tentative de dépassement des droits
- Le **module de variation** réutilisable sans recréer une galerie complète

### Ce que la galerie couvre mal

- **Le coordinateur (COORDO)** : persona construit sur hypothèse, aucune surface réelle documentée
- **Les scénarios multi-acteurs synchrones** : la galerie traite chaque rôle séparément ; les interactions simultanées (tuteur voit une alerte pendant qu'un apprenant est en séance) ne sont pas scénarisées
- **Les variantes de déploiement** : CFA mono-tenant vs groupe multi-sites multi-tenant ; les différences de comportement ne sont pas entièrement explorées
- **La richesse réelle des traces** : les scénarios d'export supposent des traces suffisamment riches, mais le réel local montre que `generate-trace` produit un payload minimal — certains scénarios export peuvent ne pas être jouables en l'état

### Ce qui reste ouvert

- Le **script conversationnel détaillé** de l'orchestrateur formateur (ordre des questions, relances) : non fixé dans le corpus
- La **matrice précise des droits de validation** (formateur vs coordo vs orgadmin sur les TrainerKnowledgeItem)
- La **RLS Postgres effective en production réelle** : marquée AVERIFIER dans tous les domaines concernés
- Le **catalogue canonique des ConversationQualitySignal** (LOT 6) : signaux cibles non listés précisément
- L'**équivalence comportementale local / runtime distant Encoors** sur tous les domaines
- Les **intercalaires pédagogiques** (persona A1/A2 séances) : capacité V1 en cours, non livrable complète à ce jour

# ANNEXE C. PERSONAE HUGO 2.0 × CURSOR × SUIVI DES LOTS DE CONVERGENCE

## C.1. Objet de l'annexe

Cette annexe précise comment utiliser la galerie de personae Hugo 2.0 comme entrée structurée pour des prompts Cursor, afin de générer et maintenir des tests automatisés de suivi de l’implémentation du plan de convergence (par lots et clusters).

Elle ne modifie pas la définition des personae cœur, mais ajoute des champs normés et une matrice d’usage permettant :
- de relier chaque persona aux clusters de lots concernés (par ex. « Cluster 2 — front apprenant, UIState, memory-summary, CTA synthèse/évaluation ») ;
- de décrire, pour chaque couple persona × cluster, les contrats cibles à tester, les scénarios clés et les risques d’échec attendus ;
- de générer automatiquement des prompts Cursor de type « audit code/doc/runtime » ou « implémentation guidée » à partir de ces éléments.

## C.2. Champs additionnels standard par persona

Pour un usage systématique avec Cursor, chaque persona canonique (A1–A3, B1–B2, C1–C2, D1–D2, F1, etc.) est enrichi des champs additionnels suivants :

- **ClustersConvergenceCibles**  
  Liste structurée des clusters de lots pour lesquels ce persona est pertinent, par ex. :  
  - `Cluster_1_Backend_P0_Progression`  
  - `Cluster_2_Front_UIState_Memory_CTA`  
  - `Cluster_3_Intercalaires`  
  - `Cluster_4_Exports_Preuve_QualiopiLite`  
  - `Cluster_5_Confidentialite_Roles_MultiTenant`

- **ContratsCiblesParCluster**  
  Pour chaque cluster listé, une sous-structure :  
  - `ContratsInterfaces`: références aux contrats minimaux (UI, API, objets) impliqués (ex. `UIState`, `GET /hugosessions/{id}/ui-state`, `GET /hugosessions/{id}/memory-summary`, `ctaevaluation`, `ctasynthesis`).  
  - `NiveauPreuve`: `IMP_OBSERVE` (implémenté et audité), `CIBLE_FERME`, `CIBLE_PARTIELLE`, `AVERIFIER`.  
  - `CommentaireLecture`: court texte rappelant si on teste le code actuel ou une cible documentaire (ex. « cible 2.0, non encore prouvée en runtime distant »).

- **ScenariosTestsParCluster**  
  Liste de scénarios typés pour ce persona et ce cluster :  
  - `ScenarioID` (stable, pour Cursor et le backlog),  
  - `Intitule` (ex. « A2 voit la progression et un CTA de synthèse bloqué avec explication lisible »),  
  - `TypeTest` (`UNIT`, `INTEGRATION`, `E2E_DEMO`),  
  - `SurfaceConcernee` (`APPRENANT_FRONT`, `API_BACKEND`, `EXPORTS`, `ADMIN_ORG`, etc.),  
  - `RisquesEchec` (liste courte alignée sur les matrices d’écarts, ex. `CONF-07`, `CONF-09`, `EXP-011`).

- **NiveauxVéritéEtUsageCursor**  
  Champ qui explicite comment Cursor doit lire ce persona :  
  - `UsageAudit` : le persona sert à générer des prompts d’audit (lecture code/doc/runtime) ;  
  - `UsageImpl` : le persona sert à générer des squelettes d’implémentation ou de tests ;  
  - `GardeFous` : rappel des règles de lecture (ne pas déduire la prod distante du local, distinguer cible 2.0 vs réel observé, etc.).

Ces champs sont **additifs** : ils ne créent pas de nouvelles personae, ils augmentent les noyaux stables et les modules de variation existants pour les rendre pilotables par Cursor.

## C.3. Matrice Persona × Domaine d’écarts × Type de tests

Pour relier les personae aux domaines d’écarts documentés (par ex. `90_confidentialite_partage_multitenant_roles`, `100_exports_preuves_qualiopi_lite`), on introduit une matrice synthétique :

- Lignes : personae canoniques (A1, A2, A3, B1, B2, C1, C2, D1, D2, F1, …).  
- Colonnes :  
  - `DomaineEcart` (ex. `90_confidentialite_partage_multitenant_roles`, `100_exports_preuves_qualiopi_lite`),  
  - `Pertinence` (`FORT`, `MOYEN`, `FAIBLE`, `N/A`),  
  - `ScenariosTestsTypiques` (référence aux `ScenarioID` définis dans `ScenariosTestsParCluster`),  
  - `NiveauPreuveDomaine` (reprend les statuts de la matrice d’écarts : `ALIGNE`, `ALIGNEDOC_PARTIEL`, `AMBIGU`, `AVERIFIER`, `ABSENT_NOUVEAU_CONTRAT`).

Cette matrice est la principale entrée pour générer des prompts Cursor de type :

> « À partir du persona A2 et du domaine 90_confidentialite_partage_multitenant_roles, produire un plan de tests automatisés pour le cluster 2 (front apprenant) en respectant les statuts de preuve `ALIGNE` / `ALIGNEDOC_PARTIEL` / `AVERIFIER`. »

## C.4. Recommandations d’usage avec Cursor

- Cursor doit utiliser les champs `ClustersConvergenceCibles`, `ContratsCiblesParCluster` et `ScenariosTestsParCluster` comme **contrat d’entrée** pour générer :  
  - soit des audits de code/doc (`PROMPTCURSOR` des backlogs de domaines 90 et 100),  
  - soit des tests unitaires/intégration (`pytest`, tests DRF, tests front) alignés avec les contrats d’interface.

- Les champs `NiveauPreuve` doivent être transportés dans les prompts Cursor (par ex. via un bloc « Niveaux de vérité ») afin de distinguer :  
  - ce qui est **déjà observable dans le rel local**,  
  - ce qui est **cible 2.0** mais non encore prouvé,  
  - ce qui dépend d’un **runtime distant / RLS prod / flags** marqué explicitement `AVERIFIER`.

- Pour tous les tests qui touchent la confidentialité, le partage ou le multi-tenant, les garde-fous du domaine 90 (verbatim privé, front non pilote, RLS prod AVERIFIER, etc.) doivent être rappelés dans le contexte du prompt Cursor.

Cette annexe ne prétend pas que les comportements décrits sont déjà livrés ; elle fournit un contrat exploitable par Cursor pour accompagner leur implémentation et en suivre la convergence lot par lot.

# ANNEXE D. EXEMPLES DE PERSONAE ENRICHIS POUR CURSOR

## D.1. Persona A2 — Apprenant en alternance, autonomie moyenne (exemple enrichi)

> NB : ce bloc ne remplace pas la fiche A2 existante ; il la complète en ajoutant les champs Cursor-ready.

### D.1.1. Métadonnées Cursor

- **PersonaID** : `A2`  
- **RôleProduit** : `APPRENANT`  
- **ClustersConvergenceCibles** :  
  - `Cluster_1_Backend_P0_Progression`  
  - `Cluster_2_Front_UIState_Memory_CTA`  
  - `Cluster_3_Intercalaires`  

### D.1.2. Contrats cibles par cluster

```json
{
  "Cluster_1_Backend_P0_Progression": {
    "ContratsInterfaces": [
      "Service Analyse du tour -> TurnState (P0)",
      "Service Decision locale -> ContratDecision",
      "Service ProgressionCalculator -> ConversationProgress"
    ],
    "NiveauPreuve": "CIBLE_FERME",
    "CommentaireLecture": "Contrats spécifiés dans la spec 2.0, non lisibles directement dans le front. À tester via audit code/runtime, pas via UI seule."
  },
  "Cluster_2_Front_UIState_Memory_CTA": {
    "ContratsInterfaces": [
      "GET /hugosessions/{id}/ui-state",
      "GET /hugosessions/{id}/memory-summary",
      "UIState.scene / phase / progression / brancheActive / maturite",
      "UIState.ctaevaluation / UIState.ctasynthesis"
    ],
    "NiveauPreuve": "ALIGNEDOC_PARTIEL",
    "CommentaireLecture": "Contrat d'interface apprenant détaillé dans specs-interface-2.0 pour le lot courant, avec front déjà basé sur ui-state, mais messages UI et granularité exacte partiellement ouverts."
  },
  "Cluster_3_Intercalaires": {
    "ContratsInterfaces": [
      "POST /hugosessions/{id}/messages (hook post-réponse)",
      "Task async prepareInterstitialForNextTurn",
      "Table sessioninterstitial (objet pédagogique préparé pour le tour suivant)",
      "GET /hugosessions/{id}/next-interstitial"
    ],
    "NiveauPreuve": "CIBLE_PARTIELLE",
    "CommentaireLecture": "Contrat décrit dans le dernier run intercalaires, backend-first, hors P0, à implémenter additivement."
  }
}
```

### D.1.3. Scénarios de tests typiques par cluster

```json
{
  "Cluster_2_Front_UIState_Memory_CTA": [
    {
      "ScenarioID": "A2_UI_01",
      "Intitule": "A2 voit une scène lisible, la branche active et la couleur de maturité sans aucun champ P0 brut.",
      "TypeTest": "INTEGRATION",
      "SurfaceConcernee": "APPRENANT_FRONT",
      "RisquesEchec": ["CONF-02", "CONF-03", "CONF-04"]
    },
    {
      "ScenarioID": "A2_UI_02",
      "Intitule": "Le bouton de synthèse est visible mais bloqué avec un helpertext lisible expliquant le blocage (contenu insuffisant ou contexte incomplet).",
      "TypeTest": "INTEGRATION",
      "SurfaceConcernee": "APPRENANT_FRONT",
      "RisquesEchec": ["CONF-06", "CONF-19"]
    },
    {
      "ScenarioID": "A2_UI_03",
      "Intitule": "Le bouton d'évaluation n'apparaît pas tant que la maturité de session n'est pas suffisante, et ne laisse jamais croire à une certification autonome.",
      "TypeTest": "INTEGRATION",
      "SurfaceConcernee": "APPRENANT_FRONT",
      "RisquesEchec": ["CONF-18", "CONF-19"]
    }
  ],
  "Cluster_3_Intercalaires": [
    {
      "ScenarioID": "A2_INT_01",
      "Intitule": "A2 ne voit aucun intercalaire si la charge cognitive ou le risque interactionnel sont élevés (gating V1).",
      "TypeTest": "UNIT",
      "SurfaceConcernee": "API_BACKEND",
      "RisquesEchec": ["CONF-02"]
    },
    {
      "ScenarioID": "A2_INT_02",
      "Intitule": "A2 voit au plus un intercalaire de type 'notion' ou 'contraste', sans verbatim recopié, entre deux tours.",
      "TypeTest": "INTEGRATION",
      "SurfaceConcernee": "APPRENANT_FRONT",
      "RisquesEchec": ["CONF-02", "CONF-03"]
    }
  ]
}
```

### D.1.4. Niveaux de vérité et garde-fous pour Cursor

- **UsageAudit** : oui (surtout pour Cluster 1 et 3).  
- **UsageImpl** : oui (génération de tests front et backend).  
- **GardeFous** :  
  - Ne pas déduire l’état de la prod distante `hugoback.encoors.com` à partir du local ;  
  - Marquer comme `AVERIFIER` tout test qui suppose RLS Postgres effective ou permissions exhaustives par rôle ;  
  - Ne jamais exposer TurnState ou les champs P0 bruts côté front dans les tests.

---

## D.2. Persona D1 — ORGADMIN (COORDO fusionné) — exemple enrichi

> NB : ce bloc suppose que les responsabilités “coordinateur” historiques ont été rabattues sur ORGADMIN, comme correction de biais historique.

### D.2.1. Métadonnées Cursor

- **PersonaID** : `D1`  
- **RôleProduit** : `ORGADMIN` (incluant fonctions de coordination qualité)  
- **ClustersConvergenceCibles** :  
  - `Cluster_2_Front_UI_AdminMinimal`  
  - `Cluster_4_Exports_Preuve_QualiopiLite`  
  - `Cluster_5_Confidentialite_Roles_MultiTenant`

### D.2.2. Contrats cibles par cluster

```json
{
  "Cluster_2_Front_UI_AdminMinimal": {
    "ContratsInterfaces": [
      "Vue administration d'organisation (UsersView, gestion comptes/rattachements)",
      "Indicateurs agrégés usage (volumes de sessions, usage synthèse/évaluation)",
      "Aucune lecture de contenu apprenant non partagé ni de champs P0 bruts"
    ],
    "NiveauPreuve": "ALIGNEDOC_PARTIEL",
    "CommentaireLecture": "Admin observable partielle dans le rel ; matrice de permissions fine encore ouverte."
  },
  "Cluster_4_Exports_Preuve_QualiopiLite": {
    "ContratsInterfaces": [
      "POST /exports/run",
      "GET /exports/download/{runId}",
      "POST /quality/qualiopi/evidence-bundle",
      "Traces, Evidence, EvidenceBundleView rattachées à session/trace"
    ],
    "NiveauPreuve": "ALIGNEDOC_PARTIEL",
    "CommentaireLecture": "Capacités d'exports et de bundle observables ; richesse des traces et composition exacte du bundle à qualifier honnêtement."
  },
  "Cluster_5_Confidentialite_Roles_MultiTenant": {
    "ContratsInterfaces": [
      "Isolation par organisationId, RLS cible",
      "Aucun accès libre au contenu apprenant non partagé",
      "Exports filtrés par tenant uniquement"
    ],
    "NiveauPreuve": "CIBLE_FERME_AVEC_AVERIFIER",
    "CommentaireLecture": "Doctrine très ferme ; preuve RLS prod et permissions exhaustives par rôle restent AVERIFIER."
  }
}
```

### D.2.3. Scénarios de tests typiques par cluster

```json
{
  "Cluster_4_Exports_Preuve_QualiopiLite": [
    {
      "ScenarioID": "D1_EXP_01",
      "Intitule": "D1 déclenche un export Qualiopi lite pour son organisation et obtient un ZIP sans aucune preuve orpheline, toutes les Evidence étant rattachées à une Trace ou une HugoSession.",
      "TypeTest": "INTEGRATION",
      "SurfaceConcernee": "EXPORTS_BACKOFFICE",
      "RisquesEchec": ["EXP-011", "EXP-016"]
    },
    {
      "ScenarioID": "D1_EXP_02",
      "Intitule": "D1 ne voit dans les exports que des données filtrées par son organisation, sans aucune fuite cross-tenant.",
      "TypeTest": "INTEGRATION",
      "SurfaceConcernee": "EXPORTS_BACKOFFICE",
      "RisquesEchec": ["CONF-11", "CONF-13"]
    }
  ],
  "Cluster_5_Confidentialite_Roles_MultiTenant": [
    {
      "ScenarioID": "D1_CONF_01",
      "Intitule": "D1 ne peut jamais lire le verbatim apprenant non partagé, même via exports ou vues admin.",
      "TypeTest": "INTEGRATION",
      "SurfaceConcernee": "ADMIN_ORG",
      "RisquesEchec": ["CONF-02", "CONF-04", "CONF-09"]
    },
    {
      "ScenarioID": "D1_CONF_02",
      "Intitule": "Une tentative d'accès à des données d'une autre organisation échoue systématiquement (tests cross-tenant).",
      "TypeTest": "UNIT",
      "SurfaceConcernee": "API_BACKEND",
      "RisquesEchec": ["CONF-11", "CONF-12", "CONF-13"]
    }
  ]
}
```

### D.2.4. Niveaux de vérité et garde-fous pour Cursor

- **UsageAudit** : oui (particulièrement pour les domaines 90 et 100).  
- **UsageImpl** : oui (génération de tests d’exports et de non-régression RLS/multi-tenant).  
- **GardeFous** :  
  - marquer `AVERIFIER` pour tout ce qui suppose RLS Postgres prod effective ou équivalence local/distant ;  
  - ne pas présenter les exports Qualiopi lite comme preuve de certification autonome, seulement comme bundle d’aide à l’audit ;  
  - ne jamais attribuer à ORGADMIN un droit générique de lecture du contenu apprenant non partagé, même dans les scénarios de test.
---

## References

1. [specs-interface-2.0.md](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_b6293b86-ebae-4ad6-bc9f-6cbd5fd4b34f/0a476ede-ac43-44da-a9bd-d188bcd07dd8/specs-interface-2.0.md?AWSAccessKeyId=ASIA2F3EMEYEW4BJEHVL&Signature=PZmvMAwj3kJpC9mK8539YNgiPBE%3D&x-amz-security-token=IQoJb3JpZ2luX2VjENr%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJHMEUCIEom08nPqXdxoFIP7aMlFGtfxfegja8uhNPKf8UGJP0OAiEA%2BPUkbbA3F24QMyERGqVzM6gLHjthGZuqyBWaShSA%2BcMq%2FAQIo%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARABGgw2OTk3NTMzMDk3MDUiDB2xuULkfrastNDNpirQBAVpDGx%2BR1MMg9vrGsupMusimLw3lPmIKxSMaic%2Bx92J6RxDT42JJcXvy6cXNsJWFf6MQgAmNgezJX0X%2BjN9L7W6H4TSkCBQDfeuFVnJhDcMMOxKn%2FIOb%2Fdhl5N9WHeS28%2FkpFFgFbPdq4NuDpsY9QZrqqs9bpWwIMfcBxmgbOYmfNeFzNQsw%2FimRRCjCTrPr4j%2F5f9LCnERxiicsVzBE65VBrf%2FiMOxkdSnhJBh6zCc%2B6RY0%2Bc7ePWkmz5ZMaUPKs%2BuHMVgA8Bdm6kpi7xUUNsmOLAg%2BQMw%2BbxBQIU2D%2BefsHWPRPSJRHUx049AkaxqioqIBNQC7gxrWdAMQTnXTw75cCiDjm0Tr5NjL7mjnBb4IhE1iT0Q4CcFIBjqZ1uSY6MMoXGkteLWIcqghWpxa%2F0j3KcF7L%2BKdxrqjcYqWfNfNGDMNyj%2BZpfQDY1SbKUz%2FNoMoryAWKIb6h4LkcaOvzkPhYkOo9JGw%2FFcjjlC8ncd47a3PX0t5MRUtGq8PeoA6vPH9uq82nia5xGU2aHTQyKgQ9KTQdz37QuYUkZPl5LlnCeOFWCd9gOeVXOawLWxNQGbJQjv24SpCbWF%2FjUy49%2BjRhuHVPNx%2FGS8gF0fyCKsLPgc5u1vc0HbxH4e12PuOX9VxZaMPxYlUoJsGbmlTXAMIi4u7EZfkW8aS%2Bzp6IqaIj%2Ff%2B8iQOs3e7RcOX%2BE9Ts8qsm8sNQluGga%2FOKdT1KoyPhG6iCQl1a15lkMB9Ps6bcV%2FjGcJAxsSwKVHQgu0sQ%2B4HsyGY2ydkkvSyg7rsksw9fHO0QY6mAFoxV7V7GNCyOz5Ig3Tz1NPjkX9GNVzecKnJi%2FnyuydrFluxQ5CeBY4oMOt%2F%2F9yxOtzW%2BxG7bnhuVd4gW122DE9fMWra3fT5VRdREvIHe4N%2FJXSp9XAGPD2zp26ZUq20FGI6Aw0ret4WOZ7LIWTIPhXyjJxb6vLCewV7mCeT82HK6hqXwYg6AkIxUxvVAH%2FI5IdiKI2JfVZAA%3D%3D&Expires=1781778120) - - Le tuteur peut recommander des amnagements des situations de travail, suggrer des bascules de mode...

2. [spec_canonique_hugo_2_0.md](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_b6293b86-ebae-4ad6-bc9f-6cbd5fd4b34f/069edac1-ed7f-4701-9c83-ac26699f41b2/spec_canonique_hugo_2_0.md?AWSAccessKeyId=ASIA2F3EMEYEW4BJEHVL&Signature=fZ%2F1pgXTPwNqzkKF9VFfrxcPkhY%3D&x-amz-security-token=IQoJb3JpZ2luX2VjENr%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJHMEUCIEom08nPqXdxoFIP7aMlFGtfxfegja8uhNPKf8UGJP0OAiEA%2BPUkbbA3F24QMyERGqVzM6gLHjthGZuqyBWaShSA%2BcMq%2FAQIo%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARABGgw2OTk3NTMzMDk3MDUiDB2xuULkfrastNDNpirQBAVpDGx%2BR1MMg9vrGsupMusimLw3lPmIKxSMaic%2Bx92J6RxDT42JJcXvy6cXNsJWFf6MQgAmNgezJX0X%2BjN9L7W6H4TSkCBQDfeuFVnJhDcMMOxKn%2FIOb%2Fdhl5N9WHeS28%2FkpFFgFbPdq4NuDpsY9QZrqqs9bpWwIMfcBxmgbOYmfNeFzNQsw%2FimRRCjCTrPr4j%2F5f9LCnERxiicsVzBE65VBrf%2FiMOxkdSnhJBh6zCc%2B6RY0%2Bc7ePWkmz5ZMaUPKs%2BuHMVgA8Bdm6kpi7xUUNsmOLAg%2BQMw%2BbxBQIU2D%2BefsHWPRPSJRHUx049AkaxqioqIBNQC7gxrWdAMQTnXTw75cCiDjm0Tr5NjL7mjnBb4IhE1iT0Q4CcFIBjqZ1uSY6MMoXGkteLWIcqghWpxa%2F0j3KcF7L%2BKdxrqjcYqWfNfNGDMNyj%2BZpfQDY1SbKUz%2FNoMoryAWKIb6h4LkcaOvzkPhYkOo9JGw%2FFcjjlC8ncd47a3PX0t5MRUtGq8PeoA6vPH9uq82nia5xGU2aHTQyKgQ9KTQdz37QuYUkZPl5LlnCeOFWCd9gOeVXOawLWxNQGbJQjv24SpCbWF%2FjUy49%2BjRhuHVPNx%2FGS8gF0fyCKsLPgc5u1vc0HbxH4e12PuOX9VxZaMPxYlUoJsGbmlTXAMIi4u7EZfkW8aS%2Bzp6IqaIj%2Ff%2B8iQOs3e7RcOX%2BE9Ts8qsm8sNQluGga%2FOKdT1KoyPhG6iCQl1a15lkMB9Ps6bcV%2FjGcJAxsSwKVHQgu0sQ%2B4HsyGY2ydkkvSyg7rsksw9fHO0QY6mAFoxV7V7GNCyOz5Ig3Tz1NPjkX9GNVzecKnJi%2FnyuydrFluxQ5CeBY4oMOt%2F%2F9yxOtzW%2BxG7bnhuVd4gW122DE9fMWra3fT5VRdREvIHe4N%2FJXSp9XAGPD2zp26ZUq20FGI6Aw0ret4WOZ7LIWTIPhXyjJxb6vLCewV7mCeT82HK6hqXwYg6AkIxUxvVAH%2FI5IdiKI2JfVZAA%3D%3D&Expires=1781778120) - Le front de Hugo 2.0 doit rendre visible la progression conversationnelle de manire montrable. parti...

3. [ecarts-90_confidentialite_partage_multitenant_roles.md](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_b6293b86-ebae-4ad6-bc9f-6cbd5fd4b34f/5cb658c7-1362-4d9b-ad5b-48944669f091/ecarts-90_confidentialite_partage_multitenant_roles.md?AWSAccessKeyId=ASIA2F3EMEYEW4BJEHVL&Signature=351zygQrOXnXsIYCIaHIYtz6dYs%3D&x-amz-security-token=IQoJb3JpZ2luX2VjENr%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJHMEUCIEom08nPqXdxoFIP7aMlFGtfxfegja8uhNPKf8UGJP0OAiEA%2BPUkbbA3F24QMyERGqVzM6gLHjthGZuqyBWaShSA%2BcMq%2FAQIo%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARABGgw2OTk3NTMzMDk3MDUiDB2xuULkfrastNDNpirQBAVpDGx%2BR1MMg9vrGsupMusimLw3lPmIKxSMaic%2Bx92J6RxDT42JJcXvy6cXNsJWFf6MQgAmNgezJX0X%2BjN9L7W6H4TSkCBQDfeuFVnJhDcMMOxKn%2FIOb%2Fdhl5N9WHeS28%2FkpFFgFbPdq4NuDpsY9QZrqqs9bpWwIMfcBxmgbOYmfNeFzNQsw%2FimRRCjCTrPr4j%2F5f9LCnERxiicsVzBE65VBrf%2FiMOxkdSnhJBh6zCc%2B6RY0%2Bc7ePWkmz5ZMaUPKs%2BuHMVgA8Bdm6kpi7xUUNsmOLAg%2BQMw%2BbxBQIU2D%2BefsHWPRPSJRHUx049AkaxqioqIBNQC7gxrWdAMQTnXTw75cCiDjm0Tr5NjL7mjnBb4IhE1iT0Q4CcFIBjqZ1uSY6MMoXGkteLWIcqghWpxa%2F0j3KcF7L%2BKdxrqjcYqWfNfNGDMNyj%2BZpfQDY1SbKUz%2FNoMoryAWKIb6h4LkcaOvzkPhYkOo9JGw%2FFcjjlC8ncd47a3PX0t5MRUtGq8PeoA6vPH9uq82nia5xGU2aHTQyKgQ9KTQdz37QuYUkZPl5LlnCeOFWCd9gOeVXOawLWxNQGbJQjv24SpCbWF%2FjUy49%2BjRhuHVPNx%2FGS8gF0fyCKsLPgc5u1vc0HbxH4e12PuOX9VxZaMPxYlUoJsGbmlTXAMIi4u7EZfkW8aS%2Bzp6IqaIj%2Ff%2B8iQOs3e7RcOX%2BE9Ts8qsm8sNQluGga%2FOKdT1KoyPhG6iCQl1a15lkMB9Ps6bcV%2FjGcJAxsSwKVHQgu0sQ%2B4HsyGY2ydkkvSyg7rsksw9fHO0QY6mAFoxV7V7GNCyOz5Ig3Tz1NPjkX9GNVzecKnJi%2FnyuydrFluxQ5CeBY4oMOt%2F%2F9yxOtzW%2BxG7bnhuVd4gW122DE9fMWra3fT5VRdREvIHe4N%2FJXSp9XAGPD2zp26ZUq20FGI6Aw0ret4WOZ7LIWTIPhXyjJxb6vLCewV7mCeT82HK6hqXwYg6AkIxUxvVAH%2FI5IdiKI2JfVZAA%3D%3D&Expires=1781778120) - - DOMAINECODE 90confidentialitepartagemultitenantroles - DOMAINELABEL confidentialit, partage, multi...

4. [specs-Orchestrateur-diagnostic-2.0.md](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_b6293b86-ebae-4ad6-bc9f-6cbd5fd4b34f/9da9d80e-dcd7-441e-b4c0-5cc8e75c25fa/specs-Orchestrateur-diagnostic-2.0.md?AWSAccessKeyId=ASIA2F3EMEYEW4BJEHVL&Signature=J2Vl8Nz4LQELkrBwkWvINWp8wjM%3D&x-amz-security-token=IQoJb3JpZ2luX2VjENr%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJHMEUCIEom08nPqXdxoFIP7aMlFGtfxfegja8uhNPKf8UGJP0OAiEA%2BPUkbbA3F24QMyERGqVzM6gLHjthGZuqyBWaShSA%2BcMq%2FAQIo%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARABGgw2OTk3NTMzMDk3MDUiDB2xuULkfrastNDNpirQBAVpDGx%2BR1MMg9vrGsupMusimLw3lPmIKxSMaic%2Bx92J6RxDT42JJcXvy6cXNsJWFf6MQgAmNgezJX0X%2BjN9L7W6H4TSkCBQDfeuFVnJhDcMMOxKn%2FIOb%2Fdhl5N9WHeS28%2FkpFFgFbPdq4NuDpsY9QZrqqs9bpWwIMfcBxmgbOYmfNeFzNQsw%2FimRRCjCTrPr4j%2F5f9LCnERxiicsVzBE65VBrf%2FiMOxkdSnhJBh6zCc%2B6RY0%2Bc7ePWkmz5ZMaUPKs%2BuHMVgA8Bdm6kpi7xUUNsmOLAg%2BQMw%2BbxBQIU2D%2BefsHWPRPSJRHUx049AkaxqioqIBNQC7gxrWdAMQTnXTw75cCiDjm0Tr5NjL7mjnBb4IhE1iT0Q4CcFIBjqZ1uSY6MMoXGkteLWIcqghWpxa%2F0j3KcF7L%2BKdxrqjcYqWfNfNGDMNyj%2BZpfQDY1SbKUz%2FNoMoryAWKIb6h4LkcaOvzkPhYkOo9JGw%2FFcjjlC8ncd47a3PX0t5MRUtGq8PeoA6vPH9uq82nia5xGU2aHTQyKgQ9KTQdz37QuYUkZPl5LlnCeOFWCd9gOeVXOawLWxNQGbJQjv24SpCbWF%2FjUy49%2BjRhuHVPNx%2FGS8gF0fyCKsLPgc5u1vc0HbxH4e12PuOX9VxZaMPxYlUoJsGbmlTXAMIi4u7EZfkW8aS%2Bzp6IqaIj%2Ff%2B8iQOs3e7RcOX%2BE9Ts8qsm8sNQluGga%2FOKdT1KoyPhG6iCQl1a15lkMB9Ps6bcV%2FjGcJAxsSwKVHQgu0sQ%2B4HsyGY2ydkkvSyg7rsksw9fHO0QY6mAFoxV7V7GNCyOz5Ig3Tz1NPjkX9GNVzecKnJi%2FnyuydrFluxQ5CeBY4oMOt%2F%2F9yxOtzW%2BxG7bnhuVd4gW122DE9fMWra3fT5VRdREvIHe4N%2FJXSp9XAGPD2zp26ZUq20FGI6Aw0ret4WOZ7LIWTIPhXyjJxb6vLCewV7mCeT82HK6hqXwYg6AkIxUxvVAH%2FI5IdiKI2JfVZAA%3D%3D&Expires=1781778120) - - Source LOT 3 multipostures, template diagnostic.1 - Extrait - Mission aider lapprenant explorer un...

5. [specs-Orchestrateur-diagnostic-2.0.md](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_b6293b86-ebae-4ad6-bc9f-6cbd5fd4b34f/257f7d24-6b5c-4ca4-ad8b-684f9ef42219/specs-Orchestrateur-diagnostic-2.0.md?AWSAccessKeyId=ASIA2F3EMEYEW4BJEHVL&Signature=B%2BKaEHI58AMvyfvWJ7WeW2p6Zrk%3D&x-amz-security-token=IQoJb3JpZ2luX2VjENr%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJHMEUCIEom08nPqXdxoFIP7aMlFGtfxfegja8uhNPKf8UGJP0OAiEA%2BPUkbbA3F24QMyERGqVzM6gLHjthGZuqyBWaShSA%2BcMq%2FAQIo%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARABGgw2OTk3NTMzMDk3MDUiDB2xuULkfrastNDNpirQBAVpDGx%2BR1MMg9vrGsupMusimLw3lPmIKxSMaic%2Bx92J6RxDT42JJcXvy6cXNsJWFf6MQgAmNgezJX0X%2BjN9L7W6H4TSkCBQDfeuFVnJhDcMMOxKn%2FIOb%2Fdhl5N9WHeS28%2FkpFFgFbPdq4NuDpsY9QZrqqs9bpWwIMfcBxmgbOYmfNeFzNQsw%2FimRRCjCTrPr4j%2F5f9LCnERxiicsVzBE65VBrf%2FiMOxkdSnhJBh6zCc%2B6RY0%2Bc7ePWkmz5ZMaUPKs%2BuHMVgA8Bdm6kpi7xUUNsmOLAg%2BQMw%2BbxBQIU2D%2BefsHWPRPSJRHUx049AkaxqioqIBNQC7gxrWdAMQTnXTw75cCiDjm0Tr5NjL7mjnBb4IhE1iT0Q4CcFIBjqZ1uSY6MMoXGkteLWIcqghWpxa%2F0j3KcF7L%2BKdxrqjcYqWfNfNGDMNyj%2BZpfQDY1SbKUz%2FNoMoryAWKIb6h4LkcaOvzkPhYkOo9JGw%2FFcjjlC8ncd47a3PX0t5MRUtGq8PeoA6vPH9uq82nia5xGU2aHTQyKgQ9KTQdz37QuYUkZPl5LlnCeOFWCd9gOeVXOawLWxNQGbJQjv24SpCbWF%2FjUy49%2BjRhuHVPNx%2FGS8gF0fyCKsLPgc5u1vc0HbxH4e12PuOX9VxZaMPxYlUoJsGbmlTXAMIi4u7EZfkW8aS%2Bzp6IqaIj%2Ff%2B8iQOs3e7RcOX%2BE9Ts8qsm8sNQluGga%2FOKdT1KoyPhG6iCQl1a15lkMB9Ps6bcV%2FjGcJAxsSwKVHQgu0sQ%2B4HsyGY2ydkkvSyg7rsksw9fHO0QY6mAFoxV7V7GNCyOz5Ig3Tz1NPjkX9GNVzecKnJi%2FnyuydrFluxQ5CeBY4oMOt%2F%2F9yxOtzW%2BxG7bnhuVd4gW122DE9fMWra3fT5VRdREvIHe4N%2FJXSp9XAGPD2zp26ZUq20FGI6Aw0ret4WOZ7LIWTIPhXyjJxb6vLCewV7mCeT82HK6hqXwYg6AkIxUxvVAH%2FI5IdiKI2JfVZAA%3D%3D&Expires=1781778120) - - Source LOT 3 multipostures, template diagnostic.1 - Extrait - Mission aider lapprenant explorer un...

6. [specs-formateur-tuteur-2.0.md](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_b6293b86-ebae-4ad6-bc9f-6cbd5fd4b34f/e5a6a344-6cb2-47a5-8d15-1ed6dfc41247/specs-formateur-tuteur-2.0.md?AWSAccessKeyId=ASIA2F3EMEYEW4BJEHVL&Signature=831uiwuTCCeq5FxGRUAQSYJXUqc%3D&x-amz-security-token=IQoJb3JpZ2luX2VjENr%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJHMEUCIEom08nPqXdxoFIP7aMlFGtfxfegja8uhNPKf8UGJP0OAiEA%2BPUkbbA3F24QMyERGqVzM6gLHjthGZuqyBWaShSA%2BcMq%2FAQIo%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARABGgw2OTk3NTMzMDk3MDUiDB2xuULkfrastNDNpirQBAVpDGx%2BR1MMg9vrGsupMusimLw3lPmIKxSMaic%2Bx92J6RxDT42JJcXvy6cXNsJWFf6MQgAmNgezJX0X%2BjN9L7W6H4TSkCBQDfeuFVnJhDcMMOxKn%2FIOb%2Fdhl5N9WHeS28%2FkpFFgFbPdq4NuDpsY9QZrqqs9bpWwIMfcBxmgbOYmfNeFzNQsw%2FimRRCjCTrPr4j%2F5f9LCnERxiicsVzBE65VBrf%2FiMOxkdSnhJBh6zCc%2B6RY0%2Bc7ePWkmz5ZMaUPKs%2BuHMVgA8Bdm6kpi7xUUNsmOLAg%2BQMw%2BbxBQIU2D%2BefsHWPRPSJRHUx049AkaxqioqIBNQC7gxrWdAMQTnXTw75cCiDjm0Tr5NjL7mjnBb4IhE1iT0Q4CcFIBjqZ1uSY6MMoXGkteLWIcqghWpxa%2F0j3KcF7L%2BKdxrqjcYqWfNfNGDMNyj%2BZpfQDY1SbKUz%2FNoMoryAWKIb6h4LkcaOvzkPhYkOo9JGw%2FFcjjlC8ncd47a3PX0t5MRUtGq8PeoA6vPH9uq82nia5xGU2aHTQyKgQ9KTQdz37QuYUkZPl5LlnCeOFWCd9gOeVXOawLWxNQGbJQjv24SpCbWF%2FjUy49%2BjRhuHVPNx%2FGS8gF0fyCKsLPgc5u1vc0HbxH4e12PuOX9VxZaMPxYlUoJsGbmlTXAMIi4u7EZfkW8aS%2Bzp6IqaIj%2Ff%2B8iQOs3e7RcOX%2BE9Ts8qsm8sNQluGga%2FOKdT1KoyPhG6iCQl1a15lkMB9Ps6bcV%2FjGcJAxsSwKVHQgu0sQ%2B4HsyGY2ydkkvSyg7rsksw9fHO0QY6mAFoxV7V7GNCyOz5Ig3Tz1NPjkX9GNVzecKnJi%2FnyuydrFluxQ5CeBY4oMOt%2F%2F9yxOtzW%2BxG7bnhuVd4gW122DE9fMWra3fT5VRdREvIHe4N%2FJXSp9XAGPD2zp26ZUq20FGI6Aw0ret4WOZ7LIWTIPhXyjJxb6vLCewV7mCeT82HK6hqXwYg6AkIxUxvVAH%2FI5IdiKI2JfVZAA%3D%3D&Expires=1781778120) - - Source Contextualisation 1.9, section LOT 5 Base de connaissances formateur.1 - Extrait Finalit pe...

7. [specs-formateur-tuteur-2.0.md](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_b6293b86-ebae-4ad6-bc9f-6cbd5fd4b34f/d59a744b-9e08-41fc-af68-afd5b235f13b/specs-formateur-tuteur-2.0.md?AWSAccessKeyId=ASIA2F3EMEYEW4BJEHVL&Signature=Q3s4OIKVmPEJ%2FAdAKBAcU3I3yQc%3D&x-amz-security-token=IQoJb3JpZ2luX2VjENr%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJHMEUCIEom08nPqXdxoFIP7aMlFGtfxfegja8uhNPKf8UGJP0OAiEA%2BPUkbbA3F24QMyERGqVzM6gLHjthGZuqyBWaShSA%2BcMq%2FAQIo%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARABGgw2OTk3NTMzMDk3MDUiDB2xuULkfrastNDNpirQBAVpDGx%2BR1MMg9vrGsupMusimLw3lPmIKxSMaic%2Bx92J6RxDT42JJcXvy6cXNsJWFf6MQgAmNgezJX0X%2BjN9L7W6H4TSkCBQDfeuFVnJhDcMMOxKn%2FIOb%2Fdhl5N9WHeS28%2FkpFFgFbPdq4NuDpsY9QZrqqs9bpWwIMfcBxmgbOYmfNeFzNQsw%2FimRRCjCTrPr4j%2F5f9LCnERxiicsVzBE65VBrf%2FiMOxkdSnhJBh6zCc%2B6RY0%2Bc7ePWkmz5ZMaUPKs%2BuHMVgA8Bdm6kpi7xUUNsmOLAg%2BQMw%2BbxBQIU2D%2BefsHWPRPSJRHUx049AkaxqioqIBNQC7gxrWdAMQTnXTw75cCiDjm0Tr5NjL7mjnBb4IhE1iT0Q4CcFIBjqZ1uSY6MMoXGkteLWIcqghWpxa%2F0j3KcF7L%2BKdxrqjcYqWfNfNGDMNyj%2BZpfQDY1SbKUz%2FNoMoryAWKIb6h4LkcaOvzkPhYkOo9JGw%2FFcjjlC8ncd47a3PX0t5MRUtGq8PeoA6vPH9uq82nia5xGU2aHTQyKgQ9KTQdz37QuYUkZPl5LlnCeOFWCd9gOeVXOawLWxNQGbJQjv24SpCbWF%2FjUy49%2BjRhuHVPNx%2FGS8gF0fyCKsLPgc5u1vc0HbxH4e12PuOX9VxZaMPxYlUoJsGbmlTXAMIi4u7EZfkW8aS%2Bzp6IqaIj%2Ff%2B8iQOs3e7RcOX%2BE9Ts8qsm8sNQluGga%2FOKdT1KoyPhG6iCQl1a15lkMB9Ps6bcV%2FjGcJAxsSwKVHQgu0sQ%2B4HsyGY2ydkkvSyg7rsksw9fHO0QY6mAFoxV7V7GNCyOz5Ig3Tz1NPjkX9GNVzecKnJi%2FnyuydrFluxQ5CeBY4oMOt%2F%2F9yxOtzW%2BxG7bnhuVd4gW122DE9fMWra3fT5VRdREvIHe4N%2FJXSp9XAGPD2zp26ZUq20FGI6Aw0ret4WOZ7LIWTIPhXyjJxb6vLCewV7mCeT82HK6hqXwYg6AkIxUxvVAH%2FI5IdiKI2JfVZAA%3D%3D&Expires=1781778120) - - Source Contextualisation 1.9, section LOT 5 Base de connaissances formateur.1 - Extrait Finalit pe...

8. [ecarts-100_exports_preuves_qualiopi_lite.md](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_b6293b86-ebae-4ad6-bc9f-6cbd5fd4b34f/434c8e11-41df-4978-8ef6-3247e145b266/ecarts-100_exports_preuves_qualiopi_lite.md?AWSAccessKeyId=ASIA2F3EMEYEW4BJEHVL&Signature=qgF%2BphqstV5JnPqMZsPXBKK6Ffk%3D&x-amz-security-token=IQoJb3JpZ2luX2VjENr%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJHMEUCIEom08nPqXdxoFIP7aMlFGtfxfegja8uhNPKf8UGJP0OAiEA%2BPUkbbA3F24QMyERGqVzM6gLHjthGZuqyBWaShSA%2BcMq%2FAQIo%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARABGgw2OTk3NTMzMDk3MDUiDB2xuULkfrastNDNpirQBAVpDGx%2BR1MMg9vrGsupMusimLw3lPmIKxSMaic%2Bx92J6RxDT42JJcXvy6cXNsJWFf6MQgAmNgezJX0X%2BjN9L7W6H4TSkCBQDfeuFVnJhDcMMOxKn%2FIOb%2Fdhl5N9WHeS28%2FkpFFgFbPdq4NuDpsY9QZrqqs9bpWwIMfcBxmgbOYmfNeFzNQsw%2FimRRCjCTrPr4j%2F5f9LCnERxiicsVzBE65VBrf%2FiMOxkdSnhJBh6zCc%2B6RY0%2Bc7ePWkmz5ZMaUPKs%2BuHMVgA8Bdm6kpi7xUUNsmOLAg%2BQMw%2BbxBQIU2D%2BefsHWPRPSJRHUx049AkaxqioqIBNQC7gxrWdAMQTnXTw75cCiDjm0Tr5NjL7mjnBb4IhE1iT0Q4CcFIBjqZ1uSY6MMoXGkteLWIcqghWpxa%2F0j3KcF7L%2BKdxrqjcYqWfNfNGDMNyj%2BZpfQDY1SbKUz%2FNoMoryAWKIb6h4LkcaOvzkPhYkOo9JGw%2FFcjjlC8ncd47a3PX0t5MRUtGq8PeoA6vPH9uq82nia5xGU2aHTQyKgQ9KTQdz37QuYUkZPl5LlnCeOFWCd9gOeVXOawLWxNQGbJQjv24SpCbWF%2FjUy49%2BjRhuHVPNx%2FGS8gF0fyCKsLPgc5u1vc0HbxH4e12PuOX9VxZaMPxYlUoJsGbmlTXAMIi4u7EZfkW8aS%2Bzp6IqaIj%2Ff%2B8iQOs3e7RcOX%2BE9Ts8qsm8sNQluGga%2FOKdT1KoyPhG6iCQl1a15lkMB9Ps6bcV%2FjGcJAxsSwKVHQgu0sQ%2B4HsyGY2ydkkvSyg7rsksw9fHO0QY6mAFoxV7V7GNCyOz5Ig3Tz1NPjkX9GNVzecKnJi%2FnyuydrFluxQ5CeBY4oMOt%2F%2F9yxOtzW%2BxG7bnhuVd4gW122DE9fMWra3fT5VRdREvIHe4N%2FJXSp9XAGPD2zp26ZUq20FGI6Aw0ret4WOZ7LIWTIPhXyjJxb6vLCewV7mCeT82HK6hqXwYg6AkIxUxvVAH%2FI5IdiKI2JfVZAA%3D%3D&Expires=1781778120) - Restent explicitement AVERIFIER - le comportement exact du runtime distant sur les exports et bundle...

9. [ecarts-40_base_connaissances_formateur.md](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_b6293b86-ebae-4ad6-bc9f-6cbd5fd4b34f/4642d734-9ae6-492d-82a0-1209e952e559/ecarts-40_base_connaissances_formateur.md?AWSAccessKeyId=ASIA2F3EMEYEW4BJEHVL&Signature=rpLQGNdYhwIPOsiwuVJVQBGSB%2B4%3D&x-amz-security-token=IQoJb3JpZ2luX2VjENr%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJHMEUCIEom08nPqXdxoFIP7aMlFGtfxfegja8uhNPKf8UGJP0OAiEA%2BPUkbbA3F24QMyERGqVzM6gLHjthGZuqyBWaShSA%2BcMq%2FAQIo%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARABGgw2OTk3NTMzMDk3MDUiDB2xuULkfrastNDNpirQBAVpDGx%2BR1MMg9vrGsupMusimLw3lPmIKxSMaic%2Bx92J6RxDT42JJcXvy6cXNsJWFf6MQgAmNgezJX0X%2BjN9L7W6H4TSkCBQDfeuFVnJhDcMMOxKn%2FIOb%2Fdhl5N9WHeS28%2FkpFFgFbPdq4NuDpsY9QZrqqs9bpWwIMfcBxmgbOYmfNeFzNQsw%2FimRRCjCTrPr4j%2F5f9LCnERxiicsVzBE65VBrf%2FiMOxkdSnhJBh6zCc%2B6RY0%2Bc7ePWkmz5ZMaUPKs%2BuHMVgA8Bdm6kpi7xUUNsmOLAg%2BQMw%2BbxBQIU2D%2BefsHWPRPSJRHUx049AkaxqioqIBNQC7gxrWdAMQTnXTw75cCiDjm0Tr5NjL7mjnBb4IhE1iT0Q4CcFIBjqZ1uSY6MMoXGkteLWIcqghWpxa%2F0j3KcF7L%2BKdxrqjcYqWfNfNGDMNyj%2BZpfQDY1SbKUz%2FNoMoryAWKIb6h4LkcaOvzkPhYkOo9JGw%2FFcjjlC8ncd47a3PX0t5MRUtGq8PeoA6vPH9uq82nia5xGU2aHTQyKgQ9KTQdz37QuYUkZPl5LlnCeOFWCd9gOeVXOawLWxNQGbJQjv24SpCbWF%2FjUy49%2BjRhuHVPNx%2FGS8gF0fyCKsLPgc5u1vc0HbxH4e12PuOX9VxZaMPxYlUoJsGbmlTXAMIi4u7EZfkW8aS%2Bzp6IqaIj%2Ff%2B8iQOs3e7RcOX%2BE9Ts8qsm8sNQluGga%2FOKdT1KoyPhG6iCQl1a15lkMB9Ps6bcV%2FjGcJAxsSwKVHQgu0sQ%2B4HsyGY2ydkkvSyg7rsksw9fHO0QY6mAFoxV7V7GNCyOz5Ig3Tz1NPjkX9GNVzecKnJi%2FnyuydrFluxQ5CeBY4oMOt%2F%2F9yxOtzW%2BxG7bnhuVd4gW122DE9fMWra3fT5VRdREvIHe4N%2FJXSp9XAGPD2zp26ZUq20FGI6Aw0ret4WOZ7LIWTIPhXyjJxb6vLCewV7mCeT82HK6hqXwYg6AkIxUxvVAH%2FI5IdiKI2JfVZAA%3D%3D&Expires=1781778120) - - DOMAINECODE 40baseconnaissancesformateur - DOMAINELABEL base de connaissances formateur --- TITLE ...

10. [ecarts-50_orchestrateur_formateur.md](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_b6293b86-ebae-4ad6-bc9f-6cbd5fd4b34f/c6e8559c-62c1-4c16-8b23-b50fba3738aa/ecarts-50_orchestrateur_formateur.md?AWSAccessKeyId=ASIA2F3EMEYEW4BJEHVL&Signature=laeHMddjnwCLLIPuMJICNicte0A%3D&x-amz-security-token=IQoJb3JpZ2luX2VjENr%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJHMEUCIEom08nPqXdxoFIP7aMlFGtfxfegja8uhNPKf8UGJP0OAiEA%2BPUkbbA3F24QMyERGqVzM6gLHjthGZuqyBWaShSA%2BcMq%2FAQIo%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARABGgw2OTk3NTMzMDk3MDUiDB2xuULkfrastNDNpirQBAVpDGx%2BR1MMg9vrGsupMusimLw3lPmIKxSMaic%2Bx92J6RxDT42JJcXvy6cXNsJWFf6MQgAmNgezJX0X%2BjN9L7W6H4TSkCBQDfeuFVnJhDcMMOxKn%2FIOb%2Fdhl5N9WHeS28%2FkpFFgFbPdq4NuDpsY9QZrqqs9bpWwIMfcBxmgbOYmfNeFzNQsw%2FimRRCjCTrPr4j%2F5f9LCnERxiicsVzBE65VBrf%2FiMOxkdSnhJBh6zCc%2B6RY0%2Bc7ePWkmz5ZMaUPKs%2BuHMVgA8Bdm6kpi7xUUNsmOLAg%2BQMw%2BbxBQIU2D%2BefsHWPRPSJRHUx049AkaxqioqIBNQC7gxrWdAMQTnXTw75cCiDjm0Tr5NjL7mjnBb4IhE1iT0Q4CcFIBjqZ1uSY6MMoXGkteLWIcqghWpxa%2F0j3KcF7L%2BKdxrqjcYqWfNfNGDMNyj%2BZpfQDY1SbKUz%2FNoMoryAWKIb6h4LkcaOvzkPhYkOo9JGw%2FFcjjlC8ncd47a3PX0t5MRUtGq8PeoA6vPH9uq82nia5xGU2aHTQyKgQ9KTQdz37QuYUkZPl5LlnCeOFWCd9gOeVXOawLWxNQGbJQjv24SpCbWF%2FjUy49%2BjRhuHVPNx%2FGS8gF0fyCKsLPgc5u1vc0HbxH4e12PuOX9VxZaMPxYlUoJsGbmlTXAMIi4u7EZfkW8aS%2Bzp6IqaIj%2Ff%2B8iQOs3e7RcOX%2BE9Ts8qsm8sNQluGga%2FOKdT1KoyPhG6iCQl1a15lkMB9Ps6bcV%2FjGcJAxsSwKVHQgu0sQ%2B4HsyGY2ydkkvSyg7rsksw9fHO0QY6mAFoxV7V7GNCyOz5Ig3Tz1NPjkX9GNVzecKnJi%2FnyuydrFluxQ5CeBY4oMOt%2F%2F9yxOtzW%2BxG7bnhuVd4gW122DE9fMWra3fT5VRdREvIHe4N%2FJXSp9XAGPD2zp26ZUq20FGI6Aw0ret4WOZ7LIWTIPhXyjJxb6vLCewV7mCeT82HK6hqXwYg6AkIxUxvVAH%2FI5IdiKI2JfVZAA%3D%3D&Expires=1781778120) - - DOMAINECODE 50orchestrateurformateur - DOMAINELABEL orchestrateur formateur --- TITLE 00rapporteca...

