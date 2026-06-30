# Cluster dev — encadrants & exports vague 2 — résultats

> Rapport de clôture du cluster de développement borné sur les domaines 90/100/110
> (liens 70/40/50/60/31). Discipline : **RÉEL OBSERVÉ** prouvé par code + tests locaux ;
> prod Encoors / RLS Postgres = **A_VÉRIFIER**.

**Date :** 2026-06-18  
**Sources :** `cluster2_encadrants_roles_audit_reel_vs_cible.md`, backlog ENC-*

---

## 1. Actions retenues pour ce cluster

| ID | Type | Domaine | Description | Priorité | Lot CTO | Pourquoi maintenant ? | Pourquoi pas plus ? |
|---|---|---|---|---|---|---|---|
| ENC-CODE-01 | CODE | 90 | Aligner exports UI sur `isOrgAdminLike` | P0 | Vague 2 | Fausses affordances → 403 | Pas de refonte UX exports |
| ENC-CODE-02 | CODE | 90 | Garde trainer sur knowledge APIs | P0 | Vague 2 | Faille LEARNER/TUTOR | ORGADMIN seul sur admin groupe inchangé |
| ENC-CODE-03 | CODE | 90 | Tests négatifs rôles exports/trainer | P0 | Vague 2 | Preuve régression | Pas de tests E2E navigateur |
| ENC-CODE-04 | CODE | 100 | Strip EXIF Evidence | P1 | Vague 2 | Écart CONF-22 | Pas tous formats exotiques |
| ENC-CODE-05 | CODE | 100 | Test cross-tenant EvidenceBundle | P1 | Vague 2 | Complète G3-02 | RLS prod hors scope |
| ENC-CODE-07 | CODE | 110 | Router guard encadrants vs LEARNER | P1 | Vague 3 | `/dashboard` ouvert à tous | Pas de RBAC fin par route métier |
| ENC-CODE-08 | CODE | 110 | Surface tuteur prod minimale | P1 | Vague 3 | B1 hors shell tester | Pas de CTA tuteur moteur |
| ENC-CODE-09 | CODE | 40/110 | Surface formateur prod + list API | P1 | Vague 3 | C1 minimal | Pas d'ingest UI prod |
| ENC-DOC-01 | DOC | 90 | Màj ecarts-90 §7 | P0 | Vague 2 | Traçabilité | Matrice complète D2-M07 partielle |
| ENC-DOC-02 | DOC | 100 | Màj ecarts-100 §8 EXIF/exports | P0 | Vague 2 | Traçabilité | — |
| ENC-DOC-03 | DOC | 110 | Màj ecarts-110 §8 surfaces prod | P1 | Vague 3 | Traçabilité | — |
| ENC-OPS-02 | OPS | 100 | Tests E3/E4/G3-02 consolidés | P0 | Vague 2 | Preuve CI | Template Cursor séparé |

**Non retenus ce cluster (Couronne / P2 / reporté) :** ENC-CODE-11 (ORGADMIN vs SUPERADMIN), ENC-CODE-12 (bundle enrichi), ENC-CODE-10 (UI éval tuteur), ENC-OPS-01/03/05/07, ENC-DOC-04/05/06, D9bis, intercalaires v1, observabilité 80.

---

## 2. Plan de patch CODE (réalisé)

#### Action ENC-CODE-01 — Alignement exports front

- **Domaines :** 90, 100
- **Backend :** inchangé (`ExportRunView`, `EvidenceBundleView` déjà `is_admin_like`)
- **Front :** `GroupView.vue`, `stores/auth.js`, `utils/roleGuards.js`
- **Modifications :** `canRunExports` → `auth.isOrgAdminLike` ; getter `isAdminLike` realigné sur backend
- **Tests :** `roleGuards.test.js` (5 tests)
- **Risques :** TRAINER ne voit plus liens admin tester — voulu

#### Action ENC-CODE-02 — Guards trainer knowledge

- **Domaines :** 90, 40, 110
- **Backend :** `access_control.can_manage_trainer_knowledge`, `views_trainer.py`, `urls.py` (+ `TrainerKnowledgeItemListView`)
- **Modifications :** 403 si rôle ∉ {TRAINER, ORGADMIN, SUPERADMIN}
- **Tests :** `test_encadrants_role_guards.py`

#### Action ENC-CODE-04 — EXIF stripping

- **Domaines :** 100
- **Backend :** `services/evidence_media.py`, `views_evidence.py`, `requirements.txt` (+ Pillow)
- **Tests :** `test_evidence_exif.py`

