# Analyse — bloc « Mode testeur » dashboard superadmin vs perception export Qualiopi

**Date :** juin 2026  
**Périmètre :** analyse uniquement — **aucune modification de code**  
**Instance de référence :** `http://localhost:5173`, mode `tester`, org **Demo Hugo Org**, groupe **bac pro melec**

---

## Sources mobilisées

| Source | Usage |
|--------|--------|
| `hugo-hugolucia/frontend_1.8/src/views/DashboardView.vue` | Bloc UI + handler bouton |
| `hugo-hugolucia/frontend_1.8/src/constants/demoReferenceGroup.js` | Intention « bac pro melec » / route testeur |
| `hugo-hugolucia/frontend_1.8/src/views/GroupView.vue` | Page d’atterrissage réelle |
| `hugo-hugolucia/frontend_1.8/src/views/LearnerSpaceView.vue` + `LearnerDetailView.vue` | Calibration encadrant (profondeur) |
| `hugo-hugolucia/frontend_1.8/src/router/index.js` | Routes nommées |
| `docs-workspace/03_ETAT_PRODUIT_REEL.md` §6 | Mode testeur documenté |
| `docs-workspace/09_PARCOURS_DEMO_ET_SCENARIOS.md` §S6, §S8 | Séparation raccourci démo / admin |
| `docs-workspace/VERIF_COHERENCE_SUPERADMIN_2026-06-26.md` | Séparation wizard vs raccourci démo |
| `docs-workspace/ecarts — 100_exports_preuves_qualiopi_lite.md` | Exports Felix / Qualiopi lite |
| `docs-workspace/cluster2_encadrants_roles_audit_reel_vs_cible.md` | Exports visibles selon rôle |
| E2E `lot03-dashboard-demo.spec.ts` + audit `audit_admin_ui_runtime_full.mjs` | Preuve routing `/group/:id` |

---

## 1. Localisation du code

### 1.1 Page d’accueil superadmin

| Élément | Fichier | Lignes / détail |
|---------|---------|-----------------|
| Vue tableau de bord | `src/views/DashboardView.vue` | Route `/dashboard` (`router/index.js` L65-68) |
| Section « Mode testeur » | `DashboardView.vue` L78-134 | Titre, texte d’intro, carte bac pro melec, bouton canonique |
| Constante groupe démo | `src/constants/demoReferenceGroup.js` | `REFERENCE_GROUP_NAME = 'bac pro melec'` ; `findReferenceGroup()` |
| Résolution du groupe | `DashboardView.vue` L40, L87-107 | `GET /groups/` au montage ; recherche par nom (pas par ID fixe en UI) |
| Bouton « Ouvrir le mode testeur » | `DashboardView.vue` L96-104 | `data-testid="dashboard-tester-canonical"` |
| Handler clic | `DashboardView.vue` L36-38 | `openGroup(group)` → `router.push({ name: 'Group', params: { groupId: group.id } })` |

**Backend direct :** aucun handler dédié au clic. Seul appel amont : `GET /groups/` pour peupler la liste et trouver `bac pro melec`.

### 1.2 Libellés affichés (runtime)

| Zone | Texte exact (template) |
|------|------------------------|
| Titre section | « Mode testeur » |
| Intro | « Raccourci de démonstration pour la calibration encadrant (hors parcours d’onboarding admin). Cible par défaut : **bac pro melec**. » |
| Sous-bloc | « Raccourci démo — cohorte préconfigurée pour les tests encadrant. » |
| Bouton | « Ouvrir le mode testeur » |

Commentaire dans `demoReferenceGroup.js` L23-25 :

> Route mode testeur (`GroupView` legacy / calibration encadrant).

---

## 2. Intention initiale probable

### 2.1 Ce que le wording et l’architecture suggèrent

**Réel confirmé (code + doc interne) :**

Le bloc « Mode testeur » a été **volontairement séparé** du wizard d’onboarding admin (juin 2026). Il sert de **raccourci de démonstration** vers une cohorte métier connue (**bac pro melec**), pas de pivot du parcours IAM (`VERIF_COHERENCE_SUPERADMIN_2026-06-26.md`, `WIZARD_ORG_GROUP_UPDATE_2026-06-26.md`).

L’intention métier probable, pour un **encadrant** (tuteur / formateur / équipe technique) :

