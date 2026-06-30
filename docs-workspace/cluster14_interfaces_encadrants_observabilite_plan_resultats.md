# Cluster 14 — Interfaces encadrants, COORDO & observabilité produit (plan)

> Date : 2026-06-18  
> Scope : domaines **110**, **90** (COORDO), **80** (produit), **100** (exports côté encadrants)  
> Garde-fou : `REFERENCE_CONVERGENCE_HUGO_REEL_VS_2_0_GARDEFOU.md`  
> Prérequis : runtime clusters 1–11, RAG cluster 13, plan cluster 12 apprenant — **sans rouvrir moteur / RAG / D9bis riche**

---

## 1. Introduction

Le cluster 14 **stabilise les surfaces encadrants** (tuteur, formateur, ORGADMIN) et positionne **COORDO** et l’**observabilité produit** par rapport au backend déjà convergé. Les contrats P0, mémoire, EVAL1, exports runtime et RAG lexical restent **intouchés** ; le travail porte sur inventaire UI, doctrine rôles, taxonomie exports E1–E6 côté encadrants, et décisions sur dashboards / COORDO.

Deux familles de surfaces coexistent dans `frontend_1.8` :

- **Prod montrable** (`layout: prod`) : `/app/tutor/*`, `/app/trainer/knowledge`
- **Back-office testeur** (`layout: tester`) : `/groups-admin/*`, `/dashboard`, prompts, référentiels

Les smokes Playwright cluster 8 couvrent déjà la branche **prod** ; le cluster 14 consolide la cartographie et les écarts restants.

**Sources mobilisées :** garde-fou §3.6–3.9, `matrice_role_visibilite_v2.md`, `note_frontiere_observabilite_base_vs_d9bis.md`, `design_D2-M06_D2-M11_exports_analytics.md`, écarts 80/90/100/110, code front/back, smokes Playwright.

---

## 2. Photo actuelle des interfaces encadrants

### 2.1 Synthèse par rôle

| Rôle | Routes prod | Routes tester / admin | Données visibles (réel) | Garde-fous |
|------|-------------|---------------------|-------------------------|------------|
| **TUTOR** | `/app/tutor`, `/app/tutor/group/:id`, `.../learner/:id` | `/dashboard`, `/group/...` (encadrant) | Timeline sessions/traces ; preview session **sans verbatim** si non partagé ; badges pilotage dérivés ; validation trace | **ALIGNE** — smoke SMOKE_TUTOR ; pas de P0 UI |
| **TRAINER** | `/app/trainer/knowledge` | idem + référentiels | Liste `TrainerKnowledgeItem` ; validate ; **pas** timeline apprenant libre | **ALIGNE** — smoke SMOKE_TRAINER ; guards backend |
| **ORGADMIN** | — (redir `/app` si non encadrant) | `/groups-admin/*`, exports, users, prompts, conduct-profiles | Gestion groupe, docs RAG, **ExportRun CSV/JSON**, learners ; pas de verbatim non partagé | **ALIGNE** — smoke ORGADMIN exports ; `isOrgAdminLike` |
| **SUPERADMIN** | — | Toutes routes ORGADMIN + routes internal | Idem + endpoints D9bis / conversation-summary (**backend**, pas UI prod) | Guards `is_superadmin` |
| **COORDO** | **Même accès que TUTOR** via `isTutorLike` | `/app/tutor/*` si rôle COORDO | **Pas de surface dédiée** — hérite timeline tuteur | **PARTIEL** — rôle backend + guard front ; pas de vue cohorte |

### 2.2 Détail TUTOR (domaine 110)

| Écran | Composant | API principales | Contenu |
|-------|-----------|-----------------|---------|
| Accueil tuteur | `ProdTutorHomeView.vue` | groupes liés | Liste groupes, CTA apprenants |
| Groupe | `ProdTutorGroupView.vue` | learners du groupe | Apprenants rattachés |
| Apprenant | `TutorLearnerView.vue` | `GET /dashboard/groups/{g}/learners/{l}/timeline/` | Sessions, traces, compétences ; messages **filtrés** ; badges `pilotage` product-safe |
| Validation trace | idem | `POST /hugo/traces/{id}/validate/` | Si `canValidateTraces` (TUTOR/TRAINER/COORDO/admin) |

