# Préparation cible 1.9 — Workspace Hugo

**Workspace :** `/Users/machin/Desktop/Zone de travail Hugo`  
**Objet :** conditions et garde-fous avant un futur prompt « cible 1.9 » — **sans backlog 1.9**.  
**S'appuie sur :** `docs-workspace/00` à `10` (bibliothèque recalage + couche démo).  
**Hugo cœur** = priorité ; **Hugo & Cie** (Julia, Felix, Hector, Jérémy, LMS/SIRH) = hors scope 1.9 sauf mention explicite.

---

## 1. Objectif du doc 06

### Ce qu'un prompt « cible 1.9 » pourra faire (après prérequis levés)

- Confronter les **LOTs 1.9** et specs v2 (`hugo-hugolucia/specs/`) au **code réel** (`hugo_back`, `frontend_1.8` hugolucia).
- Prioriser les **écarts confirmés** encore ouverts (ex. injection mémoire, RAG vectoriel, admin comptes, traces riches).
- Produire une **vision 1.9** structurée : déjà fait / partiel / cible / à abandonner — avec preuves.
- Définir le **périmètre 1.9** sur le cœur AFEST (P0, ui-state, sessions, mémoire, évaluation, conduct profiles, robustesse).
- Proposer une **séquence de chantiers** (pas des tickets ligne par ligne).

### Ce qu'il ne devra pas faire tant que prérequis non levés

- Prendre `MEMO_CTO_Hugo1.9_v2.md` ou l'audit mai 2026 comme **état actuel**.
- Supposer que `hugo-main` ou `docker-compose` reflètent le moteur.
- Prioriser depuis `SPEC Hugo 1.6.2` ou `p0_description*` sans recroiser doc 02.
- Confondre démo (`hugoback.encoors.com`) et code local sans arbitrage.
- Étendre le scope à Hugo & Cie, LMS, Felix bot, Jérémy planning.
- Refondre le produit ou réorganiser le workspace sans décision préalable.

---

## 2. Prérequis documentaires (checklist)

| Prérequis | Statut | Source |
|-----------|--------|--------|
| Hiérarchie de vérité (code > tests > front > docs) | **Prêt** | `00_HIERARCHIE_DOCUMENTAIRE.md` |
| Cartographie workspace (3 dossiers, entrées) | **Prêt** | `01_CARTOGRAPHIE_WORKSPACE_REEL.md` |
| État moteur `hugo_back` factuel | **Prêt** | `02_ETAT_MOTEUR_REEL.md` |
| État produit `frontend_1.8` hugolucia | **Prêt** | `03_ETAT_PRODUIT_REEL.md` |
| Index qualifié des ~109 docs historiques | **Prêt** | `04_INDEX_DOCUMENTAIRE_QUALIFIE.md` |
| Tableau écarts doc / code / produit | **Prêt** | `05_ECARTS_DOC_CODE_PRODUIT.md` |
| Arbitrage **hugolucia** = référence produit | **Prêt** (documenté) | 01, 03, 05 |
| Arbitrage **hugo_back** = référence moteur local | **Prêt** (documenté) | 01, 02, 05 |
| Équivalence **local ↔ API distante** | **Partiel** | `10_FICHE_RUNTIME_PROD_ENCOORS.md` (juin 2026) — routes/CORS/DEBUG ; flags env **VRIFIER** |
| Flags **prod** (P0 v17, classifieur) | **Pas prêt** | 02, 05, 10 — **VRIFIER** (non lus sur Encoors) |
| Statut **MEMO CTO** (obsolète partiellement) | **Pas prêt** — à trancher archive vs réécriture | 05 §7 |
| Stratégie **monorepo** (back séparé ou réintégré) | **Pas prêt** | 05 §2, §8 |
| Fiche **runtime prod** (version déployée, env) | **Partiel** | `10_FICHE_RUNTIME_PROD_ENCOORS.md` — inspection HTTP 2026-06-12 ; pas de commit ni flags env |
| Fiche **flags déployés** sur `hugoback.encoors.com` | **Pas prêt** | **VRIFIER** — non exposés par l'inspection doc 10 |
| Couche **démo opérationnelle** (stack, parcours, flags) | **Prêt** | `07_RUNTIME_DEMO_REFERENCE.md`, `08_FLAGS_ET_ENVIRONNEMENT_DEMO.md`, `09_PARCOURS_DEMO_ET_SCENARIOS.md` |
| Fiche **comptes / données de démo** | **Manquant** | `11_FICHE_COMPTES_ET_DONNEES_DEMO.md` (à produire) ; parcours dans `09` |
| **Démo à froid** sans comptes documentés | **Pas prêt** | 09 §2, 07 baseline B non formalisée |

**Verdict :** base documentaire **prête pour cadrer 1.9** (00–06 + écarts 05) ; **prête pour préparer une démo** avec réserves (07–10, 09) ; **3 arbitrages humains** + **fiche 11** manquante avant démo reproductible sans improvisation ; flags prod **VRIFIER**.

---

## 3. Décisions à trancher avant 1.9

