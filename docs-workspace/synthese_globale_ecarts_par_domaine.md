# Synthèse globale des écarts par domaine — Hugo 2.0 (runtime local)

**Workspace :** `/Users/machin/Desktop/Zone de travail Hugo`  
**Date :** 2026-06-18  
**Périmètre :** runtime **local** uniquement (`hugo_back` + `hugo-hugolucia/frontend_1.8` + `docs-workspace`)  
**Sources principales :** `cluster2_matrice_runtime_vs_cible.md`, écarts domaines 10–120, designs D2‑M06/M07/M08/M11, Retex clusters 1–7

---

## 0. Périmètre et posture

Cette synthèse couvre les domaines structurants **10, 20, 30, 31, 40, 50, 60, 70, 80, 90, 100, 110, 120** sur le **runtime local** audité. Elle ne déduit pas le comportement de `hugoback.encoors.com`, de la RLS Postgres prod, ni des flags non relus localement : ces points restent **A_VÉRIFIER** sauf mention contraire.

La lecture suit la hiérarchie documentaire Hugo : **code + tests** pour le réel, **spec 2.0** pour la cible, **écarts par domaine** pour le raccord, glossaire comme pont de vocabulaire uniquement.

### Légende

| Tag | Signification |
|-----|---------------|
| **CIBLE** | État visé Hugo 2.0 |
| **RÉEL OBSERVÉ** | Code, tests ou audits locaux vérifiables |
| **ÉCART CONFIRMÉ** | Divergence recoupée et documentée |
| **A_VÉRIFIER** | Dépend prod, RLS, Encoors, flags, UI non rejouée |
| **HYPOTHÈSE** | Recommandation de replay / choix, non prouvée |

### Statuts documentaires (colonnes « état de convergence »)

| Statut | Signification |
|--------|---------------|
| **IMPLÉMENTÉ** | Vérifiable code local + tests |
| **CREDIBLE** | Cohérent code/docs, preuve partielle |
| **PARTIEL** | Couverture incomplète |
| **ABSENT_NOUVEAU_CONTRAT** | Cible identifiée, contrat à produire |
| **A_VÉRIFIER** | Preuve insuffisante (prod, flags, variante) |

---

## 1. Synthèse par domaine

### 1.1 Domaine 10 — runtime / P0 / progression / UIState

#### Photo rapide

Noyau conversationnel backend : chaîne `build_hugo_turn` (contexte → posture → P0 → décision → plan/RAG → mémoire session → progression → UIState → prompt). P0 et `ConversationProgress` sont opérationnels ; le front prod consomme `GET .../ui-state/` sans exposer TurnState ni champs P0 bruts. Double stack documentée : `build_ui_state` (engagement) vs `build_contract_ui_state` (produit). Cluster 4 a livré `conversation_mode` et `learner_display_profile` dans le contrat UIState.

#### Tableau « état de convergence »

| Sous-domaine / sujet | Statut documentaire | Tag principal | Commentaire court | Référence |
|----------------------|---------------------|---------------|-------------------|-----------|
| P0 + TurnState + décision | IMPLÉMENTÉ | RÉEL OBSERVÉ | Classifieur, analyse tour, `ConversationDecision` opérationnels | `ecarts —10_runtime_p0_progression_uistate.md` |
| ConversationProgress (branches, maturité) | IMPLÉMENTÉ | RÉEL OBSERVÉ | Calculator + éligibilité synthèse/éval branchés CTA | `cluster2_matrice_runtime_vs_cible.md` §1.3 |
| UIState produit + CTA synthèse/éval | IMPLÉMENTÉ | RÉEL OBSERVÉ | `cta_ui_state.py`, tests cluster 1 | `10_runtime_p0_progression_uistate_note_lot_courant_cta_synthese_evaluation.md` |
| `conversation_mode` dans UIState | IMPLÉMENTÉ | RÉEL OBSERVÉ | D2‑M01 livré C4 ; bandeau front lecture seule | `cluster4_surface_contracts.md` |
| `learner_display_profile` (contrat API) | IMPLÉMENTÉ | RÉEL OBSERVÉ | Enum + cascade groupe/org ; rendu front partiel | `design_D2-M07_D2-M08_profils_grammaires_matrice_roles.md` |
| Double builder UIState | PARTIEL | ÉCART CONFIRMÉ | Engagement vs contrat : risque confusion doc | `cluster2_matrice_runtime_vs_cible.md` §12.4 |
| TurnState v17 / flag `HUGO_P0_V17_ENABLED` | A_VÉRIFIER | A_VÉRIFIER | Coexistence legacy/v17 non auditée prod | D2‑M10 |
| CTA × posture (libellés variables) | ABSENT_NOUVEAU_CONTRAT | CIBLE | Libellés identiques toutes postures aujourd’hui | `cluster2_matrice_runtime_vs_cible.md` §1.5 |
| Sélecteur posture front + `set-posture` | ABSENT_NOUVEAU_CONTRAT | CIBLE | API backend OK ; UI interactive absente (G2‑02) | `ecarts — 31_front_apprenant_postures_et_bascule.md` |
| Tableau posture → RAG → maturité → CTA | PARTIEL | CIBLE | Code explicite ; doc D2‑M02 non finalisée | D2‑M02 |

#### Points convergés

- Pipeline orchestrateur backend-first avec P0, progression, UIState et CTA testés (`test_p0_non_regression.py`, `test_cta_*`, `test_cluster4_surface_contracts.py`).
- Progression par branches/maturité alignée doctrine ; éligibilité synthèse/évaluation calculée côté serveur.
- `conversation_mode` et `learner_display_profile` exposés dans UIState sans fuite P0.
- Parcours `/app` prod montrable : chat, ui-state, CTA terminales, badges RAG « Appui ».

#### Points encore ouverts

