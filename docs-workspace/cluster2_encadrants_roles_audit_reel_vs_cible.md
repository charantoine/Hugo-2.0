# Cluster 2 — Audit encadrants & rôles (réel vs cible)

> Ce document résume le cluster d'audit sur les domaines 90/100/110
> (rôles, confidentialité, exports, interfaces encadrants) en lien avec
> les domaines 70/40/50/60/31. Il s'appuie sur la spec 2.0, les écarts
> par domaine et la matrice runtime vs cible, sans les remplacer.
> Il sert de référence locale pour le plan de convergence CTO.

**Sources mobilisées :** `plan_documentation_cto_convergence_hugo.md` (étapes 5–8), `spec_canonique_hugo_2_0.md` (§29.6 matrice rôles), `specs interface 2.0.md`, `complements_spec_2_0_depuis_anterieurs.md`, `Cluster 2 — Oracles de test par persona + validation courte.md`, `cluster2_matrice_runtime_vs_cible.md` V3, `design_D2-M07_D2-M08_profils_grammaires_matrice_roles.md`, `design_D2-M06_D2-M11_exports_analytics.md`, `ecarts — 90/100/110/70/40/50/60/31*.md` ; code `hugo_back` (routes, modèles, tests pytest) ; front `hugo-hugolucia/frontend_1.8` (routes, surfaces tester).

**Périmètre runtime :** audit **local** (SQLite, tests pytest). Toute inférence prod Encoors / RLS Postgres = **A_VÉRIFIER**.

---

## 3.1. Réel confirmé — parcours encadrants et rôles

### Tuteur (`Role.TUTOR`)

| Dimension | CIBLE (spec 2.0) | RÉEL OBSERVÉ (code/runtime local) | ÉCART CONFIRMÉ | A_VÉRIFIER |
|---|---|---|---|---|
| Surfaces UI | Progression, signaux blocage, traces partagées, synthèses/éval partageables, vues cohorte/apprenant | Layout **tester** : `/dashboard` → `/group/:id` → `/group/:id/learner/:id` avec `TutorLearnerView` (timeline, compétences, validation trace) ; parcours prod apprenant `/app` séparé | Pas de surface tuteur dédiée en layout **prod** ; encadrant sur shell tester/POC | Parité prod Encoors sur timeline B1-01 |
| Actions backend | Lire, commenter, recommander, valider traces partageables | `GET /dashboard/groups/{gid}/learners/`, `.../timeline/`, `.../competences/` ; `POST /traces/{id}/validate/` si `TutorLearnerLink` + membership groupe | Export Felix-ready affiché côté front groupe (`GroupView`) mais **403 backend** (`ExportRunView` exige `is_admin_like`) | Boutons export tuteur en prod distante |
| Confidentialité verbatim | Pas d'accès libre au non-partagé | Si `share_verbatim=false` : `messages[]` vide, `first_learner_message` vide (oracle B1-01, `test_d2_m07`, `test_cluster3`) | — | Prod |
| P0 / TurnState | Interdit en surface tuteur | Sous partage : `pilotage` agrégé produit-safe (`_pilotage_from_learner_payload`) ; pas de `turn_state`/`p0_debug` dans réponse timeline (B1-02) | Test legacy `test_tutor_access_control` peut encore viser `p0_debug` | — |
| Multi-tenant | Isolation stricte org | Filtres `organisation_id` sur sessions/traces ; visibilité apprenants via `learner_ids_visible_in_group` + `TutorLearnerLink` | — | RLS Postgres prod |

### Formateur (`Role.TRAINER`)

