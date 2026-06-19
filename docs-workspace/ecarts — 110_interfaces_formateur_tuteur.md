# 00_rapport_ecarts — 110_interfaces_formateur_tuteur

> **Mise à jour post-cluster 16 — 2026-06-18** · **Apprenant PARTIEL+ C16 :** posture, mémoire, profils, scène, CTA advisory (`PostureSelector`, `LearnerMemoryPanel`, `LearnerSceneContextBar`). **Tests :** C15 (21) + C16 (15+10). **A_VÉRIFIER :** Encoors, IFT-042.

## Domaine

- `DOMAINE_CODE = 110_interfaces_formateur_tuteur`
- `DOMAINE_LABEL = interfaces formateur / tuteur`

---

## 1. Objet du rapport

Ce rapport qualifie, pour le seul domaine **interfaces formateur / tuteur** de Hugo cœur, l’écart entre :
- la **cible 2.0** décrite par la spec canonique et les documents de cadrage projet ;
- le **réel observable** décrit par les audits du workspace Hugo réel ;
- le **pont de vocabulaire** fourni par le glossaire d’alignement entre doctrine et implémentation.

Le périmètre couvert ici concerne les surfaces et contrats d’usage destinés aux rôles **tuteur** et **formateur** dans Hugo cœur : lecture de progression, accès aux traces et objets partageables, validation humaine, lecture de timeline, vues de cohorte, surfaces trainer liées à la base de connaissances, et garde-fous de confidentialité. Ce rapport ne traite ni Hugo & Cie, ni l’interface apprenant comme domaine principal, sauf lorsque cette interface conditionne l’accès ou le partage vers les rôles formateur/tuteur.

---

## 2. Règles de lecture et de vérité

### 2.1 Corpus mobilisé

Pour parler du **réel**, la priorité est donnée aux documents d’audit du corpus Hugo réel, notamment :
- `02_ETAT_MOTEUR_REEL.md` pour les services backend et endpoints observables ;
- `03_ETAT_PRODUIT_REEL.md` pour les surfaces réellement montrables côté produit ;
- `07_RUNTIME_DEMO_REFERENCE.md` et `09_PARCOURS_DEMO_ET_SCENARIOS.md` pour ce qui peut être montré en démo ;
- `05_ECARTS_DOC_CODE_PRODUIT.md` pour les divergences confirmées entre documentation, code local et runtime distant supposé.

Pour parler de la **cible**, on s’appuie d’abord sur :
- `spec_canonique_hugo_2_0.md` ;
- les documents 2.0 relatifs aux orchestrateurs formateur / tuteur ;
- les compléments doctrinaux associés.

Le **glossaire d’alignement Hugo réel vs spec** est utilisé comme pont de vocabulaire entre noms doctrinaux 2.0 et noms réellement observés dans le code ou les audits. Il ne constitue jamais, à lui seul, une preuve d’implémentation.

Le document `SPEC_POC_v1.5-update-27_03_2026.md` est utilisé ici comme document de cadrage historique utile sur les rôles, visibilités et endpoints POC, mais pas comme preuve suffisante de l’état livré actuel.

### 2.2 Garde-fous de lecture

- La spec 2.0 décrit une **cible** ; elle ne prouve jamais qu’une interface ou un workflow est déjà livré.
- Le glossaire aligne le vocabulaire ; il ne prouve pas que les objets et surfaces correspondantes sont complètes ou stabilisées.
- Une route, un composant, une vue testeur ou une mention dans une spec POC ne prouvent pas à eux seuls une surface produit pleinement opérationnelle.
- Toute affirmation qui dépend du runtime distant, d’un `.env`, d’un flag ou d’une variante non auditée localement reste marquée `A_VERIFIER`.
- Le domaine doit rester lu dans la doctrine Hugo cœur : backend Django orchestré, TutorPrompt pivot runtime, P0 conserv et enrichi additivement, front drivé par états, confidentialité-first, partage explicite, multi-tenant strict.

---

## 3. Périmètre cible 2.0 du domaine

### 3.1 Ce que la cible 2.0 fixe

Dans la cible Hugo 2.0, les interfaces **tuteur** et **formateur** ne sont pas des consoles de pilotage libre du moteur. Ce sont des surfaces métier gouvernées, branchées sur des objets backend structurés.

La cible fixe notamment les principes suivants :

- La couche **tuteur** est orientée lecture de progression, détection de blocages, compréhension de la maturité conversationnelle, consultation de traces partageables, recommandations d’accompagnement et, selon les cas, validation de certains objets partageables.
- La couche **formateur** est liée à l’orchestrateur formateur et à la base de connaissances gouvernée. Elle doit permettre d’ingérer des documents, expliciter du savoir métier, produire ou corriger des `TrainerKnowledgeItem`, relier ces objets au référentiel, et valider humainement ce qui doit l’être.
- Ces interfaces doivent consommer des objets dérivés backend de type `UIState`, `ConversationProgress`, synthèses, signaux de qualité conversationnelle, objets de mémoire gouvernée, traces et évaluations terminales partageables.
- Le **front ne pilote pas** directement le moteur conversationnel apprenant. Il ne force pas librement le P0, n’expose pas les prompts complets, et ne transforme pas un rôle tuteur/formateur en opérateur direct du runtime apprenant.
- Le **verbatim non partagé** reste privé par défaut. Les rôles tuteur, formateur, coordinateur et administration ne doivent voir que ce qui a été explicitement partagé ou rendu visible par un contrat produit gouverné.
- La validation finale de certaines traces, connaissances ou évaluations reste **humaine**. Le produit ne doit pas laisser croire que Hugo certifie ou valide seul.

### 3.2 Ce que la cible 2.0 laisse encore ouvert

La cible 2.0 fixe bien les responsabilités et garde-fous, mais plusieurs éléments restent encore partiellement sous-spécifiés :
- la chorégraphie UX détaillée des interfaces tuteur et formateur ;
- le script précis de l’orchestrateur formateur ;
- le catalogue canonique détaillé des signaux de qualité conversationnelle ;
- le pouvoir exact de validation du tuteur sur certaines traces terminales ;
- le niveau de frontalisation produit de la posture active, de la progression ou des objets persistants selon les rôles.

En conséquence, le domaine est doctrinalement solide, mais **pas complètement figé dans ses workflows UI détaillés**.

---

## 4. Photo du réel observable

### 4.1 Présence réelle de surfaces tutorales et trainer

Le réel audité montre que Hugo cœur ne se limite pas à une interface apprenant. Des surfaces et endpoints existent bien pour des usages **tuteur / trainer / testeur**, avec notamment :
- des vues de dashboard de groupe et de lecture apprenant ;
- des timelines apprenant ;
- des routes liées aux traces, évaluations, synthèses et partage ;
- des vues trainer autour de la connaissance ou du calibrage ;
- des éléments d’administration liés à TutorPrompt et à certains réglages de conduite.

Le document de glossaire d’alignement confirme par ailleurs que plusieurs objets centraux du domaine existent réellement ou au moins nominalement dans le système : `ConversationProgress`, `UIState`, `LearnerThemeMemory`, `TrainerKnowledgeItem`, `ConversationQualitySignal`, `Trace`, `Evidence`, `LearnerEvaluationRecord`.

### 4.2 Ce que le produit montrable expose réellement

Le réel produit observable montre surtout :
- un front apprenant enrichi dans `frontend1.8` ;
- des surfaces de lecture et de suivi en mode tuteur/testeur ;
- une route `conduct-profiles` et une vue `ConductProfilesView` présentes en mode testeur ;
- des vues admin utilisateurs incomplètes ;
- des branchements réels pour synthèse et évaluation dans l’interface apprenant ;
- une consommation du `sessionUiState` côté front, sans exposition des champs bruts de `TurnState`.

En revanche, le corpus d’audit ne montre pas, à lui seul, une interface formateur/tuteur pleinement stabilisée et homogène au sens cible 2.0. Les surfaces observées apparaissent réelles, mais encore **fragmentées entre prod montrable, mode testeur, admin et capacités de back-office**.

### 4.3 Contrats backend et objets consommables

Le glossaire d’alignement montre un bon raccord entre plusieurs objets doctrinaux 2.0 et des objets réellement observés :
- `UIState` <-> `builduistate`, endpoint `ui-state` ;
- `ConversationProgress` <-> `buildconversationprogress` ;
- mémoire gouvernée résumée <-> endpoint `memory-summary` ;
- synthèse <-> `synthesisservice.py`, endpoint `request-synthesis` ;
- évaluation terminale <-> `evaluationservice.py`, `evaluationworkflowengine.py`, endpoints `request-evaluation`, `finalize-evaluation`, `evaluation-readiness` ;
- qualité conversationnelle <-> `qualitytracker.py`, `ConversationQualitySignal` ;
- savoir formateur gouverné <-> `TrainerKnowledgeItem`.

Ces points indiquent que le domaine **interfaces formateur / tuteur** repose déjà sur un socle backend réel et non sur une projection purement spéculative.

### 4.4 Rôles et visibilité dans le réel cadré

