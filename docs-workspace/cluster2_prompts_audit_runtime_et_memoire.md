# Cluster 2 — Prompts d'audit runtime, mémoire, exports et multi-rôles

**Workspace :** `/Users/machin/Desktop/Zone de travail Hugo`  
**Version :** 3 (post-tests cluster 15 — 2026-06-18)  
**V2 :** 2026-06-16  
**Usage :** copier un bloc **Prompt** dans Cursor ; remplir les entrées `[…]` ; exiger la **sortie structurée** indiquée.

**Références communes :**
- [DOCS] `00_HIERARCHIE_DOCUMENTAIRE.md`, `DOC_METHODO_REFERENCE_CONVERGENCE_HUGO_REVISE.md`, `plan_documentation_cto_convergence_hugo.md`, `synthese_globale_ecarts_par_domaine.md`, `cluster2_matrice_runtime_vs_cible.md` **(V4)**
- [TESTS] `rapport_mise_a_jour_doc_post_tests_2026-06-18.md`, `test_cluster15_interfaces_*.py`, `protocole_tests_interfaces_apprenant_formateur_v1.md`
- [CODE] `hugo_back/`, `hugo-hugolucia/frontend_1.8/`
- [PERSONAE] `Bibliothèque canonique de personae Hugo 2.0.md`

---

## 0. En-tête générique (préfixer chaque audit)

```markdown
## Entrées
- [ENVIRONMENT] : local | docker | Encoors (si Encoors → section A_VERIFIER obligatoire)
- [SESSION_ID] : uuid ou « à créer »
- [ROLE] : LEARNER | TUTOR | TRAINER | ORGADMIN | SUPERADMIN | tester
- [COMMIT] : optionnel

## Règles
- Backend-first : hugo_back + pytest avant front.
- Séparer : Réel confirmé | Cible 2.0 | Écarts | A_VERIFIER | Hypothèses.
- Spec ≠ preuve d'implémentation.
- Surfaces : métier (/app) vs technique (tester, superadmin debug).
- Ne pas exposer P0/TurnState/verbatim comme produit apprenant.
- Distinguer **cœur de convergence** (Vagues 1–3 plan CTO : domaines 10/20/31/70/90/100/110/40/50/60) et **couronne optionnelle** (D9bis, intercalaires v1, RAG vectoriel, observabilité avancée) — ne pas promouvoir en IMPLÉMENTÉ ce qui est CIBLE / A_VÉRIFIER dans `synthese_globale_ecarts_par_domaine.md`.

## Sortie obligatoire
1. Sources mobilisées (fichiers, endpoints, docs)
2. Réel confirmé (faits prouvés)
3. Cible 2.0 (rappel doctrinal minimal)
4. Écarts (statut : ALIGNE | PARTIEL | ABSENT_NOUVEAU_CONTRAT | AMBIGU)
5. A_VERIFIER
6. Actions DOC / CODE / OPS (référencer D2-Mxx si applicable)
```

---

## A. Audit runtime P0 / décision locale

### A.1 — Cartographie P0 et TurnState

**Entrées :** [ENVIRONMENT], [DOCS] `02_ETAT_MOTEUR_REEL.md`, [FILE] `p0_classifier.py`, `turn_state_analyzer.py`, `hugo_orchestrator.py`, `domain/schemas.py`

**Prompt :**
```markdown
[Coller en-tête §0]

Objectif : décrire le pipeline P0 réel par tour.

Tâches :
1. Séquence : heuristique → classifieur → TurnState (legacy et v17 si flag actif).
2. Tableau : champ TurnState → producteur → consommateur (décision, progress, prompt, UI).
3. Valeur [ENVIRONMENT] de HUGO_P0_V17_ENABLED et impact sur le chemin.
4. Lister surfaces techniques (LearnerDetailView) vs interdites prod.
5. Comparer à cible 2.0 (charge cognitive, risque interaction, clarté épisode).

Invariants à vérifier :
- TurnState absent de GET /ui-state/
- TurnState présent dans traces testeur si p0_debug

Sortie : + tableau champs × preuve.
```

