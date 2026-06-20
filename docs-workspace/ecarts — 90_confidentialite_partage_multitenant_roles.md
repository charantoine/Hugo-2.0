# 00_rapport_ecarts — 90_confidentialite_partage_multitenant_roles

> **Mise à jour post-cluster 16 — 2026-06-18** · **Cluster 16 :** pas d'impact direct ; oracle U16-S3 vérifie absence P0 dans panneau mémoire. **A_VÉRIFIER :** RLS prod.
>
> **Mise à jour post-campagne multi-tenant — 2026-06-20** · Isolation tenant backend **validée localement** (90/90 smoke relaxed, 0 fuite inter-org). Front multi-org SUPERADMIN + e2e **11/11 PASS**. Tutor-links création = **SUPERADMIN only** (transitoire). RLS : gate strict actif mais connexion locale/CI encore en superuser `postgres` — vert strict prod-like **en attente** rôle `hugo_app`. Synthèse : [`tests/archives/tests_hugo_2_0_2026-06-18_20.md`](tests/archives/tests_hugo_2_0_2026-06-18_20.md) · ops : [`hugo_back/docs/MULTITENANT_SMOKE.md`](../hugo_back/docs/MULTITENANT_SMOKE.md).

## Domaine

- `DOMAINE_CODE = 90_confidentialite_partage_multitenant_roles`
- `DOMAINE_LABEL = confidentialité, partage, multi-tenant et rôles`

---

## 1. Objet du rapport

Ce rapport qualifie, pour le seul domaine **confidentialité / partage / multi-tenant / rôles** de Hugo cœur, l’écart entre :
- la **cible 2.0** décrite par la spec canonique, son complément et les specs de domaine ;
- le **réel observable** décrit par les audits du workspace Hugo réel ;
- le **pont de vocabulaire** fourni par le glossaire d’alignement.

Ce document ne traite ni Hugo & Cie, ni une doctrine générique de sécurité logicielle hors Hugo, ni un audit infra complet de production. Il vise à établir une lecture propre de ce qui est déjà fixé doctrinalement, de ce qui est réellement observable dans Hugo cœur, de ce qui reste partiellement ouvert, et de ce qui doit explicitement rester `A_VERIFIER`.

---

## 2. Règles de lecture et de vérité appliquées sur ce domaine

### 2.1 Réel, cible, glossaire

Pour parler du **réel**, ce rapport s’appuie d’abord sur les audits du corpus Hugo réel :
- `02_ETAT_MOTEUR_REEL.md` pour les garde-fous backend, la gestion des accès, les endpoints, les modèles et le runtime local observé ;
- `03_ETAT_PRODUIT_REEL.md` pour les surfaces visibles par rôle, les limites du front montrable et la nature effective des parcours ;
- `07_RUNTIME_DEMO_REFERENCE.md` et `09_PARCOURS_DEMO_ET_SCENARIOS.md` pour ce qui est réellement démontrable sans sur-vendre ;
- `05_ECARTS_DOC_CODE_PRODUIT.md` pour les contradictions confirmées entre documentation, code local, front 1.8 et variante distante ;
- `10_FICHE_RUNTIME_PROD_ENCOORS.md` uniquement quand une mention concerne la variante distante, qui doit rester prudente.

Pour parler de la **cible**, on s’appuie sur :
- `spec_canonique_hugo_2_0.md` ;
- `complement_unique_specs_2_0` ;
- les specs 2.0 pertinentes côté interface et formateur/tuteur quand elles précisent les rôles et les garde-fous de visibilité.

Le **glossaire d’alignement** n’est utilisé que comme **pont de vocabulaire**. Il aide à raccorder noms doctrinaux et noms réels observés, mais ne constitue jamais une preuve suffisante d’implémentation ou de conformité effective.

### 2.2 Garde-fous de lecture

- La cible 2.0 décrit un **cadre de référence** ; elle ne prouve jamais qu’un dispositif complet de confidentialité, de partage ou de multi-tenant strict est déjà démontré bout en bout.
- La présence d’un middleware, d’un test local, d’un rôle d’interface ou d’un endpoint ne suffit pas, à elle seule, à prouver la robustesse complète du contrôle d’accès ou de l’isolation inter-tenant.
- Toute affirmation dépendant de la variante distante, des flags runtime, de la configuration Postgres réelle, de la RLS active en production ou d’un parcours non audité reste marquée `A_VERIFIER`.
- Le domaine doit être lu dans la doctrine Hugo 2.0 : confidentialité-first, partage explicite, front non pilote, verbatim non librement exposable, séparation stricte des rôles et multi-tenant fort.

---

## 3. Périmètre cible 2.0 du domaine

Dans la cible Hugo 2.0, le domaine **confidentialité / partage / multi-tenant / rôles** n’est pas un module latéral. Il fait partie des invariants de l’architecture produit et des règles de vérité du système.

### 3.1 Ce que la cible 2.0 fixe déjà fermement

La cible 2.0 fixe explicitement les points suivants :

- Le système est **confidentialité-first** : le contenu apprenant n’est pas librement accessible aux autres rôles.
- Le **verbatim est privé par défaut** ; il ne doit jamais devenir une surface librement lisible hors partage explicite.
- Toute visibilité pour des rôles non apprenant doit passer par un **partage explicite distinct**, selon le type d’objet concerné : synthèse, preuves, verbatim, traces, objets gouvernés.
- Le **multi-tenant strict** implique une isolation complète par organisation, avec RLS active comme contrainte de produit et non simple détail d’infrastructure.
- Les rôles non apprenant, y compris tuteur, formateur, coordinateur, administrateur d’organisation et superadministration technique, ne doivent pas disposer d’un accès libre au contenu apprenant non partagé.
- Les capacités par rôle doivent être distinguées, même si toutes les surfaces UI détaillées ne sont pas encore entièrement spécifiées.

### 3.2 Ce que la cible 2.0 laisse encore partiellement ouvert

La cible 2.0 est forte sur les principes, mais laisse encore plusieurs points à préciser plus finement :
- la granularité complète des autorisations par rôle sur chaque type d’objet ;
- le détail produit exact des workflows de partage ;
- la modélisation opérationnelle de certains rôles métier, notamment coordinateur ;
- la preuve technique complète d’une RLS effective sur la variante de production réelle ;
- la description exacte des écrans d’administration finaux.

Autrement dit, la doctrine de sécurité et de partage est **fortement verrouillée**, mais toutes les projections produit et toutes les preuves d’exécution ne sont pas encore exhaustivement stabilisées.

---

## 4. Photo du réel observé

### 4.1 Le réel confirme une orientation générale cohérente avec la doctrine

Le réel audité montre que Hugo cœur n’est pas documenté comme un système à accès libre aux contenus sensibles. Les audits et le produit montrable convergent plutôt vers une logique où :
- le backend reste source de vérité ;
- le front consomme des états dérivés ;
- les surfaces visibles ne sont pas structurées autour d’un accès brut aux données internes ;
- certaines vues sont déjà séparées selon les rôles ou les modes d’usage.

Le glossaire renforce cette lecture en montrant un alignement fort autour de `UIState`, de la mémoire gouvernée résumée, des traces, des objets de connaissance gouvernée et des services backend dérivés, plutôt qu’autour d’une exposition directe du verbatim ou des états bruts.

### 4.2 Verbatim, mémoire et objets visibles dans le réel

Le réel local audité montre plusieurs éléments cohérents avec la doctrine 2.0 :
- le front produit ne consomme pas les champs P0 bruts ;
- la mémoire affichable passe par un endpoint de **résumé gouverné** (`memory-summary`) ;
- les objets visibles ou partageables sont des projections produit et non des dumps techniques du moteur ;
- les traces, synthèses et évaluations passent par des workflows dédiés plutôt que par une lecture brute de tout l’historique.

Cette base est importante : elle montre que la doctrine 2.0 n’invente pas ex nihilo une séparation entre données internes et surfaces visibles. Une part de cette séparation existe déjà dans le réel.

### 4.3 Rôles et surfaces observables dans le réel

Le réel montre également une différenciation de surfaces selon les usages :
- un parcours apprenant ;
- des surfaces testeur / back-office ;
- des vues ou actions liées au trainer ;
- un espace d’administration incomplet mais distinct ;
- des parcours tutoraux ou analytiques partiels selon les composants disponibles.

Cependant, les audits montrent aussi que la **couverture produit des rôles** reste partielle :
- certaines UI existent en mode testeur mais pas en prod montrable ;
- certains parcours admin sont incomplets ;
- le rôle coordinateur reste peu stabilisé comme surface observable ;
- les droits fins ne sont pas tous démontrés exhaustivement par des parcours bout en bout.

Le réel permet donc de parler d’une **séparation présente mais encore inégalement outillée** selon les rôles.

### 4.4 Multi-tenant et RLS dans le réel audité

C’est ici que le domaine devient plus sensible.

Le réel audité mentionne un middleware et des tests liés au cross-tenant. Cela constitue un signal positif : le sujet multi-tenant n’est pas absent de l’architecture réelle. En revanche, l’audit croisé documente explicitement que la preuve complète d’une **RLS Postgres effective en production réelle** n’est pas établie à partir du corpus local utilisé :
- les tests observés reposent sur SQLite ;
- la preuve sur Postgres réel n’est pas acquise dans ce corpus ;
- la variante distante n’est pas auditée de manière suffisante pour conclure.

