# 00_rapport_ecarts — 70_evaluation_traces_preuves

> **Mise à jour post-cluster 16 — 2026-06-18** · **Confirmé :** CTA éval/synthèse + **`ui.advisory`** (B16-C2) ; rendu front advisory C16. **PARTIEL :** EvaluationTrace pivot.

## Domaine

- `DOMAINE_CODE = 70_evaluation_traces_preuves`
- `DOMAINE_LABEL = évaluation, traces et preuves`

---

## 1. Objet du rapport

Ce rapport qualifie, pour le seul domaine **évaluation / traces / preuves** de Hugo cœur, l’écart entre :
- la **cible 2.0** telle qu’elle est fixée par la spec canonique et son complément ;
- le **réel observable** dans les audits du workspace Hugo réel ;
- le **pont de vocabulaire** fourni par le glossaire d’alignement.

Le rapport ne traite ni Hugo & Cie, ni les extensions client spécifiques, ni une administration métier complète au-delà de ce qui est explicitement cadré dans Hugo cœur. Son rôle est de préparer une lecture propre du domaine, d’identifier les continuités réelles, de qualifier les écarts documentaires et fonctionnels, et de poser les garde-fous avant la matrice d’écarts.

---

## 2. Règles de lecture et de vérité appliquées

### 2.1 Sources mobilisées et hiérarchie

Pour parler de la **cible**, ce rapport s’appuie prioritairement sur :
- `spec_canonique_hugo_2_0.md` ;
- `complement_unique_specs_2_0.md`.

Pour parler du **réel**, ce rapport s’appuie sur le corpus d’audit Hugo réel, relayé ici notamment par :
- le glossaire d’alignement, qui recense les objets, services et endpoints réellement observés pour le couple évaluation / traces / preuves ;
- `05_ECARTS_DOC_CODE_PRODUIT.md`, qui confirme plusieurs divergences documentaires et plusieurs limites du workflow réel.

Le **glossaire d’alignement** est utilisé comme **pont de vocabulaire** entre doctrine 2.0 et noms réellement observés (`LearnerEvaluationRecord`, `Trace`, `Evidence`, `request-evaluation`, `finalize-evaluation`, `generate-trace`). Il ne constitue pas, à lui seul, une preuve d’implémentation complète du domaine.

### 2.2 Garde-fous de lecture

- La spec 2.0 décrit un **état cible** ; elle ne prouve jamais qu’une capacité est déjà livrée.
- Une route d’API, un modèle ou une vue de front ne suffisent pas, à eux seuls, à prouver un workflow produit complet et stabilisé.
- Toute différence possible entre le code local audité et le runtime distant `hugoback.encoors.com` reste marquée `A_VERIFIER`.
- Le domaine doit être lu dans la doctrine Hugo cœur 2.0 : backend Django orchestré, P0 conserv et enrichi, évaluation comme branche terminale bornée, validation humaine finale, confidentialité-first, partage explicite, multi-tenant strict.

---

## 3. Périmètre cible 2.0 du domaine

### 3.1 Ce que la cible 2.0 fixe déjà

Dans Hugo 2.0, l’évaluation n’est **pas** un quatrième régime principal. Elle est une **branche terminale spécialisée**, facultative, de fin de scénario, activable seulement quand la conversation a atteint une maturité suffisante et que les bases structurées sont suffisamment exploitables.

La cible 2.0 fixe aussi plusieurs invariants structurants sur ce domaine :

- l’évaluation peut préparer une **trace structurée**, un auto-positionnement ou un objet partageable, mais **la validation finale reste humaine** ;
- le produit ne doit jamais laisser croire que Hugo certifie seul un niveau ou une compétence ;
- les objets du domaine comprennent au moins une **EvaluationTrace** côté doctrine, ainsi que des traces et preuves rattachées à une session ou à une trace ;
- les exports structurés doivent être possibles, notamment en CSV et JSON ;
- les preuves, en particulier photo, doivent rester gouvernées, rattachées à un contexte explicite, avec suppression EXIF par défaut et GPS opt-in ;
- la visibilité des traces, preuves et éventuels verbatims doit respecter la logique de **partage explicite** et l’interdiction d’accès libre au non-partagé par les rôles non apprenant.

La cible 2.0 fixe également une contrainte importante de produit : les actions terminales d’évaluation doivent être drivées par des états backend (`UIState`, `ConversationProgress`, états de CTA), et non par une logique front autonome.

### 3.2 Ce que la cible 2.0 laisse encore ouvert

Même si le rôle du domaine est bien cadré, plusieurs points restent encore partiellement ouverts côté cible 2.0 :

- le **format final** de `EvaluationTrace` ;
- le mapping exact entre trace d’évaluation, preuve, validation humaine et objets de circulation partageable ;
- le rôle précis de certains rôles métier dans la validation terminale ;
- le niveau de détail du contrat quasi-JSON côté `ui-state`, `progress` et actions terminales ;
- la nomenclature exacte qui relie doctrine 2.0 et objets réels (`EvaluationTrace`, `LearnerEvaluationRecord`, `Trace`, `Evidence`).

Le domaine est donc doctrinalement **bien verrouillé sur ses principes**, mais encore **partiellement ouvert sur ses contrats fins**.

---

## 4. Photo du réel observé

### 4.1 Services, objets et endpoints réellement observés

Le réel audité montre qu’un domaine **évaluation / traces / preuves** existe déjà dans Hugo cœur, avec plusieurs points d’ancrage réels :

- un workflow d’évaluation observé via `evaluationservice.py` et `evaluationworkflowengine.py` ;
- des endpoints réels liés à l’évaluation, notamment `request-evaluation`, `finalize-evaluation` et `evaluation-readiness` ;
- un objet réel côté glossaire rapproché de l’`EvaluationTrace` doctrinale, nommé `LearnerEvaluationRecord` ;
- des objets métier réels `Trace`, `TraceCriterionAssessment`, `Evidence` et une vue de type `EvidenceBundleView` ;
- un endpoint `generate-trace` ;
- des actions terminales visibles côté produit autour de la synthèse et de l’évaluation.

Le glossaire d’alignement indique cependant que le mapping entre la cible doctrinale `EvaluationTrace` et les objets réels observés (`LearnerEvaluationRecord`, `Trace`, objets de validation partagée) reste **ambigu** et doit être harmonisé.

### 4.2 Ce que le réel confirme sur le workflow d’évaluation

Le réel confirme que le domaine n’est pas absent : il existe bien un **workflow d’évaluation** distinct, ainsi que des actions API et des objets associés.

Le glossaire classe d’ailleurs le service d’évaluation comme `ALIGNE_DOC_PARTIEL` : le concept doctrinal de branche terminale d’évaluation est cohérent avec le réel, mais la documentation doit distinguer plus proprement la branche terminale 2.0 et le workflow actuellement observé (`evaluationservice.py`, `evaluationworkflowengine.py`, `request-evaluation`, `finalize-evaluation`, `evaluation-readiness`).

Autrement dit, le réel couvre déjà une part substantielle de la responsabilité métier, mais pas encore dans une nomenclature doctrinale stabilisée.

### 4.3 Traces et preuves dans le réel audité

Le réel montre aussi un domaine métier distinct pour les **traces** et les **preuves** :

- `Trace` existe comme objet réel ;
- `TraceCriterionAssessment` existe comme objet d’évaluation ou de qualification associé ;
- `Evidence` existe comme objet preuve ;
- la documentation d’alignement recommande explicitement de faire mieux apparaître ces noms réels dans la doc 2.0.

