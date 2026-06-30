# Checklist d’audit backend — Hugo 1.9

## Mode d’emploi

Pour chaque ligne, renseigner :
- statut : `OK`, `KO`, `PARTIEL`, `NON OBSERVABLE`, `HORS PÉRIMÈTRE`, `À ARBITRER`
- preuve : fichier, test, endpoint, capture, log
- commentaire court

---

## A. Fondations P0

### A1. Gel du noyau P0
- [ ] `backend/apps/hugo/domain/turnstatev17.py` non modifié directement.
- [ ] `backend/apps/hugo/services/decisionenginev17.py` non modifié directement.
- [ ] `hugoorchestrator.py` modifié seulement par patches additifs.
- [ ] `promptrenderer.py` modifié seulement par patches additifs.

### A2. Enums canoniques
- [ ] `ConversationPosture` défini uniquement dans `conversationprofile.py`.
- [ ] `SessionMaturityLevel` défini uniquement dans `conversationprofile.py`.
- [ ] `KnowledgeItemStatus` défini uniquement dans `conversationprofile.py`.
- [ ] Aucun doublon local dans `schemas.py`, `turnstatev17.py`, `LOT3`, `LOT5`, `LOT6`.
- [ ] Le test NR-09 ou équivalent existe et protège ce point.

### A3. UIState propre
- [ ] `UIState` défini dans `conversationprofile.py`.
- [ ] Aucun champ P0 brut dans `UIState`.
- [ ] Le test NR-07 ou équivalent existe et couvre ce point.

### A4. RLS / tenant
- [ ] Usage canonique de `organisationid` avec un `s`.
- [ ] Migrations conformes à ce nom de champ.
- [ ] Filtres ORM conformes.
- [ ] Contexte transactionnel `SET LOCAL app.organisationid` appliqué.
- [ ] Test cross-tenant présent et crédible.

---

## B. LOT 0 — Contrats et fondations

### B1. Fichiers attendus
- [ ] `conversationprofile.py` existe.
- [ ] `reasoncodes.py` existe.
- [ ] `tutorprofiles.py` stub LOT 0 existe ou a été remplacé correctement plus tard.
- [ ] `test_p0_non_regression.py` existe.

### B2. Modèle de progression
- [ ] `ConversationBranch` existe.
- [ ] `ConversationProgress` existe.
- [ ] `UIState` existe.
- [ ] `reasoncodes` canoniques sont présents.

### B3. Migration et endpoints stubs
- [ ] migration ajoutant `conversationprogress` à `HugoSession`.
- [ ] stub `/progress`.
- [ ] stub `/ui-state`.
- [ ] stub `/posture`.

---

## C. LOT 1 — Progression conversationnelle

### C1. Service principal
- [ ] `conversationprogresscalculator.py` existe.
- [ ] `ConversationProgressCalculator` existe.
- [ ] `build_ui_state_from_progress` existe.
- [ ] `deserialize_conversation_progress` existe.

### C2. Calcul progression
- [ ] max 3 branches actives respecté.
- [ ] maturité RED / ORANGE / GREEN calculée.
- [ ] non-régression d’une branche GREEN.
- [ ] éligibilité synthèse calculée.
- [ ] éligibilité évaluation calculée.
- [ ] `missing_for_next_level` calculé.
- [ ] `reason_codes` calculés.

### C3. Branchement orchestrateur
- [ ] calcul après `decideconversation`.
- [ ] lecture seule sur `turnstate` et `decision`.
- [ ] persistance JSONB dans `session.conversationprogress`.
- [ ] posture session recastée correctement.

### C4. Désérialisation JSONB
- [ ] pas de `ConversationProgress(**raw)` direct en production.
- [ ] endpoints `/progress` et `/ui-state` utilisent la désérialisation explicite.
- [ ] enums et branches imbriquées bien recastées.

### C5. Endpoints
- [ ] `/progress` renvoie une structure cohérente.
- [ ] `/ui-state` renvoie un UIState propre.
- [ ] fallback `gamification_profile` vers `B` si invalide.

### C6. Tests
- [ ] test désérialisation JSONB.
- [ ] test gamification profile invalide.
- [ ] test maturité ORANGE.
- [ ] test maturité GREEN.
- [ ] test max 3 branches.
- [ ] test non-régression GREEN.

---

## D. LOT 3 — Modes / postures

### D1. Sélecteur de posture
- [ ] `postureselector.py` existe.
- [ ] `resolve_posture` ou équivalent existe.
- [ ] default posture = `reflective_afest`.
- [ ] heuristiques diagnostic / knowledgereview présentes.

### D2. Tutor profiles
- [ ] le stub `tutorprofiles.py` LOT 0 a été remplacé intégralement.
- [ ] trois postures présentes.
- [ ] règles `maxquestionsperturn` par posture présentes.
- [ ] gestes autorisés / interdits présents.

### D3. Transitions
- [ ] `posturetransitions.py` existe.
- [ ] règles de transitions présentes.
- [ ] warnings si maturité RED quand nécessaire.
- [ ] endpoint `set-posture` présent.

