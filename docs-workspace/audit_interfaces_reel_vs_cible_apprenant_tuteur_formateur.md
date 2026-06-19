# Audit interfaces — réel vs cible 2.0 (apprenant / tuteur / formateur)

> **Date :** 2026-06-18  
> **Méthode :** specs 2.0 = **CIBLE** ; code `frontend_1.8` + `hugo_back` + tests = **RÉEL OBSERVÉ** ; écarts clusters 12/14 = **COURONNE** ou **convergence inachevée**.  
> **Périmètre :** surfaces prod `/app/*` (prioritaire) + mention des surfaces tester `/dashboard` quand elles divergent.

---

## 1. Apprenant

### CIBLE 2.0 (specs interface + canonique + écarts 31)

- **Modes / postures** : trois régimes doctrinaux — diagnostic, réflexif AFEST, savoirs/révision (`knowledge_review`) — visibles et, en début de séance, **modifiables** via un sélecteur borné (endpoint set-posture, refus si maturité avancée).
- **Profils d’affichage** : youth / adult / professional — **même UIState**, rendu UX différencié (densité, tutoiement, icônes).
- **CTA** : synthèse et évaluation **100 % backend-driven** (`cta_synthesis`, `cta_evaluation`) ; variation libellés/aide selon posture (D2-M02).
- **Mémoire visible** : résumé gouverné intra-conversation (pas de verbatim) ; éventuellement objets persistants dérivés.
- **RAG** : badge « Appui » sur citations lexicales ; pas de recherche documentaire autonome ; pas de panneau RAG.

### RÉEL DANS LE CODE

| Élément | Fichier(s) | Comportement observé |
|---------|------------|----------------------|
| Shell session prod | `src/views/ProdLearnerSessionView.vue` → `ProdLearnerWorkspace.vue` | Route `/app/session/:id` ; charge session, messages, **ui-state**, traces/preuves apprenant, streaming messages. |
| UIState | `ProdLearnerWorkspace.vue` L231-239 | `GET /hugo/sessions/{id}/ui-state/` avec `gamification_profile` + `learner_display_profile`. |
| Mode conversationnel (lecture seule) | `ConversationModeBanner.vue` | Affiche `conversation_mode.label` + `switchWarning` si présent ; **aucun contrôle interactif** ; `can_switch` non utilisé côté UI. |
| Postures backend | `ui_state_builder.py` `_build_conversation_mode` | Codes : `diagnostic`, `reflective_afest`, `knowledge_review` ; labels : « Diagnostic », « Réflexif AFEST », « Savoirs / révision ». |
| Set-posture API | `views_sessions.SessionSetPostureView`, `urls.py` L19 | `POST /hugo/sessions/{id}/set-posture/` — **testé pytest** ; **0 appel front** (grep `set-posture` vide dans `frontend_1.8`). |
| Profils d’affichage | `displayProfilePresets.js`, `displayProfileCopy.js`, `engagementUiModel.js` | Presets youth/adult/pro : barre progression, icônes étapes, intro panneau ; copy tutoiement (youth) vs vous (adult/pro). Classe CSS `prod-panel--{profile}` sur `HugoProgressPanel.vue`. |
| Résolution profil | Backend `ui_state_builder.resolve_learner_display_profile` | Cascade org → groupe → défaut `professional` ; configurable côté ORGADMIN (`GroupAdminDetailView.vue`). |
| Progression + CTA | `HugoProgressPanel.vue`, `engagementUiModel.js` | Scène (Raconter/Explorer/Synthétiser), maturité, boutons synthèse/éval depuis `cta_*` ; labels = `ui.button_label` backend (**identiques toutes postures** — `cta_ui_state.py`). |
| RAG Appui | `ProdLearnerWorkspace.vue` L701-711 | Badge par message assistant si `message.rag_citations` ; titre document uniquement — pas de contenu chunk. |
| Traces / synthèse / éval résultats | `ProdLearnerWorkspace.vue` panneau droit | Affiche résultats locaux post `request-synthesis` / `request-evaluation` ; compteurs traces/preuves ; **pas d’appel `memory-summary`**. |
| Partage | `ProdLearnerWorkspace.vue` L831-858 | Checkboxes `share_summary`, `share_evidence`, `share_verbatim` → `PATCH share`. |
| Objets persistants | `engagementUiModel.buildPersistentObjects` | Lit `ui_state.persistent_objects` si flag `VITE_PERSISTENT_OBJECTS_ENABLED` ; **pas de rendu `session_memory`**. |
| Récompenses cosmétiques | `engagementUiModel.buildSymbolicRewards` | Badges/thèmes gamification profil A/B/C — **cosmétique**, pas pédagogique. |
| Surface tester (non prod) | `LearnerDetailView.vue` (~2300 lignes) | Layout tester `/dashboard` : debug P0 optionnel, plus de contrôles ; **hors parcours prod `/app`**. |

