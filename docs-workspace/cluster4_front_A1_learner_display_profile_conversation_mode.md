# Cluster 4 — Front A1 : exploitation `conversation_mode` et `learner_display_profile`

**Workspace :** `/Users/machin/Desktop/Zone de travail Hugo`  
**Date :** 2026-06-16  
**Statut :** implémenté (backend persistance + front A1)  
**Prérequis backend :** `cluster4_surface_contracts.md` — contrats UIState livrés et testés

---

## 1. Périmètre et principes

### 1.1 Objectif

Préparer l’exploitation **front** des champs cluster 4 dans le parcours **A1** (apprenant jeune, persona Karim), plus un **patch backend minimal de persistance** du `learner_display_profile` au niveau org/groupe.

### 1.2 Hors périmètre (ne pas rouvrir)

- Moteur, P0, orchestrateur, injection mémoire inter-sessions
- D9bis (`ConversationTurnLLMAnalysis`), mapping `EvaluationTrace`
- Correctifs cluster 3 (timeline tuteur) et cluster 4 (contrat UIState déjà vert)
- Sélecteur posture interactif complet (backlog UI — API `POST .../set-posture/` existe déjà)
- Rendu des 3 grammaires **adult** et **professional** au-delà du défaut actuel (priorité A1 = `youth`)

### 1.3 Sources mobilisées

| Document | Usage |
|----------|--------|
| `cluster4_surface_contracts.md` | Contrats JSON livrés |
| `cluster2_oracles_test_par_persona.md` | DSP-01..07, A1-08, INV-07/08 |
| `cluster2_matrice_runtime_vs_cible.md` | D2-M01 livré API ; D2-M08 partiel |
| `specs interface 2.0.md` | § profils d’affichage, UIState unique |
| `ecarts — 90_confidentialite_partage_multitenant_roles.md` | Frontières rôle × données |
| `ecarts — 110_interfaces_formateur_tuteur.md` | Tuteur/formateur ne configure pas encore le profil |

### 1.4 Règles impératives

- **Backend-first :** le front lit `GET /ui-state/` et dérive l’affichage ; pas de recalcul d’éligibilité CTA ni de posture.
- **Contrat JSON unique :** un seul schéma UIState ; les variantes `youth` / `adult` / `professional` ne modifient que le **rendu**, pas la forme de la réponse.
- **`gamification_profile` ≠ `learner_display_profile` :** engagement cosmétique A/B/C vs grammaire d’affichage (oracle INV-08).

---

## 2. Analyse front A1 — état réel

### 2.1 Chaîne de consommation UIState (parcours prod `/app`)

| Fichier | Rôle | Consomme `/ui-state/` ? |
|---------|------|------------------------|
| `hugo-hugolucia/frontend_1.8/src/views/ProdLearnerSessionView.vue` | Route session apprenant | Indirect (enveloppe) |
| `hugo-hugolucia/frontend_1.8/src/components/learner/ProdLearnerWorkspace.vue` | **Cœur A1** — fetch UIState, chat, CTA | **Oui** (`loadSessionUiState`) |
| `hugo-hugolucia/frontend_1.8/src/utils/engagementUiModel.js` | Projection UIState → modèle d’affichage | **Oui** (`buildDisplayModel`) |
| `hugo-hugolucia/frontend_1.8/src/components/learner/HugoProgressPanel.vue` | Rail scène, CTA synthèse/éval | Via `engagementModel` |
| `hugo-hugolucia/frontend_1.8/src/layouts/ProdLearnerLayout.vue` | Thème layout | Non (thème `gamification_profile` env) |
| `hugo-hugolucia/frontend_1.8/src/utils/frontendConfig.js` | Flags + `VITE_GAMIFICATION_PROFILE` | Paramètre requête uniquement |

**Point d’entrée unique à enrichir :** `ProdLearnerWorkspace.vue` → `loadSessionUiState()` + appels synthèse/évaluation qui repassent `gamification_profile` seul.

### 2.2 Champs UIState aujourd’hui exploités

- `scene_label`, `scene_progress`, `active_quest_label`, `quest_progress`, `maturity_color`
- `cta_synthesis`, `cta_evaluation` (via `buildSynthesisButtonFromCta` / `buildEvaluationButtonFromCta`)
- `persistent_objects`, `gamification_profile`
- Legacy : `synthesis_button_state`, `evaluation_button_state` (secondaires)

### 2.3 Champs cluster 4 **non exploités**

