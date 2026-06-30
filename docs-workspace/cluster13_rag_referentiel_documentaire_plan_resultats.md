# Cluster 13 — RAG & référentiel documentaire (plan & clôture lot courant)

> Date : 2026-06-18  
> Scope : domaine **30** (référentiel documentaire / RAG)  
> Dépendances lecture : **20** (mémoire), **10** (UIState), **31** (badge Appui — plan cluster 12)  
> Garde-fou : `REFERENCE_CONVERGENCE_HUGO_REEL_VS_2_0_GARDEFOU.md`

---

## 1. Introduction

Le cluster 13 **clôt le domaine 30** au niveau Hugo 2.0 « lot courant » : doctrine RAG lexical gouverné, décision explicite sur le vectoriel, hiérarchie de contexte livrée, dossier d’écarts 30 consolidé. Le runtime (clusters 1–11) et le front apprenant (plan cluster 12) sont considérés **cadrés** — le RAG s’y insère comme **renfort situé**, jamais comme moteur ni mémoire principale.

Ce cluster est **majoritairement documentaire** (DOC). Aucune activation pgvector, aucune refonte orchestrateur, aucune modification du plan cluster 12 (31).

**Sources mobilisées :** garde-fou §3.3, spec canonique §18, compléments 2.0, matrice cluster 2, `ecarts — 30_referentiel_documentaire_rag.md`, code `rag_support.py`, `hugo_orchestrator.py`, `context_builder.py`, tests `test_rag_support_tracing.py`, plan cluster 12.

---

## 2. CIBLE 2.0 pour le RAG documentaire

### Doctrine (spec canonique + compléments)

- **Référentiel métier** : couche primaire d’orientation (couverture, traces, overlays groupe).
- **Base formateur** (`TrainerKnowledgeItem`) : savoir dérivé, validation humaine, enrichit sans remplacer le référentiel.
- **RAG documentaire** : question-driven, documents **ACTIFS** du groupe, renfort situé post-décision ; jamais mémoire principale ni moteur de cours.
- **Hiérarchie de contexte** (doctrine) : état apprenant structuré → mémoire gouvernée → verbatim interne borné → overlay référentiel → documentaire/RAG.
- **RAG vectoriel** : compatible cible 2.0 mais **non figé** comme moteur obligatoire ; toute vectorisation reste additive et prouvable.

### Lot courant retenu (cluster 13)

| Capacité | Statut lot courant |
|----------|-------------------|
| RAG lexical gouverné | **LIVRÉ** (runtime local) |
| Citations produit (badge Appui) | **LIVRÉ** |
| Hiérarchie contexte | **DOCUMENTÉE** (contrat v1 ci-dessous) |
| RAG vectoriel (pgvector) | **COURONNE** — off, explicité |
| DocumentContextBundle formel | **P2 DOC** — backlog, pas bloquant |
| Panneau ressources apprenant autonome | **INTERDIT** — hors doctrine |

---

## 3. RÉEL OBSERVÉ

### 3.1 Backend — pipeline RAG lexical

| Objet / service | Fichier | Rôle observé |
|---------------|---------|--------------|
| Sélection chunks | `apps/hugo/services/rag_support.py` | `select_rag_chunks`, `should_use_rag`, scoring lexical + meta posture |
| Gating posture | `should_use_rag` | Règles distinctes `diagnostic` / `reflective_afest` / `knowledge_review` |
| Orchestration | `hugo_orchestrator.py` | RAG **après** décision + teaching plan (L330–337), avant `build_session_memory` |
| Contexte référentiel | `context_builder.py` | Items référentiel, traces récentes, titres docs groupe |
| Citations persistées | `tracing.persist_rag_citations` | Liens message assistant ↔ chunks |
| Exposition API message | `views_sessions._compact_rag_citations` | `document_id`, `title`, `chunk_id`, `score`, `reason` — **sans contenu chunk brut étendu** |
| Indexation | `library/tasks.py`, `chunking.py` | Chunking texte **500 car.**, overlap 50 — **pas d’embedding calculé** |
| Modèle embedding | `library/models.py` | `EmbeddingField` pgvector ou TextField fallback — **champ présent, non peuplé ni interrogé** |
| Debug interne | `views_internal.RagSearchView` | `POST /internal/rag/search` — calibration, pas surface apprenant |
| Ingestion groupe | `GroupDocument` ACTIVE | Filtre tenant + groupe dans `select_rag_chunks` |

**Tests prouvés :** `apps/hugo/tests/test_rag_support_tracing.py` (priorisation procedure, profil doc, skip low-risk), `apps/library/tests/test_library_ingestion.py`.

### 3.2 Surfaces produit

