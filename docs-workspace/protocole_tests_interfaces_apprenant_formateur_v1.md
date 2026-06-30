# Protocole de tests interfaces apprenant + formateur (post‑cluster 15)

Workspace : `.../Zone de travail Hugo`  
Version : 1.1 — campagne post‑cluster 15  
Environnement : **local**  
Branche cible : branche contenant les implémentations cluster 15 (`feature/cluster15-interfaces-apprenant-formateur` ou équivalent)

## 0. Objectifs

- Vérifier en runtime local que les nouvelles fonctions front (sélecteur de posture, profils d’affichage, panneau mémoire apprenant, workflows formateur) respectent :
  - la doctrine backend‑first, UIState comme unique source UI,
  - les garde-fous de confidentialité,
  - les comportements attendus par persona.
- S’appuyer sur les oracles `cluster2_oracles_test_par_persona.md` et les tests pytest cluster 15.

Résultat attendu : exécution reproductible (pytest + parcours UI manuels) couvrant **A1, A2, A3, C1**.

### Entrées campagne (à renseigner avant démo)

| Variable | Valeur |
|----------|--------|
| ENVIRONMENT | `local` |
| BRANCH | branche cluster 15 |
| SESSION_IDS_DEMO | 2–3 UUID sessions démo (voir fixtures ou Encoors) |
| PERSONAE_CIBLES | `A1, A2, A3, C1` |

**SESSION_IDS_DEMO (placeholders — remplacer)** :

- A1 youth : `00000000-0000-4000-8000-000000000001`
- A2 adult : `00000000-0000-4000-8000-000000000002`
- A3 professional : `00000000-0000-4000-8000-000000000003`

---

## 1. Personae cibles et surfaces testées

| Persona | Rôle | Profil affichage | Surface | Fonctions cluster 15 |
|---------|------|------------------|---------|----------------------|
| **A1** Karim | LEARNER | `youth` | `/app/session/:id` | Posture, profil youth, mémoire |
| **A2** Nadège | LEARNER | `adult` | `/app/session/:id` | Profil adult, mémoire, posture |
| **A3** Ibrahima | LEARNER | `professional` | `/app/session/:id` | Profil pro, CTA synthèse/éval |
| **C1** Amélie | TRAINER | — | `/app/trainer/knowledge`, `/app/trainer/elicitation` | Validation, élicitation, usage |

---

## 2. Oracles API par persona (cluster 15)

### 2.1 A1 — Karim (youth)

**Champs UIState** : `conversation_mode`, `learner_display_profile`, `cta_synthesis`, `cta_evaluation`, `maturity_color`, `scene_label`.

**Endpoints** :

- `GET /hugo/sessions/{id}/ui-state/`
- `POST /hugo/sessions/{id}/set-posture/`
- `GET /hugo/sessions/{id}/memory-summary/`
- `POST /hugo/sessions/{id}/request-synthesis/` (si eligible)
- `POST /hugo/sessions/{id}/request-evaluation/` (si eligible)

**Oracles cluster 15** :

1. `learner_display_profile === youth` (groupe ou query param).
2. `conversation_mode.label` = « Diagnostic » si posture diagnostic.
3. `set-posture` : 200 si transition autorisée ; 400 `transition_not_allowed` si diagnostic → knowledge_review.
4. `memory-summary` : `session_memory.memory_scope === intra_conversation` ; pas de verbatim message brut.
5. CTA : boutons disabled/labels cohérents avec `cta_*` (pas de recalcul front).

**Tests pytest** : `test_cluster15_interfaces_apprenant.py` — préfixe `test_a1_*`.

### 2.2 A2 — Nadège (adult)

**Oracles cluster 15** :

1. Même jeu de clés UIState que A1/A3 ; seule `learner_display_profile === adult` change.
2. `gamification_profile` et `learner_display_profile` indépendants.
3. Après `set-posture`, `ui-state.conversation_mode.code` aligné sur `session.posture`.
4. Panneau mémoire : champs structurés (`facts_confirmed`, `open_points`) sans `turn_state`.

**Tests pytest** : préfixe `test_a2_*`.

### 2.3 A3 — Ibrahima (professional)

**Oracles cluster 15** :

1. `learner_display_profile === professional` par défaut.
2. CTA évaluation `eligible` + `button_disabled === false` en maturité GREEN.
3. CTA synthèse bloquée en RED quel que soit le profil.
4. `POST request-evaluation` → 400 `evaluation_not_eligible` si CTA non eligible.
5. UIState sans champs P0 (INV-01).

**Tests pytest** : préfixe `test_a3_*`.

### 2.4 C1 — Amélie (formatrice)

**Endpoints** :

- `GET /hugo/trainer/knowledge-items/`
- `POST /hugo/trainer/knowledge-items/{id}/validate/` (`validate`, `reject`, `mark_provisional`, `edit`)
- `GET /hugo/trainer/referential-items/{id}/elicitation-questions/`
- `POST /hugo/trainer/referential-items/{id}/elicitation-answers/`
- `POST /hugo/trainer/documents/ingest/` (optionnel V0)

