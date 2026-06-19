# Inventaire convergence Hugo réel → cible 2.0

> Dernière vague de convergence — domaines **10, 20, 30, 31, 70, 80, 90, 100, 110**  
> Date : 2026-06-18  
> Méthode : spec 2.0 = **CIBLE** ; code + tests + audits clusters 2–10 = **RÉEL OBSERVÉ**

---

## Introduction

Ce document inventorie, domaine par domaine, ce qui reste à faire pour rapprocher **Hugo réel local** (backend `hugo_back`, front `hugo-hugolucia/frontend_1.8`, tests pytest/Playwright) de la **cible Hugo 2.0** (spec canonique + compléments + specs interface).

**Domaines couverts :** 10, 20, 30, 31, 70, 80, 90, 100, 110.

**Niveaux de vérité utilisés :**

| Niveau | Signification |
|--------|---------------|
| **CIBLE 2.0** | Spec / compléments — jamais preuve de livraison |
| **RÉEL OBSERVÉ** | Code, tests, audits récents (matrice cluster 2 V3, clusters 8–10, écarts domaine) |
| **ÉCART CONFIRMÉ** | Divergence recoupée doc + code |
| **A_VÉRIFIER** | Encoors, RLS prod, flags, UI non auditée |
| **HYPOTHÈSE** | Inférence non prouvée — signalée comme telle |

**Hiérarchie appliquée :** audits récents (clusters 8–10, matrice V3) priment sur anciennes notes isolées. UIState, memory-summary, traces = **états dérivés backend**, pas logique moteur.

**Sources mobilisées :** `cluster2_matrice_runtime_vs_cible.md`, écarts 10/20/30/31/70/80/90/100/110, rapports clusters 8–10, `contrat_api_memory_summary_v1.md`, `fiche_trace_exploitable_pivot_v1.md`, `matrice_role_visibilite_v2.md`, `02_ETAT_MOTEUR_REEL.md`, `03_ETAT_PRODUIT_REEL.md`, `10_FICHE_RUNTIME_PROD_ENCOORS.md`.

---

## Domaine 10 — runtime P0, progression, UIState

### CIBLE 2.0 (résumé)

Moteur piloté par état : P0/TurnState internes, `ConversationProgress` et `DecisionContract`, UIState dérivé côté serveur consommé par le front sans recalcul local. CTA synthèse/évaluation backend-driven. P0 et diagnostics techniques **hors surface apprenant**. Variation CTA/libellés selon posture. Flag v17 documenté. Pas d’exposition TurnState brut au produit.

### RÉEL OBSERVÉ (local)

**Implémenté et prouvé :**

- P0 : `classify_p0_turn_state`, `TurnState`, tests (`test_p0_v17_flow.py`, etc.).
- Progression : `build_conversation_progress_contract`, branches, maturité.
- UIState : `build_contract_ui_state`, `GET .../ui-state/`, CTA via `cta_ui_state.py` — tests cluster 4, front unitaires.
- `conversation_mode` dans UIState (cluster 4).
- `learner_display_profile` cascade org/groupe/query — backend prêt.
- Front `/app` sans TurnState/P0 brut (`03_ETAT_PRODUIT_REEL`).

**Partiel / ambigu :**

- Double builder `build_ui_state` vs `build_contract_ui_state` — confusion doc (**ÉCART CONFIRMÉ**).
- TurnState v17 : code présent, flag `HUGO_P0_V17_ENABLED` **A_VÉRIFIER** prod.
- Libellés CTA identiques toutes postures (D2-M02 ouvert).

### Mini-table

| Objet / règle | CIBLE 2.0 | RÉEL OBSERVÉ | Statut | Action |
|---------------|-----------|--------------|--------|--------|
| P0 / TurnState moteur | Interne, gouverné | `p0_classifier.py`, orchestrateur | ALIGNE | — |
| TurnState v17 | Option flaggée | Code + flag env | A_VÉRIFIER | OPS flags prod |
| ConversationProgress | Contrat branches | `conversation_progress.py` | ALIGNE | — |
| UIState produit | Dérivé serveur | `build_contract_ui_state` | ALIGNE | — |
| Double UIState builder | Un contrat canonique | Deux chemins | AMBIGU | DOC |
| CTA synthèse/éval | Backend-only front | Tests CTA + front | ALIGNE | — |
| CTA × posture libellés | Variation | Identiques | ABSENT | DOC D2-M02 |
| conversation_mode | UIState | Livré C4 | ALIGNE | — |
| Sélecteur posture prod | — | Absent (→ domaine 31) | ABSENT | CODE 31 |