| Surface | RAG visible ? | Détail |
|---------|---------------|--------|
| **Apprenant prod** (`ProdLearnerWorkspace.vue`) | **Oui, minimal** | Badge « Appui : {titre} » sur messages assistant si `rag_citations` |
| **UIState apprenant** | **Non** | Pas de liste documents ni moteur recherche — conforme doctrine |
| **ORGADMIN** (`GroupAdminDetailView`) | **Back-office** | Upload, liaison groupe, métadonnées `knowledge_type`, `intended_profiles` |
| **Formateur** (`ProdTrainerKnowledgeView`) | **Parallèle** | `TrainerKnowledgeItem` — canal distinct du RAG documentaire tour |
| **Testeur** (`LearnerDetailView`) | **Hors prod** | Expose `turn_state` — **ne pas généraliser au parcours `/app`** |

Cohérence cluster 12 : le RAG apprenant reste **badge Appui complémentaire** ; copy profil via `displayProfileCopy` (clé `ragSupportLabel` planifiée P1).

### 3.3 Mémoire & articulation (domaine 20 — lecture)

| Couche | Runtime tour | Exposition front apprenant |
|--------|--------------|----------------------------|
| SessionMemoryContract | Construit post-tour (`build_session_memory`) | Via `ui-state` / memory-summary encadrant — **pas panneau mémoire apprenant** |
| LearnerThemeMemory inter-session | **Non injecté** au tour (clusters 9–11) | `theme_memories` dans memory-summary — ADR scope |
| Verbatim messages | Contexte LLM interne | **Non exposé** prod apprenant |

Le RAG **ne remplace pas** la mémoire intra-conversation ; ordre de priorité doctrinal respecté dans le pipeline (état → décision → RAG en renfort).

### 3.4 Encoors / prod

**A_VÉRIFIER** — aucun oracle RAG authentifié exécuté cluster 13.

Protocole prêt (hérité cluster 11) : avec session groupe documentée + message déclenchant `should_use_rag`, vérifier présence `rag_citations` dans réponse message ; confirmer absence endpoint vectoriel actif.

---

## 4. Décision cluster 13 sur pgvector

### Statut retenu : **OFF — Couronne / CIBLE 2.0 future**

**Motifs (réel + risque) :**

1. `select_rag_chunks` est **100 % lexical** — aucune requête embedding.
2. `index_document` crée des chunks texte sans calcul vectoriel.
3. Activer pgvector exigerait : pipeline embeddings, stratégie de requête hybride, tests OPS, gouvernance confidentialité chunk — **effort CODE/OPS significatif**, hors périmètre clôture noyau.
4. Tous les clusters 2–12 ont classé vectoriel en **Couronne** ; cohérence maintenue.

**Impacts :**

| Type | Action |
|------|--------|
| **DOC** | Interdire formulations « RAG vectoriel actif » pour le réel ; réserver à backlog Couronne |
| **CODE** | **Aucun** dans cluster 13 |
| **OPS** | Option P2 : variable env `HUGO_RAG_VECTOR_ENABLED=false` documentée (sans implémenter si absent) |

**Alternative rejetée :** activation minimale pgvector — rejetée pour ce lot (complexité hiérarchie contexte + non-besoin prouvé vs lexical opérationnel).

---

## 5. Hiérarchie de contexte finale livrée (lot courant)

Contrat **v1 lot courant** — aligné runtime observé + doctrine 2.0, sans prétendre à l’agrégat `DocumentContextBundle` complet.

### 5.1 Ordre de priorité (doctrine / vérité comportementale)

```
1. État apprenant structuré     TurnState + P0 + ConversationDecision + ConversationProgress
2. Mémoire intra-conversation SessionMemoryContract (gouvernée, sans verbatim)
3. Verbatim interne borné       Historique tour courant côté prompt — NON exposé front prod
4. Overlay / référentiel métier Items compétences, critères, coach_questions (context_builder)
5. Documentaire titre / méta    Liste docs actifs groupe (contexte compact)
6. RAG lexical chunks           select_rag_chunks — renfort post-décision, gating posture
─── COURONNE ───
7. Mémoire inter-session        LearnerThemeMemory — consolidée, non injectée tour
8. RAG vectoriel                pgvector — champ modèle seulement
9. TrainerKnowledgeItem → tour  Canal formateur — partiel, hors injection directe chunks tour
```

### 5.2 Séquence runtime observée (`build_hugo_turn`)

1. `build_hugo_context` — référentiel, traces, docs groupe  
2. Posture → analyse tour → P0 → décision → teaching plan  
3. **`select_rag_chunks`** — si `should_use_rag` + docs ACTIVE + overlap lexical  
4. `build_session_memory` — mémoire intra tour  
5. `build_ui_state` / rendu prompt avec snippets RAG  

### 5.3 Front apprenant (cluster 12 — non modifié)

- Consomme **UIState** + messages (`rag_citations` compactes).
- **Pas** de panneau recherche documentaire ; badge Appui uniquement.
- Posture influence RAG **côté backend** (`should_use_rag`, `_score_document_meta`) — pas de logique RAG front.

### 5.4 Invariants confidentialité

- Pas de verbatim brut dans citations produit (`_compact_rag_citations` : métadonnées seulement).
- Pas de contenu chunk complet dans UIState apprenant.
- RAG limité aux documents **ACTIVE** du **groupe** de la session (filtre tenant).

