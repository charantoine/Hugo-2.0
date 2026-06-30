# DOC_RUNTIME_UPDATE_2026-06 — Recalage doc ↔ audit runtime admin/superadmin

**Date :** 23 juin 2026  
**Objet :** aligner la bibliothèque `docs-workspace` (et les packs photo réelle A1–A4) avec les constats d'exécution réelle du front admin/superadmin en mode `tester`.  
**Audit source :** [`audit-ui-runtime-2026-06/AUDIT_ADMIN_UI_RUNTIME.md`](audit-ui-runtime-2026-06/AUDIT_ADMIN_UI_RUNTIME.md) + [`audit-ui-runtime-2026-06/screenshots/`](audit-ui-runtime-2026-06/screenshots/)

---

## Sources mobilisées

| Source | Rôle dans ce recalage |
|--------|----------------------|
| `documentation_photo_reel_2026_06_22/A1`–`A4` | Socle photo réelle (référence Perplexity) — **non réécrit** ici |
| `docs-workspace/03_ETAT_PRODUIT_REEL.md` | État produit montrable + mode testeur |
| `docs-workspace/09_PARCOURS_DEMO_ET_SCENARIOS.md` | Parcours démo / testeur |
| `docs-workspace/MINI_SPEC_PROFILS_CONVERSATIONNELS_APPRENANT.md` | Contrat profils globaux |
| `docs-workspace/10_FICHE_RUNTIME_PROD_ENCOORS.md` | Runtime distant (non exercé dans l'audit UI) |
| Audit TutorPrompt vs profils (conversation 2026-06-23) | Résolution runtime `LearnerConversationGlobalProfile` vs legacy |
| Audit UI runtime admin (2026-06-23) | Lisibilité, hiérarchie, top 10 adaptations |

---

## Baseline d'exécution (audit UI 2026-06)

| Élément | Valeur |
|--------|--------|
| Front | `http://localhost:5173`, `VITE_FRONTEND_MODE=tester` |
| API | `VITE_API_URL=/api` → `127.0.0.1:8000` (**local**, pas Encoors) |
| Compte | `demo.superadmin` / `demo-superadmin-2026` |
| Organisation | **Demo Hugo Org** |
| Groupe pivot | **bac pro melec** (`29e5cdb9-de89-49b3-a36e-53b4b9bbbc50`) |
| Profil global observé (fixture démo) | `profil_conversationnel_mk1` — le suffixe `_mk1` est un **marqueur de version interne**, pas une notion UI |

---

## 1. Cartographie des fichiers concernés

| Rôle documentaire | Emplacement | Action dans ce recalage |
|-------------------|-------------|-------------------------|
| Socle réel observé | `documentation_photo_reel_2026_06_22/A1_SOCLE_REEL_OBSERVE.md` | Référence — §5–6 nuancés ci-dessous |
| Cartographie fonctionnelle | `documentation_photo_reel_2026_06_22/A2_CARTOGRAPHIE_FONCTIONNELLE_EXISTANT.md` | §11 Administration — complété |
| Objets / contrats | `documentation_photo_reel_2026_06_22/A3_…` | Inchangé (pas de contradiction UI) |
| Architecture / pipelines | `documentation_photo_reel_2026_06_22/A4_…` | Inchangé pour l'audit UI |
| Écarts / A_VERIFIER | `documentation_photo_reel_2026_06_22/A6_…` | §TODO Encoors mis à jour ici §5 |
| État produit workspace | `docs-workspace/03_ETAT_PRODUIT_REEL.md` | **Encart ajouté** §6 |
| Parcours démo | `docs-workspace/09_PARCOURS_DEMO_ET_SCENARIOS.md` | **Encart ajouté** §3 |
| Mini-spec profils | `docs-workspace/MINI_SPEC_PROFILS_CONVERSATIONNELS_APPRENANT.md` | **Encart ajouté** §5 |
| Audit UI runtime | `docs-workspace/audit-ui-runtime-2026-06/` | **Créé** (`AUDIT_ADMIN_UI_RUNTIME.md` + screenshots existants) |

---

## 2. Réel confirmé par l'audit runtime

### 2.1 Administration / IAM

| Constat | Preuve runtime | Doc antérieure |
|---------|----------------|----------------|
| `/users` : org active visible, création LEARNER / TUTOR / **TRAINER** (SUPERADMIN) | `02-users.png`, E2E TRAINER 23/06 | A2 §11 « admin comptes incomplet » — **nuancé** : TRAINER créable depuis 23/06 |
| `/users/:id` : rôle non modifiable, association groupe fonctionnelle | `03-user-detail.png` | Confirmé A2 |
| Mot de passe superadmin démo ≠ `demo` | Login audit | À documenter dans fiche comptes 11 (toujours **A_VERIFIER** prod) |

### 2.2 Onboarding cohorte (superadmin)

| Constat | Preuve | Impact doc |
|---------|--------|------------|
| `/dashboard` : CTA « Voir les apprenants » → `/group/:id` (testeur), **pas** admin | `01-dashboard.png` | **Écart** vs parcours onboarding implicite dans `09` §3 |
| `/groups-admin/:id` : colonne gauche = exports + LLM + profil + P0 + RAG ; membres à droite | `05-group-detail-full.png` | Confirme lecture code `GroupAdminDetailView.vue` ; **pire visuellement** que la doc ne le disait |
| Pas de lien référentiel depuis détail groupe admin | Capture groupe vs `15-group-referential.png` | A2 §5 RAG — parcours orphelin confirmé |
| `/referentials` et `/group/:id/referential` : pages claires | `14`, `15` | Confirmé A2 |

### 2.3 Configuration conversationnelle

| Constat | Preuve | Impact doc |
|---------|--------|------------|
| Hub `/admin/conversation` : cartes posture libellées « (legacy) » alors qu’un profil global est le chemin réel sur la démo | `06-admin-conversation.png` + détail groupe | **Nuance** `MINI_SPEC` §5 : legacy = surface expert, pas « non utilisé » |
| `/admin/conversation/learner/profiles` : pivot produit lisible ; badge 4/7 sans légende | `07-learner-profiles.png` | Confirmé implémentation ; UX à améliorer (N1) |
| Fixture `profil_conversationnel_mk1` sur bac pro melec (`_mk1` = suffixe version) ; prompt legacy groupe masqué si profil sélectionné | Détail groupe | Confirme résolution profil global — **ne pas** exposer `_mk1` en UI |
| `/tutor-prompts` et `/conduct-profiles` encore dans **navbar** principale | `12`, `13` + `TesterLayout.vue` | **Contredit** l'hypothèse « relégués au hub uniquement » |

### 2.4 TutorPrompt vs profils globaux (audit code + runtime Demo Hugo Org)

| Constat | Statut |
|---------|--------|
| Runtime Demo Hugo Org + profil global de démo : postures résolues via slots du profil (prompts nommés `*_mk1` en base = version interne) | **RÉEL OBSERVÉ** |
| `TutorPrompt` reste dans le moteur (`_resolve_tutor_prompt`, fallback legacy) | **RÉEL OBSERVÉ** — pas supprimé |
| Sessions / groupes sans profil global → fallback `group.default_tutor_prompt` ou org `is_default` | **RÉEL OBSERVÉ** |
| `POST /hugo/sessions/` accepte `learner_conversation_profile_id` (PR-B1, 23/06) | **RÉEL OBSERVÉ** local |

---

## 3. Écarts doc « théorique » ↔ runtime

| Zone | Doc / hypothèse antérieure | Runtime 2026-06 | Statut |
|------|---------------------------|-----------------|--------|
| Contexte tenant `/users` | Faible (audit code) | Bon (texte + switcher) | **Infirmé** |
| Contexte tenant pages groupe | Non décrit | Faible (navbar seule) | **Confirmé** |
| Dashboard comme entrée admin | Liste groupes « neutre » | Orienté testeur uniquement | **Écart confirmé** |
| Legacy relégué au hub | Hubs + mini-spec | Navbar expose encore CRUD expert | **Écart confirmé** |
| Admin comptes incomplet | A2 §11 | TRAINER créable ; guidage post-création manquant | **Nuancé** |
| Conduct-profiles API Encoors | Absent (A1 §5, doc 10) | Non testé dans audit UI | **Toujours A_VERIFIER** distant |
| Équivalence API `.env` défaut | `03` : Encoors par défaut | Audit UI : `.env.local` force local | **Précision** : baseline dépend des fichiers env actifs |

**Garde-fou nommage `_mk1` / `_mk2` :** les suffixes dans les noms de fixtures (`profil_conversationnel_mk1`, `diagnostic_mk1`, …) sont des **marqueurs de version interne** (première itération / Mark One), pas des concepts produit à afficher dans l’UI admin. Ne pas dériver de recommandations UX du type « badge Profil mk1 » ou « encart mk1 sur hubs posture ».

---

## 4. Corrections appliquées dans `docs-workspace`

| Fichier | Type de correction |
|---------|-------------------|
| `03_ETAT_PRODUIT_REEL.md` | Encart §6 — surfaces admin runtime + lien audit |
| `09_PARCOURS_DEMO_ET_SCENARIOS.md` | Encart §3 — onboarding admin vs testeur |
| `MINI_SPEC_PROFILS_CONVERSATIONNELS_APPRENANT.md` | Encart §5 — libellés legacy vs usage réel ; précision suffixe `_mk1` |
| `audit-ui-runtime-2026-06/AUDIT_ADMIN_UI_RUNTIME.md` | Rapport d'audit persisté (était en sortie chat uniquement) |
| Ce fichier | Synthèse croisée A1–A4 ↔ runtime |

**Non modifié (volontairement) :** contenu intégral A1–A4 dans `documentation_photo_reel_2026_06_22/` — ce pack reste la photo réelle de référence ; les encarts ci-dessus et dans `03`/`09`/`MINI_SPEC` portent les corrections minimales côté workspace.

---

## 5. TODO runtime distant / Encoors

Points **non éclaircis** par l'audit UI local (baseline B — voir `07_RUNTIME_DEMO_REFERENCE.md`) :

| Point | Local (audit 23/06) | Encoors | Action |
|-------|---------------------|---------|--------|
| Parité pages admin (layout, navbar, TRAINER) | Observé | **A_VERIFIER** | Re-capture sur baseline A après deploy |
| `GET/POST /hugo/conduct-profiles/` | Présent | Absent (sonde 12/06 et 23/06) | **ÉCART CONFIRMÉ** — doc 10 |
| `evaluation-readiness`, `finalize-evaluation` | Présent local | **A_VERIFIER** | Sonde HTTP authentifiée |
| CORS `localhost:5173` | OK via proxy `/api` | Refusé (doc 10) | Démo distante = baseline A sans proxy |
| Flags `HUGO_P0_*` prod | Défauts locaux connus | Inconnus | Test comportemental |
| Comptes `demo.superadmin` sur Encoors | Local `hugo_poc` | **A_VERIFIER** | Fiche comptes 11 |
| SSE `/messages/stream/` | Endpoint local | Route urlconf ; flux non testé | Test authentifié |
| Build front servi en prod | `frontend_1.8` dev | `frontend/` vs `frontend_1.8/` — **AMBIGU** | Doc 01, A1 §4 |

---

## 6. Prochaine sortie utile (étape 2 — implémentation)

Backlog UX **sans moteur ni P0**, ordonné par rentabilité (cf. audit §D) :

1. **N2** — `GroupAdminDetailView.vue` : réordonnancement (membres / profil avant expert).
2. **N1** — Badge état config profil sur détail groupe.
3. **N1** — Bandeau org dans corps de page (`groups-admin`, hubs).
4. **N1** — Hub conversation : retirer « (legacy) » des cartes posture actives.
5. **N3** — `DashboardView.vue` : liens admin + libellé testeur explicite.
6. **N3** — `TesterLayout.vue` : retirer `/tutor-prompts` et `/conduct-profiles` de la navbar.
7. **N3** — Lien référentiel depuis détail groupe.
8. **N1** — Légende complétude 4/7 sur profils globaux.
9. **N1** — Guidage post-création compte → rattachement groupe.
10. **N1** — Replier LLM à la création de groupe.

---

## 7. Patron méthodo (synthèse)

| Couche | Contenu |
|--------|---------|
| **Réel confirmé** | §2 — exécution locale `demo.superadmin` + captures |
| **Cible 2.0** | Profil global pivot ; surfaces legacy non fonctionnelles à terme — **pas encore livré** |
| **Écarts** | §3 — doc théorique vs runtime |
| **A_VERIFIER** | §5 — Encoors et prod |
| **Prochaine sortie** | §6 — implémentation front N1–N3 |