- Formalisation doc : `DecisionContract` ↔ `ConversationDecision`, mapping services réels (D2‑M02, D2‑M03).
- Flag v17 et convergence décision unique (D2‑M10) — **A_VÉRIFIER** prod.
- Sélecteur posture interactif et messages CTA par posture — **CIBLE**.
- Déprécation ou documentation explicite du double stack UIState engagement/contrat.

---

### 1.2 Domaine 20 — mémoire gouvernée intra-conversation

#### Photo rapide

Lot courant = **mémoire intra-conversation** uniquement (`SessionMemoryContract`, `build_session_memory`). Endpoint `memory-summary` expose une projection (session + thème inter-session). `LearnerThemeMemory` et `MemoryConsolidator` existent en stockage mais ne sont pas prouvés injectés dans `build_hugo_turn`. Pas d'injection `session_memory` dans `prompt_renderer` (intention lot 1).

#### Tableau « état de convergence »

| Sous-domaine / sujet | Statut documentaire | Tag principal | Commentaire court | Référence |
|----------------------|---------------------|---------------|-------------------|-----------|
| `SessionMemoryContract` + tests | IMPLÉMENTÉ | RÉEL OBSERVÉ | Contrat intra-conv, `memory_scope` testé | `ecarts — 20_memoire_gouvernee.md` |
| `GET .../memory-summary/` | IMPLÉMENTÉ | RÉEL OBSERVÉ | Projection API ; schéma plat vs nested ouvert | D2‑M04 |
| Mémoire dans UIState engagement | PARTIEL | RÉEL OBSERVÉ | Dict `session_memory` ; prod n'affiche pas | `cluster2_matrice_runtime_vs_cible.md` §2 |
| Injection prompt LLM | PARTIEL | ÉCART CONFIRMÉ | Absence vérifiée ; décision doc à figer | `ecarts — 20_memoire_gouvernee.md` §3.2 |
| `LearnerThemeMemory` au tour | PARTIEL | CIBLE | Stockage oui ; injection tour non prouvée | `ecarts — 20_memoire_gouvernee.md` §4.2 |
| Mémoire dans UIState contrat prod | ABSENT_NOUVEAU_CONTRAT | CIBLE | Pas de résumé gouverné dans `build_contract_ui_state` | D2‑M04 |
| Front prod consommant memory-summary | A_VÉRIFIER | A_VÉRIFIER | Pas de preuve panneau mémoire apprenant | `ecarts — 20_memoire_gouvernee.md` §7 |

#### Points convergés

- Service `session_memory.py` + contrat JSON minimal intra-conversation documenté et testé.
- Garde-fou : pas de verbatim brut dans la projection mémoire gouvernée.
- Distinction explicite intra-conversation vs inter-sessions dans la doc de domaine.

#### Points encore ouverts

- Canonisation schéma `memory-summary` (plat vs nested cible) — D2‑M04.
- Décision documentaire figée : injection prompt hors périmètre lot courant ou chantier futur.
- Projection mémoire dans UIState contrat produit.
- Audit injection réelle `LearnerThemeMemory` — **A_VÉRIFIER**.

---

### 1.3 Domaine 30 — référentiel documentaire / RAG

#### Photo rapide

Socle réel : apps `referentials`, `library`, `TrainerKnowledgeItem`, sélection RAG lexicale (`rag_support.py`) dans le pipeline post-décision. Citations produit via `rag_citations` et badge « Appui ». RAG vectoriel (pgvector) **inactif** en runtime. Hiérarchie contexte 2.0 (état → mémoire → verbatim → référentiel → RAG) pas encore contractualisée bout en bout.

#### Tableau « état de convergence »

| Sous-domaine / sujet | Statut documentaire | Tag principal | Commentaire court | Référence |
|----------------------|---------------------|---------------|-------------------|-----------|
| Référentiel métier (`referentials`) | IMPLÉMENTÉ | RÉEL OBSERVÉ | Import, structure compétences | `ecarts — 30_referentiel_documentaire_RAG.md` |
| Bibliothèque + indexation chunks | IMPLÉMENTÉ | RÉEL OBSERVÉ | Upload, chunking lexical | idem §4.1 |
| RAG lexical runtime | IMPLÉMENTÉ | RÉEL OBSERVÉ | `select_rag_chunks`, gating par posture | `cluster2_matrice_runtime_vs_cible.md` §3 |
| RAG vectoriel | ABSENT_NOUVEAU_CONTRAT | CIBLE | pgvector présent, non exploité | **ÉCART CONFIRMÉ** |
| Citations produit apprenant | IMPLÉMENTÉ | RÉEL OBSERVÉ | Badge « Appui », pas panneau RAG | `03_ETAT_PRODUIT_REEL` |
| Hiérarchie récupération contexte | PARTIEL | CIBLE | Ordre doctrinal non formalisé comme contrat unique | `ecarts — 30` matrice |
| RAG dans UIState prod | PARTIEL | ÉCART CONFIRMÉ | Absent contrat ; `supporting_documents` engagement seulement | `cluster2` §1.5 |
| `TrainerKnowledgeItem` → RAG apprenant | PARTIEL | A_VÉRIFIER | Présence nominale ; consommation runtime à auditer | V3 backlog domaine 30 |

#### Points convergés

- RAG documentaire backend opérationnel en mode lexical, positionné comme renfort situé (non mémoire principale).
- Référentiel et bibliothèque existants ; séparation surfaces testeur vs apprenant respectée.
- Doctrine triptyque référentiel > base formateur > RAG documentée dans écarts 30/40.

#### Points encore ouverts

- Désambiguïsation doc « RAG vectoriel » vs réel lexical — priorité doc haute.
- Contrat `DocumentContextBundle` ou équivalent (B2 backlog 30).
- Audit consommation `TrainerKnowledgeItem` dans pipeline apprenant — **A_VÉRIFIER**.
- Parité runtime distant sur indexation — **A_VÉRIFIER**.

---