### A.2 — DecisionContract / ConversationDecision

**Entrées :** [FILE] `decision_engine.py`, `decision_engine_v17.py`, `schemas.py`

**Prompt :**
```markdown
[Coller en-tête §0]

Objectif : auditer le contrat de décision réel vs DecisionContract doctrinal.

Tâches :
1. Schéma ConversationDecision (champs, metadata, pedagogical_move).
2. Branches par conversation_profile (diagnostic, reflective_afest, knowledge_review).
3. forbidden_moves : appliqué en code ou seulement dans prompt ?
4. Chaîne décision → teaching_plan.rag_mode → select_rag_chunks.

Sortie : + 3 exemples message → move attendu (référence tests si existants).
```

---

## B. Audit progression / ConversationProgress

**Entrées :** [FILE] `conversation_progress_calculator.py`, `conversation_progress.py`, [ENDPOINT] `GET /progress/`, `GET /ui-state/`

**Prompt :**
```markdown
[Coller en-tête §0]

Objectif : clarifier les **deux** objets ConversationProgress et leur usage.

Tâches :
1. Contrat branches/maturité (session.conversation_progress JSON).
2. Objet engagement legacy (build_conversation_progress).
3. Critères GREEN par posture (tableau).
4. Lien synthesis_eligible / evaluation_eligible → cta_*.
5. reason_codes : lesquels atteignent le front (via blocking_reasons seulement).

Sortie : diagramme texte tour N → progress N → ui-state N.
```

---

## C. Audit UIState / surfaces produit

**Entrées :** [ENDPOINT] `GET /hugo/sessions/{id}/ui-state/`, [FILE] `ui_state_builder.py`, `cta_ui_state.py`, `engagementUiModel.js`, `ProdLearnerWorkspace.vue`

**Prompt :**
```markdown
[Coller en-tête §0]

Objectif : contrat UIState **prod** vs engagement.

Tâches :
1. Liste exhaustive champs build_contract_ui_state + consommation front /app.
2. Champs build_ui_state **non** présents dans contrat prod.
3. cta_evaluation / cta_synthesis : statuts, blocking_reasons, endpoints.
4. gamification_profile A/B/C : effet réel (cosmétique) vs profil affichage 2.0 [CIBLE].
5. Absence conversation_mode : écart vs specs interface 2.0.

Invariants :
- Pas de P0, TurnState, reason_codes bruts dans ui-state prod
- Front ne recalcule pas éligibilité CTA

Sortie : tableau champ UIState × source backend × lu par front × niveau vérité.
```

### C.1 — **Profils d'affichage apprenant vs UIState canonique** (nouveau)

**Entrées :** [DOCS] `specs interface 2.0.md` § Profils d'affichage, [FILE] `frontendConfig.js`, `engagementUiModel.js`, [PERSONAE] A1, A2, A3

**Prompt :**
```markdown
[Coller en-tête §0]

Objectif : séparer **profil d'affichage** (3 UX, 1 UIState) de **gamification_profile** (A/B/C cosmétique).

Tâches :
1. Citer cible 2.0 : jeune 16–20, reconversion 20–35, ingénieur/supérieur — exigences UX.
2. Décrire réel : une seule grammaire `/app` + variations A/B/C (barres, badges, quête).
3. Chercher learner_display_profile ou équivalent dans code → attendu ABSENT.
4. Chercher API choix profil par formateur/ORGADMIN → attendu ABSENT.
5. Proposer contrat minimal :
   - enum learner_display_profile : youth | adult | professional
   - même UIState ; rendu front différent
   - skins cosmétiques optionnels au-dessus

Garde-fous :
- Profil affichage ≠ mode pédagogique ≠ gamification_profile
- Pas de recalcul progression/posture côté front

Sortie :
- Tableau cible × réel × statut
- Actions D2-M08, ecarts-110 § à créer
```

---

## D. Audit mémoire intra-conversation

**Entrées :** [DOCS] `ecarts — 20_memoire_gouvernee.md`, `20_memoire_gouvernee_note_lot_courant_memoire_intra_conversation.md`, [FILE] `session_memory.py`, [ENDPOINT] `GET .../memory-summary/`

