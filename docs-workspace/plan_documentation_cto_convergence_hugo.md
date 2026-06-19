# Plan de documentation de convergence Hugo réel → Hugo 2.0

## Objet du document

Ce document sert de note de cadrage à placer en bibliothèque pour rappeler les enjeux du chantier de convergence et fixer un plan de documentation exploitable par un CTO qui doit faire évoluer Hugo réel proprement, rapidement, et sans repartir d'une base théorique déconnectée du code existant.

Il vise un contexte précis : partir d'un socle local « fast & (not so) dirty », sécuriser les décisions de développement à court terme, et produire une documentation de travail qui évite les erreurs déjà identifiées dans le workspace, notamment la confusion entre cible 2.0 et réel observé, le recentrage de la vérité sur le front, et la promotion du verbatim brut comme mémoire principale.

## Enjeux du chantier

Hugo 2.0 est défini comme un moteur tutoriel multi-postures piloté par état, avec backend Django orchestré, P0 conservé, TutorPrompt comme pivot runtime, progression conversationnelle, mémoire gouvernée et UIState dérivé côté serveur ; cette architecture cible ne doit jamais être relue comme une preuve que le code local livre déjà tous ces objets sous leur forme canonique.

L'enjeu principal n'est donc pas de « réécrire Hugo » mais de converger proprement à partir du réel : stabiliser les couches déjà présentes, corriger les ambiguïtés documentaires, standardiser quelques contrats clés, et préparer des extensions futures sans casser l'architecture locale ni sur-promettre ce qui n'est pas encore prouvé dans le runtime.

Le lot courant a déjà été implicitement réduit sur les zones les plus risquées : la mémoire gouvernée doit être lue par défaut comme mémoire intra-conversation implémentable maintenant, tandis que l'inter-sessions reste doctrinalement préparé mais hors périmètre d'implémentation immédiat.

Le même principe de réduction de risque vaut pour le reste du chantier : RAG lexical observé plutôt que RAG vectoriel supposé, branche terminale d'évaluation utilisable mais sobre, standardisation progressive des CTA synthèse/évaluation, et refus d'exposer les champs P0 ou le verbatim brut au front produit.

## Principes directeurs pour le CTO

Le premier principe est de toujours séparer les niveaux de vérité : réel observé, cible spécifiée, écarts confirmés, points A_VERIFIER et hypothèses de convergence. Une spec, un complément ou une note d'interface ne prouve jamais à elle seule qu'une fonctionnalité est livrée dans Hugo réel.

Le deuxième principe est backend-first : la source de vérité comportementale reste la combinaison backend Django orchestré, P0, progression, mémoire gouvernée, TutorPrompt et règles produit. Le front consomme des états dérivés propres via UIState et ne doit ni piloter le moteur, ni exposer des données techniques brutes.

Le troisième principe est de partir du code et des audits réels avant de raffiner la cible. Pour le réel, la méthode impose de faire primer les docs-workspace 00–05 et 07–10, puis les rapports d'écarts de domaine ; pour la cible, elle impose de partir de la spec canonique 2.0 et de ses compléments, puis du glossaire comme pont de vocabulaire, jamais comme preuve autonome d'implémentation.

Le quatrième principe est d'éviter la refonte prématurée. Quand un socle réel existe déjà — mémoire de session, endpoints d'évaluation, RAG backend, objets TrainerKnowledgeItem, signaux qualité post-conversation — la bonne trajectoire consiste d'abord à clarifier, renommer proprement, standardiser les contrats minimaux et auditer les points critiques avant d'ouvrir des chantiers lourds.

## Gabarit canonique de protocole de test Hugo 2.0

Chaque protocole de test Hugo 2.0 doit respecter la structure suivante.
Ce gabarit est la référence unique pour tous les scénarios de test
(personae × fonctions × domaines).

### 1. En-tête et niveau de preuve