Cela confirme qu’il ne faut pas écrire la cible 2.0 comme si les preuves étaient une simple abstraction future. Une partie de cette mécanique existe déjà dans Hugo cœur, même si la structuration canonique complète n’est pas encore documentée proprement.

### 4.4 Limites confirmées dans le réel

Le document d’écarts doc/code/produit confirme plusieurs limites importantes du réel local :

- le payload de `generate-trace` est actuellement **minimal**, avec `messagescount` et des listes vides, ce qui est explicitement qualifié comme un écart par rapport à certaines attentes documentaires plus riches ;
- les divergences entre documentation antérieure et code réel sont suffisamment fortes pour imposer un recalage documentaire prudent ;
- la réalité du runtime distant `hugoback.encoors.com` n’est pas prouvée équivalente au local pour les endpoints d’évaluation, et reste donc `A_VERIFIER`.

Le réel doit donc être lu comme **présent mais incomplet**, plutôt que comme domaine absent ou comme domaine déjà pleinement stabilisé.

### 4.5 Produit et surfaces visibles

Côté produit, le document d’écarts croisés indique que les boutons **synthèse** et **évaluation** sont branchés dans le front prod montrable, ce qui contredit des docs plus anciennes qui les présentaient comme non câblés.

Cela confirme que le domaine a déjà une **surface produit effective**, au moins pour le déclenchement des actions terminales. En revanche, cette présence front ne suffit pas à prouver :
- la richesse complète de la trace générée ;
- la stabilisation finale des objets de partage ;
- la cohérence totale entre produit local et runtime distant ;
- la formalisation 2.0 complète du domaine.

---

## 5. Analyse narrative des écarts

### 5.1 Zone de bon alignement

Le premier constat est que le domaine **n’est pas à créer ex nihilo**.

La cible 2.0 attend une évaluation terminale bornée, des traces structurées, des preuves gouvernées, des exports et des règles de validation humaine. Le réel montre déjà :
- un workflow d’évaluation ;
- des endpoints dédiés ;
- des objets de trace et de preuve ;
- des actions terminales visibles côté produit.

Il y a donc un **socle réel solide** sur lequel s’appuyer. Cela interdit de lire la spec comme une injonction à refondre entièrement le domaine.

### 5.2 Écart principal : vocabulaire et modèle de domaine encore dispersés

Le plus gros écart observé n’est pas l’absence du domaine, mais sa **dispersion de vocabulaire**.

Côté cible, la doctrine parle d’`EvaluationTrace`, de validation humaine, de traces et de preuves gouvernées. Côté réel, on observe plutôt :
- `LearnerEvaluationRecord` ;
- `Trace` ;
- `TraceCriterionAssessment` ;
- `Evidence` ;
- plusieurs endpoints et workflows techniques associés.

Le glossaire classe précisément `EvaluationTrace` comme `AMBIGU`, ce qui signifie que le rapprochement conceptuel existe, mais que le mapping n’est pas encore assez net pour être présenté comme stabilisé. L’écart à traiter est donc d’abord un écart de **modélisation documentaire et de raccord sémantique**.

### 5.3 Écart important : richesse réelle des traces produites

Le document d’écarts croisés confirme un point de friction majeur : le endpoint `generate-trace` existe, mais son payload réel est **minimal** par rapport à certaines attentes documentaires plus riches.

Cet écart est important pour deux raisons :
- il montre que le domaine ne doit pas être sur-vendu comme s’il produisait déjà des traces riches et pleinement exploitables ;
- il indique que la priorité n’est pas forcément de créer de nouveaux concepts, mais plutôt de clarifier ce qui est effectivement généré aujourd’hui, puis d’enrichir progressivement le contrat si nécessaire.

Autrement dit, la cible 2.0 peut garder l’ambition de traces structurées plus robustes, mais il faut documenter honnêtement que le réel observé est plus limité.

### 5.4 Écart de formalisation sur validation humaine

La cible 2.0 est ferme : l’évaluation ne certifie pas seule, la validation finale reste humaine, et les objets dérivés ne doivent pas être auto-promus vers un statut validé humainement.

Le réel audité confirme des objets et des workflows d’évaluation, mais ne permet pas encore, via le seul corpus mobilisé ici, d’affirmer que tout le cycle de validation humaine est déjà formalisé de bout en bout dans Hugo cœur local. Le complément 2.0 précise même que le rôle exact des rôles métier dans certaines validations terminales reste encore partiellement ouvert.

L’écart ici n’est donc pas forcément un manque fonctionnel brut ; c’est surtout un manque de **contrat stabilisé** et de **vocabulaire cohérent** entre doctrine, objets réels et surfaces produit.

### 5.5 Écart de produit : surface visible oui, contrat lisible encore partiel

Le front montre que les actions terminales existent réellement. C’est une bonne nouvelle, car cela confirme que Hugo cœur n’est pas seulement au stade de promesse backend sur ce domaine.

Mais la cible 2.0 attend plus qu’un simple bouton :
- un état backend propre de disponibilité ;
- des raisons de blocage ou d’éligibilité ;
- une articulation claire avec `ConversationProgress`, `UIState`, partage explicite et validation humaine ;
- un langage produit non trompeur sur ce que vaut réellement la trace.

Le réel paraît déjà aller dans cette direction, mais le corpus mobilisé ici ne suffit pas encore à prouver que le **contrat produit complet** est déjà stabilisé. Il faut donc éviter à la fois la sous-estimation et la sur-affirmation.

### 5.6 À propos des preuves

La cible 2.0 fixe des règles fortes sur les preuves : rattachement à un contexte explicite, gouvernance, confidentialité, suppression EXIF par défaut, GPS opt-in.

Le réel confirme l’existence d’objets `Evidence`, mais le corpus mobilisé ici ne suffit pas à démontrer en détail tout le niveau de conformité effective du workflow preuve à ces règles fines, notamment en runtime distant ou sur toutes les variantes d’usage. Ces points doivent donc rester partiellement `A_VERIFIER` tant qu’une relecture de code et d’exécution plus ciblée n’a pas été faite.

---

## 6. Lecture de synthèse par niveau de vérité

### 6.1 Implémenté / observable

Sur ce domaine, le réel audité permet d’affirmer comme **implémenté ou observable** :

- un workflow d’évaluation distinct ;
- des endpoints d’évaluation observés (`request-evaluation`, `finalize-evaluation`, `evaluation-readiness`) ;
- des actions terminales de synthèse / évaluation branchées côté front produit local ;
- des objets réels `Trace`, `TraceCriterionAssessment`, `Evidence` ;
- un endpoint `generate-trace` ;
- un rapprochement réel possible entre `EvaluationTrace` doctrinale et `LearnerEvaluationRecord`, même si ce mapping n’est pas encore stabilisé.

### 6.2 Cible 2.0

Relèvent de la **cible 2.0** :

- une définition propre et stable de l’`EvaluationTrace` comme trace terminale structurée ;
- un contrat produit explicite des états d’éligibilité, blocage, disponibilité et partage ;
- une articulation propre entre évaluation, traces, preuves, validation humaine et exports ;
- une doctrine de circulation des objets partageables pleinement stabilisée ;
- une clarification plus fine des rôles métier dans certaines validations terminales.

### 6.3 Écarts confirmés

À ce stade, les **écarts confirmés** sur le domaine sont principalement :