### ÉCARTS CONFIRMÉS

- Double stack UIState documentaire.
- CTA libellés non différenciés par posture.

### A_VÉRIFIER

- `HUGO_P0_V17_ENABLED` local et Encoors — **audit flags** (`08_FLAGS`, env prod).
- Comportement UIState distant — **oracle Encoors** session avec JWT.

### Actions derniers clusters

| Type | Action |
|------|--------|
| DOC | D2-M02 tableau posture→RAG→maturité→CTA ; D2-M10 flag v17 dans fiche flags ; clarifier builder UIState unique |
| CODE | Aucun P0 obligatoire lot courant |
| OPS | Oracle Encoors : `GET ui-state/` sur session démo |

---

## Domaine 20 — mémoire gouvernée

### CIBLE 2.0 (résumé)

Mémoire **intra-conversation** gouvernée, structurée, sans verbatim brut ; projection `memory-summary`. Mémoire **inter-session** (`LearnerThemeMemory`) consolidée post-conversation, sans auto-promotion vers « validé humainement ». Injection prompt selon ordre contexte 2.0 — lot courant : intra-conv prioritaire. Verbatim ≠ mémoire.

### RÉEL OBSERVÉ (local)

**Implémenté et prouvé :**

- `SessionMemoryContract`, `build_session_memory` — `test_session_memory_contract.py` (5/5).
- `GET /hugo/sessions/{id}/memory-summary/` — `test_memory_summary_smoke.py` (cluster 10).
- Verbatim exclu du JSON mémoire (tests).
- `LearnerThemeMemory` + `memory_consolidator` — stockage inter-session.
- UIState inclut `session_memory` dict par tour.

**Partiel :**

- Endpoint mélange `session_memory` (intra) et `theme_memories` (inter) — doc `contrat_api_memory_summary_v1.md` livré ; ADR Option A `?scope=intra` **non implémenté**.
- Front ne consomme pas directement memory-summary (UIState seulement).

### Mini-table

| Objet / règle | CIBLE 2.0 | RÉEL OBSERVÉ | Statut | Action |
|---------------|-----------|--------------|--------|--------|
| SessionMemoryContract | Intra gouvernée | Implémenté + tests | ALIGNE | — |
| memory-summary API | Projection produit | GET livré | ALIGNE_DOC_PARTIEL | DOC/CODE |
| Verbatim exclu | Oui | Tests PASS | ALIGNE | — |
| Injection prompt LLM | Ordre contexte | Absente renderers | ABSENT | DOC ADR |
| LearnerThemeMemory | Inter-session | Modèle + consolidator | ALIGNE_DOC_PARTIEL | Hors tour |
| Injection LTM au tour | CIBLE future | Non observée | ABSENT | Couronne |
| Contrat doc v1 | — | `contrat_api_memory_summary_v1.md` | ALIGNE | — |

### ÉCARTS CONFIRMÉS

- Pas d’injection `SessionMemoryContract` dans prompts LLM.
- Endpoint unique intra+inter sans paramètre scope.

### A_VÉRIFIER

- Shape memory-summary Encoors — **oracle GET** authentifié.

### Actions derniers clusters

| Type | Action |
|------|--------|
| DOC | ADR injection prompt (C9-CODE-01) ; mise à jour ecarts-20 § cluster 10 |
| CODE | Option A `?scope=intra` si arbitrage CTO (P2) |
| OPS | pytest `test_memory_summary_smoke.py` en CI |

---

## Domaine 30 — référentiel documentaire / RAG

### CIBLE 2.0 (résumé)

RAG **question-driven**, renfort situé, documents actifs ; référentiel métier primaire. Hiérarchie contexte : état apprenant → mémoire → verbatim borné → overlay référentiel → documentaire. Pas de RAG vectoriel comme moteur de cours. Citations produit contrôlées.

### RÉEL OBSERVÉ (local)

**Implémenté et prouvé :**

