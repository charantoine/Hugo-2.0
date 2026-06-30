# Mini-spec — Profils conversationnels globaux apprenant

**Statut :** implémenté (v1 incrémentale)  
**Périmètre :** bibliothèque **apprenant** uniquement — tuteur / formateur inchangés.

## 1. Modèle cible

**`LearnerConversationGlobalProfile`** (`learner_conversation_global_profile`)

| Champ | Rôle |
|-------|------|
| `name` | Nom global du profil |
| `description` | Texte libre |
| `status` | `draft` / `active` / `inactive` |
| `organisation` | Portée tenant |
| `is_default` | Défaut org (un seul actif par org) |
| `diagnostic_*` / `reflective_*` / `knowledge_review_*` | Slots TutorPrompt + TutorConductProfile |
| `evaluation_prompt_profile` | Slot évaluation finale |
| `evaluation_policy` | Politique org (group=null) optionnelle |

**Relations :** FK vers objets existants — pas de duplication de contenu prompt.

## 2. Compatibilité / fallback runtime

Priorité `_resolve_tutor_prompt(session, posture)` :

1. `session.tutor_prompt` (override explicite legacy)
2. Profil global résolu → slot posture
3. `group.default_tutor_prompt` (legacy)
4. `TutorPrompt.is_default` org

Priorité profil global (`resolve_learner_conversation_global_profile`) :

1. `session.learner_conversation_profile`
2. `group.default_learner_conversation_profile`
3. profil org `is_default=True` + `status=active`

Conduite : `resolve_conduct_profile(..., session=)` → slot conduct du profil global, sinon résolution org/système inchangée.

Évaluation : code profil depuis `evaluation_prompt_profile` du profil global si présent ; policy org liée au profil si renseignée.

## 3. Migration

- Migration `0020` (hugo) : modèle + `HugoSession.learner_conversation_profile`
- Migration `0018` (referentials) : `Group.default_learner_conversation_profile`
- **Pas de backfill automatique** — orgs non migrées restent en legacy.
- API : `/hugo/learner-conversation-profiles/` (CRUD tenant)
- Admin front : `/admin/conversation/learner/profiles`

## 4. Risques surveillés

- Multi-tenant : validation FK même org (serializer + GroupSerializer)
- Pas de suppression TutorPrompt / conduct / evaluation existants
- Hubs par posture + legacy `/tutor-prompts` conservés
- Tuteur / formateur : aucun endpoint modifié hors périmètre apprenant

## 5. Legacy / dépréciation

| Élément | Statut |
|---------|--------|
| `Group.default_tutor_prompt` | Conservé, fallback après profil global |
| Hubs posture `/admin/conversation/learner/:posture` | Mode expert, label legacy |
| `/tutor-prompts`, `/conduct-profiles` | Legacy 1.6, libellés corrigés |

> **Confirmé / nuancé par audit UI 2026-06** ([`DOC_RUNTIME_UPDATE_2026-06.md`](DOC_RUNTIME_UPDATE_2026-06.md))  
> - Sur Demo Hugo Org, un profil global de démo est le chemin runtime réel (identifiant fixture `profil_conversationnel_mk1` : `_mk1` = suffixe de version interne, **pas** un libellé à promouvoir en UI) ; le libellé « (legacy) » sur les cartes hub posture est **trompeur** (recommandation N1 : « Briques par posture »).  
> - Les pages `/tutor-prompts` et `/conduct-profiles` restent accessibles depuis la **navbar** principale en mode testeur — pas seulement via le hub.  
> - Le sélecteur profil global sur `/groups-admin/:id` masque le prompt legacy groupe quand un profil est sélectionné — comportement conditionnel confirmé en runtime.

**Prochaine étape (hors v1) :** backfill automatique profil default org ; dépréciation UI legacy après migration orgs.