- le mapping doctrinal `EvaluationTrace` ↔ objets réels (`LearnerEvaluationRecord`, `Trace`, `Evidence`) reste insuffisamment stabilisé ;
- le payload réel de `generate-trace` est plus minimal que certaines attentes documentaires ;
- la doc doit mieux distinguer branche terminale doctrinale et workflow réel observé ;
- certaines docs anciennes sur l’état des boutons synthèse / évaluation sont obsolètes et ne doivent plus être utilisées comme vérité du produit.

### 6.4 À vérifier

Restent explicitement `A_VERIFIER` :

- l’équivalence exacte entre le runtime local audité et `hugoback.encoors.com` sur le domaine évaluation / traces / preuves ;
- le niveau réel de conformité de toutes les preuves aux règles fines de gouvernance attendues par la cible 2.0 ;
- la chaîne exacte de validation humaine dans toutes les variantes de rôles et d’environnements ;
- la profondeur réelle du contrat produit côté partage et circulation des objets sur runtime distant.

---

## 7. Garde-fous documentaires et techniques pour la suite

### 7.1 Ce qu’il ne faut pas faire

Pour ce domaine, il faut éviter quatre dérives :

1. présenter `EvaluationTrace` comme un objet déjà unifié et stabilisé dans le réel alors que le mapping reste ambigu ;
2. lire la présence d’endpoints et de boutons comme preuve d’un workflow complet et riche sur toute la chaîne trace / preuve / validation ;
3. relire la cible 2.0 comme une injonction à reconstruire tout le domaine alors qu’un socle réel existe déjà ;
4. laisser entendre que Hugo évalue ou certifie seul, alors que la doctrine 2.0 maintient explicitement la validation humaine finale.

### 7.2 Ce qu’il faut privilégier

La bonne trajectoire sur ce domaine est plutôt :

- clarifier le **vocabulaire** entre `EvaluationTrace`, `LearnerEvaluationRecord`, `Trace`, `Evidence` ;
- expliciter le **niveau réel** du payload et des objets aujourd’hui produits ;
- stabiliser les **contrats backend** des actions terminales sans déplacer la logique vers le front ;
- clarifier la doctrine de **partage** et de **validation humaine** appliquée aux traces et preuves ;
- enrichir ensuite de façon additive les objets ou payloads réellement utiles, plutôt que créer une architecture parallèle.

---

## 8. Conclusion opérationnelle du domaine

Le domaine `70_evaluation_traces_preuves` est un domaine **réellement présent** dans Hugo cœur, avec des services, endpoints, objets métier et surfaces produit déjà observables.

L’écart principal ne porte pas sur l’existence du domaine, mais sur son **raccord doctrinal et contractuel** : vocabulaire encore dispersé, richesse réelle des traces encore limitée, validation humaine et partage encore insuffisamment formalisés comme contrat unifié. La suite du travail doit donc prioriser le **recalage de vocabulaire**, la **clarification des contrats réels**, et les **compléments backend additifs**, sans sur-vendre ni sous-estimer ce qui existe déjà.

---

## 9. D2-M05 — Mapping EvaluationTrace (juin 2026)

**Référence canonique :** `mapping_EvaluationTrace_runtime_local.md`  
**Sources complémentaires :** note lot CTA (`10_runtime_p0_progression_uistate_note_lot_courant_cta_synthese_evaluation.md`), matrice cluster 2 §4.

### 9.1 RÉEL OBSERVÉ — ce que l’on peut revendiquer sans survendre

| Affirmation | Preuve locale |
|-------------|---------------|
| Branche d’évaluation utilisable (éligibilité → demande → record → preview) | `request-evaluation`, `evaluation-readiness`, `finalize-evaluation` ; `test_request_evaluation_guard.py`, A1-04 |
| CTA standardisés via UIState | `cta_evaluation` / `cta_synthesis` ; `test_cta_*` |
| Validation humaine obligatoire (pas de certification autonome) | `TrainerEvaluationRecordValidationView`, `tutor_validated*` ; doctrine + note lot CTA |
| Objets métier séparés : évaluation calculée, trace, preuve | `LearnerEvaluationRecord`, `Trace`, `Evidence` |
| Trace `generate-trace` **minimale** (payload squelette) | `GenerateTraceView`, `_get_or_create_runtime_trace` — **ÉCART CONFIRMÉ** vs cible riche |
| Deux circuits de validation : **record** vs **trace** | `trainer/.../validate/` et `POST /traces/{id}/validate/` — coexistence documentée, non fusionnée |

### 9.2 CIBLE 2.0 — ce qui reste hors lot courant

| Élément | Statut |
|---------|--------|
| Objet unique `EvaluationTrace` (modèle ou endpoint agrégé) | **CIBLE** — nom doctrinal conservé ; dispersion runtime assumée |
| Enrichissement automatique `payload_structured` post-évaluation | **CIBLE** — refonte workflow, hors D2-M05 |
| Bundle Qualiopi « riche » (eval + critères + preuves détaillées) | **CIBLE** — enrichissement distinct |
| D9bis / `ConversationTurnLLMAnalysis` | **CIBLE** — ne pas fusionner avec EvaluationTrace |

### 9.3 A_VÉRIFIER

| Point | Motif |
|-------|-------|
| Contenu ZIP `evidence-bundle` sur Encoors | Local : `traces.json` = métadonnées sans `payload_structured` ni `LearnerEvaluationRecord` |
| Parité endpoints évaluation prod vs local | `10_FICHE_RUNTIME_PROD_ENCOORS` |
| RLS Postgres sur traces / bundles | SQLite local ; migrations présentes, efficacité prod non prouvée |

### 9.4 Décision de vocabulaire (lot courant)

| Terme doctrinal | Terme runtime | Règle |
|-----------------|---------------|-------|
| **EvaluationTrace** | *Concept* — jamais nom de table | Specs 2.0 et docs CTO uniquement |
| Trace d’évaluation calculée | `LearnerEvaluationRecord` | Code, APIs, tickets |
| Trace structurée / trace_rich_v1 | `Trace.payload_structured` | Préciser « minimale » si création apprenant |
| Preuve | `Evidence` | Inchangé |

**Statut matrice interne :** la ligne `EvaluationTrace` passe de **AMBIGU** à **RENOMMER_DANS_DOC** (dispersion nommée et assumée) ; `LearnerEvaluationRecord` en **ALIGNE_DOC_PARTIEL**.

---

# 01_matrice_ecarts — 70_evaluation_traces_preuves

- `DOMAINE_CODE = 70_evaluation_traces_preuves`
- `DOMAINE_LABEL = évaluation, traces et preuves`

Légende des statuts :
- `ALIGNE`
- `ALIGNE_DOC_PARTIEL`
- `RENOMMER_DANS_DOC`
- `AMBIGU`
- `A_VERIFIER`
- `ABSENT / NOUVEAU_CONTRAT`

---

## 1. Objets de domaine

### 1.1 EvaluationTrace (doctrine) ↔ LearnerEvaluationRecord, Trace, Evidence (réel)