**Preuves :** Playwright `test_smoke_tutor.spec.ts` — absence `verbatim_marker` ; E2E API vague 5 T1.

**Gaps vs cible 2.0 :** pas de cockpit orchestrateur tuteur ; recommandations / signaux cohorte = **Couronne** ; pas d’UI observabilité session (`/internal/.../observability/` non consommée front).

### 2.3 Détail TRAINER (domaine 110)

| Écran | API | Actions |
|-------|-----|---------|
| `ProdTrainerKnowledgeView.vue` | `GET/POST .../knowledge-items/` | Liste, filtre statut, **validate** |

**Gap :** ingestion dialogique / orchestrateur formateur complet = **Couronne** ; pas de lien UI explicite vers RAG documentaire (domaine 30/40).

### 2.4 Détail ORGADMIN (110 + 100)

| Écran | Fonctions | Exports |
|-------|-----------|---------|
| `GroupAdminDetailView.vue` | Users, docs bibliothèque, profil affichage groupe, RAG docs | **ExportRun** CSV + JSON (`runExportAndDownload`) |
| `GroupsAdminListView.vue` | Liste groupes org | — |
| Autres tester | Users, TutorPrompts, ConductProfiles, OvhLlm | — |

**Preuves :** smoke ORGADMIN ; backend `is_admin_like` sur E3/E4 (ADR C9-CODE-03).

**Gap :** pas de UI EvidenceBundle one-click visible dans grep exports (ExportRun oui) — **A_VÉRIFIER** écran ; observabilité session non affichée.

### 2.5 Fragmentation prod vs tester

| Aspect | Statut |
|--------|--------|
| Parcours **démo prod** encadrant | Tuteur + formateur knowledge **OK** |
| ORGADMIN exports | Surface **tester** (`/groups-admin`) — hors layout prod montrable |
| Dashboard legacy | `/dashboard` mode testeur — timeline riche **non** unifiée prod |

**Écart confirmé 110 :** surfaces **réelles mais fragmentées** entre prod et tester.

---

## 3. COORDO (domaine 90)

### CIBLE 2.0

Coordinateur : vues métier consolidées, progression agrégée, indicateurs couverture, planification jalons — **sans** lecture libre du verbatim non partagé, P0 brut, ni logs internes (`plan_documentation_cto_convergence_hugo.md`).

### RÉEL OBSERVÉ

| Couche | Statut |
|--------|--------|
| Modèle `Role.COORDO` | **Présent** — `accounts/models.py` |
| Backend `TUTOR_ROLES` inclut COORDO | **Présent** — `access_control.py` |
| Front `isTutorLike` / `isEncadrantLike` inclut COORDO | **Présent** — `roleGuards.js` |
| Route `/app/coordo` ou dashboard dédié | **Absent** |
| Projections cohorte / métriques org | **Absent** |
| COORDO dans Playwright bootstrap | **A_VÉRIFIER** |

### Décision cluster 14

**Option retenue : statut documentaire + clarification « héritage tuteur » — pas de mini-surface P0 dans ce cluster.**

- COORDO est **partiellement matérialisé** : même accès prod que le tuteur (`/app/tutor/*`), validation traces autorisée dans `TutorLearnerView`.
- Ce n’est **pas** la cible 2.0 complète (vues cohorte, planification) → classer **ALIGNE_DOC_PARTIEL** + **Couronne** pour le reste.
- **Interdit** cluster 14 : créer un COORDO avec accès verbatim élargi ou observabilité D9bis.

**Alternative rejetée :** vue filtrée sessions org — effort CODE/OPS non prioritaire vs stabilisation doc + smokes ; report **P2 Couronne** si besoin produit.

---

## 4. Observabilité produit (domaine 80)

### Backend (déjà cadré — clusters 9–11)

