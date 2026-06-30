# Audit — attribution des profils conversationnels apprenants (superadmin multi-org)

**Date :** juin 2026  
**Périmètre :** analyse uniquement — **aucune modification de code**  
**Question métier :** le superadmin peut créer un profil depuis le wizard, mais ne trouve pas comment l’attribuer à une organisation et/ou à un groupe.

---

## Sources mobilisées

| Couche | Fichiers / preuves |
|--------|-------------------|
| Front profils | `LearnerConversationProfilesView.vue`, route `/admin/conversation/learner/profiles` |
| Front groupe admin | `GroupAdminDetailView.vue`, route `/groups-admin/:groupId` |
| Front wizard | `AdminOnboardingWizardView.vue`, `useAdminOnboardingStatus.js` |
| Front hub | `AdminConversationIndexView.vue`, `adminConversationModes.js` |
| Back modèles | `LearnerConversationGlobalProfile`, `Group.default_learner_conversation_profile` |
| Back API | `views_learner_conversation_profiles.py`, `views_groups.py`, `serializers.py` |
| Résolution runtime | `learner_profile_resolver.py`, `MINI_SPEC_PROFILS_CONVERSATIONNELS_APPRENANT.md` |
| Tests | `test_learner_conversation_global_profile.py`, `test_session_learner_conversation_profile.py` |

---

## Constat

**Le backend et une page admin groupe permettent déjà l’attribution au groupe.**  
**Le parcours guidé par le wizard et la page profil ne mènent pas à cette capacité** : l’utilisateur crée un profil, puis reste sur un écran d’édition de slots sans lien explicite vers l’affectation groupe.

Ce n’est **pas** une absence totale de fonctionnalité, mais une **rupture de parcours UX** entre création (bibliothèque de profils) et affectation (configuration du groupe).

---

## Parcours actuel observé

### 1. Entrée wizard (`/admin/onboarding`)

1. Superadmin sélectionne l’organisation active (navbar `#tenant-switcher`).
2. Sélectionne un **groupe à configurer** (`wizard-group-select`).
3. Parcourt 4 étapes guidées (lecture seule + boutons d’ouverture).

| Étape | CTA wizard | Destination réelle |
|-------|------------|-------------------|
| Comptes | Gérer les utilisateurs | `/users` |
| Groupe | Gérer le groupe | `/groups-admin/{groupId}` ✅ |
| **Conversation apprenant** | Configurer la conversation apprenant | `/admin/conversation/learner/profiles` ou `/profiles/{id}` ❌ |
| Référentiel | Associer un référentiel | `/group/{groupId}/referential` ✅ |

**Asymétrie confirmée :** l’étape Référentiel pointe vers une **action groupe** (`/group/.../referential`), alors que l’étape Conversation pointe vers la **bibliothèque de profils** — pas vers l’attribution sur le groupe sélectionné.

Source : `useAdminOnboardingStatus.js` L141-203 (conversationStep), L206-254 (referentialStep).

### 2. Page profils (`/admin/conversation/learner/profiles`)

Actions possibles :

- Créer / éditer un `LearnerConversationGlobalProfile` (nom, statut, 7 slots posture, évaluation).
- Cocher **« Profil par défaut (organisation) »** (`is_default`) → affectation **niveau org** via PATCH profil.
- **Aucun** sélecteur de groupe, **aucun** lien « Attribuer au groupe X », **aucune** liste des groupes qui utilisent ce profil.

Source : `LearnerConversationProfilesView.vue` L583-585 (checkbox org), absence de `default_learner_conversation_profile` ou `groups-admin` dans le template.

### 3. Page détail groupe admin (`/groups-admin/:groupId`)

Section **« Conversation apprenant »** (carte dédiée, après la cohorte) :

- Label : **« Profil conversationnel du groupe »**
- `<select>` alimenté par `GET /hugo/learner-conversation-profiles/` (profils de l’**org active**).
- `@change` → `PATCH /groups/{id}/` avec `{ default_learner_conversation_profile: uuid | null }`.
- Lien secondaire : « Gérer les profils globaux » → page profils.