| Élément                  | Cible 2.0 / Doctrine                                                                                                          | Réel audité / Glossaire                                                                                         | Analyse d’écart                                                                                                                         | Statut             |
|-------------------------|--------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------|--------------------|
| EvaluationTrace         | Agrégat doctrinal (évaluation + trace + preuves + validation) — **pas de modèle unique**. | Dispersion : `LearnerEvaluationRecord`, `Trace`, `TraceCriterionAssessment`, `Evidence`. | Mapping **documenté** D2-M05 (`mapping_EvaluationTrace_runtime_local.md`) ; agrégat runtime = **CIBLE**. | **RENOMMER_DANS_DOC** |
| LearnerEvaluationRecord | Non nommé doctrine ; porte l’évaluation calculée.                        | Modèle réel ; OneToOne `session` ; `request-evaluation` / `finalize-evaluation`.          | Pont glossaire stabilisé : candidat principal pour la composante **évaluation** d’EvaluationTrace.     | **ALIGNE_DOC_PARTIEL** |
| Trace                   | Notion de trace structurée (fiche, bilan, etc.) présente côté doctrine.                                                       | Modèle `Trace` réel + `TraceCriterionAssessment` observés.                                                       | Concept de trace bien présent, mais lien explicite doc ↔ objets réels encore partiel.                                                  | ALIGNE_DOC_PARTIEL |
| Evidence                | Preuve métier rattachée à une trace ou une session, gouvernée, non flottante.                                                 | Modèle réel `Evidence` + `EvidenceBundleView` observés.                                                         | Très bon raccord conceptuel ; la doc 2.0 doit faire apparaître explicitement le nom `Evidence` et son rôle concret.                    | RENOMMER_DANS_DOC  |

---

## 2. Services backend et workflows

### 2.1 Services d’évaluation

| Élément                    | Cible 2.0 / Doctrine                                                                                                                       | Réel audité / Glossaire                                                                                  | Analyse d’écart                                                                                                                                 | Statut             |
|---------------------------|---------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------|--------------------|
| Service d’évaluation      | Branche terminale spécialisée, facultative, produisant une EvaluationTrace structurée avec validation humaine finale.                      | `evaluationservice.py`, `evaluationworkflowengine.py`, endpoints `request-evaluation`, `finalize-evaluation`, `evaluation-readiness`. | Workflow réel présent, mais la doc 2.0 doit distinguer plus clairement branche terminale doctrinale vs workflow concret observé.              | ALIGNE_DOC_PARTIEL |
| Génération de trace riche | Production d’une trace structurée exploitable (exports, tuteur, coordinateur), pas seulement un compteur de messages.                       | Endpoint `generate-trace` existant, avec payload minimal (ex. `messagescount` et listes vides) dans le local audité.                | Capacité réelle présente mais très en-deçà des ambitions documentaires les plus riches ; l’écart est déjà identifié dans les audits.          | ALIGNE_DOC_PARTIEL |
| SynthesisService          | Service de synthèse structurée, pouvant alimenter des traces / bilans mais distinct de l’évaluation certificative.                          | `synthesisservice.py`, endpoint `request-synthesis` observés et fonctionnels.                                                      | Alignement conceptuel bon ; important de garder la distinction synthèse ↔ évaluation dans la documentation.                                   | ALIGNE             |

---

## 3. Endpoints et actions terminales

### 3.1 Endpoints d’évaluation et de trace

| Élément                     | Cible 2.0 / Doctrine                                                                                                    | Réel audité / Glossaire                                                                                   | Analyse d’écart                                                                                                                                       | Statut             |
|----------------------------|--------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------|
| POST `request-evaluation`  | Déclencher la branche terminale d’évaluation si la session est éligible (maturité, conditions, etc.).                   | Endpoint présent localement ; divergence partielle possible avec runtime distant.                          | Concept aligné mais comportement distant non vérifié ; la doc doit distinguer clairement comportement local et éventuelles variantes distantes.     | ALIGNE_DOC_PARTIEL |
| POST `finalize-evaluation` | Finaliser la trace d’évaluation après action humaine, sans auto-valider des statuts humains.                             | Endpoint observé dans l’audit ; rôle exact et contrat complet encore peu détaillés au niveau doctrinal.    | Alignement global, mais nécessiterait un contrat doctrinal plus explicite sur les conditions et la validation humaine.                              | ALIGNE_DOC_PARTIEL |
| GET `evaluation-readiness` | Lire l’éligibilité d’une session à l’évaluation (ready / possible / locked) et les raisons associées.                    | Endpoint observé ; divergences possibles entre local et distant signalées dans le glossaire.              | Bon concept ; statut et mapping local/distant restent à préciser pour ne pas sur-affirmer la situation en production distante.                      | A_VERIFIER         |
| POST `generate-trace`      | Générer une trace structurée associée à la session, aux critères, aux preuves.                                           | Endpoint présent ; payload minimal confirmé dans le local audité.                                          | Implémenté, mais très éloigné d’une trace riche ; écart confirmé et déjà classé majeur dans les écarts doc/code/produit.                            | ALIGNE_DOC_PARTIEL |

---

## 4. États, statuts et validation humaine

### 4.1 Statuts de traces et d’évaluation

| Élément                          | Cible 2.0 / Doctrine                                                                                                    | Réel audité / Glossaire                                                                 | Analyse d’écart                                                                                                                                   | Statut    |
|---------------------------------|--------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------|-----------|
| Statuts EvaluationTrace         | Trace d’évaluation avec statuts structurés, validation humaine obligatoire avant tout usage certifiant ou de circulation. | Objets `LearnerEvaluationRecord` et `Trace` existent, mais les statuts exacts ne sont pas détaillés dans ce corpus. | Rôle doctrinal clair, mais implémentation fine des statuts et de leur usage reste à documenter et à vérifier.                                       | A_VERIFIER |
| Non auto-promotion vers validé | Aucune trace ou connaissance dérivée ne doit être auto-promue vers un statut “validé humainement”.                       | Règle doctrinale forte ; pas de contre-exemple explicite dans l’audit, mais pas de preuve exhaustive non plus.     | Invariant à respecter ; conformité effective à confirmer sur l’ensemble du workflow d’évaluation et des statuts.                                   | A_VERIFIER |

---

## 5. Preuves et confidentialité

### 5.1 Preuves, photos et gouvernance

| Élément                                 | Cible 2.0 / Doctrine                                                                                                                                      | Réel audité / Glossaire                                                                    | Analyse d’écart                                                                                                                                                  | Statut             |
|----------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------|
| Evidence (preuve)                      | Preuve rattachée à un contexte explicite ; suppression EXIF par défaut, GPS opt‑in, jamais flottante hors gouvernance métier.                             | Modèle `Evidence` et `EvidenceBundleView` présents.                                        | Concept implémenté ; conformité détaillée (EXIF, GPS, multi-tenant strict, etc.) à confirmer sur l’ensemble du code et du runtime distant.                      | ALIGNE_DOC_PARTIEL |
| Confidentialité-first sur traces      | Traces et preuves visibles uniquement via partage explicite ; aucun accès libre au verbatim non partagé pour les rôles non apprenant.                      | Doctrine 2.0 ferme ; l’audit ne montre pas de violation explicite mais n’épuise pas tous les cas. | Invariant à maintenir ; conformité globale à vérifier, en particulier côté API, exports et runtime distant.                                                     | A_VERIFIER         |
| Multi-tenant strict sur preuves/traces | Isolation complète par organisation, RLS active, pas de lecture inter-tenant sur traces et preuves.                                                        | Middleware RLS testé sur SQLite ; pas de preuve équivalente en Postgres prod dans ce corpus. | Principes en place, mais preuve de mise en œuvre complète en production distante manquante dans ce corpus ; à vérifier avant d’affirmer un alignement complet. | A_VERIFIER         |

---

## 6. Surfaces produit et contrats d’état

### 6.1 Actions terminales dans UIState / progression