1. **Choisir rapidement** le groupe de démo Bac Pro MELEC (données melec, RNCP38878, apprenants `apprenant_melec_*` si présents).
2. **Accéder à la liste des apprenants** du groupe en layout **testeur** (`TesterLayout`).
3. **Ouvrir l’espace apprenant de calibration** : chat sans masquage prod, traces, preuves, documents, overrides phase/classifieur, debug P0 optionnel — via `LearnerDetailView` / `TutorLearnerView` (`03_ETAT_PRODUIT_REEL.md` §6).

Ce n’est **pas** le parcours produit `/app` (apprenant en `prod_showable`). C’est l’**atelier de calibration** historique du POC, conservé sous le nom « mode testeur ».

### 2.2 Rôle de bac pro melec et RNCP38878

| Élément | Intention probable | Source |
|---------|-------------------|--------|
| **bac pro melec** | Cohorte de référence locale pour démos encadrant et audits UI (7+ membres observés en runtime) | `demoReferenceGroup.js` ; audits 26/06 ; `11_FICHE_COMPTES_ET_DONNEES_DEMO.md` |
| **RNCP38878** | Référentiel métier MELEC rattaché au groupe (parcours onboarding étape référentiel) | `demo-env.ts` ; scripts `restore_rncp38878_smoke.py` ; wizard / `/group/:id/referential` |
| **Séparation wizard** | Le wizard admin est **généralisé** (org + groupe choisi) ; le dashboard garde un **raccourci démo** explicite vers bac pro melec | `VERIF_COHERENCE_SUPERADMIN_2026-06-26.md` |

### 2.3 Ce que le bloc ne devait probablement pas signifier

D’après la doc produit et les scénarios démo (`09` §S6, §S8) :

- Ce n’est **pas** l’entrée onboarding superadmin (comptes → groupes → profils → référentiel) → c’est la section **Administration** + `/admin/onboarding`.
- Ce n’est **pas** un libellé pour l’export audit Qualiopi / Felix en tant qu’action principale — les exports sont un **domaine adjacent** (artefacts métier, traçabilité), visible surtout pour ORGADMIN/SUPERADMIN (`ecarts — 100`).

**Hypothèse de conception initiale :**  
« Ouvrir le mode testeur » = **voir les apprenants du groupe démo et entrer en calibration** (timeline, chat, réglages), pas **télécharger un export CSV/JSON** pour un auditeur Qualiopi.

---

## 3. État actuel du routing

### 3.1 Chaîne technique complète

```text
/dashboard
  └─ clic « Ouvrir le mode testeur » (dashboard-tester-canonical)
       └─ router.push({ name: 'Group', params: { groupId } })
            └─ URL : /group/{uuid}     ← ex. /group/29e5cdb9-de89-49b3-a36e-53b4b9bbbc50
                 └─ composant : GroupView.vue
                      └─ clic « Voir » sur un apprenant
                           └─ router.push({ name: 'LearnerSpace', ... })
                                └─ URL : /group/{gid}/learner/{lid}
                                     └─ LearnerSpaceView.vue
                                          ├─ LearnerDetailView (si soi-même)
                                          └─ TutorLearnerView (si autre apprenant)
```

| Étape | Route nommée | URL type | Composant |
|-------|--------------|----------|-----------|
| Dashboard | `Dashboard` | `/dashboard` | `DashboardView.vue` |
| Atterrissage bouton | `Group` | `/group/:groupId` | `GroupView.vue` |
| Calibration réelle | `LearnerSpace` | `/group/:groupId/learner/:learnerId` | `LearnerSpaceView.vue` |

**Preuves automatisées :**

- E2E `lot03-dashboard-demo.spec.ts` : clic → URL match `/group/`, **pas** `/admin/onboarding`.
- Audit `audit_admin_ui_runtime_full.mjs` L122-131 : attend `/group/{REFERENCE_GROUP_ID}`.

**Le bouton ne pointe pas vers :**

- `/groups-admin/:id` (admin cohorte + accordéons expert + exports) ;
- `/referentials` ou bundle Qualiopi dédié ;
- `/app/tutor` (surface tuteur produit).

### 3.2 Contenu de la page d’atterrissage (`GroupView.vue`)

Pour un **superadmin** connecté (`auth.isOrgAdminLike === true`) :

| Zone (ordre à l’écran) | Contenu | Endpoint si action |
|------------------------|---------|-------------------|
| **1 — En-tête** | Titre « Apprenants du groupe bac pro melec » | — |
| **2 — Boutons header** | « CSV principal (Felix-ready) », « JSON trace_rich_v1 », « Configurer le référentiel » | `POST /exports/run/` via `runExportAndDownload()` |
| **3 — Carte exports** | « Exports Felix-ready (v1) » + filtres période + aide CSV/JSON | idem |
| **4 — Liste** | Apprenants + bouton « Voir » / « Mon espace » | `GET /dashboard/groups/{id}/learners/` |