Le bon niveau de vérité, sur ce point, est donc : **intention réelle présente, outillage local partiel, preuve infra prod complète non démontrée ici**.

### 4.5 Partage explicite dans le réel produit

Le réel produit montre une logique de circulation d’objets structurés — synthèses, traces, évaluations, mémoire résumée — plus qu’une logique d’ouverture libre de toutes les données. Cela va dans le sens de la doctrine de **partage explicite**.

En revanche, le corpus ici mobilisé ne permet pas encore d’établir complètement :
- la cartographie exhaustive des objets partageables ;
- les transitions exactes entre privé, partagé, confirmable, validé, exportable ;
- les droits fins selon tous les rôles ;
- l’équivalence de comportement entre local audité et runtime distant.

Le réel donne donc une base crédible de partage gouverné, mais pas encore un contrat documentaire complètement stabilisé.

### 4.7 UIState surface — cluster 4 (conversation_mode, learner_display_profile)

**Réel confirmé (local) :** `GET /hugo/sessions/{id}/ui-state/` expose désormais :
- `conversation_mode` : objet dérivé de la posture (`code`, `label`, `can_switch`, `switch_warning`) — sans P0 ;
- `learner_display_profile` : enum `youth` | `adult` | `professional` (défaut `professional`), distinct de `gamification_profile`.

**Preuve :** `test_cluster4_surface_contracts.py` (9 tests verts).

**Invariants confidentialité :** aucun verbatim, P0 ni donnée inter-tenant ajoutée ; champs purement dérivés / paramétriques. Aligné CONF-03, CONF-04.

**CIBLE restante :** persistance du profil d’affichage par org/groupe ; choix par rôles non-apprenant (DSP-05/06) — non livré.

### 4.6 Cas de référence B1-01 — timeline tuteur (cluster 3 court, local)

**Oracle :** B1-01 — pas de verbatim privé pour le rôle **TUTOR** sur `GET /dashboard/groups/{group_id}/learners/{learner_id}/timeline/`.

**Réel confirmé (local, post-patch 2026-06-16) :**
- si `share_verbatim=false` : `messages[]` vide **et** `first_learner_message` vide (chaîne `""`) — plus d’extrait du premier message apprenant ;
- si `share_verbatim=true` : messages et aperçu du premier message apprenant restent disponibles comme avant ;
- les messages apprenant exposés sous partage portent un résumé **`pilotage`** (dérivé produit-safe), pas les champs P0 bruts (`turn_state`, `conversation_decision` complets) ni les prompts.

**Preuve automatisée :** `hugo_back/apps/hugo/tests/test_cluster3_oracles.py::test_b1_01_timeline_hides_messages_when_share_verbatim_false` (vert en local).

**Niveau de vérité :** **IMPLÉMENTÉ / observable localement** pour ce garde-fou timeline ; prod Encoors et RLS Postgres restent **A_VERIFIER**.

---

## 5. Analyse narrative des écarts

### 5.1 Zone de fort alignement doctrinal

Le domaine est l’un de ceux où l’**alignement doctrinal** est le plus net.

La cible 2.0 affirme clairement :
- confidentialité-first ;
- verbatim privé par défaut ;
- partage explicite ;
- interdiction d’un accès libre pour les rôles non apprenant ;
- multi-tenant strict ;
- séparation des rôles.

Le réel observé ne contredit pas cette orientation générale. Au contraire, plusieurs éléments visibles vont dans le même sens :
- usage d’états dérivés et d’objets gouvernés ;
- front non nourri par les états bruts ;
- mémoire résumée plutôt qu’historique brut ;
- séparation de surfaces selon les usages ;
- présence d’un outillage multi-tenant au moins partiel.

Sur le plan des principes et de l’architecture de lecture, l’alignement est donc bon.

### 5.2 Écart majeur : niveau de preuve technique inférieur au niveau doctrinal

L’écart principal n’est pas une contradiction frontale entre cible et réel. C’est un **écart de niveau de preuve**.

La cible 2.0 fixe un multi-tenant strict avec RLS active et absence de lecture/écriture inter-tenant. Le réel local audité montre des indices sérieux de prise en compte du sujet, mais il ne fournit pas, dans le corpus mobilisé ici, une démonstration complète de conformité sur l’infra de production réelle :
- tests observés sur SQLite ;
- runtime distant non entièrement inspecté ;
- RLS Postgres prod non prouvée dans ce périmètre ;
- certains comportements dépendants des variantes restent ouverts.

L’écart n’appelle pas à réécrire la doctrine. Il impose surtout de **documenter honnêtement ce qui est prouvé, ce qui est seulement préparé, et ce qui reste à vérifier**.

### 5.3 Écart important : rôles doctrinaux mieux définis que surfaces réellement stabilisées

La doctrine 2.0 énonce clairement les rôles minimaux :
- apprenant ;
- tuteur ;
- formateur ;
- coordinateur ;
- administrateur d’organisation ;
- superadministration technique.

Le réel, lui, montre surtout :
- des parcours apprenant ;
- des surfaces trainer / testeur ;
- un admin partiel ;
- des parcours de démonstration non équivalents à une couverture produit complète.

Il existe donc un écart entre :
- **la clarté doctrinale des rôles** ;
- et **la stabilisation observable des surfaces et permissions concrètes**.

Cela ne signifie pas que la doctrine est trop ambitieuse ou que le réel est faux. Cela signifie que la documentation doit mieux distinguer :
- rôle doctrinal ;
- rôle observable dans le produit local ;
- rôle réellement démontré bout en bout ;
- rôle encore partiellement ouvert.

### 5.4 Écart de formalisation sur le partage explicite

La doctrine 2.0 dit juste sur le fond : le partage est explicite, gouverné et distinct selon les objets. Le réel montre des objets structurés et des workflows spécifiques. Mais la documentation n’est pas encore entièrement homogène sur :
- les objets partageables exacts ;
- les états de partage ;
- la différence entre visible, partageable, confirmable, exportable, validé humainement ;
- les droits précis par rôle sur ces transitions.

Cet écart est principalement un **écart de formalisation documentaire**. La responsabilité métier semble déjà largement présente, mais elle doit être mieux contractée.

### 5.5 Écart de prudence nécessaire entre local audité et variante distante

Le document d’écarts doc/code/produit insiste sur un point transversal critique : la démo courante pointe vers `hugoback.encoors.com`, et le comportement de cette API distante ne prouve pas automatiquement celui du backend local, ni l’inverse.

Pour le domaine confidentialité / partage / multi-tenant, cette prudence est encore plus importante :
- il est risqué de supposer une équivalence des droits réels entre local et distant ;
- les flags, la config CORS, la base réelle, la RLS et certains contrats peuvent diverger ;
- une inspection HTTP partielle ne suffit pas à conclure sur toute la politique de sécurité ou d’isolation.

Le domaine doit donc porter plus explicitement que d’autres la mention `A_VERIFIER` dès qu’on parle de prod distante ou de garanties infra effectives.

### 5.6 Écart secondaire : administration et rôles métier encore partiellement outillés

Les audits montrent aussi que certains parcours d’administration sont incomplets, notamment sur la gestion des utilisateurs. Cela ne contredit pas la doctrine de séparation des rôles, mais cela signale que :
- la couche admin observable n’est pas encore à la hauteur d’une modélisation produit totalement stabilisée ;
- certains rôles peuvent exister doctrinalement sans parcours outillé complet ;
- la documentation doit éviter de sur-vendre un modèle de gouvernance UI pleinement livré.

Là encore, l’écart est moins un écart de doctrine qu’un **écart de maturité produit et de preuve d’outillage**.

---

## 6. Lecture de synthèse par niveau de vérité

### 6.1 Implémenté / observable

Sur ce domaine, le réel audité permet d’affirmer comme **implémenté ou observable** :
- une logique générale backend-first cohérente avec la confidentialité-first ;
- l’absence d’exposition frontale des champs P0 bruts ;
- l’existence d’objets et vues gouvernés plutôt que d’une exposition brute du moteur ;
- un endpoint de mémoire résumée gouvernée ;
- des surfaces différenciées selon certains usages et rôles ;
- des éléments de prise en compte du multi-tenant et du cross-tenant dans le code local ;
- des workflows structurés pour synthèse, évaluation, traces et objets partageables.

### 6.2 Cible 2.0

Relèvent clairement de la **cible 2.0** :
- la formalisation complète du partage explicite par type d’objet ;
- une séparation stabilisée et exhaustive des permissions par rôle ;
- la preuve robuste d’un multi-tenant strict avec RLS active dans toutes les variantes visées ;
- une cartographie UI complète des surfaces par rôle ;
- une doctrine documentaire parfaitement homogène sur visible / partageable / validable / exportable.

### 6.3 Écarts confirmés

À ce stade, les **écarts confirmés** du domaine sont surtout :
- un niveau de preuve infra et runtime inférieur à la force du contrat doctrinal sur le multi-tenant strict ;
- une modélisation des rôles plus claire dans la cible que dans les surfaces réellement stabilisées ;
- une formalisation encore incomplète des workflows de partage explicite ;
- une administration observable partielle sur certains parcours.

### 6.4 À vérifier