```markdown
# PROTOCOLE {ID} — {Titre synthétique}

### Niveau de preuve ciblé

- Cible 2.0 : {oui/non}
- Implémenté observable dans le runtime audité : {oui/non/partiel}
- Dépendances runtime distant / prod / flags : {oui/non}
- Points explicitement AVERIFIER dans ce test :
  - …
```

Si `Dépendances runtime distant / prod / flags = oui`, ajouter le bloc suivant :

```markdown
### Dépendance au runtime distant / prod

Ce protocole :
- [ ] ne dépend que du backend local audité
- [x] dépend du runtime distant / prod / flags inconnus → marquer AVERIFIER

Conséquence :
- Toute conclusion de conformité sur ce point doit être considérée comme AVERIFIER
  tant qu’un audit ciblé prod n’a pas été mené.
```

### 2. Rôle testé et matrice de référence

```markdown
### Rôle testé

- Rôle : {Apprenant / Tuteur / Formateur / Coordinateur / ORGADMIN / Superadmin technique}
- Référence matrice : voir “Matrice rôle × voit / peut / ne voit pas”.

Les étapes et oracles du protocole doivent rester compatibles avec cette matrice.
```

### 3. Pré-requis

```markdown
## Pré-requis

- …
```

### 4. Garde-fous confidentialité / multi-tenant (obligatoires pour tout rôle non-apprenant)

```markdown
## Garde-fous confidentialité / multi-tenant (obligatoires)

- Vérifier que le rôle testé :
  - ne voit pas le verbatim non partagé de l’apprenant ;
  - ne voit pas les champs P0 ou TurnState bruts ;
  - ne peut pas accéder à des données d’une autre organisation ;
  - ne peut pas lire d’export ou de bundle contenant du contenu non partagé.

- Résultat à consigner :
  - [ ] conforme à la cible ET observable dans le local audité
  - [ ] conforme à la cible MAIS niveau de preuve AVERIFIER
  - [ ] non conforme (décrire précisément).
```

### 5. Étapes du test

```markdown
## Étapes

1. …
2. …
```

### 6. Oracle (incluant exports / preuves si concerné)

```markdown
## Oracle

- Résultat attendu côté UX / API :
  - …

- Si le scénario touche exports / preuves / Qualiopi lite :

  ### Oracle exports / preuves

  - Capacité nominale attendue :
    - [ ] un bundle ou export est produit.
    - [ ] les preuves sont rattachées à une trace ou une session (aucune Evidence orpheline).

  - Richesse effective :
    - [ ] documentée et vérifiée dans ce test
    - [ ] partiellement vérifiée
    - [ ] non vérifiable dans ce protocole (marquer AVERIFIER)

  - Invariants spécifiques :
    - [ ] EXIF supprimés sur les photos
    - [ ] GPS uniquement si opt-in explicite.
```

### 7. Points AVERIFIER spécifiques (optionnel)

```markdown
### Points AVERIFIER spécifiques

- …
```

---

Tout protocole existant peut être migré vers ce gabarit à la demande, mais **dès aujourd’hui**, tout nouveau protocole doit être créé en copiant-collant ce bloc gabarit depuis ce document.  

---

## Patch 2 — Matrice rôle × voit / peut / ne voit pas

**But**: ne l’écrire qu’une seule fois, et y référer partout (tests, specs, écarts).

### 2.1. Document cible et emplacement

- **Document**: `spec_canonique_hugo_2_0.md`  
- **Emplacement**: immédiatement après la section existante sur les rôles (section 25 “Rôles”) ou, si elle existe déjà, en remplaçant/ancrant la matrice rôle existante.

Tu ajoutes / remplaces par :

