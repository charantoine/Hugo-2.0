# R1 — État réel actualisé

**Date :** 1er juillet 2026  
**Rôle :** nouvelle cartographie synthétique de l'état réel — remplace fonctionnellement `A1_SOCLE_REEL_OBSERVE.md` (22/06/2026).  
**Sources mobilisées :** code `hugo_back`, `frontend_1.8`, tests clusters 15–16, protocole E2E 29/06, rapport test 30/06, docs 02/07/08/10, baseline A1.

---

## 1. Stack réellement active

| Couche | Emplacement | Statut | Preuve |
|--------|-------------|--------|--------|
| Moteur API | `hugo_back/` | **REL OBSERV** | Django ≥5.2, DRF, JWT, PostgreSQL, Celery, MinIO ; `manage.py` → `config.settings.dev` |
| Produit montrable | `hugo-hugolucia/frontend_1.8/` | **REL OBSERV** | Routes `/app*`, tests Playwright, `npm run dev` |
| Bibliothèque doc active | `docs-workspace/` + lot **R0–R7** | **REL OBSERV** | Ce lot |
| Monorepo `hugo-main/` | specs + front en retard | **BASELINE HISTORIQUE** | `backend/` vide — non référence moteur |
| Monorepo `hugo-hugolucia/` deploy | nginx/compose | **REL OBSERV PARTIEL** | Compose suppose `backend/` vide — déploiement moteur = `hugo_back` séparé |

**Python :** 3.11+ (requirements) ; venv local observé 3.12.  
**Front :** Vue 3 + Vite ; port dev typique 5173.

---

## 2. Baselines effectives (ne pas fusionner)

| Baseline | Description | Statut | Preuve dominante |
|----------|-------------|--------|------------------|
| **A — Front 1.8 + API Encoors** | `.env.development` → `https://hugoback.encoors.com` | **REL OBSERV** (config) ; moteur distant **À VÉRIFIER** | `.env.development`, doc 10 (12/06) |
| **B — Front 1.8 + `hugo_back` local** | `VITE_API_URL=/api` + proxy Vite | **REL OBSERV** | E2E 29/06, rapport 30/06 |
| **B′ — Smoke sqlite** | `run_local_hugo.sh`, `bootstrap_smoke_playwright` | **REL OBSERV PARTIEL** | DB ≠ `hugo_poc` ; `which-hugo-stack.sh` (30/06) |
| **C — Stratégie d'usage** | A pour démo externe ; B pour preuve dev | **CART CONFIRM** | doc 07, R0 |

**Impact documentaire :** tout constat « Hugo fait X » doit préciser **quelle baseline**.

---

## 3. Vérité runtime actuelle (local — baseline B)

### 3.1 Flags structurants backend

Source : `hugo_back/config/settings/base.py` (lecture 01/07/2026).

| Variable | Défaut local | Effet | Tag |
|----------|--------------|-------|-----|
| `HUGO_P0_V17_ENABLED` | `false` | Pipeline P0 **legacy** actif | **REL OBSERV** |
| `HUGO_P0_CLASSIFIER_ENABLED` | `false` | Classifieur LLM P0 désactivé | **REL OBSERV** |
| `HUGO_PHASE_CLASSIFIER_ENABLED` | `true` | Classifieur phase LLM actif | **REL OBSERV** |
| `ENABLE_EXTERNAL_LLM` | `true` | Appels LLM autorisés | **REL OBSERV** |
| `LLM_PROVIDER_DEFAULT` | `ollama` | Provider par défaut | **REL OBSERV** |

**Encoors :** valeurs **À VÉRIFIER** (dernière inspection HTTP 12/06, pas de lecture env).

### 3.2 Dual base de données locale

| Stack | Settings | DB | Usage |
|-------|----------|-----|-------|
| Dev courant | `config.settings.dev` | `hugo_poc` PostgreSQL | Campagne 30/06, E2E 29/06 |
| Smoke Playwright | `config.settings.sqlite_test` | SQLite | `bootstrap_smoke_playwright`, cluster 16 |

**REL OBSERV** — `print_runtime_stack`, `which-hugo-stack.sh` (memo CTO 30/06).  
**HYPOTHÈSE :** ne pas extrapoler les résultats smoke vers `hugo_poc` sans rejeu.

---

