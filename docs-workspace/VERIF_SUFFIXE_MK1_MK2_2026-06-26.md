# Vérification exhaustive — suffixes `mk1` / `mk2` (pas de dérive UX)

**Date :** 26 juin 2026  
**Périmètre :** workspace `/Users/machin/Desktop/Zone de travail Hugo` (hors `venv/`, `node_modules/`, `.git/`)  
**Alignement rappelé :** `_mk1` / `_mk2` = marqueurs internes de version (Mark One / Mark Two) sur fixtures, prompts, profils — **pas** une notion produit à exposer en UI.

---

## 1. Méthode de recherche

```bash
# Recherche ciblée (outil workspace + exclusions implicites venv/node_modules)
rg -n --glob '!**/.venv/**' --glob '!**/venv/**' --glob '!**/node_modules/**' \
  -i 'mk1|mk2|profil_conversationnel_mk1|diagnostic_mk1|reflective_afest_mk1|knowledge_review_mk1|profil mk1|mode mk1' \
  "/Users/machin/Desktop/Zone de travail Hugo"

# Compléments par zone sensible
rg -n 'mk1|mk2' hugo-hugolucia/frontend_1.8/src
rg -n 'mk1|mk2' hugo_back/apps
rg -n 'mk1|mk2' docs-workspace
```

Lecture manuelle des composants admin listés (`GroupAdminDetailView`, `learnerProfileCompleteness.js`, etc.) pour confirmer l’absence de libellés codés en dur.

---

## 2. Tableau des occurrences par catégorie

| Catégorie | Signification | Occurrences |
|-----------|---------------|-------------|
| **A** | Fixture / id interne / test | 1 |
| **B** | Doc neutre + garde-fou (suffixe interne explicite) | 18 |
| **C** | UI / libellé utilisateur | 0 (après correction) |
| **D** | Spéculation produit / backlog UX mk1 | 0 (après corrections antérieures + cette passe) |

### Détail

| Fichier | Ligne / extrait | Cat. | Commentaire |
|---------|-----------------|------|-------------|
| `hugo_back/apps/hugo/tests/test_learner_conversation_global_profile.py` | `code="diag-mk1"` | **A** | Code TutorPrompt de test pytest, hors UI |
| `docs-workspace/DOC_RUNTIME_UPDATE_2026-06.md` | 5 mentions `_mk1` / garde-fou | **B** | Fixture démo + interdiction d’exposer en UI |
| `docs-workspace/audit-ui-runtime-2026-06/AUDIT_ADMIN_UI_RUNTIME.md` | 5 mentions | **B** | Audit historique ; badge `{nom}` ; pas « Profil mk1 » |
| `docs-workspace/audit-ui-runtime-2026-06/QA_POST_UX_2026-06-23.md` | section Note mk1 | **B** | Documente l’**erreur passée** à ne pas reproduire |
| `docs-workspace/03_ETAT_PRODUIT_REEL.md` | encart §6 | **B** | Fixture id + précision suffixe |
| `docs-workspace/MINI_SPEC_PROFILS_CONVERSATIONNELS_APPRENANT.md` | encart §5 | **B** | Idem |
| `hugo-hugolucia/frontend_1.8/src/**` | *(aucune)* | — | **Aucun** `mk1`/`mk2` dans le code front après correction |
| `hugo-hugolucia/frontend_1.8/src/utils/learnerProfileCompleteness.js` | `Profil ${profile.name}` | **OK** | Utilise `profile.name` API, jamais le suffixe en dur |
| Captures `screenshots-post-ux/05-group-detail-viewport.png` | badge « Profil global incomplet » | **OK** | Pas de libellé « Profil mk1 » codé ; si `profile.name` en base contient `_mk1`, c’est le **nom enregistré** affiché tel quel (donnée démo), pas une notion produit inventée par le front |

**`mk2` :** aucune occurrence produit dans le workspace (hors mention préventive dans `QA_POST_UX` §Note).

---

## 3. Corrections effectuées (cette passe)