### 1.4 Domaine 31 — front apprenant (postures et bascule)

#### Photo rapide

Front prod (`ProdLearnerWorkspace`, `HugoProgressPanel`) backend-first : consomme UIState, CTA synthèse/évaluation, progression scène/quête/maturité. Cluster 4/5 a livré bandeau `conversation_mode` lecture seule et grammaires `learner_display_profile`. **Bascule de posture interactive** : cadrée en cible, non démontrée en réel prod.

#### Tableau « état de convergence »

| Sous-domaine / sujet | Statut documentaire | Tag principal | Commentaire court | Référence |
|----------------------|---------------------|---------------|-------------------|-----------|
| UIState + panneau progression | IMPLÉMENTÉ | RÉEL OBSERVÉ | Pas de heuristique P0 locale | `ecarts — 31_front_apprenant_postures_et_bascule.md` |
| CTA synthèse / éval branchés | IMPLÉMENTÉ | RÉEL OBSERVÉ | États backend-driven | `09_PARCOURS_DEMO_ET_SCENARIOS.md` |
| Affichage `conversation_mode` (lecture) | IMPLÉMENTÉ | RÉEL OBSERVÉ | `ConversationModeBanner.vue` | `design_D2-M07_D2-M08` |
| 3 grammaires `learner_display_profile` | PARTIEL | RÉEL OBSERVÉ | Youth livré ; adult/professional peu différenciés | Retex C5 |
| Sélecteur posture / bascule régime | ABSENT_NOUVEAU_CONTRAT | CIBLE | Matrice maquettée ; composant absent prod | `ecarts — 31` §5.3 |
| `POST/PATCH set-posture` côté front | A_VÉRIFIER | CIBLE | Backend `SessionSetPostureView` ; branchement UI absent | G2‑02 |
| Matrice états UI bascule (SW-01…) | CREDIBLE | CIBLE | Spec produit détaillée, non implémentée | `ecarts — 31` matrice maquettée |

#### Points convergés

- Architecture front dérivée d'états : invariant 2.0 respecté sur progression et CTA.
- Séparation posture / geste / évaluation terminale documentée.
- Contrat `conversation_mode` minimal testé API + bandeau front.

#### Points encore ouverts

- Implémentation composant « Mode de travail » avec états `VISIBLE_SWITCHABLE` / `LOCKED` — **CIBLE**.
- Annexe spec interface bascule + quasi-contrat UIState enrichi (BA-011, BA-018).
- Tests composants Vue (`ConversationModeBanner`, workspace) — **ÉCART CONFIRMÉ** couverture partielle.
- Endpoint posture : POST réel vs PATCH spec — D2‑M03.

---

### 1.5 Domaine 40 — base de connaissances formateur

#### Photo rapide

Objet central `TrainerKnowledgeItem` aligné vocabulaire cible/réel. Vues trainer, ingestion documentaire, statuts doctrinaux (`declared`, `derived_provisional`, `validated`). Chaîne complète ingestion → dialogue → validation → consommation apprenant **non prouvée** bout en bout.

#### Tableau « état de convergence »

| Sous-domaine / sujet | Statut documentaire | Tag principal | Commentaire court | Référence |
|----------------------|---------------------|---------------|-------------------|-----------|
| Modèle `TrainerKnowledgeItem` | IMPLÉMENTÉ | RÉEL OBSERVÉ | Alignement glossaire fort | `ecarts — 40_base_connaissances_formateur.md` |
| Vues trainer + tests | IMPLÉMENTÉ | RÉEL OBSERVÉ | Surfaces back-office / trainer | idem §4.1 |
| Statuts gouvernés | PARTIEL | CIBLE | Doctrine claire ; enforcement runtime partiel | idem §5.4 |
| Validation humaine formateur | PARTIEL | CIBLE | Pas de matrice rôle × action complète | `ecarts — 110` IFT-020 |
| Lien item → RAG / orchestrateurs apprenant | PARTIEL | A_VÉRIFIER | Présence structurelle ; usage tour non prouvé | domaine 30 V3 |
| Workflow dialogique complet | ABSENT_NOUVEAU_CONTRAT | CIBLE | Script F1–F4 non stabilisé | `ecarts — 50` |

#### Points convergés

- Objet métier formateur nommé et présent ; subordination au référentiel primaire doctrinalement verrouillée.
- Ingestion documentaire et surfaces trainer réelles.
- Pas de sur-vente : base formateur ≠ vérité automatique.

#### Points encore ouverts

- Contrat backend place de `TrainerKnowledgeItem` dans chaîne apprenant (B3 backlog 30/40).
- Matrice validation par rôle habilité.
- Parcours formateur démontrable persona C1 — **PARTIEL**.
- Équivalence trainer local vs Encoors — **A_VÉRIFIER**.

---

### 1.6 Domaine 50 — orchestrateur formateur

#### Photo rapide

Orchestrateur spécialisé cible : dialogue d'élaboration du savoir, production d'items structurés, validation humaine. Réel = briques (`TrainerKnowledgeItem`, vues trainer, ingestion) sans service unique « OrchestrateurFormateur » ni script dialogique figé.

#### Tableau « état de convergence »

| Sous-domaine / sujet | Statut documentaire | Tag principal | Commentaire court | Référence |
|----------------------|---------------------|---------------|-------------------|-----------|
| Objets et vues trainer | IMPLÉMENTÉ | RÉEL OBSERVÉ | Base nominale solide | `ecarts — 50_orchestrateur_formateur.md` |
| Ingestion documentaire | IMPLÉMENTÉ | RÉEL OBSERVÉ | Lien library / trainer | idem §4.1 |
| Questionnaire dialogique F1–F4 | ABSENT_NOUVEAU_CONTRAT | CIBLE | Ouvert cadré ; non prouvé | idem §5.2 |
| Script / chorégraphie UI | ABSENT_NOUVEAU_CONTRAT | CIBLE | Spec ne doit pas inventer écrans | idem §5.3 |
| Variables backend prompts formateur | PARTIEL | CIBLE | Cartographie à compléter | backlog 50 |
| Validation sans auto-promotion | PARTIEL | RÉEL OBSERVÉ | Doctrine OK ; surfaces fines ouvertes | idem §5.5 |

