# Campagne de tests — encadrants & exports (post vague 2)

> Consolidation des blocs T / E / S / X / R après cluster dev
> `cluster_dev_encadrants_exports_vague2_resultats.md`.

## Entrées

- **[ENVIRONMENT]** : local (SQLite, pytest + tests front unitaires ; pas de run Encoors)
- **[SESSION_ID]** : créées dynamiquement par fixtures pytest
- **[ROLE]** : LEARNER | TUTOR | TRAINER | ORGADMIN | SUPERADMIN (SUPERADMIN partiellement couvert)
- **[COMMIT]** : non disponible (workspace sans git HEAD au moment du run)

## Règles appliquées

- Backend-first : 46 pytest + 5 tests front unitaires verts avant conclusion front.
- Séparation : Réel confirmé | Cible 2.0 | Écarts | A_VÉRIFIER | Hypothèses.
- Surfaces : prod `/app/*` vs tester `/dashboard/*` vs superadmin Django admin (hors run).
- Couronne exclue : D9bis, intercalaires v1, observabilité 80 avancée.

---

## Bloc T — Gardes de rôles encadrants

### Sources mobilisées

- `test_encadrants_role_guards.py`, `test_d2_m06_d2_m11_exports_and_analytics.py` (E3/E4)
- `access_control.py`, `views_trainer.py`, `exports/views.py`, `quality/views.py`
- `roleGuards.js`, `GroupView.vue`, `router/index.js`, `stores/auth.js`

### Tableau Rôle × Endpoint/Surface

| Rôle | Endpoint / surface | Attendu | Observé | Statut |
|---|---|---|---|---|
| LEARNER | `POST /hugo/trainer/.../elicitation-answers/` | 403 | 403 | **ALIGNE** |
| LEARNER | `GET /hugo/trainer/knowledge-items/` | 403 | 403 | **ALIGNE** |
| LEARNER | `POST /exports/run/` | 403 | 403 | **ALIGNE** |
| LEARNER | `POST /quality/qualiopi/evidence-bundle/` | 403 | 403 | **ALIGNE** |
| TUTOR | elicitation-answers | 403 | 403 | **ALIGNE** |
| TUTOR | knowledge-items list | 403 | 403 | **ALIGNE** |
| TUTOR | ExportRun | 403 | 403 | **ALIGNE** |
| TRAINER | knowledge-items list | 200 | 200 | **ALIGNE** |
| TRAINER | elicitation-answers | 200 (flow test) | 201 | **ALIGNE** |
| TRAINER | ExportRun | 403 | 403 | **ALIGNE** |
| ORGADMIN | knowledge-items list | 200 | 200 | **ALIGNE** |
| ORGADMIN | ExportRun | 200 | 200 | **ALIGNE** |
| ORGADMIN | EvidenceBundle | 200 | 200 | **ALIGNE** |
| SUPERADMIN | ExportRun / trainer | 200 (contrat) | **non testé pytest** | **PARTIEL** |
| TUTOR/TRAINER/LEARNER | Boutons export `GroupView` | masqués | `canRunExports = isOrgAdminLike` | **ALIGNE** (code) |
| LEARNER | `/dashboard`, routes `requiresEncadrant` | redirect `/app` | `router redirectForRole` | **ALIGNE** (code) |
| LEARNER | `/groups-admin/*` | redirect `/app` | `requiresOrgAdmin` | **ALIGNE** (code) |

### Tests exécutés (bloc T)

| Test | Résultat |
|---|---|
| `test_encadrants_role_guards.py` (9) | **9/9 PASS** |
| `test_learner_forbidden_on_evidence_bundle` | **PASS** |
| `test_learner_forbidden_on_export_run` | **PASS** |
| `test_tutor_forbidden_on_export_run` | **PASS** |
| `test_trainer_forbidden_on_export_run` | **PASS** |
| `test_orgadmin_allowed_on_export_run` | **PASS** |
| `roleGuards.test.js` (5) | **5/5 PASS** |

### Cible 2.0 (rappel)

- Formateur : savoir métier gouverné, pas accès libre non-partagé apprenant.
- ORGADMIN : exports filtrés tenant, pas lecture verbatim masse.
- Tuteur : pas d’export org-wide.

### Écarts / actions

| Écart | Statut | Action suggérée |
|---|---|---|
| SUPERADMIN non couvert par pytest dédié | **PARTIEL** | Ajouter 2 tests négatifs/positifs SUPERADMIN (P2) |
| `GET elicitation-questions` guard non testé isolément | **PARTIEL** | Test miroir answers (P2) |
| E2E navigateur multi-rôles exports | **A_VÉRIFIER** | Scénario Playwright/Cypress (OPS) |

---

## Bloc E — EXIF / Evidence / bundles (domaine 100)

### Sources mobilisées

- `test_evidence_exif.py`, `evidence_media.py`, `views_evidence.py`
- `test_d2_m06_d2_m11_exports_and_analytics.py`, `test_d2_m07_confidentiality_oracles.py`
- `ecarts — 100_exports_preuves_qualiopi_lite.md` §8