```markdown
## Matrice canonique rôle × voit / peut / ne voit pas (Hugo 2.0)

Cette matrice est la référence unique pour :
- la définition des surfaces UI par rôle,
- les tests de confidentialité / multi-tenant,
- les oracles des scénarios de test.

| Rôle      | Ce qu’il doit voir                                               | Ce qu’il peut faire                                             | Ce qu’il ne doit jamais voir                                      |
|----------|------------------------------------------------------------------|-----------------------------------------------------------------|-------------------------------------------------------------------|
| Apprenant| scène de séance, progression, quête active, posture si exposée, CTA de synthèse/évaluation, objets persistants visibles | converser, choisir une posture dans les limites prévues, confirmer/partager certains objets, déclencher synthèse/évaluation si éligible | verbatim d’autres apprenants, P0 brut, TurnState, prompts complets, logs internes |
| Tuteur   | progression, signaux de blocage, traces partagées, synthèses et évaluations partageables, vues cohorte autorisées | lire, commenter, recommander, préparer un accompagnement, valider certaines traces partageables | verbatim non partagé de l’apprenant, P0, TurnState, RAG brut, historique complet non filtré |
| Formateur| documents de référence, orchestrateur formateur, items de connaissance et leurs statuts, liens référentiels | uploader, expliciter, structurer, corriger, valider, rattacher au référentiel, déclencher certains exports métier | contenu apprenant non partagé, P0 brut, verbatim interne non partagé |
| Coordinateur | vues métier consolidées (à préciser), états de progression agrégés, indicateurs de couverture (cible partiellement ouverte) | coordonner, planifier, valider certains jalons organisationnels selon habilitations (cible à préciser) | lecture libre du contenu apprenant non partagé, P0 brut, logs internes |
| ORGADMIN | administration minimale de l’organisation (utilisateurs, groupes, paramètres non sensibles), exports filtrés par organisation | créer/éditer des comptes, rattacher à des groupes/cohortes, déclencher des exports structuré filtrés | lecture libre du contenu apprenant non partagé, P0, TurnState, verbatim interne, traces non partagées |
| Superadmin technique | surfaces de debug / observabilité filtrées, paramètres bornés d’orchestrateurs et d’évaluation | supervision technique, réglages bornés, analyse d’incidents, exports techniques en environnement de test | lecture applicative libre du contenu apprenant non partagé, contournement du multi-tenant, accès brut P0/verbatim |

Les protocoles de test doivent toujours se référer à cette matrice.
Toute divergence observée doit être documentée comme écart dans les rapports de domaine.
```

Ensuite, dans tes docs de tests et d’écarts (90, 100, etc.), tu peux écrire simplement : “voir matrice canonique rôle × voit / peut / ne voit pas dans `spec_canonique_hugo_2_0.md`”.

---

## Patch 3 — Marqueurs AVERIFIER et runtime distant sur le domaine confidentialité/exports

**But**: éviter de dupliquer la logique “ne pas déduire prod distant du local” et “marquer AVERIFIER” dans chaque protocole.

### 3.1. Document cible et emplacement (confidentialité / multi‑tenant / rôles)

- **Document**: `ecarts — 90_confidentialite_partage_multitenant_roles.md`  
- **Emplacement**: dans la partie “Décisions de structure documentaire” / “Garde-fous” (vers la fin du doc, là où sont listées les décisions CONFDOC‑0x).

Tu ajoutes un bloc explicitement pour les tests :

```markdown
## Règles transverses pour les protocoles de test (domaine 90)

Les protocoles de test qui touchent à ce domaine doivent respecter les règles suivantes :

1. **Toujours inclure une section “Niveau de preuve ciblé”** en en-tête du protocole,
   distinguant clairement :
   - cible 2.0,
   - implémenté observable dans le runtime local audité,
   - dépendances au runtime distant / prod / flags (à marquer AVERIFIER).

2. **Marquer explicitement comme AVERIFIER** toute conclusion ou scénario qui :
   - dépend de la variante distante (ex. `hugoback.encoors.com`),
   - suppose une RLS Postgres effective en production,
   - s’appuie sur des comportements non audités bout en bout.

3. **Pour tout protocole impliquant un rôle non-apprenant** (tuteur, formateur, coordinateur, ORGADMIN, superadmin technique),
   il est obligatoire d’ajouter un bloc “Garde-fous confidentialité / multi-tenant” vérifiant :
   - l’absence de lecture du verbatim non partagé,
   - l’absence de lecture de P0/TurnState bruts,
   - l’absence d’accès inter-tenant,
   - l’absence de lecture d’exports ou bundles contenant du contenu non partagé.
```

