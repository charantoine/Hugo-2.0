# R2 — Cartographie fonctionnelle actualisée

**Date :** 1er juillet 2026  
**Rôle :** mise à jour de `A2_CARTOGRAPHIE_FONCTIONNELLE_EXISTANT.md` (22/06/2026).  
**Méthode :** par domaine — réel observé, changements depuis juin 2026, partiels, dépendances runtime non prouvé.

---

## Légende

| Tag | Usage dans ce document |
|-----|------------------------|
| **REL OBSERV** | Livré et recoupé code + test |
| **REL OBSERV PARTIEL** | Livré sur un sous-ensemble de surfaces ou rôles |
| **CART CONFIRM** | Écart doc/code formalisé |
| **À VÉRIFIER** | Dépend Encoors, prod, ou preuve manquante |
| **CIBLE** | Spec 2.0 non prouvée livrée |

---

## Domaine 10 — Runtime, P0, progression, UIState

### Réel observé

- Pipeline tour via `build_hugo_turn()` — stack **legacy** par défaut (**REL OBSERV**).
- Progression structurée `ConversationProgress` persistée sur session (**REL OBSERV**).
- **Double surface UIState** :
  - **Contract** (`build_contract_ui_state`) — consommé par `GET .../ui-state/` (**REL OBSERV**).
  - **Engagement** (`build_ui_state`) — payloads tour SSE/POST avec panneaux gamification (**REL OBSERV PARTIEL** — pas le même schéma que GET ui-state).
- CTA synthèse et évaluation dans contract UIState (`cta_synthesis`, `cta_evaluation`) (**REL OBSERV** — B16-C1/C2).
- Scène : `scene_label`, `scene_progress`, `dispersion_risk`, `priority_branch_label` (**REL OBSERV** — B16-S1).

### Changé depuis 22/06

- Renforcement tests cluster 16 (15 backend + 10 Playwright).
- Matrice cluster 2 **V6** : profils d'affichage + conversation_mode stabilisés.

### Partiel / ouvert

- Stack P0 v17 : code présent, flag off — **À VÉRIFIER** si activation démo.
- Verrou phase/tours avancé (spec 2.0) : **CIBLE**.

### Runtime non prouvé

- Comportement P0 sur Encoors : **À VÉRIFIER**.

**Fichiers historiques :** A2 § runtime — **complété** ; A4 — voir **R3**.

---

## Domaine 20 — Mémoire gouvernée intra-conversation

### Réel observé

- `SessionMemoryContract` produit par `build_session_memory_contract` (**REL OBSERV**).
- `GET .../memory-summary/` : blocs `session_memory` + `theme_memories` (**REL OBSERV**).
- Panneau apprenant `LearnerMemoryPanel.vue` : affiche **uniquement** `session_memory` (**REL OBSERV** — C15 A3).
- Consolidation post-tour `consolidate_session` → `LearnerThemeMemory` (**REL OBSERV** — inter-session préparée).
- **Pas d'injection** du contrat mémoire dans les prompts LLM du tour (**REL OBSERV** — audit code prompt).

### Changé depuis 22/06

- Front consomme memory-summary (A2 disait absent).
- Tests B16-M1/M2, A1 memory tests cluster 15.

### Partiel

- ADR scope `?scope=intra` pour masquer `theme_memories` : **CIBLE** / décision CTO en attente.
- Mémoire dans `persistent_objects` UIState engagement (tour) vs panneau dédié : deux surfaces — **CART CONFIRM**.

### Runtime non prouvé

- Shape memory-summary Encoors : **À VÉRIFIER**.

**Fichiers historiques :** `contrat_api_memory_summary_v1.md` — **confirmé** ; `ecarts — 20_memoire_gouvernee.md` — à mettre à jour via **R5**.

---

## Domaine 30 — Référentiel documentaire / RAG

### Réel observé

- Bibliothèque : upload, chunks, `GroupDocument` (**REL OBSERV**).
- Sélection RAG **lexical** : overlap tokens dans `rag_support.select_rag_chunks` (**REL OBSERV**).
- `pgvector` en dépendance ; **pas de requête vectorielle** dans le chemin actif (**REL OBSERV** — `test_preprod_garde_fou.py`).
- Panneau documents apprenant via `supporting_documents` dans UIState tour (**REL OBSERV PARTIEL**).

### Changé depuis 22/06

- Inchangé sur le fond lexical ; cluster 15 B3 note `usage_count` null côté trainer.

### Partiel