| Canal | Endpoint | Rôle | UI front |
|-------|----------|------|----------|
| **Observabilité base v1** | `GET /internal/hugo/sessions/{id}/observability/` | ORGADMIN+ / tuteur lié | **Aucune** |
| **D9bis v4** | `.../d9bis/build|export`, `conversation-summary` | SUPERADMIN | **Aucune** |
| **Pilotage timeline** | Dérivé `llm_request_payload` filtré | TUTOR (dashboard API) | **Badges** dans `TutorLearnerView` |

### Visible côté encadrant aujourd’hui

- Progression **indirecte** : badges pilotage (profil, objectif, %, clôture, aide, boucle) — **sans** P0 brut.
- Traces / validation — domaine 70, pas observabilité qualité exhaustive.
- **Pas** de dashboard cohorte, **pas** de catalogue signaux UI, **pas** de graphiques D9bis.

### Décision cluster 14 — dashboards

**Option retenue : documentation + Couronne pour dashboards riches ; incrément P1 optionnel documenté, non exécuté dans ce cluster.**

| Incrément | Priorité | Description |
|-----------|----------|-------------|
| Panneau ORGADMIN « Observabilité session » | **P1 CODE** (optionnel post-C14) | Consommer endpoint v1 existant sur fiche session tester — read-only, pas de D9bis |
| Dashboard cohorte | **P2 Couronne** | Agrégats org/groupe — backend `conversation-summary` SUPERADMIN seulement |
| Exposition signaux qualité apprenant | **Interdit** | Doctrine 2.0 |

---

## 5. Exports encadrants & taxonomie E1–E6 (domaine 100)

Reprise `design_D2-M06_D2-M11_exports_analytics.md` — **vue encadrants** :

| Cat. | Export / surface | TUTOR | TRAINER | ORGADMIN | Écran UI réel |
|------|------------------|-------|---------|----------|---------------|
| **E1** | Traces apprenant (sien) | — | — | — | Parcours **LEARNER** `/app` |
| **E2** | `evaluation-records/export` | **V** (shared) | **V** | **V** | **API** — pas de bouton prod dédié |
| **E3** | EvidenceBundle ZIP | — | — | **V** | **A_VÉRIFIER** UI ; API OK |
| **E4** | ExportRun CSV/JSON | — | — | **V** | `GroupAdminDetailView` — CSV + JSON |
| **E5** | turn-review, pilotage, verbatim-window | Self / admin | Lié | Admin | **Tester / internal** — hors prod apprenant |
| **E6** | D9bis export | — | — | — | **COURONNE** — SUPERADMIN backend |

**Invariants confidentialité (logique, runtime verrouillé cluster 11) :**

- E3/E4 : métadonnées + `payload_structured` / pivot — **pas** P0, **pas** LLM analysis, **pas** verbatim non partagé.
- TUTOR : **403** sur E3/E4 API (tests D2-M07) ; UI LEARNER sans CTA export.
- Taxonomie E1–E6 : **consolidée DOC** cluster 14 ; pas de nouveau type export.

---

## 6. Plan de tests UI (smokes Playwright)

### Existants (cluster 8 — conserver)

| ID | Spec | Assertions clés |
|----|------|-----------------|
| SMOKE-TUTOR | `test_smoke_tutor.spec.ts` | Timeline ; **pas** verbatim_marker |
| SMOKE-TRAINER | `test_smoke_trainer.spec.ts` | Knowledge list |
| SMOKE-ORGADMIN | `test_smoke_orgadmin_exports.spec.ts` | CTA exports ; LEARNER sans export |

### Proposés cluster 14

| ID | Rôle | Scénario | Assertions confidentialité |
|----|------|----------|----------------------------|
| **C14-T1** | TUTOR | Ouvrir timeline → valider présence traces, **absence** contenu message privé | `verbatim_marker` absent ; pas de `turn_state` dans DOM |
| **C14-F1** | TRAINER | Filtrer knowledge `declared` → validate → statut mis à jour | Pas d’accès `/groups-admin` |
| **C14-O1** | ORGADMIN | Export JSON depuis group admin → download | LEARNER redirect `/app` sur `/groups-admin` |
| **C14-C1** | COORDO | Si user bootstrap COORDO : accès `/app/tutor` ; timeline OK | Même garde-fous T1 |
| **C14-X1** | LEARNER | Tentative `/groups-admin` → redirect `/app` | Pas de bouton export |