#### Points convergés

- Domaine non théorique : objets et responsabilité métier présents dans le code.
- Garde-fous : pas d'auto-certification, subordination référentiel.

#### Points encore ouverts

- Formaliser écart « briques vs workflow complet » sans refonte moteur.
- Contrat dialogique minimal (sections, relances) — **CIBLE**, pas de reconstruction spéculative.
- Parcours encadrant C1 bout-en-bout — repoussé au lot parcours encadrants.
- Runtime distant formateur — **A_VÉRIFIER**.

---

### 1.7 Domaine 60 — orchestrateur tuteur

#### Photo rapide

Couche tuteur = assemblage de briques backend (`ConversationProgress`, UIState, synthèse, évaluation, `QualityTracker`, timeline dashboard). Pas de service unique « TutorOrchestrator ». Oracle B1‑01 (verbatim masqué si non partagé) **vert en local** après patch C3. Validation terminale générique tuteur **non actée** en Hugo cœur 2.0.

#### Tableau « état de convergence »

| Sous-domaine / sujet | Statut documentaire | Tag principal | Commentaire court | Référence |
|----------------------|---------------------|---------------|-------------------|-----------|
| Progression + UIState (lecture) | IMPLÉMENTÉ | RÉEL OBSERVÉ | Endpoints consommables | `ecarts — 60_orchestrateur_tuteur.md` |
| Timeline tuteur B1‑01 | IMPLÉMENTÉ | RÉEL OBSERVÉ | `share_verbatim` respecté ; test cluster 3 | `cluster3_validation_courte_personae.md` |
| Synthèse / éval partageables | PARTIEL | RÉEL OBSERVÉ | Workflows existent ; surfaces tuteur partielles | `ecarts — 110` IFT-010/011 |
| Signaux qualité (`QualityTracker`) | IMPLÉMENTÉ | RÉEL OBSERVÉ | Modèle + service ; catalogue ouvert | domaine 80 |
| Vues cohorte | PARTIEL | A_VÉRIFIER | `cohort_dashboard` ; exposition prod incertaine | `cluster2` §5 |
| Validation trace tuteur | PARTIEL | RÉEL OBSERVÉ | `POST traces/{id}/validate/` ; périmètre à borner | mapping EvaluationTrace |
| Pouvoir validation terminale éval | ABSENT_NOUVEAU_CONTRAT | CIBLE | Extension ultérieure, pas défaut 2.0 | complément 2.0 |
| Parcours UI tuteur complet | PARTIEL | A_VÉRIFIER | Backend > surface métier stabilisée | D2‑M09 |

#### Points convergés

- Socle backend riche pour accompagnement : progression, signaux, artefacts partageables.
- Garde-fous confidentialité timeline prouvés localement (B1‑01, B1‑02 recalibré).
- Doctrine : tuteur lit et recommande, ne pilote pas P0.

#### Points encore ouverts

- Checklist parcours tuteur B1 complète (D2‑M09).
- Catalogue `ConversationQualitySignal` — lien domaine 80.
- UI tuteur bout-en-bout vs mode testeur — **A_VÉRIFIER** prod.
- Commentaire / accompagnement humain structuré — **ABSENT_NOUVEAU_CONTRAT** (IFT-018).

---

### 1.8 Domaine 70 — évaluation / traces / preuves

#### Photo rapide

Branche terminale utilisable : `request-evaluation`, `finalize-evaluation`, CTA backend, `LearnerEvaluationRecord`, `Trace`, `Evidence`, partage session. `EvaluationTrace` = agrégat **conceptuel** uniquement ; mapping documenté D2‑M05. Payload `generate-trace` souvent **minimal** localement.

#### Tableau « état de convergence »

| Sous-domaine / sujet | Statut documentaire | Tag principal | Commentaire court | Référence |
|----------------------|---------------------|---------------|-------------------|-----------|
| Workflow évaluation terminale | IMPLÉMENTÉ | RÉEL OBSERVÉ | Services + endpoints + CTA | `ecarts — 70_evaluation_traces_preuves.md` |
| CTA synthèse / éval UIState | IMPLÉMENTÉ | RÉEL OBSERVÉ | Tests cluster 1 | Retex C1 |
| `LearnerEvaluationRecord` | IMPLÉMENTÉ | RÉEL OBSERVÉ | Pont EvaluationTrace.evaluation | `mapping_EvaluationTrace_runtime_local.md` |
| `Trace` + `Evidence` | IMPLÉMENTÉ | RÉEL OBSERVÉ | Génération + création preuve | `cluster2` §4.3 |
| Mapping EvaluationTrace (doc) | IMPLÉMENTÉ | RÉEL OBSERVÉ | D2‑M05 livré documentairement | idem |
| Payload trace riche (`trace_rich_v1`) | PARTIEL | ÉCART CONFIRMÉ | Squelette minimal en local | `05_ECARTS_DOC_CODE_PRODUIT` |
| Validation humaine bout-en-bout | PARTIEL | CIBLE | Circuits record vs trace parallèles | `ecarts — 70` §5.4 |
| Certification autonome | IMPLÉMENTÉ | RÉEL OBSERVÉ | Absente par design | doctrine |

#### Points convergés

- Domaine existant et montrable : boutons prod branchés, garde `can_request_evaluation`.
- Vocabulaire stabilisé via mapping EvaluationTrace (dispersion assumée, pas de modèle homonyme).
- Partage explicite session + flags record documentés.

#### Points encore ouverts