Pour un **tuteur** (non `isOrgAdminLike`) : les blocs exports (2 et 3) sont **masqués** (`v-if="canRunExports"`). La page ressemble davantage à une liste d’apprenants — plus cohérente avec le libellé « tests encadrant ».

**Constat :** il n’existe **aucune page front nommée « Qualiopi »**. La perception « page d’export Qualiopi » vient du **dominant visuel** pour le superadmin : carte **Exports Felix-ready** et libellés **trace_rich_v1** / **CSV principal**, vocabulaire du domaine **exports / preuves / Qualiopi lite** (`ecarts — 100`).

### 3.3 Lien avec Qualiopi / audit (backend)

| Artefact | Rôle | Visible sur `/group/:id` ? |
|----------|------|----------------------------|
| `POST /exports/run/` | Export CSV ou JSON `trace_rich_v1` (pivot traces × items) | Oui — boutons + carte (superadmin) |
| Bundle Qualiopi lite | ZIP métadonnées / traces (`quality/qualiopi/…` côté back) | **Non** exposé comme page dédiée depuis ce bouton |
| `LearnerDetailView` | Chat calibration, traces, evidence, partage | **Non** — un clic « Voir » supplémentaire |

Le parcours export est donc **adjacent** au mode testeur (même layout tester, même groupe), mais **pas** la destination nommée dans le handler du bouton. C’est une **collision de surfaces** sur `GroupView` pour les rôles admin.

---

## 4. Divergence UX / technique

### 4.1 Texte annoncé vs première impression à l’arrivée

| Dimension | Ce que dit le bloc dashboard | Ce que voit le superadmin en arrivant sur `/group/:id` |
|-----------|------------------------------|------------------------------------------------------|
| Intention affichée | Calibration **encadrant**, cohorte **tests encadrant** | **Exports Felix-ready (v1)** en carte proéminente |
| Action principale suggérée | « Ouvrir le **mode testeur** » | Boutons **CSV / JSON** en haut de page |
| Public cible implicite | Tuteur / formateur qui pilote un apprenant | Responsable **audit / données** (ORGADMIN, auditeur Qualiopi) |
| Profondeur | Une action | Calibration réelle à **deux clics** (liste → Voir apprenant) |

**Verdict :** le **routing est techniquement aligné** avec l’intention historique (`/group/:id` = entrée mode testeur). La **hiérarchie visuelle et le rôle superadmin** créent une **divergence vécue** : on atterrit sur un **écran d’export traçabilité**, pas sur un **écran de calibration encadrant**.

### 4.2 Asymétrie par rôle (facteur aggravant)

| Rôle | Exports visibles sur `GroupView` | Lecture du libellé « mode testeur encadrant » |
|------|----------------------------------|-----------------------------------------------|
| SUPERADMIN / ORGADMIN | Oui — carte + boutons | **Incohérent** — ressemble à un outil audit |
| TUTOR / TRAINER (si accès) | Non (`canRunExports` false) | **Plus cohérent** — liste apprenants d’abord |

Source : `GroupView.vue` L21, L110-152 ; `cluster2_encadrants_roles_audit_reel_vs_cible.md` (écart permissions exports front/back).

### 4.3 Risques métier

**Pour l’encadrant (tuteur / formateur)**  
- Peut ne jamais utiliser le raccourci s’il se connecte en superadmin pour tester.  
- Confusion entre « tester la conduite d’un apprenant » et « extraire des fichiers pour un audit ».

**Pour le responsable Qualiopi / ORGADMIN**  
- Peut croire que le raccourci dashboard est **l’entrée officielle export** — alors que l’export existe aussi sur `/groups-admin/:id` (accordéon expert) avec contexte admin plus complet.  
- Double entrée export (testeur vs admin) non harmonisée dans les libellés.

**Pour le superadmin**  
- Le bloc est présenté comme **hors onboarding** (correct) mais mène à une page où l’**export domine** l’**exploration apprenant** — contraire au message « calibration encadrant ».

### 4.4 Écart routing vs écart perception

| Type | Gravité | Description |
|------|---------|-------------|
| **Routing nominal** | Faible | Le code ouvre bien `/group/:id`, pas une URL export isolée |
| **Routing métier** | Moyen | La « vraie » calibration est `/group/:id/learner/:id` ; le bouton s’arrête un niveau au-dessus |
| **Perception Qualiopi** | Élevé | Superadmin voit d’abord Felix-ready / trace_rich_v1 = domaine audit, pas encadrant |
| **Cohérence libellé** | Élevé | « Mode testeur encadrant » ≠ première action proposée (export CSV) |

