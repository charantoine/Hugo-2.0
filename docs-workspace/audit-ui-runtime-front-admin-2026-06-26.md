# Audit runtime — front admin/superadmin/tester (post-UX)

**Date :** 26 juin 2026  
**Périmètre :** `frontend_1.8`, mode `tester`, surfaces admin/superadmin — **audit seul, aucune implémentation**.  
**Références :** audit initial [`audit-ui-runtime-2026-06/AUDIT_ADMIN_UI_RUNTIME.md`](audit-ui-runtime-2026-06/AUDIT_ADMIN_UI_RUNTIME.md), QA post-UX [`audit-ui-runtime-2026-06/QA_POST_UX_2026-06-23.md`](audit-ui-runtime-2026-06/QA_POST_UX_2026-06-23.md), synthèse [`DOC_RUNTIME_UPDATE_2026-06.md`](DOC_RUNTIME_UPDATE_2026-06.md).

---

## 1. Baseline d'exécution

| Élément | Valeur observée |
|--------|------------------|
| Front | `http://localhost:5173` (Vite dev) |
| Mode | `tester` (`.env.local`) |
| API effective | **`/api` → proxy → `127.0.0.1:8000`** (backend local, pas Encoors) |
| Compte | `demo.superadmin` / `demo-superadmin-2026` |
| Organisation | **Demo Hugo Org** (switcher navbar + libellé post-login) |
| Groupe test | **bac pro melec** (`29e5cdb9-de89-49b3-a36e-53b4b9bbbc50`) — **présent** |
| Utilisateur détail testé | `formateur_melec_test` (`4c1b14e6-d990-44b1-ac85-67851ae099c7`) |
| Viewport | 1440×900, Playwright headless |
| Méthode | Connexion réelle → 5 s sans interaction → capture viewport (+ full-page si utile) → smoke fonctionnel |
| Capturé à | `2026-06-26T11:13:05Z` |
| Script | `hugo-hugolucia/frontend_1.8/scripts/audit_admin_ui_runtime_full.mjs` |
| Dossier preuves | [`audit-ui-runtime-front-admin-2026-06-26/screenshots/`](audit-ui-runtime-front-admin-2026-06-26/screenshots/) |
| Manifest | [`screenshots/manifest.json`](audit-ui-runtime-front-admin-2026-06-26/screenshots/manifest.json), journal complet [`screenshots/journal.json`](audit-ui-runtime-front-admin-2026-06-26/screenshots/journal.json) |

**Blocage :** aucun — groupe `bac pro melec` trouvé et utilisé pour toutes les routes groupe.

---

## 2. Tableau par page

Légende risque : **N1** = cosmétique / guidage ; **N2** = confusion parcours ou charge cognitive ; **N3** = rupture onboarding ou exposition expert critique.