- Enrichissement payload trace exportable — contrat additif, pas sur-vente actuelle.
- Fusion circuits validation record / trace — chantier séparé si priorisé.
- Richesse bundle Qualiopi vs attentes D1 — **A_VÉRIFIER** prod.
- EXIF/GPS preuves — **A_VÉRIFIER** implémentation fine.

---

### 1.9 Domaine 80 — observabilité / qualité conversationnelle

#### Photo rapide

`ConversationQualitySignal`, `quality_tracker`, `analytics_state` JSON session, hooks post-conversation. Signaux **non exposés** à l'apprenant (doctrine). Catalogue canonique des signaux **absent**. D9bis (analyse LLM qualité) = **CIBLE**, distinct du tracing technique.

#### Tableau « état de convergence »

| Sous-domaine / sujet | Statut documentaire | Tag principal | Commentaire court | Référence |
|----------------------|---------------------|---------------|-------------------|-----------|
| `QualityTracker` + enregistrement signaux | IMPLÉMENTÉ | RÉEL OBSERVÉ | Post-conversation | `ecarts — 80_observabilite_qualite_conversationnelle.md` |
| `ConversationQualitySignal` (modèle) | IMPLÉMENTÉ | RÉEL OBSERVÉ | Types non catalogués | idem matrice §2 |
| Vues cohorte / analytics | PARTIEL | A_VÉRIFIER | `cohort_dashboard` ; prod non tranchée | `cluster2` §5 |
| Qualité visible apprenant | IMPLÉMENTÉ | RÉEL OBSERVÉ | Absente par doctrine | idem §3 |
| Catalogue signaux canonique | ABSENT_NOUVEAU_CONTRAT | CIBLE | Spec ouverte | OBSQ backlog |
| D9bis LLM analysis qualité | ABSENT_NOUVEAU_CONTRAT | CIBLE | Ne pas mapper vers EvaluationTrace | `design_D2-M06_D2-M11` |
| `turn-review` internal | CREDIBLE | A_VÉRIFIER | Surface testeur / debug | domaine 100 |

#### Points convergés

- Infrastructure signaux présente côté backend ; alignement post-conversation (pas front moteur).
- Séparation observabilité technique vs état produit UIState.
- Tests exports C7 verrouillent absence D9bis dans bundles.

#### Points encore ouverts

- Catalogue `ConversationQualitySignal` — contrat doc prioritaire (OBSQ-01).
- Projection tuteur des signaux (lien domaine 60).
- Parité qualité local / Encoors — **A_VÉRIFIER**.
- D9bis : rester **CIBLE** sauf priorisation explicite CTO.

---

### 1.10 Domaine 90 — confidentialité / multi-tenant / rôles

#### Photo rapide

Multi-tenant via `organisation_id`, partage explicite (`share_*`), rôles LEARNER/TUTOR/TRAINER/ORGADMIN/SUPERADMIN. Matrice rôle × donnée amorcée ; pack pytest D2‑M07 (10 tests) + cluster 3. RLS Postgres prod et rôle COORDO **non prouvés**. Frontière ORGADMIN / superadmin technique ouverte (D2‑M12).

#### Tableau « état de convergence »

| Sous-domaine / sujet | Statut documentaire | Tag principal | Commentaire court | Référence |
|----------------------|---------------------|---------------|-------------------|-----------|
| Verbatim privé par défaut | IMPLÉMENTÉ | RÉEL OBSERVÉ | `/app` conforme ; B1‑01 timeline | `ecarts — 90_confidentialite_partage_multitenant_roles.md` |
| Partage explicite session | IMPLÉMENTÉ | RÉEL OBSERVÉ | Flags + ShareView | CONF-04 matrice |
| Isolation tenant (middleware, tests) | PARTIEL | RÉEL OBSERVÉ | Cross-tenant tests ; RLS prod A_VÉRIFIER | CONF-11/12 |
| Matrice rôle × visibilité | PARTIEL | CIBLE | §6.2 cluster 2 amorcé ; D2‑M07 partiel | `design_D2-M07` |
| Rôle COORDO | ABSENT_NOUVEAU_CONTRAT | CIBLE | Absent code | `cluster2` §6.1 |
| Frontière ORGADMIN / superadmin | PARTIEL | CIBLE | Export debug md absent ; LLM analysis CIBLE | D2‑M12 |
| RLS Postgres effective prod | A_VÉRIFIER | A_VÉRIFIER | SQLite local ; migrations présentes | CONF-12 |
| Choix profil affichage par rôle | ABSENT_NOUVEAU_CONTRAT | CIBLE | PATCH groupe orgadmin partiel seulement | IFT-042 |

#### Points convergés

- Doctrine confidentialité-first ancrée ; oracle B1‑01 vert local.
- Pack confidentialité reproductible (`test_d2_m07_confidentiality_oracles.py`).
- Pas d'exposition P0 aux surfaces prod documentée.

#### Points encore ouverts

- Matrice complète endpoint × permission × donnée sensible (D2‑M07).
- Audit RLS prod Encoors — **A_VÉRIFIER**.
- COORDO et superadmin technique : contractualiser sans sur-spécifier UI.
- Durcissement permissions rôle sur exports org (scoping données OK, rôle PARTIEL).

---

### 1.11 Domaine 100 — exports / preuves / Qualiopi lite

#### Photo rapide

Taxonomie E1–E6 documentée (cluster 7). `EvidenceBundleView` (ZIP métadonnées), `ExportRun` (`trace_rich_v1`), exports trainer/apprenant implémentés. Bundle **non certifiant**. D9bis et `export-md` **absents**. Permissions ORGADMIN sur exports org **partielles** (tenant OK, rôle faible).

#### Tableau « état de convergence »