## 4. Produits / fronts / backends qui font foi

| Rôle | Fait foi | Ne fait pas foi |
|------|----------|-----------------|
| Comportement API | `hugo_back/` + pytest | `spec_canonique_hugo_2_0.md` |
| Parcours UX servi | `frontend_1.8/` routes `meta.layout: 'prod'` ou `tester` | `hugo-main/frontend_1.8/` |
| Contrat UIState consommé | `GET /hugo/sessions/{id}/ui-state/` → `build_contract_ui_state` | Ancien `UiState` engagement (tour SSE uniquement) |
| Multi-tenant | `TenantRLSMiddleware` + tests | Effet RLS prod |

---

## 5. Endpoints structurants (inventaire condensé)

Préfixes racine (`config/urls.py`) : `/auth/`, `/users/`, `/groups/`, `/hugo/`, `/documents/`, `/referentials/`, `/exports/`, `/dashboard/`, `/evidence/`, `/quality/`, `/internal/`, `/traces/`, `/learners/`.

**Hugo session (critiques produit)** — `apps/hugo/urls.py` :

| Méthode | Path | Statut local |
|---------|------|--------------|
| POST | `/hugo/sessions/` | **REL OBSERV** |
| GET/PATCH | `/hugo/sessions/{id}/` | **REL OBSERV** |
| GET | `/hugo/sessions/{id}/ui-state/` | **REL OBSERV** |
| POST | `/hugo/sessions/{id}/set-posture/` | **REL OBSERV** (C15/C16) |
| POST | `/hugo/sessions/{id}/messages/` | **REL OBSERV** |
| POST | `/hugo/sessions/{id}/messages/stream/` | **REL OBSERV** |
| POST | `/hugo/sessions/{id}/request-synthesis/` | **REL OBSERV** |
| GET | `/hugo/sessions/{id}/evaluation-readiness/` | **REL OBSERV** |
| POST | `/hugo/sessions/{id}/request-evaluation/` | **REL OBSERV** |
| POST | `/hugo/sessions/{id}/finalize-evaluation/` | **REL OBSERV** |
| POST | `/hugo/sessions/{id}/generate-trace/` | **REL OBSERV** |
| GET | `/hugo/sessions/{id}/memory-summary/` | **REL OBSERV** |
| POST | `/hugo/sessions/{id}/share/` | **REL OBSERV** |
| CRUD | `/hugo/learner-conversation-profiles/` | **REL OBSERV** (V6 matrice, 20/06) |
| CRUD | `/hugo/conduct-profiles/` | **REL OBSERV** local ; **absent Encoors** 12/06 |
| Trainer | `/hugo/trainer/knowledge-items/`, élicitation, ingest | **REL OBSERV** (C15) |

Détail payloads : **R4**.

---

## 6. Surfaces produit servies

### 6.1 Mode prod (`VITE_FRONTEND_MODE` absent ou `prod_showable`)

| Persona | Routes | Preuve |
|---------|--------|--------|
| Apprenant | `/app`, `/app/session/:id` | E2E L12, cluster 16 |
| Tuteur / coordo | `/app/tutor`, `/app/tutor/group/:id`, learner detail | `test_smoke_tutor`, rapport 30/06 |
| Formateur | `/app/trainer/knowledge`, `library`, `elicitation`, `referentials` | C15, Playwright trainer smoke |

### 6.2 Mode testeur (`VITE_FRONTEND_MODE=tester`)

| Persona | Routes | Preuve |
|---------|--------|--------|
| Encadrant / admin | `/dashboard`, `/users`, `/groups-admin`, `/referentials` | E2E lots 0–4 |
| Superadmin | switch org navbar, `/admin/organisations`, onboarding wizard | E2E L1, rapport 30/06 |
| Calibration | `/conduct-profiles`, `/tutor-prompts`, `/admin/conversation/*` | Router + audits UI 26/06 |

**Séparation confirmée :** parcours `/app` sans modales P0 debug (`VITE_P0_DEBUG_ENABLED=false` par défaut) — **REL OBSERV** cluster 3, E2E L12.

---

## 7. Principaux invariants confirmés (post-juin 2026)

