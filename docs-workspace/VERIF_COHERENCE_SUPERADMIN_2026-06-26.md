# Vérification finale — cohérence superadmin (org active + séparation démo / wizard)

**Date :** 26 juin 2026  
**Compte :** `demo.superadmin` / org **Demo Hugo Org**  
**Surfaces :** `/dashboard`, `/users`, `/groups-admin`, `/groups-admin/:id`, `/admin/onboarding`  
**Preuves :** [`verif-coherence-superadmin-2026-06-26/`](verif-coherence-superadmin-2026-06-26/) (captures + `journal.json`)  
**Script :** `hugo-hugolucia/frontend_1.8/scripts/verif_coherence_superadmin.mjs`

---

## Verdict global

| Objectif | Statut |
|----------|--------|
| 1. Organisation active claire et cohérente | **OK** sur les 5 surfaces |
| 2. Wizard indépendant de `bac pro melec` | **OK** (code + runtime) |
| 3. Pas de `bac pro melec` comme référence onboarding implicite | **OK** (présence en liste = nom de groupe réel, pas pivot produit) |
| 4. Raccourci démo dashboard assumé et séparé du wizard | **OK** (libellés « Raccourci démo » / hors onboarding) |

---

## 1. Organisation active — par surface

Mécanisme unique : `useTenantStore` + `OrgTenantSwitcher` (navbar) + `ActiveOrganisationBanner` (corps de page).

| Surface | Bandeau corps | Libellé | Navbar switcher | Hint SUPERADMIN |
|---------|---------------|---------|-----------------|-----------------|
| `/dashboard` | Oui (`compact`) | Organisation active : Demo Hugo Org | Oui | Oui |
| `/users` | Oui | idem | Oui | Oui |
| `/groups-admin` | Oui | idem | Oui | Oui |
| `/groups-admin/:id` | Oui | idem | Oui | Oui |
| `/admin/onboarding` | Oui + note de scope org | idem | Oui | Oui |

**Runtime confirmé :** `orgBannerCount = 1` et `hasDemoHugoOrg = true` sur les 5 pages (`journal.json`).

**Harmonisation :** toutes les surfaces auditées utilisent `ActiveOrganisationBanner` avec le même libellé **« Organisation active : {nom} »**. L’ancienne formulation « Organisation actuelle » / « Organisation : » a été retirée des pages concernées.

---

## 2. Wizard — indépendance de `bac pro melec`

### Code

| Fichier | Référence `bac pro melec` / `demoReferenceGroup` |
|---------|---------------------------------------------------|
| `useAdminOnboardingStatus.js` | **Aucune** |
| `AdminOnboardingWizardView.vue` | **Aucune** |
| `demoReferenceGroup.js` | Utilisé **uniquement** par `DashboardView.vue` (mode testeur) |

### Comportement wizard

- Liste groupes : `GET /groups/` (org active)
- Sélection : dropdown **« Groupe à configurer »** + `?groupId=` optionnel
- Pré-sélection par défaut : **premier groupe de la liste API** (ordre backend), sans nom codé
- Aucun libellé « Groupe de référence » dans le wizard (**confirmé runtime**)

### Présence de « bac pro melec » dans le wizard

**Constat :** le nom peut apparaître dans le `<select>` comme **option parmi les groupes de l’organisation** — comportement attendu, pas une dépendance produit.

Ce n’est **pas** une référence onboarding implicite : l’utilisateur choisit explicitement le groupe ; le wizard ne privilégie plus ce nom en code.

---

## 3. Surfaces sans pivot démo onboarding

| Surface | `bac pro melec` visible ? | Interprétation |
|---------|---------------------------|----------------|
| `/users` | Non | OK — scope org comptes uniquement |
| `/groups-admin` | Oui (liste des groupes) | OK — nom de ressource réelle |
| `/groups-admin/:id` | Oui (titre h1 si ce groupe) | OK — page détail d’un groupe existant |
| `/admin/onboarding` | Oui (option dropdown) | OK — liste neutre, pas pivot |
| `/dashboard` | Oui (section **Mode testeur** uniquement) | OK — raccourci démo explicite (voir §4) |

Aucune de ces surfaces (hors section testeur du dashboard) ne présente `bac pro melec` comme **chemin d’onboarding par défaut**.

---

## 4. Dashboard — raccourci démo séparé du wizard

### Section Administration

- Lien **« Assistant de mise en route »** → `/admin/onboarding`
- Texte : parcours guidé comptes → groupe → conversation → référentiel
- **Aucune mention** de `bac pro melec`

### Section Mode testeur (démo-spécifique)

| Élément | Libellé actuel |
|---------|----------------|
| Intro section | « Raccourci de démonstration … (hors parcours d’onboarding admin). Cible par défaut : **bac pro melec**. » |
| Carte principale | « Raccourci démo — cohorte préconfigurée pour les tests encadrant. » |
| Bouton | `data-testid="dashboard-tester-canonical"` — Ouvrir le mode testeur |
| Autres groupes | Panneau replié `<details>` (dont groupes debug) |

**Séparation nette :** le wizard = produit généralisé org + groupe choisi ; le dashboard testeur = **raccourci démo** documenté, limité à la section Mode testeur.

---

## 5. Ce qui est généralisé vs démo-spécifique

### Généralisé (produit)

- Bandeau **Organisation active** harmonisé
- Wizard **org-scoped** (tenant switcher existant)
- Wizard **group-selected** (dropdown + query `groupId`)
- Étapes onboarding sans nom de groupe codé
- Pages admin users / groupes : contexte org, pas de pivot démo

### Volontairement démo-spécifique

- `demoReferenceGroup.js` + carte mode testeur sur `/dashboard`
- Scripts d’audit (`auditConstants.mjs`) — IDs/noms de fixture locale
- Groupe `bac pro melec` en base démo (ressource réelle listée partout où les groupes sont affichés)

---

## 6. Incohérences résiduelles — lot ultérieur

| Sujet | Niveau | Détail |
|-------|--------|--------|
| Bandeau org répété page par page | Faible | Envisager une barre unique dans `TesterLayout` (proposition audit org) |
| `/admin/conversation/learner/profiles` | Faible | Encart org inline, pas encore `ActiveOrganisationBanner` |
| Test changement d’org multi-tenant | Moyen | Non couvert auto (besoin ≥2 orgs en base) |
| État wizard org sans groupe | Faible | CTA codé ; validation manuelle sur org vide |
| Nom `bac pro melec` dans listes | N/A | Donnée démo, pas incohérence UX si non présenté comme pivot |

**Aucune incohérence bloquante superadmin** identifiée sur les 5 surfaces cibles.

---

## 7. Synthèse pour décision

- **Visibilité org :** lot livré et cohérent sur le périmètre demandé.
- **Wizard :** généralisé ; plus de logique `bac pro melec` ; séparation dashboard démo / wizard produit **claire**.
- **Action ultérieure optionnelle :** barre org layout global ; aligner hubs conversation sur `ActiveOrganisationBanner` ; test runtime switch org avec 2e organisation.

---

## 8. Captures

| Fichier | Surface |
|---------|---------|
| `dashboard.png` | Tableau de bord (admin + raccourci démo testeur) |
| `users.png` | Utilisateurs |
| `groups-admin.png` | Liste groupes |
| `group-detail.png` | Détail bac pro melec |
| `onboarding.png` | Assistant mise en route + sélecteur groupe |
