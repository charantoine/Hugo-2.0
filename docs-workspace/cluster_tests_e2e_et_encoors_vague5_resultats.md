# Campagne E2E & oracle Encoors — convergence locale (vague 5)

> Photo de convergence vs plan CTO — scénarios T1/F1/O1/EVAL1/D9-OBS1  
> Environnement principal : **local** (SQLite, pytest orchestration API + tests front unitaires)  
> Date : 2026-06-18

## Entrées

- Plan CTO : `plan_documentation_cto_convergence_hugo.md` (vagues 1–4 livrées)
- Rapports vagues 2–4 + retex vague 2
- Code front prod : `/app/tutor/*`, `/app/trainer/knowledge`, `GroupView` exports
- **Playwright : absent** du workspace → E2E = orchestration API structurée + revue routes/composants front

---

## Synthèse exécutive

| Bloc | Scénario | Méthode | Statut local | Encoors |
|---|---|---|---|---|
| T | T1 — Tuteur timeline & trace | pytest `test_vague5_e2e_scenarios` | **ALIGNE** | **A_VÉRIFIER** |
| F | F1 — Formateur knowledge | pytest + `ProdTrainerKnowledgeView` | **ALIGNE** (list/validate) ; ingest prod **PARTIEL** | **A_VÉRIFIER** |
| O | O1 — ORGADMIN exports & obs | pytest | **ALIGNE** | **A_VÉRIFIER** / routes v3 **ABSENTES** |
| EVAL | EVAL1 — CTA → pivot → export | pytest | **ALIGNE** | **A_VÉRIFIER** |
| D9 | D9-OBS1 — analytics tech | pytest | **ALIGNE** | **404** (non déployé) |
| UI | Navigateur multi-rôles | non automatisé | **PARTIEL** | **A_VÉRIFIER** |

**Bilan tests vague 5 :** 8/8 pytest E2E + 24/24 tests front unitaires = **32/32 PASS**.

---

## 1. Scénario T1 — Tuteur : lecture & trace

**Rôle :** TUTOR  
**Surface prod :** `/app/tutor` → `TutorLearnerView` → `GET /dashboard/groups/{g}/learners/{l}/timeline/`

### Exécution (local)

| Étape | Attendu | Observé | Statut |
|---|---|---|---|
| Timeline tuteur lié | 200, sessions + traces | `test_t1_tutor_timeline_no_private_verbatim` | **ALIGNE** |
| Verbatim non partagé | absent du payload | `share_verbatim=false` → pas de contenu message | **ALIGNE** |
| Traces listées | id trace présent | confirmé | **ALIGNE** |
| Validation trace | POST `/traces/{id}/validate/` | `test_t1_tutor_can_validate_trace` 200 | **ALIGNE** |
| P0 / TurnState | absents | tests D2-M07 / cluster3 (régression) | **ALIGNE** |

### Objets visibles × domaines

| Objet | Domaine | Visible tuteur | Statut |
|---|---|---|---|
| Sessions (métadonnées) | 60/90 | oui | **ALIGNE** |
| Traces (id, dates) | 70 | oui | **ALIGNE** |
| Verbatim privé | 90 | non | **ALIGNE** |
| Pilotage badges | 60/80 | oui (via timeline) | **ALIGNE** local API |
| UI `/app/tutor` rendu | 110 | non testé navigateur | **PARTIEL** |

---

## 2. Scénario F1 — Formateur : base de connaissances

**Rôle :** TRAINER  
**Surface prod :** `/app/trainer/knowledge` → `GET /hugo/trainer/knowledge-items/`

### Exécution (local)

| Étape | Attendu | Observé | Statut |
|---|---|---|---|
| List items | 200 | `test_f1_trainer_knowledge_list_and_validate` | **ALIGNE** |
| Validate item | status `validated_trainer` | confirmé | **ALIGNE** |
| ExportRun org | 403 | `test_f1_trainer_forbidden_on_org_exports` | **ALIGNE** |
| Ingest / elicitation prod UI | flux dialogique | surface prod = list+validate seulement | **PARTIEL** |
| Accès verbatim apprenant | interdit | guards rôle + pas d’endpoint timeline trainer non lié | **ALIGNE** |

---

## 3. Scénario O1 — ORGADMIN : exports & observabilité

**Rôle :** ORGADMIN  
**Surfaces :** `GroupView` (exports), API `/exports/run/`, `/quality/qualiopi/evidence-bundle/`, `/internal/.../observability/`

### Exécution (local)

| Fichier / endpoint | Attendu | Observé | Statut |
|---|---|---|---|
| ExportRun JSON | `trace_rich_v1` + pivot | pivot présent par trace | **ALIGNE** |
| EvidenceBundle ZIP | `traces.json` lite, pas payload_structured | confirmé | **ALIGNE** |
| Observabilité base | `session_observability_v1` | tours, CTA counters | **ALIGNE** |
| Données sensibles obs | pas de verbatim | confirmé | **ALIGNE** |
| TUTOR ExportRun | 403 | `test_o1_tutor_forbidden_on_exports` | **ALIGNE** |
| CTA exports front | `canRunExports = isOrgAdminLike` | `roleGuards.test.js` | **ALIGNE** (code) |

### Payload observabilité (résumé)

- `turn_counts`, `cta_counters`, `analytics_state`, `quality_signal` (si existant)
- `scope: admin_debug_only`
- **Sans** D9bis / conversation_summary

---

## 4. Scénario EVAL1 — CTA éval → trace → export

**Rôles :** LEARNER → ORGADMIN

### Chaîne exécutée (local)