| Invariant | Statut | Preuve |
|-----------|--------|--------|
| UIState GET sans champs P0 | **REL OBSERV** | `test_cluster3_oracles.py` INV-01 ; B16-P1 |
| Mémoire API sans verbatim | **REL OBSERV** | B16-M2, `test_memory_summary_smoke.py` |
| RAG runtime lexical (pas vectoriel) | **REL OBSERV** | `rag_support.py` ; `test_preprod_garde_fou.py` |
| CTA synthèse/évaluation dans UIState contract | **REL OBSERV** | B16-C1/C2, `cta_ui_state.py` |
| Posture gouvernée backend (`set-posture`) | **REL OBSERV** | C15 A1, B16-P2/P3 |
| Panneau mémoire apprenant (`session_memory` seul) | **REL OBSERV** | C15 A3, E2E L8 |
| Mémoire **non injectée** prompts LLM | **REL OBSERV** | Absence dans services prompt ; clusters 9–11 |
| `theme_memories` exposé API, hors UI apprenant | **REL OBSERV** | `contrat_api_memory_summary_v1.md` |
| Multi-tenant superadmin via `X-Organisation-Id` | **REL OBSERV** | `test_tenant_ui_campaign` 8/8 (30/06) |
| Traces pivot v1 dans generate-trace | **REL OBSERV** | cluster 11, tests pivot |

---

## 8. Principales divergences vs baseline 22 juin 2026

| Sujet | Juin 22 (A1) | État 01/07 | Documents impactés |
|-------|--------------|------------|-------------------|
| Interface apprenant posture/mémoire | Bandeau lecture seule ; pas panneau mémoire front | PostureSelector + LearnerMemoryPanel branchés | A2, A4 → **R2, R3** |
| Formateur workflow | Liste + validate basique | Rejet, provisoire, élicitation V0, usage_stats | A2 → **R2** |
| Profils conversationnels globaux | Non mentionnés A1 | API + admin `/admin/conversation/learner/profiles` | A1, A3 → **R1, R4** |
| Tests E2E protocole | Non existant juin 22 | 23 PASS / 5 SKIP (29/06) | A6 → **R6** |
| Campagne multi-tenant | Partielle | Rapport structuré 30/06 + quick wins INC | A1, doc 11 |
| Encoors | Inspection 12/06 | **Pas de nouvelle inspection authentifiée** | doc 10 — toujours **À VÉRIFIER** |
| Front défaut API | Encoors | Inchangé commité | A1 confirmé |
| ACL formateur learners dashboard | Peu documenté | `[]` confirmé — décision CTO ouverte | **Nouveau** R5/R6 |

---

## 9. Runtime distant Encoors (rappel — non actualisé)

Dernière preuve HTTP directe : **12 juin 2026** (`10_FICHE_RUNTIME_PROD_ENCOORS.md`).

| Constat 12/06 | Tag | Toujours valide ? |
|---------------|-----|-------------------|
| API HTTPS disponible | **REL OBSERV** (date 12/06) | **À VÉRIFIER** sans re-probe |
| `DEBUG=True` sur distant | **REL OBSERV** (12/06) | **À VÉRIFIER** |
| CORS : `localhost:5173` refusé | **REL OBSERV** (12/06) | **À VÉRIFIER** |
| `/hugo/conduct-profiles/` absent | **REL OBSERV** (12/06) | **À VÉRIFIER** post-déploiements |
| Routes evaluation-readiness / finalize absentes urlconf 404 | **REL OBSERV** (12/06) | **À VÉRIFIER** — code local les a depuis |

**Oracle cluster 11 (18/06) :** exécuté **sans credentials** — pas de scénario M1/EVAL1 authentifié.

---

## 10. Synthèse par tag

| Zone | Tag global |
|------|------------|
| Stack locale dev | **REL OBSERV** |
| Pipeline P0 legacy | **REL OBSERV** |
| Interface apprenant prod | **REL OBSERV** (tests auto 18/06 + E2E partiel 29/06) |
| Interface formateur prod | **REL OBSERV PARTIEL** (smoke OK ; élicitation bout-en-bout manuel) |
| Interface tuteur prod | **REL OBSERV PARTIEL** |
| Admin testeur / multi-tenant | **REL OBSERV** (30/06) |
| Encoors / prod distant | **À VÉRIFIER** |
| Hugo 2.0 spec | **CIBLE** |

---

*Suite recommandée : **R2** (domaines fonctionnels) ou **R4** (contrats JSON).*