| Dimension | CIBLE | RÉEL OBSERVÉ | ÉCART CONFIRMÉ | A_VÉRIFIER |
|---|---|---|---|---|
| Surfaces UI | Documents, questionnaire dialogique, items connaissance, validation, exports métier | Pas de workspace formateur prod dédié ; APIs `hugo/trainer/*` ; admin groupe (`GroupAdminDetailView`) : upload docs, types knowledge ; config référentiel (`GroupReferentialConfigView`) ; `ConductProfilesView`, `TutorPromptsView` (tester) | Surface formateur = **fragment tester/back-office**, pas parcours 2.0 stabilisé (DSP-05 design D2-M08) | Qui accède à `/groups-admin` en prod |
| Actions backend | Uploader, structurer, valider `TrainerKnowledgeItem`, rattacher référentiel, exporter | `GET/POST .../elicitation/`, `.../ingest/`, `.../knowledge/{id}/validate/` ; `GET/POST .../evaluation-records/` + export CSV/JSON (`_can_manage_evaluations` = TRAINER/ORGADMIN/SUPERADMIN) | Endpoints elicitation/ingest/validate : **`IsAuthenticated` seulement**, pas de garde `Role.TRAINER` explicite | Tests négatifs LEARNER sur trainer APIs |
| Accès contenu apprenant | Interdit non-partagé | Pas de route trainer lisant verbatim session ; accès dashboard tuteur-like possible via `TUTOR_ROLES` si COORDO/TRAINER liés | TRAINER dans `TUTOR_ROLES` → peut voir timeline si link tuteur (hybridation rôles) | Intention produit formateur vs tuteur |
| Exports | Exports métier bornés | Export éval formateur : filtre `shared_with_tutor=true` (test E2) ; **ExportRun/EvidenceBundle** réservés `is_admin_like` (ORGADMIN/SUPERADMIN) malgré `isAdminLike` front incluant TRAINER | **Décalage front/back** sur exports Felix-ready pour TRAINER | — |

### Coordinateur (`Role.COORDO`)

| Dimension | CIBLE | RÉEL OBSERVÉ | ÉCART CONFIRMÉ | A_VÉRIFIER |
|---|---|---|---|---|
| Surfaces | Vues métier à préciser | Rôle en base ; traité comme **tuteur-like** (`TUTOR_ROLES` dans `access_control.py`) : même règles visibilité/validation trace | **Aucune surface UI ou parcours dédié** | Cas métier coordinateur en prod |
| Actions | Coordination / validation futures | Timeline + validate trace si link ; pas d'orchestrateur coordo distinct | Rôle **doctrinal non matérialisé** (CONF-15, D9) | — |

### ORGADMIN (`Role.ORGADMIN`)

| Dimension | CIBLE | RÉEL OBSERVÉ | ÉCART CONFIRMÉ | A_VÉRIFIER |
|---|---|---|---|---|
| Surfaces UI | Admin minimale, users/groupes, exports | `/groups-admin`, `/users`, `/group/:id` exports, tutor-links, profils affichage groupe, documents | Admin **partielle** (pas DELETE users confirmé) | Capacités prod |
| Actions backend | Admin + exports filtrés, sans lecture libre non-partagé | `is_admin_like` → `ExportRun`, `EvidenceBundle` ; gestion users (POST/PATCH LEARNER/TUTOR) ; pas de route timeline sans link tuteur pour ORGADMIN sur apprenant non-admin | ORGADMIN **ne voit pas** verbatim via timeline sans mécanisme de partage (aligné cible) ; accès admin groupe ≠ lecture masse verbatim | Matrice permissions admin exhaustive |
| Exports | Capacités bornées | ZIP Qualiopi lite (`traces.json` métadonnées seulement) ; CSV/JSON `trace_rich_v1` tenant-scoped (tests cross-tenant G3-02) | Bundle **non riche** ; pas de `LearnerEvaluationRecord` dans ZIP | Contenu ZIP prod |
| Multi-tenant | Strict | Filtre `organisation_id` partout ; tests cross-tenant exports | — | RLS prod effective |

### Superadmin technique (`Role.SUPERADMIN`)

| Dimension | CIBLE | RÉEL OBSERVÉ | ÉCART CONFIRMÉ | A_VÉRIFIER |
|---|---|---|---|---|
| Surfaces | Supervision technique sous contraintes | Même `is_admin_like` qu'ORGADMIN sur exports ; Django admin ; routes tester non gardées par rôle dans le router Vue | **Pas de frontière applicative** ORGADMIN vs SUPERADMIN dans le code audité (D2-M12 ouvert) | Superadmin prod vs ORGADMIN |
| Accès contenu apprenant | Pas de lecture applicative libre | Pas de route `export-md` / debug P0 pour ORGADMIN (test G3-03) ; `LearnerDetailView` (modales debug) réservé espace **propre** apprenant dans `LearnerSpaceView` | Surface debug P0 existe en tester pour **soi-même**, pas garde superadmin explicite | Flags `VITE_P0_DEBUG_ENABLED` prod |
| Exports debug | Réservés superadmin technique (cible) | Absence modèle `ConversationTurnLLMAnalysis` ; pas d'endpoint export-md | Aligné par **absence** | D9bis couronne |