---

## 5. Options de correction (non implémentées)

### Option A — Recâbler vers une vraie entrée « calibration encadrant »

**Principe :** le bouton mène directement à l’expérience encadrant, pas à la coque `GroupView` orientée export.

**Pistes (existant uniquement) :**

- Atterrir sur `/group/:id/learner/:learnerId` du **premier apprenant** de la cohorte (ou dernier actif) — composant `TutorLearnerView` / `LearnerDetailView`.
- Ou garder `/group/:id` mais **masquer / replier** la carte exports pour le parcours issu de `dashboard-tester-canonical` (query `?tester=1` ou état navigation).

**Pour :** alignement immédiat texte → action pour superadmin et encadrants.  
**Contre :** choix de l’apprenant par défaut arbitraire ; masquage exports peut frustrer l’usage audit depuis le même écran.

### Option B — Conserver la destination, reworder le bloc dashboard

**Principe :** si l’atterrissage sur `GroupView` (liste + exports) est voulu pour les superadmins, le texte doit parler d’**accès groupe démo + exports traçabilité**, pas de « mode testeur encadrant ».

**Pistes :**

- Titre : « Groupe démo bac pro melec » / « Accès cohorte et exports ».
- Bouton : « Ouvrir le groupe démo » ou « Voir la cohorte et les exports ».
- Sous-texte : mentionner explicitement Felix-ready / traces pour audit Qualiopi lite.

**Pour :** honnête vis-à-vis de ce que voit un superadmin aujourd’hui.  
**Contre :** n’offre plus un raccourci clair vers la calibration ; le tuteur perd un libellé utile.

### Option C — Séparer deux raccourcis (recommandée)

**Principe :** deux entrées distinctes sur `/dashboard`, chacune avec texte et route explicites — prolonge la logique « Administration vs Raccourci démo » déjà en place.

| Raccourci | Libellé proposé | Destination existante | Public |
|-----------|-----------------|---------------------|--------|
| **C1 — Calibration encadrant** | « Ouvrir la cohorte démo (calibration) » | `/group/:id` avec liste apprenants **sans** carte exports en tête — ou deep-link premier apprenant | Tuteur, formateur, équipe produit |
| **C2 — Export audit / Qualiopi lite** | « Exports traces (Felix-ready) » | `/groups-admin/:id` accordéon exports **ou** `/group/:id` avec ancre exports seulement | ORGADMIN, auditeur, superadmin |

**Pour :**

- Supprime l’ambiguïté encadrant vs Qualiopi.
- Cohérent avec `VERIF_COHERENCE_SUPERADMIN` (séparation des concerns).
- Réutilise routes et composants **déjà livrés**.

**Contre :** deux cartes au lieu d’une ; nécessite arbitrage UX (quel ID groupe pour C2 — bac pro melec vs org active).

---

## 6. Recommandation documentée

**Option retenue pour une future implémentation : C (séparation)** — avec variante C1 qui deep-lie vers un apprenant démo connu si la liste est longue.

**Rationale courte :**

1. Le **code route** actuel n’est pas « faux » (`/group/:id` = mode testeur historique).
2. La **rupture** est surtout **sémantique et visuelle** pour SUPERADMIN (exports en premier).
3. Les besoins **encadrant** et **audit Qualiopi** sont deux personas distincts ; les fusionner sous « Ouvrir le mode testeur » crée la confusion observée.

**Actions de suivi suggérées (hors scope analyse) :**

- Protocole E2E : assert que l’atterrissage post-clic expose la **liste apprenants** avant les exports, ou assert deep-link calibration.
- Doc `09` §S6 : préciser que le superadmin voit les exports sur `GroupView` (attente actuelle à documenter, pas à cacher).

---

## 7. Synthèse des écarts

| Objet | Intention probable | Réel observé | Statut |
|-------|-------------------|--------------|--------|
| Bouton dashboard | Entrée calibration encadrant bac pro melec | `GroupView` `/group/:id` | Routing **OK**, profondeur **partielle** |
| Première UI superadmin | Liste apprenants / espace test | Carte **Exports Felix-ready** | **Écart UX majeur** |
| Page « Qualiopi » | — | N’existe pas ; perception via exports | **Métaphore utilisateur** |
| Wizard onboarding | Indépendant | Séparé (OK) | **Aligné** |

---

*Analyse produite sans modification de code — juin 2026.*
