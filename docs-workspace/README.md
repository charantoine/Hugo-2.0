# Documentation Hugo — guide du dossier `docs-workspace`

Ce README explique comment est organisée la bibliothèque documentaire du workspace Hugo, comment la lire sans se perdre, et comment la maintenir au fil des convergences entre le **Hugo réel** (code local audité) et la **cible Hugo 2.0** (doctrine et specs).


## Origine du code et crédits

### Références aux dépôts d’origine

## Origine et rôle de ce dépôt

Ce dépôt GitHub privé est hébergé sous le compte **[charantoine](https://github.com/charantoine)** et correspond au workspace local `Zone de travail Hugo` (`hugo-main/`, `hugo-hugolucia/`, `hugo_back/`, `docs-workspace/`).

Le socle applicatif utilisé comme point de départ provient de travaux de **Pierre Fardeau** (compte GitHub : [hamanad](https://github.com/Hamanad)), via des archives ZIP téléchargées les **11 et 12 juin 2026** à partir de ses dépôts :
- backend et noyau Hugo 1.9 : [Hamanad/hugo](https://github.com/Hamanad/hugo) (dossiers `hugo_back/` et `hugo-main`),
- PoC frontend `hugo-hugolucia` : [Hamanad/hugo_poc](https://github.com/Hamanad/hugo_poc) (dossier `hugo-hugolucia`).

Ce dépôt ne revendique pas la paternité du socle initial : il documente et versionne le **travail de convergence, d’audit et de transformation** réalisé ensuite en local (backend, frontend, documentation, tests) à partir de ces bases, en vue d’alimenter les décisions de convergence vers Hugo 2.0.

Les documents `Origine du code, provenance des sources et clarification de contribution.md` et `docs-workspace/README.md` détaillent la traçabilité et la répartition de responsabilité entre le socle de Pierre Fardeau et les contributions réalisées dans ce dépôt.Les versions utilisées dans ce dépôt proviennent de ZIP téléchargés entre le 11 et le 12 juin 2026 depuis son dépôt privé, puis utilisées comme base de travail **en local** sur Mac.  
Le travail présent dans ce dépôt correspond ensuite à des développements, transformations, audits, tests et documents produits localement, puis **déposés sur GitHub le 19 juin 2026**.

Afin de lever toute ambiguïté de propriété :
- le **socle initial** reste attribué à **Pierre Fardeau** ;
- les **modifications et développements ultérieurs** présents dans ce dépôt correspondent au travail réalisé à partir de cette base ;
- ce dépôt ne prétend pas requalifier la paternité du code de départ, mais documenter clairement l’origine du socle et l’état du travail partagé.

Les archives ZIP utilisées comme base de travail ont été **conservées à la racine de ce dépôt** comme traces explicites du point de départ utilisé les **11 et 12 juin 2026**.

---

## 1. Objet du dossier `docs-workspace`

Le dossier `docs-workspace` est la **bibliothèque de convergence** du projet Hugo. Il ne remplace pas la doc marketing ni les specs produit isolées : il sert à **décrire juste** ce qui existe, ce qui est visé, et ce qui manque encore, avec des preuves traçables (code, tests, audits).

En pratique, ce dossier :

- recense l’**état réel** du moteur et du produit montrable (`hugo_back`, `frontend_1.8`) ;
- fixe la **doctrine cible** Hugo 2.0 sans la confondre avec le livré ;
- documente les **écarts par domaine** (mémoire, RAG, interfaces, exports, etc.) ;
- enregistre les **campagnes de tests**, oracles par persona et résultats de clusters ;
- fournit des **templates Cursor** pour auditer ou converger proprement.

Tout nouveau lecteur (CTO, dev, produit) doit partir d’ici avant d’ouvrir une spec ancienne ou un fil de discussion isolé.

---

## 2. Comment est organisée la documentation

La bibliothèque se découpe en cinq blocs complémentaires. Le tableau ci-dessous indique le rôle de chaque bloc et le moment où le consulter.

| Bloc | Fichiers typiques | Rôle | Quand le lire |
|------|-------------------|------|---------------|
| **Socle historique 00–10** | `00_HIERARCHIE…`, `01`–`03`, `05`–`10`, `04_INDEX…` | Règles de vérité, cartographie du workspace, état moteur/produit, écarts doc/code, démo et Encoors | **Toujours en premier** pour savoir quelle source fait foi |
| **Doctrine et specs 2.0** | `spec_canonique_hugo_2_0.md`, `specs interface 2.0.md`, `complements_spec_2_0…`, specs orchestrateurs/formateur/tuteur | Cible consolidée : architecture, UIState, postures, mémoire, encadrants | Après le socle — pour la **cible**, jamais comme preuve de livraison |
| **Écarts et matrices** | `ecarts — <domaine>.md`, `cluster2_matrice_runtime_vs_cible.md`, `synthese_globale_ecarts…`, backlogs `D2-Mxx` | Raccord réel ↔ cible par domaine ; priorités documentaires | Pour un chantier précis ou une revue CTO |
| **Tests et oracles** | `cluster2_oracles…`, `cluster3_validation…`, `cluster15_*`, `protocole_tests_*`, `rapport_mise_a_jour_doc_post_tests_*` | Preuves automatisées et check-lists manuelles | Avant d’affirmer « livré » ou « validé en prod » |
| **Outillage Cursor** | `30/70/20_cursorops_templates.md`, `cluster2_prompts_audit…`, templates d’audit mémoire/RAG | Prompts reproductibles pour audits et mises à jour doc | Quand on lance un audit ou un nouveau cluster |

### 2.1 Socle historique (00–10)

| Fichier | Contenu |
|---------|---------|
| `00_HIERARCHIE_DOCUMENTAIRE.md` | Ordre de priorité des sources (code > tests > front > docs) |
| `01_CARTOGRAPHIE_WORKSPACE_REEL.md` | Où est le code, quels dossiers font foi |
| `02_ETAT_MOTEUR_REEL.md` | Services, modèles, endpoints backend observables |
| `03_ETAT_PRODUIT_REEL.md` | Surfaces front prod (`/app*`), composants, flux UI |
| `04_INDEX_DOCUMENTAIRE_QUALIFIE.md` | Index qualifié de toute la doc du workspace (hors venv) |
| `05_ECARTS_DOC_CODE_PRODUIT.md` | Divergences doc ↔ code ↔ produit (vue transversale) |
| `06_PREPARATION_CIBLE_1_9.md` | Garde-fous vers une cible proche (ne pas sur-lire comme livré) |
| `07_RUNTIME_DEMO_REFERENCE.md` | Baselines de démo locale |
| `08_FLAGS_ET_ENVIRONNEMENT_DEMO.md` | Variables d’environnement et flags de démo |
| `09_PARCOURS_DEMO_ET_SCENARIOS.md` | Scénarios montrables sans sur-vendre |
| `10_FICHE_RUNTIME_PROD_ENCOORS.md` | Photo du runtime distant (à croiser avec prudence) |

### 2.2 Doctrine et specs 2.0

| Fichier | Contenu |
|---------|---------|
| `spec_canonique_hugo_2_0.md` | Porte d’entrée doctrinale Hugo cœur |
| `specs interface 2.0.md` | Interfaces apprenant, tuteur, formateur (UX cible) |
| `complements_spec_2_0_depuis_anterieurs.md` | Compléments issus des versions antérieures |
| `specs Orchestrateur diagnostic 2.0.md` | Régime diagnostic (cible) |
| `specs formateur + tuteur 2.0.md` | Orchestrateurs encadrants (cible) |
| `glossaire_alignement_hugo_reel_vs_spec.md` | Pont de vocabulaire réel ↔ spec (**pas une preuve**) |

### 2.3 Écarts par domaine

Chaque domaine structurant possède un rapport `ecarts — <intitulé>.md` :

| Code | Fichier | Thème |
|------|---------|-------|
| 10 | `ecarts —10_runtime_p0_progression_uistate.md` | P0, progression, UIState |
| 20 | `ecarts — 20_memoire_gouvernee.md` | Mémoire gouvernée intra-conversation |
| 30 | `ecarts — 30_referentiel_documentaire_rag.md` | RAG lexical, référentiel documentaire |
| 31 | `ecarts — 31_front_apprenant_postures_et_bascule.md` | Front apprenant, postures, bascule |
| 40 | `ecarts — 40_base_connaissances_formateur.md` | TrainerKnowledgeItem, base formateur |
| 50 | `ecarts — 50_orchestrateur_formateur.md` | Orchestrateur formateur |
| 60 | `ecarts — 60_orchestrateur_tuteur.md` | Orchestrateur tuteur |
| 70 | `ecarts — 70_evaluation_traces_preuves.md` | Évaluation, traces, preuves |
| 80 | `ecarts — 80_observabilite_qualite_conversationnelle.md` | Observabilité, qualité conversationnelle |
| 90 | `ecarts — 90_confidentialite_partage_multitenant_roles.md` | Confidentialité, rôles, multi-tenant |
| 100 | `ecarts — 100_exports_preuves_qualiopi_lite.md` | Exports, bundles Qualiopi lite |
| 110 | `ecarts — 110_interfaces_formateur_tuteur.md` | Interfaces tuteur et formateur |
| 120 | `ecarts — 120_intercalaires_v1.md` | Intercalaires pédagogiques V1 (couronne) |

Vue transversale : `cluster2_matrice_runtime_vs_cible.md` (matrice **V5**), `synthese_globale_ecarts_par_domaine.md`, `plan_documentation_cto_convergence_hugo.md`.

Méthode obligatoire : `DOC_METHODO_REFERENCE_CONVERGENCE_HUGO_REVISE.md`.

### 2.4 Tests, oracles et garde-fous

| Fichier | Contenu |
|---------|---------|
| `plan_tests_global_hugo.md` | Cartographie pytest / Playwright / Encoors par domaine et persona (**à jour C16**) |
| `cluster2_oracles_test_par_persona.md` | Catalogue d’oracles par persona (A1, B1, C1…) |
| `cluster3_validation_courte_personae.md` | Validation opérationnelle 8 oracles prioritaires |
| `cluster15_interfaces_apprenant_formateur_resultats.md` | Livrables cluster 15 (posture, mémoire, formateur) |
| `cluster16_interface_apprenant_spec_conformite_resultats.md` | Polish apprenant spec 2.0 (cluster 16) |
| `cluster16_interface_apprenant_resultats_tests.md` | Campagne tests C16 (15+10 PASS) |
| `rapport_mise_a_jour_doc_post_cluster16_2026-06-18.md` | Passe doc transversale post-C16 |
| `protocole_tests_interfaces_apprenant_formateur_v1.md` | Protocole + check-lists UI manuelles (C15, apprenant + formateur) |
| `cluster16_protocole_tests_interface_apprenant_v1.md` | Protocole tests interface apprenant C16 (B16-*, U16-*) |
| `rapport_mise_a_jour_doc_post_tests_2026-06-18.md` | Synthèse post-campagne pytest (90 tests PASS local) |
| `REFERENCE_CONVERGENCE_HUGO_REEL_VS_2_0_GARDEFOU.md` | Garde-fou de convergence (à relire avant toute promo « livré ») |
| `handover_hugo_reel_vs_2_0.md` | Handover synthétique réel / cible / couronne |

Personae : `Bibliothèque canonique de personae Hugo 2.0.md`.

### 2.5 Outillage Cursor

| Fichier | Contenu |
|---------|---------|
| `cluster2_prompts_audit_runtime_et_memoire.md` | Boîte à outils prompts d’audit (runtime, mémoire, exports) |
| `30_cursorops_templates.md` | Templates domaine 30 (RAG / référentiel) |
| `70_cursorops_templates.md` | Templates domaine 70 (évaluation / traces) |
| `20_cursorops_templates.md` | Templates domaine 20 (mémoire) |
| `template_prompt_audit_memoire_intra_conversation.md` | Audit mémoire intra-conversation |

---

## 3. Parcours de lecture conseillé

### 3.1 CTO / lead dev

Ordre recommandé :

1. **`00_HIERARCHIE_DOCUMENTAIRE.md`** — Règles de vérité et pièges connus (backend vide dans les monorepos, Encoors ≠ local).
2. **`DOC_METHODO_REFERENCE_CONVERGENCE_HUGO_REVISE.md`** — Patron de travail : réel / cible / écarts / A_VÉRIFIER.
3. **`cluster2_matrice_runtime_vs_cible.md`** — Vue V5 des 13 domaines et backlog `D2-Mxx`.
4. **`synthese_globale_ecarts_par_domaine.md`** — Synthèse exécutable par domaine.
5. **`plan_documentation_cto_convergence_hugo.md`** — Trajectoire Vagues 1–3 + couronne.
6. **`REFERENCE_CONVERGENCE_HUGO_REEL_VS_2_0_GARDEFOU.md`** — Ce qu’on a le droit d’affirmer en prod.
7. **`rapport_mise_a_jour_doc_post_tests_2026-06-18.md`** — Dernière campagne de tests et promotions documentaires.
8. **`02_ETAT_MOTEUR_REEL.md`** puis **`03_ETAT_PRODUIT_REEL.md`** — Ancrage code et surfaces.

### 3.2 Produit / pédagogie

Ordre recommandé :

1. **`spec_canonique_hugo_2_0.md`** — Vision cible (lire les bandeaux de statut runtime en tête de sections).
2. **`specs interface 2.0.md`** — Grammaires UX apprenant et encadrants.
3. **`09_PARCOURS_DEMO_ET_SCENARIOS.md`** — Ce qui est montrable en démo aujourd’hui.
4. **`03_ETAT_PRODUIT_REEL.md`** — Surfaces réelles `/app*`.
5. **`Bibliothèque canonique de personae Hugo 2.0.md`** — Personae et scénarios métier.
6. **`ecarts — 110_interfaces_formateur_tuteur.md`** — Écarts interfaces tuteur/formateur.
7. **`ecarts — 31_front_apprenant_postures_et_bascule.md`** — Postures et profils d’affichage côté apprenant.
8. **`cluster15_interfaces_apprenant_formateur_resultats.md`** — Dernier lot livré local (posture, mémoire, formateur).

### 3.3 Dev arrivant sur le projet

Ordre recommandé :

1. **`README.md`** (ce fichier).
2. **`01_CARTOGRAPHIE_WORKSPACE_REEL.md`** — Où coder (`hugo_back`, `frontend_1.8`).
3. **`02_ETAT_MOTEUR_REEL.md`** — Services et endpoints à connaître.
4. **`glossaire_alignement_hugo_reel_vs_spec.md`** — Vocabulaire sans confusion de noms.
5. **Domaine concerné** — ex. `ecarts — 20_memoire_gouvernee.md` + note de lot `20_memoire_gouvernee_note_lot_courant…`.
6. **Tests** — ex. `test_cluster15_interfaces_apprenant.py` pour interfaces apprenant.
7. **`cluster2_prompts_audit_runtime_et_memoire.md`** — Si audit ou PR de convergence.
8. **`08_FLAGS_ET_ENVIRONNEMENT_DEMO.md`** — Avant de lancer une démo locale.

**Exemple fil directeur — mémoire gouvernée (20)** : socle `00` → spec § mémoire → `ecarts — 20` → `contrat_api_memory_summary_v1.md` → tests `test_session_memory_contract.py` → code `session_memory.py`.

**Exemple fil directeur — interfaces formateur (110)** : `ecarts — 110` → cluster 15 résultats → `protocole_tests_interfaces…` → `ProdTrainerKnowledgeView.vue` + `views_trainer.py`.

---

## 4. Niveaux de vérité et statuts

La doc Hugo utilise deux familles de statuts. Les confondre est l’erreur la plus fréquente.

### 4.1 Niveaux de vérité (contenu / runtime)

| Statut | Signification | En prod / démo, on peut dire… |
|--------|---------------|-------------------------------|
| **IMPLÉMENTÉ** | Vérifiable dans le code local + tests | « Existe dans notre runtime local audité » (pas « partout en prod » sans Encoors) |
| **CRÉDIBLE** | Cohérent avec le code, preuve partielle | « Probablement là, à confirmer par test ciblé » |
| **PARTIEL** | Couverture incomplète | « Une première brique existe ; le workflow complet non » |
| **CIBLE** | Spec 2.0 uniquement | « Visé par la doctrine ; non prouvé livré » |
| **AMBIGU** | Versions coexistants non arbitrées | « Ne pas trancher sans audit » (ex. P0 legacy vs v17) |
| **A_VÉRIFIER** | Dépend prod, flags, RLS, UI non rejouée | « À valider sur Encoors / environnement cible » |
| **ARCHIVE** | Doc datée ou remplacée | Ne pas utiliser pour décider |

### 4.2 Statuts documentaires (alignement doc ↔ réel)

| Statut | Signification |
|--------|---------------|
| **ALIGNE** | Réel et cible raccordés et documentés |
| **ALIGNE_DOC_PARTIEL** | Fond OK ; doc ou nommage à compléter |
| **PARTIEL** | Couverture incomplète côté produit ou doc |
| **ABSENT_NOUVEAU_CONTRAT** | Cible identifiée ; contrat minimal à rédiger |
| **RENOMMER_DANS_DOC** | Pont glossaire à formaliser |
| **A_VÉRIFIER** | Preuve insuffisante |

### 4.3 Règles d’usage en réunion ou en spec produit

- **IMPLÉMENTÉ + test PASS local** → OK pour démo locale et PR ; marquer **A_VÉRIFIER** si Encoors non rejoué.
- **CIBLE** → toujours formulé au futur ou « cible 2.0 » ; jamais « Hugo fait déjà ».
- **Glossaire** → aligne les mots ; ne remplace jamais un grep ou un pytest.
- **Front seul** → ne prouve pas une règle moteur ; repartir de `hugo_back` et UIState.

Patron minimal pour toute note ou commentaire :

- Sources mobilisées  
- Réel confirmé  
- Cible 2.0  
- Écarts  
- A_VÉRIFIER  
- Prochaine sortie utile  

---

## 5. Lire un domaine donné — recette type

Pour comprendre un domaine (ex. 20, 70, 90, 110, 120), appliquer la même séquence :

| Étape | Action | Fichiers |
|-------|--------|----------|
| 1 | Cadre méthodo | `DOC_METHODO…`, `00_HIERARCHIE…` |
| 2 | Cible doctrinale | `spec_canonique_hugo_2_0.md` (+ spec interface si UX) |
| 3 | Réel observé | `02` / `03` + grep code `hugo_back` |
| 4 | Rapport d’écarts | `ecarts — <domaine>.md` (bandeau post-tests en tête si présent) |
| 5 | Matrice | Ligne domaine dans `cluster2_matrice_runtime_vs_cible.md` |
| 6 | Synthèse | `synthese_globale_ecarts_par_domaine.md` § domaine |
| 7 | Preuves | Tests pytest listés dans le rapport d’écarts ou `rapport_mise_a_jour_doc_post_tests_*` |
| 8 | Backlog | Entrées `D2-Mxx` dans la matrice cluster 2 |

### Exemples rapides

| Domaine | Question type | Fichiers clés |
|---------|---------------|---------------|
| **20** Mémoire | « Que voit l’apprenant ? » | `ecarts — 20`, `contrat_api_memory_summary_v1.md`, `test_memory_summary_smoke.py`, cluster 15 |
| **30** RAG | « Le RAG vectoriel est-il actif ? » | `ecarts — 30`, `test_rag_support_tracing.py` — lexical oui, vectoriel CIBLE |
| **70** Évaluation | « Qui déclenche l’évaluation ? » | `ecarts — 70`, `mapping_EvaluationTrace_runtime_local.md`, `test_request_evaluation_guard.py` |
| **90** Confidentialité | « Le tuteur voit-il le verbatim ? » | `ecarts — 90`, `test_cluster3_oracles.py` (B1-01), `matrice_role_visibilite_v2.md` |
| **110** Interfaces | « Où en est l’apprenant / formateur ? » | `ecarts — 110`, clusters 15–16, `protocole_tests_interfaces…`, `cluster16_protocole_tests…` |
| **120** Intercalaires | « Est-ce codé ? » | `ecarts — 120`, `audit_domaine_120…` — domaine CIBLE, 0 implémentation locale |

---

## 6. Clusters et versions

Un **cluster** est un **lot de convergence** documenté de bout en bout : audit → écarts → code/tests → rapport de résultats → mise à jour matrice et écarts. Ce n’est pas une version produit ; c’est un **paquet de travail** traçable.

| Cluster | Périmètre principal | Fichiers de résultats |
|---------|---------------------|------------------------|
| **Cluster 2** | Matrice 13 domaines, oracles, prompts d’audit | `cluster2_matrice…`, `cluster2_oracles…`, `cluster2_prompts…` |
| **Cluster 3 court** | 8 oracles prioritaires (A1, B1, D1) | `cluster3_validation_courte_personae.md` |
| **Clusters 4–14** | UIState, profils, RAG, encadrants, observabilité… | `cluster4_*` … `cluster14_*`, Retex associés |
| **Cluster 15** | Interfaces apprenant + formateur (posture, mémoire, trainer) | `cluster15_interfaces…`, `protocole_tests_interfaces…` |
| **Cluster 16** | Interface apprenant spec 2.0 (polish UX, E2E profils) | `cluster16_protocole_tests…`, `cluster16_interface_apprenant_*`, `rapport_mise_a_jour_doc_post_cluster16_2026-06-18.md` |
| **Post-tests 2026-06-18** | Mise à jour doc après campagne pytest C15 | `rapport_mise_a_jour_doc_post_tests_2026-06-18.md` |

Un futur **cluster 2.1** (ou cluster 16+) s’accroche ainsi :

1. Choisir le domaine et les personae (`Bibliothèque canonique…`).
2. Mettre à jour ou créer les tests pytest (`test_cluster<N>_…`).
3. Produire un `cluster<N>_<theme>_resultats.md`.
4. Mettre à jour la matrice **V5+** et le bandeau du `ecarts — <domaine>.md`.
5. Ajouter une entrée dans `rapport_mise_a_jour_doc_post_tests_<date>.md` ou `rapport_mise_a_jour_doc_post_cluster<N>_<date>.md`.
6. Cocher les oracles dans `cluster2_oracles_test_par_persona.md`.

Les dossiers **`cluster<N>_…_plan_resultats.md`** et **`cluster_dev_*`** documentent le détail des vagues antérieures ; la matrice cluster 2 reste la **carte de navigation** la plus à jour.

---

## 7. Comment maintenir la documentation

### 7.1 Créer un nouveau fichier ou enrichir l’existant ?

| Situation | Action |
|-----------|--------|
| Nouveau **domaine** structurant | Créer `ecarts — <code>_<intitulé>.md` + ligne dans la matrice cluster 2 |
| Nouveau **lot de convergence** | Créer `cluster<N>_<theme>_resultats.md` ; ne pas dupliquer toute la matrice |
| **Contrat API** stable | Fichier dédié (`contrat_api_*.md`, `fiche_*_pivot_v1.md`) + lien depuis l’écart domaine |
| **Campagne de tests** | `rapport_mise_a_jour_doc_post_tests_<YYYY-MM-DD>.md` + bandeau en tête des écarts touchés |
| **Prompt Cursor réutilisable** | `*_cursorops_templates.md` ou section dans `cluster2_prompts…` |
| Correction ponctuelle | Enrichir l’écart domaine existant ; éviter un troisième rapport parallèle |

### 7.2 Renseigner un nouvel écart de domaine

Structure minimale d’un `ecarts — <domaine>.md` :

1. Bandeau **Mise à jour post-tests** (date, preuves, statut).
2. Périmètre et sources mobilisées.
3. Photo du **réel observé** (code, tests).
4. **Cible 2.0** (spec, sans la présenter comme livrée).
5. Matrice d’écarts (objet / cible / réel / statut / action).
6. Backlog **DOC / CODE / OPS** court.

Toujours séparer réel, cible, écarts confirmés, A_VÉRIFIER.

### 7.3 Ajouter un résultat de campagne de tests

1. Exécuter pytest (commande consignée dans le protocole ou le rapport cluster).
2. Créer ou mettre à jour `rapport_mise_a_jour_doc_post_tests_<date>.md`.
3. Promouvoir un statut **uniquement** si code + test + rapport cluster convergent.
4. Mettre à jour `cluster2_matrice_runtime_vs_cible.md` (version incrémentée).
5. Ajouter §19 ou équivalent dans `cluster2_oracles_test_par_persona.md` si nouveaux oracles validés.

### 7.4 Nommer les prompts Cursor

- Audits transverses : `cluster2_prompts_audit_<theme>.md`
- Templates par domaine : `<code>_cursorops_templates.md` (ex. `20_cursorops_templates.md`)
- Audits ponctuels : `template_prompt_audit_<sujet>.md`
- Protocoles de test : `protocole_tests_<surface>_v<N>.md`

Éviter les noms génériques (`notes.md`, `temp_audit.md`) à la racine de `docs-workspace`.

### 7.5 Fichiers à ne pas modifier sans garde-fou

- **`spec_canonique_hugo_2_0.md`** : doctrine de fond ; ajouter des **bandeaux de statut runtime**, pas de refonte métier dans un fil de convergence.
- **`00_HIERARCHIE_DOCUMENTAIRE.md`** : changer uniquement si la hiérarchie des sources change réellement.
- **`REFERENCE_CONVERGENCE…_GARDEFOU.md`** : tenir à jour après chaque vague majeure.

---

## 8. Liens utiles hors `docs-workspace`

| Emplacement | Rôle |
|-------------|------|
| `hugo_back/apps/hugo/` | Moteur Django — source de vérité comportementale |
| `hugo_back/apps/hugo/tests/` | Preuves automatisées |
| `hugo-hugolucia/frontend_1.8/` | Front prod de référence (`/app*`) |
| `hugo-hugolucia/frontend_1.8/tests_playwright/` | E2E Playwright |
| `.cursorrules` (racine workspace) | Règles Cursor pour ce projet |

---

## Historique des mises à jour du README

| Date | Auteur / rôle | Résumé |
|------|---------------|--------|
| 2026-06-18 | conv-hugo-doc | Création du README : organisation 00–10 / specs / écarts / clusters / Cursor, parcours CTO-produit-dev, niveaux de vérité, recette par domaine, maintenance post-cluster 15 et campagne pytest 90 PASS. |
