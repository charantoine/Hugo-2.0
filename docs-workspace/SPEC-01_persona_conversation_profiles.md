# SPEC-01 — Contrat minimal profils persona tuteur / formateur

**Chantier :** orchestrateur tuteur/formateur — Pass 2 (implémentation)  
**Baseline :** B (`frontend_1.8` + `hugo_back` local)  
**Date :** 2026-07-01

---

## Sources mobilisées

- `docs-workspace/audit_orchestrateur_tuteur_formateur.md` (Pass 1)
- `hugo_back/apps/hugo/models.py` — `PersonaConversationProfile`, `TutorPrompt.persona_scope`
- `hugo_back/apps/hugo/services/persona_session.py`
- `hugo_back/apps/hugo/views_persona_conversation_profiles.py`

---

## Réel confirmé (`REL OBSERV` / `REL OBSERV PARTIEL`)

| Objet | Statut | Tag |
|-------|--------|-----|
| Modèle `PersonaConversationProfile` (org, persona, code, status, is_default, FK `tutor_prompt`) | Livré Pass 2 | **REL OBSERV PARTIEL** |
| `TutorPrompt.persona_scope` : `learner` \| `tutor` \| `trainer` | Livré Pass 2 | **REL OBSERV PARTIEL** |
| `HugoSession.persona_conversation_profile` (FK nullable) | Livré Pass 2 | **REL OBSERV PARTIEL** |
| Résolution persona early-return dans `_resolve_tutor_prompt` | Livré Pass 2 | **REL OBSERV PARTIEL** |
| Injection `persona_context_block` / `tutor_context_block` / `trainer_context_block` **uniquement si session persona** | Livré Pass 2 — fix KeyError P1 | **CART CONFIRM** |
| API CRUD `/hugo/persona-conversation-profiles/` + preview sans LLM | Livré Pass 2 | **REL OBSERV PARTIEL** |
| CTA éval/synthèse → 404 sur sessions persona | Livré Pass 2 | **REL OBSERV PARTIEL** |
| UI admin `/admin/conversation/{tutor,trainer}/profiles` | Livré Pass 2 | **REL OBSERV PARTIEL** |
| `LearnerConversationGlobalProfile` + résolveurs apprenant | Inchangés | **REL OBSERV** |
| `build_contract_ui_state` / contrat `GET /ui-state/` | Inchangés côté backend ; **Décision B** (01/07) : contract engagement **front apprenant** ; persona `loadUiState: false` | **REL OBSERV** + **doctrine provisoire** |
| Mémoire non injectée LLM | Inchangée | **REL OBSERV** |
| RAG lexical | Inchangé | **REL OBSERV** |

---

## Cible 2.0 (`CIBLE`)

- Profils conversationnels **persona** (tuteur / formateur) administrables, avec templates system/user et métadonnées org.
- Affectation par session (`persona_conversation_profile_id`) ou détection legacy (`tutor_workspace_*`) / rôle TRAINER.
- Preview rendu template sans appel LLM.
- Chaîne apprenant strictement isolée.

---

## Contrat minimal (codable)

### PersonaConversationProfile

```json
{
  "id": "uuid",
  "organisation": "uuid (read-only, tenant)",
  "persona": "tutor | trainer",
  "code": "slug unique par (organisation, persona)",
  "name": "string",
  "description": "string",
  "status": "draft | active | inactive",
  "is_default": "boolean",
  "tutor_prompt": {
    "id": "uuid",
    "system_template": "string",
    "user_template": "string",
    "persona_scope": "tutor | trainer"
  }
}
```

**Création :** soit `tutor_prompt_id` existant, soit `system_template` + `user_template` (crée/met à jour un `TutorPrompt` scoped).

### Affectation session

- Champ write : `persona_conversation_profile_id` sur `POST/PATCH /hugo/sessions/`.
- Legacy P1 : `learner_conversation_profile_id` avec code `tutor_workspace_*` → détection persona tuteur (non modifié côté résolveur apprenant).
- Rôle `TRAINER` sans profil apprenant actif → persona formateur par défaut.

### Variables template persona (injection conditionnelle)

| Variable | Portée |
|----------|--------|
| `persona_context_block` | Sessions persona |
| `tutor_context_block` | Alias tuteur |
| `trainer_context_block` | Alias formateur |
| `situation_content`, `history_block`, `referential_block` | Communes |

**Interdit Pass 2 :** injection mémoire session dans prompts apprenant.

### Endpoints

| Méthode | Chemin | Rôle |
|---------|--------|------|
| GET/POST | `/hugo/persona-conversation-profiles/?persona=` | Liste / création |
| GET/PATCH/DELETE | `/hugo/persona-conversation-profiles/{id}/` | Détail |
| POST | `/hugo/persona-conversation-profiles/{id}/preview-render/` | Preview sans LLM |

---

## Écarts

| Écart | Statut |
|-------|--------|
| Affectation persona au niveau **groupe** (policy) | Hors Pass 2 — **CIBLE** ultérieure |
| Campaign E2E persona comparable protocole apprenant | Absent — **À VÉRIFIER** |
| Playwright FRONT persona | Non livré Pass 2 — **À VÉRIFIER** |

---

## Non-régression apprenant

Tests rejoués après implémentation Pass 2 (voir `pass2_non_regression_log` ci-dessous).

---

## Prochaine sortie utile

1. Campaign E2E persona tuteur/formateur (TEST-02 Playwright).
2. Affectation groupe → profil persona par défaut.
3. Doc runtime Encoors — marquer **À VÉRIFIER** (baseline B uniquement).

---

## Rappel discipline

Toute surface persona nouvelle reste **REL OBSERV PARTIEL** tant qu’elle n’a pas de campaign E2E comparable au protocole apprenant (clusters 3/15/16).