Restent explicitement `A_VERIFIER` :
- l’activation et l’effectivité complètes de la RLS Postgres dans la variante de production réelle ;
- l’équivalence locale / distante sur les politiques d’accès et de partage ;
- le détail effectif des droits par rôle sur tous les objets produit ;
- les effets de certains flags ou variantes runtime sur les surfaces visibles et les garde-fous ;
- toute affirmation forte sur un dispositif de gouvernance complet en prod distante.

---

## 7. Garde-fous pour la suite documentaire et technique

### 7.1 Ce qu’il ne faut pas faire

Pour ce domaine, il faut éviter six dérives :
1. prendre la spec 2.0 comme preuve que la RLS prod est déjà démontrée ;
2. prendre un test local, un middleware ou un rôle affiché comme preuve d’une séparation complète des droits ;
3. confondre surface testeur, surface admin partielle et modèle produit final de gouvernance ;
4. supposer que `hugoback.encoors.com` réplique exactement l’état du backend local audité ;
5. relire la confidentialité-first comme une simple recommandation UX au lieu d’un invariant d’architecture ;
6. rebasculer vers une logique où le verbatim non partagé deviendrait librement consultable.

### 7.2 Ce qu’il faut privilégier

La bonne trajectoire pour ce domaine est plutôt :
- clarifier les **contrats** de visibilité, partage et validation ;
- distinguer précisément **rôles doctrinaux**, **rôles observables**, et **rôles effectivement démontrés** ;
- documenter explicitement ce qui est **local audité** et ce qui reste **A_VERIFIER** en distant ;
- consolider le raccord entre doctrine 2.0 et noms réels des surfaces, endpoints et garde-fous ;
- privilégier des compléments backend et documentaires additifs plutôt qu’une réécriture théorique du système.
### 7.3 Règles transverses pour les protocoles de test (domaine 90)

Les protocoles de test qui touchent au domaine
« confidentialité, partage, multi-tenant et rôles » doivent appliquer
des règles communes, pour éviter de reconstruire implicitement une
doctrine parallèle dans la bibliothèque de tests.

1. En-tête « Niveau de preuve ciblé »

Tout protocole de test commence par une section « Niveau de preuve ciblé »
conforme au gabarit décrit dans `plan_documentation_cto_convergence_hugo.md`.
Cette section distingue explicitement :

- ce qui relève de la cible 2.0 ;
- ce qui est effectivement observable dans le runtime local audité ;
- ce qui dépend du runtime distant, de la production ou de flags non audités
  et doit être marqué AVERIFIER.

2. Référence obligatoire à la spec canonique des rôles

La section « Rôle testé » de chaque protocole doit :

- nommer le rôle (Apprenant, Tuteur, Formateur, Coordinateur,
  Administrateur d’organisation, Superadministration technique) ;
- se référer à la description de ce rôle dans `spec_canonique_hugo_2_0.md` ;
- considérer comme échec de test tout comportement qui contredit les
  garde-fous suivants déjà fixés dans la spec 2.0 :
  - verbatim non partagé privé par défaut ;
  - aucun accès front aux champs P0 ou TurnState bruts ;
  - multi-tenant strict, sans lecture/écriture inter-tenant ;
  - absence d’accès libre au contenu apprenant non partagé pour les
    rôles non-apprenants.

3. Garde-fous de confidentialité / multi-tenant dans les scénarios

Pour tout protocole impliquant un rôle non-apprenant (Tuteur, Formateur,
Coordinateur, Administrateur d’organisation, Superadministration technique),
le protocole doit inclure un bloc de tests explicites vérifiant au minimum :

- que le rôle testé ne voit pas le verbatim non partagé de l’apprenant ;
- qu’il ne voit pas les champs P0 ou TurnState bruts ;
- qu’il ne peut pas accéder à des données d’une autre organisation ;
- qu’il ne peut pas lire un export ou un bundle contenant du contenu
  apprenant non partagé.

L’absence de ce bloc dans un nouveau protocole de test couvrant le
domaine 90 doit être considérée comme un défaut de couverture de ce domaine.

4. Marquage systématique AVERIFIER sur le runtime distant

Tout scénario ou oracle qui se prononce sur :

- l’activation et l’effectivité de la RLS Postgres en production réelle ;
- l’absence de lecture/écriture inter-tenant en prod ;
- le comportement exact d’un runtime distant ou d’une variante Encoors ;

doit être marqué AVERIFIER, tant qu’un audit spécifique de ces points
n’a pas été mené sur l’environnement visé. Les protocoles de test ne
doivent pas réinterpréter la spec 2.0 comme preuve que ces garanties
sont déjà livrées.
---

## 8. Conclusion opérationnelle du domaine

Le domaine `90_confidentialite_partage_multitenant_roles` est l’un des domaines les plus structurants de Hugo cœur, et aussi l’un de ceux où la doctrine 2.0 est la plus ferme.

Le réel audité montre une base déjà cohérente avec cette doctrine :
- backend-first ;
- états dérivés ;
- pas d’exposition brute des champs moteur ;
- mémoire gouvernée résumée ;
- séparation partielle des surfaces ;
- prise en compte réelle du multi-tenant et du cross-tenant.

L’écart principal n’est donc pas un défaut massif d’orientation, mais un **écart de preuve, de formalisation et de couverture observable** :
- la doctrine des rôles et du partage est plus nette que les surfaces livrées ;
- la preuve complète du multi-tenant strict en production réelle n’est pas établie dans ce corpus ;
- les workflows précis de partage et les permissions détaillées restent à mieux contractualiser.

Ce domaine doit donc être lu comme :
- **doctrinalement très stabilisé** ;
- **réellement partiellement aligné** ;
- **encore incomplet dans sa démonstration de bout en bout** ;
- avec un besoin prioritaire de clarification documentaire, de bornage des niveaux de preuve et de marquage explicite des zones `A_VERIFIER`.


# 01_matrice_ecarts — 90_confidentialite_partage_multitenant_roles

## Domaine

- `DOMAINE_CODE = 90_confidentialite_partage_multitenant_roles`
- `DOMAINE_LABEL = confidentialité, partage, multi-tenant et rôles`

---

## 1. Règle de lecture

Cette matrice croise, pour le seul domaine **confidentialité / partage / multi-tenant / rôles** :
- la **cible 2.0** telle qu’elle est formulée dans `spec_canonique_hugo_2_0.md` ;
- le **réel observable** tel qu’il ressort des audits Hugo réel ;
- le **glossaire d’alignement** comme pont de vocabulaire, sans lui donner valeur de preuve autonome.

### Statuts utilisés

- `ALIGNE` : la responsabilité cible est clairement couverte dans le réel observé.
- `ALIGNE_DOC_PARTIEL` : le fond est bien aligné, mais la documentation doit mieux expliciter le raccord cible / réel.
- `RENOMMER_DANS_DOC` : le réel emploie un nom concret utile à faire apparaître dans la documentation 2.0.
- `AMBIGU` : le raccord conceptuel existe, mais le mapping reste trop flou ou insuffisamment stabilisé.
- `A_VERIFIER` : le corpus utilisé ici ne permet pas d’établir la preuve de manière suffisamment robuste.
- `ABSENT / NOUVEAU_CONTRAT` : la cible fixe une responsabilité qui n’est pas encore démontrée comme contractualisée ou outillée proprement dans le réel.

### Garde-fous

- La cible 2.0 reste une **cible**, pas une preuve de livraison.
- Les audits 00–10 restent la base pour parler du **réel**.
- Le glossaire sert de **raccord de vocabulaire**, pas de preuve fonctionnelle.
- Toute mention dépendant du runtime distant, de la RLS Postgres réelle ou de variantes non auditées reste marquée `A_VERIFIER`.

---

## 2. Matrice d’écarts