- `conversation_mode` — absent du front
- `learner_display_profile` — absent du front (ni en query param)

### 2.4 Logiques front à corriger (imitation / dérive)

| Emplacement | Comportement actuel | Risque |
|-------------|---------------------|--------|
| `ProdLearnerWorkspace.vue` — `phaseLabel(session.current_phase)` | Libellés scène dérivés de la **phase session** pendant le streaming | Parallèle implicite à `conversation_mode` / scène UIState ; source ≠ contrat produit |
| `ProdLearnerWorkspace.vue` — `productHeaderBadges` | Badge « Profil » = label **gamification** | Collision INV-08 ; masque le profil d’affichage |
| `engagementUiModel.js` — `GAMIFICATION_PROFILES` | Densité UI (barres, quêtes, maturité) pilotée par A/B/C | À **découpler** : cosmétique engagement vs grammaire `learner_display_profile` |
| `frontendConfig.js` — `VITE_GAMIFICATION_PROFILE` | Profil engagement figé au build | OK pour A/B/C ; ne doit pas porter `youth` |

**Décision design :** conserver `gamification_profile` pour le cosmétique engagement ; introduire une couche **`displayProfilePresets`** keyed par `learner_display_profile` pour densité de texte, visibilité des badges, et copy.

---

## 3. Design d’exploitation — `conversation_mode`

### 3.1 Contrat consommé (inchangé côté backend)

```json
{
  "conversation_mode": {
    "code": "diagnostic",
    "label": "Diagnostic",
    "can_switch": true,
    "switch_warning": null
  }
}
```

Source : `ConversationProgress.posture` — pas de lecture directe de `session.posture` côté front.

### 3.2 Emplacement UI proposé (A1 / `youth`)

| Zone | Composant | Rendu |
|------|-----------|--------|
| En-tête workspace | Nouveau bandeau `ConversationModeBanner.vue` | Pill : `conversation_mode.label` + icône posture |
| Sous le bandeau | Alerte conditionnelle | Si `switch_warning` non null → `alert-warning` texte verbatim du backend |
| Streaming | Remplacer `phaseLabel(session.current_phase)` | Pendant le stream : pill fixe « Hugo réfléchit… » + **pas** de relabeling local de phase ; après refresh UIState, reprendre `conversation_mode.label` |

**Format visuel A1 (`youth`) :**

```
[ Mode : Diagnostic ]     (pill, couleur neutre, pas de jargon « posture »)
```

Libellés affichés = **`conversation_mode.label` uniquement** (oracle A1-08). Pas de mapping local `diagnostic` → autre texte.

### 3.3 Comportement `can_switch` / `switch_warning` (sans sélecteur)

| Champ | Comportement front minimal |
|-------|---------------------------|
| `can_switch` | Si `true` : afficher un bouton secondaire désactivé ou lien « Changer de mode » avec tooltip « Bientôt disponible » **ou** masquer jusqu’au sprint sélecteur — **ne pas** appeler `set-posture` sans UX validée |
| `switch_warning` | Afficher tel quel dans une alerte non bloquante au-dessus du composer |
| `code` | Attribut `data-conversation-mode` pour tests e2e ; **ne pas** brancher de logique métier front |

### 3.4 Extension `engagementUiModel.js`

Ajouter au modèle retourné :

```javascript
conversationMode: {
  code: uiState.conversation_mode?.code || null,
  label: uiState.conversation_mode?.label || null,
  canSwitch: Boolean(uiState.conversation_mode?.can_switch),
  switchWarning: uiState.conversation_mode?.switch_warning || null,
}
```

Aucune inférence si `conversation_mode` absent → mode dégradé (`isDegraded` existant).

---

## 4. Design d’exploitation — `learner_display_profile`

### 4.1 Contrat consommé

- Valeur dans UIState : `youth` | `adult` | `professional`
- Query param supporté : `?learner_display_profile=youth` (override ponctuel, déjà backend)
- **Même JSON UIState** pour les trois valeurs (oracle DSP-04)

### 4.2 Matrice de rendu (couche présentation uniquement)

Nouveau fichier proposé : `frontend_1.8/src/utils/displayProfilePresets.js`