Une seule fois ici, et dans les templates/tests tu peux te contenter de dire “conforme aux règles de tests du domaine 90”.

### 3.2. Document cible et emplacement (exports / preuves / Qualiopi lite)

- **Document**: `ecarts-100_exports_preuves_qualiopi_lite.md`  
- **Emplacement**: dans la section “Décisions documentaires” (D7, D8, D9, D11, D13, D15…) où tu cadences déjà la doc.

Tu ajoutes :

```markdown
## Règles transverses pour les protocoles de test (domaine 100)

Pour tous les scénarios de test qui impliquent exports, preuves ou bundles (dont Qualiopi lite) :

1. **Ne jamais présumer un bundle “riche” par défaut.**
   L’oracle doit distinguer :
   - la capacité nominale (bundle ou export produit, preuves rattachées à une trace ou une session),
   - la richesse effective (documentée, partielle, ou non vérifiable → AVERIFIER).

2. **Tester systématiquement les invariants suivants** :
   - aucune Evidence orpheline (toute preuve est rattachée à une trace ou une session),
   - EXIF supprimés par défaut sur les photos,
   - GPS uniquement en opt-in explicite,
   - respect du partage explicite (shareSummary / shareEvidence / shareVerbatim).

3. **Marquer comme AVERIFIER** :
   - tout ce qui concerne la composition exacte des bundles en environnement distant,
   - toute conclusion sur les permissions fines par rôle en prod,
   - toute équivalence supposée entre runtime local et distant.

Ces règles sont obligatoires pour toute nouvelle écriture ou révision de protocole de test sur ce domaine.
```

---

Avec ces 3 patches globaux :

- tu définis un **gabarit unique** de protocole (Patch 1),
- tu poses une **matrice de rôles unique** (Patch 2),
- tu centralises les règles “AVERIFIER / runtime distant / exports” dans **2 docs de domaine** (Patch 3).

Ensuite, quand tu touches un protocole de test, tu te contentes de :

- mettre son en-tête au format du gabarit,
- pointer vers la matrice de rôles,
- indiquer “conforme aux règles de test du domaine 90/100” sans re-décrire la logique.

Si tu veux, je peux maintenant t’écrire le patch concret à copier‑coller dans `plan_documentation_cto_convergence_hugo.md` (version finale du gabarit complet, prêt à coller).

### 8. Rattachement aux domaines d’écarts

Tout protocole doit, en pied de document, préciser les domaines d’écarts qu’il couvre
et se déclarer conforme aux règles de test de ces domaines :

```markdown
### Domaines d’écarts couverts

- 90_confidentialite_partage_multitenant_roles : conforme aux règles de test du domaine 90.
- 100_exportspreuvesqualiopilite : conforme aux règles de test du domaine 100.
- Autres domaines concernés : …
```

Pour les domaines 90 et 100, cela signifie que le protocole :
- applique la structure “Niveau de preuve ciblé”,
- marque comme AVERIFIER toute dépendance au runtime distant / prod / RLS Postgres non auditée,
- applique les garde-fous de confidentialité / multi-tenant pour tout rôle non-apprenant,
- utilise l’oracle exports / preuves dès qu’il y a des traces, preuves ou bundles.

## Ce qui sera effectivement développé sur la version locale

### 1. Mémoire gouvernée intra-conversation

Le développement local doit viser une mémoire gouvernée utile sur le fil courant seulement : résumé backend, sans verbatim brut, sans exposition front dédiée, et sans dépendance runtime à une mémoire inter-sessions injectée dans l'orchestrateur.

Concrètement, cela implique de stabiliser la lecture/écriture de mémoire de session, de clarifier le rôle de `buildsessionmemory` / `sessionmemory.py`, d'auditer le contenu réel de `GET /hugo/sessions/{id}/memory-summary`, et de documenter explicitement que LearnerThemeMemory et MemoryConsolidator restent des ancrages de convergence mais non des capacités inter-sessions livrées dans ce lot.