| Page | Visible sans scroll | Action principale évidente | Contexte tenant/groupe clair | Éléments trop visibles | Éléments pas assez visibles | Problème principal (runtime réel) | Ajustement recommandé | Risque |
|------|---------------------|----------------------------|------------------------------|------------------------|----------------------------|-----------------------------------|------------------------|--------|
| **`/dashboard`** | Oui — section Administration + 3 groupes testeur | **Oui** — cartes admin (Users, Groupes, Config) distinctes des boutons testeur | Org : navbar + cartes ; groupe : cartes testeur nommées | 3 boutons testeur homogènes (choix groupe peu hiérarchisé) | Indication que l'administration est le chemin « onboarding » | **Corrigé vs audit 23/06** : admin et testeur coexistent clairement | Mettre en avant `bac pro melec` si groupe démo unique ; ou trier groupes démo en premier | **N1** |
| **`/users`** | Oui — formulaire + liste (~15 comptes) | **Oui** — « Créer l'apprenant » (dynamique selon rôle) | **Oui** — texte org dans le corps + switcher | Liste longue à droite (charge visuelle modérée) | Guidage post-création **hors écran** tant qu'aucun compte n'est créé | Guidage « rattacher au groupe » présent mais **conditionnel** (alerte succès) | Bandeau persistant « Après création → Groupes » sous le formulaire | **N1** |
| **`/users/:userId`** | Oui — 2 cartes Profil / Rattachement | **Oui** — « Associer l'utilisateur au groupe » | Org implicite (navbar) ; **groupe non nommé** | 2 paragraphes rôle non modifiable | **Memberships existants absents** (formateur déjà dans bac pro melec non affiché) | Fiche utile pour rattachement initial, aveugle sur l'état courant | Bloc « Déjà membre de : bac pro melec » + lien groupe | **N2** |
| **`/groups-admin`** | Oui — création + liste 3 groupes | **Oui** — « Créer le groupe » | **Oui** — bandeau « Organisation actuelle : Demo Hugo Org » | — | Lien « étape suivante » vers rattachement users | **Corrigé** : LLM replié sous « Paramètres avancés » | Lien retour « Utilisateurs » depuis bandeau onboarding | **N1** |
| **`/groups-admin/:groupId`** | **Oui** — cohorte + début conversation ; expert **replié** | **Modérée** — ajout membre évident ; config profil secondaire | **Oui** — breadcrumb, bandeau org, titre groupe, badge config | Badge « Profil global incomplet » + nom technique `profil_conversationnel_mk1` dans sélecteur | État fallback explicite ; lien profils globaux discret (coin droit) | **Fortement amélioré** vs fourre-tout ; reste dense au scroll (4 accordéons expert) | Renommer affichage sélecteur : nom métier prioritaire, code technique en secondaire | **N2** |
| **`/admin/conversation`** | Oui — hub complet | **Oui** — carte « Profils conversationnels » badge « Chemin principal » | Navbar ; org non répétée dans le corps | Carte « Clôture évaluation (legacy) » encore au même niveau que briques posture | Section tuteur/formateur peu contextualisée (org) | **Corrigé** : hiérarchie profils > briques > compatibilité expert | Retirer « (legacy) » sur clôture si encore utilisée en démo | **N1** |
| **`/admin/conversation/learner/profiles`** | Oui — liste + panneau vide | **Oui** — « Créer un profil vide » | **Oui** — org en alerte orange + légende 7 slots | Deux entrées legacy (« Créer depuis legacy » sidebar + carte) | Détail slots avant sélection d'un profil | Légende complétude **présente** ; noms fixtures `profil_conversationnel_mk1` visibles en liste | Afficher nom métier en titre liste ; code/id en sous-titre discret | **N1** |
| **`/admin/conversation/learner/diagnostic`** | Oui — conduite + orchestrateur lecture seule | Modérée — « Enregistrer la conduite » | Posture claire ; encart vers profils globaux | `diagnostic_mk1` en liste prompts ; templates YAML | Lien direct vers profil global **lié** (pas le slot du profil actif du groupe) | Double édition possible (ici + profils globaux + conduct-profiles) | Encart « profil global du groupe : … » avec lien deep-link | **N2** |
| **`/admin/conversation/learner/reflective_afest`** | Idem diagnostic | Idem | Idem | Idem (`reflexif_mk1` attendu) | Idem | Même pattern que diagnostic | Idem | **N2** |
| **`/admin/conversation/learner/knowledge_review`** | Idem (titre « Buchage ») | Idem | Idem | Idem | Idem | Même pattern | Idem | **N2** |
| **`/admin/conversation/learner/closing`** | Partiel — 1er profil éval visible | Floue — plusieurs « Enregistrer » | Bandeau org + encart profils globaux | 3 blocs prompts + 3 politiques denses ; badges `evaluation-mk1` | Synthèse hard-codée signalée (Phase 3) | Charge cognitive **élevée** malgré encart | Accordéon par profil ; masquer profils TEST en prod démo | **N2** |
| **`/tutor-prompts`** | Formulaire création domine | « Créer le TutorPrompt » | Navbar ; breadcrumb « Prompts tuteur » | CRUD complet, champs techniques (max tokens, phase) | Indication posture / lien profil global | **Navbar : corrigé** (absent). Page reste **très experte** une fois ouverte | Titre métier (« Prompts orchestrateur apprenant ») ; création repliée | **N2** |
| **`/conduct-profiles`** | Oui — sidebar + formulaire | « Enregistrer » | Navbar | Titre technique `TutorConductProfiles` | Lien profil global / groupe | Redondant avec hubs posture ; accès via hub uniquement (OK) | Renommer titre ; bandeau « accès expert — préférer profils globaux » | **N2** |
| **`/referentials`** | Oui — tableau 1 ligne | **Oui** — « Importer un référentiel » | Navbar | — | Lien depuis parcours onboarding (dashboard) | Page **saine** mais hors fil conducteur admin | Lien depuis carte dashboard « Référentiels » ou depuis détail groupe (fait) | **N1** |
| **`/group/:id/referential`** | Oui — 2 cartes | **Oui** — « Associer au groupe » | **Oui** — breadcrumb `Groupes / bac pro melec / Référentiel` | — | Org dans le corps (navbar seulement) | **Corrigé** vs audit initial | Bandeau org optionnel | **N1** |

---

## 3. Notes 1 à 5 par page

Légende : 5 = excellent, 1 = faible.