Source : `GroupAdminDetailView.vue` L373-384, L433-443, L743-771.

### 4. Ce que l’utilisateur ne voit pas naturellement

- Le wizard **ne renvoie pas** vers `/groups-admin/{groupId}` pour l’étape conversation (alors que l’étape groupe le fait).
- Après création d’un profil, **aucun message** n’indique « allez sur le groupe pour l’activer ».
- La page `/group/:id` (mode testeur, `GroupView.vue`) **n’a pas** de sélecteur de profil — seulement exports et liste apprenants.

---

## Capacités backend existantes

### Modèle `LearnerConversationGlobalProfile`

Fichier : `hugo_back/apps/hugo/models.py` L678+

| Champ | Rôle | Portée |
|-------|------|--------|
| `organisation` | FK obligatoire | **Tenant** — un profil appartient à une seule org |
| `name`, `description`, `status` | Métadonnées | draft / active / inactive |
| `is_default` | Booléen | **Défaut organisation** si aucun profil session/groupe |
| Slots `*_tutor_prompt`, `*_conduct_profile`, `evaluation_*` | Composition | Objets existants (pas de duplication) |

**Pas de FK directe profil → groupe** : l’attribution groupe passe par `Group.default_learner_conversation_profile`.

### Modèle `Group`

Fichier : `hugo_back/apps/referentials/models.py` L33-39

```python
default_learner_conversation_profile = models.ForeignKey(
    "hugo.LearnerConversationGlobalProfile", ...
    related_name="groups_with_default_profile",
)
```

Migration : `0018_group_default_learner_conversation_profile.py`.

**Legacy distinct :** `default_tutor_prompt` (TutorPrompt unique) — chemin historique, toujours présent.

### Modèle `Organisation`

Fichier : `hugo_back/apps/accounts/models.py`

- `default_learner_display_profile` (youth/adult/professional) — **affichage UI apprenant**, pas conversationnel global.
- **Pas de champ** `default_learner_conversation_profile` sur `Organisation`.
- Défaut org conversationnel = `LearnerConversationGlobalProfile.is_default=True` (au plus un actif par org, enforced serializer).

### Hiérarchie runtime (preuve code)

Fichier : `learner_profile_resolver.py` L12-43

| Priorité | Source |
|----------|--------|
| 1 | `session.learner_conversation_profile` (actif) |
| 2 | `group.default_learner_conversation_profile` (actif) |
| 3 | profil org `is_default=True` + `status=active` |
| 4 | (hors profil global) fallback legacy `TutorPrompt` / `group.default_tutor_prompt` |

### API

| Endpoint | Méthodes | Permission écriture | Rôle |
|----------|----------|---------------------|------|
| `/hugo/learner-conversation-profiles/` | GET, POST | POST : `IsOrgAdminOrSuperadmin` | CRUD bibliothèque org |
| `/hugo/learner-conversation-profiles/{id}/` | GET, PATCH, DELETE | PATCH/DELETE : idem | Édition + `is_default` |
| `/groups/{group_id}/` | GET, PATCH | `IsOrgAdminOrSuperadmin` | **Attribution groupe** via `default_learner_conversation_profile` |
| `/groups/` | GET, POST | POST : admin | Liste groupes (inclut FK profil dans serializer) |

Validations multi-tenant :

- `GroupSerializer.validate_default_learner_conversation_profile` — profil et groupe **même organisation** (`referentials/serializers.py` L78-89).
- `LearnerConversationGlobalProfileSerializer` — un seul `is_default=True` par org (L671-683).
- Profils filtrés par `tenant_organisation_id(request)` dans les vues.

### Objets distincts (ne pas confondre)

| Objet | Rôle | Attribution |
|-------|------|-------------|
| **LearnerConversationGlobalProfile** | Profil global apprenant (3 postures + éval) | Groupe via FK inverse ; org via `is_default` |
| **TutorPrompt** | Prompt orchestrateur (legacy / slots) | Groupe `default_tutor_prompt` ; ou slot dans profil global |
| **TutorConductProfile** | Règles de conduite posture | Slot dans profil global ; hubs `/admin/conversation/learner/:posture` |
| **EvaluationPromptProfile** | Profil prompt évaluation | Slot `evaluation_prompt_profile` dans profil global |
| **EvaluationPolicy** | Politique évaluation org | Slot optionnel profil global |