---

## 6. Plan d’actions cluster 13 (tableau)

| Axe | Type | Domaine | Priorité | Fichier(s) impacté(s) |
|-----|------|---------|----------|------------------------|
| Doctrine RAG lot courant | **DOC** | 30 | **P0** | `ecarts — 30_...md`, `specs interface 2.0.md` § RAG |
| Décision pgvector OFF | **DOC** | 30 | **P0** | `cluster13_*.md`, garde-fou, inventaire |
| Hiérarchie contexte v1 | **DOC** | 30/20 | **P0** | `ecarts — 30`, `ecarts — 20` § articulation |
| Noms réels (`rag_support.py`, etc.) | **DOC** | 30 | **P1** | spec canonique §18, compléments |
| DocumentContextBundle | **DOC** | 30 | **P2** | backlog Couronne — contrat futur |
| Activation pgvector | **CODE** | 30 | **P2 Couronne** | `library/`, `rag_support.py` — **hors cluster 13** |
| Flag `HUGO_RAG_VECTOR_ENABLED` | **CODE** | 30 | **P2** | `settings` — seulement si arbitrage futur |
| Test sélection posture × RAG | **CODE** | 30 | **P1** | `test_rag_support_tracing.py` — étendre si gap |
| Smoke UI badge Appui | **OPS** | 31/30 | **P1** | `tests_playwright/test_b1_rag_appui.spec.ts` (plan C12) |
| Oracle Encoors RAG | **OPS** | 30 | **P2** | protocole cluster 11 — **A_VÉRIFIER** |
| Copy `ragSupportLabel` profils | **CODE** | 31 | **P1** | `displayProfileCopy.js` — hérité cluster 12 |

---

## 7. Mise à jour écarts 30 — trame consolidée

Le fichier **`ecarts — 30_referentiel_documentaire_rag.md`** est mis à jour (§ cluster 13). Synthèse :

### CIBLE 2.0
- Triptyque référentiel → base formateur → RAG renfort ; hiérarchie contexte §5 ci-dessus ; vectoriel = capacité future.

### RÉEL OBSERVÉ
- RAG lexical opérationnel ; pgvector inactif ; citations Appui ; ingestion/indexation chunks ; gating posture ; pas de panneau RAG apprenant.

### ÉCARTS CONFIRMÉS
| Écart | Statut post-C13 |
|-------|-----------------|
| RAG vectoriel supposé vs lexical réel | **CLÔTURÉ DOC** — désambiguïsation |
| Hiérarchie contexte non contractualisée | **CLÔTURÉ DOC** — contrat v1 §5 |
| DocumentContextBundle absent | **OUVERT P2** — Couronne |
| TrainerKnowledgeItem → pipeline tour | **PARTIEL** — formalisation future |
| Lien item formateur → chunks RAG | **A_VÉRIFIER** |

### A_VÉRIFIER
- Parité RAG Encoors ; embeddings prod ; consommation effective TrainerKnowledgeItem au tour.

### ACTIONS cluster 13 (backlog court)

| ID | Type | Action |
|----|------|--------|
| C13-DOC-01 | DOC | Consolidation écarts 30 § cluster 13 |
| C13-DOC-02 | DOC | Hiérarchie contexte v1 dans spec / compléments |
| C13-DOC-03 | DOC | Interdiction sémantique « RAG vectoriel actif » réel |
| C13-OPS-01 | OPS | Smoke Playwright badge Appui (avec C12 B1-06) |
| C13-CODE-01 | CODE | **Aucun P0** — pgvector repoussé Couronne |

---

## 8. Garde-fous de non-régression

- [ ] RAG reste **post-décision** dans l’orchestrateur — pas de déplacement avant P0/décision.
- [ ] Pas de panneau recherche documentaire apprenant autonome.
- [ ] Pas d’exposition chunk texte intégral au front prod (citations compactes seulement).
- [ ] `should_use_rag` conserve gating posture — pas de RAG systématique.
- [ ] Mémoire inter-session **non injectée** tour — inchangé (domaine 20).
- [ ] Cluster 12 (sélecteur posture, profils UX) **non modifié** par cluster 13.
- [ ] Tests `test_rag_support_tracing.py` restent PASS après toute évolution future.

---

## 9. Conclusion opérationnelle

Le domaine 30 est **clôturable en lot courant** sur la base du **RAG lexical gouverné** déjà livré : doctrine fixée, pgvector explicitement **Couronne**, hiérarchie de contexte **documentée v1**, écarts 30 consolidés. Aucun patch CODE P0 requis pour cette clôture.

**Verrouillé (local) :** sélection lexical, gating posture, citations Appui, ingestion chunks, séparation debug `/internal/rag/search`.

**Explicitement Couronne :** pgvector, DocumentContextBundle, panneau ressources avancé, chaîne trainer → RAG tour complète.

**Prochain cluster naturel :** implémentation P0 cluster 12 (UX apprenant postures) — indépendant du RAG ; ou cluster Couronne si activation vectorielle arbitrée.
