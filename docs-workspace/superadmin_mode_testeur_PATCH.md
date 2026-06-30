# Patch — séparation raccourcis Mode testeur (dashboard superadmin)

**Date :** juin 2026  
**Référence analyse :** `docs-workspace/superadmin_mode_testeur_ANALYSE.md`  
**Option retenue :** C — deux raccourcis distincts + réorganisation `GroupView` via query `focus`

---

## Fichiers modifiés

| Fichier | Nature du changement |
|---------|---------------------|
| `hugo-hugolucia/frontend_1.8/src/views/DashboardView.vue` | Deux boutons (calibration / export) sur la carte bac pro melec |
| `hugo-hugolucia/frontend_1.8/src/views/GroupView.vue` | Hiérarchie conditionnelle selon `?focus=calibration` ou `?focus=exports` |
| `hugo-hugolucia/frontend_1.8/src/constants/demoReferenceGroup.js` | Helpers `groupCalibrationPath()` / `groupExportsPath()` |
| `hugo-hugolucia/frontend_1.8/tests_playwright/e2e/protocol/lot03-dashboard-demo.spec.ts` | Assertions sur les deux raccourcis et la hiérarchie cible |

---

## Comportement avant / après

### Avant

- Un seul bouton « Ouvrir le mode testeur » → `/group/:groupId`.
- Pour un superadmin, `GroupView` affichait en premier la carte **Exports Felix-ready (v1)** et les boutons CSV/JSON.
- Impression d’atterrir sur un outil Qualiopi/export alors que le libellé promettait la calibration encadrant.

### Après

- **Calibration encadrant** (bouton primaire, `data-testid="dashboard-tester-canonical"`) → `/group/:groupId?focus=calibration`.
  - Liste des apprenants en premier.
  - Exports repliables en bas (`<details>`), hors viewport initial.
- **Export audit (Felix-ready)** (bouton secondaire, `data-testid="dashboard-tester-exports"`) → `/group/:groupId?focus=exports`.
  - Carte exports et boutons CSV/JSON en tête de page (comportement export inchangé fonctionnellement).
- Les autres groupes du panneau « Autres groupes » ont aussi deux boutons compacts (Calibration / Exports).
- Accès direct à `/group/:id` sans query : liste apprenants d’abord, exports en `<details>` (même logique que `focus=calibration`).

---

## Routes finales choisies

| Raccourci | Route | Justification |
|-----------|-------|---------------|
| **Calibration encadrant** | `/group/:groupId?focus=calibration` | Réutilise la route mode testeur historique ; point d’entrée naturel = liste apprenants puis « Voir » → `LearnerSpace`. Pas de backend ni d’ID apprenant figé. |
| **Export audit Qualiopi lite / Felix-ready** | `/group/:groupId?focus=exports` | Même composant et mêmes appels `POST /exports/run/` ; query explicite pour remonter la zone export sans nouvelle page ni refonte admin. |

**Non retenu (pour ce patch minimal) :**

- Deep-link `/group/:id/learner/:id` — nécessiterait un apprenant démo stable ou un appel API supplémentaire au clic dashboard.
- `/groups-admin/:id` — exports déjà présents mais parcours admin plus lourd ; le besoin export est déjà couvert sur `GroupView`.

---

## Vérification locale attendue

1. Se connecter en `demo.superadmin` sur `/dashboard`.
2. Cliquer **Calibration encadrant** → URL avec `focus=calibration`, titre « Apprenants du groupe bac pro melec », liste visible, exports repliés en bas.
3. Retour dashboard → cliquer **Export audit (Felix-ready)** → URL avec `focus=exports`, carte « Exports Felix-ready (v1) » visible en haut.
4. Les exports CSV/JSON fonctionnent dans les deux contextes (replié ou proéminent).

---

## Limite restante

La calibration réelle (chat, traces, overrides) reste à **un clic supplémentaire** (« Voir » sur un apprenant → `/group/:gid/learner/:lid`). Ce patch corrige la confusion d’atterrissage, pas la profondeur du parcours encadrant.