| Étape | Endpoint | Statut |
|---|---|---|
| UIState CTA eligible | `GET .../ui-state/` | **ALIGNE** |
| Request evaluation | `POST .../request-evaluation/` | **ALIGNE** |
| Generate trace + pivot | `POST .../generate-trace/` | **ALIGNE** |
| Pivot minimal | `evaluation_trace_pivot_v1`, disclaimer | **ALIGNE** |
| Export JSON | `POST /exports/run/` | **ALIGNE** |
| Certification autonome | absente des libellés export | **ALIGNE** |

**Limite :** criteria/modalities legacy generate-trace encore vides → richesse pivot **PARTIEL** (hors chaîne fonctionnelle).

---

## 5. Scénario D9-OBS1 — Analytics tech (SUPERADMIN)

| Étape | Endpoint | Local | Encoors |
|---|---|---|---|
| Build D9bis | POST `.../d9bis/build/` | 201 SUPERADMIN ; 403 ORGADMIN | **404** |
| Export D9bis | GET `.../d9bis/export/` | `d9bis_session_export_v1`, sans verbatim | **404** |
| Conversation summary | GET `.../conversation-summary/` | SUPERADMIN only | **404** |
| Absence exports métier | ExportRun | pas de d9bis | n/a |

**Conclusion Encoors :** fonctionnalités vagues 3–4 **non déployées** sur `hugoback.encoors.com` (2026-06-18).

---

## 6. Oracle Encoors minimal

**Méthode :** probes HTTP sans credentials (`curl`), complété par `10_FICHE_RUNTIME_PROD_ENCOORS.md`.

| Endpoint | Local (attendu) | Encoors (observé) | Statut | Action |
|---|---|---|---|---|
| `/exports/run/` | 403 sans JWT | **401** | **A_VÉRIFIER** auth | pas de comparaison payload |
| `/internal/.../observability/` | 403 ORGADMIN+ avec JWT | **404** | **DIVERGENCE Encoors** | OPS deploy v3 |
| `/internal/.../d9bis/build/` | 403 non-SUPERADMIN | **404** | **DIVERGENCE Encoors** | OPS deploy v4 |
| `/internal/.../conversation-summary/` | 403 non-SUPERADMIN | **404** | **DIVERGENCE Encoors** | OPS deploy v4 |
| `generate-trace` pivot | pivot v1 | **A_VÉRIFIER** | pas de JWT test | oracle authentifié futur |
| EvidenceBundle lite | métadonnées | **A_VÉRIFIER** | pas de JWT test | oracle authentifié futur |
| RLS Postgres | migrations présentes | **A_VÉRIFIER** | DOC | ecarts-90 |
| DEBUG=True Encoors | — | **OBSERVÉ** (fiche 10) | risque ops | hors convergence fonctionnelle |

**Non bloquant pour déclaration convergence locale** : la cible du plan CTO sur le noyau est d’abord **local testé** ; Encoors reste oracle séparé.

---

## 7. E2E navigateur — statut

| Élément | Statut |
|---|---|
| Playwright / Cypress | **ABSENT** |
| Routes prod `/app/*` | **ALIGNE** code (router guards) |
| Parcours visuel multi-rôles | **PARTIEL** — scénario manuel recommandé |
| Tests front unitaires | **24/24 PASS** (roleGuards, CTA, profils) |

**Scénario manuel minimal (OPS) :**
1. Login TUTOR → `/app/tutor` → timeline apprenant lié → valider trace.
2. Login TRAINER → `/app/trainer/knowledge` → valider item.
3. Login ORGADMIN → groupe → exports JSON + bundle.
4. Login LEARNER → CTA éval → refus accès `/app/tutor`.

---

## 8. Écarts / bugs ouverts

| ID | Description | Sévérité | Action |
|---|---|---|---|
| V5-E2E-01 | Pas de Playwright — couverture UI navigateur PARTIEL | P2 | OPS : ajouter Playwright smoke |
| V5-ENC-01 | Encoors sans routes v3/v4 (observability, D9bis, pivot?) | P1 ops | Déployer ou documenter lag |
| V5-ENC-02 | Equivalence payload generate-trace / export non prouvée Encoors | P2 | Oracle authentifié |
| V5-DOC-01 | RLS prod A_VÉRIFIER | P2 | Audit infra |

---

## 9. Promotion statuts locaux (recommandée)

| Domaine | Avant vague 5 | Après preuves E2E API | Encoors |
|---|---|---|---|
| 90 | ALIGNE local P0 | **ALIGNE** (timeline + guards confirmés) | A_VÉRIFIER |
| 100 | ALIGNE_DOC_PARTIEL | **ALIGNE local** (bundle lite + pivot export) | A_VÉRIFIER |
| 70 | PARTIEL+ pivot | **PARTIEL** chaîne EVAL1 **ALIGNE** | A_VÉRIFIER |
| 80 | PARTIEL | **PARTIEL** base ALIGNE ; D9bis tech ALIGNE local | routes absentes Encoors |
| 110 | PARTIEL surfaces | **PARTIEL** API OK ; UI browser PARTIEL | A_VÉRIFIER |
| 60 | PARTIEL B1 | **ALIGNE_DOC_PARTIEL+** timeline/validation | A_VÉRIFIER |

---

## 10. Campagne tests exécutée

```
apps/hugo/tests/test_vague5_e2e_scenarios.py     8/8 PASS
hugo-hugolucia/frontend_1.8 npm test            24/24 PASS
```

Régression recommandée avant release : campagne v4 (68 pytest) + vague 5 (8) = **76 pytest** + **24 front**.
