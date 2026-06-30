# Conception — pilotage formateur de la conversation via RAG et apports métier

**Date :** juin 2026  
**Prérequis :** [audit_front_formateur_00_rapport.md](audit_front_formateur_00_rapport.md)  
**Statut :** proposition d’itération incrémentale — **non implémentée**

---

## Sources mobilisées (réel code)

| Zone | Fichiers |
|------|----------|
| RAG sélection | `hugo_back/apps/hugo/services/rag_support.py` |
| Injection prompt | `hugo_orchestrator.py` L330-337, `prompt_renderer.py` L374-384 |
| Citations apprenant | `tracing.py` `persist_rag_citations`, `ProdLearnerWorkspace.vue` |
| Documents | `library/models.py`, `library/views.py`, `library/serializers.py` |
| Meta document admin | `GroupAdminDetailView.vue` L195-205 |
| Knowledge formateur | `TrainerKnowledgeItem`, `views_trainer.py` |
| Consommation knowledge aujourd’hui | `evaluation_service.py` uniquement |
| Référentiel overlays | `ReferentialItemOverlay`, `context_builder.py`, `teaching_plan_builder.py` |
| Permissions TRAINER library | `IsOrgAdminSuperadminOrTrainer` |

---

## 1. Carte des points d’ancrage techniques

### 1.1 Bibliothèque documentaire (RAG conversation — **déjà actif**)

| Élément | Comportement réel | Limites | Réutilisation |
|---------|-------------------|---------|---------------|
| `Document` | `title`, `source_text`, `meta` JSON, `file_path` (optionnel) | **Pas d’upload fichier front** ; collage texte ou chemin serveur | **Base cas 1** (cours) |
| `POST /documents/` | Création org-scoped | TRAINER autorisé ; **pas d’UI prod** | Surface formateur à extraire de `GroupAdminDetailView` |
| `POST /documents/{id}/index/` | Chunking ; copie `document.meta` → `chunk.meta.document_meta` | Lexical only (pas embedding search en prod observé) | Indexation cours |
| `GroupDocument` | Lie doc ↔ groupe, `ACTIVE`/`INACTIVE` | Portée = **groupe** uniquement | Portée cohorte |
| `select_rag_chunks()` | Filtre `session.group_id` ; score lexical + `_score_document_meta` | RAG **conditionnel** (`should_use_rag`) ; max 3 chunks | Boost priorité formateur |
| `render_with_tutor_prompt` | `rag_chunks` → `documents_block` dans system prompt | Pas de bloc « intention pédagogique » séparé | Extension vars |
| `RagCitation` | Badges « Appui : {titre} » côté apprenant | Lié aux chunks RAG sélectionnés au tour | **Voie citable apprenant** |

**`Document.meta` déjà exploité par le score RAG** (`rag_support._score_document_meta`) :

- `trainer_priority` : `"high"` → +1.5
- `knowledge_type` : `diagnostic`, `knowledge`, `revision`, `mistake_pattern`, etc.
- `intended_profiles` : liste postures (`reflective_afest`, …)
- `mastery_criteria`, `common_mistakes`, `reasoning_points` : listes → +0.5 chacune

**Champs admin déjà saisis** (`GroupAdminDetailView`) mais **inaccessibles au TRAINER** aujourd’hui.

### 1.2 TrainerKnowledgeItem (knowledge formateur — **évaluation seulement**)

| Élément | Comportement réel | Limites | Réutilisation |
|---------|-------------------|---------|---------------|
| Modèle | `content`, `content_type`, `status`, `referential_item_id` (texte), `provenance_note` | **Pas de `meta` JSON** ; pas de `group_id` | **Base cas 2** avec petite extension |
| `content_type` | `mastery_criterion`, `frequent_error`, `reasoning_chain`, `reference_rule`, `procedure` | Aligné sémantique cas 2 | Réutiliser tel quel |
| Workflow | `declared` → `derived_provisional` → `validated_trainer` | Validation humaine obligatoire | Garder |
| UI | `ProdTrainerKnowledgeView`, `ProdTrainerElicitationView` | Pas de lien groupe ; ID référentiel manuel | Étendre formulaires |
| Runtime | `_validated_trainer_items()` → **prompt évaluation** | **Absent de `hugo_orchestrator`** | **Extension P0 conversation** |

### 1.3 Référentiel et overlays (hors saisie formateur obligatoire)

| Élément | Rôle | Lien formateur |
|---------|------|----------------|
| `ReferentialItemOverlay` | `common_mistakes`, `coach_questions`, … par item référentiel | Saisie encadrant/tester ; **pas formateur prod** |
| `teaching_plan_builder` | Injecte `overlay_common_mistakes` dans `critical_mistakes` | Consommé au tour si focus référentiel |
| `PUT …/overlay` | Édition overlay par item | Option **liaison suggérée** cas 2, pas prérequis |