- RAG lexical : `select_rag_chunks`, `should_use_rag`, `rag_support.py`, tests.
- Gating par posture/profile conversationnel.
- Citations : `rag_citations`, badge « Appui » front.
- Apps `referentials` vs `library` séparées.

**Partiel / absent :**

- pgvector : champ présent, **inactif runtime** (**ÉCART CONFIRMÉ**).
- Hiérarchie contexte 2.0 non contractualisée bout en bout.
- RAG dans UIState : engagement only, pas panneau dédié prod.

### Mini-table

| Objet / règle | CIBLE 2.0 | RÉEL OBSERVÉ | Statut | Action |
|---------------|-----------|--------------|--------|--------|
| RAG lexical gouverné | Renfort situé | `rag_support.py` | ALIGNE | — |
| RAG vectoriel | Option Couronne | pgvector inactif | ABSENT | Couronne |
| RAG × posture | Gating | Implémenté | ALIGNE_DOC_PARTIEL | DOC D2-M02 |
| Citations produit | Badge contrôlé | Front + back | ALIGNE | — |
| Hiérarchie contexte | Ordre 2.0 | Partielle | AMBIGU | DOC |
| Lien TrainerKnowledge→RAG apprenant | Consommation | **A_VÉRIFIER** | A_VÉRIFIER | Audit pipeline |

### ÉCARTS CONFIRMÉS

- RAG vectoriel non actif.
- Hiérarchie contexte non documentée comme contrat exécutable.

### A_VÉRIFIER

- Consommation runtime des items formateur validés dans RAG apprenant.
- Qualité/latence RAG Encoors.

### Actions derniers clusters

| Type | Action |
|------|--------|
| DOC | Contrat minimal RAG lexical (`ecarts — 30`) ; lien D2-M02 posture×RAG |
| CODE | Aucun vectoriel lot courant |
| OPS | Test régression `test_rag_support_tracing.py` |

---

## Domaine 31 — front apprenant, postures et bascule

### CIBLE 2.0 (résumé)

Front consomme UIState backend sans piloter le moteur. Trois grammaires UX (`learner_display_profile`). **Sélecteur posture** interactif et matrice états bascule SW-xx. `conversation_mode` affiché. Pas de recalcul local CTA/éligibilité.

### RÉEL OBSERVÉ (local)

**Implémenté et prouvé :**

- `ProdLearnerWorkspace`, CTA branchés backend (`engagementUiModel.js`).
- `ConversationModeBanner.vue` — lecture seule.
- `displayProfilePresets.js` — youth OK ; adult/pro partiel (Retex C5).
- API `POST .../set-posture/` backend (`SessionSetPostureView`).

**Partiel / absent :**

- Sélecteur posture « Mode de travail » — **ABSENT prod** (**ÉCART CONFIRMÉ** G2-02).
- Matrice SW-xx spec interface — non implémentée.

### Mini-table

| Objet / règle | CIBLE 2.0 | RÉEL OBSERVÉ | Statut | Action |
|---------------|-----------|--------------|--------|--------|
| UIState consommé | Pas recalcul local | Front tests | ALIGNE | — |
| CTA front | Backend-driven | ALIGNE | ALIGNE | — |
| conversation_mode affichage | Banner | Livré | ALIGNE_DOC_PARTIEL | — |
| 3 grammaires UX | youth/adult/pro | Partiel | ALIGNE_DOC_PARTIEL | CODE |
| Sélecteur posture | Interactif | Absent UI | ABSENT | CODE |
| set-posture API | PATCH/POST | POST backend | A_VÉRIFIER UI | OPS smoke |
| Matrice SW-xx | Spec UI | Absente | ABSENT | DOC |

### ÉCARTS CONFIRMÉS

- Sélecteur posture absent.
- Grammaires adult/pro incomplètes.

### A_VÉRIFIER

- Parcours bascule posture E2E navigateur (non smoke actuellement).

### Actions derniers clusters

| Type | Action |
|------|--------|
| DOC | Annexe spec interface SW-xx ; D2-M03 POST vs PATCH |
| CODE | Composant sélecteur posture (G2-02) — P1 |
| OPS | Playwright apprenant : bascule posture si UI livrée |

---

## Domaine 70 — évaluation, traces, preuves

### CIBLE 2.0 (résumé)