| Élément                                | Cible 2.0 / Doctrine                                                                                                          | Réel audité / Glossaire                                                                 | Analyse d’écart                                                                                                                                       | Statut             |
|---------------------------------------|-------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------|
| CTA synthèse / évaluation (UIState)   | UIState doit exposer l’état des actions de synthèse et d’évaluation (disponible, bloqué, non éligible) de façon lisible.     | Front 1.8 montre des boutons synthèse / évaluation branchés ; logique exacte peu détaillée ici. | Alignement de principe ; contrat exact des champs UIState et conditions d’affichage/éligibilité reste à formaliser dans la doc 2.0.                    | ALIGNE_DOC_PARTIEL |
| Projection de progression → évaluation | ConversationProgress doit porter les signaux d’éligibilité à la synthèse / évaluation (maturité, blocages, etc.).            | Progression réelle calculée, mais export dédiée `progress` côté API encore ambigu (passage surtout via `ui-state`). | Alignement conceptuel, mais exposition produit et mapping endpoint restent partiels (progression surtout visible via UIState aujourd’hui).             | AMBIGU             |

---

## 7. Contrats d’export

### 7.1 Exports structurés (CSV / JSON)

| Élément                          | Cible 2.0 / Doctrine                                                                                       | Réel audité / Glossaire                                                 | Analyse d’écart                                                                                                                           | Statut    |
|---------------------------------|-------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|-----------|
| Exports de traces / preuves     | Possibilité d’exports structurés (CSV, JSON) pour traces et preuves, avec règles de confidentialité adaptées. | Capacité d’export mentionnée côté doctrine ; formats effectifs peu détaillés dans ce corpus. | Rôle cible bien posé ; implémentation effective des formats et filtres reste à documenter précisément.                                   | A_VERIFIER |
| Objets partageables vers tuteur | Certains objets (EvaluationTrace, Trace, Evidence) doivent être partageables vers tuteur / coordinateur, sans verbatim brut non partagé. | Présence réelle d’objets et vues tuteur ; contrat complet de partage non exhaustif dans ce corpus.    | Principes clairs, implémentation fine (quels champs, quel filtrage) à expliciter et vérifier.                                           | ALIGNE_DOC_PARTIEL |

---

## 8. Lignes de fracture principales

| Sujet                                       | Lecture synthétique                                                                                                              | Statut dominant                |
|--------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|--------------------------------|
| Existence d’un domaine évaluation / traces | Domaine bien présent (services, endpoints, objets) ; pas à inventer from scratch.                                               | ALIGNE                         |
| Mapping EvaluationTrace ↔ objets réels     | Concept clair mais mapping doctrinal ↔ `LearnerEvaluationRecord` / `Trace` / `Evidence` encore insuffisamment stabilisé.        | AMBIGU                         |
| Richesse de generate-trace                 | Endpoint existant mais payload minimal, très en deçà des attentes documentaires les plus ambitieuses.                           | ALIGNE_DOC_PARTIEL             |
| Gouvernance des preuves                    | Objet `Evidence` réel cohérent, mais conformité détaillée (EXIF, GPS, RLS, partage explicite) à confirmer.                      | ALIGNE_DOC_PARTIEL / A_VERIFIER |
| Validation humaine                         | Doit rester obligatoire, non auto-promue ; conformité fine du workflow d’évaluation encore à vérifier dans ce corpus.          | A_VERIFIER                     |

# 02_decisions_documentaires — 70_evaluation_traces_preuves

- `DOMAINE_CODE = 70_evaluation_traces_preuves`
- `DOMAINE_LABEL = évaluation, traces et preuves`

---

## 1. Objet du document

Ce document fixe les **décisions documentaires** à appliquer au domaine **évaluation / traces / preuves** pour aligner proprement :
- la doctrine cible Hugo 2.0 ;
- le réel audité de Hugo cœur ;
- le vocabulaire utilisé dans les futurs travaux CTO, prompts Cursor et matrices d’écarts.

Ces décisions ne constituent ni une preuve d’implémentation supplémentaire, ni une injonction automatique à refondre le code. Elles servent à stabiliser la manière correcte de décrire le domaine, sans sur-vendre le réel ni appauvrir la cible.

---

## 2. Décisions de cadrage

### D1 — Le domaine reste borné à Hugo cœur

La documentation de ce domaine reste strictement bornée à **Hugo cœur**. Aucune décision documentaire ici ne doit dépendre de Hugo & Cie, d’extensions client spécifiques, ni d’une capacité supposée exister hors du corpus audité.

### D2 — L’évaluation est décrite comme branche terminale, pas comme régime autonome

Dans toute la documentation 2.0 et dérivée, l’évaluation reste décrite comme une **branche terminale spécialisée et facultative**, jamais comme un quatrième régime principal ni comme une logique autonome de certification.

### D3 — La validation finale reste humaine

Toute formulation documentaire doit rappeler explicitement que Hugo peut préparer une trace d’évaluation, un auto-positionnement ou un objet partageable, mais que la **validation finale reste humaine**.

### D4 — Le produit ne doit jamais laisser croire à une certification autonome

La documentation produit, les specs d’interface et les formulations de backlog ne doivent jamais laisser entendre que Hugo “certifie” seul un niveau ou une compétence.

---

## 3. Décisions de vocabulaire

### D5 — Le nom doctrinal central reste `EvaluationTrace`

Dans la doctrine 2.0, le nom conceptuel de référence reste **`EvaluationTrace`** pour désigner la trace terminale structurée d’évaluation ou de bilan.

### D6 — La doc doit exposer explicitement le mapping vers les noms réels observés

La documentation ne doit plus parler d’`EvaluationTrace` seule. Elle doit faire apparaître explicitement, quand c’est utile, le mapping avec les noms réellement observés dans Hugo développé :
- `LearnerEvaluationRecord`
- `Trace`
- `TraceCriterionAssessment`
- `Evidence`

### D7 — On ne prétend pas que ce mapping est déjà totalement stabilisé

La doc doit dire clairement que le mapping `EvaluationTrace` ↔ `LearnerEvaluationRecord` / `Trace` / `Evidence` est **encore partiellement ambigu**. Il faut donc parler d’objets réels observés et de rapprochement conceptuel, sans affirmer une équivalence finale déjà figée.

### D8 — Les noms réels `Trace` et `Evidence` doivent être ajoutés dans les matrices 2.0

Les matrices d’objets et pseudo-schémas documentaires 2.0 doivent faire apparaître explicitement les noms réels `Trace`, `TraceCriterionAssessment` et `Evidence`, comme objets réellement observés à raccorder à la doctrine.

### D9 — `LearnerEvaluationRecord` doit apparaître dans les annexes de mapping

`LearnerEvaluationRecord` doit être documenté dans les annexes de mapping ou tableaux de correspondance comme **nom réel observé** susceptible d’incarner, au moins partiellement, l’`EvaluationTrace` doctrinale.

---

## 4. Décisions sur les services et endpoints

### D10 — Le service doctrinal d’évaluation doit être raccordé au workflow réel

La documentation 2.0 doit expliciter que la branche terminale doctrinale d’évaluation correspond, dans le réel audité, à un workflow observé autour de :
- `evaluationservice.py`
- `evaluationworkflowengine.py`
- `request-evaluation`
- `finalize-evaluation`
- `evaluation-readiness`

### D11 — La doc doit distinguer branche terminale doctrinale et workflow réel observé

La documentation ne doit pas confondre :
- le **rôle doctrinal** du domaine, c’est-à-dire branche terminale d’évaluation, trace terminale et validation humaine ;
- et le **workflow technique réel** observé dans le code local.

### D12 — Les endpoints d’évaluation locaux doivent être documentés comme observés localement

Les endpoints `request-evaluation`, `finalize-evaluation` et `evaluation-readiness` doivent être documentés comme **observés dans le local audité**, avec mention explicite que la stricte équivalence du runtime distant Encoors reste `A_VERIFIER`.

