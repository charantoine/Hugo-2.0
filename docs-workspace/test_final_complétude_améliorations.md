# Rapport final — complétude tests convergence Hugo 2.0

**Date d’exécution :** 2026-06-18  
**Environnement :** local (`hugo_back` + `hugo-hugolucia/frontend_1.8`)  
**Méthode :** README §7 → `cluster16_protocole_tests_interface_apprenant_v1.md` (patron) → `plan_tests_global_hugo.md` (inventaire) → `cluster2_oracles_test_par_persona.md` (oracles)  
**Contrainte campagne :** aucune modification du code applicatif — exécution et analyse uniquement.

**Briefing CTO :** [`briefing_cto_convergence_hugo_2_0_tests.docx`](briefing_cto_convergence_hugo_2_0_tests.docx)

**Archives campagnes 2026-06 :** synthèse consolidée 18/06 + 20/06 → [`tests/archives/tests_hugo_2_0_2026-06-18_20.md`](tests/archives/tests_hugo_2_0_2026-06-18_20.md) (ce rapport reste la source détaillée pour la campagne du 18/06).

---

## 0. Synthèse exécutive

| Campagne | Résultat | Durée |
|----------|----------|-------|
| Backend convergence (noyau + clusters 15/16 + qualité) | **168 PASS / 0 FAIL** | ~2 min 35 s |
| Playwright complet (7 specs, 20 tests) | **19 PASS / 1 FAIL / 0 SKIP** | ~33 s |
| Dont cluster 16 apprenant (10 tests) | **10 PASS** | ~13 s |

**Verdict global local :** le **noyau convergence 2.0 apprenant + garde-fous backend** est **solidement prouvé** par pytest et Playwright C16. Un **échec Playwright formateur** est un **bug de test** (libellé titre obsolète), pas un bug produit. **Encoors/prod, RLS, qualité LLM multi-tours et intercalaires** restent **A_VÉRIFIER** ou **CIBLE**.

---

## 1. Protocole de test complet — conception

### 1.1 Chaîne documentaire (patron appliqué)

```
README.md §7 (méthode campagne)
    ↓
cluster16_protocole_tests_interface_apprenant_v1.md (structure B16-* / U16-* / S16-*)
    ↓
plan_tests_global_hugo.md (inventaire domaines × pytest × Playwright × persona)
    ↓
cluster2_oracles_test_par_persona.md (oracles INV, A1–A3, B1, C1, D1)
    ↓
Exécution + rapport (ce document)
```

### 1.2 Périmètre fonctionnel testé

Aligné sur les **13 domaines** de la matrice V5 et les capacités **qualité conversationnelle apprenant** :