**OPS :** étendre `bootstrap_smoke_playwright.py` avec user `smoke_coordo` (optionnel P1).

---

## 7. Plan d’actions cluster 14 (tableau)

| Axe | Type | Domaine | Priorité | Fichier(s) impacté(s) |
|-----|------|---------|----------|------------------------|
| Inventaire surfaces encadrants | **DOC** | 110 | **P0** | `ecarts — 110_...md`, ce document |
| Matrice rôles ↔ écrans | **DOC** | 90/110 | **P0** | `matrice_role_visibilite_v2.md` § écrans |
| COORDO = héritage tuteur, Couronne cohorte | **DOC** | 90 | **P0** | `ecarts — 90_...md`, spec canonique |
| Taxonomie E1–E6 ↔ UI encadrants | **DOC** | 100 | **P0** | `ecarts — 100_...md`, renvoi design D2-M11 |
| Frontière obs base vs dashboards | **DOC** | 80 | **P0** | `ecarts — 80_...md`, `note_frontiere_...` |
| Unifier ORGADMIN exports en prod layout | **CODE** | 110/100 | **P2** | router + `GroupAdminDetailView` — Couronne UX |
| Panneau observabilité session ORGADMIN | **CODE** | 80/110 | **P1** | `GroupAdminDetailView` + client API — optionnel |
| Surface COORDO dédiée | **CODE** | 90 | **P2 Couronne** | — |
| Playwright C14-C1 COORDO | **OPS** | 90/110 | **P1** | bootstrap + spec |
| Playwright C14-X1 guards | **OPS** | 90 | **P1** | `tests_playwright/` |
| Encoors UI encadrants | **OPS** | 110 | **P2** | oracle — **A_VÉRIFIER** |

**CODE P0 cluster 14 : aucun** — cluster documentaire + consolidation ; implémentation UX reportée P1/P2.

---

## 8. Garde-fous de non-régression

- [ ] Aucune modification `hugo_orchestrator`, P0, mémoire, `rag_support`, EVAL1, ExportRun runtime.
- [ ] Pas d’exposition D9bis / conversation-summary dans UI prod encadrant.
- [ ] Pas de panneau observabilité apprenant (scoring opaque).
- [ ] COORDO ne reçoit pas d’accès verbatim élargi vs TUTOR.
- [ ] Smokes cluster 8 restent **PASS** après évolutions P1.
- [ ] `turn-review` / debug reste **tester/admin** uniquement.

---

## 9. Conclusion opérationnelle

Le cluster 14 **cadre** les encadrants sans rouvrir le runtime :

- **Verrouillé (doc)** : inventaire prod/tester, matrice E1–E6 ↔ rôles, COORDO = rôle backend + surfaces tuteur héritées, observabilité produit = badges pilotage + **absence** dashboards (Couronne).
- **Partiel réel** : ORGADMIN exports en layout tester ; observabilité backend sans UI ; COORDO sans vue cohorte.
- **Couronne** : dashboards cohorte, COORDO métier, D9bis front, unification prod ORGADMIN, E6 analytique.

**Prochaine sortie utile :** exécuter P0 DOC (écarts 80/90/100/110 § cluster 14) + handover global « Hugo réel vs 2.0 » ; en parallèle ou après, P0 **cluster 12** (sélecteur posture apprenant) reste indépendant.

---

## 10. Backlog cluster 14 (6 lignes)

| ID | Priorité | Action |
|----|----------|--------|
| C14-DOC-01 | P0 | Consolidation écarts 110/90/80/100 § cluster 14 |
| C14-DOC-02 | P0 | Tableau surfaces prod vs tester dans matrice rôles v2 |
| C14-DOC-03 | P0 | Acte COORDO « héritage tuteur, pas surface dédiée » |
| C14-OPS-01 | P1 | Playwright C14-C1 + C14-X1 |
| C14-CODE-01 | P1 | Panneau observabilité session ORGADMIN (optionnel) |
| C14-CODE-02 | P2 | Vue COORDO cohorte — Couronne |