**Champs usage** : `usage_stats.exploitable`, `usage_stats.usage_note`, `usage_stats.usage_count` (null tant que RAG non tracé).

**Oracles cluster 15** :

1. Validate → `validated_trainer` persisté.
2. Provisoire → `derived_provisional` ; reject → item supprimé.
3. Élicitation → items `declared`, `source_type === dialogue_elicited`.
4. Aucun verbatim apprenant dans les réponses trainer.
5. LEARNER → 403 sur endpoints trainer.

**Tests pytest** : `test_cluster15_interfaces_formateur.py` — préfixe `test_c1_*`.

---

## 3. Commandes pytest (local)

```bash
cd hugo_back

# Campagne apprenant (A1, A2, A3)
python -m pytest apps/hugo/tests/test_cluster15_interfaces_apprenant.py -v

# Campagne formateur (C1)
python -m pytest apps/hugo/tests/test_cluster15_interfaces_formateur.py -v

# Campagne complète cluster 15 + régressions proches
python -m pytest \
  apps/hugo/tests/test_cluster15_interfaces_apprenant.py \
  apps/hugo/tests/test_cluster15_interfaces_formateur.py \
  apps/hugo/tests/test_cluster4_surface_contracts.py \
  apps/hugo/tests/test_memory_summary_smoke.py \
  apps/hugo/tests/test_posture_modes.py \
  -v
```

---

## 4. Scénarios UI par persona (check-lists manuelles)

> Utiliser un compte / groupe configuré avec le bon `learner_display_profile`.  
> URL apprenant : `/app/session/{SESSION_ID}` · formateur : `/app/trainer/knowledge`.

### 4.1 A1 — Karim (youth) — `/app/session/:id`

| # | Point de contrôle | Attendu | KO si |
|---|-------------------|---------|-------|
| A1-UI-01 | Bandeau mode conversationnel | Label posture visible (ex. « Diagnostic ») + micro-copie courte | Bandeau absent ou label vide |
| A1-UI-02 | Sélecteur posture | `<select>` visible **uniquement** si backend `can_switch=true` | Sélecteur toujours visible ou absent alors que `can_switch=true` |
| A1-UI-03 | Changement posture | Choisir un mode autorisé → label mis à jour après reload UIState | Erreur silencieuse ou label incohérent |
| A1-UI-04 | Erreur transition | Transition interdite → message d’erreur lisible (pas de crash) | 400 non géré ou posture affichée incorrecte |
| A1-UI-05 | Profil youth | Coins arrondis plus marqués (`prod-workspace--youth`), typo plus généreuse | Même rendu que professional sans raison |
| A1-UI-06 | Panneau « Mémoire du fil » | Section latérale : thème, points explorés/ouverts | Verbatim chat recopié ; `theme_memories` inter-session affichés |
| A1-UI-07 | CTA synthèse / évaluation | États boutons = UIState (`disabled`, labels, helper) | Bouton actif alors que CTA backend disabled |
| A1-UI-08 | Confidentialité | Aucun bloc « turn_state », P0, diagnostic interne | Champ technique visible |

### 4.2 A2 — Nadège (adult) — `/app/session/:id`

| # | Point de contrôle | Attendu | KO si |
|---|-------------------|---------|-------|
| A2-UI-01 | Profil adult | Classe `prod-workspace--adult` ; densité intermédiaire (ni youth maximal ni pro minimal) | Profil youth ou pro par erreur |
| A2-UI-02 | Même structure écran | Progression + conversation + mémoire présents comme A1 | Composants manquants vs A1 |
| A2-UI-03 | Panneau mémoire | Contenu structuré ; bouton Actualiser fonctionne | Erreur persistante ou liste brute messages |
| A2-UI-04 | Posture réflexif → savoirs | Si autorisé : bascule vers « Savoirs / révision » | Transition autorisée backend mais UI bloquée |
| A2-UI-05 | Quête / objectif | Texte `active_quest_label` ou équivalent visible si profil B/C | — (non bloquant si flag off) |

**Différence vs A1** : rendu visuel adult (espacements/titres) ; même logique métier backend.

### 4.3 A3 — Ibrahima (professional) — `/app/session/:id`

| # | Point de contrôle | Attendu | KO if |
|---|-------------------|---------|-------|
| A3-UI-01 | Profil professional | `prod-workspace--professional` ; texte plus compact/explicite | Profil youth par défaut sans config groupe |
| A3-UI-02 | CTA synthèse (session mature) | Bouton actif si `synthesis_eligible` ; helper si présent | Incohérence avec GET ui-state |
| A3-UI-03 | CTA évaluation (GREEN) | « Demander une évaluation » actif si eligible | Clic possible alors que POST renverrait 400 |
| A3-UI-04 | CTA bloqué (RED) | Boutons disabled + message/helper explicatif | Boutons cliquables en RED |
| A3-UI-05 | Panneau mémoire | Présent ; lecture seule | Édition mémoire côté apprenant |
| A3-UI-06 | Posture knowledge_review | Label « Savoirs / révision » ; warning si maturité faible | Warning backend absent en UI |

