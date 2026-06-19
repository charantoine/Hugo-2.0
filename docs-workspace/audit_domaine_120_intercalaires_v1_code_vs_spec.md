# Audit domaine 120 — intercalaires pédagogiques V1 (code vs spec)

> **Date :** 2026-06-18  
> **Périmètre :** `hugo_back` + `hugo-hugolucia/frontend_1.8` (code applicatif Hugo cœur)  
> **Méthode :** recherche nominale exhaustive + inspection pipeline post-tour, contrats UIState, front apprenant ; confrontation avec `ecarts — 120_intercalaires_v1.md` et spec canonique.

---

## 1. Rappel du contrat cible minimal (domaine 120)

Les **intercalaires pédagogiques V1** sont une **capacité cible additive** de Hugo cœur : un appoint pédagogique **bref**, **passif**, **non interactif**, **non évaluatif**, visible **côté apprenant uniquement**, produit **côté backend** à partir d’artefacts structurés du moteur **après le tour principal** (idéalement post-persistance / async), **sans effet retour** sur le noyau P0 ni sur la décision tutorale.

Contraintes V1 :

- Typologie minimale : **`NONE`** (fréquent), **`NOTION`**, **`CONTRAST`** ;
- **Au plus un** intercalaire par tour ;
- **Débrayable par flag** ;
- Distinct de la réponse Hugo principale, des CTA terminaux, du RAG badge « Appui », et de toute branche d’évaluation.

---

## 2. Ce que dit la doc d’écarts actuelle

| Section | Synthèse |
|---------|----------|
| **00_rapport_ecarts** | Capacité **cadrée doctrinalement** ; **aucune preuve positive** d’un sous-système intercalaires actif dans les audits réel ; socle backend compatible (TurnState, UIState, mémoire, signaux). |
| **01_matrice_ecarts** | Majorité des lignes en **`ABSENT / NOUVEAU_CONTRAT`** (feature, producteur, composant, enum, endpoint) ; quelques **`ALIGNE`** / **`ALIGNE_DOC_PARTIEL`** sur garde-fous et socle architecture. |
| **02_decisions_documentaires** | Interdiction formelle de présenter le domaine comme **livré** ; `SessionInterstitial` = **nom conceptuel** uniquement ; pas de nom réel inventé. |
| **03_backlog_actions** | Priorité **P0_DOC → P1_CONTRAT → P2_PREP_TECH** avant tout code ; INT-011 = identifier point d’insertion pipeline (préparation, pas implémentation). |

**Formulation canonique (doc) :** capacité cadrée, **non observée comme feature livrée** dans Hugo cœur audité.

---

## 3. Observations dans le code

### 3.1. Noms / modèles / services (recherche nominale)

**Requêtes :** `interstitial`, `intercalaire`, `SessionInterstitial`, `NOTION`, `CONTRAST` (enum métier), `next-interstitial`, `prepareInterstitial`, fichiers `*Interstitial*`.

| Zone | Résultat |
|------|----------|
| `hugo_back/apps/**` | **0 occurrence** (hors dépendances `.venv`) |
| `hugo-hugolucia/frontend_1.8/src/**` | **0 occurrence** |
| Migrations Django | **0 table / champ** intercalaire |
| Tests pytest / Playwright | **0 test** domaine 120 |

**Occurrences hors code Hugo (non probantes) :**

- Docs `docs-workspace/*` (écarts, matrice, personae, handover) — **CIBLE / backlog** ;
- `Bibliothèque canonique de personae Hugo 2.0.md` — bloc JSON **conceptuel** (`Task async prepareInterstitialForNextTurn`, `GET .../next-interstitial`) marqué « à implémenter additivement » — **≠ code** ;
- `node_modules/playwright` — `interstitialHidden` (navigateur Chrome) — **sans lien**.

| Fichier | Symbole | Rôle réel | Lien domaine 120 |
|---------|---------|-----------|------------------|
| — | — | — | **Aucun symbole applicatif trouvé** |

**Conclusion 3.1 :** aucune implémentation nominale, même partielle ou déguisée sous un autre nom métier Hugo.

---

### 3.2. Points d’insertion pipeline (post-tour)

**Point d’insertion cible (spec) :** après génération réponse principale + persistance ; producteur additif async ; zéro effet retour P0/décision.