Le cadrage POC v1.5 rappelle une séparation claire des visibilités :
- l’apprenant voit son historique, ses traces et ses preuves ;
- tuteur, trainer et coordo ne voient que ce qui a été partagé selon les règles de produit ;
- l’org admin administre mais ne doit pas lire librement le contenu apprenant non partagé ;
- le superadmin reste borné par l’isolation multi-tenant et l’absence de lecture applicative libre.

Ce cadrage est cohérent avec la doctrine 2.0. En revanche, le corpus mobilisé ici ne prouve pas que **toutes** les variantes runtime ou surfaces actuelles appliquent déjà ce contrat de manière homogène et exhaustive.

### 4.5 Limites observées dans le réel

Le document `05_ECARTS_DOC_CODE_PRODUIT.md` confirme plusieurs limites importantes pour ce domaine :
- les `ConductProfiles` ne sont pas seulement “codés en dur” ; il existe un resolver, une API et une UI dédiée, mais celle-ci reste séparée et visible surtout côté testeur ;
- l’admin comptes est incomplète côté UI et côté API, notamment pour la suppression d’utilisateurs ;
- l’API distante `hugoback.encoors.com` n’est pas assimilable automatiquement au back local audité ;
- plusieurs documents anciens ou intermédiaires sont partiellement obsolètes et ne doivent pas être relus comme vérité produit actuelle.

Autrement dit, le domaine dispose de briques réelles, mais il reste **inégalement stabilisé selon les rôles et les surfaces**.

### 4.7 UIState surface — cluster 4 (`conversation_mode`, `learner_display_profile`)

**Contrat observé :** `GET /hugo/sessions/{id}/ui-state/` enrichi (cluster 4).

| Champ UIState | Valeurs / forme | Rôle tuteur / formateur |
|---------------|-----------------|-------------------------|
| `conversation_mode` | `{code, label, can_switch, switch_warning}` | **Ne voit pas** — endpoint apprenant session |
| `learner_display_profile` | `youth` \| `adult` \| `professional` | **Ne configure pas** (CIBLE DSP-05/06) ; lecture même contrat si un jour exposé |

**Comportement :**
- `conversation_mode` reflète la posture courante (`diagnostic`, `reflective_afest`, `knowledge_review`) — libellé produit, pas de P0.
- `learner_display_profile` est orthogonal à `gamification_profile` (engagement A/B/C).
- Query param `?learner_display_profile=` sur ui-state ; défaut `professional`.

**Preuve :** `test_cluster4_surface_contracts.py`.

**CIBLE restante :** rendu front 3 grammaires (IFT-041), endpoints choix profil par C1/D1, sélecteur posture UI prod.

### 4.6 Parcours tuteur B1 — timeline après patch B1-01 (cluster 3 court)

**Contrat observé :** `GET /dashboard/groups/{group_id}/learners/{learner_id}/timeline/` (`DashboardTimelineView`).

| État partage | Comportement attendu (doctrine) | Réel local post-patch |
|--------------|--------------------------------|------------------------|
| `share_verbatim=false` | Pas de lecture des messages privés | `messages: []` **et** `first_learner_message: ""` |
| `share_verbatim=true` | Verbatim partagé lisible | `messages[]` peuplé ; aperçu 1er message si présent |
| Tous | Pas d’exposition P0 brute aux encadrants | `pilotage` agrégé sur messages apprenant si partagés — pas de `turn_state` / prompts |

**Historique :** avant cluster 3, `first_learner_message` fuyait un extrait du 1er message même si `share_verbatim=false` — **corrigé localement** dans `views_dashboard.py` (2026-06-16).

**Oracle :** B1-01 · **Preuve :** `test_cluster3_oracles.py::test_b1_01_timeline_hides_messages_when_share_verbatim_false` (vert).

**Niveau de vérité :** parcours tuteur timeline **IMPLÉMENTÉ** pour ce garde-fou ; parcours formateur et UI bout-en-bout restent **PARTIEL / A_VERIFIER** prod.

---

## 5. Analyse narrative des écarts

### 5.1 Bon alignement de fond sur la doctrine

L’écart principal n’est pas un écart de philosophie produit. Sur le fond, le réel observé va plutôt dans la bonne direction de la cible 2.0.

Le front ne semble pas piloter directement le moteur. Les objets produits sont déjà orientés `UIState`, progression, synthèse, évaluation, mémoire résumée et objets partageables. Les rôles tuteur/formateur sont pensés comme des rôles de lecture, de validation, de structuration et d’accompagnement, pas comme des rôles ayant un accès libre aux entrailles du runtime.

De ce point de vue, il n’y a pas lieu de relire la spec 2.0 comme une injonction à reconstruire entièrement le domaine.

### 5.2 Écart de stabilisation produit : surfaces réelles mais fragmentées

Le principal écart porte sur la **stabilisation et la cohérence produit** des interfaces formateur/tuteur.

La cible 2.0 décrit des surfaces métier relativement nettes :
- couche tuteur de lecture et accompagnement ;
- couche formateur orientée connaissance gouvernée et validation ;
- visibilité propre des objets de progression, qualité et traces partageables.

Le réel montre bien des briques correspondantes, mais pas encore sous la forme d’un ensemble unique, homogène et clairement borné :
- certaines vues sont surtout en mode testeur ;
- certaines capacités d’admin sont incomplètes ;
- certaines surfaces trainer existent nominalement mais leur workflow détaillé n’est pas encore documenté proprement ;
- les documents intermédiaires ont parfois figé une image inexacte ou partielle du domaine.

L’écart est donc moins “absence totale” que **dispersion et hétérogénéité des surfaces**.

### 5.3 Écart de vocabulaire : doctrine 2.0 vs noms réels observés

Le glossaire d’alignement montre un bon potentiel de raccord, mais plusieurs objets du domaine restent documentés avec un vocabulaire qui ne colle pas encore assez aux noms réellement observés :
- `DecisionContract` vs `ConversationDecision` / `decisionstate` ;
- `ProgressionCalculator` vs `buildconversationprogress` ;
- `UIStateBuilder` vs `builduistate` ;
- `PostureSelector` vs `resolveposture` ;
- `EvaluationTrace` vs `LearnerEvaluationRecord` + objets de trace ;
- mémoire gouvernée inter-session vs mémoire intra-session.

Pour les interfaces formateur/tuteur, ce décalage est important car ces rôles lisent justement des objets traduits, validés et exposables. Une mauvaise clarification de vocabulaire peut faire croire à des objets stabilisés alors qu’ils sont encore composites dans le réel.

### 5.4 Écart spécifique sur la couche tuteur

La cible 2.0 donne à la couche tuteur une mission claire : lire progression, blocages, synthèses, signaux de qualité, objets partageables et préparer l’accompagnement humain.

Le réel montre des dashboards, timelines, accès aux traces partagées, lecture apprenant et fonctions de validation. C’est un socle réel utile. Mais plusieurs points restent ouverts :
- le niveau exact de lecture des signaux de qualité conversationnelle en surface tuteur ;
- la formalisation du rôle de recommandation plutôt que de pilotage ;
- le contrat précis de validation terminale ou de recommandation d’évaluation ;
- l’étendue exacte des vues cohorte réellement stabilisées dans le produit montrable.

La couche tuteur apparaît donc **partiellement alignée**, mais encore insuffisamment contractualisée dans la doc.

### 5.5 Écart spécifique sur la couche formateur

La cible 2.0 attend une vraie couche formateur :
- ingestion documentaire ;
- dialogue d’explicitation ;
- production de `TrainerKnowledgeItem` ;
- rattachement au référentiel ;
- validation humaine.

Le réel confirme la présence de `TrainerKnowledgeItem`, de vues trainer et d’une logique documentaire / référentielle déjà active dans Hugo cœur. Cela va clairement dans le sens de la cible. Mais le corpus mobilisé ici ne prouve pas encore une interface formateur complètement stabilisée comme “orchestrateur formateur” au sens fort de la cible 2.0.

Le risque documentaire est donc double :
- sous-estimer le réel, alors qu’il existe déjà une base trainer significative ;
- ou au contraire sur-affirmer la complétude de l’orchestrateur formateur, alors que le script UX détaillé, les étapes et les statuts complets restent encore à mieux qualifier.

### 5.6 Écart de gouvernance et d’administration

La cible 2.0 prévoit des rôles distincts, des garde-fous de confidentialité et des capacités admin bornées.

Le réel montre une admin utilisateurs partielle, une UI de `ConductProfiles` en mode testeur, une séparation imparfaite entre surfaces métier, admin et testeur, ainsi qu’une divergence possible entre le runtime local audité et l’API distante de démo. Cela signifie que la gouvernance de surface existe, mais qu’elle n’est pas encore complètement **nettoyée, homogénéisée et sécurisée dans la documentation produit**.

### 5.7 Écart critique à ne pas mal lire

Le principal danger sur ce domaine serait de conclure trop vite :
- soit que “tout est déjà là” parce qu’on voit des dashboards, des timelines, des routes et des objets ;
- soit qu’“il faut tout refaire” parce que la cible 2.0 parle d’orchestrateur tuteur et formateur de manière plus propre.