**Différence vs A1/A2** : priorité lisibilité textuelle ; scénario CTA GREEN prioritaire pour démo.

### 4.4 C1 — Amélie (formatrice) — `/app/trainer/*`

#### Liste — `/app/trainer/knowledge`

| # | Point de contrôle | Attendu | KO si |
|---|-------------------|---------|-------|
| C1-UI-01 | Tableau items | Colonnes : contenu, type, statut, dates, validé par, usage | Liste minimaliste sans statut |
| C1-UI-02 | Filtre statut | Filtre declared / provisoire / validé fonctionne | Filtre sans effet |
| C1-UI-03 | Valider | Item → statut « Validé formateur » ; colonne usage « exploitable » | Statut inchangé |
| C1-UI-04 | Provisoire | Item declared → « Provisoire » | Action absente ou erreur |
| C1-UI-05 | Rejeter | Motif saisi → item disparaît de la liste | Item reste sans feedback |
| C1-UI-06 | Éditer + valider | Contenu corrigé puis validé | Validation sans relecture |
| C1-UI-07 | Usage | Note lecture seule ; pas de verbatim apprenant | Données apprenant visibles |
| C1-UI-08 | Accès rôle | Seul TRAINER (ou orgadmin) accède | LEARNER peut ouvrir la page |

#### Atelier — `/app/trainer/elicitation`

| # | Point de contrôle | Attendu | KO if |
|---|-------------------|---------|-------|
| C1-UI-09 | Démarrage atelier | Saisie référentiel + chargement questions | Écran vide sans questions |
| C1-UI-10 | Réponses | Submit → redirection liste ; items `declared` | Items validés auto sans humain |
| C1-UI-11 | Ingest document | Chemin serveur optionnel ; message succès/erreur | Upload client non géré silencieux |
| C1-UI-12 | Confidentialité | Aucune session apprenant / verbatim dans l’atelier | Fil apprenant visible |

#### Tableau récap — différences profils apprenant (A1 / A2 / A3)

| Élément | A1 youth | A2 adult | A3 professional |
|---------|----------|----------|-----------------|
| Classe racine | `prod-workspace--youth` | `prod-workspace--adult` | `prod-workspace--professional` |
| Rayons panneaux | Plus arrondis (22px) | Intermédiaire (18px) | Plus sobres (16px) |
| Densité texte | Plus aérée, copy youth | Équilibrée | Plus compacte |
| Logique CTA / posture | **Identique** (UIState) | **Identique** | **Identique** |
| Panneau mémoire | Oui (session_memory) | Oui | Oui |

---

## 5. Critères de clôture campagne

- [x] Tous les tests `test_cluster15_interfaces_*.py` PASS en local (2026-06-18).
- [x] Campagne consolidée 90 tests PASS — voir `rapport_mise_a_jour_doc_post_tests_2026-06-18.md`.
- [ ] Check-lists §4 validées pour au moins 1 session par persona (A1, A2, A3, C1) — **manuel restant**.
- [ ] Aucune fuite verbatim / P0 constatée en UI — **à confirmer en démo**.
- [ ] Captures ou notes datées pour SESSION_IDS_DEMO réels.

---

## 6. Références

- `cluster15_interfaces_apprenant_formateur_resultats.md`
- `cluster16_interface_apprenant_spec_conformite_resultats.md`
- `cluster16_protocole_tests_interface_apprenant_v1.md`
- `cluster16_interface_apprenant_resultats_tests.md`
- `rapport_mise_a_jour_doc_post_tests_2026-06-18.md`
- `rapport_mise_a_jour_doc_post_cluster16_2026-06-18.md`

---

## 7. Statut post-cluster 16 (2026-06-18)

| Scénario | Couverture auto | Reste manuel |
|----------|-----------------|--------------|
| Posture API (A1-07) | cluster 15/16 backend B16-P | — |
| Posture UI (A1-08) | Playwright U16-S1 | S16-A2 verrou séance avancée |
| Mémoire panneau (A1-05) | B16-M*, U16-S3 | — |
| Profils youth/adult/pro (A2/A3) | U16-P1/P2 E2E | S16-A4/A5 ressenti UX |
| CTA advisory | B16-C2 backend | S16-A3 + U16-S2b Playwright dédié |
| Formateur C1 | cluster 15 (21 tests) | check-lists §4 C1-UI |

- `cluster2_oracles_test_par_persona.md`
- `cluster2_matrice_runtime_vs_cible.md` (domaines 10, 20, 31, 70, 110)
- Tests : `test_cluster15_interfaces_*.py`, `test_cluster16_interface_apprenant_backend.py`
