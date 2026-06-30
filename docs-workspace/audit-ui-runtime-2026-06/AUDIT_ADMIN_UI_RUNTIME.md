# Audit runtime — lisibilité front admin/superadmin

**Date :** 23 juin 2026  
**Périmètre :** front `frontend_1.8`, mode `tester`, surfaces admin/superadmin — **sans modification moteur ni P0**.  
**Synthèse croisée :** [`DOC_RUNTIME_UPDATE_2026-06.md`](../DOC_RUNTIME_UPDATE_2026-06.md)

---

## Baseline d'exécution

| Élément | Valeur observée |
|--------|------------------|
| Front | `http://localhost:5173` (Vite dev) |
| Mode | `tester` (`.env.local`) |
| API effective | **`/api` → proxy → backend local `127.0.0.1:8000`** (pas Encoors) |
| Raison | `.env.local` / `.env.development.local` écrasent `.env.development` (`https://hugoback.encoors.com`) |
| Compte | `demo.superadmin` / `demo-superadmin-2026` |
| Organisation | **Demo Hugo Org** (`dc1e8465-0ff2-4d66-bfbb-a0f8e7a23b3d`) |
| Groupe test | **bac pro melec** (`29e5cdb9-de89-49b3-a36e-53b4b9bbbc50`) |
| Méthode | Playwright headless 1440×900, 5 s d'attente sans interaction puis capture ; navigation réelle page par page |
| Preuves | [`screenshots/`](screenshots/) (+ [`manifest.json`](screenshots/manifest.json)) |
| Script | `hugo-hugolucia/frontend_1.8/scripts/audit_admin_ui_capture.mjs` |

**Note Encoors :** non utilisée dans ce run (baseline locale active). Les constats structurels restent valides ; seuls les libellés de données (noms de profils, comptes) peuvent différer sur Encoors.

---

## A. Tableau par page

| Page | Baseline | Visible sans scroll | Action principale évidente ? | Contexte tenant/groupe clair ? | Éléments trop visibles | Éléments pas assez visibles | Problème principal (runtime réel) | Ajustement recommandé | Niveau |
|------|----------|---------------------|----------------------------|--------------------------------|------------------------|----------------------------|-----------------------------------|----------------------|--------|
| **`/dashboard`** | Local tester | Oui (tout) | **Non** — bouton « Voir les apprenants » mène au **testeur** `/group/:id`, pas à l'admin | Org : navbar uniquement | Espace vide, version plateforme | Liens admin (Users, Groupes admin, Config) | Mauvais point d'entrée admin ; action orientée encadrant, pas IAM/cohorte | Ajouter 3 liens admin sous le titre ; renommer bouton « Voir les apprenants (testeur) » | **N3** |
| **`/users`** | Local tester | Oui (formulaire + ~10 users) | **Oui** — bouton bleu « Créer l'… » | **Oui** — texte org + switcher navbar | Liste longue à droite (charge visuelle) | Lien « étape suivante : groupe » | Pas de guidage post-création | Bandeau « Prochaine étape : rattacher au groupe » après succès | **N1** |
| **`/users/:userId`** | Local tester | Oui (2 cartes) | **Oui** — « Associer au groupe » | Org implicite (navbar) ; **groupe non nommé** | Texte rôle non modifiable (2 paragraphes) | Groupes déjà rattachés à l'utilisateur | On ne voit pas les membreships existants | Afficher liste « Déjà membre de : … » | **N1** |
| **`/groups-admin`** | Local tester | Oui (création + liste) | **Oui** — « Créer le groupe » | Org : navbar seulement | **Moteur LLM** à la création (expert) | Bandeau org dans le contenu | LLM trop tôt dans le parcours onboarding | Replier LLM en « Avancé » ; bandeau org dans la page | **N1** |
| **`/groups-admin/:groupId`** | Local tester | Partiel — exports + LLM + profil ; **membres à droite** visibles ; RAG/P0 **hors écran** | **Non** — 2 colonnes à responsabilités concurrentes | Groupe : breadcrumb ; org : navbar | **Exports Felix**, calibrations P0/phase, formulaire RAG complet | Badge complétude profil, état fallback, lien référentiel | **Confirmé** : colonne gauche = fourre-tout technique ; membres noyés | Réordonner : bandeau → membres → profil conv. → accordéons expert | **N2** |
| **`/admin/conversation`** | Local tester | Oui (hub + legacy bas) | Oui — choisir une carte | Navbar | 4 cartes « **(legacy)** » au même niveau que profils | Mise en avant unique « Profils conversationnels » | Libellé legacy sur briques **encore utilisées** (fixtures démo avec suffixe `_mk1` interne) | Renommer « Briques par posture » ; carte profils plus large / en premier | **N1** |
| **`/admin/conversation/learner/profiles`** | Local tester | Oui (liste + panneau vide) | Oui — « Créer un profil vide » | **Oui** — org en orange sous le titre | Bouton « Depuis legacy » au même niveau que « Créer » | Détail des 3 slots avant sélection | Badge **4/7** peu explicite sans légende | Légende complétude ; « Depuis legacy » en secondaire | **N1** |
| **`/admin/conversation/learner/diagnostic`** | Local tester | Oui (conduite + params lecture seule) | Modérée — « Enregistrer la conduite » | Navbar ; posture claire | Templates YAML, panneau orchestrateur | Lien vers profil global lié à un TutorPrompt dont le code contient un suffixe `_mk1` (fixture ; pas libellé UI) | Double édition conduite (ici + profil global + `/conduct-profiles`) | Encart générique vers profils globaux + lien retour | **N2** |
| **`/admin/conversation/learner/reflective_afest`** | Local tester | Idem diagnostic | Idem | Idem | Idem | Idem | Même pattern | Idem | **N2** |
| **`/admin/conversation/learner/knowledge_review`** | Local tester | Idem (titre « Buchage ») | Idem | Idem | Idem | Idem | Même pattern | Idem | **N2** |
| **`/admin/conversation/learner/closing`** | Local tester | Partiel — 1er profil éval visible | Floue — plusieurs « Enregistrer » | Navbar | **3 blocs prompts + 3 politiques** denses, champs JSON | Lien vers slot éval du profil global | Charge cognitive élevée ; bannière synthèse hard-codée | Regrouper en accordéon ; lien « Profil global → évaluation » | **N2** |
| **`/tutor-prompts`** | Local tester | Formulaire création **domine** ; liste en bas | « Créer le TutorPrompt » | Navbar | **CRUD complet** (templates, metadata) encore en nav principale | Indication posture / profil lié | Page expert exposée comme courante | Retirer de la nav ; accès via hub « Compatibilité » uniquement | **N3** |
| **`/conduct-profiles`** | Local tester | Oui (sidebar postures + formulaire) | « Enregistrer » | Navbar | Templates techniques, liste de gestes | Lien profil global | Redondant avec hub posture | Même traitement que tutor-prompts | **N3** |
| **`/referentials`** | Local tester | Oui (tableau 1 ligne) | **Oui** — « Importer un référentiel » | Navbar | — | Lien depuis détail groupe | Page claire mais **orpheline** dans parcours cohorte | Lien depuis `/groups-admin/:id` | **N3** |
| **`/group/:id/referential`** | Local tester | Oui (2 cartes) | **Oui** — « Associer au groupe » | Groupe : breadcrumb générique « Groupe » | — | Nom du groupe dans le breadcrumb | Contexte groupe faible | Breadcrumb `Groupes / bac pro melec / Référentiel` | **N1** |