**Mapping doctrinal ↔ réel (postures)**

| Spec / doctrine | Code backend | UI prod |
|---------------|--------------|---------|
| Réflexif AFEST | `reflective_afest` | Label « Réflexif AFEST » (banner) |
| Diagnostic | `diagnostic` | Label « Diagnostic » |
| Révision savoirs / « buchage » | `knowledge_review` | Label « Savoirs / révision » |
| Bascule posture | `set-posture` + `can_switch` dans UIState | **Non implémentée** |

### ÉCARTS IMPORTANTS POUR L’UX

1. **Sélecteur de posture G2-02 absent** — spec interface + cluster 12 + écarts 31 : CIBLE lot courant ; API prête, banner lecture seule seulement.
2. **CTA identiques quelle que soit la posture** — D2-M02 ouvert ; backend `cta_ui_state.py` libellés fixes ; front ne varie pas non plus.
3. **Profils adult/pro partiels** — youth le plus différencié ; professional = défaut quasi inchangé ; tests unitaires confirment même CTA labels cross-profile.
4. **Mémoire gouvernée invisible en UI prod** — `memory-summary` et `session_memory` dans UIState backend **non consommés** par le front ; pas de panneau « fil de séance structuré ».
5. **Pas de recherche RAG** — conforme cible ; badge Appui seulement.
6. **Double surface apprenant** — prod (`ProdLearnerWorkspace`) vs tester (`LearnerDetailView`) : risque de confusion doc/demo.

### CLASSIFICATION

| Écart | Classification |
|-------|----------------|
| Sélecteur posture interactif | **Convergence inachevée** (cluster 12 planifié, API OK, jamais branché front) |
| Variation CTA × posture | **Convergence inachevée** (doc D2-M02 ; ni back ni front) |
| Profils UX adult/pro complets | **Mixte** — youth livré ; adult/pro = **convergence inachevée** partielle |
| Panneau memory-summary apprenant | **Couronne 2.0+ assumée** pour UX riche ; **oubli probable** pour affichage minimal `persistent_objects` / résumé fil |
| Matrice SW-xx bascule états | **Couronne 2.0+** (spec interface ouverte) |
| Skins cosmétiques avancés | **Couronne 2.0+** |
| RAG badge Appui | **Livré** |
| CTA backend-driven | **Livré** |
| Partage explicite verbatim | **Livré** |

---

## 2. Tuteur

### CIBLE 2.0 (specs formateur + tuteur 2.0, écarts 60/110)

- **Timeline** apprenant : sessions, progression, blocages, traces partageables.
- **Confidentialité** : pas de verbatim non partagé ; pas de P0/TurnState brut.
- **Signaux qualité** : consommation de `ConversationQualitySignal` / pilotage pour recommandations.
- **Recommandations** : suggérer synthèse, évaluation, bascule posture — **actions UI explicites** côté tuteur (spec ouverte).
- **Validation** traces et objets partageables — humaine, non certifiante.

### RÉEL DANS LE CODE

| Élément | Fichier(s) | Comportement observé |
|---------|------------|----------------------|
| Espace tuteur prod | `ProdTutorHomeView.vue` → groupes → `ProdTutorGroupView.vue` → `ProdTutorLearnerView.vue` | Routes `/app/tutor/*` ; liste groupes/apprenants. |
| Timeline | `TutorLearnerView.vue` | `GET /dashboard/groups/{g}/learners/{l}/timeline/` — sessions (date, preview 1er message), traces (id, validé/non). |
| Verbatim conditionnel | `TutorLearnerView.vue` L171-207 | Messages complets **uniquement si** `share_verbatim` ; sinon preview tronqué. |
| Badges pilotage | `TutorLearnerView.vue` `pilotageBadges()` | Sur messages partagés : profil, objectif, step, %, clôture, aide, boucle, synthèse possible — **champ `message.pilotage`**, pas P0 brut. |
| Validation trace | `TutorLearnerView.vue` L115-127 | `POST /traces/{id}/validate/` — rôles TUTOR/TRAINER/COORDO/admin. |
| Compétences | `TutorLearnerView.vue` L87-100 | `GET /dashboard/groups/{g}/competences/` filtré apprenant — résumé + skills_matrix JSON brut. |
| COORDO | `roleGuards.js` (héritage tuteur) | Accès `/app/tutor` — **pas de UI COORDO dédiée** (cluster 14). |
| Observabilité interne | Backend `/internal/.../observability/` | **Aucune page front** — zéro composant observabilité en prod. |
| Recommandations tuteur | — | **Aucun composant** « suggérer synthèse », « recommander bascule », guide accompagnement. |
| Dashboard cohorte | Backend `cohort_metrics`, `analytics/learners/.../progress` | **Pas de vue prod** ; endpoints existent, non branchés front `/app/tutor`. |
| Surface tester | `TutorLearnerView` aussi via routes `/dashboard` | Breadcrumbs tester vs prod ; même composant timeline. |