| Dimension | `youth` (A1) | `adult` | `professional` |
|-----------|--------------|---------|----------------|
| Densité texte hints / rail | Courte, phrases simples | Standard | Texte explicite (actuel) |
| `showProgressBar` | Oui, large | Oui | Selon `gamification_profile` |
| `showMaturityBadge` | Non (éviter jargon) | Optionnel | Selon gamification B/C |
| `showQuestLabel` | Oui, reformulation courte | Oui | Selon gamification |
| Icônes étapes rail | Oui (numéros + pictos) | Modéré | Sobriété actuelle |
| Badge header « Profil » | Renommer en **« Style »** ou masquer ; ne pas confondre avec mode | Idem | Idem |
| CTA labels | **Toujours** `cta_*.ui.button_label` backend | Idem | Idem |

**Règle de fusion :**  
`effectiveUiPreset = merge(displayProfilePresets[learner_display_profile], gamificationCosmetic[gamification_profile])`  
où le cosmétique ne peut **que** activer/désactiver des éléments déjà autorisés par le profil d’affichage (gamification ne crée pas de données métier).

### 4.3 Parcours A1 cible (`learner_display_profile=youth`)

1. ORGADMIN configure le groupe → `learner_display_profile=youth` (persistance §5)
2. Apprenant ouvre `/app/sessions/:id`
3. Front résout le profil : `query override` > `group.learner_display_profile` > `professional`
4. `GET /ui-state/?learner_display_profile=youth&gamification_profile=B` (exemple)
5. `buildDisplayModel` applique presets youth sur le **même** UIState
6. Bandeau mode + rail scène graphique + CTA inchangés côté logique (backend-driven)

### 4.4 Garantie contrat unique

- Interdiction d’appeler un second endpoint ou un schéma JSON par profil
- Les tests front vérifient que `buildDisplayModel` retourne les **mêmes clés métier** (`synthesisButton`, `evaluationButton`, etc.) quel que soit `learner_display_profile` ; seuls `show*` et copy wrappers diffèrent

---

## 5. Persistance `learner_display_profile` (org / groupe)

### 5.1 Modèle de données proposé (minimal)

**Niveau groupe (prioritaire — cohorte A1)** — modèle existant `referentials.Group` :

```python
learner_display_profile = models.CharField(
    max_length=32,
    choices=[
        ("youth", "Youth"),
        ("adult", "Adult"),
        ("professional", "Professional"),
    ],
    default="professional",
)
```

**Niveau organisation (optionnel, même migration ou suivante)** — modèle `accounts.Organisation` :

```python
default_learner_display_profile = models.CharField(...)  # même enum, défaut org
```

**Résolution backend (à implémenter dans `SessionUiStateView` / helper)** :

```
effective = normalize(
    request.query_params.learner_display_profile
    or session.group.learner_display_profile
    or session.organisation.default_learner_display_profile
    or "professional"
)
```

Le champ retourné dans UIState = `effective` (déjà le comportement query-only ; à étendre).

### 5.2 API (pas de nouvel endpoint dédié si possible)

| Opération | Route existante | Rôle autorisé |
|-----------|-----------------|---------------|
| Lire config groupe | `GET /groups/{id}/` | ORGADMIN, TRAINER (groupe), LEARNER (lecture seule du champ non sensible — **AVERIFIER** : lecture seule pour apprenant via session.group) |
| Écrire config groupe | `PATCH /groups/{id}/` | ORGADMIN, TRAINER selon `views_groups.py` |
| Lire défaut org | `GET /organisations/` ou détail | ORGADMIN |

**Alternative si permissions groupe trop larges :**  
`PATCH /groups/{id}/display-profile/` — vue dédiée 20 lignes, rôles `ORGADMIN | TRAINER`, audit log metadata-only.

### 5.3 Front — consommation persistance

| Étape | Fichier | Action |
|-------|---------|--------|
| 1 | `ProdLearnerWorkspace.vue` | Après `loadSession()`, `GET /groups/{session.group}/` → lire `learner_display_profile` |
| 2 | Store léger ou `ref` | `resolvedDisplayProfile` |
| 3 | `loadSessionUiState` | Passer `learner_display_profile: resolvedDisplayProfile` en query |
| 4 | Synthèse / évaluation POST | Même param dans body/query (aligné backend cluster 4) |
| 5 | `GroupAdminDetailView.vue` | Select « Profil d’affichage apprenant » → `PATCH` groupe |

### 5.4 Matrice rôle × visibilité (alignement ecarts 90 / 110)

| Rôle | Voit `conversation_mode` | Voit `learner_display_profile` | Peut configurer profil |
|------|--------------------------|--------------------------------|------------------------|
| LEARNER (A1) | Oui (son UIState) | Oui (son UIState) | Non |
| TUTOR | Non (pas d’accès ui-state apprenant) | Non | Non (CIBLE DSP-05 futur) |
| TRAINER / ORGADMIN | Non | Config groupe/org uniquement | Oui (PATCH groupe) |
| SUPERADMIN tech | Non contenu apprenant | Config plateforme `[CIBLE]` | Borné |