---

## 3.2. Réel confirmé — exports / preuves / Qualiopi lite (domaine 100)

### Capacités réelles du runtime local

| Artefact | Endpoint / modèle | Format / contenu | Rôle autorisé (backend) | Filtre confidentialité |
|---|---|---|---|---|
| **ExportRun** | `POST /exports/run/`, `GET /exports/download/{run_id}/` | CSV pivot trace×item (`felix_ready_trace_item_*.csv`) ou JSON **`trace_rich_v1`** (`payload_structured` par trace) | `is_admin_like` (ORGADMIN, SUPERADMIN) | `organisation_id` ; période ; `group_ids` ; tests : pas de tokens P0 interdits dans export JSON |
| **EvidenceBundle (Qualiopi lite)** | `POST /quality/qualiopi/evidence-bundle/` | ZIP : `traces.json` (id, session, learner, dates), `audit_log.json`, `referentials.json`, `active_documents.json`, `summary.txt` | `is_admin_like` | Tenant ; pas de verbatim ; pas de fichiers Evidence binaires dans le ZIP local |
| **Export évaluations formateur** | `GET /hugo/trainer/evaluation-records/export/` | CSV ou JSON | TRAINER, ORGADMIN, SUPERADMIN | Uniquement `shared_with_tutor=true` |
| **Evidence (upload)** | `POST /evidence/` | Fichier stocké ; lien obligatoire `trace_id` **ou** `session_id` | Authentifié ; session = propre session apprenant | `organisation_id` ; contrainte DB `evidence_trace_or_session` |
| **Trace** | Modèle + validation | `trace_rich_v1` via export JSON ; métadonnées dans bundle | — | Validée par tuteur-like si accès groupe |

### Rattachement preuves / traces / bundles

- **Trace** : liée à `HugoSession` ; alimente exports CSV/JSON et métadonnées bundle.
- **Evidence** : FK `trace` ou `session` ; **pas d'Evidence orpheline** au niveau modèle (`CheckConstraint` `evidence_trace_or_session`) ; création API refuse sans lien valide.
- **EvidenceBundle** : agrégat audit **lite** — **ne produit pas** une `EvaluationTrace` 2.0 complète (D2-M05, ecarts-100 §4.6).
- **ExportRun** : journalise `ExportRun` + audit ; régénération depuis params stockés.

### Points explicites (discipline de vérité)

| Question | Verdict |
|---|---|
| Bundle « riche » existe-t-il ? | **Non en local** — ZIP minimal métadonnées ; pas de contenu conversationnel, pas de pièces Evidence embarquées |
| Suppression EXIF / GPS | **Docstring et modèle** annoncent EXIF stripped + GPS opt-in ; **code `views_evidence.py`** enregistre le fichier tel quel + meta `gps_opt_in` — **ÉCART CONFIRMÉ** : pas de strip EXIF implémenté (CONF-22) |
| Invariant « aucune Evidence orpheline » | **Oui** : contrainte SQL + validation API à la création ; pas de job de réconciliation audité |
| D9bis analytics LLM | **Absent** (modèle inexistant, tests verrouillés) — couronne |
| Permissions exports vs front | **ÉCART CONFIRMÉ** : `GroupView.vue` expose exports à TUTOR/TRAINER/COORDO ; backend 403 sauf ORGADMIN/SUPERADMIN |

**A_VÉRIFIER :** contenu exact bundles prod Encoors ; RLS sur tables export/evidence ; async export si flag distant.

---

## 3.3. Mini-matrice réelle « rôle × voit / peut / ne voit pas »

Alignée sur la matrice canonique 2.0 (`spec_canonique_hugo_2_0.md` §29.6) et design D2-M07 §B.2.