### D4. Rendu / prompts
- [ ] contraintes de posture injectées côté rendu.
- [ ] les contraintes internes ne sont pas exposées à l’apprenant.

### D5. Synthèse / évaluation
- [ ] `synthesisservice.py` existe.
- [ ] `request-synthesis` branché sur génération synthèse.
- [ ] `request-evaluation` branché sur génération évaluation.

### D6. Tests
- [ ] tests de profils complets.
- [ ] tests transitions.
- [ ] tests clé enum canonique.

---

## E. LOT 4 — Mémoire thématique inter-session

### E1. Modèle
- [ ] `LearnerThemeMemory` existe.
- [ ] `organisationid` avec `s`.
- [ ] unicité `(learnerid, organisationid, themekey)`.
- [ ] pas de verbatim brut.

### E2. Consolidation
- [ ] `memoryconsolidator.py` existe.
- [ ] `normalize_knowledge_status` existe.
- [ ] `consolidate_session` existe.
- [ ] consolidation seulement post-conversation.
- [ ] pas d’appel pendant un tour.

### E3. Règles métier
- [ ] `DERIVED_PROVISIONAL` ne devient pas `VALIDATED_TRAINER` automatiquement.
- [ ] stockage en `.value` avant save.
- [ ] fallback défensif en cas de statut invalide.

### E4. Endpoint / injection contexte
- [ ] `memory-summary` existe.
- [ ] injection conditionnelle mémoire dans le contexte via feature flag.
- [ ] `priorThemeMemory` ou équivalent présent sans casser P0.

### E5. Tests
- [ ] création de record.
- [ ] idempotence.
- [ ] test `organisationid`.
- [ ] test pas d’auto-upgrade provisional.
- [ ] test fallback statut invalide.

---

## F. LOT 5 — Base de connaissances formateur

### F1. Modèle
- [ ] `TrainerKnowledgeItem` existe.
- [ ] champ `status` basé sur `KnowledgeItemStatus` canonique.
- [ ] `organisationid` correct.
- [ ] champs provenance / validation présents.

### F2. Ingestion documentaire
- [ ] `documentingestor.py` existe.
- [ ] support PDF texte.
- [ ] support PDF scanné / image via vision LLM.
- [ ] extraction retourne des items structurés.
- [ ] les items extraits par LLM sont marqués `derived_provisional` si c’est la règle effectivement implémentée.

### F3. Questionnaire dialogique
- [ ] questions d’élicitation formateur présentes.
- [ ] endpoint de récupération des questions.
- [ ] endpoint de sauvegarde des réponses.
- [ ] mapping question -> contenttype correct.

### F4. Validation humaine
- [ ] endpoint validation item présent.
- [ ] action `validate`.
- [ ] action `reject`.
- [ ] action `edit`.
- [ ] validation humaine nécessaire avant `validated_trainer`.

### F5. Vues / accès
- [ ] `views_trainer.py` existe.
- [ ] routes réellement exposées.
- [ ] contrôle d’accès par organisation / rôle.

---

## G. LOT 6 — Observabilité et cohorte

### G1. Modèles / services
- [ ] `ConversationQualitySignal` existe.
- [ ] `qualitytracker.py` existe.
- [ ] `analytics/cohortdashboard.py` existe.
- [ ] `views/analytics.py` existe.

### G2. Production de signaux
- [ ] signaux de qualité générés.
- [ ] agrégations cohorte générées.
- [ ] pas d’exposition de verbatim brut si ce n’est pas prévu.

### G3. Tests
- [ ] `test_qualitysignals.py` existe.
- [ ] signaux calculés de façon traçable.

---

## H. Comptes / rôles / administration

### H1. Auth / admin de base
- [ ] endpoints `auth/login`, `admin/organisations`, `admin/users`, `me`.
- [ ] rôles présents dans le modèle / auth.
- [ ] création manuelle des comptes conforme au POC.

### H2. ORGADMIN
- [ ] peut administrer users.
- [ ] peut administrer groups.
- [ ] peut déclencher exports.
- [ ] respecte la confidentialité du contenu apprenant partagé seulement.

### H3. SUPERADMIN
- [ ] espace ou capacités techniques identifiables.
- [ ] ne dispose pas d’un accès métier libre au contenu apprenant.
- [ ] isolation multi-tenant respectée.

### H4. Gestion comptes métier avancée
- [ ] création / suppression apprenants côté interface métier.
- [ ] création / suppression tuteurs côté interface métier.
- [ ] rattachement à une formation / groupe.
- [ ] modification des consignes pédagogiques.
- [ ] statut documenté : implémenté / partiel / absent / non balisé.

---

## I. Preuves à collecter

- [ ] liste exacte des fichiers modifiés
- [ ] liste des migrations
- [ ] liste des endpoints
- [ ] capture des tests passants / échouants
- [ ] extraits de code sur points litigieux
- [ ] cartographie branche / commit / lot