### ÉCARTS IMPORTANTS POUR L’UX

1. **Pas de recommandations orchestrées** — spec tuteur 2.0 (mapping signal → action) **non codée** en UI.
2. **Signaux qualité partiels** — badges `pilotage` produit-safe sur timeline verbatim partagé ; pas de catalogue signaux ; pas d’observabilité session en UI.
3. **Progression / blocages** — pas de vue synthétique maturité/branches type UIState tuteur ; competences = JSON brut.
4. **Validation évaluations** — backend `TrainerEvaluationRecordValidationView` existe ; **pas d’UI tuteur prod** pour valider les `LearnerEvaluationRecord`.
5. **Parcours B1 persona** — timeline + validation trace = **smokes OK** ; recommandations = gap.

### CLASSIFICATION

| Écart | Classification |
|-------|----------------|
| Timeline + traces + validation trace | **Livré** |
| Verbatim protégé | **Livré** |
| Badges pilotage produit-safe | **Livré** (partiel vs catalogue signaux) |
| Recommandations tuteur (synthèse, bascule, éval) | **Couronne 2.0+** en doc cluster 14 ; **oubli probable** si considéré lot UX tuteur initial |
| UI observabilité / D9bis | **Couronne 2.0+** |
| Dashboard cohorte analytics | **Couronne 2.0+** |
| Validation LearnerEvaluationRecord UI | **Convergence inachevée** (backend seul) |
| Cockpit COORDO | **Couronne 2.0+** |

---

## 3. Formateur

### CIBLE 2.0 (specs formateur + tuteur 2.0, écarts 40/50/110)

- **Base connaissances** : ingestion documents, dialogue d’élaboration (questionnaire), `TrainerKnowledgeItem` avec statuts `declared` / `derived_provisional` / `validated_trainer`.
- **Validation humaine** items dérivés ; lien référentiel ; alimentation RAG apprenant (indirect).
- **Orchestrateur formateur** : flux dialogique structuré, reprise, relances — **doctrinal riche**.
- **Pas d’accès** verbatim apprenant non partagé ; pas d’exports org (guard).

### RÉEL DANS LE CODE

| Élément | Fichier(s) | Comportement observé |
|---------|------------|----------------------|
| UI prod formateur | `ProdTrainerKnowledgeView.vue` | Route `/app/trainer/knowledge` — **liste + filtre statut + bouton Valider** uniquement. |
| API list | `TrainerKnowledgeItemListView` | `GET /hugo/trainer/knowledge-items/` — id, content, status, content_type, referential_item_id. |
| API validate | `TrainerKnowledgeValidationView` | `POST .../validate/` actions validate/reject/edit — **UI n’expose que validate**. |
| Élicitation dialogique | `TrainerElicitationQuestionsView`, `TrainerElicitationAnswersView` | Backend questionnaire 5 questions — **0 page front**. |
| Ingestion document | `TrainerDocumentIngestView` + `document_ingestor.py` | `POST /hugo/trainer/ingest-document/` — **0 UI upload**. |
| Création item manuelle | List view POST (si implémenté) | ListView = GET only ; création via elicitation/ingest backend — **pas de formulaire prod**. |
| Évaluations formateur | `TrainerEvaluationRecordListView`, validation, export | Endpoints complets — **0 composant front**. |
| Modèle | `TrainerKnowledgeItem` | Statuts, provenance, validated_by/at — aligné cible objet. |
| Tests | `test_trainer_knowledge.py`, smoke Playwright | List + validate couverts. |
| Surface tester | Routes admin référentiel / groupes | Configuration org, pas orchestrateur formateur dialogique. |

### ÉCARTS IMPORTANTS POUR L’UX

1. **Orchestrateur formateur = list/validate seulement en prod** — gap majeur vs spec (ingestion, elicitation, édition, rejet UI).
2. **Pas de création ni édition item** dans `ProdTrainerKnowledgeView` — items créés par bootstrap, tests, ou API directe.
3. **Pas de visualisation impact parcours apprenants** — cible ouverte, absent.
4. **Lien TrainerKnowledge → RAG apprenant** — pipeline backend partiel ; **A_VÉRIFIER** consommation runtime.

