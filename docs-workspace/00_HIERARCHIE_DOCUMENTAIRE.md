# Hiérarchie documentaire — Workspace Hugo

**Workspace :** `/Users/machin/Desktop/Zone de travail Hugo`  
**Objet :** règles de lecture pour recaler le Space Perplexity. Ce document ne décrit pas Hugo ; il définit **quelle source fait foi pour quoi**.  
**Périmètre :** trois dossiers code — `hugo_back`, `hugo-hugolucia`, `hugo-main` — et la bibliothèque `docs-workspace/`.

---

## 1. Principe de vérité

En cas de contradiction, appliquer cet ordre de priorité :

| Rang | Source | Rôle |
|------|--------|------|
| 1 | **Code `hugo_back/`** | Seul backend Python du workspace ; vérité runtime locale |
| 2 | **Tests `hugo_back/`** (`pytest`, `apps/*/tests/`) | Comportement attendu et couvert |
| 3 | **Front `hugo-hugolucia/frontend_1.8/`** | Produit montrable de référence ; consommation API réelle |
| 4 | **Docs récentes du workspace** | `hugo_back/docs/`, `hugo-hugolucia/docs/`, `hugo-hugolucia/specs/` (v2, juin 2026) |
| 5 | **Specs historiques** | `SPEC_POC_v1.5`, `SPEC Hugo 1.6.2`, specs 1.8 dans `hugo-main/specs/` |
| 6 | **Archives** | `specs-old/`, `specs-old-1.6/`, `specs-old-1.7/`, audits mai 2026, prompts Cursor |

**Règles transverses :**

- Une spec seule **ne prouve jamais** un comportement implémenté.
- `hugo-main` et `hugo-hugolucia` ont des `backend/` **vides** : leurs `docker-compose.yml` et docs deploy ne font pas foi pour le moteur.
- L’API distante `https://hugoback.encoors.com` (configurée dans les `.env` front) peut diverger de `hugo_back` local → statut **À VÉRIFIER** pour tout constat prod.
- **Hugo cœur** (AFEST, P0, sessions, RAG, traces, exports) = priorité documentaire. **Hugo & Cie** (Julia, Felix, Hector, Jérémy, FamilleIA/CompagnIA) = extension design, pas base de vérité actuelle.

---

## 2. Table des statuts documentaires

| Statut | Signification | Usage Perplexity |
|--------|---------------|------------------|
| **IMPLÉMENTÉ** | Présent et vérifiable dans `hugo_back` ou front hugolucia | Source fiable pour décrire l’existant |
| **CRÉDIBLE** | Cohérent avec le code mais non entièrement vérifié (ex. corpus `RAG Melec/`, doc technique alignée sur chemins obsolètes) | Contexte, pas preuve seule |
| **CIBLE** | Décrit un état visé (1.9, POST-POC, v17 derrière flags) | Roadmap, jamais état actuel par défaut |
| **ARCHIVE** | Daté, remplacé ou doublon (`specs-old-*`, v1.4–v1.7, audits mai 2026) | Historique uniquement |
| **AMBIGU** | Plusieurs versions coexistants sans arbitrage documenté (P0 legacy vs v17, main vs hugolucia) | Signaler l’ambiguïté, ne pas trancher sans preuve |
| **À VÉRIFIER** | Dépend d’un runtime non inspecté (API distante, Postgres RLS réel, déploiement prod) | Marquer explicitement avant conclusion |

**Séparation des couches :**

| Couche | Emplacement de référence | Statut typique |
|--------|------------------------|----------------|
| Doctrine structurante | `SPEC_POC_v1.5.md`, `SPEC Hugo 1.6.2`, `Synopsis-Hugo-v1.5.md` | CIBLE / ARCHIVE selon version |
| Moteur réel | `hugo_back/apps/hugo/` ; synthèse `docs-workspace/02` | IMPLÉMENTÉ |
| Produit montrable | `hugo-hugolucia/frontend_1.8/` (routes `/app*`) ; synthèse `docs-workspace/03` | IMPLÉMENTÉ |
| Démo / runtime opérationnel | `docs-workspace/07`–`10` | IMPLÉMENTÉ (workspace) — flags env distants **VRIFIER** (doc 10) |
| Cible proche 1.9 | `hugo-hugolucia/specs/` (MEMO, LOT7, SPEC v2) ; garde-fous `docs-workspace/06` | CIBLE — croiser avec `hugo_back` |
| Hugo & Cie | `Synopsis-Hugo-v1.5.md`, `Integrations-LMS-SIRH-v1.5.md` | CIBLE (POST-POC) |
| Archives / docs dangereux seuls | `specs-old/`, `message_cursor_modif_*`, `MEMO_CTO` non recoupé | ARCHIVE / AMBIGU |