Branche terminale d’évaluation distincte du diagnostic. Trace minimale standardisable (`EvaluationTrace` conceptuel). Validation **humaine** — pas certification autonome. Objets Trace, Evidence, LearnerEvaluationRecord liés. Exports encadrants sans verbatim non partagé.

### RÉEL OBSERVÉ (local)

**Implémenté et prouvé :**

- Chaîne : readiness → request-evaluation → finalize-evaluation → generate-trace.
- `evaluation_trace_pivot_v1` — `test_evaluation_trace_minimal.py`, EVAL1 E2E v5.
- Validation trace tuteur : `POST /traces/{id}/validate/`.
- Disclaimer non certifiant dans pivot.
- Fiche : `fiche_trace_exploitable_pivot_v1.md`.

**Partiel :**

- Pivot v1 ≠ EvaluationTrace doctrinal complet (D2-M05 doc livré, dispersion objets).
- Criteria legacy generate-trace parfois vides.
- Circuits validation humaine parallèles (record vs trace).

### Mini-table

| Objet / règle | CIBLE 2.0 | RÉEL OBSERVÉ | Statut | Action |
|---------------|-----------|--------------|--------|--------|
| Branche terminale éval | Endpoints dédiés | views_sessions | ALIGNE | — |
| CTA éval UIState | Backend | cta_ui_state | ALIGNE | — |
| LearnerEvaluationRecord | OneToOne session | Modèle | ALIGNE_DOC_PARTIEL | — |
| Trace + Evidence | generate-trace | Implémenté | ALIGNE_DOC_PARTIEL | — |
| Pivot v1 | Agrégat stable | Tests E2E | ALIGNE_DOC_PARTIEL | — |
| EvaluationTrace doctrinal | Objet unique | Dispersé + pivot | AMBIGU | DOC |
| Certification autonome | Interdit | Absente | ALIGNE | — |
| Criteria trace rich | Complets | Parfois vides | PARTIEL | CODE P2 |

### ÉCARTS CONFIRMÉS

- Agrégat doctrinal vs pivot minimal.
- Payload criteria legacy incomplet.

### A_VÉRIFIER

- Chaîne EVAL1 Encoors authentifiée — **encoors_oracle.py** + credentials.
- Richesse trace sur données réelles prod.

### Actions derniers clusters

| Type | Action |
|------|--------|
| DOC | Maintenir fiche pivot ; ecarts-70 à jour |
| CODE | Enrichissement criteria si priorisé (P2) |
| OPS | Oracle EVAL1 Encoors (C10-OPS-01) |

---

## Domaine 80 — observabilité et qualité conversationnelle

### CIBLE 2.0 (résumé)

Signaux qualité persistés post-tour, **non exposés apprenant**. Observabilité admin/cohorte. Catalogue signaux canonique. Analytics LLM (D9bis) canal technique séparé, hors exports métier. Dashboards produit = Couronne.

### RÉEL OBSERVÉ (local)

**Implémenté et prouvé :**

- `ConversationQualitySignal`, `quality_tracker`, `analytics_state`.
- Observabilité base : `/internal/.../observability/` ORGADMIN+ — v3, tests.
- D9bis : modèles + endpoints SUPERADMIN — v4, tests.
- Absence D9bis dans exports métier — tests verrou.
- Note : `note_frontiere_observabilite_base_vs_d9bis.md`.

**Partiel / absent :**

- Catalogue signaux canonique exhaustif — **ABSENT**.
- `cohort_dashboard` — **A_VÉRIFIER** prod.
- Dashboards observabilité produit — Couronne.

### Mini-table

| Objet / règle | CIBLE 2.0 | RÉEL OBSERVÉ | Statut | Action |
|---------------|-----------|--------------|--------|--------|
| ConversationQualitySignal | Persisté | Modèle + tracker | ALIGNE_DOC_PARTIEL | DOC |
| analytics_state | Compteurs session | JSON session | ALIGNE | — |
| Observabilité base ORGADMIN | Session snapshot | v3 livré | ALIGNE | — |
| D9bis analytics LLM | Canal SUPERADMIN | v4 backend | ALIGNE_DOC_PARTIEL | — |
| Qualité visible apprenant | Interdit | Absente | ALIGNE | — |
| Catalogue signaux | Canonique | Ouvert | ABSENT | Couronne |
| Dashboards produit | CIBLE | Absents | ABSENT | Couronne |
| D9bis Encoors | Déployé | 404 probes | A_VÉRIFIER | OPS |