| Page | Contexte | But | Action | Hiérarchie | Courant / expert | Charge cognitive |
|------|----------|-----|--------|------------|------------------|------------------|
| `/dashboard` | 4 | **5** | **5** | **4** | **4** | 2 |
| `/users` | **5** | **5** | **5** | 4 | 4 | 3 |
| `/users/:id` | 3 | 4 | 4 | 4 | 5 | 2 |
| `/groups-admin` | **5** | 4 | 4 | 4 | 4 | 2 |
| `/groups-admin/:id` | **5** | **4** | **4** | **4** | **3** | **4** |
| `/admin/conversation` | 4 | **5** | **5** | **4** | **4** | 3 |
| `/learner/profiles` | **5** | **5** | 4 | 4 | 4 | 3 |
| Hubs posture (×3) | 4 | 4 | 3 | 3 | 3 | 4 |
| `/learner/closing` | 4 | 3 | 2 | 2 | 2 | **5** |
| `/tutor-prompts` | 3 | 3 | 4 | 3 | 2 | 5 |
| `/conduct-profiles` | 3 | 3 | 4 | 3 | 2 | 4 |
| `/referentials` | 4 | **5** | **5** | **5** | 5 | 1 |
| `/group/.../referential` | **5** | **5** | **5** | **5** | 5 | 1 |

**Moyennes globales (16 surfaces) :** contexte **4,1** · but **4,2** · action **4,1** · hiérarchie **3,8** · courant/expert **3,6** · charge cognitive **3,2**.

