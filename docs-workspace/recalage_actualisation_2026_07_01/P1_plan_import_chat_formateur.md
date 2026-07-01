# P1 — Import chat formateur + réalignement UI

**Date :** 2026-07-01  
**Baseline :** B (front 1.8 + `hugo_back` local)  
**Pipeline actif par défaut :** P0 legacy (`HUGO_P0_V17_ENABLED=false`) — ne pas supposer v17  
**Décision :** réalisation autorisée (risques bloquants ≤ moyen)

---

## 1. Résumé cadrage

### Sources mobilisées

- R0–R4 (`recalage_actualisation_2026_07_01/`)
- `modelisation_activite_formateur.md`, `modelisation_activite_tuteur.md` (Desktop)
- `spec_reconfiguration_chats_tuteur_formateur.md`
- Code : `views_trainer.py`, `TrainerKnowledgeItem`, `ProdLearnerLayout.vue`, `LearnerConversationFeed.vue`, `views_sessions.py`

### Réel confirmé utile P1

| Élément | Tag | Preuve |
|---------|-----|--------|
| CRUD `TrainerKnowledgeItem` + validate/provisional/reject | **REL OBSERV** | C15, `test_trainer_knowledge.py` |
| Statut `derived_provisional` | **REL OBSERV** | `mark_provisional` action |
| Chat formateur = réutilisation `/app` + `/app/session/:id` (formateur = `learner` de session) | **REL OBSERV PARTIEL** | `SessionListCreate.perform_create` ; pas de route `/app/trainer/chat` dédiée |
| `build_contract_ui_state` ≠ `build_ui_state` | **REL OBSERV** | R2 domaine 10, R4 §3 vs §7 |
| Label topbar « Chat apprenant » → `/app` | **REL OBSERV** | `ProdLearnerLayout.vue:75` |
| Boutons d'import chat | **CIBLE** → livrés P1 | ce lot |

---

## 2. Analyse de risque

| Risque | Niveau | Justification | Mesure de réduction |
|--------|--------|---------------|---------------------|
| Architecture / runtime | **Moyen** | Pas de session trainer dédiée ; formateur crée des sessions comme `learner` sur P0 legacy | Documenter ; ne pas brancher sur v17 ; import hors `GET ui-state` |
| Backend / contrat | **Faible** | Extension POST/PATCH existant, pas de nouveau modèle | Contrat JSON borné ; `source_type=chat_import` ; tests pytest |
| Frontend / UI | **Moyen** | Composants nouveaux sur fil conversation partagé | Composant `ImportFromChatAction` isolé ; prop `showTrainerImportActions` |
| ACL / permissions | **Faible** | `can_manage_trainer_knowledge` déjà en place | Réutiliser garde backend ; masquer boutons si non trainer-like |
| Surface non prouvée | **Moyen** | Espace chat formateur = clone `/app`, non respecifié métier | P1 limité à import + labels ; pas de prompting formateur dédié |
| Régression trainer | **Faible** | Toucher knowledge list minimalement | Tests smoke Playwright existants conservés |
| Confusion baseline B vs A | **Moyen** | Encoors non revalidé | Rappel baseline B dans doc et tests locaux uniquement |

**Règle de décision :** aucun risque **élevé** bloquant → **réalisation P1 autorisée**.

---

## 3. Cible retenue (P1)

1. **Réalignement UI formateur** : `Chat apprenant` → `Mon chat` pour persona TRAINER pur sur `/app*` ; entrée « Mon chat » depuis orchestrateur.
2. **Bouton « Importer comme ressource provisoire »** : modale de confirmation → `POST /hugo/trainer/knowledge-items/` en `derived_provisional`.
3. **Bouton « Importer comme explicitation pédagogique »** : même socle, `content_type=pedagogical_explication`, champs structurés dans `meta.explication`.
4. **Bouton « Importer comme justification d'arbitrage »** : `PATCH` item existant, `meta.decision_rationale` (brouillon), pas de création autonome.

**Hors P1 :** flows tuteur, surfaces 2.0 non prouvées, écriture sans confirmation humaine.

---

## 4. Plan de tâches ordonné

### Backend

1. Étendre `POST /hugo/trainer/knowledge-items/` : `status`, `source_type`, `provenance_note`, `meta` avec trace import (`import_kind`, `session_id`, `source_message_ids`).
2. Fusionner `meta` sur `PATCH` (ne pas écraser les clés existantes).
3. Tests pytest `test_trainer_chat_import.py`.

### Frontend

1. Utilitaires `trainerUiLabels.js`, `trainerChatImport.js` + tests unitaires.
2. `ImportFromChatAction.vue` + `TrainerImportConfirmModal.vue`.
3. Brancher sur `LearnerConversationFeed` / `ProdLearnerWorkspace` si `isTrainerLike` et session active.
4. Réaligner `ProdLearnerLayout`, `ProdTrainerKnowledgeView`, microcopy accueil formateur.
5. Playwright : label « Mon chat » + smoke import (mock ou fixture).

### Contrats

- Voir §6 — pas de nouveau endpoint ; extension payloads POST/PATCH.

---

## 5. Fichiers à modifier

