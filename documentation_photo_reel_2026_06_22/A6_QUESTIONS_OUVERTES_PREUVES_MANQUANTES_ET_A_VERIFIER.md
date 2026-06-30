# A6 — Questions ouvertes, preuves manquantes et A_VERIFIER

**Date :** 22 juin 2026  
**Statut des entrées :** **A_VERIFIER** sauf mention **ÉCART CONFIRMÉ** ou **HYPOTHÈSE**.

---

## 1. Runtime distant / Encoors

| Point | Ce qu'on sait | Ce qui manque |
|-------|---------------|---------------|
| Version déployée | Urlconf proche local (inspection 12/06) | Commit git, date deploy |
| Flags `HUGO_P0_*` | Inconnus | Lecture env ou test comportemental |
| `DEBUG` prod | **OBSERVÉ True** (page 404) | Décision correction |
| CORS localhost:5173 | **OBSERVÉ refusé** | Politique dev distant |
| SSE flux réel | Route dans urlconf | Test authentifié stream |
| LLM provider prod | Inconnu | Latence, qualité, coût |
| Parcours login complet | Non testé inspection (pas credentials) | Fiche comptes 11 |
| Routes absentes vs local | conduct-profiles, evaluation-readiness | Re-test post 20/06 |

**Source :** `10_FICHE_RUNTIME_PROD_ENCOORS.md`

---

## 2. Flags actifs

| Flag | Local défaut | Prod | Méthode vérification |
|------|--------------|------|----------------------|
| `HUGO_P0_V17_ENABLED` | false | ? | Env + tour test |
| `HUGO_P0_CLASSIFIER_ENABLED` | false | ? | Logs tracing |
| `HUGO_PHASE_CLASSIFIER_ENABLED` | true | ? | Comportement phase |
| `ENABLE_EXTERNAL_LLM` | true | ? | Chat fonctionnel |
| Override session classifieur | Possible | ? | Inspecter session démo |

---

## 3. RLS réelle

| Point | Local | Prod |
|-------|-------|------|
| Middleware présent | **RÉEL OBSERVÉ** | ? |
| Tests cross-tenant | SQLite | Postgres RLS ? |
| Playwright tenant 11/11 | Local 20/06 | Encoors ? |
| Fuite inter-org données | Non prouvé en prod | Audit SQL requis |

---

## 4. Périmètre effectif prod

- Quel build front est servi : `frontend/` vs `frontend_1.8/` — **AMBIGU**.
- Nginx compose vs hébergement `hugo.encoors.com` — **A_VERIFIER**.
- Fonctions cluster 16 disponibles sur Encoors — **A_VERIFIER**.
- Profils globaux apprenant en prod — **A_VERIFIER**.

---

## 5. Richesse exports / bundles

| Artefact | Local | Prod |
|----------|-------|------|
| ExportRun CSV/JSON | Testé | ? |
| EvidenceBundle ZIP | Testé E2E v5 | ? |
| trace_rich_v1 + pivot | Partiel critères vides | ? |
| D9bis export LLM analysis | SUPERADMIN local | ? |
| Contenu métadonnées traces bundle | POC | Audit données réelles |

---

## 6. Mémoire : injectée ou seulement exposée ?

| Mécanisme | Injection tour | Exposition API/UI | Statut |
|-----------|----------------|-------------------|--------|
| `build_session_memory` | Objet orchestrateur ; **pas prompt** | memory-summary, panneau | **ÉCART CONFIRMÉ** prompt |
| `LearnerThemeMemory` | **Non** | memory-summary theme | **ÉCART CONFIRMÉ** |
| UIState mémoire | Absent | — | **CIBLE** |
| Consolidation post-message | **RÉEL OBSERVÉ** | Indirect | OK écriture |

---

## 7. RAG vectoriel vs lexical

| Question | Statut |
|----------|--------|
| Embeddings calculés à l'indexation ? | **NON** local — **ÉCART CONFIRMÉ** |
| pgvector utilisé en runtime ? | **NON** — **ÉCART CONFIRMÉ** |
| Sélection = lexical tokens | **RÉEL OBSERVÉ** |
| Items formateur consommés RAG ? | **A_VERIFIER** |
| Hiérarchie contexte documentaire | **PARTIEL** non contractualisé |

---

## 8. Part réelle de v17

| Question | Réponse connue | À vérifier |
|----------|----------------|------------|
| Code v17 présent ? | Oui, complet | — |
| Activé par défaut local ? | Non | — |
| Activé prod ? | Inconnu | Flags + tests |
| Tests v17 | Opt-in flag | Couverture prod-like |
| Stratégie migration | Absente | Décision CTO |

---

## 9. Surfaces tuteur / formateur servies

| Surface | Local | Encoors |
|---------|-------|---------|
| `/app/tutor` timeline | Livré cluster 3 | ? |
| `/app/trainer/knowledge` | Livré C15 | ? |
| Élicitation formateur | V0 | ? |
| Validation knowledge | UI C15 | ? |
| Exports trainer eval | API | ? |

---

## 10. Autres points non définitivement prouvés

### Technique

- Efficacité `recalc_learner_state` (placeholder).
- Token OVH en dur : utilisé en prod ?
- `production.py` DEBUG=True : reflète-t-il Encoors ?
- Playwright E2E : absent du repo — couverture réelle démo ?

### Produit

- Scénarios manuels S16-A1→A5 (cluster 16) — non tous exécutés.
- Starter prompts admin — API seule testeur.
- Orchestrateur params éditables — panneau read-only.
- `session.learner_conversation_profile` REST PATCH — absent.
- Rôle COORDO — absent.
- Intercalaires derrière flag distant ? — **A_VERIFIER** INT-022.

### Documentaire

- Fiche `11_FICHE_COMPTES_ET_DONNEES_DEMO.md` — **à produire**.
- Équivalence git branches main/hugolucia.
- Procédure baseline B « officielle ».

---

## 11. Matrice de preuve manquante par domaine

| Domaine | Preuve forte locale | Trou principal |
|---------|---------------------|----------------|
| 10 P0/UIState | pytest cluster 4/16 | v17 prod |
| 20 Mémoire | contract tests | injection prompt |
| 30 RAG | lexical tests | vectoriel, lien formateur |
| 31 Front postures | Playwright 10/10 | Encoors |
| 40–50 Formateur | C15 tests | F2–F4 E2E |
| 60 Tuteur | B1-01 oracle | prod surface |
| 70 Eval/traces | guard tests | trace riche prod |
| 80 Observabilité | signaux tests | catalogue, dashboards |
| 90 Confidentialité | 10 tests + Playwright | RLS Postgres |
| 100 Exports | E2E v5 | Encoors bundle |
| 110 Interfaces | C15/C16 | tuteur prod |
| 120 Intercalaires | audit code | aucun réel |

---

## 12. Prochaines actions de preuve recommandées

1. **Fiche runtime Encoors authentifiée** : login compte démo + 1 tour + ui-state + flags inférés.
2. **Test SSE** depuis origine front réelle (`hugo.encoors.com`).
3. **Audit RLS** Postgres staging/prod avec `test_cross_tenant` adapté.
4. **Diff routes** local HEAD vs Encoors urlconf (automatisé).
5. **Rejeu pytest + Playwright** avant toute spec qui suppose régression 0.

---

*Liste exhaustive non garantie — compléter par relecture `ecarts — *.md` et oracles cluster 2.*