### CLASSIFICATION

| Écart | Classification |
|-------|----------------|
| Liste + validation items | **Livré** |
| Guards rôle / pas exports org | **Livré** (backend + tests) |
| Questionnaire élicitation UI | **Convergence inachevée** (backend prêt cluster précédent, jamais surfacé) |
| Upload / ingest document UI | **Convergence inachevée** |
| Édition / rejet item en UI | **Convergence inachevée** (API reject/edit existent) |
| Orchestrateur formateur dialogique complet | **Couronne 2.0+** |
| Validation evaluation records UI | **Convergence inachevée** |
| Impact items sur parcours | **Couronne 2.0+** |

---

## 4. Synthèse transversale

| Axe | Cible clé | Implémenté (prod `/app`) | Statut |
|-----|-----------|---------------------------|--------|
| **Apprenant** — UIState / progression / CTA | Contrat unique backend, CTA terminales | `ProdLearnerWorkspace` + `HugoProgressPanel` | **Livré** |
| **Apprenant** — sélecteur posture | G2-02 interactif + set-posture | Banner lecture seule ; API sans appel front | **Convergence inachevée** |
| **Apprenant** — profils youth/adult/pro | 3 grammaires UX | Presets + copy ; youth > adult ≈ pro | **Partiel / inachevé** |
| **Apprenant** — mémoire visible | Résumé gouverné fil | persistent_objects optionnel ; pas memory-summary | **Couronne / oubli probable** |
| **Apprenant** — RAG Appui | Badge citation lexicale | Badges sur messages assistant | **Livré** |
| **Tuteur** — timeline / traces | Lecture partageable, validation | `TutorLearnerView` prod | **Livré** |
| **Tuteur** — recommandations | Signal → action UI | Absent | **Couronne / oubli probable** |
| **Tuteur** — observabilité | Snapshots qualité | Backend only | **Couronne 2.0+** |
| **Formateur** — knowledge base | Ingest + elicitation + validate | List + validate | **Partiel** |
| **Formateur** — orchestrateur riche | Flux dialogique spec 2.0 | Non | **Couronne 2.0+** |
| **Encadrants** — validation éval records | Humaine, partagée | API sans UI prod | **Convergence inachevée** |

### Commentaire (5–10 lignes)

**Solide :** l’architecture **backend-first** tient en prod — UIState, CTA, confidentialité partage, timeline tuteur, badge RAG, guards rôles. Les smokes Playwright (A1/B1/C1) couvrent ces fondations.

**Sous-livré / mis de côté :** trois objets UX majeurs spec 2.0 restent **fragmentaires** : (1) le **sélecteur de posture apprenant** — le plus documenté (clusters 2, 4, 12, écarts 31), API livrée, **jamais branché** ; (2) l’**orchestrateur tuteur** côté recommandations — timeline OK mais pas de couche « guide d’accompagnement » ; (3) l’**orchestrateur formateur** — réduit à une **liste de validation** alors que le backend expose elicitation, ingest et evaluation-records.

**Pattern observé :** le backend a **anticipé** (set-posture, elicitation, observabilité, evaluation-records) ; le front prod `/app` n’a reçu qu’une **couche minimale showable**. Les surfaces tester (`LearnerDetailView`, admin) conservent plus de contrôles — écart prod/tester non résorbé.

**Recommandations priorité UX 2.0 cohérente :**

1. **P0 produit :** brancher `PostureSelector` sur `POST set-posture` (cluster 12) — ROI maximal, API prête.  
2. **P1 :** surfaces formateur elicitation + création item (réutiliser endpoints existants).  
3. **P1 :** panneau tuteur validation `LearnerEvaluationRecord` (endpoint prêt).  
4. **P2 / couronne :** recommandations tuteur, observabilité UI, memory-summary apprenant — cadrer explicitement avant implémentation.

---

## Sources mobilisées

- **Code front :** `hugo-hugolucia/frontend_1.8/src/` (composants ci-dessus, grep 2026-06-18).
- **Code back :** `hugo_back/apps/hugo/views_sessions.py`, `views_trainer.py`, `services/ui_state_builder.py`, `services/cta_ui_state.py`, `urls.py`.
- **Docs :** écarts 31, 40, 60, 110 ; clusters 12, 13, 14 ; specs interface 2.0, formateur + tuteur 2.0.
- **Tests :** `test_posture_modes.py`, `test_cluster4_surface_contracts.py`, smokes Playwright, `engagementUiModel.test.js`.

**A_VÉRIFIER :** parité Encoors des mêmes surfaces ; comportement `LearnerDetailView` en demo tester vs prod `/app`.