### 1.4 Profils comportementaux (config admin — consommés, non pilotés formateur)

| Élément | Rôle dans conversation |
|---------|------------------------|
| `LearnerConversationGlobalProfile` | Slots `TutorPrompt` + `TutorConductProfile` par posture |
| `resolve_conduct_profile` | Contraintes posture chaque tour |
| `EvaluationPolicy.trainer_directives` | Évaluation uniquement |

**Ne pas confondre** avec le playbook formateur : les profils restent orgadmin ; les apports formateur s’**additionnent** sans les remplacer.

### 1.5 Synthèse réutilisation vs nouveau

| Besoin | Réutiliser | Étendre / créer |
|--------|------------|-----------------|
| Cours / support | `Document` + `GroupDocument` + RAG | `meta` : `pedagogical_intent`, `conversation_role` ; UI formateur ; upload fichier (P2) |
| Point technique texte | `Document` court **ou** `TrainerKnowledgeItem` | Champ `visibility` ; branche orchestrateur |
| Raisonnements / erreurs | `TrainerKnowledgeItem` types existants | `situation_cue`, `desired_response` en `meta` ; injection conversation |
| Lien référentiel optionnel | `referential_item_id` + endpoint suggestion | `POST …/suggest-referential-links/` (lecture seule) |
| Conduite conversation | `hugo_orchestrator` + `prompt_renderer` | Nouveau bloc `trainer_playbook_block` + boost RAG |

---

## 2. Design des flux formateur

### Cas 1 — « J’upload mon cours pour que Hugo s’y réfère préférentiellement »

#### Parcours minimal (incrémental)

```
/app/trainer (hub) 
  → Bibliothèque cohorte (/app/trainer/library?groupId=…)
  → [Créer ressource] 
  → Coller texte / (P2) upload fichier 
  → Renseigner intention pédagogique 
  → [Indexer] → [Activer sur le groupe]
```

**Aujourd’hui :** TRAINER doit passer par orgadmin (`/groups-admin`) — **bloqué**. **Évolution P0 :** extraire le panneau library vers `/app/trainer/library` (même API).

#### Données nécessaires

| Champ | Stockage | Existant ? |
|-------|----------|------------|
| Fichier / texte | `Document.source_text` ou `file_path` | `source_text` oui ; upload non |
| Titre | `Document.title` | Oui |
| Portée | `GroupDocument.group_id` | Oui (groupe) |
| Rôle pédagogique | `Document.meta.pedagogical_intent` (texte) | **À ajouter** (JSON) |
| Priorité conversation | `Document.meta.trainer_priority = "high"` | **Oui** |
| Type | `Document.meta.knowledge_type = "knowledge"` ou `"reference_course"` | Partiel (`knowledge` existe) |
| Postures cibles | `Document.meta.intended_profiles` | Oui |
| Rôle conversationnel | `Document.meta.conversation_role = "reference_course"` | **À ajouter** |
| Citabilité | `Document.meta.visibility = "learner_citable"` | **À ajouter** |

#### Traduction technique

1. `POST /documents/` — payload identique à `GroupAdminDetailView` + nouveaux champs `meta`.
2. `POST /documents/{id}/index/` — inchangé ; `document_meta` propagé aux chunks.
3. `POST /groups/{groupId}/library/` — liaison ACTIVE.
4. **RAG boost** (`rag_support._score_document_meta`) — ajouter :

```python
if document_meta.get("conversation_role") == "reference_course":
    score += 2.5
    reasons.append("reference_course")
```

5. **Option diagnostic / knowledge_review** : si `reference_course` lié au groupe et `should_use_rag` faux, injecter **synopsis** (titre + `pedagogical_intent` + 1er chunk) via nouveau bloc playbook — évite dépendance totale au lexical match.

#### Interaction profils

- `intended_profiles` continue de filtrer par posture active.
- `TutorConductProfile` / profil global **inchangés** — le cours enrichit le **contenu**, pas la conduite.

---

### Cas 1 bis — « J’ajoute un point technique en texte libre »

#### Deux voies selon visibilité

| Visibilité | Modèle | Mécanisme conversation |
|------------|--------|------------------------|
| **Interne** (guide Hugo, pas cité) | `TrainerKnowledgeItem` `content_type=reference_rule` ou nouveau `technical_note` | Bloc `trainer_playbook_block` (toujours injecté si `validated_trainer`) |
| **Citable** (peut apparaître à l’apprenant) | `Document` court (`source_text` < 2k) + lien groupe | RAG + `RagCitation` si sélectionné |

