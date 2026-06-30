# Backlog — restructuration front formateur (depuis le réel)

**Référence :** [audit_front_formateur_00_rapport.md](audit_front_formateur_00_rapport.md) · [matrice](audit_front_formateur_01_matrice.md)  
**Principe :** pas de refonte moteur ; réutiliser routes/API existantes ; orgadmin garde le CRUD profils.

---

## Modules cibles (organisation écrans)

| Module | Vues existantes à regrouper | Objet central | Priorité formateur |
|--------|----------------------------|---------------|-------------------|
| **Cockpit formateur** | *nouveau* `/app/trainer` | Org + cohortes | Entrée unique |
| **Base connaissances** | `ProdTrainerKnowledgeView`, `ProdTrainerElicitationView` | `TrainerKnowledgeItem` | Valider, éditer, éliciter |
| **Bibliothèque & RAG** | Extraire bloc library de `GroupAdminDetailView` | `Document`, `GroupDocument` | Créer, indexer, lier (API déjà OK) |
| **Profils (lecture)** | *nouveau* lecture depuis GET groupe + profil | `LearnerConversationGlobalProfile` | Consulter profil actif du groupe |
| **Suivi cohortes** | `ProdTutorHome/Group/Learner` | Apprenants liés | Timeline (existant) |
| **Évaluations** | *nouveau* | `LearnerEvaluationRecord` | Valider / commenter |

**Hors périmètre formateur (reste orgadmin) :** CRUD profils, conduct profiles, tutor prompts, attribution groupe, exports Qualiopi.

---

## Chantiers classés

### P0 — rupture parcours

| ID | Chantier | Type | Fichiers / zone | Critère d’acceptation |
|----|----------|------|-----------------|----------------------|
| B1 | Hub `/app/trainer` (index) + nav prod | CODE | `router/index.js`, `ProdLearnerLayout.vue`, nouveau `ProdTrainerHomeView.vue` | TRAINER atterrit sur cockpit ; liens knowledge, élicitation, suivi |
| B2 | Lecture profil conversationnel du groupe (sans édition) | CODE | Nouvelle vue ou section hub ; `GET /groups/{id}/`, profils actifs | Formateur voit nom + complétude du profil appliqué à sa cohorte |
| B3 | Libellé honnête usage knowledge | CODE + DOC | `ProdTrainerKnowledgeView`, `03_ETAT_PRODUIT_REEL.md` | Colonne Usage précise « évaluation » ; pas « moteur général » |

### P1 — capacités backend déjà prêtes

| ID | Chantier | Type | Fichiers / zone | Critère d’acceptation |
|----|----------|------|-----------------|----------------------|
| B4 | UI documents/RAG formateur | CODE | Réutiliser handlers `GroupAdminDetailView` ; route `/app/trainer/library` | TRAINER crée document, indexe, lie au groupe (smoke API 200) |
| B5 | Picker référentiel dans élicitation | CODE | `ProdTrainerElicitationView` ; `GET /referentials/` | Plus de saisie UUID libre seule |
| B6 | Écran `trainer/evaluation-records` | CODE | Nouvelle vue prod ; `views_trainer.py` existant | Liste + validate/comment depuis UI |
| B7 | Séparer UX orgadmin vs TRAINER sur knowledge | CODE | `roleGuards` + templates | Orgadmin voit lien admin ; TRAINER vue simplifiée |

### P2 — cohérence produit

| ID | Chantier | Type | Fichiers / zone | Critère d’acceptation |
|----|----------|------|-----------------|----------------------|
| B8 | Redirect rôle à la connexion | CODE | `frontendConfig.js` ou post-login | TRAINER → `/app/trainer` (si pas multi-rôle apprenant) |
| B9 | Renommer / déplacer hub admin | DOC + CODE | `TrainerOrchestratorAdminView` | Libellé « Admin — outils formateur » ; pas « orchestrateur » pour orgadmin |
| B10 | Scénario démo formateur | DOC + OPS | `09_PARCOURS_DEMO_ET_SCENARIOS.md` | Parcours Sx : knowledge → validation → (évaluation) |

### P3 — arbitrage moteur (hors front immédiat)

| ID | Chantier | Type | Note |
|----|----------|------|------|
| B11 | Knowledge items dans tour conversation | CODE back | Écart cible 2.0 vs réel ; décision CTO avant front |
| B12 | Unifier tester : entrée encadrant vs formateur | CODE | Réduire confusion `/dashboard` mode testeur |

---

## Décisions documentaires suggérées

| # | Décision | Statut proposé |
|---|----------|----------------|
| D1 | Le formateur **ne CRUD pas** les profils comportementaux ; lecture + demande à l’orgadmin | À valider CTO |
| D2 | `TrainerKnowledgeItem` **n’alimente pas** le chat aujourd’hui — documenter comme réel, pas comme bug front seul | À valider produit |
| D3 | Bibliothèque RAG formateur = **même API** que admin groupe ; pas de nouveau modèle | Validé par code |
| D4 | Hub `/admin/conversation/trainer` = **console orgadmin**, pas surface TRAINER | À mettre à jour dans `03` |

---

## Ordre d’exécution recommandé

```
B1 → B3 → B2 → B5 → B4 → B6 → B7 → B8 → B10
```

Estimation indicative : **P0** ~ 2–3 j dev front ; **P1** ~ 4–6 j ; **P2–P3** selon arbitrage moteur.

---

*Backlog juin 2026 — actions DOC / CODE / OPS ; pas de migration base.*
