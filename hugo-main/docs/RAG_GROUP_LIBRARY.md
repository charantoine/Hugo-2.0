# RAG par groupe : bibliothèque de documents

Les extraits utilisés par Hugo (`select_rag_chunks` → `{documents_block}` dans le [TutorPrompt](TUTOR_PROMPT_PLACEHOLDERS.md)) proviennent de **documents d’organisation** liés au **groupe** de la session.

## Chaîne de données

1. **`Document`** (`apps.library.models.Document`) — titre + `source_text` (texte brut ou markdown collé en base).
2. **`DocumentChunk`** — morceaux générés par `POST /documents/{id}/index/` (fenêtre avec chevauchement, pas d’embedding obligatoire en POC).
3. **`GroupDocument`** — attache un document à un `referentials.Group` avec statut `ACTIVE` ou `INACTIVE`.

Au tour Hugo, [`rag_support.select_rag_chunks`](backend/apps/hugo/services/rag_support.py) ne considère que les documents **actifs** pour `session.group_id` et `session.organisation_id`.

## API

### Gestion documents (ORGADMIN / SUPERADMIN / TRAINER)

| Méthode | Chemin | Rôle |
|---------|--------|------|
| `GET` / `POST` | `/documents/` | Lister / créer un document (`title`, `source_text`). |
| `GET` / `PATCH` | `/documents/{document_id}/` | Lire ou mettre à jour le texte source. |
| `POST` | `/documents/{document_id}/index/` | Régénère les chunks (supprime les anciens). Paramètres optionnels : `chunk_size`, `overlap`. |
| `POST` | `/groups/{group_id}/library/` | Lier un `document_id` au groupe. Réactive `ACTIVE` si la liaison existait en `INACTIVE`. |
| `PUT` | `/groups/{group_id}/library/{group_document_id}/` | Changer le statut (ex. `INACTIVE` pour retirer du RAG). |

Réservé aux rôles **ORGADMIN**, **SUPERADMIN** et **TRAINER** (formateur). Les **tuteurs** et **apprenants** n’ont pas ces opérations d’écriture.

### Lecture (tout acteur du groupe, même organisation)

Tout utilisateur authentifié peut **lister** et **lire le texte** pour un groupe s’il est **admin org**, **superadmin**, **formateur** (`TRAINER`, lecture sur tout groupe de l’org), ou **lié au groupe** : adhésion (`GroupMembership`), **lien tuteur / apprenant** (`TutorLearnerLink`), ou au moins une **session Hugo** apprenant sur ce groupe.

| Méthode | Chemin | Contenu |
|---------|--------|---------|
| `GET` | `/groups/{group_id}/library/` | Liste des liaisons ; sans droit de gestion, seules les liaisons **ACTIVE** sont renvoyées. |
| `GET` | `/groups/{group_id}/library/documents/{document_id}/content/` | `{ id, title, source_text }` ; liaison **ACTIVE** obligatoire pour les profils sans droit de gestion. |

## Interface

- **Admin groupe** ([`GroupAdminDetailView.vue`](frontend/src/views/GroupAdminDetailView.vue)) : création de document, indexation, liaison au groupe courant, retrait de la liaison.
- **Mon espace apprenant** ([`LearnerDetailView.vue`](frontend/src/components/learner/LearnerDetailView.vue)) : onglet **Documents** — liste des documents liés au groupe, ouverture d’une modale avec le texte source.

## Mise à jour du contenu

1. Modifier le texte (`PATCH /documents/{id}/` ou recréer un document).
2. Relancer **`POST .../index/`** pour régénérer les chunks.
3. La liaison groupe reste valide si `GroupDocument` est encore `ACTIVE`.

## Hors périmètre

- Pas de lien automatique avec le **référentiel** : le RAG est groupé par classe / groupe, pas par item de référentiel.
- Pas de lecture automatique des dossiers du dépôt Git : importer le texte via l’API ou l’UI.