| Sous-domaine / sujet | Statut documentaire | Tag principal | Commentaire court | Référence |
|----------------------|---------------------|---------------|-------------------|-----------|
| EvidenceBundle Qualiopi lite | IMPLÉMENTÉ | RÉEL OBSERVÉ | Métadonnées traces ; pas record LLM | `design_D2-M06_D2-M11_exports_analytics.md` |
| ExportRun CSV/JSON | IMPLÉMENTÉ | RÉEL OBSERVÉ | `payload_structured` inclus ; tests tenant | `test_exports_run.py` |
| Export trainer eval records | IMPLÉMENTÉ | RÉEL OBSERVÉ | RBAC `_can_manage_evaluations` | idem §1.1 |
| Liste traces/preuves apprenant | IMPLÉMENTÉ | RÉEL OBSERVÉ | Endpoints learners | mapping EvaluationTrace |
| Trace exportable riche | PARTIEL | ÉCART CONFIRMÉ | Intrants `generate-trace` pauvres | `ecarts — 100` |
| D9bis export analytique LLM | ABSENT_NOUVEAU_CONTRAT | CIBLE | Modèles absents ; tests absence | D2‑M06 |
| `debug/export-md` | ABSENT_NOUVEAU_CONTRAT | CIBLE | Route absente urls | G3‑03 oracle |
| Matrice artefacts × rôle | PARTIEL | CIBLE | D2‑M11 partiel ; E1–E6 posés | design cluster 7 |
| Bundle prod contenu réel | A_VÉRIFIER | A_VÉRIFIER | ZIP local minimal | `10_FICHE_RUNTIME_PROD_ENCOORS` |

#### Points convergés

- Exports métier et techniques classés ; pas de confusion debug / Qualiopi / D9bis dans tests C7.
- Scoping tenant sur ExportRun et bundle (tests D1‑02, G3‑02).
- Doctrine : bundle aide audit, ne certifie pas.

#### Points encore ouverts

- Durcissement permissions `IsAuthenticated` → rôle ORGADMIN sur E3/E4.
- Enrichissement bundle (record, preuves binaires) — hors lot minimal.
- Liste canonique exportable par rôle — finaliser D2‑M11.
- Parité Encoors exports — **A_VÉRIFIER**.

---

### 1.12 Domaine 110 — interfaces formateur / tuteur

#### Photo rapide

Parcours apprenant prod mature (`ProdLearnerWorkspace`). Surfaces tuteur : timeline dashboard partiellement prouvée (B1‑01). Formateur : trainer views + knowledge, orchestrateur dialogique **non démontré**. Profils affichage : contrat backend + socle front youth ; sélecteur posture **CIBLE**. Mode testeur (`LearnerDetailView`) hors démo standard.

#### Tableau « état de convergence »

| Sous-domaine / sujet | Statut documentaire | Tag principal | Commentaire court | Référence |
|----------------------|---------------------|---------------|-------------------|-----------|
| Parcours apprenant `/app` | IMPLÉMENTÉ | RÉEL OBSERVÉ | Chat, ui-state, CTA, partage | `03_ETAT_PRODUIT_REEL` |
| Interface tuteur timeline | PARTIEL | RÉEL OBSERVÉ | B1‑01 OK local ; prod A_VÉRIFIER | `ecarts — 110_interfaces_formateur_tuteur.md` |
| Interface formateur trainer | PARTIEL | RÉEL OBSERVÉ | Items + admin ; workflow complet ouvert | IFT-003/037 |
| ConductProfiles / TutorPrompts admin | IMPLÉMENTÉ | RÉEL OBSERVÉ | API + admin UI | IFT-024 |
| `learner_display_profile` 3 UX | PARTIEL | RÉEL OBSERVÉ | API OK ; rendu 3 grammaires partiel | D2‑M08 |
| `conversation_mode` + sélecteur UI | PARTIEL | ÉCART CONFIRMÉ | Backend OK ; sélecteur absent | G2‑02 |
| Workflow validation formateur | ABSENT_NOUVEAU_CONTRAT | CIBLE | Chaîne F1–F4 non prouvée | IFT-037 |
| Choix profil par formateur (cohorte) | ABSENT_NOUVEAU_CONTRAT | CIBLE | DSP‑05 ouvert | design D2‑M08 |
| Surface COORDO | A_VÉRIFIER | CIBLE | Rôle doctrine ; UI absente | IFT-038 |

#### Points convergés

- Séparation nette prod apprenant / testeur / trainer documentée.
- Timeline tuteur comme référence confidentialité post-C3.
- Multi-postures code (3 postures) ; ne pas AFEST-iser la doc.

#### Points encore ouverts

- Parcours formateur persona C1 bout-en-bout — lot encadrants.
- Compléter 3 grammaires front (adult/professional) + tests composants Vue.
- Checklist tuteur B1 (D2‑M09).
- Équivalence interfaces local / Encoors — **A_VÉRIFIER**.

---

### 1.13 Domaine 120 — intercalaires v1

#### Photo rapide

Capacité **additive** cible : micro-artefacts pédagogiques post-tour (`NONE` / `NOTION` / `CONTRAST`), passifs, non évaluatifs, sans effet sur P0. **Aucune feature observée** dans le runtime local audité : pas de modèle, service, endpoint ni composant front identifié.

#### Tableau « état de convergence »

| Sous-domaine / sujet | Statut documentaire | Tag principal | Commentaire court | Référence |
|----------------------|---------------------|---------------|-------------------|-----------|
| Doctrine intercalaires V1 | CREDIBLE | CIBLE | Cadre spec 2.0 + décisions doc domaine | `ecarts — 120_intercalaires_v1.md` |
| `SessionInterstitial` ou équivalent code | ABSENT_NOUVEAU_CONTRAT | CIBLE | Objet conceptuel sans ancrage réel | matrice INT |
| Producteur post-tour | ABSENT_NOUVEAU_CONTRAT | CIBLE | Point d'insertion défini, non branché | idem |
| Composant apprenant passif | ABSENT_NOUVEAU_CONTRAT | CIBLE | Non interactif, non évaluatif | idem §5 |
| Projection via UIState | ABSENT_NOUVEAU_CONTRAT | CIBLE | Arbitrage produit ouvert (INT-024) | backlog 120 |
| Flags / variante distante | A_VÉRIFIER | A_VÉRIFIER | INT-022 : pas de preuve activation | idem |