---

## Capacités UI existantes

| Surface | Création profil | Défaut org (`is_default`) | Attribution groupe | Visible superadmin |
|---------|-----------------|---------------------------|--------------------|--------------------|
| `/admin/conversation/learner/profiles` | ✅ | ✅ checkbox | ❌ | ✅ (org active) |
| `/groups-admin/:id` → Conversation apprenant | ❌ (lien vers profils) | ❌ | ✅ select + PATCH | ✅ |
| `/admin/onboarding` étape Conversation | ❌ (redirige création) | ❌ | ❌ (ne redirige pas groupe) | ✅ |
| `/group/:id` (testeur) | ❌ | ❌ | ❌ | ✅ |
| Page organisation `/admin/organisations/:id` | — | — | **Non audité en détail** — pas de sélecteur profil conversationnel attendu | — |

**Tests E2E existants :** `admin_learner_profiles.spec.ts` couvre **création** profil uniquement — pas l’attribution groupe.

---

## Point exact de rupture

| # | Rupture | Preuve |
|---|---------|--------|
| **R1** | Le wizard envoie l’étape « Conversation » vers la **bibliothèque profils**, pas vers la **config groupe** | `useAdminOnboardingStatus.js` L199-202 : `ctaTo` → `/admin/conversation/learner/profiles[...]` |
| **R2** | La page profil permet **création + défaut org**, mais **aucune affectation groupe** | `LearnerConversationProfilesView.vue` — pas de PATCH groupe |
| **R3** | L’attribution groupe **existe** mais est **hors parcours wizard** — il faut connaître `/groups-admin/:id` | `GroupAdminDetailView.vue` L750-756 |
| **R4** | Incohérence avec l’étape Référentiel du même wizard (qui, elle, cible le groupe) | `ctaTo: /group/${g.id}/referential` L242 |
| **R5** | Après sauvegarde profil, **aucun CTA** « Activer sur le groupe {nom} » | `LearnerConversationProfilesView.vue` — message succès générique seulement |

**Synthèse :** on peut **créer** partout où le wizard mène ; on ne peut **attribuer au groupe** qu’en naviguant manuellement vers `/groups-admin/:groupId` — parcours non signalé.

---

## Endroit le plus logique pour la correction

### Analyse des options UX

| Option | Logique métier | Multi-tenant | Cohérence wizard |
|--------|----------------|--------------|------------------|
| **Page groupe** (`/groups-admin/:id`) | Un profil global est **consommé par les sessions du groupe** — l’affectation est une propriété du groupe | ✅ PATCH déjà validé même org | À relier depuis wizard (comme référentiel) |
| **Page profil** | Création + « où ce profil est utilisé » | ✅ liste groupes filtrée org | Complément utile, pas suffisant seul |
| **Page orga** | Défaut org déjà via `is_default` sur profil | ✅ | Pas de champ org dédié en base |
| **Wizard seul** | Guidance only aujourd’hui | ✅ | Meilleur levier **immédiat** si CTA corrigé |

### Recommandation d’emplacement principal

**La page détail groupe admin (`/groups-admin/:groupId`) reste le lieu canonique d’attribution par groupe** — le backend et l’UI l’ont déjà prévu (`Group.default_learner_conversation_profile`).

**Le wizard doit y renvoyer** pour l’étape Conversation (comme il le fait déjà pour l’étape Groupe et pour le Référentiel vers une URL groupe).

**La page profil** doit compléter avec : défaut org (déjà là) + **lien explicite** vers le groupe sélectionné dans le wizard (ou liste des groupes de l’org).

**Pas de nouvelle page orga** : le modèle n’a pas de FK org→profil ; `is_default` sur le profil suffit.

---

## Risques / impacts multi-tenant