| Rôle | Ce qu'il voit (RÉEL) | Ce qu'il peut faire (RÉEL) | Écarts vs matrice canonique | Points A_VÉRIFIER |
|---|---|---|---|---|
| **Apprenant** | `/app` : conversation, UIState, CTA, progression via contrats backend filtrés | Converser, CTA synthèse/éval si éligible, upload Evidence sur sa session | Aligné sur confidentialité prod `/app` | UIState prod Encoors |
| **Tuteur** | Timeline tester : sessions/traces métadonnées ; verbatim + `pilotage` **si** `share_verbatim` ; compétences `LearnerState` | Valider trace si link ; lire cohorte filtrée | Pas de surface prod dédiée ; exports UI visibles mais **403 API** ; pas de commentaire structuré éval côté UI tuteur | Prod B1-01 |
| **Formateur** | Items `TrainerKnowledgeItem` via API ; docs groupe admin ; pas de timeline apprenant sans link tuteur | Elicitation, ingest, validate knowledge ; export éval partagées | Endpoints trainer **sans garde rôle** sur elicitation/ingest ; pas d'UI formateur prod ; orchestrateur formateur 50 = **CIBLE** | LEARNER sur `/hugo/trainer/*` |
| **Coordinateur** | Idem tuteur-like si link | Idem tuteur-like | Rôle canonique **non différencié** | Périmètre métier coordo |
| **ORGADMIN** | Users, groupes, config, exports ; pas verbatim masse | CRUD users partiel, tutor-links, exports tenant, bundle Qualiopi | Admin incomplète ; frontière superadmin floue | DELETE user ; prod admin |
| **Superadmin technique** | Idem ORGADMIN + Django admin | Idem exports ; maintenance Django | Pas de séparation stricte ORGADMIN/superadmin dans code ; pas d'export debug P0 dédié superadmin seul | D2-M12 ; prod |

### Risques confidentialité (runtime local)

1. **Verbatim sous partage** : si `share_verbatim=true`, contenu message complet exposé au tuteur lié — conforme au modèle P, mais dépend du flag session.
2. **Trainer APIs ouvertes** : tout utilisateur authentifié de l'org pourrait appeler elicitation/ingest (non prouvé bloqué).
3. **Front exports** : UI suggère des droits que le backend refuse (TUTOR/TRAINER) — risque UX et contournement tenté.
4. **EXIF** : photos Evidence peuvent conserver métadonnées embarquées — écart cible CONF-22.
5. **RLS Postgres** : isolation reposant sur filtres applicatifs + tests SQLite — **A_VÉRIFIER** en prod.

---

## 3.4. Décisions documentaires et doctrinales