### ÉCARTS CONFIRMÉS

- Catalogue signaux non livré.
- Encoors sans routes v3/v4 (probes cluster 8).

### A_VÉRIFIER

- Encoors observabilité/D9bis authentifié.
- Métriques cohorte réelles.

### Actions derniers clusters

| Type | Action |
|------|--------|
| DOC | Catalogue signaux backlog Couronne ; note frontière (livré) |
| CODE | Aucun dashboard produit lot courant |
| OPS | Oracle internal routes Encoors avec JWT SUPERADMIN |

---

## Domaine 90 — confidentialité, multi-tenant, rôles

### CIBLE 2.0 (résumé)

Multi-tenant strict (RLS + filtres app). Verbatim non partagé invisible aux encadrants. Matrice rôle × visibilité × partage. COORDO personae cible. Frontière ORGADMIN vs SUPERADMIN. Pas d’exposition P0/verbatim brut aux exports métier.

### RÉEL OBSERVÉ (local)

**Implémenté et prouvé :**

- `organisation_id` partout ; middleware `TenantRLSMiddleware`.
- RLS policies : `hugo_session`, `trace`, `evidence`, `export_run` — tests.
- RLS SQL rôle applicatif `hugo_app_tenant_test` — **PASS** cluster 10.
- Isolation API cross-tenant 404 — tests.
- B1-01 timeline : verbatim masqué si `share_verbatim=false` — pytest + Playwright cluster 8.
- Pack D2-M07 : `test_d2_m07_confidentiality_oracles.py` (10 tests).
- Matrice v2 : `matrice_role_visibilite_v2.md`.

**Partiel :**

- D2-M12 ORGADMIN/SUPERADMIN exports — ADR maintien recommandé.
- COORDO absent (**ÉCART CONFIRMÉ**).

### Mini-table

| Objet / règle | CIBLE 2.0 | RÉEL OBSERVÉ | Statut | Action |
|---------------|-----------|--------------|--------|--------|
| Multi-tenant app | organisation_id | Modèles | ALIGNE | — |
| RLS Postgres | Policies actives | Migrations + tests | ALIGNE local | OPS prod |
| RLS rôle applicatif | Non-superuser | Test PASS local | ALIGNE local | A_VÉRIFIER prod |
| Verbatim non partagé | Masqué tuteur | Backend + smoke UI | ALIGNE | — |
| Matrice rôles | Complète | v2 doc + tests partiels | ALIGNE_DOC_PARTIEL | DOC |
| COORDO | Personae | Absent | ABSENT | Couronne |
| ORGADMIN vs SUPERADMIN | Distinct | is_admin_like partagé exports | AMBIGU | ADR |
| EXIF Evidence | Strip | test_evidence_exif | ALIGNE local | A_VÉRIFIER prod |

### ÉCARTS CONFIRMÉS

- COORDO non implémenté.
- Frontière exports org ORGADMIN/SUPERADMIN ouverte (D2-M12).

### A_VÉRIFIER

- RLS prod Encoors (rôle DB réel).
- EXIF strip prod.

### Actions derniers clusters

| Type | Action |
|------|--------|
| DOC | Fiche RLS prod Encoors (C10-DOC-01) ; matrice v2 maintenue |
| CODE | D2-M12 si restriction export technique (P2) |
| OPS | Oracle Encoors + fiche rôle Postgres prod |

---

## Domaine 100 — exports, preuves, Qualiopi lite

### CIBLE 2.0 (résumé)

Exports métier (JSON/CSV traces, bundle ZIP audit) pour ORGADMIN, sans verbatim non partagé ni analytics LLM. Taxonomie exports E1–E6. Qualiopi **lite** = preuve documentaire, pas label certifiant. Export debug md réservé superadmin.

### RÉEL OBSERVÉ (local)

**Implémenté et prouvé :**

- `ExportRun` JSON/CSV + pivot v1 — E2E O1 v5.
- `EvidenceBundleView` ZIP — tests E3/E4.
- Guards rôle : ORGADMIN+ ; front `isOrgAdminLike` — smoke cluster 8.
- D9bis absent exports métier — tests.
- Trainer export evaluation-records séparé.
- Fiche pivot + exports référence (cluster 9–10).