La lecture juste est plus nuancée :
- des responsabilités métier réelles sont déjà couvertes ;
- le backend fournit déjà plusieurs objets structurants ;
- le domaine souffre surtout d’un **écart de formalisation, de vocabulaire, de stabilisation de surfaces et de bornage des rôles**.

---

## 6. Lecture par niveau de vérité

### 6.1 Implémenté / observable

À ce stade, on peut considérer comme **implémenté ou observable** dans Hugo cœur :
- des surfaces dashboard / timeline / lecture apprenant pour usages tuteur ou testeur ;
- des routes et vues liées aux traces, synthèses, évaluations et partage ;
- des objets backend de progression, `UIState`, mémoire résumée, synthèse, évaluation et qualité conversationnelle ;
- la présence réelle de `TrainerKnowledgeItem` ;
- une couche documentaire et référentielle déjà utile à des surfaces trainer ;
- une consommation front d’états dérivés backend plutôt que des états bruts P0.

### 6.2 Cible 2.0

Relèvent de la **cible 2.0** :
- une couche tuteur pleinement formalisée comme lecture de progression, signaux, recommandations et validation bornée ;
- une couche formateur pleinement formalisée comme orchestrateur d’élaboration de savoir gouverné ;
- une distinction parfaitement propre entre objets doctrinaux et noms réels observés ;
- une grammaire UI stabilisée pour progression, posture active, maturité, actions terminales et objets persistants selon les rôles ;
- un contrat produit complet et homogène sur l’ensemble des surfaces tuteur / formateur.

### 6.3 Écarts confirmés

Les **écarts confirmés** sur ce domaine sont principalement :
- fragmentation des surfaces entre prod montrable, testeur, trainer et admin ;
- documentation partiellement obsolète ou imprécise sur certaines capacités réelles ;
- vocabulaire encore insuffisamment aligné entre doctrine 2.0 et objets réels observés ;
- UI admin et certaines actions d’administration incomplètes ;
- rôle exact de certaines validations ou recommandations encore insuffisamment borné dans la doc.

### 6.4 À vérifier

Restent explicitement `A_VERIFIER` :
- l’équivalence entre le runtime local audité et `hugoback.encoors.com` sur les surfaces tuteur / formateur ;
- l’activation réelle en prod distante de certaines routes, vues ou contrats observés localement ;
- les flags pouvant modifier la posture, les profils de conduite ou certaines actions terminales ;
- le niveau exact de complétude de l’orchestrateur formateur en runtime courant ;
- la portée réelle des vues cohorte et signaux qualité dans les variantes non auditées ici.

---

## 7. Garde-fous pour la suite documentaire

### 7.1 Ce qu’il ne faut pas faire

Pour ce domaine, il faut éviter :
1. de décrire les interfaces formateur/tuteur comme un cockpit de pilotage libre du moteur ;
2. de relire toute vue testeur ou admin comme une surface produit stabilisée ;
3. de déduire la prod distante à partir du seul code local ou inversement ;
4. de prendre le glossaire comme preuve que tous les objets 2.0 sont déjà pleinement implémentés ;
5. de confondre surfaces trainer liées à la connaissance gouvernée et administration générale ;
6. de présenter l’accès aux contenus apprenant comme libre alors que la doctrine impose partage explicite et confidentialité-first.

### 7.2 Ce qu’il faut privilégier

La trajectoire saine pour ce domaine est :
- clarifier les **contrats d’interface** par rôle ;
- aligner le **vocabulaire** entre doctrine 2.0 et noms réels observés ;
- distinguer proprement ce qui relève de la **lecture tutorale**, de la **structuration formateur**, de la **validation humaine** et de l’**administration** ;
- documenter séparément ce qui est **prod montrable**, **mode testeur**, **surface trainer**, et **A_VERIFIER en runtime distant** ;
- préférer des compléments backend et documentaires additifs à une refonte front arbitraire.

---

## 8. Conclusion opérationnelle du domaine

Le domaine `110_interfaces_formateur_tuteur` n’est ni vide, ni déjà complètement stabilisé au sens Hugo 2.0.

Le réel audité montre un socle substantiel : dashboards, timelines, partage, synthèse, évaluation, objets de progression, mémoire résumée, qualité conversationnelle, et présence d’une base trainer avec `TrainerKnowledgeItem`. La cible 2.0 n’appelle donc pas une réinvention du domaine, mais un **travail de raccord propre** entre doctrine, surfaces observées et vocabulaire réel.

L’écart principal porte sur :
- la clarification des rôles et contrats de surface ;
- la réduction de la fragmentation entre prod, testeur, admin et trainer ;
- l’alignement de vocabulaire entre objets 2.0 et objets réellement observés ;
- le bornage explicite des zones encore `A_VERIFIER`.

La bonne lecture de ce domaine est donc :
- **socle réel déjà présent** ;
- **alignement doctrinal globalement bon** ;
- **écarts surtout documentaires, de stabilisation produit et de vocabulaire** ;
- **pas de preuve suffisante, à ce stade, d’une couche formateur/tuteur entièrement homogène et définitivement stabilisée sur tous les runtimes**.


# 01_matrice_ecarts — 110_interfaces_formateur_tuteur

## Domaine

- `DOMAINE_CODE = 110_interfaces_formateur_tuteur`
- `DOMAINE_LABEL = interfaces formateur / tuteur`

---

## 1. Règles de lecture

Cette matrice croise :
- la **cible 2.0** issue de la spec canonique et des specs de domaine ;
- le **réel observable** issu des audits Hugo réel ;
- le **glossaire d’alignement**, utilisé uniquement comme pont de vocabulaire.

### Statuts utilisés

- `ALIGNE`
- `ALIGNE_DOC_PARTIEL`
- `RENOMMER_DANS_DOC`
- `AMBIGU`
- `A_VERIFIER`
- `ABSENT / NOUVEAU_CONTRAT`

### Règles d’interprétation

- `ALIGNE` signifie que la responsabilité cible et le réel observable convergent clairement.
- `ALIGNE_DOC_PARTIEL` signifie que le fond est présent, mais que la documentation doit mieux expliciter le raccord.
- `RENOMMER_DANS_DOC` signifie que le réel existe, mais que la doc 2.0 doit faire apparaître le nom réellement observé.
- `AMBIGU` signifie qu’un rapprochement plausible existe, sans preuve suffisante pour figer un mapping propre.
- `A_VERIFIER` signifie que le corpus mobilisé ici ne suffit pas à conclure, notamment en cas de dépendance au runtime distant ou à des variantes non auditées.
- `ABSENT / NOUVEAU_CONTRAT` signifie que le réel mobilisé ici ne permet pas de montrer une capacité ou un contrat déjà installé comme tel.

---

## 2. Matrice des écarts