#### Saisie

- **Surface 2** (voir §4) : formulaire simple titre + texte + toggle « visible apprenant » + groupe.
- API :
  - Si interne → `POST` via élicitation-like ou nouveau `POST /hugo/trainer/knowledge-items/` (list view n’a que GET aujourd’hui — **petit endpoint CREATE**).
  - Si citable → `POST /documents/` + link library.

#### Distinction technique

```json
// Document.meta (citable)
{
  "conversation_role": "technical_point",
  "visibility": "learner_citable",
  "trainer_priority": "high"
}

// TrainerKnowledgeItem (interne) — extension meta migration légère
{
  "visibility": "internal",
  "scope_group_ids": ["uuid-groupe"]
}
```

---

### Cas 2 — « Raisonnements attendus, erreurs fréquentes, astuces »

#### Structure data minimale (extension `TrainerKnowledgeItem`)

**Migration légère recommandée :** `meta = models.JSONField(default=dict)` sur `TrainerKnowledgeItem`.

| Champ `meta` | Usage |
|--------------|-------|
| `situation_cue` | Ce que l’apprenant dit/fait (déclencheur) |
| `expected_reasoning` | Raisonnement attendu |
| `desired_response` | Réaction souhaitée de Hugo |
| `visibility` | `internal` \| `citable` |
| `scope_group_ids` | Portée cohorte(s) ; vide = org entière |
| `referential_item_id_confirmed` | Lien optionnel confirmé |
| `referential_suggestions` | Liste suggestions non confirmées |

**Mapping `content_type` existant :**

| Saisie formateur | `content_type` |
|------------------|----------------|
| Erreur fréquente | `frequent_error` |
| Raisonnement attendu | `reasoning_chain` |
| Astuce / règle | `reference_rule` |
| Critère de maîtrise | `mastery_criterion` |
| Procédure / situation pro | `procedure` |

**Pas de compétence obligatoire à la saisie** — `referential_item_id` reste optionnel (vide autorisé).

#### Liaison référentiel optionnelle (workflow)

1. Formateur enregistre en `declared` sans référentiel.
2. `POST /hugo/trainer/knowledge-items/{id}/suggest-referential-links/` :
   - Entrée : `content` + `situation_cue`
   - Backend : recherche lexicale sur `ReferentialItem` du groupe (`GET /referentials/`, items) — **pas de nouveau modèle**
   - Sortie : `[{ item_id, label, score }]` top 5
3. UI : panneau « Suggestions » — boutons Confirmer / Ignorer.
4. Si confirmé → `meta.referential_item_id_confirmed` + optionnel `PATCH` overlay (orgadmin ou formateur selon arbitrage — **A_VERIFIER** permissions overlay).

#### Exploitation conversation

Nouveau service **`trainer_playbook_resolver.py`** :

```python
def load_trainer_playbook_for_session(session) -> TrainerPlaybook:
    """
    Items validated_trainer pour org (+ filtre group_id si scope).
    Regroupe par content_type pour le prompt.
  """
```

Injection dans `hugo_orchestrator` **après** `build_hugo_context`, **avant** `render_with_tutor_prompt` :

```
trainer_playbook_block =
  "## Apports formateur validés\n"
  "- Erreurs fréquentes à surveiller : …\n"
  "- Si l'apprenant … alors …\n"
```

**Patterns erreurs** : pas de classifieur dédié en P0 — le LLM lit le bloc ; P2 : matcher `situation_cue` tokens dans `learner_text` pour prioriser sous-ensemble.

**Compatibilité** : `teaching_plan.critical_mistakes` reste alimenté par référentiel ; playbook **concatène** sans écraser.

---

## 3. Intégration pipeline RAG + orchestrateur

### 3.1 Points d’injection (modifications minimales)

```
hugo_orchestrator.run_turn()
  │
  ├─ build_hugo_context(session)          [existant — référentiel, overlays]
  ├─ decide_conversation / teaching_plan  [existant]
  │
  ├─ NEW: trainer_playbook = load_trainer_playbook_for_session(session)
  │
  ├─ select_rag_chunks(...)               [existant — étendre _score_document_meta]
  │
  ├─ render_with_tutor_prompt(
  │     …,
  │     rag_chunks=[…],
  │     trainer_playbook=trainer_playbook,  # NEW param
  │   )
  │
  └─ persist_rag_citations               [existant — citations apprenant]
```

### 3.2 Fichiers impactés

