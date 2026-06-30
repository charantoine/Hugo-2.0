# Matrice d’écarts — front formateur (juin 2026)

**Référence :** [audit_front_formateur_00_rapport.md](audit_front_formateur_00_rapport.md)

---

## 1. Surfaces front

| Objet / surface | Route | Composant | Rôle UI | Fonction réelle TRAINER | Maturité | Impact conversation |
|-----------------|-------|-----------|---------|-------------------------|----------|---------------------|
| Knowledge liste | `/app/trainer/knowledge` | `ProdTrainerKnowledgeView` | TRAINER (+ orgadmin) | Valider / rejeter / éditer items | REL_OBSERVÉ | Évaluation uniquement |
| Élicitation | `/app/trainer/elicitation` | `ProdTrainerElicitationView` | TRAINER | Créer items `declared` | REL_OBSERVÉ | Indirect |
| Espace tuteur | `/app/tutor` | `ProdTutorHomeView` | Tuteur-like | Lister groupes accessibles | REL_OBSERVÉ | Non |
| Cohorte tuteur | `/app/tutor/group/:gid` | `ProdTutorGroupView` | Tuteur-like | Apprenants visibles | REL_OBSERVÉ | Non |
| Timeline apprenant | `/app/tutor/.../learner/:lid` | `TutorLearnerView` | Tuteur-like | Traces, compétences | REL_OBSERVÉ | Non |
| Parcours apprenant | `/app` | `ProdLearnerHomeView` | Tous | Session apprenant | REL_OBSERVÉ | Oui si self |
| Dashboard testeur | `/dashboard` | `DashboardView` | Encadrant | Raccourci groupe démo | REL_OBSERVÉ | Non |
| Groupe testeur | `/group/:gid` | `GroupView` | Encadrant | Liste + exports (si orgadmin) | REL_OBSERVÉ | Non |
| Learner testeur | `/group/:gid/learner/:lid` | `LearnerSpaceView` | Encadrant | Timeline (autrui) / chat (soi) | REL_OBSERVÉ | Partiel |
| Référentiel groupe | `/group/:gid/referential` | `GroupReferentialConfigView` | Encadrant | Associer référentiel | REL_OBSERVÉ | Indirect |
| Hub admin formateur | `/admin/conversation/trainer` | `TrainerOrchestratorAdminView` | ORGADMIN | Liens vers prod + admin | REL_OBSERVÉ | — (TRAINER bloqué) |
| Profils conversationnels | `/admin/conversation/learner/profiles` | `LearnerConversationProfilesView` | ORGADMIN | CRUD profils globaux | REL_OBSERVÉ | Config moteur |
| Profils conduite | `/conduct-profiles` | `ConductProfilesView` | ORGADMIN | CRUD `TutorConductProfile` | REL_OBSERVÉ | Config moteur |
| Attribution profil groupe | `/groups-admin/:id` | `GroupAdminDetailView` | ORGADMIN | Select profil + library RAG | REL_OBSERVÉ | Config moteur |
| Évaluations formateur | — | *absent* | — | — | REL_OBSERVÉ (API seule) | Évaluation |

---

## 2. Capacités par objet métier

| Capacité | TRAINER UI | ORGADMIN UI | Endpoint clé | Consommé runtime |
|----------|------------|-------------|--------------|------------------|
| `TrainerKnowledgeItem` list | ✅ | ✅ (même route) | `GET /hugo/trainer/knowledge-items/` | Évaluation |
| `TrainerKnowledgeItem` create | ⚠️ élicitation/ingest | idem | `POST elicitation-answers`, `documents/ingest` | — |
| `TrainerKnowledgeItem` validate | ✅ | ✅ | `POST …/validate/` | Évaluation |
| `LearnerConversationGlobalProfile` CRUD | ❌ | ✅ | `/hugo/learner-conversation-profiles/` | Tour + évaluation |
| Profil → groupe | ❌ | ✅ | `PATCH /groups/{id}/` | Tour |
| `TutorConductProfile` CRUD | ❌ | ✅ | `/hugo/conduct-profiles/` | Tour |
| `TutorPrompt` CRUD | ❌ | ✅ | `/hugo/tutor-prompts/` | Tour (legacy/slots) |
| `Document` + RAG groupe | ❌ | ✅ `GroupAdminDetailView` | `/documents/`, `/groups/:id/library/` | Tour (RAG) |
| `trainer_directives` | ❌ | ✅ closing view | `EvaluationPolicy` | Évaluation |
| `LearnerEvaluationRecord` review | ❌ | ❌ front | `trainer/evaluation-records/` | Évaluation |

Légende : ✅ REL_OBSERVÉ · ❌ absent · ⚠️ PARTIEL

---

## 3. Flux action → moteur

| Flux formateur | Chemin | Impact chat apprenant | Impact évaluation |
|----------------|--------|----------------------|-------------------|
| Valider knowledge item | Front → `validate/` → `validated_trainer` | Non | Oui (prompt) |
| Élicitation | Front → items `declared` → validation | Non | Après validation |
| Documents RAG (backend OK) | Pas de front TRAINER | Oui (si lié groupe) | Non |
| Config profils (orgadmin) | Hors TRAINER | Oui (tour) | Oui |

---

## 4. Matrice écarts → action

| ID | Objet | Réel | Cible / attente métier | Statut | Action suggérée |
|----|-------|------|------------------------|--------|-----------------|
| M1 | UI profils groupe | Absente TRAINER | Formateur informé du profil actif | Écart | Lecture seule + lien admin |
| M2 | Knowledge → chat | Évaluation seule | Enrichissement conversation (cible 2.0 partielle) | Écart | Clarifier UI + doc ; cible moteur A_VERIFIER |
| M3 | Library TRAINER | API oui, UI non | Ingestion documentaire formateur | Écart | Vue formateur réutilisant API |
| M4 | Evaluation records | API oui, UI non | Validation humaine évaluations | Écart | Écran prod formateur |
| M5 | Hub formateur | 2 routes | Cockpit métier | Écart | `/app/trainer` index |
| M6 | Élicitation | ID manuel | Rattachement référentiel guidé | Partiel | Picker référentiel |
| M7 | Rôle / navigation | `/app` défaut | Entrée formateur claire | Écart | Redirect ou hub selon rôle |
| M8 | `usage_stats` | Message générique | Transparence usage réel | Partiel | Libellé « évaluation uniquement » |

---

*Matrice juin 2026 — à fusionner dans les mises à jour périodiques des ecarts domaine 40 / 50 / 110.*