---

## 3. Règles de lecture par type de question

| Question | Lire en priorité | Ne pas lire seul |
|----------|------------------|------------------|
| **Comment fonctionne P0 ?** | `hugo_back/apps/hugo/services/hugo_orchestrator.py`, settings (`HUGO_P0_*`), tests `test_p0_*` | `SPEC Hugo 1.6.2`, `p0_description_technique_actuelle.md` |
| **TurnState / décision / phase ?** | `hugo_back/apps/hugo/domain/`, `decision_engine*.py`, `phase_decider.py` | Specs 1.7 refactor, LOT1 1.9 |
| **RAG / bibliothèque ?** | `hugo_back/apps/hugo/services/rag_support.py`, `apps/library/` | `RAG Melec/` (données démo), `docs/RAG_GROUP_LIBRARY.md` |
| **Mémoire / persistence ?** | Modèles + `memory_consolidator.py` dans `hugo_back` ; vérifier injection dans orchestrateur | `LOT4_memoire_inter_session.md` |
| **Que montrer en démo ?** | `09_PARCOURS_DEMO_ET_SCENARIOS.md` ; puis `03_ETAT_PRODUIT_REEL.md` et code `frontend_1.8` (`/app*`) | `hugo-main/frontend_1.8/` ; confondre parcours prod et mode testeur |
| **Quelle stack pour une démo ?** | `07_RUNTIME_DEMO_REFERENCE.md` (baselines A/B/C) | `docker-compose.yml` monorepo sans `hugo_back` |
| **Quels flags / env pour la démo ?** | `08_FLAGS_ET_ENVIRONNEMENT_DEMO.md` | Token OVH ou `DEBUG` par défaut dans `base.py` comme référence prod |
| **Front debug / calibration ?** | `09` §3 ; `frontend_1.8` mode `tester` — `LearnerDetailView.vue` | Confondre avec parcours prod `/app` |
| **Exports / Qualiopi ?** | `hugo_back/apps/exports/`, `apps/quality/` | Synopsis Felix POST-POC |
| **Déploiement local ?** | `hugo_back/Dockerfile`, `manage.py` ; pour compose/nginx → `hugo-hugolucia/deploy/` **avec** rattachement `hugo_back` | `docker-compose.yml` des monorepos sans backend |
| **Écarts 1.9 / backlog ?** | `05_ECARTS_DOC_CODE_PRODUIT.md` ; prérequis `06_PREPARATION_CIBLE_1_9.md` | `MEMO_CTO_Hugo1.9_v2.md` seul |
| **Vision produit / écosystème ?** | `Synopsis-Hugo-v1.5.md` (section Hugo cœur uniquement) | Personas, intégrations LMS comme périmètre POC actuel |
| **Julia / Felix / Hector / Jérémy ?** | `annexes/HUGO_ET_CIE_EXTENSIONS` (à produire) ou Synopsis § assistants | Toute spec POC ou 1.9 |
| **Runtime prod Encoors (flags, SSE, CORS) ?** | `10_FICHE_RUNTIME_PROD_ENCOORS.md` (inspection HTTP juin 2026) ; compléter `07`, `08` | Supposer équivalence avec `hugo_back` local ; flags env encore **VRIFIER** |
| **Comptes et données de démo ?** | `11_FICHE_COMPTES_ET_DONNEES_DEMO.md` (à produire) ; en attendant `09` + profil démo `08` §5 | Identifiants ou mots de passe en clair dans un doc |

---

## 4. Pièges connus