### D13 — `generate-trace` doit être décrit honnêtement

L’endpoint `generate-trace` doit être documenté comme **existant dans le réel**, mais avec un payload observé **minimal** dans le local audité. La documentation ne doit plus le présenter comme produisant déjà une trace riche si ce n’est pas ce que montre l’audit.

---

## 5. Décisions sur les objets métier

### D14 — `Trace` est documenté comme objet métier réel, pas comme simple alias

La documentation cible doit mieux relier la notion générique de trace aux objets réels `Trace` et `TraceCriterionAssessment`, sans réduire ces objets à de simples détails techniques invisibles.

### D15 — `Evidence` est documenté comme objet preuve réel

Le nom réel `Evidence` doit être explicitement introduit dans la documentation cible sur les preuves, au lieu de rester implicite derrière une formulation trop abstraite.

### D16 — On conserve la distinction trace / preuve

La documentation doit maintenir une distinction nette entre :
- **trace** : objet structuré de bilan, d’évaluation ou de restitution ;
- **preuve** : artefact rattaché à un contexte explicite, mobilisable dans ou autour d’une trace.

### D17 — On ne crée pas de faux objet unificateur dans la doc

Tant que le mapping réel n’est pas stabilisé, la documentation ne doit pas inventer un objet “unique” déjà livré qui fusionnerait `EvaluationTrace`, `Trace`, `LearnerEvaluationRecord` et `Evidence`.

---

## 6. Décisions sur validation humaine et partage

### D18 — La validation humaine reste une clause visible dans chaque sous-document du domaine

Chaque sous-document pertinent du domaine doit rappeler que :
- une trace peut être préparée automatiquement ;
- une évaluation peut être déclenchée si elle est éligible ;
- mais aucune validation humaine ne doit être supposée automatique.

### D19 — Le rôle du tuteur est borné dans la doc

La documentation doit rappeler que le tuteur peut lire, commenter, recommander et, selon les cas explicitement prévus, intervenir sur certaines traces partageables, mais qu’il ne dispose pas par défaut d’un pouvoir générique de validation terminale des évaluations dans Hugo cœur 2.0 de référence.

### D20 — Les traces, preuves et verbatims doivent rester décrits sous logique de partage explicite

La documentation doit continuer à séparer :
- synthèse partageable ;
- trace partageable ;
- preuve partageable ;
- verbatim non partagé par défaut.

On ne doit pas faire glisser le domaine vers une logique où les rôles non apprenant auraient un accès libre au contenu brut.

---

## 7. Décisions sur produit et UI

### D21 — Les actions terminales restent documentées comme états backend-first

La documentation produit doit continuer à décrire la disponibilité de la synthèse et de l’évaluation comme des **états backend drivés** (`UIState`, `ConversationProgress`, readiness, éligibilité), et non comme une logique calculée côté front.

### D22 — Le front peut exposer les CTA, pas décider la doctrine

La doc interface peut montrer des boutons ou CTA de synthèse / évaluation, mais elle doit préciser que leur disponibilité dépend du backend et des états de session, pas d’une logique front autonome.

### D23 — Les docs obsolètes sur les boutons non branchés doivent être déclassées

Les documents anciens qui affirment que les boutons synthèse / évaluation ne sont pas branchés ne doivent plus être utilisés comme vérité produit pour ce domaine, car le réel audité montre qu’ils sont branchés dans le front prod local montrable.

---

## 8. Décisions sur les garde-fous rédactionnels

### D24 — Toute formulation “riche” sur les traces doit être indexée au niveau de vérité

Si une documentation décrit une trace riche, détaillée, critériée, exportable ou validable, elle doit préciser si elle parle :
- de la **cible 2.0** ;
- du **réel local audité** ;
- ou d’un point encore `A_VERIFIER`.

### D25 — Toute mention d’Encoors doit être marquée `A_VERIFIER` si non prouvée

Aucune documentation de ce domaine ne doit affirmer que le runtime distant `hugoback.encoors.com` se comporte exactement comme le local audité sur les endpoints, payloads et règles d’évaluation tant que cela n’est pas vérifié.

### D26 — On ne transforme pas un besoin documentaire en verdict de refonte

Quand le réel couvre déjà la responsabilité métier du domaine, la documentation doit prioriser :
- le raccord de vocabulaire ;
- la clarification des contrats ;
- l’explicitation des niveaux de vérité ;
- puis seulement les compléments backend additifs nécessaires.

### D27 — Les noms de fonctions Python ne remplacent pas la doctrine

La documentation doit garder les noms doctrinaux pour raisonner juste, tout en ajoutant les noms réels observés pour parler juste du code. Elle ne doit ni rebaptiser toute la doctrine avec des noms de fichiers Python, ni rester dans une abstraction qui n’existe nulle part dans le code réel.

---

## 9. Mise à jour documentaire attendue

### D28 — Mettre à jour la spec canonique 2.0 sur les objets de domaine

La matrice des objets 2.0 doit être enrichie, pour ce domaine, avec une colonne ou un sous-bloc “nom réel observé”, faisant apparaître au minimum :
- `LearnerEvaluationRecord`
- `Trace`
- `TraceCriterionAssessment`
- `Evidence`

### D29 — Mettre à jour les specs interface / tuteur / formateur sur le partage des traces

Les specs 2.0 dérivées doivent mieux expliciter :
- quels objets sont partageables ;
- quels objets restent non partageables par défaut ;
- et comment ne pas confondre trace d’évaluation, preuve, synthèse et verbatim.

### D30 — Ajouter un sous-bloc “niveau réel observé” pour `generate-trace`

Les documents techniques de référence doivent inclure un rappel explicite : `generate-trace` est observé dans le réel, mais avec un payload actuellement minimal dans le local audité.

### D31 — Ajouter un sous-bloc “local vs distant” pour les endpoints d’évaluation

Les docs de contrat API ou d’audit doivent distinguer :
- ce qui est **confirmé localement** ;
- ce qui est **observé partiellement** ;
- et ce qui reste **A_VERIFIER sur Encoors**.

---

## 10. Formule de clôture documentaire pour ce domaine

Pour le domaine `70_evaluation_traces_preuves`, la documentation doit désormais adopter la ligne suivante :

- le domaine est **réellement présent** dans Hugo cœur ;
- la doctrine 2.0 garde **`EvaluationTrace`** comme objet conceptuel de référence ;
- le réel observé repose aujourd’hui sur un ensemble d’objets et workflows comprenant notamment `LearnerEvaluationRecord`, `Trace`, `TraceCriterionAssessment`, `Evidence`, `request-evaluation`, `finalize-evaluation`, `evaluation-readiness` et `generate-trace` ;
- le principal besoin documentaire n’est pas de réinventer le domaine, mais de **stabiliser le vocabulaire**, **clarifier les contrats**, **rendre visible la validation humaine** et **ne pas sur-promettre la richesse réelle des traces actuellement générées**.

# 03_backlog_actions — 70_evaluation_traces_preuves

- `DOMAINE_CODE = 70_evaluation_traces_preuves`
- `DOMAINE_LABEL = évaluation, traces et preuves`

---

## 1. Objet du backlog

Ce backlog limite les actions au seul domaine **évaluation / traces / preuves** de Hugo cœur.

Il ne présume pas d’une refonte générale du moteur. Il priorise d’abord :
- le recalage documentaire ;
- la clarification des contrats ;
- la réduction des ambiguïtés entre cible 2.0 et réel audité ;
- puis seulement les compléments backend additifs réellement utiles.