| Risque | Mitigation existante | Si correction UI |
|--------|---------------------|------------------|
| Profil org A affecté à groupe org B | `GroupSerializer.validate_default_learner_conversation_profile` | Conserver — ne lister que profils `GET /hugo/learner-conversation-profiles/` de l’org active |
| Superadmin sur mauvaise org | `tenant_organisation_id` + switcher | Tous les CTA wizard doivent inclure le **groupe de l’org active** |
| Utilisateur groupe (tuteur) modifie profils globaux | Écriture profils : `IsOrgAdminOrSuperadmin` only | Ne pas exposer CRUD profil aux tuteurs |
| Confusion legacy `default_tutor_prompt` | Badge `conversationConfigBadge` sur détail groupe | Garder masquage prompt legacy quand profil global sélectionné |
| Plusieurs `is_default` par org | Serializer unset autres profils | Inchangé |
| Profil `draft` affecté au groupe | Runtime : seuls profils `active` résolus | Optionnel : filtrer select groupe sur `status=active` (à vérifier si déjà fait côté front) |

**AVERIFIER :** le `<select>` groupe charge-t-il tous les statuts ou seulement `active` ? Le front charge la liste complète (`loadLearnerProfiles` sans filtre) — un admin pourrait affecter un profil brouillon (résolution runtime l’ignorera).

---

## Recommandation de correction minimale

Corriger le **parcours** sans nouveau modèle : wizard + renforts légers page profil et page groupe.

---

# Phase 2 — Proposition de correction (non implémentée)

## Option recommandée

**Combinaison légère C1 + C2 :**

- **C1 — Wizard :** l’étape « Conversation apprenant » ouvre **`/groups-admin/{groupId}`** (section Conversation), avec lien secondaire « Créer ou éditer un profil » vers `/admin/conversation/learner/profiles`.
- **C2 — Page profil :** après enregistrement, bandeau + lien « Attribuer à un groupe » → `/groups-admin` ou deep-link groupe si `?groupId=` passé en query depuis wizard.

**Pourquoi pas uniquement page profil (option profil seule) :** l’attribution est modélisée sur **Group**, pas sur le profil ; éditer le profil ne change pas `default_learner_conversation_profile` sans PATCH groupe.

**Pourquoi pas uniquement orga :** pas de FK org ; `is_default` reste sur la fiche profil.

**Pourquoi pas wizard seul sans renfort profil :** après création, l’utilisateur reste sur la page profil sans instruction.

### Hiérarchie à respecter (rappel produit)

| Niveau | Mécanisme | Qui configure | Priorité runtime |
|--------|-----------|---------------|------------------|
| **Groupe** | `Group.default_learner_conversation_profile` | Superadmin / ORGADMIN sur `/groups-admin/:id` | 2 (après session) |
| **Organisation** | `LearnerConversationGlobalProfile.is_default` | Sur fiche profil | 3 (fallback) |
| **Session** | `HugoSession.learner_conversation_profile` | Runtime apprenant (hors scope admin) | 1 (plus forte) |

**Règle affichage :** si groupe et org ont des valeurs, **le groupe prime** pour les apprenants de ce groupe (sauf override session).

---

## Pourquoi cette option est la plus logique

1. **Alignement données** — la FK est sur `Group` ; l’UI existe déjà au bon endroit.
2. **Alignement wizard** — même pattern que l’étape Référentiel (`/group/{id}/referential`).
3. **Minimal** — pas de migration, pas de nouvel endpoint obligatoire.
4. **Multi-tenant** — réutilise validations et filtrage org existants.
5. **Clarté superadmin** — « Je configure ce groupe » vs « Je crée un objet dans la bibliothèque ».

---

## Patch plan minimal

### Frontend