| ID | Responsabilité cible 2.0 | Formulation cible | Réel observable mobilisé | Nom réel / point d’ancrage observé | Statut | Lecture d’écart | Action documentaire attendue |
|---|---|---|---|---|---|---|---|
| CONF-01 | Confidentialité-first | La confidentialité-first est un invariant transversal de Hugo cœur. | Les audits produit et moteur convergent vers un backend source de vérité, des états dérivés côté front et l’absence d’exposition frontale des états moteur bruts. | `UIState`, front drivé par états serveur, pas d’exposition brute P0 | ALIGNE | Le principe général est cohérent entre cible et réel. | Conserver la formulation canonique et citer plus explicitement les ancrages réels côté UIState / projections produit. |
| CONF-02 | Verbatim privé par défaut | Le verbatim non partagé ne doit pas être librement visible par les rôles non apprenant. | La cible est très explicite ; le réel observable montre surtout des projections gouvernées et un résumé mémoire plutôt qu’une lecture libre de l’historique brut. | `memory-summary`, objets dérivés, verbatim non frontal | ALIGNE_DOC_PARTIEL | Le sens global est bon, mais la preuve exhaustive par rôle n’est pas entièrement formalisée dans la doc du réel. | Renforcer la doc de domaine avec un paragraphe explicite “verbatim privé par défaut” relié aux surfaces réellement observées. |
| CONF-03 | Interdiction d’exposer les champs P0 au front | Le front ne doit pas consommer TurnState ou les champs P0 bruts. | Le glossaire et la spec convergent ; le document d’écarts confirme que le front prod ne recalcule pas les signaux P0 et n’expose pas TurnState en parcours prod. | `UIState`, absence de `turnstate` dans `ProdLearnerWorkspace`, fallback debug hors parcours prod | ALIGNE | Très bon alignement entre doctrine et réel. | Garder tel quel et rappeler le cas particulier du mode testeur / debug pour éviter toute ambiguïté. |
| CONF-04 | UIState comme surface montrable filtrée | Les surfaces visibles doivent passer par UIState et des objets traduits côté backend. | Le glossaire montre un alignement fort sur `UIState`, `builduistate`, endpoint `ui-state`. | `builduistate`, `uistatebuilder.py`, `GET /hugo/sessions/{id}/ui-state` | ALIGNE | Zone de très bon raccord doctrine / réel. | Ajouter systématiquement le nom réel observé dans les annexes techniques. |
| CONF-05 | Mémoire gouvernée résumée | La mémoire visible ne doit pas être un historique brut mais une projection gouvernée. | La spec et le glossaire convergent sur une mémoire gouvernée résumée ; le réel expose un endpoint `memory-summary`. | `GET /hugo/sessions/{id}/memory-summary` | ALIGNE | Très bon point d’ancrage pour le domaine confidentialité / partage. | Garder le nom doctrinal et citer l’endpoint réel comme projection produit actuelle. |
| CONF-06 | Partage explicite distinct selon type d’objet | La visibilité des objets doit passer par des mécanismes de partage explicite distincts. | La cible est ferme sur le principe ; le réel montre des workflows structurés pour synthèse, trace, évaluation, mémoire résumée, mais la cartographie complète des états de partage n’est pas encore documentée proprement. | synthèse, traces, évaluations, mémoire résumée | ALIGNE_DOC_PARTIEL | Le principe est crédible dans le réel, mais le contrat documentaire reste incomplet. | Formaliser une table des objets partageables et des niveaux de visibilité par rôle. |
| CONF-07 | Tuteur sans accès libre au non-partagé | Le tuteur lit progression, blocages, traces partagées, sans accès libre au verbatim non partagé ni contrôle direct du moteur. | Timeline dashboard : `messages[]` et `first_learner_message` vides si `share_verbatim=false` ; résumé `pilotage` sans P0 brut si partage actif. Preuve pytest cluster 3. | `DashboardTimelineView`, `test_cluster3_oracles.py::test_b1_01_*`, oracle B1-01 | ALIGNE | Garde-fou verbatim tuteur corrigé et testé en local ; matrice fine D2-M07 encore à compléter. | Citer B1-01 comme cas de référence dans la matrice rôle × données ; conserver A_VERIFIER prod. |
| CONF-08 | Formateur sans accès libre au contenu apprenant non partagé | Le formateur manipule des connaissances métier gouvernées, pas le contenu apprenant non partagé en libre accès. | La cible l’énonce ; le réel montre des objets `TrainerKnowledgeItem` et des surfaces trainer, sans preuve d’un libre accès au non-partagé apprenant. | `TrainerKnowledgeItem`, vues trainer | ALIGNE_DOC_PARTIEL | Bonne cohérence de fond, mais les règles de visibilité précises restent à mieux documenter. | Ajouter une distinction explicite entre surfaces trainer métier et données apprenant non partagées. |
| CONF-09 | Org admin sans lecture libre du contenu apprenant | L’admin d’organisation ne doit pas accéder librement au contenu apprenant non partagé. | La cible est explicite ; le réel montre un admin partiel et ne démontre pas de lecture libre du non-partagé, mais la matrice des permissions admin n’est pas stabilisée. | `UsersView`, admin partiel | AMBIGU | Absence de contradiction forte, mais preuve insuffisante et outillage incomplet. | Produire une matrice documentaire des permissions admin minimales et des interdits explicites. |
| CONF-10 | Superadministration technique sous contraintes | La superadministration technique ne vaut pas droit applicatif libre au contenu apprenant. | La cible le fixe ; le corpus de réel mobilisé ici ne documente pas suffisamment une superadmin produit opérationnelle ni ses garde-fous effectifs. | rôle conceptuel de superadmin technique | A_VERIFIER | La doctrine est claire, mais la preuve runtime / produit est insuffisante dans ce corpus. | Marquer explicitement ce rôle comme cible fortement cadrée mais peu démontrée dans le réel observable. |
| CONF-11 | Multi-tenant strict | Le produit doit garantir une isolation stricte par organisation. | Le document d’écarts confirme la présence d’un middleware et de tests cross-tenant, mais précise que la preuve complète en Postgres réel n’est pas établie depuis ce corpus. | middleware cross-tenant, `testcrosstenant.py` | ALIGNE_DOC_PARTIEL | Intention et début de couverture réels, mais preuve infra incomplète. | Documenter distinctement “prise en compte réelle” et “preuve complète d’isolation prod non démontrée ici”. |
| CONF-12 | RLS active comme contrainte produit | La RLS active fait partie de la cible produit, pas d’un simple détail d’infrastructure. | Le document d’écarts souligne explicitement que la preuve d’une RLS Postgres réelle reste ouverte et que les tests visibles sont sur SQLite. | RLS mentionnée, tests SQLite, prod Postgres non prouvée | A_VERIFIER | Écart de preuve majeur : cible forte, démonstration runtime insuffisante. | Ajouter un marquage systématique `A_VERIFIER` sur toute mention de RLS prod effective. |
| CONF-13 | Absence de lecture/écriture inter-tenant | Aucune lecture/écriture inter-tenant ne doit être possible. | Le domaine est visé dans la cible ; le réel montre une prise en compte locale, mais pas une preuve complète bout en bout sur environnement prod réel. | cross-tenant tests, middleware | A_VERIFIER | Le sujet est clairement traité, mais pas encore prouvé à hauteur du contrat 2.0. | Écrire la doc en deux niveaux : “contrat cible” et “preuve observable locale actuelle”. |
| CONF-14 | Distinction minimale des rôles | Le produit doit distinguer au moins apprenant, tuteur, formateur, coordinateur, org admin, superadmin technique. | La cible fixe la liste minimale ; le réel montre plusieurs surfaces différenciées, mais pas une couverture complète et stabilisée de tous les rôles. | apprenant, testeur, trainer, admin partiel | AMBIGU | Les rôles existent doctrinalement ; le réel observable n’en démontre qu’une partie de manière nette. | Distinguer dans la doc rôle doctrinal, rôle observable, rôle démontré bout en bout. |
| CONF-15 | Coordinateur | Le coordinateur existe comme rôle cible, mais ses vues métier restent à préciser. | La spec le marque elle-même comme partiellement ouvert ; le réel mobilisé ici ne permet pas de l’adosser à une surface stabilisée. | pas d’ancrage réel clair dans le corpus utilisé | ABSENT / NOUVEAU_CONTRAT | C’est une responsabilité cible encore peu matérialisée dans le réel observable. | Marquer explicitement coordinateur comme rôle cible à contractualiser davantage. |
| CONF-16 | Administration d’organisation minimale | Le produit doit au moins permettre certaines capacités d’administration et d’exports, dans des bornes strictes. | Le réel montre un admin incomplet, avec création/édition d’utilisateurs mais pas suppression visible selon le document d’écarts. | `UsersView`, POST/PATCH sans DELETE visible | ALIGNE_DOC_PARTIEL | La responsabilité existe, mais les capacités réelles sont plus limitées que ne pourrait le suggérer une lecture trop rapide. | Documenter l’admin observée comme partielle, sans la présenter comme complète. |
| CONF-17 | Aucun accès libre au non-partagé via administration | L’administration ne doit pas contourner la confidentialité applicative. | La cible l’interdit clairement ; le réel ne documente pas de contournement libre, mais ne fournit pas non plus une matrice exhaustive de permissions back-office. | admin partiel, absence de preuve de lecture libre | ALIGNE_DOC_PARTIEL | Bonne orientation, preuve encore incomplète. | Ajouter des interdits explicites par rôle dans la doc de domaine. |
| CONF-18 | Validation humaine obligatoire pour certaines promotions de statut | Aucun statut dérivé provisoire ne doit être auto-promu vers un statut validé humainement. | La cible est très explicite ; le réel et le glossaire confirment `TrainerKnowledgeItem` et des statuts, mais l’ensemble des workflows de validation par rôle n’est pas encore décrit bout en bout ici. | `TrainerKnowledgeItem`, statuts, validation humaine | ALIGNE_DOC_PARTIEL | Très bon alignement doctrinal ; preuve produit fine encore partielle. | Clarifier la matrice “qui peut valider quoi” selon rôle habilité. |
| CONF-19 | Traces et évaluations partageables sous conditions | Les traces et évaluations peuvent circuler comme objets structurés, mais avec validation humaine finale et règles de partage. | Le glossaire et la spec convergent ; le réel montre `Trace`, `LearnerEvaluationRecord`, endpoints dédiés, mais la nomenclature reste partiellement dispersée. | `Trace`, `TraceCriterionAssessment`, `LearnerEvaluationRecord`, `request-evaluation`, `finalize-evaluation` | AMBIGU | Le fond métier existe, mais le vocabulaire et le contrat de partage restent à stabiliser. | Harmoniser la doc entre EvaluationTrace, Trace, LearnerEvaluationRecord et objets partageables. |
| CONF-20 | Evidence / preuves attachées à un contexte explicite | Les preuves ne doivent pas flotter librement hors gouvernance métier. | La cible le fixe ; le glossaire indique `Evidence` et `EvidenceBundleView` comme noms réels observés. | `Evidence`, `EvidenceBundleView` | RENOMMER_DANS_DOC | Le concept cible existe, mais la doc 2.0 doit citer les noms réels observés. | Ajouter `Evidence` et `EvidenceBundleView` dans les annexes et matrices d’objets. |
| CONF-21 | Exports structurés sous règles de confidentialité | Les exports doivent exister, avec règles de confidentialité adaptées. | La cible l’énonce ; le réel montre des traces, preuves et objets d’export, mais la cartographie complète des exports autorisés par rôle n’est pas consolidée ici. | exports, traces, preuves | ALIGNE_DOC_PARTIEL | Fond cohérent, contrat opérationnel incomplet. | Ajouter une matrice “objet exportable / rôle / conditions”. |
| CONF-22 | Suppression EXIF par défaut et GPS opt-in pour preuves photo | Les preuves photo doivent être gouvernées avec suppression EXIF par défaut et GPS opt-in. | La cible le fixe explicitement, mais le corpus réel mobilisé ici ne permet pas d’en apporter la preuve d’implémentation. | aucun ancrage réel probant dans ce corpus | A_VERIFIER | Contrat cible clair, preuve réelle absente dans le périmètre mobilisé. | Marquer ce point comme cible à vérifier dans le code et non comme capacité livrée. |
| CONF-23 | Endpoint `ui-state` comme lecture filtrée | L’état produit montrable est lu via un endpoint dérivé et filtré. | Le glossaire établit un alignement fort sur `GET /hugo/sessions/{id}/ui-state`. | `GET /hugo/sessions/{id}/ui-state` | ALIGNE | Très bon ancrage réel pour la confidentialité produit. | Conserver tel quel dans la documentation de référence. |
| CONF-24 | Endpoint `memory-summary` comme lecture gouvernée | La mémoire résumée passe par une vue contrôlée et non un accès brut. | Le glossaire établit un alignement fort sur `GET /hugo/sessions/{id}/memory-summary`. | `GET /hugo/sessions/{id}/memory-summary` | ALIGNE | Point d’appui solide pour ce domaine. | Conserver tel quel et l’utiliser comme exemple de projection gouvernée. |
| CONF-25 | Endpoint `progress` avec données filtrées par rôle et partage | La cible prévoit un endpoint de progression dédié, filtré par rôle et partage. | Le glossaire signale que le réel observable ne prouve pas clairement une route `progress`, la progression passant surtout par `ui-state` et services backend. | progression surtout exposée via `ui-state` | AMBIGU | Le besoin cible est clair, mais l’ancrage réel actuel est insuffisant. | Ne pas documenter `GET /progress` comme acquis du réel sans preuve supplémentaire. |
| CONF-26 | `PATCH /posture` comme action bornée et journalisée | La cible prévoit une demande de posture active encadrée. | Le glossaire signale que cette route n’est pas confirmée comme réelle dans le corpus audité mobilisé. | `PATCH /sessions/{id}/posture` non confirmé | A_VERIFIER | Ne pas présenter cette action comme livrée dans le réel observable. | Marquer explicitement l’endpoint comme cible / à confirmer. |
| CONF-27 | Front non pilote de la confidentialité | Le front ne décide pas de la vérité d’accès ; il consomme des contrats backend filtrés. | La spec, le glossaire et le document d’écarts convergent : pas de calcul P0 front, pas de logique moteur source de vérité côté interface. | `UIState`, backend-first, front 1.8 consommateur | ALIGNE | Très bon alignement structurel. | Rappeler ce point comme garde-fou de non-régression dans toutes les docs de domaine. |
| CONF-28 | Runtime distant identique au local sur ce domaine | Une lecture trop rapide pourrait supposer l’équivalence local / distant. | Le document d’écarts dit explicitement que la démo distante ne prouve pas l’état local, ni l’inverse, et laisse les points prod en `VRIFIER`. | `hugoback.encoors.com` | A_VERIFIER | Ce n’est pas une responsabilité cible mais un garde-fou critique de lecture du réel. | Ajouter une note standard de prudence sur tout point sécurité / accès dépendant du runtime distant. |