---

## Notes 1–5 par page (moyennes observées)

Légende : 5 = excellent, 1 = faible.

| Page | Contexte | But | Action | Hiérarchie | Courant/expert | Charge cognitive |
|------|----------|-----|--------|------------|----------------|------------------|
| `/dashboard` | 4 | 3 | 2 | 3 | 2 | 1 |
| `/users` | 5 | 5 | 5 | 4 | 4 | 3 |
| `/users/:id` | 3 | 4 | 4 | 4 | 5 | 2 |
| `/groups-admin` | 3 | 4 | 4 | 4 | 3 | 2 |
| `/groups-admin/:id` | 3 | 2 | 2 | **2** | **2** | **5** |
| `/admin/conversation` | 4 | 4 | 4 | 3 | 3 | 3 |
| `/learner/profiles` | 5 | 5 | 4 | 4 | 4 | 3 |
| Hubs posture (×3) | 4 | 3 | 3 | 3 | 2 | 4 |
| `/learner/closing` | 3 | 3 | 2 | 2 | 2 | 5 |
| `/tutor-prompts` | 3 | 3 | 4 | 2 | 1 | 5 |
| `/conduct-profiles` | 3 | 3 | 4 | 3 | 2 | 4 |
| `/referentials` | 4 | 5 | 5 | 5 | 5 | 1 |
| `/group/.../referential` | 3 | 5 | 5 | 5 | 5 | 1 |

**Page la plus problématique en runtime :** `/groups-admin/:groupId` (hiérarchie + charge cognitive).  
**Pages les plus saines :** `/referentials`, `/users`, `/learner/profiles`.

---

## B. Synthèse — runtime vs analyse code

### Confirmé par l'exécution réelle

