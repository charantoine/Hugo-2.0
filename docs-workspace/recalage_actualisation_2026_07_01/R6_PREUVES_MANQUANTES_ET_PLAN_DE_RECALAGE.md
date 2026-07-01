# R6 — Preuves manquantes et plan de recalage

**Date :** 1er juillet 2026  
**Successeur de :** `A6_QUESTIONS_OUVERTES_PREUVES_MANQUANTES_ET_A_VERIFIER.md` (22/06/2026).  
**État des preuves au :** 1er juillet 2026.

---

## 1. Ce qui reste non prouvé

### 1.1 Runtime distant Encoors / prod

| ID | Question | Dernière preuve | Tag |
|----|----------|-----------------|-----|
| PM-01 | Version / commit déployé vs `hugo_back` local | Aucune | **À VÉRIFIER** |
| PM-02 | Flags `HUGO_P0_*`, `LLM_PROVIDER` prod | Aucune | **À VÉRIFIER** |
| PM-03 | Parité routes `evaluation-readiness`, `finalize-evaluation`, `learner-conversation-profiles` | Absentes urlconf 12/06 | **À VÉRIFIER** |
| PM-04 | `conduct-profiles` distant | Absent 12/06 | **À VÉRIFIER** |
| PM-05 | SSE `/messages/stream/` (CORS, nginx timeout) | Non testé auth | **À VÉRIFIER** |
| PM-06 | memory-summary authentifié distant (M1) | Oracle sans credentials 18/06 | **À VÉRIFIER** |
| PM-07 | Chaîne EVAL1 complète distant | Oracle sans credentials 18/06 | **À VÉRIFIER** |
| PM-08 | Qualité LLM synthèse/évaluation distant | Aucune | **À VÉRIFIER** |
| PM-09 | `DEBUG` encore True sur distant | True 12/06 | **À VÉRIFIER** |
| PM-10 | RLS Postgres effectif prod | Template SQL non exécuté | **À VÉRIFIER** |

### 1.2 Local — lacunes résiduelles

| ID | Question | Tag |
|----|----------|-----|
| PM-11 | Synthèse/évaluation bout-en-bout UI (LLM réel) | **À VÉRIFIER** — E2E lot 9 SKIP |
| PM-12 | Lien TrainerKnowledgeItem validé → chunk cité en RAG tour | **À VÉRIFIER** |
| PM-13 | `usage_count` réel items formateur | **À VÉRIFIER** — null par design C15 |
| PM-14 | Parcours manuels C16 S16-A1→A5 | **À VÉRIFIER** — non exécutés 18/06 |
| PM-15 | Protocole L1 complet `demo.superadmin` | **À VÉRIFIER** — rapport 30/06 |
| PM-16 | Playwright lots 5–7, 9, 11 (scaffold) | **À VÉRIFIER** — données manquantes |
| PM-17 | Smoke Playwright sur postgres `hugo_poc` (vs sqlite) | **À VÉRIFIER** — mémo CTO |
| PM-18 | Staging intermédiaire (si existe hors Encoors) | **À VÉRIFIER** |

### 1.3 Décisions produit ouvertes (bloquent spec)

| ID | Sujet | Tag |
|----|-------|-----|
| PM-19 | ACL formateur : voir learners dashboard (INC-02) | **ÉCART CONFIRMÉ** — décision CTO |
| PM-20 | ADR memory-summary scope intra (`?scope=intra`) | **HYPOTHÈSE** — arbitrage CTO |
| PM-21 | Baseline officielle unique « Hugo aujourd'hui » (A vs B) | **HYPOTHÈSE** — doc 07 |

---

## 2. Preuves manquantes prioritaires (P0 → P2)

### P0 — Avant toute spec « prod » ou démo externe

| Priorité | Preuve | Méthode | Artefact attendu |
|----------|--------|---------|------------------|
| P0-1 | Oracle Encoors authentifié | `encoors_oracle.py` + credentials | `encoors_oracle_cluster11.generated.json` à jour |
| P0-2 | EVAL1 distant | scénarios oracle EVAL1 | JSON + horodatage |
| P0-3 | M1 memory-summary distant | GET auth session | JSON shape vs R4 |
| P0-4 | Décision INC-02 formateur | Réunion CTO | ADR ou note dans ecarts 90 |

### P1 — Avant specs UX formateur / évaluation avancée

| Priorité | Preuve | Méthode |
|----------|--------|---------|
| P1-1 | E2E synthèse lot 9 | Session seed GREEN + `npm run test:protocol` |
| P1-2 | E2E évaluation bout-en-bout | Idem + assert pivot trace |
| P1-3 | RAG item validé → citation tour | Test intégration dédié ou scénario manuel documenté |
| P1-4 | Re-probe CORS/SSE Encoors | curl + navigateur depuis `hugo.encoors.com` |

### P2 — Confort documentation / OPS