| Fichier | Changement |
|---------|------------|
| `rag_support.py` | Boost `reference_course`, `technical_point` ; option seed chunk cours |
| `trainer_playbook_resolver.py` | **Nouveau** — charge items + synopsis docs |
| `hugo_orchestrator.py` | Appel resolver ; passer playbook au renderer |
| `prompt_renderer.py` | `trainer_playbook_block` dans `base_system_intro` ou `documents_block` |
| `views_trainer.py` | `POST` create item ; `suggest-referential-links` |
| `models.py` | `TrainerKnowledgeItem.meta` JSONField (migration 1) |
| `ProdTrainer*.vue` + nouvelle library view | Surfaces §4 |

### 3.3 Comportement conversationnel attendu

| Apport | Effet sans réarchitecture |
|--------|---------------------------|
| Cours `reference_course` | Chunks favorisés ; contenu dans explications quand RAG actif |
| Point technique citable | RAG + badge « Appui : … » |
| Erreurs / raisonnements (playbook) | System prompt enrichi ; influence diagnostic (`should_explain_briefly`) et réponses |
| Items non validés | **Ignorés** (garde-fou métier) |

### 3.4 Séparation des trois couches

| Couche | Mécanisme | Visible apprenant |
|--------|-----------|-------------------|
| Base documentaire RAG | `Document` + chunks | Si sélectionné → citation |
| Directives conduite internes | `trainer_playbook_block` | Non |
| Référentiel primaire | `context_builder` + overlays | Non (structure compétences) |

---

## 4. Surfaces de contribution formateur

### Surface A — « Ressources de cours et contexte »

**Route proposée :** `/app/trainer/library?groupId={uuid}`  
**Accès :** depuis hub `/app/trainer` ; TRAINER + orgadmin.

| Champ UI | API |
|----------|-----|
| Groupe (select) | `GET /groups/` |
| Titre | `POST /documents/` `{ title }` |
| Contenu (textarea / fichier P2) | `{ source_text }` ou upload futur |
| Pourquoi c’est important | `meta.pedagogical_intent` |
| Type de ressource | `meta.conversation_role` : `reference_course` \| `context` |
| Priorité | `meta.trainer_priority` : normal \| high |
| Postures concernées | `meta.intended_profiles[]` |
| Visible / citable apprenant | `meta.visibility` |
| Actions | Indexer, Lier au groupe, Désactiver lien |

**Réutilise :** logique `GroupAdminDetailView` L185-272 (copie composant).

---

### Surface B — « Points techniques et ajustements »

**Route :** `/app/trainer/playbook/notes` ou panneau dans knowledge.

| Champ | Backend |
|-------|---------|
| Texte libre | `TrainerKnowledgeItem.content` ou `Document.source_text` court |
| Visible apprenant ? | Bascule → Document vs KnowledgeItem |
| Groupe | `meta.scope_group_ids` ou lien library |
| Actions | Enregistrer → `declared` ; Valider (workflow existant) |

**API :** étendre `TrainerKnowledgeItemListView` avec `POST` ; ou endpoint dédié `POST /hugo/trainer/playbook-notes/`.

---

### Surface C — « Raisonnements attendus et erreurs typiques »

**Route :** `/app/trainer/playbook/patterns` (ou onglet dans knowledge).

| Champ | Mapping |
|-------|---------|
| Situation typique | `meta.situation_cue` |
| Type | select → `content_type` |
| Raisonnement attendu | `content` (ou champ dédié meta) |
| Erreur fréquente | `content` si type `frequent_error` |
| Réaction souhaitée | `meta.desired_response` |
| Lien référentiel | optionnel ; bouton « Suggérer » → API suggestion |

**Workflow :** save `declared` → review liste existante (`ProdTrainerKnowledgeView`) → validate.

---

## 5. Phasage implémentation recommandé

| Phase | Livrable | Effort |
|-------|----------|--------|
| **P0** | Surface A (library formateur) + meta `pedagogical_intent` / `conversation_role` + boost RAG | 3-4 j |
| **P0** | `trainer_playbook_resolver` + injection prompt items `validated_trainer` | 2-3 j |
| **P1** | Surface C + `meta` JSON sur `TrainerKnowledgeItem` + POST create | 3-4 j |
| **P1** | API suggestion référentiel optionnelle | 2 j |
| **P2** | Upload fichier réel ; matching `situation_cue` | 5+ j |

---

## 6. A_VERIFIER

- Permissions `PUT overlay` pour formateur sur item référentiel confirmé.
- Comportement RAG si `should_use_rag` false en posture réflexive — besoin synopsis cours en playbook.
- Taille prompt agrégée (limite tokens) si nombreux items validés — plafond par groupe (ex. 8 items / 1500 car).

---

*Conception ancrée code juin 2026 — complète l’audit front formateur et le backlog P0 library.*
