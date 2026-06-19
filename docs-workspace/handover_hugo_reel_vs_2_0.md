# Handover Hugo — réel vs cible 2.0

**Objet :** synthèse pour board et partenaires après les clusters de convergence 1–14 et la campagne de tests pré‑prod (juin 2026).  
Ce document décrit **ce que Hugo fait réellement aujourd’hui**, le positionne par rapport à la **cible 2.0**, et indique ce qui reste en **couronne future** — sans confondre ambition doctrinale et livraison prouvée.

> **Hiérarchie de vérité :** la spec 2.0 = cible ; le code et les tests locaux = réel observé ; Encoors/prod/RLS = à vérifier séparément avant toute release distante.

---

## Ce que Hugo fait réellement aujourd’hui

- **Moteur de conversation gouverné** — diagnostic et progression pilotés côté serveur (P0, TurnState, décisions internes). Le front apprenant ne voit que des états produit dérivés (UIState), jamais la mécanique interne.

- **Mémoire intra-conversation structurée** — résumés gouvernés, sans verbatim brut exposé. La mémoire entre sessions existe en stockage backend mais **n’est pas injectée** dans le dialogue courant (périmètre lot actuel).

- **Branche d’évaluation opérationnelle (EVAL1)** — chaîne readiness → évaluation → trace avec format pivot v1, **validation humaine explicite**, sans prétention de certification automatique.

- **Exports et preuves Qualiopi lite** — exports JSON/CSV et bundles ZIP pour les administrateurs d’organisation, avec garde-fous de confidentialité (pas de verbatim non partagé, pas d’analytique technique dans les exports métier).

- **Surfaces encadrants fonctionnelles** — espaces tuteur et formateur en production (`/app/tutor`, `/app/trainer/knowledge`), respect de la confidentialité multi-tenant et des rôles (apprenant, tuteur, formateur, admin org.).

- **Observabilité backend en place** — signaux qualité persistés, endpoint d’observabilité session pour les rôles autorisés ; première couche d’observabilité produit (badges de pilotage côté tuteur), sans tableau de bord analytique complet.

---

## Alignement avec la cible 2.0 — trois couches

### Noyau moteur, mémoire, évaluation, confidentialité (10, 20, 70, 90, 100)

**Convergé localement, tests passés.**

Le cœur Hugo répond aux exigences du lot courant : progression explicite, CTA backend-driven, mémoire gouvernée intra-conversation, évaluation non certifiante, isolation multi-tenant (RLS et filtres applicatifs testés en local), exports encadrés.

**Points ouverts (non bloquants locaux) :** parité Encoors et RLS sur la base de production réelle — **à vérifier ops** avant release distante.

### Expérience apprenant et RAG (31, 30)

**Backend-first ; UX partiellement livrée.**

Le front consomme l’UIState serveur (CTA, mode conversationnel, profil d’affichage jeunesse). Le RAG **lexical** est actif et gouverné (renfort situé, badge « Appui »). Le RAG **vectoriel** est une cible future, explicitement **hors périmètre** actuel.

**Manque principal :** sélecteur de posture apprenant et grammaires UX adulte/pro complètes (plan cluster 12, non encore implémentés en UI).

### Encadrants, observabilité élargie, exports avancés (40, 50, 60, 80, 110, 120)

**Fondations livrées ; enrichissements en couronne.**

- Formateur : liste et validation de connaissances — OK ; orchestration formateur riche = future.
- Tuteur : timeline, traces, validation — OK ; recommandations avancées = future.
- Observabilité : API backend base + canal technique D9bis — OK backend ; **pas de dashboards produit** ni UI observabilité interne.
- COORDO : rôle reconnu avec accès tuteur — **pas de cockpit dédié**.
- Intercalaires (domaine 120) : **non démarrés**.

---

## Ce qui reste en couronne 2.0+

- Mémoire **inter-session active** injectée au fil de la conversation.
- RAG **vectoriel** (pgvector) comme renfort avancé.
- **D9bis complet** et dashboards analytiques produit.
- Orchestrateurs encadrants **avancés** (formateur dialogique, cockpit COORDO cohorte).
- **Intercalaires et dossiers** (domaine 120).
- Exports techniques avancés (debug-md superadmin, Felix v3).
- Catalogue canonique exhaustif des signaux qualité et dashboards observabilité produit.
- Sélecteur posture apprenant et **trois grammaires UX** finalisées.

Ces éléments sont **documentés comme cible**, pas présentés comme livrés.

---

## Campagne de tests pré‑prod — résumé

| Volet | Commande | Résultat local |
|-------|----------|----------------|
| **Backend** | `bash hugo_back/scripts/run_preprod_suite.sh` | **113 PASS**, 2 SKIP (tests RLS Postgres conditionnels) |
| **UI Playwright** | `npm run test:smoke` (après bootstrap fixtures) | **10 PASS** — apprenant, tuteur, formateur, ORGADMIN, COORDO |
| **Oracles Encoors** | `bash hugo_back/scripts/run_encoors_preprod_oracle.sh` | Scripts prêts ; sans credentials → routes internes **404** (protection OK) ; **parité complète A_VÉRIFIER** avec auth |

**Garde-fous vérifiés :** pas de P0 en surface apprenant ; memory-summary sans verbatim ; RAG vectoriel off ; évaluation non certifiante ; exports org réservés aux rôles autorisés ; verbatim non partagé invisible au tuteur.

Détail opérationnel : `checklist_pre_prod_hugo_2_0.md`.

---

## Recommandations pour la mise en ligne

1. **GO local encadré** si la suite pré‑prod backend + Playwright passe — le noyau Hugo réel est en place et testé pour un déploiement contrôlé (demo, staging, environnement maîtrisé).

2. **Encoors / production** — exécuter les oracles authentifiés (M1, EVAL1, O1, observabilité) et le script SQL RLS prod **avant** toute release sur l’environnement distant ; valider les flags runtime (`HUGO_P0_V17_ENABLED`, etc.).

3. **Backlog 2.0+ explicite** — traiter en vagues séparées : UX postures apprenant (cluster 12), RAG vectoriel, mémoire inter-session au tour, D9bis UI, intercalaires 120 — sans les mélanger à la clôture du noyau actuel.

---

**Documents de référence :**  
`REFERENCE_CONVERGENCE_HUGO_REEL_VS_2_0_GARDEFOU.md` · `inventaire_convergence_hugo_reel_vs_cible_2_0.md` · `plan_tests_global_hugo.md` · `checklist_pre_prod_hugo_2_0.md`

**Date :** 2026-06-18