| Décision | Domaine | Lot CTO | Statut | Commentaire |
|---|---|---|---|---|
| **D2-M01** — `conversation_mode` dans UIState | 10/110 | Vague 2 | **OK** | Livré cluster 4 ; contexte encadrants indirect |
| **D2-M02** — Tableau posture → RAG → maturité → CTA | 10 | Vague 3 | **OK (cible)** | Ouvert ; peu d'impact direct encadrants |
| **D2-M03** — set-posture POST vs PATCH | 10/31 | Vague 2–3 | **OK** | Hors parcours encadrant immédiat |
| **D2-M04** — memory-summary schéma | 20 | Vague 1–2 | **OK** | Mémoire non exposée encadrants |
| **D2-M05** — Mapping EvaluationTrace | 70/100/110 | Vague 2 | **OK, à compléter** | Doc livrée ; bundle ≠ EvaluationTrace — maintenir garde-fou |
| **D2-M06** — D9bis export analytique LLM | 80/100 | **Couronne** | **OK (cible)** | Absent code — ne pas planifier en vague encadrants |
| **D2-M07** — Matrice rôle × visibilité | 90 | Vague 2 | **À corriger/compléter** | B1-01/B1-02 alignés ; matrice doc vs front exports à synchroniser ; RLS A_VÉRIFIER |
| **D2-M08** — Profils affichage | 110/31 | Vague 2 | **OK partiel** | Backend OK ; surface formateur absente (DSP-05) |
| **D2-M09** — Checklist parcours tuteur B1 | 60/110 | Vague 3 | **À compléter** | Backend local OK ; prod + UI prod manquants |
| **D2-M10** — Flag v17 doc | 10 | Vague 3 | **OK** | Contexte P0, pas surface encadrant |
| **D2-M11** — Taxonomie export E1–E6 | 100 | Vague 2 | **À corriger** | Exports existent ; permissions rôle et front/back à réaligner |
| **D2-M12** — Frontière ORGADMIN/superadmin | 90/100 | Vague 3 | **À corriger** | Code ne distingue pas ; export-md absent (OK) |
| **D5–D7** (ecarts-90) — Verbatim privé, UIState filtré, pas P0 front | 90 | Vague 2 | **OK** | Confirmé local ; prod A_VÉRIFIER |
| **D8–D11** (ecarts-90) — Rôles inégaux, coordo ouvert, admin partiel, superadmin contraint | 90/110 | Vague 2–3 | **OK** | Toujours valides au vu du runtime |
| **D12–D16** (ecarts-100) — Partage avant export, ORGADMIN borné, ne pas survendre traces | 100 | Vague 2 | **OK** | Bundle lite confirmé |
| **D13–D15** (ecarts-100) — Visibilité vs export, multi-tenant deux niveaux preuve | 90/100 | Vague 2 | **OK** | RLS prod reste A_VÉRIFIER |
| **DD-07–DD-14** (ecarts-110) — Couches tuteur/formateur, surfaces partielles, pas route progress | 110 | Vague 3 | **OK** | `GET /progress` non prouvé ; dashboard = partiel |

---

## 3.5. Backlog priorisé DOC / CODE / OPS — cluster encadrants & rôles