### 2. Standardisation des actions terminales

Le lot doit standardiser les actions terminales de synthèse et d'évaluation : états backend d'éligibilité, projection propre dans UIState, comportement homogène des CTA côté front, et discours produit explicite sur l'absence de certification automatique par Hugo.

Cela suppose de partir des workflows et endpoints déjà observés — request-evaluation, finalize-evaluation, evaluation-readiness, generate-trace et les actions de synthèse — puis de définir un contrat minimum d'états visibles et de raisons de blocage, sans sur-vendre la richesse actuelle de la trace générée.

### 3. RAG documentaire et hiérarchie de contexte

Le chantier local doit documenter et respecter le niveau réel du documentaire : RAG lexical backend, question-driven, utilisé comme renfort situé, et non comme mémoire principale ni moteur de cours.

La hiérarchie de contexte cible peut rester souple et testable dans ce lot, mais la documentation doit déjà indiquer clairement que l'état et la mémoire utile priment sur le renfort documentaire, et que toute sophistication ultérieure du contexte devra rester addititive, testée et compatible avec l'architecture existante.

### 4. Évaluation, traces et preuves

Le développement local peut assumer une branche terminale d'évaluation utilisable, à condition de la documenter honnêtement : trace minimale, validation finale humaine, pas de certification autonome, et mapping encore partiel entre EvaluationTrace doctrinale et objets réels comme LearnerEvaluationRecord, Trace et Evidence.

L'objectif n'est pas d'enrichir immédiatement toute la chaîne d'évaluation, mais de sécuriser ce qui existe déjà, d'en faire une surface standardisable, et de fournir un contrat cible conceptuel qui guide les évolutions futures sans prétendre qu'elles sont déjà en service.

## Plan de documentation à produire pour permettre un dev propre et rapide

Le plan documentaire doit produire des artefacts courts, reliés au réel, directement actionnables par un CTO. La cible n'est pas une bibliothèque de specs abstraites, mais une base de pilotage qui transforme un existant hétérogène en trajectoire de convergence lisible.

### Bloc A — Notes de cadrage exécutives

Produire 4 notes synthétiques, chacune de 1 à 3 pages, lisibles sans replonger dans tout le corpus :

- **Mémoire gouvernée — lot courant** : ce qui est livré maintenant, ce qui reste extension préparée, quelles règles ne pas violer.
- **Actions terminales — synthèse & évaluation** : ce qui est standardisé dans ce lot, états backend, portée produit, limites explicites.
- **RAG lexical & hiérarchie de contexte** : niveau réel observé, rôle exact du documentaire, garde-fous anti-survente.
- **Évaluation / traces / preuves** : socle réel existant, contrat cible minimal, zones encore ambiguës.

Ces notes doivent systématiquement suivre le même patron : objet, sources mobilisées, réel confirmé, cible 2.0, écarts confirmés, A_VERIFIER, décisions retenues.

### Bloc B — Contrats cibles minimaux

Produire ensuite les contrats minimaux nécessaires au développement local, sous forme courte mais précise :

| Contrat | Contenu attendu | Usage CTO/dev |
|---------|-----------------|---------------|
| Mémoire intra-conversation | Schéma JSON minimal, rubriques autorisées, interdits, service producteur, service consommateur  | Stabiliser backend mémoire sans ouvrir l'inter-sessions |
| CTA synthèse / évaluation | États d'éligibilité, blocages, champs UIState, mapping endpoint ↔ bouton  | Standardiser front + backend sur les actions terminales |
| RAG lexical gouverné | Rôle exact, place dans le pipeline, limites, vocabulaire à employer  | Empêcher la dérive documentaire et les fausses attentes techniques |
| EvaluationTrace conceptuelle minimale | Schéma cible de haut niveau, relations avec LearnerEvaluationRecord / Trace / Evidence  | Guider les évolutions sans prétendre que le runtime est déjà aligné |