| ID | Sous-domaine | Cible 2.0 | Réel observable / noms réels | Statut | Lecture de l’écart | Action documentaire recommandée |
|---|---|---|---|---|---|---|
| IFT-001 | Doctrine générale | Les interfaces tuteur / formateur sont des surfaces métier gouvernées, non des cockpits de pilotage libre du moteur | Le corpus réel montre des vues de lecture, dashboard, timeline, partage, validation et surfaces trainer, sans preuve d’un pilotage libre du P0 | ALIGNE | Bon alignement de fond avec la doctrine backend-first | Conserver la doctrine telle quelle |
| IFT-002 | Couche tuteur | Le tuteur lit progression, blocages, synthèses, traces partageables et prépare l’accompagnement humain | Le cadrage POC et les audits mentionnent dashboard groupe, timeline apprenant, lecture de traces, validations et exports | ALIGNE_DOC_PARTIEL | La responsabilité métier existe, mais la documentation du réel reste éparse | Mieux documenter la couche tuteur observée |
| IFT-003 | Couche formateur | Le formateur gère documents, explicitation, savoir métier gouverné, validation humaine | Présence de `TrainerKnowledgeItem`, vues trainer, bibliothèque documentaire et surfaces associées | ALIGNE_DOC_PARTIEL | Base réelle claire, mais l’orchestrateur formateur complet n’est pas encore décrit proprement dans le réel | Clarifier formateur réel vs orchestrateur formateur cible |
| IFT-004 | Confidentialité par rôle | Tuteur / formateur ne voient pas le verbatim non partagé ; partage explicite requis | Le cadrage POC pose cette règle explicitement ; la doctrine 2.0 aussi ; les audits ne la contredisent pas | ALIGNE | Invariant fort et cohérent entre cible et réel cadré | Garder comme invariant ferme |
| IFT-005 | UIState côté surfaces non apprenant | Les surfaces consomment des états dérivés backend, pas les champs P0 bruts | Le glossaire raccorde `UIState` avec `builduistate` et l’endpoint `ui-state` ; l’audit front confirme absence d’exposition de `TurnState` brut en prod | ALIGNE | Très bon point d’ancrage pour les surfaces tutorales | Garder UIState comme pivot de lecture produit |
| IFT-006 | Progression conversationnelle | La couche tuteur consomme `ConversationProgress` ou sa traduction produit | Le glossaire raccorde `ConversationProgress` à `buildconversationprogress`, mais l’exposition produit passe surtout via `ui-state` | ALIGNE_DOC_PARTIEL | La progression existe bien, mais son contrat produit côté tuteur reste indirect | Documenter plus explicitement le lien progression -> UI tutorale |
| IFT-007 | Endpoint de progression dédié | La cible 2.0 évoque un `GET .../progress` pour lecture tuteur | Le glossaire signale qu’aucune route `progress` clairement auditée n’est prouvée ; le réel passe surtout par `ui-state` et services backend | AMBIGU | Le besoin conceptuel est clair, mais le contrat réel observable n’est pas stabilisé | Ne pas documenter un endpoint `progress` comme acquis du réel |
| IFT-008 | Mémoire gouvernée résumée | Les surfaces autorisées peuvent lire une mémoire résumée gouvernée | Le glossaire aligne l’endpoint `memory-summary` avec la cible 2.0 | ALIGNE | Bon point de raccord entre doctrine et réel observable | Garder comme capacité réelle du domaine |
| IFT-009 | Verbatim non partagé | Le verbatim non partagé reste caché aux rôles tuteur / formateur | Timeline tuteur : `messages[]` + `first_learner_message` vides si `share_verbatim=false` ; oracle B1-01 vert (cluster 3). | `DashboardTimelineView`, `test_cluster3_oracles.py` | ALIGNE | Garde-fou corrigé et testé en local ; ancienne fuite `first_learner_message` documentée comme corrigée. | Conserver B1-01 comme référence ; ne pas sur-généraliser aux autres surfaces tuteur. |
| IFT-010 | Synthèse partageable | Les surfaces tuteur peuvent lire ou déclencher une synthèse selon éligibilité et règles de partage | Le glossaire raccorde `request-synthesis` ; l’audit front confirme le branchement local côté apprenant | ALIGNE_DOC_PARTIEL | La capacité existe, mais les rôles exacts et la surface tuteur précise restent à mieux écrire | Clarifier qui lit, qui déclenche, sous quelles conditions |
| IFT-011 | Évaluation terminale | La couche tuteur peut recommander ou lire une évaluation terminale partageable, avec validation humaine finale | Le glossaire raccorde `request-evaluation`, `finalize-evaluation`, `evaluation-readiness`, mais signale un mapping partiel | ALIGNE_DOC_PARTIEL | Le workflow existe, mais le vocabulaire et la place produit restent imparfaitement stabilisés | Mieux distinguer branche terminale cible et workflow réel |
| IFT-012 | EvaluationTrace | La cible 2.0 parle d’`EvaluationTrace` | Le réel observé semble réparti entre `LearnerEvaluationRecord`, objets de trace et validation | AMBIGU | Zone de friction majeure de vocabulaire | Stabiliser le mapping documentaire |
| IFT-013 | TrainerKnowledgeItem | Objet central de savoir formateur gouverné | Le glossaire indique un excellent alignement avec `TrainerKnowledgeItem` réel | ALIGNE | Très bon point d’appui pour la couche formateur | Conserver le nom doctrinal et citer le nom réel |
| IFT-014 | Signaux de qualité conversationnelle | La couche tuteur lit des signaux de qualité sans scoring opaque | Le glossaire aligne `ConversationQualitySignal` et `qualitytracker.py`; la cible 2.0 fixe la fonction, pas encore le catalogue complet | ALIGNE_DOC_PARTIEL | Bon alignement de fond, mais catalogue et exposition UI restent partiellement ouverts | Documenter les signaux observés sans sur-spécifier le catalogue cible |
| IFT-015 | Vues cohorte | La cible 2.0 prévoit des vues cohorte tutorales / trainer | Le cadrage POC mentionne dashboard groupe et `GET dashboard/groups/.../competences`, `.../learners`, `.../timeline` | ALIGNE_DOC_PARTIEL | Les vues existent dans le cadrage et les parcours, mais leur niveau de stabilisation produit complet reste à préciser | Distinguer vues cohortes POC / surfaces réellement montrables |
| IFT-016 | Dashboard apprenant pour tuteur | Lecture tutorale d’un apprenant via dashboard / timeline | Le cadrage POC et les parcours d’usage décrivent explicitement ce cas | ALIGNE | Responsabilité métier déjà bien couverte | Garder comme surface réelle de référence |
| IFT-017 | Timeline apprenant | Le tuteur / formateur peut consulter une timeline de progression | `GET dashboard/.../timeline/` ; cohérence `messages[]` / `first_learner_message` sous `share_verbatim` ; preuve B1-01 | ALIGNE_DOC_PARTIEL | Contrat timeline tuteur partiellement prouvé en local ; stabilisation prod A_VERIFIER | Documenter comportement post-patch comme référence |
| IFT-018 | Commentaire / accompagnement humain | Le tuteur peut lire, commenter, recommander et préparer l’accompagnement | Le cadrage POC décrit le rôle, mais le corpus mobilisé ici ne prouve pas un workflow produit détaillé de commentaire | ABSENT / NOUVEAU_CONTRAT | La responsabilité est doctrinalement claire, mais l’UI ou le contrat réel détaillé n’est pas démontré ici | Ouvrir un contrat documentaire séparé si nécessaire |
| IFT-019 | Validation de certaines traces partageables | Le tuteur peut valider certaines traces partageables dans la réalité de travail | Le cadrage POC cite `POST traces/{traceid}/validate` ; la cible 2.0 laisse le périmètre exact encore ouvert | ALIGNE_DOC_PARTIEL | La validation existe, mais son périmètre exact par rôle n’est pas totalement borné | Clarifier validation trace vs validation terminale vs certification |
| IFT-020 | Validation humaine formateur | Le formateur peut valider des connaissances ou objets gouvernés | La cible 2.0 l’exige ; le réel montre `TrainerKnowledgeItem` et surfaces trainer, mais sans script UX complet audité ici | ALIGNE_DOC_PARTIEL | Bon alignement, mais contrat de validation à préciser | Documenter les statuts et actions réellement observés |
| IFT-021 | Statuts de connaissance | Déclaré / dérivé provisoire / validé humainement | La cible 2.0 les fixe, mais le réel observable mobilisé ici ne permet pas de confirmer la totalité de ce contrat en surface | A_VERIFIER | Ne pas affirmer trop vite que tous les statuts sont déjà produits tels quels | Marquer explicitement comme cible partiellement à vérifier |
| IFT-022 | Orchestrateur formateur dialogique | L’interface formateur n’est pas un simple formulaire d’admin, mais un dialogue d’élaboration gouverné | Le réel montre une base trainer et des surfaces associées ; le script détaillé d’orchestrateur n’est pas prouvé ici | ABSENT / NOUVEAU_CONTRAT | La cible est structurante, mais le contrat UI/runtime détaillé n’est pas encore démontré dans le réel mobilisé | Documenter comme capacité cible à formaliser |
| IFT-023 | TutorPrompt back-office | Le back-office de gestion des prompts existe pour rôles habilités | Le cadrage POC décrit un catalogue CRUD `hugotutor-prompts` pour ORGADMIN / SUPERADMIN | ALIGNE_DOC_PARTIEL | Bon cadrage historique, mais à distinguer de la couche tuteur/formateur métier | Séparer clairement admin de prompt et interface métier tuteur / formateur |
| IFT-024 | Conduct profiles | Réglages de conduite visibles / administrables selon droits | L’audit montre `ConductProfilesView`, route dédiée, resolver API, mais surtout en mode testeur et pas comme surface prod stabilisée | ALIGNE_DOC_PARTIEL | La capacité existe, mais sa place produit est encore intermédiaire | Documenter comme surface réelle partielle, non comme UI métier finale |
| IFT-025 | Conduct profiles “codés en dur seulement” | Ancienne lecture documentaire erronée | L’audit confirme qu’il existe modèle / resolver / API / UI, donc la lecture “codé en dur seulement” est obsolète | RENOMMER_DANS_DOC | Le problème est surtout documentaire | Corriger explicitement les docs qui sous-décrivent cette capacité |
| IFT-026 | Sélection de posture côté interface apprenant | POST set-posture + `PostureSelector.vue` + transitions | cluster 15/16, Playwright U16-S1 | **PARTIEL+** local | S16-A2 manuel ; Encoors A_VÉRIFIER | Ne pas confondre avec pilotage tuteur/formateur |
| IFT-027 | Posture active visible | La cible 2.0 autorise une visibilité minimale de la posture active si le produit l’assume | Le réel mobilisé ici ne prouve pas une exposition formateur/tuteur homogène de cette donnée | A_VERIFIER | Sujet plausible, mais non suffisamment démontré | Garder comme option cible, pas comme état livré |
| IFT-028 | Objets persistants visibles | La cible 2.0 évoque des `PersistentObjects` visibles ou confirmables | Le glossaire considère ce concept comme encore ambigu, sans backing model net dans le réel | AMBIGU | Concept utile côté doctrine, mais trop tôt pour le traiter comme objet réel unifié | Ne pas inventer de backing model dans la doc |
| IFT-029 | Admin comptes | Le produit distingue rôles et admin minimale bornée | L’audit signale création / édition user mais absence de suppression côté UI et absence apparente de destroy côté API | ALIGNE_DOC_PARTIEL | L’admin existe mais reste incomplète | Documenter honnêtement l’incomplétude du réel |
| IFT-030 | Séparation admin / métier | La cible distingue administration, tutorat, formation et coordination | Le réel montre des surfaces mêlées entre testeur, admin et métier, avec stabilisation partielle | AMBIGU | Le principe est bon, mais le découpage produit réel reste imparfait | Clarifier les frontières de surface dans les docs |
| IFT-031 | Lecture du contenu apprenant par org admin | L’org admin n’a pas de lecture libre du non-partagé | Cible 2.0 et cadrage POC convergent ; pas de contradiction probante dans le réel mobilisé | ALIGNE | Invariant structurant à conserver | Garder sans dilution |
| IFT-032 | Runtime local vs runtime distant | Les surfaces observées localement valent-elles pour Encoors ? | L’audit `05_ECARTS_DOC_CODE_PRODUIT.md` dit explicitement que non, et maintient ce point ouvert | A_VERIFIER | Ne pas sur-affirmer la prod distante | Marquer toutes les dépendances runtime comme `A_VERIFIER` |
| IFT-033 | Lecture mémoire inter-session injectée dans le tour | La mémoire gouvernée peut nourrir les surfaces et le moteur | Le glossaire note `LearnerThemeMemory` aligné, mais l’audit confirme l’absence d’injection dans l’orchestrateur local | ALIGNE_DOC_PARTIEL | L’objet existe, mais son usage runtime complet n’est pas atteint | Documenter l’écart entre présence objet et injection moteur |
| IFT-034 | Lecture de traces partageables | Le tuteur lit des traces partageables et non le brut librement | Le cadrage POC et les endpoints historiques le confirment | ALIGNE | Responsabilité stable et cohérente | Conserver comme base de la couche tuteur |
| IFT-035 | Lecture de preuves partageables | Le formateur / tuteur peut consulter des preuves selon partage | Le cadrage POC et la doctrine confidentialité-first le permettent ; le domaine preuve existe réellement | ALIGNE_DOC_PARTIEL | Cohérent, mais l’UI métier détaillée n’est pas entièrement explicitée ici | Mieux lier preuves, partage et rôles dans la doc |
| IFT-036 | Vue trainer de connaissance gouvernée | Le formateur dispose d’actions de gestion d’items de connaissance | La cible 2.0 le fixe, la présence de `TrainerKnowledgeItem` le soutient, mais la preuve UI fine reste partielle | ALIGNE_DOC_PARTIEL | Réel partiel mais crédible | Documenter comme surface en place partiellement observée |
| IFT-037 | Workflow complet trainer de validation | Création, dérivation, correction, validation, rattachement référentiel, export | Le réel mobilisé ici ne démontre pas toute la chaîne de bout en bout | ABSENT / NOUVEAU_CONTRAT | Ne pas sur-vendre la complétude du workflow | Ouvrir un contrat cible/réel dédié |
| IFT-038 | Surface coordinateur | La cible 2.0 admet un rôle coordinateur, mais reste partiellement ouverte sur ses écrans | Le cadrage POC le cite ; le réel produit détaillé n’est pas démontré ici | A_VERIFIER | Ne pas construire une doctrine UI détaillée sans preuve | Marquer explicitement comme zone ouverte |
| IFT-039 | Surface superadmin technique | Supervision technique globale sous contrainte de non-lecture applicative libre | Doctrine 2.0 et cadrage POC convergent ; peu de preuve UI détaillée utile dans le réel | ALIGNE_DOC_PARTIEL | Principe clair, UI non centrale ici | Documenter sobrement, sans sur-spécifier |
| IFT-040 | Front tutor / trainer desktop-first | Le POC pose une expérience desktop-first pour TUTOR / TRAINER / COORDO / ORGADMIN | Le cadrage POC l’énonce explicitement | ALIGNE_DOC_PARTIEL | Bon cadrage, mais à ne pas confondre avec preuve d’ergonomie finale livrée | Garder comme cadrage de référence, pas comme preuve UX finale |