| Fichier | Type | Action |
|---------|------|--------|
| `hugo-hugolucia/frontend_1.8/src/views/admin/LearnerConversationProfilesView.vue` | **C → corrigé** | Suppression de l’exemple UI `<code>diagnostic_mk1</code>` ; remplacé par formulation générique (« identifiant technique du TutorPrompt ») |
| `docs-workspace/audit-ui-runtime-2026-06/AUDIT_ADMIN_UI_RUNTIME.md` | **D → nuancé** | Ligne diagnostic : plus de `diagnostic_mk1` comme libellé ; formulation « suffixe `_mk1` fixture » |
| `docs-workspace/audit-ui-runtime-2026-06/AUDIT_ADMIN_UI_RUNTIME.md` | **D → nuancé** | § confirmé : « profil global rattaché » au lieu de « chemin réel mk1 » |
| `docs-workspace/MINI_SPEC_PROFILS_CONVERSATIONNELS_APPRENANT.md` | **D → nuancé** | Idem — identifiant fixture, pas libellé à promouvoir |
| `docs-workspace/03_ETAT_PRODUIT_REEL.md` | **D → nuancé** | Encart §6 aligné |

### Corrections antérieures (déjà en place, confirmées)

| Fichier | Action |
|---------|--------|
| `QA_POST_UX_2026-06-23.md` | Retrait backlog « nom mk1 sur hubs » ; note garde-fou |
| `learnerProfileCompleteness.js` | Badge via `profile.name` uniquement |
| `GroupAdminDetailView.vue` | Idem ; pas de chaîne `mk1` |

---

## 4. Occurrences restantes A / B (non-UX)

| Occurrence | Pourquoi c’est acceptable |
|------------|---------------------------|
| `diag-mk1` (test back) | Identifiant technique de test ; jamais rendu admin |
| `profil_conversationnel_mk1` dans docs | **Id de fixture** de la démo bac pro melec, toujours accompagné de « suffixe interne, pas notion UI » |
| Mentions « profil mk1 » dans `QA_POST_UX` | **Méta** : description de la dérive corrigée, pas une recommandation |
| Garde-fou « ne pas faire badge Profil mk1 » dans `DOC_RUNTIME_UPDATE` | Règle négative explicite |

---

## 5. Zones sensibles — contrôle code front

| Composant | `mk1`/`mk2` en dur ? | Libellés utilisateur |
|-----------|----------------------|----------------------|
| `GroupAdminDetailView.vue` | Non | `profile.name`, complétude n/7, fallback |
| `GroupsAdminListView.vue` | Non | Org, groupe |
| `AdminConversationIndexView.vue` | Non | Briques / profils |
| `LearnerConversationProfilesView.vue` | Non (corrigé) | Nom profil, 4/7, postures |
| `LearnerModeHubView.vue` | Non | Encart générique profils globaux |
| `LearnerClosingEvaluationView.vue` | Non | Idem |
| `DashboardView.vue` | Non | Administration |
| `UsersView.vue` | Non | Rôles, org |
| `learnerProfileCompleteness.js` | Non | `profile.name` + complétude |

---

## 6. Synthèse

> **Il ne reste plus de texte ou de UI qui surinterprète `mk1` / `mk2` comme notion produit.** Les suffixes sont uniquement utilisés comme marqueurs internes de version (fixtures, ids de test) ou documentés comme tels, avec garde-fous explicites contre toute exposition UX.

**Point de vigilance données (hors code) :** si un profil en base s’appelle littéralement `profil_conversationnel_mk1`, le front affichera ce **nom enregistré** via `profile.name`. Ce n’est pas une dérive UX du code ; pour une démo plus lisible, renommer le profil côté données (hors périmètre de cette vérification).

---

## 7. Renvoi

- [`QA_POST_UX_2026-06-23.md`](audit-ui-runtime-2026-06/QA_POST_UX_2026-06-23.md) — note alignement mk1  
- [`DOC_RUNTIME_UPDATE_2026-06.md`](DOC_RUNTIME_UPDATE_2026-06.md) — garde-fou §3