1. **`backend/` vide** dans `hugo-main` et `hugo-hugolucia` — le moteur est dans `hugo_back/`, pas dans les monorepos.
2. **`docker-compose.yml` trompeur** — référence `./backend` absent ; stack complète non lançable sans réintégration.
3. **Duplication docs** — ~109 fichiers `.md`, souvent en double entre `hugo-main` et `hugo-hugolucia` ; une seule copie ne fait pas foi.
4. **`p0_description_technique_actuelle*.md`** (×3 emplacements) — chemins `backend/apps/...` obsolètes vs arborescence `hugo_back/apps/...`.
5. **`MEMO_CTO_Hugo1.9_v2.md`** — écarts listés peuvent être partiellement résolus dans `hugo_back` (ex. synthèse LLM, TutorConductProfiles) → **À VÉRIFIER** avant priorisation.
6. **P0 double stack** — legacy actif par défaut ; v17 et classifieur LLM derrière flags (`HUGO_P0_V17_ENABLED=false`, `HUGO_P0_CLASSIFIER_ENABLED=false`).
7. **`hugo-main` vs `hugo-hugolucia`** — deux vérités produit si non tranché ; référence = **hugolucia** `frontend_1.8`.
8. **API distante vs local** — fronts pointent `hugoback.encoors.com` ; CORS n'autorise pas `localhost:5173` (doc 10) ; comportement prod ≠ garanti = copie locale.
9. **README racine** (`# hugo_poc` seul) — inutilisable comme guide workspace.
10. **Docs dangereux lus seuls** — `message_cursor_modif_P0_Hugo_optimise.md`, audits `specs_audit_1.9/`, `SPEC Hugo 1.6.2` comme preuve d’implémentation.

---

## 5. Bibliothèque `docs-workspace/`

| # | Fichier | Rôle |
|---|---------|------|
| 00 | `00_HIERARCHIE_DOCUMENTAIRE.md` | Règles de lecture et priorités (ce document) |
| 01 | `01_CARTOGRAPHIE_WORKSPACE_REEL.md` | Où est quoi : 3 dossiers, entrées, relations |
| 02 | `02_ETAT_MOTEUR_REEL.md` | Comportement réel de `hugo_back` |
| 03 | `03_ETAT_PRODUIT_REEL.md` | Démo montrable (`hugo-hugolucia/frontend_1.8`) |
| 04 | `04_INDEX_DOCUMENTAIRE_QUALIFIE.md` | Catalogue qualifié des docs existants |
| 05 | `05_ECARTS_DOC_CODE_PRODUIT.md` | Divergences doc / code / produit |
| 06 | `06_PREPARATION_CIBLE_1_9.md` | Pré-requis avant tout prompt backlog 1.9 |
| 07 | `07_RUNTIME_DEMO_REFERENCE.md` | Stack(s) runtime utilisables pour les démos (baselines A/B/C) |
| 08 | `08_FLAGS_ET_ENVIRONNEMENT_DEMO.md` | Flags et variables d'environnement impactant les démos |
| 09 | `09_PARCOURS_DEMO_ET_SCENARIOS.md` | Parcours de démo concrets (apprenant, testeur, limites) |
| 10 | `10_FICHE_RUNTIME_PROD_ENCOORS.md` | Inspection HTTP `hugoback.encoors.com` (CORS, DEBUG, routes, écarts vs local) |
| 11 | `11_FICHE_COMPTES_ET_DONNEES_DEMO.md` | **À produire** — comptes, groupes, scénario pré-testé (hors secrets en clair) |

**Ordre de lecture recommandé :**

- **Recalage général :** 00 → 01 → 02 → 03 → 05
- **Préparer ou animer une démo :** 07 → 08 → 10 (si baseline A distante) → 09 (s'appuient sur 02 et 03, ne les remplacent pas)
- **Avant backlog 1.9 :** 06 après 05 — ne pas lancer de backlog 1.9 détaillé sans arbitrages §3 du doc 06

**Décisions encore ouvertes** (non résolues par 07–10 ; fiche 11 à produire) : runtime de référence officiel (local vs `hugoback.encoors.com`), flags env prod (**VRIFIER** malgré doc 10), procédure baseline B « officielle », comptes démo documentés.

---

*Document 00 — base de recalage Perplexity. Dernière révision : juin 2026 — bibliothèque 00 → 10 (+ 11 à produire).*