| IFT-041 Profils d’affichage apprenant par public | Enum `learner_display_profile` + CSS 3 grammaires | youth/adult/professional | **PARTIEL+** contrat + rendu + E2E | cluster4 + C16 U16-P | IFT-042 ouvert | `test_cluster16_interface_apprenant_backend.py` |

IFT-042 Choix de profil d’affichage par rôle non apprenant La cible 2.0 prévoit que certains rôles (formateur, ORGADMIN, superadmin technique) puissent, dans des bornes définies, choisir quel profil d’affichage voit l’apprenant, sans piloter la logique moteur ni P0. Le rel audit ne prouve pas de surface stabilisée permettant ce choix de profil ; les surfaces admin actuelles restent partielles et mélangées avec le mode testeur. ABSENT NOUVEAUCONTRAT La responsabilité de configuration existe conceptuellement, mais le contrat produit et les permissions fines par rôle ne sont pas encore posés proprement. Créer un sous-contrat d’interface par rôle pour le choix de profil d’affichage, en le bornant clairement comme configuration d’UX et non comme pilotage du moteur.

---

## 3. Points les plus structurants

### Alignements forts

- `UIState` comme pivot de traduction produit.
- `ConversationProgress` comme socle de lecture d’avancement.
- `TrainerKnowledgeItem` comme objet central de la couche formateur.
- confidentialité-first et partage explicite.
- lecture tutorale via traces, synthèses, timeline et vues de cohorte.
- présence d’un socle dashboard / timeline / validation déjà compatible avec la doctrine.

### Frictions principales

- `EvaluationTrace` vs `LearnerEvaluationRecord` / `Trace`.
- couche tuteur réelle présente mais encore insuffisamment contractualisée.
- couche formateur réelle présente mais pas encore prouvée comme orchestrateur dialogique complet.
- mélange partiel entre surfaces métier, admin et testeur.
- endpoint de progression dédié non prouvé dans le réel.
- visibilité et contrôle de posture encore trop ouverts ou non démontrés.

### Zones à ne pas sur-affirmer

- runtime distant Encoors ;
- exposition réelle d’un endpoint `progress` ;
- interface complète coordinateur ;
- script détaillé d’orchestrateur formateur ;
- pouvoir exact de validation terminale du tuteur ;
- homogénéité finale de toutes les surfaces tuteur / formateur sur tous les runtimes.

---

## 4. Lecture opérationnelle

La matrice montre un domaine :
- **globalement aligné sur la doctrine 2.0 dans ses principes** ;
- **déjà partiellement couvert dans le réel** par des objets, vues et endpoints utiles ;
- **encore en écart surtout sur la formalisation des contrats, le vocabulaire et la stabilisation des surfaces** ;
- **sans justification, à ce stade, pour une refonte globale**, mais avec un besoin fort de clarification documentaire et de bornage des zones `A_VERIFIER`.

# 02_decisions_documentaires — 110_interfaces_formateur_tuteur

## Domaine

- `DOMAINE_CODE = 110_interfaces_formateur_tuteur`
- `DOMAINE_LABEL = interfaces formateur / tuteur`

---

## 1. Objet du document

Ce document fixe les **décisions documentaires** à appliquer pour le domaine **interfaces formateur / tuteur** de Hugo cœur, à partir de la cible 2.0, des audits du réel et du glossaire d’alignement.

Il ne décide pas, à lui seul :
- d’une refonte produit ;
- d’un changement de runtime ;
- d’un redesign UX complet ;
- d’une modification de périmètre Hugo cœur.

Son rôle est de stabiliser la manière correcte de **nommer**, **décrire**, **borner** et **prioriser** ce domaine dans la documentation de travail.

---

## 2. Principes de rédaction retenus

### 2.1 Doctrine conservée

La documentation de ce domaine reste écrite dans le cadre doctrinal Hugo 2.0 :
- moteur tutoriel multi-postures piloté par état ;
- backend Django orchestré ;
- TutorPrompt pivot runtime ;
- P0 conservé et enrichi additivement ;
- front drivé par états ;
- mémoire gouvernée ;
- confidentialité-first ;
- partage explicite ;
- multi-tenant strict.

Aucune décision documentaire de ce domaine ne doit réintroduire :
- une lecture front-driven ;
- une logique “prompt seul” ;
- une console de pilotage libre du moteur côté tuteur ou formateur ;
- une exposition libre du verbatim non partagé.

### 2.2 Réel vs cible

Dans tous les documents futurs de ce domaine :
- la **spec 2.0** continue de décrire une **cible** ;
- les **audits 00–10** continuent de décrire le **réel observable** ;
- le **glossaire** reste un **pont de vocabulaire**, jamais une preuve d’implémentation.

Les formulations doivent donc distinguer explicitement :
- “cible 2.0” ;
- “réel observé dans le workspace audité” ;
- “point restant à vérifier” ;
- “contrat encore à formaliser”.

---

## 3. Décisions de vocabulaire

### DD-01 — Conserver les noms doctrinaux structurants

Les noms doctrinaux suivants sont conservés comme vocabulaire principal du domaine :
- `UIState`
- `ConversationProgress`
- `TrainerKnowledgeItem`
- `ConversationQualitySignal`
- `LearnerThemeMemory`
- `orchestrateur tuteur`
- `orchestrateur formateur`

