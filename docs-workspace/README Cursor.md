Contexte
Tu travailles dans le repo local Hugo, avec la structure suivante :

- docs-workspace/
  - 00_HIERARCHIE_DOCUMENTAIRE.md
  - 01_CARTOGRAPHIE_WORKSPACE_REEL.md
  - 02_ETAT_MOTEUR_REEL.md
  - 03_ETAT_PRODUIT_REEL.md
  - 04_INDEX_DOCUMENTAIRE_QUALIFIE.md
  - 05_ECARTS_DOC_CODE_PRODUIT.md
  - 06_PREPARATION_CIBLE_1_9.md
  - 07_RUNTIME_DEMO_REFERENCE.md
  - 08_FLAGS_ET_ENVIRONNEMENT_DEMO.md
  - 09_PARCOURS_DEMO_ET_SCENARIOS.md
  - 10_FICHE_RUNTIME_PROD_ENCOORS.md
  - 10_runtime_p0_progression_uistate_note_lot_courant_cta_synthese_evaluation.md
  - 20_cursorops_templates.md
  - 20_memoire_gouvernee_note_lot_courant_memoire_intra_conversation.md
  - 30_cursorops_templates.md
  - 70_cursorops_templates.md
  - backlog_lot_1.md
  - Bibliothèque canonique de personae Hugo 2.0.md
  - complements_spec_2_0_depuis_anterieurs.md
  - contrat minimal mémoire gouvernée intra‑conversation.txt
  - DOC_METHODO_REFERENCE_CONVERGENCE_HUGO_REVISE.md
  - ecarts — 10_runtime_p0_progression_uistate.md (si présent)
  - ecarts — 20_memoire_gouvernee.md
  - ecarts — 30_referentiel_documentaire_rag.md
  - ecarts — 70_evaluation_traces_preuves.md
  - ecarts — 80_observabilite_qualite_conversationnelle.md
  - ecarts — 90_confidentialite_partage_multitenant_roles.md
  - ecarts — 100_exports_preuves_qualiopi_lite.md
  - ecarts — 110_interfaces_formateur_tuteur.md
  - glossaire_alignement_hugo_reel_vs_spec.md
  - plan_documentation_cto_convergence_hugo.md
  - README Cursor.md
  - spec_canonique_hugo_2_0.md
  - specs interface 2.0.md
  - template_prompt_audit_memoire_intra_conversation.md

- hugo_back/ (backend Django, vrai moteur)
- hugo-hugolucia/ (front 1.8, produit montrable)
- hugo-main/ (monorepo historique, backend vide)

Règles de lecture
- Tu dois respecter 00_HIERARCHIE_DOCUMENTAIRE.md comme source de vérité méthodologique.
- Une spec seule ne prouve jamais l’implémentation.
- Le code hugo_back + tests priment pour décrire le réel.
- Les docs 2.0 (spec_canonique_hugo_2_0.md, specs interface 2.0.md, complements_spec_2_0_depuis_anterieurs.md) décrivent la cible.
- Les documents ecarts — *.md servent à raccorder réel vs cible, pas à inventer une troisième doctrine.

Objectif du cluster 2
Produire, à partir de ce corpus, un ensemble de livrables très structurés et réutilisables pour la convergence Hugo :

1. Matrices de mapping runtime/cible sur le bloc :
   - P0, DecisionContract / ConversationDecision
   - ConversationProgress
   - UIState
   - Mémoire intra-conversation (session memory, memory-summary)
   - Exports et preuves (Trace, Evidence, EvidenceBundleView, nouveaux artefacts analytiques LLM)
   - Rôles / surfaces (apprenant, tuteur, formateur, coordinateur, ORGADMIN, superadmin technique)

   Pour chaque famille d’objet, la matrice doit au minimum contenir :
   - Nom doctrinal 2.0
   - Nom(s) réel(s) observé(s) (code, modèles, endpoints, fichiers)
   - Niveau de vérité (IMPLÉMENTÉ, CIBLE, CREDIBLE, A_VERIFIER, AMBIGU) selon 00_HIERARCHIE_DOCUMENTAIRE.md
   - Source(s) documentaire(s) / code correspondantes
   - Actions documentaires recommandées (ALIGNE, ALIGNEDOCPARTIEL, RENOMMERDANSDOC, ABSENT NOUVEAUCONTRAT, etc.)