| Décision | Options | Pourquoi bloquant | Recommandation lecture |
|----------|---------|-------------------|------------------------|
| **Runtime de référence** | A) `hugo_back` local B) `hugoback.encoors.com` C) les deux avec fiche d'écarts | Tous les « reste à faire » dépendent de la baseline | 05 §6 ; 03 §8 |
| **Stack P0 « prod »** | A) Legacy (défaut actuel) B) v17 (`HUGO_P0_V17_ENABLED`) C) coexistence documentée | Priorisation 1.9 différente (migration vs complétion legacy) | 02 §4, §8 |
| **Organisation repo** | A) Garder 3 dossiers B) Réintégrer `hugo_back` → `backend/` C) Monorepo unique | Impact deploy, CI, chemins docs, Perplexity Space | 01, 05 §2 |
| **Branche front cible** | A) `hugo-hugolucia/frontend_1.8` seule B) inclure `hugo-main` | Risque de prioriser une version en retard | 03 §7, 05 §5 |
| **MEMO CTO juin 2026** | A) Archiver B) Réécrire écarts C) Utiliser seulement LOTs/archived audits | 5/10 écarts MEMO contredits localement | 05 §3–4, §7 |
| **Injection mémoire LOT4** | A) Scope 1.9 obligatoire B) Optionnel C) Hors scope | Seul écart MEMO **encore confirmé** côté moteur | 05 §3 ; `LOT4_memoire_inter_session.md` |
| **RAG vectoriel** | A) Livrer en 1.9 B) Rester lexical C) Abandonner pgvector | Effort infra + library vs valeur POC | 02 §5, 05 §3 |
| **Admin comptes** | A) ORGADMIN seul B) Tuteur délégué (MEMO §6) | Périmètre interface 1.9 | MEMO ; 05 §3–4 |
| **Démo / nginx** | A) `frontend_1.8` en prod B) `frontend/` testeur dans compose | Cohérence démo vs infra documentée | 01 §4, 05 §2 |

---

## 4. Ambiguïtés repo à lever (priorisées)

1. **API distante vs `hugo_back` local** — comportement prod inconnu (**À VÉRIFIER**).
2. **P0 actif en prod** — legacy, v17 ou classifieur LLM (**À VÉRIFIER**).
3. **Lien historique** `hugo_back` ↔ monorepos — extraction, copie parallèle ou branche orpheline (**AMBIGU**).
4. **Déploiement réel** — compose sert `frontend/` pas `frontend_1.8/` (**AMBIGU**).
5. **Duplication docs** — quelle copie indexer dans Perplexity (**CONFIRMÉ**, arbitrage : hugolucia + docs-workspace).
6. **ConductProfiles** — back + UI tester vs « non administrable » dans MEMO (**PARTIEL**).
7. **RLS Postgres réel** — middleware OK, efficacité prod non prouvée (**À VÉRIFIER**).
8. **Trace `generate-trace`** — payload minimal vs attentes Felix/Qualiopi (**CONFIRMÉ** écart, priorité métier à trancher).

---

## 5. Granularités documentaires requises

### Déjà en place (`docs-workspace/`)

| Doc | Granularité couverte |
|-----|---------------------|
| 00 | Règles de lecture, statuts, pièges |
| 01 | Où est le code, entrées opérationnelles |
| 02 | Moteur : API, P0, flags, sous-systèmes, tests |
| 03 | Produit : parcours `/app`, contrats API front, engagement UI |
| 04 | Catalogue et dangerosité des anciens docs |
| 05 | Écarts doc/code/produit, docs obsolètes |
| 06 | Ce document — garde-fous avant 1.9 |

### Manquant encore (recommandé avant backlog 1.9)

| Fiche | Contenu minimal | Statut |
|-------|-----------------|--------|
| **Runtime prod** | Version/commit `hugoback.encoors.com`, date deploy, lien avec `hugo_back` local | **Manquant** |
| **Flags déployés** | `HUGO_P0_V17_ENABLED`, classifieur, phase classifier, provider LLM | **Manquant** |
| **Décisions tranchées** | Réponses écrites aux §3 (même 1 page) | **Manquant** |
| **MEMO CTO statut** | Archivé + renvoi 05, ou note de révision datée | **Manquant** |

Les **LOTs 1.9** (`specs-old/specs-old-1.9/`) et **specs v2** restent des sources **CIBLE** — à lire **après** 02, 03, 05, jamais seules.

---

## 6. Questions 1.9 mal posées si on saute cette étape