Ces contrats doivent être écrits comme des contrats de convergence : assez précis pour coder, assez prudents pour ne pas transformer une cible en fait observé.

### Bloc C — Dossiers de domaine standardisés

Pour chaque domaine critique, conserver ou compléter la chaîne documentaire en quatre artefacts déjà recommandée par la méthode : rapport d'écarts, matrice d'écarts, décisions documentaires, backlog d'actions.

L'objectif n'est pas de réécrire cette chaîne à chaque fois, mais de s'en servir comme colonne vertébrale de travail sur les domaines prioritaires : 20 mémoire gouvernée, 30 référentiel/documentaire/RAG, 70 évaluation/traces/preuves, puis 80 observabilité si nécessaire.

### Bloc D — Backlog CTO exploitable

Le backlog CTO doit être séparé par type d'action et relié à des preuves documentaires. Chaque ligne doit porter au minimum : type, priorité, description courte, source d'écart, dépendances, livrable attendu.

La structure recommandée est la suivante :

- **DOC** : mettre à jour la spec canonique, les compléments, la spec interface, les notes de frontiere de domaine.
- **CODE** : audits ciblés, standardisation de services ou endpoints, ajout de champs UIState, homogénéisation de comportements.
- **OPS** : templates Cursor, checklists d'audit, procédures de vérification locale vs distant.

Le backlog ne doit pas être une roadmap floue. Il doit rester un backlog de convergence articulé au réel observé et à la cible retenue pour le lot courant.

## Ordre de production recommandé

Pour que le CTO puisse faire un dev rapide sans perdre la propreté du chantier, l'ordre de production documentaire doit suivre la dépendance réelle du code et non la nostalgie des anciennes specs.

1. **Contrat mémoire intra-conversation** — parce qu'il fixe immédiatement ce que le moteur lit et écrit dans la session courante.
2. **Contrat CTA synthèse / évaluation** — parce qu'il fixe ce que le front standardise et ce que les endpoints doivent soutenir proprement.
3. **Note RAG lexical / contexte** — parce qu'elle évite de prendre des raccourcis documentaires dangereux pendant le dev.
4. **Contrat conceptuel EvaluationTrace minimale** — parce qu'il donne une cible de convergence sans forcer un refactoring immédiat du runtime.
5. **Backlog CTO unifié** — parce qu'il transforme les quatre éléments précédents en plan d'exécution ordonné.

## Garde-fous rédactionnels et techniques à rappeler en bibliothèque

Les garde-fous suivants doivent apparaître explicitement dans la note et dans les futurs documents de travail :

- La spec 2.0 décrit la cible, pas l'état livré.
- Le glossaire raccorde les noms, il ne prouve pas l'implémentation.
- Le front n'est pas la source de vérité comportementale ; UIState est une traduction produit, pas une logique moteur.
- Aucun champ P0 brut ne doit être exposé au front produit.
- Le verbatim brut ne doit jamais devenir la mémoire principale.
- L'inter-sessions mémoire est préparé, pas livré dans ce lot.
- Le RAG réel doit être décrit comme lexical et gouverné tant qu'aucune preuve runtime plus forte n'existe.
- L'évaluation terminale ne doit jamais être documentée comme certification autonome ; la validation finale reste humaine.
- Tout point dépendant du runtime distant, d'un flag ou d'une variante non auditée doit rester marqué A_VERIFIER.

## Résultat attendu pour le CTO

Si ce plan est suivi, le CTO dispose d'une base simple et robuste pour travailler : un rappel clair des enjeux, des contrats minimaux permettant de coder vite sans casser la doctrine, un backlog hiérarchisé, et une documentation qui transforme un existant hétérogène en chantier de convergence pilotable.

Le bénéfice recherché n'est pas seulement documentaire. Il est opérationnel : réduire les ambiguïtés, limiter les faux refactorings, éviter la sur-promesse produit, et permettre un développement local plus propre, plus additif et plus rapide à converger vers Hugo 2.0.

