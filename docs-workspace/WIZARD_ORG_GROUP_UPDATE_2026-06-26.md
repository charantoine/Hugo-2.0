# Mise à jour — organisation active + wizard généralisé

**Date :** 26 juin 2026  
**Lot :** visibilité tenant + wizard org-scoped / group-selected (SAFE, sans backend)

---

## Changements faits

### 1. Visibilité organisation active

| Élément | Détail |
|---------|--------|
| `composables/useActiveOrganisationLabel.js` | Libellé harmonisé depuis `useTenantStore` |
| `components/admin/ActiveOrganisationBanner.vue` | Bandeau sobre **« Organisation active : {nom} »** |
| Pages mises à jour | `/dashboard` (section admin), `/users`, `/groups-admin`, `/groups-admin/:id`, `/admin/onboarding` |
| SUPERADMIN | Hint optionnel : *« changez-la via le sélecteur en barre de navigation »* |
| Mécanisme de sélection | **Inchangé** — `OrgTenantSwitcher` navbar + `localStorage` + header `X-Organisation-Id` |

### 2. Wizard généralisé (`/admin/onboarding`)

| Avant | Après |
|-------|-------|
| `findReferenceGroup()` → `bac pro melec` puis `groups[0]` | **Sélecteur « Groupe à configurer »** (`GET /groups/` org-scoped) |
| Libellé « Groupe de référence » | **« Groupe à configurer »** / « Groupe sélectionné » |
| Pas de `?groupId=` | **`?groupId=`** pré-sélectionne si valide dans l’org |
| Dépendance `demoReferenceGroup.js` dans le wizard | **Supprimée** du composable wizard |

**Comportement :**
- Étape **Comptes** : niveau **organisation** (inchangé)
- Étapes **Groupe / Conversation / Référentiel** : niveau **groupe sélectionné**
- Aucun groupe : alerte + CTA **Créer un groupe** → `/groups-admin`
- Si groupes existent sans `?groupId=` : premier de la liste API (choix technique, non présenté comme « référence »)
- Changement d’org (navbar) : `watch tenant.activeOrganisationId` → reset sélection + refresh

### 3. Hors périmètre respecté

- Pas de switcher d’org dans le wizard
- Pas de création inline groupe/user/profil
- Pas de store global « groupe courant »
- Pas de vue multi-groupes avec statuts
- Pas de nouveau backend

**Note :** `demoReferenceGroup.js` reste utilisé par le **dashboard mode testeur** (carte canonique `bac pro melec`) — hors scope de ce lot.

---

## Vérification runtime (`demo.superadmin`)

Script : `node scripts/test_wizard_org_group.mjs`  
Preuves : [`wizard-org-group-2026-06-26/`](wizard-org-group-2026-06-26/)

| Cas | Résultat |
|-----|----------|
| Bandeau org sur `/dashboard` | **OK** — « Organisation active : Demo Hugo Org » |
| Sélecteur groupes wizard (plusieurs groupes) | **OK** — dropdown visible, ≥2 options |
| Message scope org dans wizard | **OK** |
| `?groupId=` valide | **OK** — pré-sélection `bac pro melec` |
| Changement de groupe → recalcul étape Groupe | **OK** |
| Absence de « Groupe de référence » | **OK** |

**Non testé automatiquement :**
- **Cas 1 changement d’org** via switcher (nécessite ≥2 orgs en base locale) — mécanisme confirmé par code (`watch` + reload navbar existant)
- **Cas 3 aucun groupe** — état vide + CTA codés ; à valider manuellement sur org sans groupe

---

## Pourquoi c’est plus généralisé tout en restant SAFE

| Critère | Réponse |
|---------|---------|
| Généralisation | Le wizard raisonne sur **l’org active du tenant switcher** + **un groupe choisi**, pas sur un nom démo codé |
| SAFE | Lecture seule, CTA vers pages existantes, pas de PATCH/POST depuis le wizard |
| Cohérence produit | Même bandeau org que le reste de l’admin ; une seule source de vérité pour l’org (navbar) |
| Limites assumées | Un groupe à la fois ; pas de tableau d’onboarding multi-groupes |

---

## Prochaines étapes possibles (hors lot)

- Barre org unique dans `TesterLayout` (éviter répétition des bandeaux)
- Test runtime changement d’org avec 2e organisation de démo
- Lien retour « Assistant de mise en route » sur les pages cibles
- Retirer progressivement `demoReferenceGroup` du dashboard testeur si souhaité

---

## Fichiers modifiés

- `src/composables/useActiveOrganisationLabel.js` (nouveau)
- `src/components/admin/ActiveOrganisationBanner.vue` (nouveau)
- `src/composables/useAdminOnboardingStatus.js`
- `src/views/admin/AdminOnboardingWizardView.vue`
- `src/views/DashboardView.vue`
- `src/views/UsersView.vue`
- `src/views/GroupsAdminListView.vue`
- `src/views/GroupAdminDetailView.vue`
- `scripts/test_wizard_org_group.mjs` (nouveau)

**Docs liées mises à jour par ce rapport :** complète [`AUDIT_ORGANISATION_ACTIVE_FRONT_ADMIN_2026-06-26.md`](AUDIT_ORGANISATION_ACTIVE_FRONT_ADMIN_2026-06-26.md) et [`PROTOTYPE_WIZARD_ONBOARDING_SAFE_2026-06-26.md`](PROTOTYPE_WIZARD_ONBOARDING_SAFE_2026-06-26.md) (voir encarts ci-dessous si besoin de lecture croisée).