| Question mal posée | Pourquoi elle échoue |
|------------------|---------------------|
| « Corriger les écarts du MEMO CTO » | 5 écarts déjà résolus en local ; liste fausse comme backlog |
| « Brancher les boutons synthèse/évaluation sur frontend_1.8 » | Déjà branchés (`ProdLearnerWorkspace.vue`) — problème peut être API distante |
| « Implémenter TutorConductProfiles from scratch » | Back + resolver + UI tester déjà présents — reste périmètre admin/prod |
| « Faire consommer UIState pur au front » | Déjà le cas en parcours prod — confusion avec mode testeur |
| « Consolider la mémoire sur generate-trace seulement » | Consolidation déjà post-message (`_post_conversation_hooks`) |
| « Migrer tout le repo vers P0 v17 » | Flag off par défaut ; prod inconnue ; coexistence legacy non arbitrée |
| « Lancer docker compose pour valider 1.9 » | `backend/` vide — stack cassée sans décision monorepo |
| « Utiliser hugo-main/frontend_1.8 comme référence » | Version en retard vs hugolucia |
| « Prioriser depuis SPEC 1.6.2 » | Doctrine cible, pas implémentation (legacy actif) |
| « Inclure Julia / Felix / LMS dans 1.9 » | Hors cœur Hugo ; extension POST-POC |
| « Reprendre l'audit mai 2026 tel quel » | Daté ; front et back locaux ont évolué |

---

## 7. Périmètre suggéré pour le futur prompt « cible 1.9 »

### In scope (Hugo cœur)

- Complétion **écarts confirmés** : injection mémoire, traces riches, admin comptes, RAG (si décidé), robustesse (RLS Postgres, E2E si décidé).
- **ConductProfiles** : exposition prod, complétion admin, héritage org/système.
- **P0** : stratégie legacy / v17 / classifieur — sans refonte doctrine 1.6.2.
- **Produit montrable** : `hugo-hugolucia/frontend_1.8`, contrats `ui-state`, streaming.
- **Qualité / observabilité** : signaux cohorte, exports, bundle Qualiopi (niveau POC).

### Out of scope (sauf directive explicite)

- Hugo & Cie (Julia, Felix bot, Hector, Jérémy).
- Intégrations LMS/SIRH (`Integrations-LMS-SIRH-v1.5.md`).
- Refonte UX prod, nouvelle gamification, rebranding.
- Réorganisation git/monorepo (sauf décision §3 actée).
- Estimations en jours, tickets Jira détaillés dans le premier passage.

### Ordre de lecture pour le prompt

1. `00_HIERARCHIE_DOCUMENTAIRE.md`
2. `01_CARTOGRAPHIE_WORKSPACE_REEL.md`
3. `02_ETAT_MOTEUR_REEL.md`
4. `03_ETAT_PRODUIT_REEL.md`
5. `05_ECARTS_DOC_CODE_PRODUIT.md`
6. Fiches runtime prod + flags (quand disponibles)
7. Ensuite seulement : `hugo-hugolucia/specs/MEMO_CTO…`, `LOT7`, `SPEC_*_v2`, LOTs archivés — **comme cible**, pas comme fait.

### Garde-fous

- Preuve = chemin fichier ou test ; statut IMPLÉMENTÉ / PARTIEL / CIBLE / À VÉRIFIER.
- Ne pas prendre une spec seule comme preuve.
- Distinguer local, prod distante, et doc historique.
- Pas de refonte produit ; incrémental sur l'existant.

---

## 8. Brouillon de prompt « phase 1.9 »

```
Tu travailles dans /Users/machin/Desktop/Zone de travail Hugo.

Lis d'abord docs-workspace/00 à 05 et les fiches runtime/flags si fournies.
Baseline moteur = hugo_back/ ; baseline produit = hugo-hugolucia/frontend_1.8/.
Runtime prod = [À PRÉCISER : hugoback.encoors.com ou local].

Objectif : produire une ANALYSE CIBLE 1.9 (pas un backlog ticket par ticket).
Confronter les LOTs/specs v2 (sources CIBLE) au code réel.
Prioriser uniquement les écarts encore CONFIRMÉS dans 05_ECARTS.
Hugo cœur uniquement ; Hugo & Cie hors scope.

Livrable : (1) déjà fait / partiel / cible / à abandonner par domaine
(P0, mémoire, RAG, admin, produit, infra, tests) ; (2) dépendances entre chantiers ;
(3) risques si on part du MEMO ou de l'audit mai 2026 ; (4) questions ouvertes restantes.
Preuve obligatoire par affirmation. Pas d'estimation en jours.
```

---

## 9. Renvoi — bibliothèque `docs-workspace/` complète

| # | Fichier | Rôle |
|---|---------|------|
| 00 | `00_HIERARCHIE_DOCUMENTAIRE.md` | Règles de vérité |
| 01 | `01_CARTOGRAPHIE_WORKSPACE_REEL.md` | Géographie dépôt |
| 02 | `02_ETAT_MOTEUR_REEL.md` | Moteur `hugo_back` |
| 03 | `03_ETAT_PRODUIT_REEL.md` | Produit montrable |
| 04 | `04_INDEX_DOCUMENTAIRE_QUALIFIE.md` | Index docs historiques |
| 05 | `05_ECARTS_DOC_CODE_PRODUIT.md` | Écarts doc/code/produit |
| 06 | `06_PREPARATION_CIBLE_1_9.md` | Ce document |

**Prochaine étape humaine recommandée :** trancher les décisions §3 (au minimum runtime de référence + stack P0 prod), puis lancer le prompt §8.

---

*Document 06 — préparation cible 1.9, juin 2026. Bibliothèque docs-workspace complète.*