- Lien TrainerKnowledgeItem validé → chunk RAG runtime : **À VÉRIFIER** bout-en-bout.
- Hiérarchie contexte documentaire spec 2.0 : **CIBLE**.

**Fichiers historiques :** A2 § RAG — **toujours valide** (lexical).

---

## Domaine 31 — Front apprenant, postures, bascule

### Réel observé

- `conversation_mode` dans UIState : code, label, `can_switch`, transitions (**REL OBSERV**).
- `POST .../set-posture/` + `PostureSelector.vue` / `InitialPostureSelector.vue` (**REL OBSERV** — C15/C16).
- `learner_display_profile` : youth / adult / professional (**REL OBSERV** — B16-L1).
- `VITE_LEARNER_UI_V2=true` par défaut — layout v2 (**REL OBSERV** — `frontendConfig.js`).
- Profils conversationnels **globaux** admin + résolution runtime (**REL OBSERV** — matrice V6, `test_learner_conversation_global_profile.py`).

### Changé depuis 22/06

- **Majeur :** posture interactive (était lecture seule en A2).
- Admin profils globaux `/admin/conversation/learner/profiles` (absent A2).

### Partiel

- Matrice transitions SW-xx spec 2.0 : **CIBLE**.
- Starter prompts admin : **REL OBSERV PARTIEL** (API existe ; UX admin incomplète).

### Runtime non prouvé

- Parcours apprenant sur Encoors avec même build front : **À VÉRIFIER** (CORS local).

**Fichiers historiques :** A2 § apprenant — **partiellement obsolète** ; `cluster4_front_A1_*` — **confirmé**.

---

## Domaine 40–50 — Base connaissances et orchestrateur formateur

### Réel observé

- CRUD `TrainerKnowledgeItem` + actions validate / provisional / reject / edit (**REL OBSERV** — C15 B1).
- Atelier élicitation `/app/trainer/elicitation` (**REL OBSERV** — C15 B2).
- Endpoints élicitation questions/answers, ingest document (**REL OBSERV**).
- `TrainerGroupContextPanel` — contexte groupe sur knowledge/library (**REL OBSERV** — rapport 30/06 D4 corrigé).
- `usage_stats` minimal sur items (**REL OBSERV** ; compteur RAG réel **À VÉRIFIER**).

### Changé depuis 22/06

- Workflow validation enrichi ; panneau contexte formateur ; serializer memberships avec username (INC-03).

### Partiel

- Orchestrateur formateur « script F1–F4 » spec 2.0 : **CIBLE**.
- Lien knowledge validé → conversation apprenant : **À VÉRIFIER**.

### Écart ouvert

- `GET /dashboard/groups/{id}/learners/` → `[]` pour TRAINER malgré memberships (**ÉCART CONFIRMÉ** — INC-02, 30/06).

**Fichiers historiques :** audits formateur 00–04 — **partiellement actualisés** par C15.

---

## Domaine 60 — Orchestrateur tuteur

### Réel observé

- Surfaces prod : `/app/tutor`, groupe, fiche apprenant (**REL OBSERV PARTIEL**).
- Timeline / traces : filtrage sans verbatim apprenant côté tuteur (**REL OBSERV** — E2E L10).
- `TutorLearnerLink` pour visibilité apprenants dashboard (**REL OBSERV**).
- Backend conduct profiles, tutor prompts (**REL OBSERV** local).

### Changé depuis 22/06

- Tests smoke tuteur Playwright ; coordo C14 spec file présent.

### Partiel

- Surface métier tuteur riche spec 2.0 : **CIBLE**.
- Conduct-profiles sur Encoors : **À VÉRIFIER** (absent 12/06).

**Fichiers historiques :** A2 § tuteur — **toujours partiel**.

---

## Domaine 70 — Évaluation, traces, preuves

### Réel observé

- Chaîne readiness → request-evaluation → generate-trace (**REL OBSERV** local — cluster 11).
- `evaluation_trace_pivot_v1` dans generate-trace (**REL OBSERV**).
- CTA évaluation advisory dans UIState (**REL OBSERV** — B16-C2).
- `finalize-evaluation` endpoint (**REL OBSERV** local).
- Policies / evaluation-prompt-profiles API (**REL OBSERV** ; UI admin dédiée **PARTIEL**).

### Changé depuis 22/06

- Renforcement tests CTA ; slot eval dans profil conversationnel global (V6).

### Partiel

- Certification autonome : **interdit** — validation humaine (**CART CONFIRM**).
- EvaluationTrace doctrinale complète : **CIBLE**.

### Runtime non prouvé