---

## 3. Lecture consolidée

### 3.1 Alignements les plus solides

Les points les plus solides sur ce domaine sont :
- `UIState` comme projection produit filtrée ;
- l’absence d’exposition frontale des champs P0 bruts ;
- `memory-summary` comme lecture gouvernée ;
- l’orientation générale confidentialité-first ;
- le backend comme source de vérité des surfaces visibles.

### 3.2 Écarts documentaires prioritaires

Les écarts documentaires prioritaires sont :
- formaliser proprement le **partage explicite** par type d’objet ;
- distinguer **rôle doctrinal**, **rôle observable**, **rôle démontré** ;
- harmoniser la nomenclature autour de **Trace / EvaluationTrace / LearnerEvaluationRecord / Evidence** ;
- expliciter plus nettement ce qui est **prouvé localement** et ce qui reste **A_VERIFIER** côté runtime distant et RLS prod.

### 3.4 Matrice rôle × données sensibles — extrait tuteur (post cluster 3)

| Rôle | Donnée / surface | `share_verbatim=false` | `share_verbatim=true` | Preuve locale |
|------|------------------|------------------------|----------------------|---------------|
| **TUTOR** | `timeline.sessions[].messages[]` | `[]` (vide) | contenu + variantes assistant | `test_cluster3_oracles.py` B1-01 |
| **TUTOR** | `timeline.sessions[].first_learner_message` | `""` (vide) | aperçu tronqué 1er message | idem (post-patch `views_dashboard.py`) |
| **TUTOR** | Champs P0 / TurnState bruts | non exposés | non exposés ; `pilotage` agrégé uniquement | doctrine + `pilotage` dans timeline |

Oracle de référence : **B1-01**. Suite smoke : `pytest apps/hugo/tests/test_cluster3_oracles.py`.

---

Ne doivent pas être présentés comme acquis du réel :
- une **RLS Postgres prod pleinement démontrée** ;
- une **couverture complète des permissions par rôle** ;
- un **rôle coordinateur déjà stabilisé dans le produit** ;
- l’existence prouvée de tous les **workflows de partage** et de tous les **endpoints cibles** ;
- l’équivalence de comportement entre le local audité et `hugoback.encoors.com`.

# 02_decisions_documentaires — 90_confidentialite_partage_multitenant_roles

## Domaine

- `DOMAINE_CODE = 90_confidentialite_partage_multitenant_roles`
- `DOMAINE_LABEL = confidentialité, partage, multi-tenant et rôles`

---

## 1. Objet du document

Ce document fixe les **décisions documentaires** à appliquer pour le domaine
**confidentialité / partage / multi-tenant / rôles** dans Hugo cœur.

Il ne tranche pas :
- un design infra complet ;
- une implémentation code future ;
- ni une vérité runtime non auditée.

Il sert à décider **comment écrire juste** ce domaine dans la documentation active, à partir de trois sources à toujours distinguer :
- la **cible 2.0** ;
- le **réel local audité** ;
- le **runtime distant / prod / flags** lorsqu’ils ne sont pas démontrés dans le corpus.

---

## 2. Principes de rédaction retenus

### D1 — Toujours séparer cible, réel et à vérifier

Décision :
- toute rédaction de ce domaine distinguera explicitement :
  - **cible 2.0** ;
  - **réel observable localement** ;
  - **A_VERIFIER** pour le runtime distant, la RLS prod réelle, les flags et les permissions non démontrées.

Conséquence documentaire :
- plus aucun document actif ne doit écrire ce domaine comme si la spec 2.0 prouvait le livré, ni comme si la démo distante prouvait le runtime local.

### D2 — La doctrine 2.0 reste la structure canonique

Décision :
- on conserve la structure doctrinale 2.0 : confidentialité-first, partage explicite, multi-tenant strict, rôles distincts, front drivé par états dérivés, backend source de vérité.

Conséquence documentaire :
- on ne rebaptise pas ce domaine depuis les seuls noms techniques du code ;
- on ajoute les noms réels observés seulement comme **ancrages** ou **raccords de vocabulaire**.

### D3 — Le glossaire reste un pont, jamais une preuve

Décision :
- le glossaire d’alignement sera utilisé pour raccorder les termes doctrinaux aux noms réels observés ;
- il ne pourra jamais, à lui seul, justifier une affirmation de livraison ou d’implémentation prouvée.

Conséquence documentaire :
- toute phrase de type “X existe réellement” devra rester adossée au corpus d’audit du réel, pas au seul glossaire.

---

## 3. Décisions de formulation sur le domaine

### D4 — Formulation canonique à conserver

Décision :
- la formule de référence à conserver est :

> Hugo cœur applique une doctrine **confidentialité-first**, avec **partage explicite**, **multi-tenant strict**, absence d’exposition libre du **verbatim non partagé**, et surfaces produit dérivées d’états backend gouvernés.

Cette formulation est doctrinalement juste et compatible avec la cible 2.0.

### D5 — Le verbatim non partagé est privé par défaut

