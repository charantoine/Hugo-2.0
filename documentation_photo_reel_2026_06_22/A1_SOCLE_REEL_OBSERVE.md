# A1 — Socle réel observé

**Date :** 22 juin 2026  
**Statut dominant :** RÉEL OBSERVÉ (local audité) + A_VERIFIER (runtime distant)

---

## 1. Cartographie synthétique du workspace

### 1.1 Quatre piliers

| Pilier | Emplacement | Rôle | Statut |
|--------|-------------|------|--------|
| Moteur | `hugo_back/` | Django 5.2+, API, P0, persistence, tests pytest | **RÉEL OBSERVÉ** |
| Produit | `hugo-hugolucia/frontend_1.8/` | Parcours `/app`, mode testeur, SSE, UIState | **RÉEL OBSERVÉ** |
| Snapshot | `hugo-main/` | Specs 1.8, front en retard | ARCHIVE / non référence |
| Bibliothèque | `docs-workspace/` | Recalage 00–10, écarts, clusters | **RÉEL OBSERVÉ** (docs) |

### 1.2 Hiérarchie de vérité (voir `00_HIERARCHIE_DOCUMENTAIRE.md`)

1. Code `hugo_back/`
2. Tests `hugo_back/`
3. Front `hugo-hugolucia/frontend_1.8/`
4. Docs récentes workspace
5. Specs historiques
6. Archives

**Règle :** une spec seule ne prouve jamais un comportement implémenté.

---

## 2. Moteur réel (`hugo_back`)

### 2.1 Stack

- Python 3.11, Django ≥5.2, DRF, SimpleJWT, PostgreSQL, pgvector (champ présent, sélection runtime lexicale), Celery/Redis, MinIO/S3.
- Point d'entrée : `manage.py` → `config.settings.dev` par défaut.
- 30+ fichiers `test_*.py` hors venv.

### 2.2 Apps Django structurantes

| App | Rôle |
|-----|------|
| `accounts` | JWT, orgs, users, multi-tenant |
| `hugo` | Sessions, messages, orchestrateur, P0, traces, évaluation |
| `referentials` | Groupes, RNCP, import v2 |
| `library` | Documents, chunks, indexation |
| `exports` | Export CSV/JSON synchrone |
| `quality` | Bundle evidence Qualiopi lite |
| `app_core` | Middleware RLS tenant |

### 2.3 Flags structurants (défaut local)

| Flag | Défaut | Effet |
|------|--------|-------|
| `HUGO_P0_V17_ENABLED` | `false` | Pipeline legacy actif |
| `HUGO_P0_CLASSIFIER_ENABLED` | `false` | Classifieur LLM P0 off |
| `HUGO_PHASE_CLASSIFIER_ENABLED` | `true` | Classifieur phase LLM on |
| `ENABLE_EXTERNAL_LLM` | `true` | Appels LLM autorisés |

**A_VERIFIER :** valeurs sur `hugoback.encoors.com`.

### 2.4 Pipeline conversationnel (résumé)

Point d'entrée : `build_hugo_turn()` dans `hugo_orchestrator.py`.

Ordre observé (stack legacy par défaut) :

1. `build_hugo_context`
2. `resolve_posture` + `resolve_conduct_profile`
3. `analyze_turn_state` → TurnState heuristique
4. `classify_p0_turn_state` (si flag classifieur)
5. `decide_conversation` (ou v17 si flag)
6. `build_teaching_plan`
7. `decide_next_phase`
8. `select_rag_chunks`
9. `build_session_memory`
10. `build_conversation_progress` + contrat
11. `build_ui_state` / `build_contract_ui_state`
12. Rendu prompt → LLM → guardrails → persistance
13. `_post_conversation_hooks` : consolidation mémoire + signaux qualité

**ÉCART CONFIRMÉ :** double stack P0 legacy + v17 coexistent ; pas de stratégie migration documentée dans le code.

---

## 3. Produit réel (`hugo-hugolucia/frontend_1.8`)

### 3.1 Modes