Ces noms structurent bien la cible 2.0 et doivent rester la grammaire de référence pour raisonner juste sur le domaine.

### DD-02 — Ajouter systématiquement les noms réels observés quand ils sont connus

Quand un nom doctrinal renvoie à un service, endpoint ou objet réellement observé, la documentation doit faire apparaître juste après le **nom réel observé**.

Exemples à appliquer :
- `ConversationProgress` -> `buildconversationprogress`
- `UIState` -> `builduistate`, endpoint `ui-state`
- `SynthesisService` -> `synthesisservice.py`, endpoint `request-synthesis`
- `workflow d’évaluation` -> `evaluationservice.py`, `evaluationworkflowengine.py`, endpoints `request-evaluation`, `finalize-evaluation`, `evaluation-readiness`
- `qualité conversationnelle` -> `qualitytracker.py`, `ConversationQualitySignal`

La règle est : **nom canonique pour raisonner**, **nom réel pour parler juste du développé**.

### DD-03 — Ne pas renommer brutalement la doctrine d’après les noms Python

La documentation ne doit pas être réécrite comme si les noms de fonctions ou de fichiers réels devenaient la doctrine officielle.

Exemples :
- on ne remplace pas `orchestrateur tuteur` par `views + dashboard + timeline` ;
- on ne remplace pas `UIStateBuilder` par `builduistate` comme nom canonique ;
- on ne remplace pas `ProgressionCalculator` par `buildconversationprogress` comme seul vocabulaire.

Les noms réels doivent être **ajoutés**, pas **substitués** au cadre doctrinal.

### DD-04 — Stabiliser le terme `EvaluationTrace` comme nom cible, sans le présenter comme mapping déjà figé

Le terme `EvaluationTrace` est conservé dans la documentation cible, car il structure correctement la branche terminale d’évaluation.

En revanche, les documents doivent désormais préciser explicitement que, dans le réel observé, le mapping passe aujourd’hui de manière encore partielle par :
- `LearnerEvaluationRecord`
- les objets de `Trace`
- les endpoints de workflow d’évaluation

Tant que cette harmonisation n’est pas faite, la doc doit employer une formule prudente du type :
> “`EvaluationTrace` est le nom doctrinal cible ; dans le réel observé, la matérialisation passe aujourd’hui par un ensemble encore partiellement dispersé entre `LearnerEvaluationRecord`, objets de trace et workflow d’évaluation.”

### DD-05 — Conserver `TrainerKnowledgeItem` comme zone d’alignement forte

`TrainerKnowledgeItem` est retenu comme point d’alignement fort entre cible et réel.

La documentation future doit :
- le garder comme objet pivot de la couche formateur ;
- rappeler qu’il appartient à une base de connaissances gouvernée ;
- éviter de sur-affirmer la complétude du workflow formateur de bout en bout ;
- distinguer clairement la présence réelle de l’objet et la complétude encore ouverte de l’orchestrateur formateur.

### DD-06 — Maintenir `PersistentObjects` comme concept produit, pas comme backing model prouvé

Le terme `PersistentObjects` peut rester dans la documentation 2.0 comme concept produit utile.

Mais il doit être explicitement marqué comme :
- **concept produit cible**
- **sans backing model unique prouvé dans le réel observé**

La documentation ne doit donc pas inventer un modèle réel unique derrière ce terme tant qu’il n’est pas audité comme tel.

---

## 4. Décisions de périmètre par rôle

### DD-07 — Décrire la couche tuteur comme couche de lecture, recommandation et validation bornée

La documentation du domaine doit désormais décrire explicitement la couche tuteur comme une couche de :
- lecture de progression ;
- lecture de signaux de blocage et de qualité conversationnelle ;
- lecture de traces, synthèses et évaluations partageables ;
- préparation d’accompagnement humain ;
- validation bornée de certaines traces partageables.

Elle ne doit pas la décrire comme :
- une couche de pilotage libre du moteur ;
- une interface de contrôle direct du P0 ;
- une surface de forçage libre des orchestrateurs apprenant ;
- une interface d’accès au verbatim non partagé.

### DD-08 — Décrire la couche formateur comme couche de savoir gouverné, pas comme simple admin documentaire

La documentation du domaine doit désormais décrire la couche formateur comme une couche orientée :
- ingestion documentaire ;
- explicitation métier ;
- production ou correction de `TrainerKnowledgeItem` ;
- rattachement au référentiel ;
- validation humaine.

Elle ne doit plus être résumée comme :
- simple “back-office documents” ;
- simple “admin trainer” ;
- simple “upload de docs”.

Le terme **orchestrateur formateur** peut être conservé, mais la doc doit signaler que son script UX détaillé reste encore partiellement ouvert.

### DD-09 — Séparer explicitement tuteur, formateur, coordinateur et admin d’organisation

Les prochains documents doivent distinguer plus clairement :
- **tuteur** : lecture / accompagnement / validation bornée ;
- **formateur** : savoir métier gouverné / structuration / validation ;
- **coordinateur** : rôle métier encore partiellement ouvert ;
- **org admin** : administration bornée / users / groupes / exports, sans accès libre au non-partagé.

Le mélange actuel entre surfaces métier, surfaces testeur et admin doit être documenté comme un **état partiellement fragmenté du réel**, pas comme une architecture cible.

---

## 5. Décisions sur les surfaces et contrats produit

### DD-10 — `UIState` devient le point d’entrée documentaire principal pour les surfaces tuteur / formateur

Pour ce domaine, `UIState` est retenu comme le point d’entrée documentaire principal pour décrire la consommation front des états backend.

Concrètement :
- les docs doivent partir de `UIState` pour décrire ce qui est lisible côté surface ;
- elles doivent rappeler que `TurnState` et les variables P0 brutes restent cachés ;
- elles doivent lier `UIState` à `ConversationProgress`, synthèse, évaluation, mémoire résumée et objets partageables.

### DD-11 — Le contrat `progress` reste une cible ou un contrat à confirmer, pas une route réelle à affirmer

La documentation ne doit plus présenter un endpoint de type `GET .../progress` comme **acquis dans le réel**.

Règle retenue :
- si l’on parle de la **cible 2.0**, on peut le mentionner comme contrat souhaité ou cible ;
- si l’on parle du **réel observable**, on doit préciser que l’exposition passe aujourd’hui surtout par `ui-state` et les services backend observés.

### DD-12 — Les surfaces dashboard / timeline doivent être décrites comme capacités réelles partielles

Les dashboards, timelines et vues cohorte peuvent être documentés comme des **capacités réelles observées ou cadrées**, mais pas comme un produit parfaitement homogène et stabilisé sur tous les runtimes.

La documentation doit employer une formulation du type :
- “surface réelle partielle”
- “capacité cadrée dans le POC et cohérente avec le réel”
- “niveau exact de stabilisation à confirmer selon runtime et surface”

### DD-13 — Les `ConductProfiles` doivent être documentés comme capacité réelle partielle, non comme mythe ni comme UI métier finale

Les documents futurs doivent cesser d’affirmer que les `ConductProfiles` sont “codés en dur seulement”.

Décision retenue :
- documenter l’existence réelle d’un resolver, d’une API et d’une UI dédiée ;
- préciser que cette UI est surtout visible côté testeur / surface séparée ;
- ne pas la décrire comme interface métier finale formateur / tuteur tant que ce n’est pas stabilisé.

### DD-14 — L’admin comptes doit être décrite comme incomplète

La documentation doit désormais marquer explicitement l’administration comptes comme **partielle** :
- création / édition observées ;
- suppression non confirmée comme pleinement disponible ;
- frontière admin / métier encore incomplètement stabilisée.

Cette incomplétude doit apparaître comme un fait documentaire, non comme une anomalie cachée.

---

## 6. Décisions sur confidentialité et partage

### DD-15 — Le partage explicite devient la règle de formulation de toutes les surfaces non apprenant

Dans tous les documents de ce domaine, la visibilité des rôles non apprenant doit être formulée selon cette règle :

> “Le rôle non apprenant ne voit que les objets explicitement partagés ou rendus visibles par un contrat produit gouverné.”

Cette règle doit être appliquée à :
- synthèses ;
- preuves ;
- verbatim ;
- traces terminales ;
- objets de mémoire exposables.

### DD-16 — Le verbatim non partagé est toujours formulé comme caché, même pour tuteur / formateur / admin

La documentation doit interdire toute formulation ambiguë du type :
- “le tuteur accède à la conversation complète” ;
- “le formateur peut consulter l’historique brut” ;
- “l’admin voit le contenu apprenant”.

La formulation correcte devient :
- “le verbatim non partagé reste privé par défaut” ;
- “les rôles non apprenant n’accèdent qu’au partage explicite et aux projections gouvernées”.

### DD-17 — La documentation doit séparer partage métier et journaux techniques sandbox

Le cadrage POC autorise des journaux techniques en sandbox/dev, mais ces journaux ne doivent jamais être confondus avec les surfaces métier tuteur / formateur.

Décision documentaire :
- les journaux techniques, prompts rendus et réponses brutes restent hors périmètre des interfaces métier ;
- leur existence éventuelle en dev ne doit pas polluer la documentation de surface tuteur / formateur.

---