#### Action ENC-CODE-07/08/09 — Surfaces prod encadrants

- **Front :** routes `/app/tutor/*`, `/app/trainer/knowledge`, `ProdLearnerLayout` nav, router guards
- **Backend :** `GET /hugo/trainer/knowledge-items/`

---

## 3. Résumé CODE / TEST / DOC réalisés

### Backend (`hugo_back`)

| Fichier | Changement |
|---|---|
| `apps/referentials/access_control.py` | `TRAINER_KNOWLEDGE_ROLES`, `can_manage_trainer_knowledge` |
| `apps/hugo/views_trainer.py` | Guards + `TTrainerKnowledgeItemListView` |
| `apps/hugo/views_evidence.py` | Strip EXIF via `evidence_media` |
| `apps/hugo/services/evidence_media.py` | **Nouveau** |
| `apps/hugo/urls.py` | Route list knowledge |
| `requirements.txt` | Pillow |
| `tests/test_encadrants_role_guards.py` | **Nouveau** — 9 tests |
| `tests/test_evidence_exif.py` | **Nouveau** — 2 tests |
| `tests/test_d2_m06_d2_m11_exports_and_analytics.py` | + `test_evidence_bundle_cross_tenant` |

**Tests exécutés :** 33 passed (pytest cluster encadrants).

### Front (`hugo-hugolucia/frontend_1.8`)

| Fichier | Changement |
|---|---|
| `src/utils/roleGuards.js` | **Nouveau** |
| `src/utils/roleGuards.test.js` | **Nouveau** — 5 tests |
| `src/stores/auth.js` | Getters rôle alignés backend |
| `src/views/GroupView.vue` | Exports ORGADMIN only |
| `src/router/index.js` | Routes prod encadrants + guards |
| `src/layouts/ProdLearnerLayout.vue` | Nav tuteur/formateur/admin |
| `src/views/ProdTutor*.vue`, `ProdTrainerKnowledgeView.vue` | **Nouveaux** |

**Tests exécutés :** 5 passed (`roleGuards.test.js`).

### Documentation

| Fichier | Màj |
|---|---|
| `ecarts — 90_confidentialite_partage_multitenant_roles.md` | §7 cluster dev |
| `ecarts — 100_exports_preuves_qualiopi_lite.md` | §8 cluster dev |
| `ecarts — 110_interfaces_formateur_tuteur.md` | §8 cluster dev |
| `specs interface 2.0.md` | Réel observé tuteur/formateur |
| `cluster2_matrice_runtime_vs_cible.md` | §0, §17, permissions exports |
| `plan_documentation_cto_convergence_hugo.md` | Vagues 2–3 annotées |

---

## 4. P0 corrigés

| Écart P0 | Statut |
|---|---|
| Décalage UI exports vs backend 403 | **Corrigé** local |
| Endpoints trainer sans garde rôle | **Corrigé** local |
| Tests négatifs rôles manquants | **Ajoutés** |
| EXIF annoncé non implémenté | **Corrigé** local |
| Bundle présenté comme riche | **Doc clarifiée** — reste lite |

---

## 5. P1 structurants couverts

| Item | Statut |
|---|---|
| Surface tuteur layout prod | **PARTIEL** — timeline read-only + validation trace |
| Surface formateur layout prod | **PARTIEL** — liste + validation knowledge |
| Router guard LEARNER → `/dashboard` | **Corrigé** |
| Test cross-tenant EvidenceBundle | **Ajouté** |
| `test_tutor_access_control` pilotage | **Déjà aligné** (B1-02) — pas de changement requis |

---

## 6. Explicitement laissé en Couronne / reporté

| Sujet | Lot |
|---|---|
| D9bis analytics LLM / export-md | Couronne |
| Intercalaires v1 riches | Couronne |
| Observabilité avancée (80) | Couronne |
| D2-M12 frontière ORGADMIN / SUPERADMIN exports | Vague 3 |
| Enrichissement bundle Qualiopi (Evidence binaires) | Couronne |
| UI tuteur évaluations partagées (ENC-CODE-10) | Vague 3 P2 |
| RLS Postgres prod | **A_VÉRIFIER** |
| Parité Encoors timeline / exports | **A_VÉRIFIER** |

---

## 7. Prochaine sortie utile

1. Oracle Encoors (ENC-OPS-05) sur timeline B1-01 et exports ORGADMIN.  
2. D2-M12 : séparer permissions SUPERADMIN si la cible l'exige.  
3. Enrichir surface formateur prod (ingest documentaire) sans ouvrir orchestrateur 50 complet.