#### Points convergés

- Garde-fous architecturaux alignés : pas d'effet retour P0, confidentialité-first, un seul intercalaire max/tour.
- Domaine correctement borné comme **préparation contrat**, pas comme livré.

#### Points encore ouverts

- Contrat minimal JSON + enum typologie — doc avant code (INT-001–008).
- Raccord UIState sans dégrader grammaire produit existante — **A_VÉRIFIER**.
- Versions futures intercalaires (hors v1) — explicitement repoussées.
- Audit runtime distant pour artefact proche — **A_VÉRIFIER**.

---

## 2. Vue transversale des écarts

| Type de manque | 10 | 20 | 30 | 31 | 40 | 50 | 60 | 70 | 80 | 90 | 100 | 110 | 120 |
|----------------|----|----|----|----|----|----|----|----|----|----|-----|-----|-----|
| **Contrats non encore écrits ou partiels** | D2‑M02 posture×CTA ; UIState formel | D2‑M04 memory-summary ; mémoire UIState contrat | DocumentContextBundle ; hiérarchie contexte | Matrice états bascule ; annexe spec interface | Chaîne item→RAG apprenant | Script dialogique F1–F4 | Checklist B1 D2‑M09 ; commentaire tuteur | Trace exportable enrichie | Catalogue signaux OBSQ | Matrice complète D2‑M07 ; COORDO | Liste artefacts×rôle D2‑M11 | Workflow validation F1 ; choix profil formateur | Contrat SessionInterstitial v1 |
| **Tests manquants ou incomplets** | v17 flag ; CTA×posture | Front memory-summary ; injection prompt | Consommation TKI runtime | Composants Vue bascule/bandeau | Workflow validation E2E | Parcours formateur E2E | UI tuteur complète | Payload trace riche | Catalogue signaux | RLS prod ; EXIF preuves | Permissions rôle E3/E4 (patch) | 3 grammaires E2E ; C1 | Producteur intercalaire (futur) |
| **Doc / matrice à jour mais sans preuve code** | DecisionContract mapping | Inter-sessions doctrinale | RAG vectoriel cible | SW-01…10 maquettes | Orchestrateur 2.0 complet | Sections/relances script | Validation terminale tuteur | EvaluationTrace agrégat runtime | D9bis | COORDO projections | export-md superadmin | Orchestrateur dialogique UI | Typologie NOTION/CONTRAST en code |
| **Dépendances A_VÉRIFIER (prod, RLS, Encoors, flags)** | HUGO_P0_V17 prod | memory-summary prod ; injection thème | Indexation vectorielle prod | set-posture prod ; UI Encoors | Trainer workflow prod | Ingestion prod | Dashboard cohorte prod | Bundle ZIP prod ; traces riches | QualityTracker prod | RLS Postgres ; cross-tenant prod | EvidenceBundle contenu prod | Timeline prod ; interfaces | Flags intercalaires distants |
| **Sujets explicitement repoussés (D9bis / intercalaires futures / orchestrateurs enrichis)** | Refonte pipeline global | Mémoire inter-sessions injection tour | RAG vectoriel lot ultérieur | G2‑02 sélecteur (hors lot immédiat) | — | Script fin non inventé | Validation terminale tuteur générique | Certification autonome | D9bis LLM analysis | — | D9bis exports | Skins cosmétiques ; COORDO UI | Intercalaires > v1 ; interactifs |

---

## 3. Derniers gros lots possibles

### Lot 1 — Parcours encadrants B1 / C1 / D1

| | |
|---|---|
| **Domaines** | 10, 31, 40, 50, 60, 70, 90, 100, 110, 120 (cadrage seulement pour 120) |
| **Principaux gains** | Surface tuteur/formateur démontrable ; timeline + knowledge + exports alignés personae ; matrice confidentialité exploitable en démo |
| **Risques si non traité** | Écarts 50/60/110 restent « briques sans parcours » ; vente produit encadrants impossible ; re-travail front posture sans cadre encadrant |

### Lot 2 — Décisions structurantes v17 + frontières ORGADMIN / superadmin

| | |
|---|---|
| **Domaines** | 10, 90, 100 |
| **Principaux gains** | Convergence décision unique (legacy vs v17) ; matrice rôles complète D2‑M07/D2‑M12 ; permissions exports org durcies |
| **Risques si non traité** | Double stack décisionnelle persistante ; exports org accessibles à tout authentifié du tenant ; confusion debug superadmin vs métier ORGADMIN |

### Lot 3 — RAG & observabilité minimale

| | |
|---|---|
| **Domaines** | 30, 40, 80 |
| **Principaux gains** | Contrat lexical honnête ; place TKI dans pipeline ; catalogue signaux qualité pour tuteur ; observabilité sans D9bis |
| **Risques si non traité** | Sur-vente RAG vectoriel ; base formateur déconnectée du runtime apprenant ; couche tuteur sans signaux lisibles |

### Lot 4 — Intercalaires v1 & front postures

| | |
|---|---|
| **Domaines** | 31, 120 |
| **Principaux gains** | Contrat intercalaire avant code ; composant « Mode de travail » + sélecteur posture cohérent ; UX multi-postures montrable (G2‑02) |
| **Risques si non traité** | Deux chantiers UX divergents ; intercalaires implémentés sans garde-fous ; bascule posture toujours CIBLE en démo |

### Lot 5 — D9bis (optionnel, si priorisé CTO)

