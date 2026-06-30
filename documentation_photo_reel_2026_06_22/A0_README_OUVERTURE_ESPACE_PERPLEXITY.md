# A0 — README d'ouverture espace Perplexity

**Date de photo :** 22 juin 2026  
**Workspace :** Zone de travail Hugo  
**Objet :** cadrer un futur espace Perplexity dédié à la spécification des prochaines fonctions Hugo, sans repartir de zéro ni confondre réel, cible et hypothèses.

---

## But du futur espace

L'espace Perplexity à ouvrir doit servir à :

- spécifier les prochaines fonctions à implémenter sur Hugo cœur ;
- prioriser les chantiers de convergence Hugo réel → Hugo 2.0 ;
- rédiger des mini-specs, contrats API et décisions CTO ancrées sur le réel audité ;
- auditer des écarts par domaine sans réinventer la méthode ni la hiérarchie des sources.

Il ne doit **pas** servir de catalogue marketing, ni de preuve d'implémentation par défaut.

---

## Ce que couvre ce dossier

Le dossier `documentation_photo_reel_2026_06_22/` est une photographie documentaire au 22 juin 2026. Il contient :

| Fichier | Rôle |
|---------|------|
| `A0_README_OUVERTURE_ESPACE_PERPLEXITY.md` | Ce document — mode d'emploi du pack |
| `A1_SOCLE_REEL_OBSERVE.md` | Cartographie synthétique du réel observé |
| `A2_CARTOGRAPHIE_FONCTIONNELLE_EXISTANT.md` | Fonctions par domaine |
| `A3_CARTOGRAPHIE_OBJETS_CONTRATS_ET_VARIABLES.md` | Objets, contrats, variables structurantes |
| `A4_ARCHITECTURE_LOGIQUE_ET_PIPELINES.md` | Architecture et pipelines |
| `A5_ECARTS_MAJEURS_VERS_CIBLE_ET_CHANTIERS_DE_SPEC.md` | Écarts majeurs et chantiers futurs |
| `A6_QUESTIONS_OUVERTES_PREUVES_MANQUANTES_ET_A_VERIFIER.md` | Points non prouvés |
| `A7_MODE_EMPLOI_POUR_FUTUR_ESPACE_PERPLEXITY.md` | Prompts et ordre d'exploitation |
| `B0_MONOGRAPHIE_SCIENTIFIQUE_HUGO_REEL_2026_06_22.md` | Monographie dense pour exploitation scientifique |

---

## Ordre de lecture recommandé

### Première session (recalage)

1. `A0` (ce fichier)
2. `A1_SOCLE_REEL_OBSERVE.md`
3. `A5_ECARTS_MAJEURS_VERS_CIBLE_ET_CHANTIERS_DE_SPEC.md`
4. `A6_QUESTIONS_OUVERTES_PREUVES_MANQUANTES_ET_A_VERIFIER.md`

### Avant de spécifier une fonction

1. `A2` — domaine concerné
2. `A3` — objets et contrats
3. `A4` — pipeline si noyau conversationnel
4. Fichier `ecarts — <domaine>.md` correspondant dans `docs-workspace/`
5. `cluster2_matrice_runtime_vs_cible.md` — ligne de domaine

### Pour une lecture analytique complète

`B0_MONOGRAPHIE_SCIENTIFIQUE_HUGO_REEL_2026_06_22.md` — document autoportant.

---

## Sous-documents à lire d'abord

En priorité absolue avant toute spec :

- `docs-workspace/00_HIERARCHIE_DOCUMENTAIRE.md`
- `docs-workspace/02_ETAT_MOTEUR_REEL.md`
- `docs-workspace/03_ETAT_PRODUIT_REEL.md`
- `docs-workspace/05_ECARTS_DOC_CODE_PRODUIT.md`
- `docs-workspace/cluster2_matrice_runtime_vs_cible.md` (version 6, post-profils globaux 20/06/2026)

Pour le runtime et la démo :