| Fichier | Modification proposée |
|---------|----------------------|
| `useAdminOnboardingStatus.js` | `conversationStep.ctaTo` → `/groups-admin/${g.id}` (si groupe sélectionné). `ctaLabel` → « Configurer la conversation du groupe ». Ajouter `secondaryCtaTo` / `secondaryCtaLabel` vers profils (optionnel dans template wizard). |
| `AdminOnboardingWizardView.vue` | Afficher bouton secondaire « Créer / éditer un profil global » si `step.secondaryCtaTo` défini. |
| `GroupAdminDetailView.vue` | Ajouter `id="conversation-apprenant"` sur la carte Conversation pour ancre URL `?section=conversation` ou hash. Scroll ou highlight si query présente. |
| `LearnerConversationProfilesView.vue` | Bandeau post-save : « Pour activer ce profil sur un groupe, ouvrez la fiche groupe → Conversation apprenant. » Lien vers `/groups-admin` ou `/groups-admin/{groupId}` si `route.query.groupId`. Passer `groupId` depuis wizard sur lien « Créer profil ». |
| `GroupAdminDetailView.vue` (optionnel) | Filtrer options du select : `status === 'active'` uniquement ; libellé plus explicite « Attribuer ce profil au groupe ». |

**Pas de modification** de `GroupView.vue` (testeur), `ProdLearnerHomeView.vue`, ni des hubs posture legacy sauf liens d’aide.

### Backend

| Élément | Action |
|---------|--------|
| `PATCH /groups/{id}/` | **Réutiliser** — champ `default_learner_conversation_profile` déjà exposé |
| `LearnerConversationGlobalProfile` API | **Réutiliser** — `is_default` pour défaut org |
| Nouvel endpoint (optionnel P2) | `GET /hugo/learner-conversation-profiles/{id}/groups/` — liste des groupes référençant le profil (`related_name=groups_with_default_profile`) — **non requis** pour MVP si lien wizard + groupe suffit |

### Permissions

| Action | Permission actuelle | Changement |
|--------|-------------------|------------|
| PATCH groupe profil | `IsOrgAdminOrSuperadmin` | Aucun |
| POST/PATCH profil global | `IsOrgAdminOrSuperadmin` | Aucun |
| GET profils (select) | `IsAuthenticated` + filtre tenant | Aucun |

### Impact données

- Aucune migration.
- Données existantes : groupes avec `default_learner_conversation_profile` déjà renseigné (ex. bac pro melec démo) continuent de fonctionner.

### Impact UX

| Persona | Avant | Après (attendu) |
|---------|-------|-----------------|
| Superadmin wizard | Crée profil, bloqué | Wizard → fiche groupe → select profil |
| Superadmin direct | Doit découvrir `/groups-admin/:id` | Inchangé mais signalé depuis profil |
| ORGADMIN | Même select groupe | Inchangé |
| Tuteur / apprenant | Pas d’accès admin profils | Inchangé |

---

## Options écartées (rappel)

| Option | Raison d’écart |
|--------|----------------|
| **B — Reworder uniquement** | N’ajoute pas le chemin d’attribution ; le problème n’est pas le libellé seul |
| **A seule — Deep-link apprenant testeur** | Hors besoin admin ; confond calibration et affectation config |
| **Nouvelle page orga dédiée** | Redondant avec `is_default` sur profil |

---

## Critères d’acceptation (pour implémentation future)

1. Depuis `/admin/onboarding`, avec un groupe sélectionné, le CTA principal de l’étape **Conversation apprenant** ouvre **`/groups-admin/{groupId}`** et la section profil est visible (ancre ou scroll).
2. Sur `/groups-admin/{groupId}`, le superadmin peut sélectionner un profil créé précédemment ; `PATCH /groups/{id}/` renvoie 200 ; rechargement affiche le profil.
3. Le wizard affiche le statut conversation **OK** après attribution (`default_learner_conversation_profile` non null sur le groupe focus) — déjà calculé dans `useAdminOnboardingStatus.js` L169-178.
4. Depuis la page profil, un lien explicite mène vers l’attribution groupe (avec `groupId` si contexte wizard).
5. Cocher « Profil par défaut (organisation) » continue de fonctionner indépendamment ; un groupe sans profil dédié hérite du défaut org en runtime.
6. Aucune régression multi-tenant : impossible d’affecter un profil d’une autre org au groupe (test backend existant + test manuel switch org).
7. Distinction documentée : **LearnerConversationGlobalProfile** ≠ **TutorPrompt** legacy.

---

## Prochaine sortie utile

Validation de cette proposition → implémentation du patch C1+C2 (estimé **4 fichiers front**, **0 migration back**).

---

*Audit produit sans modification de code — juin 2026.*