| Mode | Activation | Surface |
|------|------------|---------|
| `prod_showable` | Défaut (`VITE_FRONTEND_MODE` absent) | `/app`, `/app/session/:id` |
| `tester` | `VITE_FRONTEND_MODE=tester` | Dashboard, admin, debug P0 |

### 3.2 API cible par défaut

```
VITE_API_URL=https://hugoback.encoors.com
```

**RÉEL OBSERVÉ :** démo courante = baseline A (front local + API distante).  
**A_VERIFIER :** équivalence comportementale avec `hugo_back` local.

### 3.3 Contrat produit central

`GET /hugo/sessions/{id}/ui-state/` — progression, scène, quêtes, CTA synthèse/évaluation, objets persistants, `conversation_mode`, `learner_display_profile`.

**RÉEL OBSERVÉ :** front prod ne recalcule pas P0 localement (`engagementUiModel.js`).

### 3.4 Évolutions récentes (audits cluster 15–16, 18–20/06/2026)

- `PostureSelector.vue`, bandeau scène, CTA advisory évaluation
- `LearnerMemoryPanel.vue` (mémoire intra-conversation)
- `LearnerConversationGlobalProfile` + admin `/admin/conversation/learner/profiles`
- Playwright : 10/10 posture, 11/11 tenant (archive `tests/archives/tests_hugo_2_0_2026-06-18_20.md`)

---

## 4. Architecture de workspace

```
hugo_back (MOTEUR)  ←──HTTP API──→  hugo-hugolucia/frontend_1.8 (PRODUIT)
        ↑                                    ↑
        │                                    │
   pas d'import Python croisé          backend/ vide dans monorepo
```

**ÉCART CONFIRMÉ :** `docker-compose.yml` monorepo référence `./backend` vide — stack complète non lançable sans rattacher `hugo_back`.

**AMBIGU :** nginx compose sert `frontend/dist`, pas `frontend_1.8/dist`.

---

## 5. Runtime de démo

### Baselines (voir `07_RUNTIME_DEMO_REFERENCE.md`)

| Baseline | Composition | Usage |
|----------|-------------|-------|
| **A** | Front 1.8 + Encoors | Démo produit stakeholder |
| **B** | Front 1.8 + `hugo_back` local | Preuve moteur |
| **C** | Mixte documenté | Stratégie, pas stack unique |

### Inspection Encoors (12/06/2026 — `10_FICHE_RUNTIME_PROD_ENCOORS.md`)

**RÉEL OBSERVÉ :**
- API HTTPS disponible, JWT actif
- `DEBUG=True` exposé sur page 404
- CORS autorise `https://hugo.encoors.com` ; **pas** `localhost:5173`
- Routes cœur présentes (`ui-state`, `request-synthesis`, `messages/stream/`)

**RÉEL OBSERVÉ — absent sur Encoors vs local récent :**
- `/hugo/conduct-profiles/`
- `/hugo/sessions/{id}/evaluation-readiness/`
- `/hugo/sessions/{id}/finalize-evaluation/` (probable)

---

## 6. Dépendances local / distant / flags

| Dimension | Local audité | Encoors | Statut |
|-----------|--------------|---------|--------|
| P0 legacy | ON (défaut) | Inconnu | A_VERIFIER |
| P0 v17 | OFF (défaut) | Inconnu | A_VERIFIER |
| Classifieur P0 | OFF global | Inconnu | A_VERIFIER |
| Synthèse LLM | Implémentée | Inconnu | A_VERIFIER |
| SSE stream | Endpoint présent | Route urlconf ; flux non testé | A_VERIFIER |
| RLS Postgres | Middleware + tests SQLite | Inconnu | A_VERIFIER |
| Conduct profiles API | Présent | Absent (inspection 12/06) | ÉCART CONFIRMÉ distant |

**Override session/groupe :** classifieur P0 ou provider LLM peuvent être activés par session même si flag global off (`p0_classifier.py`, `Group.llm_backend`).

---

## 7. Points robustes