1. **`/groups-admin/:id` est un fourre-tout** — exports, LLM, sélecteur profil global, affichage, deux blocs classifieurs, formulaire RAG multi-champs, puis membres à droite.
2. **Hub conversation : profils globaux vs « legacy »** — les cartes Diagnostic/Réflexif/Buchage portent le suffixe « (legacy) » alors qu’un profil global est déjà rattaché sur la démo (fixture interne `profil_conversationnel_mk1` : `_mk1` = version, **pas** libellé produit).
3. **`/users` récemment amélioré** — org active dans le corps de page + TRAINER en création ; mieux que l'audit code seul le laissait penser pour le tenant.
4. **`/dashboard` oriente vers le testeur**, pas l'admin — le bouton « Voir les apprenants » confirme la rupture de parcours onboarding.
5. **Triple entrée config** — `/tutor-prompts` et `/conduct-profiles` restent dans la **navbar principale** : pire que l'analyse code qui supposait une relégation partielle.
6. **Prompt legacy groupe masqué** quand un profil global est sélectionné — cohérent avec le code conditionnel.

### Infirmé ou nuancé

1. **Tenant « faible » sur `/users`** — en réel, **bon** (texte + switcher). Reste faible sur `/groups-admin` et hubs posture.
2. **Profils globaux pas assez mis en avant dans le hub** — partiellement : la carte existe en première position, mais **même taille** que les cartes « legacy ».
3. **Référentiel inaccessible** — **accessible** via `/referentials` et `/group/.../referential`, mais **non relié** depuis le détail groupe admin.

---

## C. Captures (preuves)

Dossier : [`screenshots/`](screenshots/)

| Fichier | Page |
|---------|------|
| `01-dashboard.png` | Tableau de bord |
| `02-users.png` | Création comptes |
| `03-user-detail.png` | Détail formateur TRAINER |
| `04-groups-admin.png` | Liste groupes |
| `05-group-detail-viewport.png` | Détail groupe — viewport |
| `05-group-detail-full.png` | Détail groupe — scroll complet (RAG + P0) |
| `06-admin-conversation.png` | Hub configuration |
| `07-learner-profiles.png` | Profils globaux |
| `08-diagnostic.png` | Hub Diagnostic |
| `09-reflective_afest.png` | Hub Réflexif |
| `10-knowledge_review.png` | Hub Buchage |
| `11-closing.png` | Clôture & évaluation |
| `12-tutor-prompts.png` | CRUD TutorPrompt |
| `13-conduct-profiles.png` | Conduct profiles |
| `14-referentials.png` | Référentiels |
| `15-group-referential.png` | Référentiel groupe |

---

## D. Top 10 adaptations les plus rentables

| # | Adaptation | Page(s) | Impact | Effort | Niveau |
|---|------------|---------|--------|--------|--------|
| 1 | **Réordonner détail groupe** : bandeau contexte → membres → profil conversationnel → accordéons (exports, RAG, P0) | `/groups-admin/:id` | Très fort | Moyen | **N2** |
| 2 | **Badge état config** : « Profil {nom} — complet n/7 » ou « ⚠ non configuré / fallback » (nom métier API, pas suffixe `_mk1`) | Détail groupe | Fort | Faible | **N1** |
| 3 | **Bandeau org** dans le contenu (pas seulement navbar) | `/groups-admin`, hubs posture | Fort | Faible | **N1** |
| 4 | Retirer **« (legacy) »** des cartes posture ; libeller **« Briques par posture »** | `/admin/conversation` | Moyen | Très faible | **N1** |
| 5 | **Dashboard admin** : liens Users / Groupes admin / Config conversation ; clarifier « testeur » | `/dashboard` | Fort (onboarding) | Faible | **N3** |
| 6 | Légende **4/7 complétude** + tooltips slots manquants | `/learner/profiles` | Moyen | Faible | **N1** |
| 7 | **Déplacer** `/tutor-prompts` et `/conduct-profiles` **hors navbar** → hub « Compatibilité » | Global | Fort | Faible | **N3** |
| 8 | Lien **Référentiel RNCP** depuis détail groupe | `/groups-admin/:id` | Moyen | Faible | **N3** |
| 9 | Encart **lien vers profils globaux** sur hubs posture (texte générique ; **sans** suffixe `_mk1` en UI) | `/learner/{posture}` | Moyen | Faible (fait) | **N2** |
| 10 | **Replier LLM** à la création de groupe | `/groups-admin` | Faible/moyen | Très faible | **N1** |

---

## E. Conclusion

L'exécution réelle **confirme et amplifie** le diagnostic code-first sur **`/groups-admin/:groupId`** et la **dispersion de la configuration conversationnelle**. Elle **infirme** une faiblesse tenant sur `/users` (déjà corrigée visuellement). La priorité runtime immédiate est le **réordonnancement local du détail groupe** (N2) et des **micro-signaux de contexte + état config** (N1), sans toucher au moteur ni à P0.

**Étape suivante (hors ce document) :** implémentation front des adaptations N1–N3 — voir backlog dans [`DOC_RUNTIME_UPDATE_2026-06.md`](../DOC_RUNTIME_UPDATE_2026-06.md) §6.

**Mise à jour 23/06 PM :** ajustements UX implémentés — voir [`QA_POST_UX_2026-06-23.md`](QA_POST_UX_2026-06-23.md).