| Fichier | Action |
|---------|--------|
| `hugo_back/apps/hugo/views_trainer.py` | Étendre POST/PATCH |
| `hugo_back/apps/hugo/tests/test_trainer_chat_import.py` | **Nouveau** |
| `frontend_1.8/src/utils/trainerUiLabels.js` | **Nouveau** |
| `frontend_1.8/src/utils/trainerUiLabels.test.js` | **Nouveau** |
| `frontend_1.8/src/utils/trainerChatImport.js` | **Nouveau** |
| `frontend_1.8/src/utils/trainerChatImport.test.js` | **Nouveau** |
| `frontend_1.8/src/utils/trainerNavigation.js` | Constantes chat |
| `frontend_1.8/src/components/trainer/ImportFromChatAction.vue` | **Nouveau** |
| `frontend_1.8/src/components/trainer/TrainerImportConfirmModal.vue` | **Nouveau** |
| `frontend_1.8/src/components/learner/LearnerConversationFeed.vue` | Slot import |
| `frontend_1.8/src/components/learner/ProdLearnerWorkspace.vue` | Câblage modal |
| `frontend_1.8/src/layouts/ProdLearnerLayout.vue` | Labels |
| `frontend_1.8/src/views/ProdTrainerKnowledgeView.vue` | Entrée Mon chat |
| `frontend_1.8/src/views/ProdLearnerHomeView.vue` | Microcopy formateur |
| `frontend_1.8/tests_playwright/test_smoke_trainer_chat_labels.spec.ts` | **Nouveau** |

---

## 6. Contrats JSON cibles

### Entrée flow (front, pré-confirmation)

```json
{
  "session_id": "uuid",
  "source_message_ids": ["uuid"],
  "import_kind": "trainer_resource_provisional | trainer_explication | trainer_decision_rationale",
  "draft_title": "string",
  "draft_body": "string",
  "source_summary": "string",
  "human_validation_required": true
}
```

### POST create (ressource / explicitation)

```json
{
  "content": "string",
  "content_type": "mastery_criterion | pedagogical_explication",
  "source_type": "chat_import",
  "status": "derived_provisional",
  "referential_item_id": "string",
  "provenance_note": "Créé depuis chat — à relire",
  "meta": {
    "import_kind": "trainer_resource_provisional",
    "session_id": "uuid",
    "source_message_ids": ["uuid"],
    "draft_title": "string",
    "explication": {}
  }
}
```

### PATCH justification (item cible)

```json
{
  "meta": {
    "decision_rationale": {
      "envisioned_decision": "string",
      "reasons": "string",
      "risks": "string",
      "criteria_used": "string",
      "next_action": "string",
      "session_id": "uuid",
      "source_message_ids": ["uuid"],
      "status": "draft"
    }
  }
}
```

---

## 7. Critères d'acceptation

### Fonctionnels

- [ ] TRAINER pur voit « Mon chat » (topbar + orchestrateur) pointant vers `/app`.
- [ ] Sous message assistant en session formateur : 3 boutons d'import visibles.
- [ ] Chaque bouton ouvre une modale éditable ; aucun write sans confirmation.
- [ ] Ressource provisoire créée en `derived_provisional`, visible dans orchestrateur.
- [ ] Explicitation : `content_type=pedagogical_explication`, statut provisoire.
- [ ] Justification : `meta.decision_rationale` sur item sélectionné, pas de nouvel item.

### Techniques

- [ ] Pas d'usage de `GET /ui-state/` pour le brouillon import.
- [ ] Tests pytest POST import PASS.
- [ ] Tests unitaires front draft builder PASS.
- [ ] Playwright label « Mon chat » PASS (baseline B).

---

## 8. Matrice de tests

| ID | Type | Scénario | Fichier |
|----|------|----------|---------|
| T1 | pytest | POST chat_import → `derived_provisional` + meta | `test_trainer_chat_import.py` |
| T2 | pytest | POST explicitation `pedagogical_explication` | idem |
| T3 | pytest | PATCH merge `decision_rationale` | idem |
| T4 | node:test | `buildChatImportDraft` shapes | `trainerChatImport.test.js` |
| T5 | node:test | `resolveTrainerChatNavLabel` | `trainerUiLabels.test.js` |
| T6 | Playwright | TRAINER voit « Mon chat » sur `/app/trainer/knowledge` | `test_smoke_trainer_chat_labels.spec.ts` |

---

## 9. Mapping labels UI (inventaire P1)

| Label actuel | Label cible | Contexte | Justification |
|--------------|-------------|----------|---------------|
| Chat apprenant | **Mon chat** | Topbar, TRAINER pur, lien `/app` | Espace conversationnel formateur, pas apprenant |
| Parcours apprenant | **Espace formateur** | Brand subtitle, TRAINER sur `/app*` | Alignement fonction réelle |
| (absent) | **Mon chat** | Orchestrateur knowledge | Point d'entrée explicite |
| Démarrer ma session | **Démarrer mon échange** | Accueil `/app`, TRAINER | Ton formateur |

---

## 10. À VÉRIFIER

- Parité Encoors des routes trainer et sessions (baseline A) — **sans oracle authentifié récent**.
- Lien `TrainerKnowledgeItem` validé → RAG lexical bout-en-bout.
- INC-02 : `GET /dashboard/groups/{id}/learners/` vide pour TRAINER.
- Comportement ORGADMIN sur `/app` : conserve « Chat apprenant » (testeur apprenant).
- Prompting / conduct-profiles formateur dédiés — **CIBLE**, hors P1.