Décision :
- toute documentation active du domaine doit reprendre explicitement la règle suivante :

> Le verbatim est privé par défaut. Les rôles non apprenant ne disposent pas d’un accès libre au contenu apprenant non partagé.

Cette règle vaut au minimum pour :
- tuteur ;
- formateur ;
- coordinateur ;
- administrateur d’organisation ;
- superadministration technique.

Conséquence documentaire :
- on ne laisse plus cette interdiction implicite dans les seuls tableaux de spec ;
- elle doit apparaître textuellement dans les documents de domaine.

### D6 — Le front ne voit que des projections filtrées

Décision :
- ce domaine doit être documenté comme **backend-first**, avec exposition produit via objets filtrés et dérivés, en premier lieu `UIState` et `memory-summary`.

Conséquence documentaire :
- on documente comme réel solide :
  - `GET /hugo/sessions/{id}/ui-state` ;
  - `GET /hugo/sessions/{id}/memory-summary` ;
- on ne documente pas le front comme source de vérité sur la confidentialité.

### D7 — Aucune exposition des champs P0 bruts au front

Décision :
- la non-exposition des champs P0 bruts au front reste une décision documentaire ferme, à maintenir comme invariant du domaine.

Conséquence documentaire :
- toute doc produit ou technique décrivant des surfaces visibles doit préciser que `TurnState`, le contrat de décision brut, les variables P0 et les prompts complets restent hors exposition frontale.

---

## 4. Décisions sur les rôles

### D8 — Les rôles restent doctrinaux, mais leur matérialisation réelle est inégale

Décision :
- la documentation doit continuer à distinguer au minimum :
  - apprenant ;
  - tuteur ;
  - formateur ;
  - coordinateur ;
  - administrateur d’organisation ;
  - superadministration technique.

Conséquence documentaire :
- on ne présente pas tous ces rôles comme également démontrés dans le réel ;
- on distingue désormais :
  - **rôle doctrinal** ;
  - **rôle observable** ;
  - **rôle encore partiellement ouvert**.

### D9 — Le coordinateur reste un rôle cible partiellement ouvert

Décision :
- le coordinateur doit être documenté comme un **rôle cible cadré**, mais **non encore stabilisé dans ses surfaces réelles**.

Conséquence documentaire :
- on cesse de parler du coordinateur comme d’un rôle pleinement matérialisé dans le produit actuel ;
- il reste présent dans la doctrine, mais marqué comme **à préciser** dans les vues métier et habilitations fines.

### D10 — L’admin observable doit être documenté comme partiel

Décision :
- l’administration observable dans le réel audité est décrite comme **partielle**, notamment sur la gestion utilisateurs, et ne doit pas être vendue comme une administration complète et stabilisée.

Conséquence documentaire :
- toute mention de `UsersView` ou des surfaces admin doit rappeler ce caractère partiel ;
- absence de suppression visible, périmètre incomplet, capacités bornées.

### D11 — La superadministration technique n’est pas un droit applicatif libre

Décision :
- la superadministration technique reste documentée comme rôle d’exploitation / supervision, non comme rôle applicatif donnant lecture libre du contenu apprenant non partagé.

Conséquence documentaire :
- on interdit toute formulation ambiguë laissant penser qu’un rôle technique contourne par principe la confidentialité produit.

---

## 5. Décisions sur partage, validation et export

### D12 — Séparer visibilité, partage, export et validation humaine

Décision :
- la documentation active ne doit plus employer comme synonymes :
  - visible ;
  - partageable ;
  - partagé ;
  - exportable ;
  - validé humainement.

Conséquence documentaire :
- chaque matrice ou paragraphe du domaine devra distinguer ces statuts comme des dimensions différentes.

### D13 — Le partage explicite doit être décrit par objet

Décision :
- le partage explicite sera désormais documenté **par type d’objet**, et non comme principe abstrait unique.

Objets à distinguer au minimum :
- synthèse ;
- trace ;
- évaluation ;
- mémoire résumée ;
- preuves ;
- verbatim.

Conséquence documentaire :
- la doc de domaine intégrera une matrice ou un tableau dédié aux objets partageables et à leurs conditions.

### D14 — La validation humaine reste une frontière documentaire ferme

Décision :
- toute formulation sur traces, évaluations, preuves et savoirs gouvernés doit rappeler que la validation finale reste humaine et qu’aucun statut dérivé provisoire n’est auto-promu vers un statut validé.

Conséquence documentaire :
- on garde cette règle comme frontière transversale entre moteur, produit et gouvernance métier.

### D15 — Les exports et preuves doivent rester contextualisés

Décision :
- les preuves et exports restent documentés comme objets **rattachés à un contexte explicite** ; ils ne doivent jamais être décrits comme circulant librement hors gouvernance métier.

Conséquence documentaire :
- les noms réels `Evidence` et `EvidenceBundleView` doivent apparaître dans les annexes ou matrices de vocabulaire du domaine.

---

## 6. Décisions sur multi-tenant et RLS

### D16 — Le multi-tenant strict reste un invariant cible ferme

Décision :
- la documentation conserve sans affaiblissement la cible 2.0 :
  **isolation stricte par organisation, absence de lecture/écriture inter-tenant, RLS active comme contrainte produit**.

Conséquence documentaire :
- on ne relativise pas la cible ;
- en revanche on distingue beaucoup mieux la **cible ferme** et la **preuve observée**.

### D17 — La preuve RLS prod reste A_VERIFIER

Décision :
- toute mention de **RLS Postgres effective en prod** doit être marquée `A_VERIFIER` tant qu’un audit probant de l’environnement concerné n’est pas disponible.

Conséquence documentaire :
- on peut documenter :
  - l’exigence cible 2.0 ;
  - l’existence d’indices ou de middleware ;
  - l’existence de tests cross-tenant locaux ;
- mais pas écrire que la RLS prod est prouvée dans le corpus actuel.

### D18 — La démo distante ne prouve pas l’état sécurité du local

Décision :
- la documentation de domaine doit rappeler qu’une démo contre `hugoback.encoors.com` ne prouve pas l’état du `hugoback` local, et inversement.

Conséquence documentaire :
- tout ce qui dépend du runtime distant, des flags ou de la configuration prod reste explicitement séparé du réel local audité.

---

## 7. Décisions de vocabulaire

### D19 — Conserver les noms doctrinaux structurants

Décision :
- on conserve comme noms doctrinaux centraux :
  - confidentialité-first ;
  - partage explicite ;
  - multi-tenant strict ;
  - UIState ;
  - mémoire gouvernée résumée ;
  - validation humaine ;
  - rôles non apprenant.

Conséquence documentaire :
- ces termes restent la colonne vertébrale des docs de domaine.

### D20 — Ajouter les noms réels observés utiles

Décision :
- les documents de domaine feront apparaître, quand utile, les noms réels suivants comme ancrages :
  - `UIState` ;
  - `GET /hugo/sessions/{id}/ui-state` ;
  - `GET /hugo/sessions/{id}/memory-summary` ;
  - `UsersView` ;
  - `Evidence` ;
  - `EvidenceBundleView` ;
  - `Trace` ;
  - `TraceCriterionAssessment` ;
  - `LearnerEvaluationRecord`.

Conséquence documentaire :
- le domaine sera mieux raccordé au réel sans perdre la doctrine.

### D21 — Ne pas forcer certains mappings comme déjà stabilisés

Décision :
- la documentation ne doit pas présenter comme stabilisés dans le réel :
  - la nomenclature complète des permissions par rôle ;
  - la complétude du rôle coordinateur ;
  - une preuve RLS prod ;
  - l’équivalence local / distant ;
  - un modèle final entièrement unifié entre `EvaluationTrace`, `Trace` et `LearnerEvaluationRecord`.

Conséquence documentaire :
- ces points restent marqués comme **ouverts**, **partiels** ou `A_VERIFIER`.

---

## 8. Décisions de maintenance documentaire

### D22 — Ajouter une matrice de lecture par rôle

Décision :
- les documents actifs du domaine devront intégrer une matrice simple :
  - rôle ;
  - voit ;
  - peut agir ;
  - ne voit pas ;
  - niveau de preuve.

Cette matrice devient la forme de référence pour éviter les formulations flottantes.

### D23 — Ajouter une matrice des objets sensibles

Décision :
- les documents actifs du domaine devront intégrer une matrice des objets sensibles distinguant :
  - visible ;
  - partageable ;
  - exportable ;
  - validable humainement ;
  - non partagé par défaut.

### D24 — Ajouter un encadré standard `A_VERIFIER`

Décision :
- chaque document de domaine devra comporter un encadré standard listant :
  - RLS prod réelle ;
  - runtime distant ;
  - flags ;
  - permissions fines non auditées ;
  - surfaces coordinateur incomplètement démontrées.

### D25 — Éviter la sur-correction

Décision :
- aucune décision documentaire de ce domaine ne doit pousser à une refonte code par principe si le réel couvre déjà la responsabilité métier centrale.

Conséquence documentaire :
- priorité à :
  - la clarification des contrats ;
  - l’alignement vocabulaire ;
  - le marquage des niveaux de preuve ;
  - la distinction entre cible et réel.

---

## 9. Formulation de référence à réemployer

La formulation de référence à réemployer dans les documents de ce domaine est la suivante :