**Prompt :**
```markdown
[Coller en-tête §0]

Objectif : mémoire **intra-conversation** uniquement (pas inter-sessions active).

Tâches :
1. SessionMemoryContract : champs, memory_scope, producteur, fréquence mise à jour.
2. GET memory-summary : structure {session_memory, theme_memories} — rôles distincts.
3. Injection orchestrateur : build_session_memory appelé où ? Injecté dans prompt ? (grep)
4. Consommation front prod : ui-state vs memory-summary.
5. LearnerThemeMemory : stockage vs injection tour.

Interdits : verbatim comme mémoire ; theme_memories comme « mémoire du fil ».

Sortie : JSON exemple memory-summary annoté (intra vs préparé inter-sessions).
```

---

## E. Audit RAG / référentiel documentaire

**Entrées :** [DOCS] `ecarts — 30_referentiel_documentaire_rag.md`, [FILE] `rag_support.py`, `library/`

**Prompt :**
```markdown
[Coller en-tête §0]

Objectif : RAG lexical, gouverné, question-driven — pas vectoriel sauf preuve.

Tâches :
1. should_use_rag × conversation_profile.
2. select_rag_chunks : scoring, filtres GroupDocument ACTIVE.
3. Injection prompt vs rag_citations message vs supporting_documents engagement.
4. pgvector/embedding : présent modèle, absent runtime.

Sortie : scénario API [SESSION_ID] avec document indexé → oracle rag_citations non vide ou explicitement vide avec raison.
```

---

## F. Audit évaluation / traces / preuves

**Entrées :** [DOCS] `ecarts — 70_evaluation_traces_preuves.md`, [ENDPOINT] evaluation-*, generate-trace, share

**Prompt :**
```markdown
[Coller en-tête §0]

Objectif : branche terminale évaluation (≠ posture).

Tâches :
1. Ficher endpoints : readiness, request, finalize, generate-trace, share.
2. Flux avec can_request_evaluation et blocking_reasons.
3. Mapping EvaluationTrace ↔ LearnerEvaluationRecord ↔ Trace ↔ TraceCriterionAssessment (tableau).
4. Richesse payload generate-trace local.
5. Front : CTA depuis cta_* uniquement.

Sortie : séquence diagramme + tableau mapping §4.2 matrice cluster2.
```

---

## G. Audit exports métier / bundles / EvidenceBundleView

**Entrées :** [DOCS] `ecarts — 100_exports_preuves_qualiopi_lite.md`, [FILE] `quality/views.py`, `exports/views.py`, [ROLE] ORGADMIN

**Prompt :**
```markdown
[Coller en-tête §0]

Objectif : exports **métier** et bundles (pas debug superadmin).

Tâches :
1. EvidenceBundleView : méthode, contenu ZIP, filtres tenant, rôle requis.
2. ExportRun apps/exports : CSV/JSON, ExportRun model.
3. Trainer evaluation export.
4. Taxonomie : export métier vs bundle vs technique (matrice cluster2 §0).
5. Bundle non certifiant : mentions doc.

Sortie : liste fichiers ZIP attendus × observés ; écarts richesse A_VERIFIER.
```

---

## H. Audit artefacts analytiques LLM (hors UX métier)

### H.1 — **ConversationTurnLLMAnalysis / ConversationLLMAnalysis** (nouveau)

**Entrées :** [DOCS] `specs interface 2.0.md` §2.3, `ecarts — 100` D9bis, [ROLE] SUPERADMIN

**Prompt :**
```markdown
[Coller en-tête §0]

Objectif : vérifier statut **CIBLE** des artefacts analytiques LLM.

Tâches :
1. grep codebase : ConversationTurnLLMAnalysis, ConversationLLMAnalysis → attendu 0 modèle dédié.
2. Distinguer de llm_response_payload / tracing (CREDIBLE, ≠ objet doctrinal).
3. Vérifier absence export-md endpoint.
4. Rappeler garde-fous : jamais UIState, jamais apprenant/tuteur/formateur/ORGADMIN.
5. Proposer squelette sous-contrat D9bis (champs, endpoint, mention « non montrable produit »).

Sortie :
- Statut : ABSENT_NOUVEAU_CONTRAT confirmé ou contre-preuve
- Esquisse JSON ConversationTurnLLMAnalysis cible
```