## 7. Décisions sur les zones ouvertes

### DD-18 — Le rôle exact du tuteur dans la validation terminale reste ouvert et doit être marqué comme tel

La documentation ne doit pas trancher prématurément :
- si le tuteur valide seulement certaines traces ;
- s’il recommande l’évaluation ;
- s’il participe à la validation terminale ;
- ou s’il ne fait qu’en lire le résultat.

La formulation retenue est :
> “Le rôle exact du tuteur dans la validation terminale reste à préciser ; le corpus fixe clairement la lecture, la recommandation et la validation bornée de certaines traces partageables.”

### DD-19 — Le script détaillé de l’orchestrateur formateur reste explicitement sous-spécifié

La documentation doit conserver le principe fort :
- l’orchestrateur formateur n’est pas un simple formulaire d’admin.

Mais elle doit signaler en même temps que restent ouverts :
- l’ordre exact des sections ;
- les relances ;
- les reprises ;
- la chorégraphie UX détaillée ;
- la grammaire précise des écrans.

### DD-20 — La surface coordinateur reste hors stabilisation fine dans ce domaine

Le coordinateur peut être mentionné comme rôle du système, mais aucune doc détaillée de ses écrans ou workflows ne doit être produite dans ce domaine sans corpus supplémentaire.

Décision :
- le coordinateur reste documenté comme **rôle admis mais partiellement ouvert** ;
- aucun faux niveau de détail ne doit être introduit.

### DD-21 — Toute dépendance au runtime distant Encoors reste `A_VERIFIER`

Pour ce domaine, toute formulation concernant :
- disponibilité exacte des endpoints en prod distante ;
- activation réelle de certaines vues ;
- flags runtime ;
- cohérence exacte avec le local audité

doit être marquée `A_VERIFIER`.

La documentation de domaine ne doit jamais faire comme si la démo distante prouvait automatiquement le runtime local, ni l’inverse.

---

## 8. Décisions d’écriture à appliquer dans les prochains documents

### DD-22 — Formulation standard cible / réel / à vérifier

Les futurs documents de ce domaine doivent reprendre cette discipline rédactionnelle :

- **Cible 2.0** : “La cible prévoit…”
- **Réel observé** : “Le réel audité montre…”
- **Pont de vocabulaire** : “Le glossaire rapproche…”
- **Zone ouverte** : “Le corpus ne permet pas encore de conclure…”
- **Runtime distant** : “A_VERIFIER”

### DD-23 — Bannir certaines formulations trompeuses

Les formulations suivantes sont interdites dans la doc de domaine :
- “déjà livré” sur la seule base d’une spec ;
- “implémenté” sur la seule base du glossaire ;
- “surface finale” sur la seule base d’une vue testeur ;
- “prod” sur la seule base de `.env` ou d’une démo distante ;
- “orchestrateur complet” sans preuve de workflow de bout en bout.

### DD-24 — Assumer les écarts documentaires comme premier chantier

La priorité documentaire de ce domaine n’est pas d’inventer de nouveaux objets, mais de :
- recaler les noms ;
- clarifier les surfaces ;
- distinguer les rôles ;
- expliciter les limites ;
- borner les zones `A_VERIFIER`.

---

## 9. Synthèse des décisions retenues

### Décisions structurantes

- conserver la doctrine 2.0 comme charpente ;
- utiliser le réel audité pour décrire les surfaces observables ;
- utiliser le glossaire comme pont de vocabulaire, pas comme preuve ;
- faire de `UIState`, `ConversationProgress` et `TrainerKnowledgeItem` les pivots documentaires du domaine ;
- documenter la couche tuteur comme lecture / recommandation / validation bornée ;
- documenter la couche formateur comme savoir gouverné / explicitation / validation ;
- clarifier la séparation tuteur / formateur / coordinateur / admin ;
- assumer `EvaluationTrace` comme nom cible encore à harmoniser avec le réel ;
- documenter `ConductProfiles` comme capacité réelle partielle ;
- marquer explicitement le runtime distant comme `A_VERIFIER`.

### Conséquence pratique

Les documents suivants sur ce domaine ne doivent ni :
- sur-vendre une couche tuteur / formateur déjà parfaitement stabilisée,
- ni sous-estimer le socle réel déjà présent.

La ligne documentaire retenue est donc :
- **doctrine conservée** ;
- **réel mieux nommé** ;
- **zones ouvertes explicitement bornées** ;
- **aucune spéculation de prod** ;
- **aucune refonte implicite du code à partir de la seule spec**.

# 03_backlog_actions — 110_interfaces_formateur_tuteur

## Domaine

- `DOMAINE_CODE = 110_interfaces_formateur_tuteur`
- `DOMAINE_LABEL = interfaces formateur / tuteur`

---

## 1. Objet du backlog

Ce backlog liste les actions à mener sur le seul domaine **interfaces formateur / tuteur** de Hugo cœur, après la phase de rapport, matrice et décisions documentaires.

Il ne constitue ni :
- un plan global Hugo 2.0 ;
- une roadmap produit exhaustive ;
- un ordre de refonte du code ;
- une validation implicite de tout ce qui est décrit par la spec cible.

La logique de priorisation appliquée ici est la suivante :
1. **réparer les ambiguïtés documentaires** ;
2. **stabiliser les contrats et le vocabulaire** ;
3. **séparer clairement réel, cible et zones ouvertes** ;
4. **ne lancer des actions code/produit que lorsqu’un besoin reste réellement non couvert**.

---

## 2. Règles de priorisation

### P0 — Recalage documentaire bloquant

Actions nécessaires pour éviter de mal décrire le domaine ou de prendre la cible pour du livré.

### P1 — Clarification de contrat

Actions nécessaires pour stabiliser le vocabulaire, les rôles, les surfaces et les responsabilités entre spec 2.0 et réel observé.

### P2 — Vérification ciblée / consolidation

Actions nécessaires pour lever des `A_VERIFIER`, préciser des mappings encore ambigus ou confirmer le comportement sur runtime/surfaces.

### P3 — Compléments produit / technique additifs

Actions utiles mais non prioritaires, à n’ouvrir qu’après recalage documentaire et clarification des contrats.

---

## 3. Backlog priorisé

| ID | Priorité | Action | Type | Résultat attendu | Sources |
|---|---|---|---|---|---|
| IFT-01 | P0 | Mettre à jour la documentation de domaine pour décrire explicitement la couche tuteur comme une couche de lecture de progression, d’interprétation, de recommandation et de validation bornée, sans pilotage direct du moteur. | Documentation | Une formulation stable, cohérente avec la cible 2.0 et sans dérive vers une console de contrôle du P0. | [file:6][file:1] |
| IFT-02 | P0 | Mettre à jour la documentation de domaine pour décrire explicitement la couche formateur comme une couche de savoir gouverné, d’ingestion documentaire, d’explicitation et de validation, et non comme un simple back-office documents. | Documentation | Une description propre de l’orchestrateur formateur, compatible avec la cible 2.0 et le réel observé. | [file:6][file:1] |
| IFT-03 | P0 | Réécrire les passages documentaires qui laissent entendre qu’un rôle non apprenant peut voir librement la conversation ou le verbatim. | Documentation | Une règle unique de formulation : non-apprenant = uniquement partage explicite + projections gouvernées. | [file:6][file:26] |
| IFT-04 | P0 | Corriger les documents de domaine qui présentent des surfaces testeur ou admin partielles comme des interfaces métier finales stabilisées. | Documentation | Une séparation explicite entre surface réelle observée, surface testeur, surface cible et surface encore ouverte. | [file:16][file:6] |
| IFT-05 | P1 | Ajouter, dans les documents de domaine, les noms réels observés derrière les objets doctrinaux structurants : `UIState`, `ConversationProgress`, `TrainerKnowledgeItem`, `QualityTracker`, `SynthesisService`, workflow d’évaluation. | Documentation | Une doc plus raccord avec le code, sans rebaptiser la doctrine à partir des noms Python. | [file:1][file:6] |
| IFT-06 | P1 | Stabiliser dans la documentation le mapping entre `EvaluationTrace` côté cible et `LearnerEvaluationRecord` / `Trace` / workflow d’évaluation côté réel. | Documentation / cadrage | Une formulation canonique de mapping, avec statut encore partiellement ambigu si besoin. | [file:1][file:6] |
| IFT-07 | P1 | Clarifier dans la doc que `GET .../ui-state` est un ancrage réel fort, alors que `GET .../progress` relève encore d’un contrat cible ou à confirmer. | Documentation de contrat | Une annexe contrats/surfaces qui distingue proprement endpoints observés et endpoints cibles. | [file:1][file:6] |
| IFT-08 | P1 | Clarifier le statut documentaire des `ConductProfiles` : capacité réelle partielle, visible surtout en surface testeur/séparée, non preuve d’une interface métier finale tuteur/formateur. | Documentation | Une description juste de la capacité, sans la nier ni la sur-vendre. | [file:16][file:26] |
| IFT-09 | P1 | Documenter explicitement l’incomplétude actuelle de l’admin comptes et la séparer des responsabilités tuteur/formateur. | Documentation | Une section “surfaces admin” propre, sans mélange avec les interfaces métier du domaine. | [file:16][file:6] |
| IFT-10 | P1 | Ajouter un sous-bloc “niveau de vérité” dans la doc de domaine : réel observé, cible 2.0, glossaire, `A_VERIFIER`. | Documentation | Une lecture plus sûre du domaine pour les prochains travaux CTO / Cursor. | [file:1][file:16][file:6] |
| IFT-11 | P2 | Vérifier dans le code et, si possible, dans les surfaces locales, le niveau exact d’exposition tuteur de `ConversationProgress`, `memory-summary`, synthèse et évaluation. | Audit ciblé | Une fiche de preuve courte par surface, distinguant backend observé et exposition UI effective. | [file:6][file:1][file:16] |
| IFT-12 | P2 | Vérifier le rôle exact du tuteur dans la validation terminale : recommandation, lecture, validation bornée de certaines traces, ou autre. | Audit ciblé / cadrage | Une décision de périmètre documentée au lieu d’une formulation floue. | [file:6] |
| IFT-13 | P2 | Vérifier la profondeur réelle du workflow formateur autour de `TrainerKnowledgeItem` : écrans, statuts, validation, rattachements référentiels. | Audit ciblé | Une photo du réel mieux bornée sur la chaîne formateur. | [file:6][file:1] |
| IFT-14 | P2 | Marquer explicitement `A_VERIFIER` toute affirmation liée au runtime distant Encoors pour ce domaine : endpoints, vues, flags, contrats exacts. | Documentation / vérification | Une doc qui n’infère jamais la prod distante depuis le local audité. | [file:16] |
| IFT-15 | P2 | Préparer une mini-annexe “surfaces par rôle” limitée à tuteur, formateur, coordinateur, org admin, avec trois colonnes : voit / peut faire / ne voit pas. | Documentation structurante | Un support de référence pour éviter les glissements de rôle dans les prochains documents. | [file:6][file:26] |
| IFT-16 | P3 | Si un vrai manque fonctionnel est confirmé après audit, préparer un contrat cible additif de projection tuteur basé sur `UIState` et `ConversationProgress`, sans exposition de P0 brut. | Cadrage produit / backend | Un mini-contrat de projection, pas une refonte moteur. | [file:6][file:1] |
| IFT-17 | P3 | Si le mapping `EvaluationTrace` reste trop dispersé, proposer un chantier de convergence documentaire puis technique léger, sans casser le workflow d’évaluation existant. | Cadrage doc + technique | Un objet mieux nommé et mieux traçable entre cible et réel. | [file:1][file:6] |
| IFT-18 | P3 | Si la chaîne formateur observée est fonctionnellement utile mais mal nommée, préparer un chantier de raccord vocabulaire/contrats avant tout redesign UX. | Cadrage | Une amélioration incrémentale et non une re-spécification lourde. | [file:1][file:6] |