**Partiel / absent :**

- Taxonomie E1–E6 — partielle (D2-M11).
- Export debug md — **ABSENT** (G3-03 cible).
- Encoors parité — **A_VÉRIFIER**.

### Mini-table

| Objet / règle | CIBLE 2.0 | RÉEL OBSERVÉ | Statut | Action |
|---------------|-----------|--------------|--------|--------|
| ExportRun JSON/CSV | ORGADMIN | apps/exports | ALIGNE local | A_VÉRIFIER Encoors |
| EvidenceBundle | ZIP Qualiopi lite | quality/views | ALIGNE local | A_VÉRIFIER Encoors |
| Pivot dans export | trace_rich_v1 | Tests | ALIGNE | — |
| Permissions rôle | ORGADMIN | is_admin_like | ALIGNE | ADR D2-M12 |
| D9bis hors exports | Séparation | Tests verrou | ALIGNE | — |
| Taxonomie E1–E6 | Doc complète | Partielle | ALIGNE_DOC_PARTIEL | DOC |
| Export debug md | SUPERADMIN | Route absente | ABSENT | Couronne |
| UI exports ORGADMIN | CTA group | Playwright PASS | ALIGNE | — |

### ÉCARTS CONFIRMÉS

- Export debug md absent.
- Taxonomie exports incomplète.

### A_VÉRIFIER

- Payload ExportRun/bundle Encoors vs local (oracle O1).

### Actions derniers clusters

| Type | Action |
|------|--------|
| DOC | Compléter D2-M11 taxonomie ; fiche pivot (livré) |
| CODE | export-md si requis superadmin (Couronne) |
| OPS | Oracle O1 Encoors ; smoke export click (optionnel) |

---

## Domaine 110 — interfaces formateur / tuteur

### CIBLE 2.0 (résumé)

Surfaces prod encadrants : tuteur timeline/partage filtré, formateur base connaissances, ORGADMIN exports/pilotage. Parcours apprenant prod stable. Trois grammaires affichage. Pas de verbatim non partagé en UI encadrant. Workflows dialogiques formateur (C1) = cible partielle.

### RÉEL OBSERVÉ (local)

**Implémenté et prouvé :**

- Apprenant : `ProdLearnerWorkspace`, `/app*`.
- Tuteur : `/app/tutor/*`, timeline API, smoke Playwright cluster 8 (4/4).
- Formateur : `/app/trainer/knowledge` list+validate — smoke + F1 E2E.
- ORGADMIN : exports UI group — smoke.
- ConductProfiles, TutorPrompts admin.
- Router guards encadrant — tests front.

**Partiel :**

- Ingest formateur dialogique (C1) — surface list/validate seulement.
- 3 grammaires UX rendu partiel (D2-M08).
- Choix profil par formateur (IFT-042) — absent.
- Encoors surfaces encadrants — **A_VÉRIFIER**.

### Mini-table

| Objet / règle | CIBLE 2.0 | RÉEL OBSERVÉ | Statut | Action |
|---------------|-----------|--------------|--------|--------|
| Parcours apprenant prod | Stable | ProdLearnerWorkspace | ALIGNE | — |
| Timeline tuteur B1-01 | Filtrée | API + smoke UI | ALIGNE local | A_VÉRIFIER Encoors |
| Interface formateur | Knowledge | list/validate | ALIGNE_DOC_PARTIEL | CODE C1 |
| Exports ORGADMIN UI | CTA | Playwright | ALIGNE | — |
| Profils affichage 3 UX | Rendu complet | Partiel | ALIGNE_DOC_PARTIEL | CODE |
| Workflow dialogique F1–F4 | Complet | Objets seuls | ABSENT | Couronne/C1 |
| Testeur / LearnerDetail | Hors démo | Présent | ALIGNE | — |

### ÉCARTS CONFIRMÉS

- Parcours formateur dialogique incomplet.
- Grammaires adult/pro partielles.

### A_VÉRIFIER

- UI encadrants sur `https://hugo.encoors.com` (CORS, parité).

### Actions derniers clusters