**Hooks post-tour réels observés** (`views_sessions.py`, orchestrateur) :

| Hook | Fichier / symbole | Rôle | Intercalaire V1 ? |
|------|-------------------|------|-------------------|
| `_post_conversation_hooks` | `views_sessions.py` L642-646 | `consolidate_session` + `record_session_signal` | **Non** — consolidation mémoire + signaux qualité persistés |
| `consolidate_session` | services mémoire | Mise à jour mémoire gouvernée intra-conversation | **Non** — domaine 20 |
| `record_session_signal` | `quality_tracker.py` | `ConversationQualitySignal` + `analytics_state` | **Non** — domaine 80, pas de payload apprenant |
| `persist_rag_citations` | `tracing.py` | Citations RAG sur message assistant | **Non** — domaine 30 |
| `build_turn_review_payload` | `tracing.py` | Trace interne / review | **Non** — diagnostic interne |
| Celery | `hugo/tasks.py` | **Seule tâche :** `recalc_learner_state` (post-validation trace) | **Non** — cache compétences tuteur |

**Absence constatée :**

- Pas de `@shared_task` / worker dédié intercalaire ;
- Pas de service `*interstitial*` ou `prepare_*_for_next_turn` ;
- Pas de hook post_save message produisant un artefact annexe apprenant.

**Conclusion 3.2 :** le pipeline post-tour existe et produit mémoire, signaux qualité et citations RAG — **aucun producteur d’intercalaire**.

---

### 3.3. Contrats de sortie (UIState / projections)

**Contrat apprenant exposé :** `GET /hugo/sessions/{id}/ui-state/` → `build_contract_ui_state` → `UIState` (`domain/conversation_profile.py`).

**Champs du contrat produit (`UIState`) :**

`scene_label`, `scene_progress`, `active_quest_label`, `quest_progress`, `maturity_color`, `synthesis_button_state`, `evaluation_button_state`, `evaluation_trigger_*`, `persistent_objects`, `gamification_profile`, `conversation_mode`, `learner_display_profile`, `cta_evaluation`, `cta_synthesis`.

→ **Aucun champ** `interstitial`, `intercalaire`, `pedagogical_insert`, `NOTION`, `CONTRAST`.

**Autres endpoints lus par le front apprenant :**

| Endpoint | Contenu pertinent | Intercalaire ? |
|----------|-------------------|----------------|
| `GET .../messages/` | `content`, `rag_citations` (compact) | **Non** — fil + RAG domaine 30 |
| `GET .../memory-summary/` | `session_memory`, `theme_memories` | **Non consommé front prod** ; pas structuré comme intercalaire inter-tour |
| `GET .../progress/` | `ConversationProgress` brut | **Non** — progression domaine 10 |

**Builder alternatif (interne / legacy) :** `build_ui_state` (`schemas.UiState`) inclut `session_memory`, `tutor_signals`, `symbolic_rewards`, `supporting_documents` — **non exposés** comme intercalaire ; `build_contract_ui_state` est le chemin prod apprenant.

#### Candidats « faux amis » — analyse vs contrat 120

| Artefact | Où | Passif ? | Non interactif ? | Non évaluatif ? | Apprenant-only ? | Inter-tour ? | Verdict |
|----------|-----|----------|------------------|-----------------|---------------|--------------|---------|
| **`rag_citations` / badge Appui** | Message assistant, `ProdLearnerWorkspace.vue` | Oui | Oui | Oui | Oui | Dans bulle réponse | **Sans lien 120** — domaine 30 |
| **`questionHints` / `prod-hints`** | Parse questions numérotées **dans** la réponse Hugo | — | Affichage seulement | Oui | Oui | Sous le fil | **Sans lien 120** — aide lecture réponse, pas appoint séparé backend |
| **`persistent_objects`** (UIState) | Panneau latéral « Traces et acquis » | Oui | Oui | Oui | Oui | Panneau session | **Base technique possible** — cartes fil actif / mémoire ; **pas** intercalaire (pas entre tours, pas typé NOTION/CONTRAST, pas producteur dédié) |
| **`conversation_mode.switch_warning`** | `ConversationModeBanner.vue` | Oui | Oui | Oui | Oui | Bandeau session | **Sans lien 120** — avertissement posture knowledge_review |
| **CTA `helper_text`** | `HugoProgressPanel.vue` | Oui | Oui (bouton séparé) | Non (lié éval) | Oui | Panneau progression | **Sans lien 120** — domaines 10/70 |
| **`symbolic_rewards`** | `engagementUiModel.js` (cosmétique) | Oui | Oui | Oui | Oui | Panneau latéral | **Sans lien 120** — gamification |
| **Streaming status** | Placeholder « Hugo analyse… » pendant génération | — | — | — | Oui | **Pendant** tour | **Sans lien 120** — UX streaming |
| **`pilotage` (timeline tuteur)** | `TutorLearnerView`, dashboard | Oui | Oui | Oui | **Non** (tuteur) | Timeline encadrant | **Sans lien 120** — domaine 60/110 |