## Trajectoire de convergence – étapes 5 à 8 (vague encadrants & couronne)

Cette section complète le plan initial centré sur le lot courant (mémoire intra, CTA, RAG lexical, branche terminale d’évaluation) en décrivant la fin de trajectoire sur le runtime local Hugo. Elle distingue explicitement :

- le **cœur de convergence** (ce qui doit être atteint pour considérer Hugo local “aligné 2.0” sur son noyau) ;
- la **couronne optionnelle** (lots utiles mais non bloquants pour ce noyau).

### 5. Résumé des domaines couverts

Le plan de convergence s’appuie désormais explicitement sur les domaines et écarts suivants :

- Noyau apprenant : 10_runtime_p0_progression_uistate, 20_memoire_gouvernee, 31_front_apprenant_postures_et_bascule, 70_evaluation_traces_preuves.  
- Rôles & sécurité : 90_confidentialite_partage_multitenant_roles, 100_exports_preuves_qualiopi_lite, 110_interfaces_formateur_tuteur.  
- Encadrants & orchestrateurs : 40_base_connaissances_formateur, 50_orchestrateur_formateur, 60_orchestrateur_tuteur.  
- Couronne : 30_referentiel_documentaire_RAG, 80_observabilite_qualite_conversationnelle, 120_intercalaires_v1.  

Les fichiers `ecarts — *.md` correspondants restent la référence pour la lecture détaillée des écarts par domaine. Le présent plan ne duplique pas leur contenu, il fixe l’ordre et le périmètre des lots.

### 6. Cœur de convergence – lots 1 à 7

Le cœur de convergence local correspond à l’alignement des domaines 10/20/31/70/90/100/110/40/50/60 sur un runtime unique, testé et documenté.

Il se décline en trois vagues :

- **Vague 1 (déjà cadrée)**  
  1. Mémoire intra-conversation (domaine 20) : contrat `sessionmemory`, endpoints, tests.  
  2. CTA synthèse / évaluation (10/70) : contrat UIState minimal pour `ctaevaluation` et `ctasynthesis`, endpoints, tests backend/front.  
  3. RAG lexical & contexte (30) : rôle de renfort situé, pas de “moteur de cours”.  
  4. Branche terminale d’évaluation utilisable (70) : trace minimale, validation humaine, pas de certification autonome.

- **Vague 2 (déjà engagée)**  
  5. Profils d’affichage & états produit apprenant (10/31/110) : `conversation_mode`, `learner_display_profile`, 3 grammaires apprenant consommées côté front.  
  6. Confidentialité & exports minimaux (90/100) : pack oracles D2‑M07, taxonomie exports D2‑M11, scoping tenant sur bundles et ExportRun. **→ cluster dev vague 2 encadrants (local) : guards trainer, EXIF Evidence, alignement exports front/back — voir `cluster_dev_encadrants_exports_vague2_resultats.md`.**  
  7. Mapping EvaluationTrace (70/100/110) : D2‑M05 livré documentairement — `mapping_EvaluationTrace_runtime_local.md`.