**Page la plus problématique :** `/admin/conversation/learner/closing` (charge + multiplicité d'actions).  
**Pages les plus saines :** `/referentials`, `/group/.../referential`, `/users`, `/learner/profiles`.

---

## 4. Vérifications fonctionnelles (runtime)

| Test | Résultat | Détail |
|------|----------|--------|
| Connexion `demo.superadmin` | **OK** | Redirection `/dashboard`, org « Demo Hugo Org » |
| Dashboard → lien Utilisateurs | **OK** | `GET /users` |
| Dashboard → mode testeur (`bac pro melec`) | **OK** | `http://localhost:5173/group/29e5cdb9-…` (3 boutons testeur sur dashboard — ambiguïté UX, pas blocage route) |
| Détail groupe → lien référentiel | **OK** | `data-testid="group-referential-link"` → `/group/…/referential` |
| Hub → Compatibilité → tutor-prompts | **OK** | Route accessible ; **pas** dans navbar principale |
| `/groups-admin` création visible | **OK** | Bandeau org + bouton « Créer le groupe » |
| Groupe `bac pro melec` | **OK** | Titre, cohorte 7 membres, accordéons expert **fermés** par défaut |
| Navbar sans tutor-prompts / conduct-profiles | **OK** | 0 lien expert direct |

**Non testé dans ce run (hors scope capture) :** création effective d'un utilisateur/groupe (POST validé le 23/06 en QA séparée) ; sélection PATCH profil global.

---

## 5. Synthèse

### Confirmé par le runtime (post-UX)

1. **Séparation admin / testeur sur `/dashboard`** — section Administration (3 cartes) + section « Classes / groupes (mode testeur) » avec libellé explicite.
2. **Réordonnancement `/groups-admin/:id`** — bandeau org → cohorte → conversation → référentiel/biblio → accordéons expert (exports, LLM, P0, RAG).
3. **Hub conversation** — profils globaux en « Chemin principal » ; briques posture renommées ; routes expert regroupées en « Compatibilité / Expert ».
4. **Navbar allégée** — `/tutor-prompts` et `/conduct-profiles` **absents** de la barre principale ; accès via hub uniquement.
5. **Continuité référentiel** — lien depuis détail groupe + breadcrumb nommé sur `/group/:id/referential`.
6. **Complétude profils** — légende 7 slots sur `/learner/profiles` ; badge « Profil global incomplet » + `4/7` sur détail groupe.
7. **Groupe démo présent** — `bac pro melec` avec RNCP38878 associé.

### Infirmé ou nuancé (vs audit 23/06 matin)

1. **Dashboard sans entrée admin** → **infirmé** : cartes admin présentes.
2. **Fourre-tout critique sur détail groupe** → **nuancé** : viewport nettement meilleur ; charge reste élevée si l'admin ouvre tous les accordéons expert.
3. **tutor-prompts / conduct-profiles dans navbar** → **infirmé** pour la navbar ; **confirmé** que les pages restent denses une fois ouvertes.
4. **Tenant faible sur `/users`** → **confirmé bon** ; **groups-admin** et hubs posture restent navbar-first (sauf closing).

### Points encore ouverts (non bloquants)

1. **Noms techniques en UI** — `profil_conversationnel_mk1`, `diagnostic_mk1`, `evaluation-mk1` : données/fixtures, pas concept produit ; visibles pour superadmin expert.
2. **`/users/:id`** — pas de liste des memberships existants.
3. **`/learner/closing`** — page la plus chargée ; plusieurs profils/politiques en parallèle.
4. **Trois groupes testeur au dashboard** — dont `_ux_audit_tmp_group2` (bruit démo).

---

## 6. Top adaptations les plus rentables (priorisées post-audit)

| # | Adaptation | Page(s) | Impact | Effort | Risque |
|---|------------|---------|--------|--------|--------|
| 1 | Afficher **memberships existants** sur fiche utilisateur | `/users/:id` | Fort (cohérence rattachement) | Faible | N2 |
| 2 | **Nom métier** prioritaire dans sélecteurs profil (id technique en secondaire) | Détail groupe, liste profils | Moyen (lisibilité démo) | Faible | N1 |
| 3 | **Accordéon / repli** sur `/learner/closing` (1 profil visible à la fois) | closing | Fort (charge cognitive) | Moyen | N2 |
| 4 | Bandeau **guidage persistant** post-création user (pas seulement alerte succès) | `/users` | Moyen | Très faible | N1 |
| 5 | Titre métier + création repliée sur pages expert | tutor-prompts, conduct-profiles | Moyen | Faible | N2 |
| 6 | Filtrer ou trier groupes **démo** sur dashboard testeur | `/dashboard` | Faible/moyen | Très faible | N1 |
| 7 | Deep-link hub posture → slot du profil global actif du groupe | hubs posture | Moyen | Moyen | N2 |

*Les adaptations 1–7 du rapport du 23/06 (réordonnancement détail groupe, dashboard admin, navbar expert, etc.) sont **déjà livrées** — voir QA post-UX.*

---

## 7. À vérifier runtime distant (Encoors)

Constats locaux **non extrapolés** à Encoors sans re-capture :

| Sujet | Local (26/06) | À vérifier Encoors |
|-------|---------------|-------------------|
| API / proxy | `/api` → `127.0.0.1:8000` | `.env` peut pointer `hugoback.encoors.com` — libellés profils/comptes peuvent différer |
| Navbar expert | tutor-prompts absent | Déploiement même branche `frontend_1.8` ? |
| Groupe démo | `bac pro melec` + RNCP38878 | Existence parité données |
| Badge config | « Profil global incomplet » 4/7 | Même profil rattaché ? |
| Version affichée | Footer « Hugo 2.0 — Lucia » | Cohérence version produit vs branche 1.8 |

---

## 8. Captures et manifest

**Dossier :** [`audit-ui-runtime-front-admin-2026-06-26/screenshots/`](audit-ui-runtime-front-admin-2026-06-26/screenshots/)

| Fichier | Route | Full-page |
|---------|-------|-----------|
| `01-dashboard.png` | `/dashboard` | non |
| `02-users.png` | `/users` | oui |
| `03-user-detail.png` | `/users/:userId` | non |
| `04-groups-admin.png` | `/groups-admin` | non |
| `05-group-detail-viewport.png` | `/groups-admin/:groupId` | non |
| `05-group-detail-full.png` | `/groups-admin/:groupId` | oui |
| `06-admin-conversation.png` | `/admin/conversation` | oui |
| `07-learner-profiles.png` | `/admin/conversation/learner/profiles` | oui |
| `08-diagnostic.png` | `…/learner/diagnostic` | oui |
| `09-reflective_afest.png` | `…/learner/reflective_afest` | oui |
| `10-knowledge_review.png` | `…/learner/knowledge_review` | oui |
| `11-closing.png` | `…/learner/closing` | oui |
| `12-tutor-prompts.png` | `/tutor-prompts` | oui |
| `13-conduct-profiles.png` | `/conduct-profiles` | oui |
| `14-referentials.png` | `/referentials` | non |
| `15-group-referential.png` | `/group/:id/referential` | oui |

**Manifest machine :** [`screenshots/manifest.json`](audit-ui-runtime-front-admin-2026-06-26/screenshots/manifest.json)  
**Journal (baseline + functional) :** [`screenshots/journal.json`](audit-ui-runtime-front-admin-2026-06-26/screenshots/journal.json)

---

## 9. Conclusion

L'audit runtime du **26/06** confirme que les ajustements UX livrés le **23/06** tiennent en conditions réelles : le parcours admin est **lisible au premier regard**, la séparation **admin / testeur / expert** est nettement meilleure qu'au audit initial, et les actions principales (création user/groupe, hub profils, lien référentiel) **correspondent** aux routes attendues.

Les résidus prioritaires sont **localisés** : fiche utilisateur sans état de rattachement, noms techniques de fixtures encore visibles pour le superadmin, et charge cognitive sur la clôture/évaluation. Aucun écart bloquant route/endpoint constaté sur la baseline locale.

**Prochaine sortie utile (hors ce document) :** micro-lot UX résiduel (memberships user, titres métier, closing) si priorisé produit ; re-capture Encoors pour valider parité navbar et données démo.