| | |
|---|---|
| **Domaines** | 80, 100 |
| **Principaux gains** | Sous-contrat export analytique LLM borné superadmin ; distinction nette tracing vs analyse doctrinale |
| **Risques si non traité** | Confusion persistante `llm_response_payload` / analyse qualité ; pression produit pour exposer debug comme métier |

---

## 4. Recommandation de pilotage Cursor

### Par domaine

Un prompt Cursor par domaine doit **nommer explicitement** le fichier d'écart correspondant et la matrice cluster 2, par exemple : « S'appuyer sur `ecarts — 60_orchestrateur_tuteur.md` et `cluster2_matrice_runtime_vs_cible.md` §5 ». Pour les domaines sans fichier dédié au numéro exact (10), utiliser le nom réel : `ecarts —10_runtime_p0_progression_uistate.md`. Toujours rappeler : **runtime local**, marquer prod/RLS **A_VÉRIFIER**.

### Par lot D2‑Mxx

Enchaîner design → tests → Retex : ex. « Exécuter D2‑M09 checklist tuteur B1 » en citant `design_D2-M07_D2-M08` + `ecarts — 110` + `test_cluster3_oracles.py`. Les lots documentaires livrés (D2‑M01, D2‑M05, D2‑M08 partiel) ne doivent pas être re-ouverts sauf enrichissement explicite.

### Par type de travail

| Type | Fichiers à citer systématiquement |
|------|-----------------------------------|
| **Design** | `ecarts — XX`, `design_D2-Mxx`, `cluster2_matrice_runtime_vs_cible.md` |
| **Exécution / tests** | Code `hugo_back` tests (`test_cluster*`, `test_d2_m*`), `cluster2_oracles_test_par_persona.md` |
| **Retex** | `Retex_cluster_1-4.md`, `Retex_clusters_5-7_profils_roles_exports.md` après clôture lot |
| **Patch doc** | `02_decisions_documentaires` du domaine + `00_HIERARCHIE_DOCUMENTAIRE.md` |

### Nommage des fichiers d'écarts dans les prompts

Pour que Cursor exploite **tous** les écarts et pas seulement les lots déjà travaillés, inclure une liste fermée dans chaque prompt transversal :

```
ecarts —10_runtime_p0_progression_uistate.md
ecarts — 20_memoire_gouvernee.md
ecarts — 30_referentiel_documentaire_RAG.md
ecarts — 31_front_apprenant_postures_et_bascule.md
ecarts — 40_base_connaissances_formateur.md
ecarts — 50_orchestrateur_formateur.md
ecarts — 60_orchestrateur_tuteur.md
ecarts — 70_evaluation_traces_preuves.md
ecarts — 80_observabilite_qualite_conversationnelle.md
ecarts — 90_confidentialite_partage_multitenant_roles.md
ecarts — 100_exports_preuves_qualiopi_lite.md
ecarts — 110_interfaces_formateur_tuteur.md
ecarts — 120_intercalaires_v1.md
cluster2_matrice_runtime_vs_cible.md
```

Ajouter les designs/Retex quand le lot touche profils (D2‑M07/M08), exports (D2‑M06/M11), ou post-mortem (Retex 1–4 / 5–7).

### Ordre de lecture recommandé pour un prompt « vue globale »

1. Cette synthèse (`synthese_globale_ecarts_par_domaine.md`) — photo d'ensemble  
2. `cluster2_matrice_runtime_vs_cible.md` — statuts et backlog D2‑Mxx  
3. Fichier `ecarts — XX` du domaine ciblé — détail matrice et backlog  
4. Retex du cluster correspondant — erreurs à ne pas répéter  

---

## Sources mobilisées

- `cluster2_matrice_runtime_vs_cible.md` (V2, 2026-06-16)
- Écarts domaines : `ecarts —10_runtime_p0_progression_uistate.md`, `ecarts — 20_memoire_gouvernee.md`, `ecarts — 30_referentiel_documentaire_RAG.md`, `ecarts — 31_front_apprenant_postures_et_bascule.md`, `ecarts — 40_base_connaissances_formateur.md`, `ecarts — 50_orchestrateur_formateur.md`, `ecarts — 60_orchestrateur_tuteur.md`, `ecarts — 70_evaluation_traces_preuves.md`, `ecarts — 80_observabilite_qualite_conversationnelle.md`, `ecarts — 90_confidentialite_partage_multitenant_roles.md`, `ecarts — 100_exports_preuves_qualiopi_lite.md`, `ecarts — 110_interfaces_formateur_tuteur.md`, `ecarts — 120_intercalaires_v1.md`
- Designs : `design_D2-M06_D2-M11_exports_analytics.md`, `design_D2-M07_D2-M08_profils_grammaires_matrice_roles.md`
- Retex : `Retex_cluster_1-4.md`, `Retex_clusters_5-7_profils_roles_exports.md`
- Mapping : `mapping_EvaluationTrace_runtime_local.md` (D2‑M05)

## Réel confirmé (transversal)

- Socle backend conversationnel + UIState + CTA + mémoire intra-contrat testés (clusters 1–4, 70 tests backend clusters 5–7).
- `conversation_mode` / `learner_display_profile` en API ; front partiellement convergé.
- Confidentialité timeline B1‑01 ; exports tenant-scoped ; D9bis absent.

## Cible 2.0 (écarts dominants)

- Orchestrateurs formateur/tuteur complets ; sélecteur posture ; intercalaires v1 ; RAG vectoriel ; mémoire inter-sessions au tour ; D9bis ; COORDO ; matrice rôles complète.

## A_VÉRIFIER

- `hugoback.encoors.com`, RLS Postgres prod, `HUGO_P0_V17_ENABLED`, richesse traces/bundles prod, interfaces encadrants prod.

## Prochaine sortie utile

Piloter les **3 à 5 gros lots** ci-dessus via prompts Cursor ciblés, en citant systématiquement la liste fermée des `ecarts — *.md` + cette synthèse comme entrée de chaque chantier transversal.