2. Intégration explicite des ajouts récents :
   - Profils d’affichage apprenant (plusieurs profils UX lisant le même UIState).
   - Couche ConversationTurnLLMAnalysis / ConversationLLMAnalysis, réservée aux exports de debug superadmin.
   - Responsabilités de configuration d’interface par rôle (formateur, ORGADMIN, superadmin).
   - Utilisation de la Bibliothèque canonique de personae Hugo 2.0 comme base pour des scénarios de test et d’audit.

   Tu dois repérer et lier, dans les documents :
   - où ces concepts sont décrits (specs interface 2.0.md, complements_spec_2_0_depuis_anterieurs.md, écarts de domaine…),
   - comment ils doivent se raccorder aux invariants existants (backend orchestré, P0 non exposé, UIState comme surface produit, mémoire gouvernée, exports gouvernés).

3. Production automatique d’outils pour les prochains clusters :
   - Un fichier `docs-workspace/cluster2_matrice_runtime_vs_cible.md` qui regroupe toutes les matrices ci-dessus, par sous-domaine (10_runtime, 20_mémoire, 70_exports, 80_qualité, 90_confidentialité, 110_interfaces).
   - Un fichier `docs-workspace/cluster2_prompts_audit_runtime_et_memoire.md` générant des prompts génériques mais paramétrables pour auditer :
     - P0 / décision locale,
     - progression / ConversationProgress,
     - UIState exposé au front,
     - mémoire intra-conversation,
     - exports et bundles, y compris artefacts analytiques LLM.
   - Un fichier `docs-workspace/cluster2_oracles_test_par_persona.md` qui, en s’appuyant sur « Bibliothèque canonique de personae Hugo 2.0.md », définit pour chaque persona clé :
     - les invariants à vérifier côté UIState,
     - les attentes de mémoire visible,
     - les attentes de partage / export / traces / évaluation,
     - des conditions de succès / échec utilisables comme oracles pour des tests automatiques (par exemple en Playwright ou en scripts d’audit backend).

Tâches concrètes pour toi (Cursor)
1. Lire 00_HIERARCHIE_DOCUMENTAIRE.md, DOC_METHODO_REFERENCE_CONVERGENCE_HUGO_REVISE.md et plan_documentation_cto_convergence_hugo.md pour caler ta méthode.
2. Lire ou survoler 02_ETAT_MOTEUR_REEL.md, 03_ETAT_PRODUIT_REEL.md, 05_ECARTS_DOC_CODE_PRODUIT.md pour ancrer la vision du réel.
3. Lire la spec 2.0 (spec_canonique_hugo_2_0.md, specs interface 2.0.md, complements_spec_2_0_depuis_anterieurs.md) pour comprendre la cible et les ajouts (profils d’affichage, couche analytique LLM).
4. Lire les rapports d’écarts pertinents :
   - ecarts — 10_runtime_p0_progression_uistate.md (si présent)
   - ecarts — 20_memoire_gouvernee.md
   - ecarts — 70_evaluation_traces_preuves.md
   - ecarts — 80_observabilite_qualite_conversationnelle.md
   - ecarts — 90_confidentialite_partage_multitenant_roles.md
   - ecarts — 100_exports_preuves_qualiopi_lite.md
   - ecarts — 110_interfaces_formateur_tuteur.md
5. Construire le fichier `cluster2_matrice_runtime_vs_cible.md` avec les matrices par sous-domaine, en t’inspirant du style existant des matrices d’écarts (statuts, colonnes, niveau de vérité).
6. Construire le fichier `cluster2_prompts_audit_runtime_et_memoire.md` en recyclant et généralisant les templates déjà présents (ex. template_prompt_audit_memoire_intra_conversation.md) pour couvrir l’ensemble du pipeline (P0, progression, UIState, mémoire, exports).
7. Lire « Bibliothèque canonique de personae Hugo 2.0.md » et produire `cluster2_oracles_test_par_persona.md`, en reliant chaque persona aux contrats d’interface, de mémoire et d’exports pertinents.
8. Respecter strictement les garde-fous de 2.0 :
   - ne pas recentrer 