| ID | Type | Domaine | Description courte | Niveau de vérité visé | Dépendance runtime distant / RLS / flags | Priorité | Lot plan CTO |
|---|---|---|---|---|---|---|---|
| ENC-DOC-01 | DOC | 90 | Finaliser matrice rôle × données dans ecarts-90 en citant B1-01/B1-02 et décalage exports front/back | ÉCART À RÉDUIRE | NON | P0 | Vague 2 noyau |
| ENC-DOC-02 | DOC | 100 | Mettre à jour ecarts-100 : bundle lite confirmé, EXIF non implémenté, pas EvaluationTrace dans ZIP | RÉEL OBSERVÉ | NON | P0 | Vague 2 noyau |
| ENC-DOC-03 | DOC | 110 | Documenter parcours encadrants = surfaces **tester** vs cible prod (DD-12) | ÉCART À RÉDUIRE | OUI | P1 | Vague 3 noyau |
| ENC-DOC-04 | DOC | 90/100 | Rédiger frontière ORGADMIN vs SUPERADMIN (D2-M12) avec liste endpoints partagés | CIBLE | OUI | P1 | Vague 3 noyau |
| ENC-DOC-05 | DOC | 70/100 | Relier export formateur éval ↔ mapping EvaluationTrace sans survente bundle | CIBLE | NON | P1 | Vague 2 noyau |
| ENC-DOC-06 | DOC | 50/60 | Statuer orchestrateurs formateur/tuteur : APIs partielles, pas de script UX complet | RÉEL OBSERVÉ | NON | P2 | Vague 3 noyau |
| ENC-CODE-01 | CODE | 90 | Aligner `GroupView.canRunExports` sur `is_admin_like` backend (masquer boutons TUTOR/TRAINER) | ÉCART À RÉDUIRE | NON | P0 | Vague 2 noyau |
| ENC-CODE-02 | CODE | 90 | Ajouter garde `Role.TRAINER` (± ORGADMIN) sur elicitation/ingest/knowledge validate | ÉCART À RÉDUIRE | NON | P0 | Vague 2 noyau |
| ENC-CODE-03 | CODE | 90 | Tests négatifs : LEARNER/TUTOR sur `/hugo/trainer/*` et TUTOR sur `/exports/run/` | RÉEL OBSERVÉ | NON | P0 | Vague 2 noyau |
| ENC-CODE-04 | CODE | 100 | Implémenter strip EXIF à l'upload Evidence ou corriger docstrings/modèle | ÉCART À RÉDUIRE | NON | P1 | Vague 2 noyau |
| ENC-CODE-05 | CODE | 100 | Test explicite G3-02 EvidenceBundle cross-tenant (alias D2-M07) | RÉEL OBSERVÉ | NON | P1 | Vague 2 noyau |
| ENC-CODE-06 | CODE | 110 | Recaler `test_tutor_access_control` : `pilotage` vs `p0_debug` legacy | RÉEL OBSERVÉ | NON | P1 | Vague 2 noyau |
| ENC-CODE-07 | CODE | 60/110 | Route/guard front : accès `/dashboard` réservé rôles encadrants (pas LEARNER seul) | ÉCART À RÉDUIRE | NON | P1 | Vague 3 noyau |
| ENC-CODE-08 | CODE | 110 | Surface tuteur minimale layout prod (timeline read-only) ou décision explicite de reporter | CIBLE | OUI | P1 | Vague 3 noyau |
| ENC-CODE-09 | CODE | 40/110 | Surface formateur minimale : liste/validation `TrainerKnowledgeItem` hors tester | CIBLE | NON | P2 | Vague 3 noyau |
| ENC-CODE-10 | CODE | 70 | UI tuteur : consultation `LearnerEvaluationRecord` partagés (lecture seule) | CIBLE | NON | P2 | Vague 3 noyau |
| ENC-CODE-11 | CODE | 90/100 | Séparer permissions SUPERADMIN vs ORGADMIN sur exports sensibles (si cible l'exige) | CIBLE | OUI | P2 | Vague 3 noyau |
| ENC-CODE-12 | CODE | 100 | Enrichir bundle Qualiopi : inclure métadonnées Evidence (sans binaire) — si validé produit | CIBLE | NON | P2 | Couronne |
| ENC-OPS-01 | OPS | 90 | Oracle B1-01/B1-02 dans template audit runtime (tuteur timeline) | RÉEL OBSERVÉ | OUI | P0 | Vague 2 noyau |
| ENC-OPS-02 | OPS | 100 | Oracle E3/E4/G3-02 exports (learner 403, cross-tenant) — checklist C7 | RÉEL OBSERVÉ | NON | P0 | Vague 2 noyau |
| ENC-OPS-03 | OPS | 90 | Procédure « ne jamais conclure prod = local » pour RLS et bundles ZIP | A_VÉRIFIER | OUI | P0 | Vague 2 noyau |
| ENC-OPS-04 | OPS | 110 | Scénarios persona B1/C1/D1/G3 dans oracles cluster 2 — rejouer post-patch exports UI | ÉCART À RÉDUIRE | OUI | P1 | Vague 3 noyau |
| ENC-OPS-05 | OPS | 90 | Audit Encoors dédié : timeline tuteur + permissions exports ORGADMIN | A_VÉRIFIER | OUI | P1 | Vague 3 noyau |
| ENC-OPS-06 | OPS | 100 | Checklist pre-release : grep `export-md`, `ConversationTurnLLMAnalysis`, tokens P0 dans exports | RÉEL OBSERVÉ | NON | P1 | Vague 2 noyau |
| ENC-OPS-07 | OPS | 31/110 | Matrice bascule prod/tester et rôles autorisés sur routes tester | ÉCART À RÉDUIRE | NON | P2 | Vague 3 noyau |

---

## Synthèse exécutive (CTO)

**Réel confirmé local :** noyau confidentialité tuteur **B1-01/B1-02** implémenté et testé ; isolation tenant sur exports ; bundle Qualiopi **lite** ; exports Felix-ready **ORGADMIN/SUPERADMIN** ; parcours encadrants surtout **shell tester**, pas prod.

**Écarts prioritaires :** (1) décalage UI exports vs backend ; (2) endpoints trainer sans garde rôle ; (3) EXIF non traité ; (4) coordinateur et formateur prod non matérialisés ; (5) frontière ORGADMIN/superadmin absente.

**Prochaine sortie utile :** exécuter ENC-CODE-01 à 03 + ENC-OPS-01/02 en vague 2, puis parcours tuteur prod (ENC-CODE-08) en vague 3 après oracle Encoors (ENC-OPS-05).
