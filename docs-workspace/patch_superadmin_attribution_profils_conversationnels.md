# Patch — attribution profils conversationnels (parcours wizard + page profil)

**Date :** juin 2026  
**Référence audit :** `docs-workspace/audit_superadmin_attribution_profils_conversationnels.md`  
**Option retenue :** C1 + C2 (wizard → fiche groupe ; bandeau post-save sur page profil)

---

## Fichiers modifiés

| Fichier | Changement |
|---------|------------|
| `hugo-hugolucia/frontend_1.8/src/composables/useAdminOnboardingStatus.js` | CTA principal conversation → `/groups-admin/:id?section=conversation` ; CTA secondaire → profils avec `?groupId=` |
| `hugo-hugolucia/frontend_1.8/src/views/admin/AdminOnboardingWizardView.vue` | Affichage bouton secondaire si `step.secondaryCtaTo` |
| `hugo-hugolucia/frontend_1.8/src/views/GroupAdminDetailView.vue` | Ancre `#conversation-apprenant`, scroll si `?section=conversation`, lien profils avec `groupId` |
| `hugo-hugolucia/frontend_1.8/src/views/admin/LearnerConversationProfilesView.vue` | Bandeau post-save + propagation `groupId` dans la navigation |
| `hugo-hugolucia/frontend_1.8/tests_playwright/e2e/protocol/lot02-wizard.spec.ts` | Test CTA conversation → fiche groupe |
| `hugo-hugolucia/frontend_1.8/scripts/test_onboarding_wizard.mjs` | Libellé CTA conversation mis à jour |

**Backend :** aucune modification.

---

## Comportement avant / après

### Avant

- Étape wizard « Conversation apprenant » → `/admin/conversation/learner/profiles` (ou `/profiles/:id`).
- L’utilisateur créait un profil sans indication pour l’attribuer au groupe.
- L’attribution existait uniquement sur `/groups-admin/:id`, hors parcours wizard.

### Après

- CTA **principal** wizard (groupe sélectionné) → `/groups-admin/{groupId}?section=conversation` avec libellé « Attribuer le profil au groupe ».
- CTA **secondaire** → `/admin/conversation/learner/profiles?groupId={groupId}` (« Créer ou éditer un profil »).
- Fiche groupe : scroll automatique vers la section Conversation si `section=conversation` dans l’URL.
- Page profils : après création ou mise à jour, bandeau info avec lien vers la fiche groupe (si `groupId` connu) ou vers `/groups-admin`.

---

## Route wizard avant / après

| Contexte | Avant | Après |
|----------|-------|-------|
| Groupe sélectionné | `/admin/conversation/learner/profiles` ou `/profiles/{id}` | **Principal :** `/groups-admin/{groupId}?section=conversation` |
| Groupe sélectionné (secondaire) | — | `/admin/conversation/learner/profiles?groupId={groupId}` |
| Aucun groupe sélectionné | `/admin/conversation` | `/groups-admin` (+ secondaire vers profils) |
| Aucun groupe dans l’org | `/groups-admin` | inchangé |

---

## Message UX ajouté (page profil)

> **Étape suivante :** la création ou la mise à jour du profil ne l’active pas sur un groupe. Attribuez-le dans la fiche groupe admin, section « Profil conversationnel du groupe ».  
> Lien : « Ouvrir la fiche du groupe » (si `?groupId=` présent) ou « Gérer les groupes ».

`data-testid="profile-attribution-hint"` pour tests.

---

## Vérifications attendues

1. Wizard + groupe bac pro melec → CTA principal ouvre la fiche groupe avec select profil visible.
2. CTA secondaire ouvre la bibliothèque profils avec `groupId` en query.
3. Sauvegarde profil → bandeau visible + lien attribution.
4. PATCH groupe existant (`default_learner_conversation_profile`) inchangé.
5. Checkbox « Profil par défaut (organisation) » inchangée.

---

## Limites restantes

- Pas de deep-link vers un profil précis dans le select groupe après création (l’admin choisit manuellement dans la liste).
- Le select groupe charge tous les statuts de profil (brouillon inclus) — comportement préexistant, non modifié.
- Pas de liste « groupes utilisant ce profil » sur la fiche profil (option P2 de l’audit).