### Comportement EXIF / GPS

| Cas | Attendu | Observé | Statut |
|---|---|---|---|
| JPEG avec EXIF upload | EXIF absent du fichier stocké | `test_evidence_upload_strips_exif_from_jpeg` | **ALIGNE** |
| GPS sans opt-in | pas de GPS dans meta | meta `gps_opt_in: false` | **ALIGNE** |
| GPS opt-in explicite | lat/lon en meta seulement | `test_evidence_gps_only_in_meta_when_opt_in` | **ALIGNE** |
| meta `exif_stripped: true` | présent | confirmé payload API | **ALIGNE** |

### Contenu ZIP EvidenceBundle lite

| Fichier ZIP | Attendu | Observé | Statut |
|---|---|---|---|
| `traces.json` | métadonnées trace (id, session, learner, dates) | `test_evidence_bundle_traces_json_shape` | **ALIGNE** |
| `audit_log.json` | actions audit org | test bundle | **ALIGNE** |
| `referentials.json` | id + name | test bundle | **ALIGNE** |
| `active_documents.json` | id document actif | test bundle | **ALIGNE** |
| `summary.txt` | compteurs | test bundle | **ALIGNE** |
| `payload_structured` / verbatim / P0 | **absents** | `test_evidence_bundle_no_payload_structured`, `no_p0_tokens` | **ALIGNE** |
| D9bis / LLM analysis | **absents** | `test_no_d9bis_models`, `test_f1_02_*` | **ALIGNE** |
| EvaluationTrace 2.0 complète | **non** (doctrine) | bundle lite confirmé | **ALIGNE** |

### Cross-tenant

| Test | Résultat |
|---|---|
| `test_export_run_cross_tenant` | **PASS** |
| `test_evidence_bundle_cross_tenant` | **PASS** |
| `test_d1_02_g3_02_evidence_bundle_scoped_to_caller_organisation` | **PASS** |

### A_VÉRIFIER

- Contenu ZIP prod Encoors.
- RLS Postgres effective (tests SQLite uniquement).
- Formats image exotiques (HEIC, etc.) — hors scope minimal.

---

## Bloc S — Surfaces encadrants prod (110)

### Sources mobilisées

- Routes `/app/tutor/*`, `/app/trainer/knowledge`
- `TutorLearnerView.vue`, `ProdTutor*.vue`, `ProdTrainerKnowledgeView.vue`
- `test_tutor_access_control.py`, `test_d2_m07` B1-01/B1-02
- `specs interface 2.0.md` (réel observé cluster dev)

### Tableau Surface × Rôle

| Surface | Rôle | Objets visibles (attendu) | Preuve campagne | Statut |
|---|---|---|---|---|
| `/app/tutor` | TUTOR | groupes accessibles | code route + guard `requiresTutorLike` | **PARTIEL** (pas E2E) |
| `/app/tutor/.../timeline` | TUTOR | traces meta ; verbatim si `share_verbatim` | B1-01/B1-02 pytest | **ALIGNE** backend |
| `/app/tutor/.../timeline` | TUTOR | pas P0 / turn_state | B1-02, pilotage test | **ALIGNE** backend |
| `/app/trainer/knowledge` | TRAINER | liste `TrainerKnowledgeItem` + validate | API list + vue prod | **PARTIEL** (pas E2E) |
| `/app/trainer/knowledge` | TRAINER | pas verbatim apprenant | pas de route timeline trainer | **ALIGNE** |
| `/dashboard` (tester) | LEARNER | redirect | router guard | **ALIGNE** code |
| Validation trace UI | TUTOR/TRAINER/COORDO | si link tuteur | `canValidateTraces` + pytest validate | **ALIGNE** backend |

### Scénarios textuels (à rejouer manuellement / E2E)

1. **TUTOR** → `/app/tutor` → groupe → apprenant lié → timeline sans verbatim si non partagé.
2. **TUTOR** → valider trace → 200 si link, 403 sinon.
3. **TRAINER** → `/app/trainer/knowledge` → filtrer `derived_provisional` → valider item.
4. **LEARNER** → tenter `/app/tutor` → redirect `/app`.

### Écarts

| Point | Statut |
|---|---|
| Pas de test E2E navigateur surfaces prod | **A_VÉRIFIER** |
| Ingest documentaire formateur en prod | **ABSENT** (C1 partiel — ingest reste API/tester) |
| UI évaluations partagées tuteur | **ABSENT** (ENC-CODE-10 reporté) |

---

## Bloc X — CTA évaluation ↔ traces ↔ exports (70/100)

### Sources mobilisées

- `test_cta_evaluation_contract.py`, `test_request_evaluation_guard.py`
- `test_d2_m06` generate-trace + export JSON
- `test_trainer_eval_export_only_shared_records`

### Schéma session → évaluation → trace → export