- `docs-workspace/07_RUNTIME_DEMO_REFERENCE.md`
- `docs-workspace/08_FLAGS_ET_ENVIRONNEMENT_DEMO.md`
- `docs-workspace/10_FICHE_RUNTIME_PROD_ENCOORS.md`

---

## Ce que ce dossier permet de faire

- Ouvrir un espace Perplexity avec un socle de vérité structuré (réel / cible / écarts / A_VERIFIER).
- Prioriser des chantiers par domaine (10 à 120) avec références croisées.
- Rédiger des contrats minimaux (UIState, mémoire intra-conversation, CTA, RAG lexical).
- Cadrer des audits code ciblés sans confondre front et moteur.
- Préparer des prompts Cursor ou CTO avec garde-fous documentaires.
- Comparer local audité vs Encoors avec les limites explicites.

---

## Ce que ce dossier ne permet pas encore de conclure

- L'équivalence exacte entre `hugo_back` local et `https://hugoback.encoors.com` (**A_VERIFIER**).
- Les flags P0 actifs en production distante (**A_VERIFIER**).
- L'efficacité RLS PostgreSQL en prod (**A_VERIFIER**).
- Le commit ou la version déployée sur Encoors (**A_VERIFIER**).
- Le comportement LLM en conditions réelles de charge (**A_VERIFIER**).
- L'existence de fonctions cible 2.0 non prouvées localement (intercalaires v1, RAG vectoriel, D9bis produit, COORDO, etc.).

---

## Limites

### Périmètre géographique du workspace

- **Moteur :** `hugo_back/` uniquement (Django).
- **Produit montrable :** `hugo-hugolucia/frontend_1.8/` uniquement.
- **Monorepos :** `backend/` vide dans `hugo-hugolucia` et `hugo-main` — docker-compose monorepo **cassé** sans rattacher `hugo_back`.
- **Snapshot en retard :** `hugo-main/frontend_1.8` ne fait pas foi pour le produit.

### Périmètre temporel

- Socle 00–10 : juin 2026.
- Audits cluster 2–16 : 16–20 juin 2026 (local audité).
- Inspection HTTP Encoors : 12 juin 2026.
- Cette photo : 22 juin 2026 — ne remplace pas une relecture code au moment de l'implémentation.

### Doctrine préservée

- Hugo est **backend-first**.
- `UIState` est une traduction produit, pas le moteur.
- P0, TurnState, verbatim brut restent **hors surfaces métier standards**.
- La mémoire utile du lot courant = mémoire gouvernée **intra-conversation** ; l'inter-sessions est préparée mais non injectée au tour.

---

## Différences réel audité / cible 2.0 / A_VERIFIER

| Catégorie | Définition | Exemple |
|-----------|------------|---------|
| **RÉEL OBSERVÉ** | Code `hugo_back`, tests, front `frontend_1.8`, docs 02–03 | Pipeline P0 legacy actif par défaut |
| **CIBLE** | Spec canonique 2.0 et compléments — jamais preuve de livraison | EvaluationTrace unifiée, intercalaires v1 |
| **ÉCART CONFIRMÉ** | Divergence recoupée doc + code | Pas d'injection `LearnerThemeMemory` dans orchestrateur |
| **A_VERIFIER** | Dépend prod, flags, RLS, runtime non inspecté | `HUGO_P0_V17_ENABLED` sur Encoors |
| **HYPOTHÈSE** | Recommandation non prouvée | Baseline B comme référence officielle moteur |

---

## Renvois corpus source (non dupliqués ici)

- Méthode : `docs-workspace/DOC_METHODO_REFERENCE_CONVERGENCE_HUGO_REVISE.md`
- Glossaire : `docs-workspace/glossaire_alignement_hugo_reel_vs_spec.md`
- Plan CTO : `docs-workspace/plan_documentation_cto_convergence_hugo.md`
- Cible : `docs-workspace/spec_canonique_hugo_2_0.md`

---

*Photo documentaire — 22 juin 2026. Aucun marqueur machine ; sources explicites par nom de fichier.*