> Hugo cœur documente la confidentialité comme un invariant **backend-first** : surfaces produit filtrées via états dérivés, **verbatim privé par défaut**, **partage explicite par objet**, rôles non apprenant sans accès libre au non partagé, et **multi-tenant strict** posé comme exigence cible. Le réel local audité confirme plusieurs ancrages solides (`UIState`, `memory-summary`, non-exposition des champs P0 bruts), tandis que la preuve complète de certains points, notamment la **RLS prod effective** et certaines permissions fines par rôle, reste explicitement `A_VERIFIER`.

---

## 10. Effet attendu de ces décisions

Après application de ces décisions documentaires, ce domaine doit devenir :
- plus vrai sur le **réel** ;
- plus net sur la **cible** ;
- plus prudent sur le **distant / prod / flags** ;
- plus robuste sur les **rôles** ;
- plus lisible sur les différences entre **visible**, **partageable**, **exportable** et **validé humainement**.

La documentation doit alors pouvoir servir de base fiable :
- pour la suite des matrices d’écarts ;
- pour les prompts Cursor d’audit ;
- et pour les compléments backend ou produit additifs, sans régression doctrinale.

# 03_backlog_actions — 90_confidentialite_partage_multitenant_roles

## Domaine

- `DOMAINE_CODE = 90_confidentialite_partage_multitenant_roles`
- `DOMAINE_LABEL = confidentialité, partage, multi-tenant et rôles`

---

## 1. Objet du backlog

Ce backlog regroupe les **actions documentaires prioritaires** à mener pour recaler proprement le domaine
**confidentialité / partage / multi-tenant / rôles** dans Hugo cœur.

Il ne s’agit ni :
- d’un plan de refonte sécurité global ;
- ni d’un audit infra complet ;
- ni d’un backlog produit transverse.

Le but est de :
- remettre la documentation au bon niveau de vérité ;
- clarifier les contrats de visibilité et de partage ;
- aligner le vocabulaire cible / réel ;
- éviter les sur-affirmations sur la prod distante, la RLS ou les rôles non encore démontrés bout en bout.

---

## 2. Règles de priorisation

- `P1` : action documentaire nécessaire pour éviter une contre-vérité ou une lecture dangereuse du réel.
- `P2` : action structurante importante pour stabiliser le contrat documentaire du domaine.
- `P3` : action utile de finition, de lisibilité ou de consolidation, non bloquante pour le recalage principal.

### Types d’action

- `DOC` : mise à jour documentaire.
- `SPEC` : clarification ou ajout dans la cible 2.0.
- `GLOSSAIRE` : alignement de vocabulaire.
- `MATRICE` : ajout ou correction dans les matrices de domaine / spec.
- `A_VERIFIER` : point à marquer explicitement comme non prouvé dans le corpus.
- `PROMPT_CURSOR` : préparation d’un prompt Cursor d’audit ciblé, sans lancer ici le chantier code.

---

## 3. Backlog priorisé

| ID | Priorité | Type | Action | Résultat attendu | Dépendances |
|---|---|---|---|---|---|
| CONFDOC-01 | P1 | DOC | Ajouter, dans les documents actifs du domaine, une formulation standard explicite : **“verbatim privé par défaut, jamais librement visible hors partage explicite”**. | Plus aucun document actif ne laisse penser qu’un rôle non apprenant peut lire librement le verbatim non partagé. | `spec_canonique_hugo_2_0.md`, rapport d’écarts |
| CONFDOC-02 | P1 | DOC | Ajouter une note standard de prudence sur toute mention de `hugoback.encoors.com` : le runtime distant ne prouve pas automatiquement l’état du local audité, ni l’inverse. | Les docs du domaine cessent de sur-déduire le comportement sécurité / accès depuis la démo distante. | `05_ECARTS_DOC_CODE_PRODUIT.md` |
| CONFDOC-03 | P1 | DOC | Ajouter une mention explicite `A_VERIFIER` sur toute affirmation de **RLS Postgres effective en prod**. | La doc distingue clairement l’exigence cible 2.0 et la preuve réellement disponible dans le corpus. | `spec_canonique_hugo_2_0.md`, `05_ECARTS_DOC_CODE_PRODUIT.md` |
| CONFDOC-04 | P1 | DOC | Documenter noir sur blanc que l’admin d’organisation, le tuteur, le formateur et la superadministration technique n’ont **pas** de droit générique de lecture du contenu apprenant non partagé. | Les interdits de lecture libre deviennent visibles et non implicites dans la doc de domaine. | `spec_canonique_hugo_2_0.md` |
| CONFDOC-05 | P1 | DOC | Ajouter une section “niveaux de vérité” spécifique au domaine : **cible 2.0 / réel local audité / runtime distant A_VERIFIER**. | La documentation de domaine devient auto-stabilisante et évite les glissements de preuve. | rapport d’écarts, matrice d’écarts |

| ID | Priorité | Type | Action | Résultat attendu | Dépendances |
|---|---|---|---|---|---|
| CONFDOC-06 | P2 | MATRICE | Créer une matrice documentaire **objet visible / objet partageable / objet exportable / objet validable**. | Le domaine cesse de mélanger visibilité, partage, validation humaine et export. | `spec_canonique_hugo_2_0.md`, matrice d’écarts |
| CONFDOC-07 | P2 | MATRICE | Créer une matrice **rôle doctrinal / rôle observable / rôle démontré bout en bout / rôle encore ouvert**. | Les rôles cessent d’être décrits comme un bloc homogène alors que leur niveau de matérialisation diffère. | matrice d’écarts |
| CONFDOC-08 | P2 | DOC | Ajouter un sous-bloc explicite “ce que voit / ce que ne voit pas” pour les rôles : apprenant, tuteur, formateur, org admin, superadmin technique, coordinateur. | Les interdits et limites par rôle deviennent lisibles sans ambiguïté. | `spec_canonique_hugo_2_0.md` |
| CONFDOC-09 | P2 | DOC | Ajouter une section “partage explicite” qui distingue les objets suivants : synthèse, trace, évaluation, mémoire résumée, preuves, verbatim. | Le contrat de partage ne repose plus sur une formule générale trop abstraite. | `spec_canonique_hugo_2_0.md`, rapport d’écarts |
| CONFDOC-10 | P2 | DOC | Documenter explicitement que `UIState` et `memory-summary` sont aujourd’hui les meilleurs ancrages réels du domaine côté surfaces filtrées. | Le domaine gagne en précision sur ses preuves réelles les plus solides. | glossaire d’alignement |
| CONFDOC-11 | P2 | GLOSSAIRE | Ajouter ou renforcer les correspondances de vocabulaire : `Evidence`, `EvidenceBundleView`, `Trace`, `TraceCriterionAssessment`, `LearnerEvaluationRecord`, `UsersView`. | La doc 2.0 parle plus juste du réel sans perdre la structure doctrinale. | glossaire d’alignement |
| CONFDOC-12 | P2 | DOC | Ajouter une note explicite : l’admin observable dans le réel audité est **partiel** et ne doit pas être présenté comme un modèle d’administration produit finalisé. | On évite de sur-vendre la gouvernance UI déjà livrée. | `05_ECARTS_DOC_CODE_PRODUIT.md` |

| ID | Priorité | Type | Action | Résultat attendu | Dépendances |
|---|---|---|---|---|---|
| CONFDOC-13 | P2 | SPEC | Ajouter, dans la cible 2.0 ou son complément, une formulation plus précise du statut du **coordinateur** : rôle cadré doctrinalement, surfaces encore ouvertes. | Le coordinateur cesse d’apparaître tantôt comme rôle acquis, tantôt comme simple hypothèse flottante. | `spec_canonique_hugo_2_0.md` |
| CONFDOC-14 | P2 | SPEC | Clarifier la relation entre **validation humaine**, **partage**, **export**, et **circulation des traces / évaluations / preuves**. | La doc sépare mieux les notions souvent confondues dans ce domaine. | `spec_canonique_hugo_2_0.md` |
| CONFDOC-15 | P2 | DOC | Ajouter une phrase stable rappelant que la confidentialité-first est un **invariant d’architecture backend-first**, pas une simple règle d’affichage UI. | Le domaine est mieux ancré dans la doctrine Hugo cœur et moins réductible à une logique front. | `spec_canonique_hugo_2_0.md` |
| CONFDOC-16 | P2 | DOC | Clarifier le statut documentaire de `GET /progress` et `PATCH /posture` : **contrats cibles / non prouvés comme acquis du réel**. | Les endpoints cibles ne sont plus lus comme déjà livrés. | glossaire d’alignement |
| CONFDOC-17 | P2 | DOC | Ajouter un encadré “ce que le domaine ne prouve pas encore” : RLS prod, équivalence local/distant, couverture complète des permissions, coordinateur finalisé. | Les zones ouvertes deviennent explicites et non disséminées. | rapport d’écarts, matrice d’écarts |