- EVAL1 Encoors : **À VÉRIFIER** (oracle sans credentials 18/06).
- E2E synthèse/éval : lots 9 SKIP (**REL OBSERV PARTIEL**).

**Fichiers historiques :** `fiche_trace_exploitable_pivot_v1.md` — **confirmé**.

---

## Domaine 80 — Observabilité

### Réel observé

- Signaux post-conversation `record_session_signal` (**REL OBSERV**).
- Observabilité base tests (`test_observabilite_base.py`) (**REL OBSERV**).
- D9bis : routes internal superadmin (**REL OBSERV** local ; 404 sans auth Encoors probe 18/06).

### Partiel

- Catalogue signaux spec 2.0 : **CIBLE**.
- D9bis UX superadmin : **REL OBSERV PARTIEL**.

**Fichiers historiques :** `note_frontiere_observabilite_base_vs_d9bis.md` — **confirmé**.

---

## Domaine 90 — Confidentialité, partage, multi-tenant, rôles

### Réel observé

- JWT + rôles LEARNER, TUTOR, TRAINER, COORDO, ORGADMIN, SUPERADMIN (**REL OBSERV**).
- `X-Organisation-Id` pour superadmin (**REL OBSERV** — campagne 30/06).
- `ActiveOrganisationBanner` + switcher navbar (**REL OBSERV** — INC-01).
- Tests cross-tenant, tenant campaign 8/8 (**REL OBSERV**).
- Partage session `POST .../share/` (**REL OBSERV** code ; usage prod **À VÉRIFIER**).

### Partiel

- RLS Postgres effectif prod : **À VÉRIFIER**.
- Playwright tenant 11/11 mentionné matrice V6 — **REL OBSERV PARTIEL** (à reconfirmer sur branche courante).

**Fichiers historiques :** doc 10 CORS — **confirmé** pour localhost vs hugo.encoors.com.

---

## Domaine 100 — Exports, Qualiopi lite

### Réel observé

- `apps/exports` ExportRun CSV/JSON (**REL OBSERV**).
- `apps/quality` evidence bundle (**REL OBSERV**).
- Exports trainer evaluation records (**REL OBSERV** — D2-M06 tests).

### Runtime non prouvé

- Parité exports Encoors : **À VÉRIFIER**.

---

## Domaine 110 — Interfaces formateur / tuteur / admin

### Réel observé

| Surface | Statut |
|---------|--------|
| Apprenant prod `/app*` | **REL OBSERV** (C16) |
| Formateur prod `/app/trainer/*` | **REL OBSERV PARTIEL** |
| Tuteur prod `/app/tutor*` | **REL OBSERV PARTIEL** |
| Admin testeur onboarding wizard | **REL OBSERV** (E2E L2–L3, 26/06) |
| Admin conversation (profils, orchestrateurs) | **REL OBSERV PARTIEL** |

### Changé depuis 22/06

- Cluster 15 + 16 = saut de maturité interface apprenant.
- Audits UI admin 26/06 (wizard org, superadmin).

**Fichiers historiques :** `audit_interfaces_reel_vs_cible_*` — **base valide**, compléter avec C15/C16.

---

## Domaine 120 — Intercalaires v1

- **CIBLE** — aucune feature runtime observée (**REL OBSERV** négatif — `audit_domaine_120`).

---

## Tableau synthèse — maturité fonctionnelle

| Domaine | Réel | Partiel | À vérifier | Cible dominante |
|---------|------|---------|------------|-----------------|
| 10 Runtime/UIState | ● | ○ double UIState | Encoors | v17, verrous |
| 20 Mémoire | ● | ○ scope API | Encoors | injection LLM |
| 30 RAG | ● lexical | ○ lien trainer | compteur usage | vectoriel |
| 31 Apprenant | ● | ○ admin prompts | Encoors UX | SW-xx |
| 40–50 Formateur | ● | ○ orchestrateur | ACL learners | F1–F4 |
| 60 Tuteur | ○ | ● | conduct Encoors | surface riche |
| 70 Éval/traces | ● | ○ E2E bout-en-bout | Encoors EVAL1 | EvaluationTrace |
| 80 Observabilité | ● base | ○ D9bis | prod | catalogue |
| 90 Multi-tenant | ● | ○ RLS prod | Encoors | — |
| 100 Exports | ● | — | Encoors | — |
| 110 Interfaces | ● apprenant | ○ tuteur/formateur | — | — |
| 120 Intercalaires | — | — | — | ● |

---

*Suite : **R3** (pipelines techniques) ou **R4** (contrats JSON).*