---

## 4. Séquence recommandée

### Étape 1 — Recalage doc immédiat

À lancer en premier :
- `IFT-01`
- `IFT-02`
- `IFT-03`
- `IFT-04`

Objectif : arrêter les formulations trompeuses sur les rôles, la confidentialité et les surfaces réellement stabilisées.

### Étape 2 — Raccord de vocabulaire et contrats

À lancer ensuite :
- `IFT-05`
- `IFT-06`
- `IFT-07`
- `IFT-08`
- `IFT-09`
- `IFT-10`

Objectif : rendre la documentation exploitable pour le CTO et pour les prompts Cursor, avec un langage cohérent entre cible 2.0 et code observé.

### Étape 3 — Vérifications ciblées

À lancer après recalage documentaire :
- `IFT-11`
- `IFT-12`
- `IFT-13`
- `IFT-14`
- `IFT-15`

Objectif : lever les ambiguïtés restantes sans ouvrir prématurément un chantier de refonte.

### Étape 4 — Compléments additifs éventuels

À n’ouvrir qu’en dernier, si un manque réel est confirmé :
- `IFT-16`
- `IFT-17`
- `IFT-18`

Objectif : compléter les contrats du domaine sans casser l’architecture Hugo cœur existante.

---

## 5. Actions à ne pas ouvrir maintenant

Les actions suivantes ne doivent **pas** être prioritaires sur ce domaine à ce stade :

- refonte générale du front tuteur / formateur ;
- réécriture de la doctrine à partir des noms de fichiers Python ;
- conclusion hâtive sur une prod distante non auditée ;
- création de nouveaux objets doctrinaux non ancrés dans le corpus ;
- chantier de pilotage direct du moteur par les rôles tuteur ou formateur ;
- exposition supplémentaire de verbatim, prompts ou états P0 bruts.

Ces actions seraient soit prématurées, soit contraires aux invariants Hugo 2.0. | [file:6][file:16][file:26]

---

## 6. Critères de clôture du domaine documentaire

Le backlog de ce domaine pourra être considéré comme correctement traité quand les conditions suivantes seront remplies :

- la documentation distingue proprement **cible**, **réel**, **glossaire** et **A_VERIFIER** ;
- les rôles **tuteur**, **formateur**, **coordinateur** et **org admin** sont décrits sans collision ;
- `UIState`, `ConversationProgress`, `TrainerKnowledgeItem` et le workflow d’évaluation disposent d’un mapping documentaire propre vers le réel observé ;
- la règle de **partage explicite** est appliquée partout pour les rôles non apprenant ;
- les affirmations dépendant du runtime distant sont correctement marquées `A_VERIFIER` ;
- aucun passage ne laisse croire que les interfaces de ce domaine pilotent librement le moteur conversationnel.

---

## 7. Ligne d’exécution recommandée

La ligne d’exécution recommandée pour ce domaine est :

1. **recaler la doc** ;
2. **stabiliser les mots** ;
3. **vérifier les zones ouvertes** ;
4. **n’ajouter du produit ou du backend que si un besoin reste réellement non couvert**.

Cette ligne est cohérente avec Hugo cœur tel qu’il est cadré en 2.0 : backend Django orchestré, moteur piloté par état, front drivé par projections, confidentialité-first, partage explicite, et enrichissement additif plutôt que refonte spéculative. | [file:6][file:26]

---

## 8. Mise à jour cluster dev vague 2 encadrants (réel local)

**Sources :** `cluster_dev_encadrants_exports_vague2_resultats.md` · tests `test_encadrants_role_guards.py`, `test_evidence_exif.py`.

| Écart | Statut après cluster | Preuve |
|---|---|---|
| Endpoints trainer knowledge sans garde rôle | **RÉDUIT** | `can_manage_trainer_knowledge` sur elicitation/ingest/validate/list |
| Décalage UI exports vs backend 403 | **RÉDUIT** | `GroupView.canRunExports` → `isOrgAdminLike` ; `roleGuards.js` |
| EXIF non implémenté | **RÉDUIT** | `evidence_media.strip_image_metadata` + tests |
| Surfaces encadrants prod absentes | **PARTIEL** | `/app/tutor/*`, `/app/trainer/knowledge` layout prod |
| Frontière ORGADMIN/SUPERADMIN exports | **OUVERT** | Toujours `is_admin_like` partagé — D2-M12 couronne/vague 3 |
| RLS Postgres prod | **A_VÉRIFIER** | Inchangé |

---

## 9. Mise à jour cluster audit vague 5 — surfaces prod E2E

| Surface | Statut |
|---|---|
| `/app/tutor/*` + timeline API | **ALIGNE local** API ; UI browser **PARTIEL** |
| `/app/trainer/knowledge` list/validate | **ALIGNE local** ; ingest prod **PARTIEL** |
| Router guards LEARNER | **ALIGNE** code + tests front |
| E2E Playwright | **ABSENT** — OPS recommandé |
| Encoors surfaces encadrants | **A_VÉRIFIER** |

---

## 10. Mise à jour cluster 8 OPS — Playwright smoke

| Surface | Statut |
|---|---|
| `/app/tutor/*` timeline navigateur | **ALIGNE local** — SMOKE_TUTOR |
| `/app/trainer/knowledge` | **ALIGNE local** — SMOKE_TRAINER |
| Exports group ORGADMIN UI | **ALIGNE local** — SMOKE_ORGADMIN |
| E2E Playwright | **ALIGNE smoke** — 4 tests ; parcours riches **PARTIEL** |
| Encoors UI encadrants | **A_VÉRIFIER** |

---

## 11. Mise à jour cluster 14 — stabilisation interfaces encadrants

**Sources :** `cluster14_interfaces_encadrants_observabilite_plan_resultats.md` · smokes Playwright cluster 8.

| Point | Statut cluster 14 |
|---|---|
| Surfaces prod tuteur/formateur | **ALIGNE** — `/app/tutor/*`, `/app/trainer/knowledge` |
| Surfaces ORGADMIN exports | **PARTIEL** — layout tester `/groups-admin` |
| Fragmentation prod vs tester | **ÉCART CONFIRMÉ** — doc consolidée |
| Timeline sans verbatim | **ALIGNE** — SMOKE_TUTOR |
| Observabilité UI encadrant | **ABSENT** — backend seul ; badges pilotage timeline |
| Orchestrateur tuteur/formateur complet | **COURONNE** |

---