---

## 2. Principes de priorisation

Les priorités sont ordonnées selon quatre critères :
1. réduire le risque de mauvaise description du réel ;
2. stabiliser les contrats utiles à Hugo cœur ;
3. éviter les régressions doctrinales ;
4. repousser ce qui dépend d’un runtime distant ou d’une refonte prématurée.

Notation utilisée :
- `P0` : nécessaire immédiatement pour assainir le domaine
- `P1` : important pour stabiliser le chantier
- `P2` : utile mais après stabilisation documentaire et contractuelle
- `P3` : optionnel ou dépendant d’arbitrages ultérieurs

---

## 3. Actions P0

### A1 — Stabiliser le mapping documentaire `EvaluationTrace` ↔ objets réels

> **Statut (2026-06-16) :** **livré** — `mapping_EvaluationTrace_runtime_local.md` ; sections §9 (rapport) et matrice §1.1 mises à jour. Enrichissement runtime agrégé = hors périmètre.

**Type** : documentation structurante  
**Priorité** : `P0`

**Action**
- Ajouter, dans les docs 2.0 concernées, un tableau de mapping explicite entre :
  - `EvaluationTrace` (nom doctrinal)
  - `LearnerEvaluationRecord`
  - `Trace`
  - `TraceCriterionAssessment`
  - `Evidence`

**But**
- Réduire la principale ambiguïté de vocabulaire du domaine.
- Empêcher les futurs documents et prompts Cursor de parler d’un objet unique fictif déjà stabilisé.

**Livrable attendu**
- Sous-bloc “nom doctrinal / nom réel observé / statut de mapping / commentaire” dans la spec canonique ou dans une annexe dédiée du domaine.

### A2 — Recaler la doc sur le niveau réel de `generate-trace`

**Type** : documentation de vérité du réel  
**Priorité** : `P0`

**Action**
- Documenter explicitement que `generate-trace` existe dans le réel audité, mais que le payload observé localement reste minimal.
- Supprimer ou déclasser toute formulation laissant croire qu’une trace riche est déjà produite de bout en bout.

**But**
- Éviter la sur-promesse documentaire.
- Revenir à une photo du réel compatible avec les audits.

**Livrable attendu**
- Mention explicite “niveau réel observé” dans les docs de domaine et, si besoin, dans les annexes techniques.

### A3 — Distinguer noir sur blanc local audité vs runtime distant

**Type** : documentation d’audit / vérité  
**Priorité** : `P0`

**Action**
- Ajouter dans les documents du domaine un sous-bloc standard :
  - confirmé sur local audité ;
  - observé mais partiel ;
  - `A_VERIFIER` sur runtime distant Encoors.

**But**
- Empêcher les glissements “le local prouve la prod”.
- Assainir tous les futurs travaux sur endpoints et payloads d’évaluation.

**Livrable attendu**
- Encadré ou section récurrente “niveau de vérité” pour :
  - `request-evaluation`
  - `finalize-evaluation`
  - `evaluation-readiness`
  - `generate-trace`

### A4 — Déclasser les docs obsolètes sur les CTA synthèse / évaluation

**Type** : hygiène documentaire  
**Priorité** : `P0`

**Action**
- Marquer comme obsolètes les documents qui affirment encore que les boutons synthèse / évaluation ne sont pas branchés.
- Référencer le front local montrable comme vérité produit locale actuelle sur ce point.

**But**
- Éviter que des documents anciens recontaminent le cadrage du domaine.
- Protéger la cohérence entre audit produit et backlog CTO.

**Livrable attendu**
- Liste de documents à archiver, annoter ou réécrire pour ce sujet précis.

---

## 4. Actions P1

### A5 — Formaliser un contrat minimal des actions terminales d’évaluation

**Type** : contrat backend / produit  
**Priorité** : `P1`

**Action**
- Rédiger un contrat minimal, lisible produit, pour les actions terminales d’évaluation :
  - conditions d’éligibilité ;
  - cas de blocage ;
  - statut affichable ;
  - résultat attendu ;
  - dépendance à la validation humaine.

**But**
- Raccorder proprement doctrine 2.0, `UIState`, progression et endpoints réels.
- Éviter que le front ou les documents réinventent chacun leur propre logique.

**Livrable attendu**
- Mini-contrat quasi-JSON ou tableau d’API fonctionnelle pour :
  - `evaluation-readiness`
  - `request-evaluation`
  - `finalize-evaluation`

### A6 — Clarifier la distinction trace / preuve / synthèse / verbatim partagé

**Type** : clarification doctrine ↔ produit  
**Priorité** : `P1`

**Action**
- Produire un sous-document ou une section stable précisant la différence entre :
  - trace d’évaluation ;
  - trace métier ;
  - preuve ;
  - synthèse ;
  - verbatim partagé ou non partagé.

**But**
- Empêcher les confusions de circulation et de droits d’accès.
- Rendre le domaine exploitable côté produit, tuteur et exports.

**Livrable attendu**
- Tableau “objet / rôle / partageable / non partageable / validation humaine requise / exposition produit”.

### A7 — Ajouter les noms réels observés dans les matrices canoniques 2.0

**Type** : mise à jour documentaire transverse  
**Priorité** : `P1`

**Action**
- Enrichir les matrices 2.0 avec une colonne “nom réel observé” pour les objets du domaine :
  - `LearnerEvaluationRecord`
  - `Trace`
  - `TraceCriterionAssessment`
  - `Evidence`

**But**
- Réduire durablement les collisions entre doctrine et code.
- Améliorer les futurs prompts Cursor et les analyses d’écarts.

**Livrable attendu**
- Version révisée des matrices d’objets / services / endpoints du domaine.

### A8 — Bornage documentaire du rôle du tuteur dans l’évaluation

**Type** : clarification de rôle  
**Priorité** : `P1`

**Action**
- Documenter explicitement qu’en Hugo cœur 2.0 de référence :
  - le tuteur lit, commente, recommande ;
  - il peut intervenir sur certaines traces partageables selon le produit ;
  - il ne dispose pas par défaut d’un pouvoir générique de validation terminale des évaluations.

**But**
- Éviter l’ambiguïté entre Hugo cœur et extensions futures.
- Protéger la doctrine de validation humaine sans inventer une gouvernance non prouvée.

**Livrable attendu**
- Encadré de rôle dans la doc tuteur et rappel dans le domaine 70.

---

## 5. Actions P2

### A9 — Spécifier le format cible minimal d’`EvaluationTrace`

**Type** : contrat cible 2.0  
**Priorité** : `P2`

**Action**
- Définir un format cible minimal de l’`EvaluationTrace` sans attendre un schéma exhaustif :
  - identifiants ;
  - session ;
  - statut ;
  - date ;
  - rattachement éventuel à trace / preuve ;
  - niveau de partage ;
  - validation humaine requise ;
  - résumé lisible produit.

**But**
- Donner une cible suffisamment claire pour les futurs compléments backend.
- Éviter que chaque chantier réinterprète librement l’objet.

**Livrable attendu**
- Pseudo-schéma léger du domaine, orienté responsabilités et non ORM détaillé.

### A10 — Clarifier la conformité attendue des preuves

**Type** : contrat sécurité / preuve  
**Priorité** : `P2`

**Action**
- Détailler dans le domaine les exigences minimales applicables à `Evidence` :
  - contexte explicite obligatoire ;
  - pas d’objet preuve flottant ;
  - suppression EXIF par défaut ;
  - GPS opt-in ;
  - partage explicite ;
  - filtrage multi-tenant.