| ID | Priorité | Type | Action | Résultat attendu | Dépendances |
|---|---|---|---|---|---|
| CONFDOC-18 | P3 | GLOSSAIRE | Ajouter une petite annexe “noms réels observés utiles pour ce domaine” avec : `UIState`, `memory-summary`, `UsersView`, `Evidence`, `LearnerEvaluationRecord`, `Trace`. | Le travail ultérieur de prompts Cursor et de mise à jour de spec devient plus précis. | glossaire d’alignement |
| CONFDOC-19 | P3 | DOC | Ajouter une section “anti-dérives documentaires” rappelant : ne pas exposer le verbatim, ne pas faire du front la source de vérité, ne pas déduire la prod depuis la démo distante. | Le domaine embarque ses propres garde-fous de non-régression. | `spec_canonique_hugo_2_0.md`, `05_ECARTS_DOC_CODE_PRODUIT.md` |
| CONFDOC-20 | P3 | DOC | Harmoniser la rédaction entre “non partagé”, “partageable”, “visible”, “confirmable”, “exportable”, “validé humainement”. | La doc gagne en cohérence terminologique et évite les faux synonymes. | matrice d’écarts |
| CONFDOC-21 | P3 | SPEC | Ajouter un mini pseudo-schéma documentaire des états d’objet utiles au domaine : privé, partageable, partagé, exportable, validable humainement. | La lecture produit / métier devient plus robuste sans exiger encore une modélisation code complète. | `spec_canonique_hugo_2_0.md` |
| CONFDOC-22 | P3 | PROMPT_CURSOR | Préparer un prompt Cursor ciblé “cartographier les permissions réelles par rôle et par endpoint sur le domaine confidentialité / partage / multi-tenant”. | Le prochain audit technique pourra être lancé avec un cadrage propre et borné. | rapport d’écarts, matrice d’écarts |
| CONFDOC-23 | P3 | PROMPT_CURSOR | Préparer un prompt Cursor ciblé “vérifier les preuves réelles de RLS / cross-tenant sur Postgres vs SQLite”. | Le chantier de vérification infra/documentation pourra être mené sans extrapolation. | `05_ECARTS_DOC_CODE_PRODUIT.md` |

---

## 4. Séquencement recommandé

### Sprint documentaire 1 — vérité et prudence

Actions à mener en premier :
- `CONFDOC-01`
- `CONFDOC-02`
- `CONFDOC-03`
- `CONFDOC-04`
- `CONFDOC-05`

Objectif :
- supprimer les contre-vérités ou glissements de lecture les plus dangereux ;
- rendre explicites les garde-fous du domaine ;
- recaler immédiatement la différence entre cible, réel local et distant à vérifier.

### Sprint documentaire 2 — contrats de visibilité et de partage

Actions à mener ensuite :
- `CONFDOC-06`
- `CONFDOC-07`
- `CONFDOC-08`
- `CONFDOC-09`
- `CONFDOC-10`
- `CONFDOC-14`
- `CONFDOC-16`
- `CONFDOC-17`

Objectif :
- stabiliser le cœur documentaire du domaine ;
- séparer proprement rôles, objets, niveaux de visibilité et niveaux de validation ;
- clarifier ce qui est déjà observable et ce qui reste cible.

### Sprint documentaire 3 — alignement vocabulaire et consolidation

Actions à mener ensuite :
- `CONFDOC-11`
- `CONFDOC-12`
- `CONFDOC-13`
- `CONFDOC-15`
- `CONFDOC-18`
- `CONFDOC-19`
- `CONFDOC-20`
- `CONFDOC-21`

Objectif :
- rendre la doc durablement exploitable ;
- réduire les collisions de vocabulaire cible / réel ;
- éviter les régressions doctrinales.

### Sprint d’appui audit futur

Actions à préparer sans les exécuter ici :
- `CONFDOC-22`
- `CONFDOC-23`

Objectif :
- préparer les futurs audits Cursor sur permissions réelles et preuves RLS/cross-tenant ;
- garder un cadre borné avant de toucher au code ou à l’infra.

---

## 5. Priorités de vérité

### À corriger avant toute autre extension doc

Les urgences documentaires de ce domaine sont :
- ne pas laisser entendre qu’un rôle non apprenant peut lire librement le non-partagé ;
- ne pas laisser croire que la RLS prod est déjà prouvée ;
- ne pas confondre démo distante et réel local audité ;
- ne pas présenter l’admin observée comme un modèle complet et stabilisé.

### À garder comme principe de suite

La suite documentaire doit privilégier :
- les **contrats clarifiés** ;
- le **vocabulaire aligné** ;
- les **niveaux de preuve explicites** ;
- les **compléments backend-first additifs**.

Elle ne doit pas réécrire Hugo cœur comme un système piloté par le front, ni transformer des hypothèses de gouvernance en capacités déjà démontrées.

---

## 6. Résultat attendu à la fin du backlog doc

À l’issue de ces actions documentaires, le domaine doit permettre de lire proprement que :
- la doctrine 2.0 est très ferme sur confidentialité, partage explicite et multi-tenant strict ;
- le réel local audité est globalement cohérent avec cette doctrine sur l’orientation générale ;
- plusieurs preuves fortes existent déjà (`UIState`, `memory-summary`, non-exposition des champs P0 bruts, objets gouvernés) ;
- plusieurs points restent explicitement `A_VERIFIER`, notamment la RLS prod réelle, certaines permissions fines par rôle et l’équivalence local / distant ;
- les rôles et objets du domaine sont décrits sans confusion entre **visible**, **partageable**, **exportable**, **validable** et **non partagé**.

---

## 7. Mise à jour cluster dev vague 2 encadrants (réel local)

**Sources :** `cluster_dev_encadrants_exports_vague2_resultats.md` · `test_encadrants_role_guards.py`, `test_d2_m07_confidentiality_oracles.py`.

| ID / thème | Statut après cluster |
|---|---|
| CONF-07 B1-01 verbatim tuteur | **ALIGNE** (inchangé, confirmé) |
| CONF-08 formateur sans accès non-partagé | **ALIGNE_DOC_PARTIEL** — guards trainer knowledge ajoutés |
| CONF-09 ORGADMIN sans lecture libre | **ALIGNE** — exports admin-like ; pas de timeline sans partage |
| CONF-22 EXIF | **ALIGNE** local — strip implémenté ; prod **A_VÉRIFIER** |
| Décalage exports front/back | **RÉDUIT** — `roleGuards.isOrgAdminLike` |
| Guards `/dashboard` LEARNER | **RÉDUIT** — router `requiresEncadrant` |
| RLS Postgres | **A_VÉRIFIER** |
| D2-M12 ORGADMIN vs SUPERADMIN | **OUVERT** |

---

## 8. Mise à jour cluster audit vague 5 — E2E & Encoors

**Sources :** `cluster_tests_e2e_et_encoors_vague5_resultats.md` · `test_vague5_e2e_scenarios.py`.

| Thème | Statut après vague 5 |
|---|---|
| B1-01 timeline verbatim | **ALIGNE** — confirmé E2E API T1 |
| Validation trace tuteur | **ALIGNE** — POST `/traces/{id}/validate/` |
| Guards exports ORGADMIN | **ALIGNE** — TUTOR 403 confirmé O1 |
| Trainer sans exports org | **ALIGNE** — F1 |
| RLS Postgres prod | **A_VÉRIFIER** — inchangé |
| Encoors équivalence | **DIVERGENCE partielle** — routes v3/v4 absentes (404) |
| E2E navigateur Playwright | **PARTIEL** — absent ; scénario manuel OPS |

---

## 9. Mise à jour cluster 8 OPS — smoke UI / RLS

**Sources :** `cluster_ops_smoke_ui_encoors_rls_resultats.md` · `tests_playwright/*` · `test_rls_postgres_minimal.py`.

| Thème | Statut après cluster 8 |
|---|---|
| Smoke UI TUTOR sans verbatim | **ALIGNE** — Playwright 4/4 local |
| Guards exports UI LEARNER | **ALIGNE** — smoke ORGADMIN |
| RLS policies tables sensibles | **ALIGNE** local migrations |
| RLS SQL cross-tenant prod | **A_VÉRIFIER** — superuser bypass en dev |
| RLS API cross-tenant session | **ALIGNE** — 404 org A → session org B |
| Encoors auth EVAL1/O1 | **A_VÉRIFIER** — credentials absents |

---

## 10. Mise à jour cluster 11 — RLS prod & Encoors

**Sources :** `cluster11_verrouillage_runtime_vs_encoors_resultats.md` · `audit_rls_prod_template.sql` · test app role PASS.

| Thème | Statut cluster 11 |
|---|---|
| RLS app role local | **ALIGNE** — cluster 10 PASS |
| RLS prod Postgres | **A_VÉRIFIER** — template SQL livré |
| API cross-tenant 404 | **ALIGNE** local |
| Encoors parité fonctionnelle | **A_VÉRIFIER** — oracle auth |
| COORDO | **COURONNE** |

---

## 11. Mise à jour cluster 14 — COORDO & encadrants

**Sources :** `cluster14_interfaces_encadrants_observabilite_plan_resultats.md` · `roleGuards.js`, `access_control.py`.

| Thème | Statut cluster 14 |
|---|---|
| Rôle `COORDO` backend | **ALIGNE** — modèle + `TUTOR_ROLES` |
| Front `isTutorLike` inclut COORDO | **ALIGNE** — accès `/app/tutor/*` |
| Surface COORDO dédiée | **ABSENT** — décision doc : héritage tuteur |
| Vues cohorte COORDO | **COURONNE** |
| Exports E3/E4 TUTOR | **ALIGNE** — 403 API |

---

---