| Priorité | Preuve | Méthode |
|----------|--------|---------|
| P2-1 | RLS prod | Exécuter `audit_rls_prod_template.sql` |
| P2-2 | Manuel C16 S16 | Checklist cluster 16 §4 |
| P2-3 | Unifier ou documenter écart sqlite vs postgres smoke | ADR OPS |
| P2-4 | Mise à jour `10_FICHE_RUNTIME_PROD_ENCOORS.md` | Nouvelle inspection HTTP datée |

---

## 3. Plan d'acquisition de preuve (exécutable)

### Phase 1 — Semaine immédiate (local)

```bash
# 1. Confirmer stack
cd hugo_back && python manage.py print_runtime_stack

# 2. Regressions socle
cd hugo_back && python -m pytest \
  apps/hugo/tests/test_cluster3_oracles.py \
  apps/hugo/tests/test_cluster16_interface_apprenant_backend.py \
  apps/hugo/tests/test_cluster15_interfaces_apprenant.py \
  apps/accounts/tests/test_tenant_ui_campaign.py -q

# 3. E2E protocole (postgres dev)
cd hugo-hugolucia/frontend_1.8
# .env.local : VITE_API_URL=/api, VITE_FRONTEND_MODE=tester
npm run test:protocol
```

**Livrable :** rapport daté dans `docs-workspace/e2e-protocol-runtime/` (mise à jour RAPPORT).

### Phase 2 — Encoors (credentials requis)

```bash
export ENCOORS_BASE_URL=https://hugoback.encoors.com
export ENCOORS_USERNAME="..."
export ENCOORS_PASSWORD="..."
export ENCOORS_ORACLE_OUT=docs-workspace/encoors_oracle_2026_07.generated.json
cd hugo_back && python scripts/encoors_oracle.py
```

**Livrable :** JSON oracle + mise à jour doc 10 ou fiche R4 §10.

### Phase 3 — Décisions CTO

| Sujet | Owner | Sortie |
|-------|-------|--------|
| INC-02 ACL trainer | CTO | Option A/B/C documentée |
| ADR memory scope | CTO | `adr_c9_code02` statué |
| Baseline démo officielle | CTO | Note dans doc 07 |

### Phase 4 — Fermeture scaffold E2E

- Enrichir seeds : tutor links, RNCP attaché, session GREEN pour synthèse.
- Relancer lots 5–7, 9, 11 — cible 0 SKIP critique.

---

## 4. Ce qu'on peut déjà spécifier sans risque

S'appuyer sur **REL OBSERV** (code + tests P0) :

| Domaine | Périmètre spec sûr |
|---------|-------------------|
| UIState contract | Champs R4 §3 ; interdits P0 |
| Posture apprenant | set-posture + conversation_mode |
| Mémoire intra UI | session_memory panneau ; pas theme_memories |
| memory-summary API | Shape R4 §4 ; pas verbatim |
| Trainer validation C15 | Actions validate/provisional/reject/edit |
| Élicitation V0 | Questions/réponses/ingest chemin serveur |
| Multi-tenant superadmin | Header + bandeau ; pas fuite cross-org |
| RAG | Lexical uniquement ; pas vectoriel |
| Traces pivot v1 | generate-trace local |
| P0 | Interne ; jamais front `/app` |

---

## 5. Ce qu'il faut geler tant que la preuve n'existe pas

| Sujet gelé | Raison |
|------------|--------|
| « Prod Encoors = local » | PM-01 à PM-10 |
| Injection mémoire session dans prompt | Confirmé absent — lot futur |
| RAG vectoriel / pgvector actif | PM + tests garde-fou |
| Formateur voit timeline tous learners | INC-02 |
| EvaluationTrace 2.0 complète | CIBLE — pivot v1 suffit |
| Certification automatique évaluation | Doctrine — validation humaine |
| Intercalaires v1 runtime | Domaine 120 absent |
| LearnerThemeMemory au tour apprenant | Hors périmètre intra-conv |
| Compteur usage RAG formateur | PM-13 |
| Staging comme 3e vérité | PM-18 |

---

## 6. Questions héritées A6 — statut actualisé

| Question A6 (typologie) | Statut 01/07 |
|------------------------|--------------|
| Équivalence Encoors | **Ouvert** — PM-01–10 |
| SSE distant | **Ouvert** — PM-05 |
| Comptes démo complets | **Partiel** — doc 11 + seeds smoke/OF_test_2 |
| v17 en prod | **Ouvert** — PM-02 |
| RLS prod | **Ouvert** — PM-10 |
| OpenAPI public | **Confirmé absent** Encoors 12/06 |
| Docker compose officiel | **Confirmé non fiable** — E02 |
| Mémoire front | **Fermé** — C15/C16 |
| Posture interactive | **Fermé** — C15/C16 |
| Profils globaux | **Fermé** — V6 |

---

## 7. Prochaine sortie utile

1. Exécuter **Phase 1** et archiver résultats.
2. Obtenir credentials **Phase 2** ou marquer toute spec prod « conditionnelle Encoors ».
3. Trancher **INC-02** avant toute spec tuteur/formateur sur visibilité learners.

---

*Mode d'emploi specs : **R7**.*