---

## 6. Plan de patchs

### 6.1 Front (`hugo-hugolucia/frontend_1.8/`)

| Fichier | Type de modification |
|---------|---------------------|
| `src/utils/displayProfilePresets.js` | **Créer** — presets youth/adult/professional |
| `src/utils/engagementUiModel.js` | **Modifier** — lire `conversation_mode`, `learner_display_profile` ; fusion presets ; exporter `conversationMode` |
| `src/utils/engagementUiModel.test.js` | **Enrichir** — cas youth + conversation_mode |
| `src/components/learner/ConversationModeBanner.vue` | **Créer** — pill + warning |
| `src/components/learner/ProdLearnerWorkspace.vue` | **Modifier** — query params, résolution profil groupe, intégrer bandeau, retirer `phaseLabel` pour l’affichage mode |
| `src/components/learner/HugoProgressPanel.vue` | **Modifier** — classes CSS `display-profile--youth` sur racine |
| `src/views/GroupAdminDetailView.vue` | **Modifier** — champ select + PATCH `learner_display_profile` |
| `src/style.css` (ou module dédié) | **Ajouter** — tokens visuels youth (espacement, taille police) |
| `src/utils/frontendConfig.js` | **Optionnel** — `VITE_LEARNER_DISPLAY_PROFILE` pour dev seulement ; pas pour prod A1 |

**Suppressions / interdits :**

- Ne pas mapper localement `posture` / `current_phase` vers des labels mode pédagogique
- Ne pas renommer `gamification_profile` en « profil apprenant » dans l’UI

### 6.2 Backend (`hugo_back/`) — persistance seule

| Fichier | Type de modification |
|---------|---------------------|
| `apps/referentials/models.py` | Champ `Group.learner_display_profile` |
| `apps/referentials/migrations/00xx_...py` | Migration |
| `apps/referentials/serializers.py` | Exposer champ dans `GroupSerializer` + validation enum |
| `apps/hugo/views_sessions.py` | `_resolve_learner_display_profile(request, session)` — cascade query > group > org |
| `apps/hugo/tests/test_cluster4_surface_contracts.py` | **Enrichir** — profil résolu depuis groupe sans query |
| `apps/referentials/tests/test_group_display_profile.py` | **Créer** — PATCH/GET ORGADMIN, isolation tenant |

**Ne pas modifier :** `ui_state_builder._build_conversation_mode` (déjà livré), CTA, mémoire, exports.

### 6.3 Documentation (post-implémentation)

| Fichier | Mise à jour légère |
|---------|-------------------|
| `cluster4_surface_contracts.md` | Section persistance + commandes pytest |
| `cluster2_matrice_runtime_vs_cible.md` | DSP-05/06 partiel si endpoint groupe livré |
| `ecarts — 110_interfaces_formateur_tuteur.md` | Choix profil formateur → PATCH groupe |

---

## 7. Garde-fous (checklist design)

| # | Garde-fou | Statut design |
|---|-----------|---------------|
| G1 | Front ne lit jamais `turn_state`, P0, `llm_request_payload` | Respecté si on supprime `phaseLabel` pour le mode |
| G2 | CTA synthèse/éval uniquement via `cta_synthesis` / `cta_evaluation` | Inchangé — `engagementUiModel` déjà conforme |
| G3 | Pas de second schéma UIState par profil | `displayProfilePresets` = CSS/visibilité seulement |
| G4 | `conversation_mode.label` affiché tel quel (A1-08) | Bandeau dédié |
| G5 | INV-08 : libellés UI distinguent engagement vs affichage | Renommer badges header |
| G6 | Nouveau PATCH groupe respecte `organisation_id` | Réutiliser `GroupRetrieveUpdate` existant |
| G7 | Apprenant ne reçoit pas de config admin dans UIState | Seulement `learner_display_profile` enum, pas de métadonnées org |

---

## 8. Tests recommandés

### 8.1 Front (Vitest)

```bash
cd hugo-hugolucia/frontend_1.8
npm test -- engagementUiModel.test.js
```

Cas à ajouter :

