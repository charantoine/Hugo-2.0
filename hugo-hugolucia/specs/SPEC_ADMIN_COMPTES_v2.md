# Spec — Gestion des comptes : apprenants, tuteurs, coordinateurs

**Version :** 2.0 — 1 juin 2026
**Statut :** Partiellement implémenté en back, UI à compléter
**Source :** Verbatim fil + SPEC POC v1.5 section 8 (rôles)

---

## 1. Ce qui est spécifié (verbatim du fil)

> "Il faut prévoir un espace de création / gestion de comptes dans accès superadmin.
> Et un espace de gestion des comptes apprenant / tuteur (création / suppression /
> rattachement à une formation / modification des consignes pédagogiques etc) dans l'interface tuteur."

> "Les comptes sont créés manuellement dans le POC." (SPEC POC v1.5)

> "SUPERADMIN : interface technique globale sans accès contenu apprenant."

---

## 2. Rôles et périmètres

| Rôle | Périmètre | Crée quoi |
|---|---|---|
| SUPERADMIN | Toutes organisations (technique) | Organisations, ORGADMIN |
| ORGADMIN | Son organisation | Tuteurs, coordinateurs, groupes |
| TUTEUR | Ses groupes | Apprenants (si délégué), TutorPrompts |
| APPRENANT | Sa session | Rien |

**Règle absolue :** SUPERADMIN n'a pas accès au contenu des apprenants (verbatim conversations, synthèses). Vue technique uniquement.

---

## 3. Interface SUPERADMIN (technique)

### Espace à créer

```
/admin-super/
  /organisations/         # CRUD organisations
  /users/                 # Vue technique des comptes (pas de contenu pédagogique)
  /system-health/         # Santé système, logs techniques
  /conduct-profiles/      # TutorConductProfiles système (profils fallback)
```

### Fonctionnalités

- Créer/désactiver une organisation
- Créer un compte ORGADMIN pour une organisation
- Voir les comptes de toutes les organisations (email, rôle, statut) — pas le contenu
- Gérer les `TutorConductProfile` système (fallback global)

---

## 4. Interface ORGADMIN

### Espace à compléter dans frontend1.8

```
/admin/
  /users/
    /learners/            # CRUD apprenants
    /trainers/            # CRUD tuteurs/coordinateurs
  /groups/                # Gestion groupes + rattachement apprenants
  /formations/            # Rattachement groupes à formations
  /tutor-prompts/         # TutorPrompts par groupe/formation (EXISTE DÉJÀ)
  /conduct-profiles/      # TutorConductProfiles de l'organisation (NOUVEAU)
```

### Fonctionnalités apprenants

- Créer un apprenant : `email`, `prénom`, `nom`, `groupe_id`
- Supprimer / désactiver un apprenant
- Rattacher à un groupe / formation
- Voir les sessions et traces de ses apprenants

### Fonctionnalités tuteurs

- Créer un tuteur : `email`, `prénom`, `nom`, `groupes_assignés`
- Supprimer / désactiver un tuteur
- Modifier les consignes pédagogiques (`TutorPrompt`) de ses groupes

---

## 5. Interface Tuteur

### Espace à compléter dans frontend1.8

```
/tutor/
  /my-learners/           # Liste apprenants de ses groupes
  /my-prompts/            # Édition TutorPrompt pour ses groupes
  /sessions/              # Sessions de ses apprenants (traces)
```

### Fonctionnalités

- Voir la liste de ses apprenants actifs
- Accéder aux traces partagées (pas au verbatim brut)
- Modifier le `TutorPrompt` de son groupe (consignes pédagogiques, contexte de formation)
- Voir les synthèses produites si partagées

---

## 6. Points à arbitrer avant implémentation

| Point | Options | Impact |
|---|---|---|
| Qui peut créer des apprenants ? ORGADMIN seulement ou aussi tuteur ? | A: ORGADMIN seul / B: Tuteur avec délégation explicite | Périmètre UI tuteur |
| Invitation email ou création directe ? | A: Lien d'activation / B: Mot de passe provisoire direct | Infrastructure email requise pour A |
| Suppression : hard delete ou désactivation ? | A: Désactivation (is_active=False) — recommandé pour traçabilité | SPEC POC : créations manuelles |
| Modification consignes par tuteur : son propre TutorPrompt ou aussi posture ? | A: TutorPrompt seulement / B: TutorPrompt + TutorConductProfile | Si B, ajouter permissions |

---

## 7. État actuel du backend

- `POST /admin/users/` : opérationnel
- `UsersView.vue` : liste LEARNER/TUTOR, sans création complète
- `GroupsAdminListView.vue` : liste groupes, sans rattachement apprenant
- `TutorPromptsView.vue` : édition TutorPrompt ORGADMIN : présente

**Ce qui manque en back :**
- Endpoint de rattachement apprenant → groupe : probablement absent
- Endpoint CRUD tuteur scopé ORGADMIN : à vérifier

```bash
# Vérifier les endpoints manquants
grep -rn "assign_learner\|add_to_group\|create_learner" backend/apps/hugo/views/ --include="*.py"
grep -rn "organisation_id" backend/apps/accounts/views.py 2>/dev/null || echo "views.py absent"
```