| Bloc | Fonctions / contrats | Backend | Front | Communication B↔F |
|------|----------------------|---------|-------|-------------------|
| **Runtime / UIState** | scene, progression, maturity, CTA, conversation_mode, dispersion | cluster 3/4/16, CTA, posture | U16-S1/S4, A1-01 | ui-state → engagementUiModel |
| **Posture / mode** | set-posture, transitions, switch_locked_reason | B16-P*, cluster 15 | U16-S1, PostureSelector | POST → refresh UIState |
| **Mémoire intra** | SessionMemoryContract, memory-summary | B16-M*, session_memory tests | U16-S3, LearnerMemoryPanel | GET memory-summary (parallèle UIState) |
| **CTA synthèse/éval** | eligible, blocked_*, advisory | B16-C*, request_evaluation_guard | U16-S2 (partiel) | cta_* → HugoProgressPanel |
| **Profils affichage** | learner_display_profile × 3 | B16-L1, cluster 4/15 | U16-P1/P2 | ui-state.learner_display_profile → CSS |
| **P0 / phases / décision** | classify, phase_decider, progression | p0_classifier, phase_* | indirect (via UIState) | orchestrateur → progress → UIState |
| **RAG lexical** | select_rag_chunks, citations | rag_support_tracing | A1-09 **GAP** UI | messages + rag_citations |
| **Observabilité** | quality signals, analytics_state | observabilite_base | non exposé apprenant (doctrine) | — |
| **Confidentialité** | IDOR, verbatim, rôles | d2_m07, cluster 3, preprod | A1-03, tutor smokes | API permissions |
| **Encadrants** | trainer knowledge, tutor timeline | cluster 15 formateur, vague5 | smokes (1 fail test) | REST trainer/* |
| **Exports / traces** | pivot eval, evidence bundle | d2_m06, evaluation_trace | orgadmin smoke | exports API |

### 1.3 Matrices de configuration (qualité conversationnelle)

Le protocole exige de tester **plusieurs configurations** pour la relation Hugo–apprenant :

| Dimension | Valeurs testées (auto) | Valeurs non couvertes E2E |
|-----------|------------------------|---------------------------|
| **Profil affichage** | youth, adult, professional | — |
| **Posture** | diagnostic, reflective_afest, knowledge_review (API) | Bascule UI séance avancée (manuel S16-A2) |
| **Maturité** | red, orange, green (API/fixtures) | Parcours LLM réel jusqu’à GREEN |
| **CTA évaluation** | eligible, blocked_*, advisory (API) | Rendu advisory explicite Playwright (U16-S2b) |
| **Mémoire** | session avec messages + turn_state interne | Injection prompt mémoire (CIBLE) |
| **Dispersion** | dispersion_risk=true (API B16-S1) | Alerte UI avec fil multi-branches réel |
| **Gamification** | profils A/B/C via UIState | — |

### 1.4 Commandes exécutées

**Prérequis fixtures :**

```bash
cd hugo_back && python manage.py bootstrap_smoke_playwright
```

**Backend — campagne convergence (168 tests) :**

```bash
cd hugo_back && python -m pytest \
  apps/hugo/tests/test_cluster3_oracles.py \
  apps/hugo/tests/test_cluster4_surface_contracts.py \
  apps/hugo/tests/test_cluster15_interfaces_apprenant.py \
  apps/hugo/tests/test_cluster15_interfaces_formateur.py \
  apps/hugo/tests/test_cluster16_interface_apprenant_backend.py \
  apps/hugo/tests/test_session_memory_contract.py \
  apps/hugo/tests/test_memory_summary_smoke.py \
  apps/hugo/tests/test_cta_synthesis_contract.py \
  apps/hugo/tests/test_cta_evaluation_contract.py \
  apps/hugo/tests/test_request_evaluation_guard.py \
  apps/hugo/tests/test_posture_modes.py \
  apps/hugo/tests/test_preprod_garde_fou.py \
  apps/hugo/tests/test_d2_m07_confidentiality_oracles.py \
  apps/hugo/tests/test_rag_support_tracing.py \
  apps/hugo/tests/test_observabilite_base.py \
  apps/hugo/tests/test_evaluation_trace_minimal.py \
  apps/hugo/tests/test_encadrants_role_guards.py \
  apps/hugo/tests/test_vague5_e2e_scenarios.py \
  apps/hugo/tests/test_d2_m06_d2_m11_exports_and_analytics.py \
  apps/hugo/tests/test_phase_progression.py \
  apps/hugo/tests/test_phase_decider.py \
  apps/hugo/tests/test_quality_signals.py \
  apps/hugo/tests/test_p0_classifier.py \
  apps/hugo/tests/test_trainer_knowledge.py \
  apps/hugo/tests/test_analytics_absence_ui_exports.py \
  apps/hugo/tests/test_d9bis_analytics_llm.py \
  -v --tb=line
```

**Front — Playwright complet :**

```bash
cd hugo-hugolucia/frontend_1.8 && npm run test:smoke
```

**Front — cluster 16 seul (revalidation) :**

```bash
npm run test:smoke -- tests_playwright/e2e/cluster16_learner_interface.spec.ts
```

---

## 2. Résultats détaillés — backend (168 PASS)

### 2.1 Par lot

| Lot | Fichier(s) | Tests | Statut | Domaines |
|-----|------------|-------|--------|----------|
| Oracles prioritaires | `test_cluster3_oracles.py` | 8 | PASS | 10, 70, 90 |
| Surface UIState | `test_cluster4_surface_contracts.py` | 9 | PASS | 10, 31, 110 |
| Interfaces C15 apprenant | `test_cluster15_interfaces_apprenant.py` | 13 | PASS | 10, 20, 31, 70 |
| Interfaces C15 formateur | `test_cluster15_interfaces_formateur.py` | 8 | PASS | 40, 110 |
| Interface C16 apprenant | `test_cluster16_interface_apprenant_backend.py` | 15 | PASS | 10, 20, 31, 70 |
| Mémoire | `test_session_memory_contract.py`, smoke | 6 | PASS | 20 |
| CTA | synthesis + evaluation + guard | 5 | PASS | 10, 70 |
| Posture | `test_posture_modes.py` | 6 | PASS | 10, 31 |
| Garde-fou preprod | `test_preprod_garde_fou.py` | 4 | PASS | 20, 30, 90, 100 |
| Confidentialité D2-M07 | `test_d2_m07_*.py` | 10 | PASS | 90 |
| RAG | `test_rag_support_tracing.py` | 9 | PASS | 30 |
| Observabilité | `test_observabilite_base.py` | 4 | PASS | 80 |
| Traces / pivot | `test_evaluation_trace_minimal.py` | 3 | PASS | 70, 100 |
| Encadrants guards | `test_encadrants_role_guards.py` | 9 | PASS | 110, 90 |
| Vague 5 E2E API | `test_vague5_e2e_scenarios.py` | 8 | PASS | 60, 40, 100, 70 |
| Exports D2-M06/M11 | `test_d2_m06_d2_m11_*.py` | 14 | PASS | 100, 80 |
| Phases / P0 / qualité | phase_*, p0_classifier, quality_signals | 24 | PASS | 10, 80 |
| Trainer API | `test_trainer_knowledge.py` | 3 | PASS | 40 |
| Analytics absence | `test_analytics_absence_*`, d9bis | 11 | PASS | 80, 100 |

### 2.2 Oracles transverses — statut post-campagne

| Oracle | Statut campagne | Preuve |
|--------|-----------------|--------|
| INV-01 Pas P0 UIState | **SUCCÈS** | cluster 3, d2_m07, cluster 16 B16-P1 |
| INV-02 Verbatim tiers | **SUCCÈS** | B1-01 pytest + vague5 T1 |
| INV-03 CTA backend-driven | **SUCCÈS** | CTA contracts + B16-C2 advisory |
| INV-06 memory-summary | **SUCCÈS** | B16-M1/M2, A1-05 |
| INV-07 conversation_mode | **SUCCÈS** | cluster 4, B16-P |
| INV-08 profil ≠ gamification | **SUCCÈS** | cluster 4 |
| A1-08 Posture UI | **SUCCÈS** Playwright | U16-S1 |
| A1-09 RAG badge Appui | **GAP** | pas de test UI |
| A1-10 Diagnostic ≤2 questions | **CREDIBLE** | doc/pytest partiel, pas E2E LLM |
| DSP-05 IFT-042 choix profil | **CIBLE** | pas de test |

---

## 3. Résultats détaillés — front Playwright (19/20 PASS)

### 3.1 Inventaire specs

| Fichier | Tests | PASS | FAIL | Persona / domaine |
|---------|-------|------|------|-------------------|
| `e2e/cluster16_learner_interface.spec.ts` | 10 | 10 | 0 | A1/A2/A3 — C16 |
| `e2e/learner_a1.spec.ts` | 3 | 3 | 0 | A1 confidentialité / P0 DOM |
| `e2e/tutor_b1.spec.ts` | 2 | 2 | 0 | B1 tuteur |
| `e2e/coordo_c14.spec.ts` | 1 | 1 | 0 | COORDO |
| `test_smoke_tutor.spec.ts` | 1 | 1 | 0 | B1 smoke |
| `test_smoke_orgadmin_exports.spec.ts` | 2 | 2 | 0 | D1 |
| `test_smoke_trainer.spec.ts` | 1 | 0 | **1** | C1 formateur |

### 3.2 Échec unique — analyse

**Test :** `SMOKE_TRAINER › trainer sees knowledge list and can validate item`

| Critère | Constat |
|---------|---------|
| Type | **Bug de test** (sélecteur obsolète) |
| Attendu par le test | `heading "Espace formateur"` |
| Réel observé (snapshot Playwright) | `heading "Orchestrateur de connaissance" [level=1]` |
| Données | Item « Smoke knowledge item for Playwright » **visible** |
| API backend | **OK** — cluster 15 formateur 8/8 PASS |
| Impact produit | **Aucun** — page formateur fonctionnelle |
| Correction proposée (sans appliquer) | Remplacer le sélecteur par `getByRole('heading', { name: 'Orchestrateur de connaissance' })` ; adapter scénario validation (item déjà validé → bouton « Rejeter » seul) |

### 3.3 Lacunes Playwright (non échecs)

| ID | Lacune | Risque | Priorité |
|----|--------|--------|----------|
| U16-S2b | CTA advisory explicite (bouton + helper) | Moyen | P1 |
| B1-06 / A1-09 | Badge RAG « Appui » | Faible | P2 |
| S16-A1→A5 | Scénarios manuels persona | Moyen | P1 |
| Flux message apprenant | Envoi message + refresh UIState | Élevé pour qualité conv. | P1 |
| Streaming assistant | Placeholder / chunk réel | Moyen | P2 |

---

## 4. Communication backend ↔ front — points vérifiés

| Flux | Mécanisme | Preuve backend | Preuve front | Écart |
|------|-----------|----------------|--------------|-------|
| État produit tour | `GET /ui-state/` | 168 tests API | U16-S1/S4 | Double builder UIState doc (10) — pas de fail test |
| Mémoire visible | `GET /memory-summary/` | B16-M* | U16-S3 | Endpoint séparé (pas dans UIState) — conforme spec |
| Posture | `POST /set-posture/` | B16-P2/P3 | U16-S1 | Sync progress OK (C15 fix) |
| CTA action | `POST request-synthesis/evaluation` | guards + vague5 EVAL1 | U16-S2 permissif | Pas de clic E2E synthèse/éval |
| Profils | `learner_display_profile` UIState | B16-L1 | U16-P2 | — |
| Auth | JWT localStorage | guards pytest | login helper | — |
| Proxy dev | Vite `/api` | — | playwright.config | Encoors **A_VÉRIFIER** |

---

## 5. Lacunes à combler — matrice complétude

### 5.1 Par domaine (post-campagne)

| Domaine | Complétude test auto | Lacune principale | Statut vérité |
|---------|---------------------|-------------------|--------------|
| **10** Runtime/UIState | **Élevée** | v17 prod ; double stack doc | PARTIEL+ |
| **20** Mémoire | **Élevée API** ; **moyenne UI** | injection prompt ; UIState mémoire | PARTIEL+ |
| **30** RAG | **Moyenne** backend | badge UI ; vectoriel | PARTIEL |
| **31** Front apprenant | **Élevée** C16 | SW-xx ; verrou phase/tours | PARTIEL+ |
| **40–50** Formateur | **Élevée** API ; **faible** E2E | smoke trainer test bug | PARTIEL+ |
| **60** Tuteur | **Moyenne** | parcours UI complet | PARTIEL |
| **70** Évaluation | **Élevée** API | Playwright advisory | PARTIEL+ |
| **80** Observabilité | **Moyenne** backend | catalogue ; dashboards | PARTIEL |
| **90** Confidentialité | **Élevée** local | RLS prod | A_VÉRIFIER |
| **100** Exports | **Élevée** local | Encoors | A_VÉRIFIER |
| **110** Interfaces | **Élevée** apprenant ; **moyenne** encadrants | IFT-042 | PARTIEL+ |
| **120** Intercalaires | **Nulle** | tout | CIBLE |

### 5.2 Qualité conversationnelle Hugo–apprenant — ce qui manque

| Capacité spec 2.0 | Testé comment | Manque |
|-------------------|---------------|--------|
| Régulation P0 par tour | Unitaire p0_classifier, phase_decider | Parcours 5–10 tours LLM |
| Posture influence copy | prompt_renderer unitaire | E2E changement posture visible |
| Maturité RED→GREEN | Fixtures API | Progression naturelle conversation |
| CTA « déconseillé mais possible » | B16-C2 API | Playwright U16-S2b |
| Mémoire enrichit fil (backend) | build_session_memory | Non injectée prompt — **CIBLE lot** |
| Dispersion multi-branches | API flag | UX avec vrais fils parallèles |
| RAG « Appui : {doc} » | Pipeline pytest | Badge front |
| Intercalaires pédagogiques | — | Domaine 120 CIBLE |
| ≤2 questions diagnostic (A1-10) | CREDIBLE doc | Campagne LLM mesurée |

---

## 6. Méthode pour combler les lacunes

### 6.1 Protocole campagne « complétude 2.1 » (proposé)

1. **Corriger tests sans toucher produit** (1 jour)
   - smoke trainer titre
   - U16-S2 : exiger visibilité boutons CTA quand fixtures orange/green
   - Ajouter U16-S2b fixture advisory

2. **Campagne manuelle guidée** (0,5 jour)
   - Exécuter S16-A1→A5 + check-lists C15 §4
   - Grille : persona × profil × posture × maturité
   - Captures + SESSION_IDS réels dans protocole

3. **Campagne LLM contrôlée** (2–3 jours)
   - 3 scripts conversation (diagnostic flou / AFEST riche / knowledge_review)
   - Mesurer : nb questions, maturité, CTA, memory-summary après N tours
   - Oracle A1-10 : compter questions assistant tour 1

4. **Staging + Encoors** (1–2 jours ops)
   - `run_encoors_preprod_oracle.sh` avec credentials
   - Diff JSON local vs prod
   - `audit_rls_prod_template.sql` sur préprod

5. **CI consolidée**
   - Job 1 : pytest 168 tests
   - Job 2 : bootstrap + Playwright 20 tests
   - Job 3 (nightly) : Encoors oracle optionnel

### 6.2 Fichiers de tests à créer (proposition, non écrits)

| Fichier | Contenu |
|---------|---------|
| `test_final_convergence_oracles.py` | Meta-suite regroupant imports cluster 3/4/15/16 + garde-fous |
| `e2e/cluster16_learner_advisory.spec.ts` | U16-S2b CTA advisory |
| `e2e/learner_conversation_turn.spec.ts` | 1 tour message → UIState refresh |
| `protocole_tests_qualite_conversationnelle_v1.md` | Scripts LLM + grilles A1-10 |

---

## 7. Propositions de correction (non appliquées — code intact)

### 7.1 Tests uniquement

```typescript
// test_smoke_trainer.spec.ts — correction proposée
await expect(page.getByRole('heading', { name: 'Orchestrateur de connaissance' })).toBeVisible()
// Si item déjà validated_trainer : assert Rejeter visible, ou re-seed fixture declared
```

```typescript
// cluster16 — U16-S2b proposé
await openLearnerSession(page, cluster16SessionId(fx, 'youth'))
await expect(page.getByRole('button', { name: /Évaluation possible/i })).toBeEnabled()
await expect(page.getByText(/conseillons|conseille/i)).toBeVisible()
```

### 7.2 Produit (si validation CTO)

| ID | Correction | Fichier | Effort |
|----|------------|---------|--------|
| DOC-01 | Aligner titre formateur test ou ajouter `aria-label` stable | Vue trainer | Faible |
| BE-01 | `switch_locked_by_session_phase` explicite | ui_state_builder | Moyen |
| BE-02 | IFT-042 endpoint choix profil groupe | referentials API | Moyen |
| FE-01 | Badge RAG Appui | ProdLearnerWorkspace | Moyen |
| FE-02 | Test id `data-testid` posture/CTA/mémoire | composants C16 | Faible |

### 7.3 Documentation

| Action | Fichier |
|--------|---------|
| Promouvoir statuts post-campagne | `cluster2_oracles_test_par_persona.md` §22 |
| Ajouter campagne final | `plan_tests_global_hugo.md` §9 |
| Protocole qualité conv. | nouveau `protocole_tests_qualite_conversationnelle_v1.md` |

---

## 8. Cartographie oracles ↔ tests exécutés

| Persona | Oracle | Backend | Playwright | Manuel |
|---------|--------|---------|------------|--------|
| A1 | A1-01 scène | indirect UIState | U16-S4 | — |
| A1 | A1-05 mémoire | PASS | U16-S3 | — |
| A1 | A1-08 posture | PASS | U16-S1 | S16-A2 |
| A2 | A2-05 profil adult | PASS | U16-P | S16-A4 |
| A3 | A3-04 profil pro | PASS | U16-P | S16-A5 |
| A3 | A3-01 knowledge_review | API fixtures | — | — |
| B1 | B1-01 verbatim | PASS | tutor smokes | — |
| C1 | C1-01 knowledge | PASS | **FAIL test** | — |
| D1 | D1-01 exports | PASS | orgadmin smoke | — |
| INV | INV-01 à 08 | PASS | partiel | — |

---

## 9. Conclusion

La campagne **final complétude** exécutée le 2026-06-18 démontre que **l’essentiel de la convergence 2.0 côté apprenant** (UIState, posture, mémoire intra, CTA, profils, scène, garde-fous confidentialité) est **couvert par 168 tests backend PASS** et **19/20 tests Playwright PASS**, avec **10/10** sur le périmètre cluster 16.

**Points forts :** doctrine backend-first respectée en test ; communication API↔front validée sur les contrats critiques ; qualité conversationnelle **côté moteur** (P0, phases, signaux) testée unitairement.

**Points faibles :** pas de campagne LLM multi-tours ; Encoors/RLS non exécutés ; un test formateur obsolète ; oracles A1-09, A1-10, S16-* et IFT-042 ouverts.

**Recommandation :** considérer le lot **prêt pour staging contrôlé** après correction du smoke trainer et passage manuel S16 — **pas pour prod directe** sans oracle Encoors.

---

## 10. Addendum 2026-06-20 — profils conversationnels globaux & pipes admin

**Commit de référence :** `c560fa8` — `feat: learner global conversation profiles with legacy fallback`  
**Mini-spec :** [`MINI_SPEC_PROFILS_CONVERSATIONNELS_APPRENANT.md`](MINI_SPEC_PROFILS_CONVERSATIONNELS_APPRENANT.md)  
**Archive consolidée :** [`tests/archives/tests_hugo_2_0_2026-06-18_20.md`](tests/archives/tests_hugo_2_0_2026-06-18_20.md) §2 bis

### 10.1 Ce qui a été livré (réel confirmé)

| Brique | Backend | Admin Super Admin / OrgAdmin | Runtime |
|--------|---------|------------------------------|---------|
| Profil global apprenant | `LearnerConversationGlobalProfile` | `/admin/conversation/learner/profiles` | Résolution session → groupe → org `is_default` |
| 4 sous-blocs | FK TutorPrompt ×3 + conduct ×3 + eval prompt + policy | Éditeur profil + hubs legacy par posture | `_resolve_tutor_prompt`, conduct, évaluation |
| Affectation groupe | `Group.default_learner_conversation_profile` | `/groups-admin/:id` | Priorité groupe |
| Fallback legacy | `default_tutor_prompt`, `TutorPrompt.is_default`, prompts hardcodés | Select legacy masqué si profil global | Chaîne documentée dans résolveurs |
| Gouvernance produit | — | Super Admin + org tenant | Apprenant choisit **mode** ; admin choisit **profil global** |

### 10.2 Campagne tests complémentaire (20/06 PM + audit pipes)

| Campagne | Résultat | Preuve |
|----------|----------|--------|
| `test_learner_conversation_global_profile.py` | **12 PASS** | CRUD, résolution, legacy template, priorité session/groupe |
| Pipeline convo ciblé (profils + eval + posture + tutorprompt + guards) | **26 PASS** | Audit pipes admin ↔ runtime |
| Interface apprenant C16 (backend + cluster15/16) | **32 PASS** | Non-régression runtime apprenant |
| Playwright profils admin | **2 PASS** | `admin_learner_profiles.spec.ts` |
| Playwright pipeline SUPERADMIN → groupe | **2 PASS** | `admin_conversation_pipeline.spec.ts` |
| Playwright tenant personas | **11 PASS** | `tenant_personas.spec.ts` (campagnes 20/06 — **existe et archivée**) |
| Smoke multi-tenant relaxed | **90 PASS, 3 SKIP** | `run_multitenant_smoke.sh` |

### 10.3 Ce qui fonctionne / ce qui reste partiel (pipes conversationnels)

| Statut | Élément |
|--------|---------|
| **OK** | Création / édition / suppression profil global ; affectation groupe ; résolution runtime ; choix mode apprenant ; clôture/éval org via closing view |
| **Legacy actif** | Hubs posture, `/tutor-prompts`, `/conduct-profiles`, `Group.default_tutor_prompt`, override `tutor_prompt_id` à la création session prod |
| **Partiel** | Création depuis legacy (dépend données org) ; policies évaluation **groupe** ; paramètres orchestrateur statiques (lecture seule) |
| **Manquant admin** | Prompts synthèse ; starter prompts ; override session `learner_conversation_profile` (modèle sans REST) |
| **A_VÉRIFIER** | Parité Encoors ; RLS strict CI ; campagne LLM multi-tours |

### 10.4 Backlog doc/code ouvert (pipes)

| Priorité | Item |
|----------|------|
| **P1** | Admin prompts synthèse (Phase 3 — `synthesis_service.py` hardcodé) |
| **P1** | UI policies évaluation par groupe |
| **P2** | Admin starter prompts (`/hugo/starter-prompts/`) |
| **P2** | Paramètres orchestrateur éditables (aujourd’hui read-only front + Python statique) |
| **P2** | Décision produit : exposer ou retirer `session.learner_conversation_profile` |

---

*Rapport généré sans modification du code applicatif (18/06). Addendum 20/06 = doc + re-tests post-livraison profils globaux. Régénérer le briefing CTO : `python docs-workspace/scripts/generate_cto_briefing_docx.py`*