| Type | Action |
|------|--------|
| DOC | D2-M09 checklist B1 ; ecarts-110 § smokes |
| CODE | Grammaires UX adult/pro ; ingest C1 si priorisé |
| OPS | Playwright Encoors ou staging aligné ; E2E tuteur riches |

---

## Synthèse finale — derniers clusters (DOC / CODE / OPS)

Regroupement des **restes assumés** après clusters 1–10 (vague runtime/OPS clôturée). Priorisation pour une **vague Couronne / prod Encoors**, pas réouverture du noyau local déjà convergé.

### DOC

| ID | Domaine | Action | Sources |
|----|---------|--------|---------|
| INV-DOC-01 | 10 | Tableau posture→RAG→maturité→CTA (D2-M02) | Matrice §10, ecarts-10 |
| INV-DOC-02 | 10 | Flag v17 fiche flags (D2-M10) | ecarts-10, 08_FLAGS |
| INV-DOC-03 | 20 | ADR injection SessionMemoryContract prompt | cluster 9, ADR C9-CODE-01 |
| INV-DOC-04 | 30 | Contrat hiérarchie contexte lexical | ecarts-30 |
| INV-DOC-05 | 31 | Annexe matrice SW-xx bascule posture | specs interface 2.0 |
| INV-DOC-06 | 90 | Fiche RLS prod Encoors | cluster 10 C10-DOC-01 |
| INV-DOC-07 | 100 | Taxonomie exports E1–E6 complète (D2-M11) | ecarts-100 |
| INV-DOC-08 | 80 | Catalogue signaux (Couronne) | ecarts-80 |

### CODE

| ID | Domaine | Priorité | Action | Sources |
|----|---------|----------|--------|---------|
| INV-CODE-01 | 31 | P1 | Sélecteur posture prod (G2-02) | ecarts-31, matrice §31 |
| INV-CODE-02 | 31 | P2 | Grammaires adult/pro complètes | D2-M08, Retex C5 |
| INV-CODE-03 | 20 | P2 | `?scope=intra` memory-summary (Option A ADR) | adr_c9_code02 |
| INV-CODE-04 | 110 | P2 | Ingest/validation formateur C1 (si priorisé) | ecarts-110, ecarts-40 |
| INV-CODE-05 | 90 | P2 | D2-M12 export technique SUPERADMIN-only (si arbitrage) | adr_c9_code03 |
| INV-CODE-06 | 70 | P2 | Enrichissement criteria generate-trace | ecarts-70 |

### OPS

| ID | Domaine | Priorité | Action | Sources |
|----|---------|----------|--------|---------|
| INV-OPS-01 | 90/70/100 | P0 | Oracle Encoors authentifié EVAL1+O1 | encoors_oracle.py, cluster 8–10 |
| INV-OPS-02 | 90 | P0 | Audit RLS prod rôle applicatif Encoors | setup_rls_app_role.sql, cluster 10 |
| INV-OPS-03 | 90/110 | P1 | CI : pytest RLS + memory smoke + Playwright smokes | cluster 10 |
| INV-OPS-04 | 80 | P1 | Oracle routes internal v3/v4 SUPERADMIN Encoors | cluster 8 probes |
| INV-OPS-05 | 10/31 | P2 | Smoke UI bascule posture (post INV-CODE-01) | ecarts-31 |
| INV-OPS-06 | 110 | P2 | Parcours Playwright apprenant CTA éval/synthèse | gap cluster 8 §PARTIEL |

---

## Bilan transversal

| Statut global | Domaines |
|-------------|----------|
| **Noyau local convergé** (backend + tests + smokes de base) | 10, 20, 70, 90, 100 — avec réserves doc |
| **Opérationnel partiel** (objets réels, UX/couronne ouverte) | 30, 31, 80, 110 |
| **Blocage prod** | Encoors authentifié, RLS prod, flags — **A_VÉRIFIER** |
| **Hors lot courant assumé** | RAG vectoriel, intercalaires, dashboards, COORDO, certification autonome |

**Prochaine sortie utile CTO :** exécuter INV-OPS-01/02 (Encoors + RLS prod), arbitrer INV-CODE-01 (sélecteur posture) et INV-CODE-03 (scope memory-summary), puis boucler DOC D2-M02/D2-M10/D2-M11.