- UIState avec `conversation_mode` → `conversationMode.label` exposé
- `learner_display_profile=youth` → `showMaturityBadge === false`, hints courts
- `gamification_profile=C` + `youth` → CTA toujours issus de `cta_*`
- Absence de `conversation_mode` → dégradé sans crash

### 8.2 Backend (pytest)

```bash
cd hugo_back
.venv/bin/python -m pytest \
  apps/hugo/tests/test_cluster4_surface_contracts.py \
  apps/referentials/tests/test_group_display_profile.py \
  apps/hugo/tests/test_cluster3_oracles.py \
  -q
```

Cas persistance :

- Groupe `youth` → GET ui-state sans query → `learner_display_profile == youth`
- Query `professional` override groupe `youth` → `professional`
- ORGADMIN autre tenant → PATCH groupe → 404/403

### 8.3 Oracles à rejouer (réf. `cluster2_oracles_test_par_persona.md`)

| Oracle | Niveau après patch front + persistance |
|--------|----------------------------------------|
| INV-07 | SUCCÈS API + **SUCCÈS UI** si bandeau visible |
| INV-08 | SUCCÈS si badges distincts |
| DSP-01 | SUCCÈS contrat + **SUCCÈS rendu youth** (snapshot ou test composant) |
| DSP-04 | SUCCÈS — un seul contrat |
| DSP-05 | PARTIEL — config groupe ORGADMIN, pas cohorte multi-endpoint |
| A1-08 | SUCCÈS — label Diagnostic visible |

---

## 9. Séquencement recommandé

1. **Backend persistance** (migration Group + résolution cascade) — débloque le front sans query manuelle
2. **`displayProfilePresets.js` + `engagementUiModel.js`** — tests unitaires
3. **`ConversationModeBanner` + `ProdLearnerWorkspace`** — câblage query + bandeau
4. **`GroupAdminDetailView`** — configuration ORGADMIN
5. **Styles youth** — itération UX A1
6. **Sélecteur posture** — sprint ultérieur (utilise `can_switch` + `POST set-posture`)

---

## 10. Recommandation CTO

### Livrable après ce patch

- Parcours A1 **lit** le mode conversationnel depuis UIState (fini l’imitation `current_phase`)
- Parcours A1 **rend** une variante `youth` sur le même contrat JSON
- ORGADMIN **persiste** le profil d’affichage au niveau groupe
- Suite de tests front + backend reproductible sans manip humaine

### Reste CIBLE (volontairement reporté)

- Sélecteur posture interactif (`can_switch` → `set-posture`)
- Configuration profil par formateur sans passer par l’admin groupe (DSP-05 fin)
- Grammaires `adult` / `professional` différenciées au-delà du défaut actuel
- D9bis, EvaluationTrace

### Prochain move le plus rentable

**Démo A1** : configurer `learner_display_profile=youth` sur le groupe (ORGADMIN), ouvrir `/app/sessions/:id`, vérifier bandeau mode + presets youth + CTA backend-driven.

### Implémentation livrée (2026-06-16)

| Zone | Fichiers |
|------|----------|
| Backend persistance | `apps/referentials/models.py` + migration `0017`, `apps/accounts/models.py` + migration `0006` |
| Résolution cascade | `apps/hugo/services/ui_state_builder.py` → `resolve_learner_display_profile_for_session` ; `views_sessions.py` |
| Tests backend | `apps/hugo/tests/test_cluster4_surface_contracts.py` (+2 cas groupe / override) |
| Presets affichage | `frontend_1.8/src/utils/displayProfilePresets.js` |
| Modèle engagement | `frontend_1.8/src/utils/engagementUiModel.js` + tests |
| Bandeau mode | `frontend_1.8/src/components/learner/ConversationModeBanner.vue` |
| Workspace A1 | `frontend_1.8/src/components/learner/ProdLearnerWorkspace.vue` |
| Admin groupe | `frontend_1.8/src/views/GroupAdminDetailView.vue` |

**Décision retenue :** le champ groupe a `default="professional"` ; la cascade org ne s’applique que si le groupe n’a pas de valeur (chaîne `or` Python). En pratique, l’org sert de défaut documentaire ; le groupe reste la source opérationnelle pour les cohortes A1.

---

**Références :** `cluster4_surface_contracts.md` · `cluster2_oracles_test_par_persona.md` (§ DSP, A1-08, INV-07/08) · `cluster2_matrice_runtime_vs_cible.md` (§1.4–1.5) · `ecarts — 90_confidentialite_partage_multitenant_roles.md` · `ecarts — 110_interfaces_formateur_tuteur.md`