**Conclusion 3.3 :** aucun champ UIState ou payload message ne porte aujourd’hui un intercalaire V1 ; des éléments passifs existent mais relèvent d’**autres domaines** ou d’**UX adjacente**, pas du contrat 120.

---

### 3.4. Front apprenant

**Composants inspectés :**

| Composant | Chemin | Rôle | Intercalaire V1 ? |
|-----------|--------|------|-------------------|
| `ProdLearnerWorkspace.vue` | `components/learner/` | Workspace prod `/app/session/:id` | **Non** |
| `ConversationModeBanner.vue` | idem | Mode conversationnel lecture seule | **Non** |
| `HugoProgressPanel.vue` | idem | Progression + CTA | **Non** |
| `ProdLearnerSessionView.vue` | `views/` | Shell session | **Non** |

**Recherche composants dédiés :** `InterstitialCard.vue`, `SessionInterstitial.vue`, `*Intercalaire*` → **inexistants**.

**Insertion entre messages :** le fil (`prod-thread`) enchaîne messages learner/assistant + placeholder streaming ; **aucun slot** pour bloc passif post-tour distinct de la bulle assistant.

**Flags front :** `frontendConfig.js` — `VITE_PERSISTENT_OBJECTS_ENABLED`, `VITE_SYMBOLIC_REWARDS_ENABLED`, etc. ; **aucun** `VITE_INTERSTITIAL*` ou équivalent.

**Conclusion 3.4 :** **aucun** proto partiel, **aucun** composant prévu non branché, **aucun** intercalaire V1 en service.

---

## 4. Relecture de la matrice d’écarts 120 (code vs statuts doc)

| Groupe matrice | Statut doc | Revu après audit code | Commentaire |
|----------------|------------|------------------------|-------------|
| Capacité additive V1 | ABSENT / NOUVEAU_CONTRAT | **Confirmé** | 0 feature |
| `SessionInterstitial` concept | A_VERIFIER | **Confirmé ABSENT code** ; concept doc seulement | Glossaire : pas de nom réel |
| Production post-tour | ABSENT / NOUVEAU_CONTRAT | **Confirmé** | Hooks existants ≠ producteur intercalaire |
| Async post-persistance | ALIGNE_DOC_PARTIEL | **Confirmé** | Celery présent ; **pas** de tâche intercalaire |
| Effet nul sur P0 / décision | ALIGNE_DOC_PARTIEL | **Confirmé** | Rien ne contredit ; rien à mesurer faute de feature |
| Composant apprenant passif | ABSENT / NOUVEAU_CONTRAT | **Confirmé** | |
| Non interactif / non évaluatif | ABSENT / NOUVEAU_CONTRAT | **Confirmé** (exigences cible) | |
| Apprenant-only | ABSENT / NOUVEAU_CONTRAT | **Confirmé** | |
| NONE fréquent / enum NOTION-CONTRAST | ABSENT / NOUVEAU_CONTRAT | **Confirmé** | Aucune enum code |
| 1 max / tour | ABSENT / NOUVEAU_CONTRAT | **Confirmé** | |
| Source = artefacts backend existants | ALIGNE | **Confirmé** | TurnState, progress, UIState, mémoire, signaux **présents** |
| Backend-first | ALIGNE | **Confirmé** | Architecture compatible |
| Appui UIState / projection | AMBIGU | **Confirmé AMBIGU** | UIState stable ; **aucun sous-champ** intercalaire ; rattachement futur non arbitré |
| Modèle / service / endpoint dédié | ABSENT / NOUVEAU_CONTRAT | **Confirmé** | |
| Présence démo | ABSENT / NOUVEAU_CONTRAT | **Confirmé** | |
| Flags runtime distants | A_VERIFIER | **Confirmé A_VERIFIER** | Aucun flag local `HUGO_*INTER*` ; Encoors non audité pour ce domaine |
| Confidentialité / multi-tenant | ALIGNE_DOC_PARTIEL | **Confirmé** | Garde-fous doc ; pas d’implémentation à auditer |