```
LEARNER session
  → UIState CTA évaluation (test_cta_evaluation_contract)
  → POST request-evaluation (guards test_request_evaluation_guard)
  → POST generate-trace (test_export_run_json_includes_payload_structured)
  → Trace en base
  → ExportRun JSON trace_rich_v1 (ORGADMIN, tenant-scoped)
  → EvidenceBundle lite (métadonnées traces, pas payload complet)
```

### Labels UI sensibles (sur-promesse)

| Label observé | Risque certification | Verdict |
|---|---|---|
| « Felix-ready (v1) » | faible — format pivot | **OK** si doc = export métier non certifiant |
| « JSON trace_rich_v1 » | faible | **OK** |
| Aucun « certifié » / « Qualiopi certifiant » | — | **ALIGNE** (grep front) |

### Tests exécutés

| Test | Résultat |
|---|---|
| `test_ui_state_exposes_cta_evaluation_contract` | **PASS** |
| `test_request_evaluation_*` (2) | **PASS** |
| `test_export_run_json_includes_payload_structured` | **PASS** |
| `test_trainer_eval_export_only_shared_records` | **PASS** |

### Écarts

| Point | Statut |
|---|---|
| Chaîne bout-en-bout UI prod apprenant → export même session | **A_VÉRIFIER** (manual/E2E) |
| EvaluationTrace doctrinal dans bundle | **ABSENT** (voulu — lite) |

---

## Bloc R — Synthèse par domaine

| Domaine | ALIGNE (tests) | PARTIEL | A_VÉRIFIER | Couronne |
|---|---|---|---|---|
| **90** confidentialité / rôles | Guards trainer, exports org, B1-01/B1-02, router LEARNER | SUPERADMIN pytest ; E2E front | RLS prod, Encoors timeline | D2-M12 ORGADMIN≠SUPERADMIN |
| **100** exports / preuves | EXIF, bundle lite, cross-tenant, permissions | Formats image exotiques | ZIP prod Encoors | D9bis, bundle enrichi |
| **110** interfaces encadrants | Routes prod + guards code | Surfaces prod sans E2E | Parité Encoors `/app/tutor` | Orchestrateurs 50/60 complets |
| **70** évaluation / traces | CTA contract, generate-trace→export, eval export filtré | Chaîne UI prod complète | Prod distante | EvaluationTrace agrégat complet |

### Bilan tests

| Suite | Pass | Fail |
|---|---|---|
| pytest campagne encadrants/exports (43) | 43 | 0 |
| pytest CTA évaluation (3) | 3 | 0 |
| front `roleGuards.test.js` (5) | 5 | 0 |
| **Total** | **51** | **0** |

---

## Patchs documentaires suggérés (minimaux)

| Fichier | Patch suggéré | Priorité |
|---|---|---|
| `ecarts — 90` §7 | Ajouter ligne « SUPERADMIN pytest non couvert — PARTIEL » | P2 |
| `ecarts — 100` §8 | Confirmer EXIF **ALIGNE** local post-tests campagne | P1 (cosmétique) |
| `ecarts — 110` §8 | Marquer surfaces prod **PARTIEL** — preuve code, E2E A_VÉRIFIER | P1 |
| `ecarts — 70` §9 | Référencer ce rapport pour chaîne trace→export | P2 |
| `cluster2_matrice_runtime_vs_cible.md` | Permissions exports → **ALIGNE** local ; surfaces prod → **PARTIEL** | P1 |

**Ne pas promouvoir en IMPLÉMENTÉ prod** sans oracle Encoors.

---

## Matrice cluster2 — statuts justifiés par cette campagne

| Ligne domaine | Peut passer à | Condition |
|---|---|---|
| 100 permissions exports org | **ALIGNE** local | 51 tests verts + front aligné |
| 110 interface tuteur timeline | **ALIGNE** backend ; **PARTIEL** prod | B1 pytest ; E2E prod ouvert |
| 90 guards trainer | **ALIGNE** local | 9 tests role guards |
| D2-M12 frontière ORGADMIN/SUPERADMIN | **OUVERT** | SUPERADMIN non testé ; code partagé |

---

## Check-list clusters futurs

- [ ] E2E Playwright : 5 rôles × exports visibility + `/app/tutor` (ENC-OPS-04)
- [ ] Oracle Encoors B1 + exports ORGADMIN (ENC-OPS-05)
- [ ] Tests SUPERADMIN explicites (exports + trainer)
- [ ] D2-M12 : séparation permissions si cible l’exige
- [ ] UI tuteur `LearnerEvaluationRecord` partagés (ENC-CODE-10)
- [ ] Ingest formateur prod (C1)

---

## Couronne — explicitement non testée

- D9bis analytics LLM / export-md
- Intercalaires v1 riches (120)
- Observabilité avancée (80)
- Enrichissement bundle Qualiopi (Evidence binaires)
- RLS Postgres prod

---

*Campagne exécutée le 2026-06-18 — environnement local.*