- Backend-first confirmé : UIState, CTA, progression calculés côté serveur.
- Pipeline P0 legacy testé (forte couverture `test_p0_*`, `test_hugo_calibration_scenarios.py`).
- Parcours apprenant `/app` bout-en-bout branché (chat, ui-state, synthèse, évaluation, trace, partage).
- TutorConductProfiles : modèle + CRUD + resolver dans orchestrateur.
- Mémoire intra-session : `SessionMemoryContract`, endpoint `memory-summary`, panneau front cluster 16.
- RAG lexical opérationnel avec traçage.
- Multi-tenant : modèle `organisation_id`, middleware RLS, tests cross-tenant.
- Exports CSV/JSON, EvidenceBundle, workflow évaluation avec garde-fous maturité.
- Confidentialité tuteur B1-01 : verbatim masqué si non partagé (tests cluster 3).

---

## 8. Points ambigus

- Équivalence git / branche officielle entre `hugo-main` et `hugo-hugolucia`.
- Stratégie d'intégration : 3 dossiers séparés vs réinjection `hugo_back` dans monorepo.
- Double builder UIState : `build_ui_state` vs `build_contract_ui_state`.
- `LearnerThemeMemory` : écriture post-message OK ; injection tour absente — périmètre lot courant vs cible 2.0.
- `EvaluationTrace` doctrinal vs dispersion `LearnerEvaluationRecord` + `Trace` + pivot.
- `production.py` local avec `DEBUG=True` — config prod incohérente.
- Token OVH en dur dans `base.py` — risque sécurité.

---

## 9. Corrections apportées par audits récents (vs socle 00–10 seul)

| Domaine | Ancien constat 00–10 | Audit plus récent | Arbitrage retenu |
|---------|---------------------|-------------------|------------------|
| Synthèse | MEMO CTO : stub | LLM + fallback (`synthesis_service.py`) | **RÉEL OBSERVÉ** — MEMO obsolète |
| Boutons prod | MEMO : non branchés | Branchés (`ProdLearnerWorkspace.vue`) | **RÉEL OBSERVÉ** |
| Consolidation mémoire | MEMO : trace-only | Après chaque message (`_post_conversation_hooks`) | **RÉEL OBSERVÉ** |
| Posture / scène UI | Partiel | Cluster 16 : sélecteur + bandeau | **RÉEL OBSERVÉ PARTIEL+** local |
| Profils globaux apprenant | Non couvert 00–10 | Cluster 20/06 : `LearnerConversationGlobalProfile` | **RÉEL OBSERVÉ** local |
| Encoors conduct-profiles | Non inspecté 05 | Absent inspection 10 | **ÉCART CONFIRMÉ** distant |
| Mémoire panneau | Non couvert 03 | `LearnerMemoryPanel` cluster 16 | **RÉEL OBSERVÉ PARTIEL+** |

Source matrice transversale : `cluster2_matrice_runtime_vs_cible.md` v6 (20/06/2026).

---

## 10. Matrice de vérité par bloc (synthèse)

| Bloc | Source la plus fiable | Date | Statut | Conflit | Arbitrage |
|------|----------------------|------|--------|---------|-----------|
| Moteur P0 | `02_ETAT_MOTEUR_REEL.md` + code | juin 2026 | RÉEL OBSERVÉ | Spec 1.6.2 | Code prime |
| Produit `/app` | `03` + cluster 16 | 18–20/06 | RÉEL OBSERVÉ | MEMO CTO | Code + tests C16 |
| Encoors | `10_FICHE_RUNTIME_PROD_ENCOORS.md` | 12/06 | RÉEL OBSERVÉ partiel | Local juin | Distinct, A_VERIFIER flags |
| Mémoire | `ecarts — 20_memoire_gouvernee.md` | 18/06 | PARTIEL | LOT4 spec | Lot intra-conv. prioritaire |
| Écarts transverses | `05` + cluster 2 | 20/06 | ÉCART CONFIRMÉ | Audits mai | Cluster 2 prime si plus fin |

---

*Sources : 00–10, cluster2_matrice v6, clusters 15–16, code local. Runtime distant partiellement inspecté.*
