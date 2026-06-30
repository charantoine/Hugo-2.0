# Prototype wizard onboarding SAFE — rapport faisabilité / utilité

**Date :** 26 juin 2026  
**Périmètre :** `frontend_1.8`, mode `tester`, compte `demo.superadmin`, org **Demo Hugo Org**  
**Route :** `/admin/onboarding`  
**Baseline runtime :** `localhost:5173`, API → `127.0.0.1:8000`

---

## 1. Ce qui a été implémenté

### Emplacement retenu

**Page dédiée** `/admin/onboarding` sous `TesterLayout`, avec entrée depuis le **dashboard** (bouton « Assistant de mise en route »).  
Choix : plus léger qu’un module navbar permanent, cohérent avec le hub admin existant, sans remplacer les écrans de gestion.

### Fichiers ajoutés / modifiés

| Fichier | Rôle |
|---------|------|
| `src/composables/useAdminOnboardingStatus.js` | Agrégation **lecture seule** des statuts (users, groupes, profils, référentiel) |
| `src/views/admin/AdminOnboardingWizardView.vue` | UI wizard : contexte, progression, 4 étapes, CTA |
| `src/router/index.js` | Route `AdminOnboarding` (`requiresOrgAdmin`) |
| `src/views/DashboardView.vue` | Lien + courte description du parcours |
| `scripts/test_onboarding_wizard.mjs` | Smoke test Playwright |

### Les 4 étapes (guidance only)

| Étape | Données lues (endpoints existants) | Statuts possibles | CTA |
|-------|-----------------------------------|-------------------|-----|
| **Comptes** | `GET /users/` — comptage LEARNER / TUTOR / TRAINER actifs | OK, Incomplet, À configurer | `/users` |
| **Groupe** | `GET /groups/`, `GET /groups/:id/members/`, détail groupe | OK, Incomplet (vide), À configurer | `/groups-admin` ou `/groups-admin/:id` |
| **Conversation apprenant** | `GET /hugo/learner-conversation-profiles/`, champs groupe | OK, Incomplet, Attention fallback, À configurer | `/admin/conversation/learner/profiles` (+ id si profil sélectionné) |
| **Référentiel** | `GET /groups/:id/referential-config/` | OK, À configurer | `/group/:id/referential` ou `/referentials` |

**Groupe de référence :** préférence pour `bac pro melec` si présent, sinon premier groupe de la liste.

> **Mise à jour 26/06/2026 :** le wizard n’utilise plus `bac pro melec` ni `demoReferenceGroup.js`. Il est **org-scoped** (tenant switcher) + **group-selected** (dropdown + `?groupId=`). Voir [`WIZARD_ORG_GROUP_UPDATE_2026-06-26.md`](WIZARD_ORG_GROUP_UPDATE_2026-06-26.md).

**Réutilisation :** `conversationConfigBadge()` de `learnerProfileCompleteness.js` (même logique que le détail groupe).

### Principes SAFE respectés

- Aucun `POST` / `PATCH` / `PUT` depuis le wizard
- Aucun nouvel endpoint backend
- Aucune création automatique multi-objets
- Disclaimer explicite : *« ne crée ni ne modifie rien à votre place »*
- Bouton « Actualiser les statuts » (re-fetch) au lieu d’orchestration cachée

---

## 2. Ce qui a été volontairement exclu

| Exclusion | Raison |
|-----------|--------|
| Création user / groupe / profil / référentiel inline | Hors périmètre SAFE |
| PATCH en cascade (profil + groupe + membres) | Orchestration métier interdite |
| Sélection interactive du groupe dans le wizard | Éviter une mini-gestion parallèle ; lecture du groupe de référence uniquement |
| Étapes tuteur / formateur / RAG / exports | Hors workflow admin cible (4 étapes) |
| Lien navbar permanent | Réduire l’intrusion ; entrée dashboard suffisante pour le prototype |
| Persistance de progression (localStorage / backend) | Pas de nouvelle logique métier ; recalcul à chaque visite |
| Masquage des pages expertes | Non demandé ; le wizard ne les remplace pas |

---

## 3. Limites du wizard SAFE

1. **Un seul groupe de référence** — si plusieurs groupes, seul `bac pro melec` (ou le premier) est évalué pour les étapes 2–4.
2. **Pas de memberships par utilisateur** — l’étape Comptes ne vérifie pas le rattachement au groupe (reste sur `/users` et `/groups-admin/:id`).
3. **Actualisation manuelle** — après une action sur une page cible, l’admin doit revenir et cliquer « Actualiser » (ou recharger).
4. **Complétude conversation** — dépend des champs `completeness` API ; si absents, statut dégradé proprement.
5. **Fallback legacy** — signalé explicitement (badge « Attention fallback ») quand `default_tutor_prompt` sans profil global.
6. **Multi-tenant SUPERADMIN** — changement d’org via switcher recharge les données (watch `tenant.activeOrganisationId`), comme le reste du front.

---

## 4. Vérification runtime (26/06/2026)

**Script :** `node scripts/test_onboarding_wizard.mjs`  
**Captures :** [`screenshots/wizard-overview.png`](screenshots/wizard-overview.png), [`screenshots/results.json`](screenshots/results.json)

| Vérification | Résultat |
|--------------|----------|
| Lien depuis `/dashboard` | OK |
| Organisation « Demo Hugo Org » visible | OK |
| 4 étapes identifiables | OK |
| Statuts distincts (OK / Incomplet / …) | OK — démo : Comptes OK, Groupe OK, **Conversation Incomplet** (4/7), Référentiel OK |
| Disclaimer guidance | OK |
| CTA → `/users` | OK |
| CTA → `/groups-admin/:id` (bac pro melec) | OK |
| CTA → profil conversation (deep-link) | OK |
| CTA → `/group/:id/referential` | OK |
| Groupe `bac pro melec` affiché | OK |

Le wizard **ne donne pas l’impression d’agir à la place de l’admin** : seuls des liens `RouterLink` ouvrent les pages existantes.

---

## 5. Utilité du prototype

### Verdict : **utile comme couche de guidage**, avec marge d’affinage légère

**Points forts observés en runtime :**

- Vue synthétique du parcours admin en **une page** (vs dispersion dashboard + 4 zones)
- Progression **4/4** immédiatement lisible sur la démo (3 OK, 1 incomplet → incite à compléter le profil global)
- Cohérence avec l’audit UX : l’étape Conversation incomplet correspond au badge « Profil global incomplet » déjà vu sur le détail groupe
- Zéro risque backend : lecture seule, dégradation propre si API partielle

**Faiblesses acceptables pour un prototype :**

- Peu visible sans passer par le dashboard (volontaire)
- Pas de checklist par membre ou par rôle dans le groupe

**Recommandation produit :** conserver le prototype, l’exposer en démo onboarding, et mesurer si les admins l’utilisent avant d’enrichir.

---

## 6. Phase suivante (hors SAFE — ne pas implémenter maintenant)

| Idée | Type |
|------|------|
| Sélecteur de groupe dans le wizard (lecture multi-groupes) | UX |
| Checklist « user X pas encore dans un groupe » | Nécessite règles métier + peut-être endpoint agrégé |
| Wizard « actif » avec étape courante suggérée automatiquement | Orchestration légère |
| Deep-link retour wizard depuis pages cibles (« Retour au parcours ») | UX faible effort |
| Persistance « dernière visite / étape vue » en localStorage | Cosmétique |
| Intégration Encoors | Re-test runtime distant |

---

## 7. Accès rapide

```
http://localhost:5173/admin/onboarding
```

Depuis le dashboard admin : **Assistant de mise en route**.