- **Vague 3 (encadrants & décisions structurantes)**  
  8. Parcours encadrants B1 / C1 / D1 (40/50/60/110) : timeline tuteur, base formateur, orchestrateurs — objets réels, workflows bout-en-bout encore partiels. **→ surfaces prod minimales tuteur/formateur livrées localement ; orchestrateurs complets et C1/D1 restent ouverts.**  
  9. Décisions structurantes transverses : flag v17 (D2‑M10), frontières ORGADMIN / superadmin (D2‑M12), checklist parcours tuteur B1 (D2‑M09), tableau posture × RAG × CTA (D2‑M02).  
  10. **Fin de fil & observabilité base (70/80/100)** : pivot `evaluation_trace_pivot_v1`, signaux observabilité admin, squelettes D9bis — **→ livré local** — voir `cluster_dev_fin_de_fil_qualite_observabilite_vague3_resultats.md`.  
  11. **D9bis backend & observabilité avancée v1 (80/100)** : modèles analytics LLM dérivés, export SUPERADMIN, conversation-summary — **→ livré local** — voir `cluster_dev_d9bis_observabilite_vague4_resultats.md`.  
  12. **Audit convergence vague 5** : E2E API multi-rôles, oracle Encoors minimal, photo convergence — **→ livré** — voir `cluster_retex_convergence_vagues1a4_v5.md`.  
  13. **Cluster 8 OPS** : smoke UI Playwright multi-rôles, oracle Encoors authentifié (script), audit RLS Postgres minimal — **→ livré local** — voir `cluster_ops_smoke_ui_encoors_rls_resultats.md`, `cluster_retex_ops_cluster8.md`.  
  14. **Cluster 9 consolidation** : contrats minimaux mémoire intra-conv, évaluation/traces/exports, confidentialité/observabilité — **→ livré documentaire** — voir `cluster9_convergence_memoire_eval_confidentialite_resultats.md`.  
  15. **Cluster 10 clôture runtime/OPS** : exécution C9-OPS (RLS rôle app, smoke memory-summary, oracle Encoors script), livrables C9-DOC, ADR C9-CODE — **→ livré** — voir `cluster10_cloture_vague_runtime_ops_resultats.md`.
  16. **Cluster 11 verrouillage runtime vs Encoors** : photo local vs distant (20/70/80/90/100), oracle étendu (M1/O1/EVAL1/OBS), template RLS prod — **→ livré local ; Encoors auth A_VÉRIFIER** — voir `cluster11_verrouillage_runtime_vs_encoors_resultats.md`.
  17. **Cluster 12 UX apprenant & postures** : plan sélecteur G2-02, 3 profils UX, CTA×posture×RAG, Playwright B1 — **→ plan livré ; implémentation P0 ouverte** — voir `cluster12_ux_apprenant_postures_plan_resultats.md`.
  18. **Cluster 13 RAG & référentiel documentaire** : doctrine lexical, décision pgvector OFF Couronne, hiérarchie contexte v1, écarts 30 consolidés — **→ livré DOC ; CODE P0 aucun** — voir `cluster13_rag_referentiel_documentaire_plan_resultats.md`.
  19. **Cluster 14 interfaces encadrants & observabilité produit** : inventaire surfaces 110, COORDO héritage tuteur, taxonomie E1–E6 ↔ UI, dashboards Couronne — **→ plan livré DOC ; CODE P0 aucun** — voir `cluster14_interfaces_encadrants_observabilite_plan_resultats.md`.

### 7. Couronne optionnelle (post-cœur)

Lots utiles mais **non bloquants** pour considérer le noyau local aligné 2.0 :

- **D9bis** — export analytique LLM (`ConversationTurnLLMAnalysis` / `ConversationLLMAnalysis`) — domaines 80/100 — D2‑M06 ; **backend partiel livré local (SUPERADMIN, hors produit)** ; exposition produit et dashboards restent **Couronne**.  
- **Intercalaires v1** — domaine 120 — contrat cible additive ; aucune preuve runtime locale à ce stade.  
- **RAG vectoriel & dashboards observabilité produit** — domaines 30/80 — catalogues signaux front, sophistication au-delà du canal technique.  
- **Sélecteur posture interactif** (G2‑02) — domaine 31 — après stabilisation encadrants si priorisé.

### 8. Renvois documentaires

- Synthèse globale des écarts (13 domaines) : `docs-workspace/synthese_globale_ecarts_par_domaine.md`  
- Matrice runtime ↔ cible : `docs-workspace/cluster2_matrice_runtime_vs_cible.md` (V3, 13 domaines)  
- Écarts détaillés : fichiers `ecarts — *.md` (un par domaine)  
- Designs lots : `design_D2-M06_D2-M11_exports_analytics.md`, `design_D2-M07_D2-M08_profils_grammaires_matrice_roles.md`  
- Retex : `Retex_cluster_1-4.md`, `Retex_clusters_5-7_profils_roles_exports.md`