---

## I. Audit rôles / confidentialité / multi-tenant

### I.1 — **Matrice rôle × visibilité × partage × confidentialité** (nouveau)

**Entrées :** [DOCS] `ecarts — 90_confidentialite_partage_multitenant_roles.md`, [ROLE] un ou plusieurs, [PERSONAE] G3, B1, A1

**Prompt :**
```markdown
[Coller en-tête §0]

Objectif : matrice exploitable rôle × données × actions.

Rôles à couvrir : [ROLE] ou liste complète LEARNER, TUTOR, TRAINER, ORGADMIN, SUPERADMIN, COORDO [CIBLE]

Pour chaque rôle, tableau :
| Donnée / action | Voit | Peut | Ne voit pas (doctrine) | Preuve locale | A_VERIFIER prod |
- UIState, messages propres, messages autrui
- Verbatim non partagé
- P0 / TurnState / turn-review
- memory-summary
- Trace, Evidence, LearnerEvaluationRecord
- EvidenceBundle ZIP
- export-md / LLM analysis [CIBLE]
- Choix profil affichage [CIBLE]

Tests négatifs :
- IDOR session autre organisation
- Tuteur sans share_verbatim

Sortie : matrice complète + écarts → alimenter ecarts-90 (D2-M07).
```

---

## J. Audit interfaces tuteur / formateur / ORGADMIN / superadmin

**Entrées :** [DOCS] `ecarts — 110_interfaces_formateur_tuteur.md`, [FILE] vues front tester vs prod

**Prompt :**
```markdown
[Coller en-tête §0]

Objectif : surfaces par rôle — ne pas confondre tester et prod.

Tâches :
1. Cartographie routes front : /app vs /dashboard vs admin.
2. APIs consommées par TutorLearnerView, trainer views, GroupAdminDetailView.
3. Posture : visible tuteur (timeline) vs absente apprenant prod.
4. Frontière ORGADMIN (users, bundle, conduct) vs superadmin (debug, D9bis).
5. Parcours persona [PERSONAE B1 ou C1] : étapes manquantes A_VERIFIER.

Sortie : checklist écarts-110 par surface.
```

---

## K. Maintenance matrice cluster 2

**Entrées :** [DOCS] `cluster2_matrice_runtime_vs_cible.md`, diff git depuis [COMMIT]

**Prompt :**
```markdown
[Coller en-tête §0]

Objectif : mettre à jour la matrice après changements code/doc.

1. Relire diff hugo_back / frontend_1.8 / docs-workspace ecarts.
2. Promouvoir niveau vérité seulement avec preuve test ou audit.
3. Mettre à jour §12 Manques résiduels et §13 Cluster 3 si besoin.
4. Lister lignes modifiées avec ancien → nouveau statut.

Sortie : patch markdown listant changements.
```

---

## L. Checklist OPS post-audit

```markdown
- [ ] pytest domaine concerné (hugo_back/apps/hugo/tests/)
- [ ] GET /ui-state/ — pas de P0
- [ ] GET /memory-summary/ — memory_scope, pas verbatim brut
- [ ] POST set-posture — persistance
- [ ] CTA éval : 400 si non éligible
- [ ] Evidence bundle : isolation organisation_id
- [ ] Si [ENVIRONMENT]=Encoors : section entière A_VERIFIER
```

---

## M. Index templates source

| Section | Source d'origine | Domaine |
|---------|------------------|---------|
| D | `20_cursorops_templates.md`, `template_prompt_audit_memoire_intra_conversation.md` | 20 |
| E | `30_cursorops_templates.md` | 30 |
| F | `70_cursorops_templates.md` | 70 |
| G, H | ecarts-100, specs interface Bloc 2 | 100 |
| I | ecarts-90, plan_documentation § protocole test | 90 |
| J | ecarts-110 | 110 |

**Fin — cluster 2 prompts V2.**