**Aucune ligne** ne passe de `ABSENT / NOUVEAU_CONTRAT` à `ALIGNE` ou `ALIGNE_DOC_PARTIEL` au sens « embryon intercalaire ».

**Seul affinage possible :** `persistent_objects` + pipeline `_post_conversation_hooks` pourraient être cités en **P2_PREP_TECH** (INT-011) comme **points d’ancrage futurs** — toujours **sans** requalifier en intercalaire livré.

---

## 5. Vérification des hypothèses doc

| Hypothèse (écarts / garde-fou) | Contredite par le code ? |
|--------------------------------|---------------------------|
| Pas de composant produit identifié comme intercalaire | **Non contredite — confirmée** |
| Pas de producteur backend | **Non contredite — confirmée** |
| Pas de champ UIState spécifique | **Non contredite — confirmée** |
| Pas de modèle / service / endpoint dédié | **Non contredite — confirmée** |

**Risque de sur-lecture corrigé par l’audit :**

- Ne **pas** appeler « intercalaires » : badges RAG, hints de questions, `persistent_objects`, bandeau mode, CTA helper, récompenses symboliques ;
- Ne **pas** inférer une feature depuis le JSON conceptuel personae (`Cluster_3_Intercalaires`) ;
- Ne **not** confondre signaux qualité persistés (`record_session_signal`) avec un appoint apprenant V1.

---

## 6. Conclusion opérationnelle

**Existe-t-il aujourd’hui une feature d’intercalaires V1 observable dans le code / produit Hugo cœur ?**

**Non.** L’audit code confirme intégralement la doc d’écarts : le domaine 120 reste une **capacité cible cadrée**, **sans implémentation active** détectée dans ce repo — ni explicite (noms, modèles, endpoints, composants), ni déguisée sous un autre nom métier Hugo.

**Socle technique déjà prêt pour un futur branchement (sans implémentation) :**

- Pipeline post-tour avec `_post_conversation_hooks` ;
- Artefacts structurés : `TurnState`, `ConversationDecision`, `ConversationProgress`, `UIState`, mémoire gouvernée, signaux qualité ;
- Front apprenant **backend-first** consommant `ui-state` ;
- Infrastructure Celery (extensible) ;
- Discipline multi-tenant et garde-fous confidentialité déjà en place sur les domaines voisins.

**Travaux à lancer (inchangés vs backlog INT-001 → INT-017) :**

1. **Documentaire / contractuel** (P0–P1) — contrat minimal, enum, point de projection UIState, flag off-by-default ;
2. **Préparation technique** (P2) — note d’insertion pipeline, schéma payload, critères NONE/NOTION/CONTRAST ;
3. **Code** (P3) — uniquement après arbitrage CTO ; producteur additif + composant passif apprenant.

**Formulation finale :**

> Le domaine 120 reste **capacité cible sans implémentation active** dans Hugo cœur audité. Les travaux à lancer sont **d’abord documentaires et contractuels** (INT-001–INT-010), puis préparation technique (INT-011–INT-017), **avant tout chantier code**. Aucune mise à jour de statut « livré » n’est justifiée par le code actuel.

---

## Sources mobilisées

- `docs-workspace/ecarts — 120_intercalaires_v1.md` (00–03)
- `docs-workspace/glossaire_alignement_hugo_reel_vs_spec.md` (SessionInterstitial)
- `docs-workspace/cluster2_matrice_runtime_vs_cible.md` § domaine 120
- Code : `hugo_back/apps/hugo/views_sessions.py`, `services/ui_state_builder.py`, `services/quality_tracker.py`, `tasks.py`, `domain/conversation_profile.py` ; `frontend_1.8/src/components/learner/ProdLearnerWorkspace.vue`

**A_VÉRIFIER (hors périmètre code local) :** variante Encoors / flag distant portant un artefact proche — **aucune preuve** dans ce repo ; INT-022 backlog.