**But**
- Transformer un principe canonique en contrat documentaire directement testable.
- Préparer ensuite une vérification technique bornée.

**Livrable attendu**
- Checklist de conformité “preuves” pour code review et audit.

### A11 — Vérifier l’exposition réelle de la progression utile à l’évaluation

**Type** : audit ciblé  
**Priorité** : `P2`

**Action**
- Revoir précisément comment les signaux de progression et d’éligibilité à l’évaluation sont exposés aujourd’hui :
  - via `ui-state`
  - via un endpoint dédié
  - ou via d’autres projections.

**But**
- Lever l’ambiguïté actuelle entre doctrine “progress” et exposition observable réelle.
- Éviter d’écrire un contrat produit faux.

**Livrable attendu**
- Note d’audit courte : “projection de progression vers évaluation — réel observé”.

---

## 6. Actions P3

### A12 — Enrichir le payload réel de `generate-trace` si l’usage le justifie

**Type** : backend additif  
**Priorité** : `P3`

**Action**
- Étudier, seulement après stabilisation documentaire et contractuelle, l’enrichissement du payload produit par `generate-trace`.

**But**
- Passer d’une trace minimale à une trace plus utile, si cela apporte une vraie valeur produit ou tuteur.
- Ne pas commencer par coder sans contrat stabilisé.

**Livrable attendu**
- Proposition d’évolution additive du payload, bornée et compatible avec la doctrine.

### A13 — Préparer une vérification ciblée Encoors sur le domaine

**Type** : audit runtime distant  
**Priorité** : `P3`

**Action**
- Planifier un contrôle ciblé du runtime distant sur :
  - comportement des endpoints d’évaluation ;
  - cohérence des réponses ;
  - éventuels écarts de contrat ;
  - signaux de readiness.

**But**
- Fermer les `A_VERIFIER` les plus importants sans mélanger local et distant.

**Livrable attendu**
- Mini-compte rendu “local vs Encoors — évaluation / traces / preuves”.

---

## 7. Dépendances et ordre recommandé

### Séquence recommandée

1. `A1` — stabiliser le mapping vocabulaire
2. `A2` — recalage doc sur `generate-trace`
3. `A3` — formaliser local vs distant
4. `A4` — déclasser docs obsolètes sur CTA
5. `A5` — contrat minimal des actions terminales
6. `A6` — clarifier trace / preuve / synthèse / verbatim
7. `A7` — mise à jour des matrices 2.0
8. `A8` — bornage du rôle tuteur
9. `A9` à `A11` — contrats cibles et audits ciblés
10. `A12` à `A13` — enrichissements ou vérifications ultérieures

### Dépendances critiques

- `A5` dépend de `A1` et `A3`.
- `A7` dépend de `A1`.
- `A9` doit venir après `A1` et `A6`.
- `A12` ne doit pas démarrer avant `A2`, `A5` et `A9`.

---

## 8. Critères de clôture du domaine

Le backlog du domaine pourra être considéré comme correctement traité lorsque les conditions suivantes seront réunies :

- la documentation n’emploie plus `EvaluationTrace` sans préciser son raccord au réel ;
- `generate-trace` est décrit au bon niveau de vérité ;
- les endpoints d’évaluation sont clairement marqués local / distant / `A_VERIFIER` ;
- la distinction trace / preuve / synthèse / verbatim partagé est stabilisée ;
- le rôle du tuteur et la place de la validation humaine sont explicités sans ambiguïté ;
- un contrat minimal lisible des actions terminales existe côté documentation ;
- aucun document actif du domaine ne sur-vend une certification autonome ou une trace riche non prouvée.

---

## 9. Mise à jour cluster dev vague 2 encadrants (liens 70/100)

**Impact indirect sur le domaine 70 :**

| Lien | Changement | Statut |
|---|---|---|
| `Evidence` (preuves) | EXIF strip implémenté ; GPS meta opt-in | **RÉEL OBSERVÉ** local — voir ecarts-100 §8 |
| Export éval formateur | Inchangé — `shared_with_tutor=true` | **RÉEL OBSERVÉ** |
| Bundle Qualiopi | Toujours métadonnées traces — pas EvaluationTrace 2.0 | **Inchangé** |
| Mapping EvaluationTrace (D2-M05) | Doc seule — pas de nouveau agrégat runtime | **CIBLE** |

**A_VERIFIER :** prod Encoors sur exports/preuves liés aux traces.

---

## 10. Mise à jour cluster dev vague 3 — fin de fil / observabilité (réel local)

**Sources :** `cluster_dev_fin_de_fil_qualite_observabilite_vague3_resultats.md` · `evaluation_trace_pivot.py` · tests `test_evaluation_trace_minimal.py`.

| Point | Avant | Après cluster (RÉEL OBSERVÉ) |
|---|---|---|
| Agrégat EvaluationTrace doctrinal | Dispersion LearnerEvaluationRecord / Trace / Evidence | **Pivot JSON** `evaluation_trace_pivot_v1` — builder testé, non modèle unique |
| generate-trace | Payload squelette sans lien explicite record/preuves | **Enrichi** — pivot dans `payload_structured` + clé réponse |
| ExportRun JSON trace_rich_v1 | `payload_structured` seul | **+** `evaluation_trace_pivot_v1` par trace |
| Lecture encadrant | Traces / records séparés | Pivot exportable — **UI avancée toujours absente** |
| Certification autonome | Interdite | Disclaimer explicite dans pivot |
| EvaluationTrace 2.0 complète | CIBLE | **Toujours CIBLE** — pivot ≠ agrégat complet |

**Écarts confirmés restants :** critères/modalités vides dans generate-trace legacy ; validation humaine circuits parallèles ; prod Encoors **A_VÉRIFIER**.

---

## 11. Mise à jour cluster dev vague 4 — lien pivot / D9bis

| Lien | Statut |
|---|---|
| EvaluationTrace pivot (`evaluation_trace_pivot_v1`) | **Inchangé** — exports métier encadrants |
| D9bis session analytics | **Canal parallèle** — pas injecté dans pivot ni trace_rich_v1 |
| Enrichissement pivot avec scores LLM | **CIBLE Couronne** — non livré |

---

## 12. Mise à jour cluster audit vague 5 — chaîne EVAL1

| Étape | Statut local |
|---|---|
| CTA évaluation eligible | **ALIGNE** |
| request-evaluation → record | **ALIGNE** |
| generate-trace + pivot v1 | **ALIGNE** |
| Export JSON avec pivot | **ALIGNE** |
| Criteria generate-trace legacy | **PARTIEL** |
| Encoors chaîne complète | **A_VÉRIFIER** |

---

## 13. Mise à jour cluster 8 OPS — traces UI

| Point | Statut cluster 8 |
|---|---|
| Timeline traces visible navigateur tuteur | **ALIGNE** — Playwright SMOKE_TUTOR |
| Verbatim marker absent page | **ALIGNE** — share_verbatim=false |
| Encoors EVAL1 authentifié | **A_VÉRIFIER** |

---

## 14. Mise à jour cluster 11 — parité Encoors EVAL1

**Sources :** `cluster11_verrouillage_runtime_vs_encoors_resultats.md` · oracle Encoors étendu (EVAL1).

| Point | Statut cluster 11 |
|---|---|
| Chaîne EVAL1 local | **ALIGNE** — tests pivot PASS |
| Pivot v1 generate-trace / export | **ALIGNE** local |
| Encoors EVAL1 authentifié | **A_VÉRIFIER** — protocole oracle prêt |
| EvaluationTrace 2.0 complète | **COURONNE** |

---