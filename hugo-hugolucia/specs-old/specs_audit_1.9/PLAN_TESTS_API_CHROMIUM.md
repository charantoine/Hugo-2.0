# Plan de tests API + Chromium — Audit Hugo 1.9

## Objectif

Ce plan vise à tester **ce qui est réellement implémenté**, pas seulement ce qui est présent dans le code. Il couvre :

- backend API ;
- intégration backend/front ;
- comportements critiques ;
- visibilité réelle dans l’interface ;
- simulation navigateur Chromium / Playwright.

---

## 1. Préparation de l’environnement

### 1.1 Prérequis
- environnement local ou sandbox capable de lancer backend + front ;
- accès à la branche auditée ;
- possibilité de seed de données ;
- comptes multi-rôles ;
- au moins deux organisations / tenants ;
- jeu minimal de sessions Hugo et de groupes.

### 1.2 Jeu de données minimal
Préparer :
- org A ;
- org B ;
- 1 ORGADMIN org A ;
- 1 SUPERADMIN global ;
- 1 TRAINER org A ;
- 1 TUTOR org A ;
- 2 LEARNER org A ;
- 1 LEARNER org B ;
- 1 groupe / formation org A ;
- 1 session Hugo avec progression faible ;
- 1 session Hugo avec progression orange ;
- 1 session Hugo avec progression green ;
- 1 référentiel minimal ;
- 1 document de classe ACTIVE ;
- si possible 1 item TrainerKnowledgeItem ;
- si possible 1 LearnerThemeMemory.

### 1.3 Stratégie de preuves
Conserver :
- logs de commandes ;
- traces réseau ;
- captures d’écran ;
- JSON de réponses API ;
- copies des erreurs ;
- mapping test -> résultat -> preuve.

---

## 2. Campagne API backend

## A. Tests fondation

### A1. Santé des endpoints de base
- `POST /auth/login`
- `GET /me`
- `POST /admin/users` si disponible
- `POST /groups`
- `GET /groups`

### A2. Multi-tenant
Scénarios :
- un utilisateur org A ne lit pas les sessions org B ;
- un utilisateur org A ne lit pas les mémoires org B ;
- un utilisateur org A ne lit pas les connaissances formateur org B ;
- vérifier les retours 403/404/vides selon design.

## B. Hugo sessions

### B1. Session / progression
- `POST /hugosessions`
- `GET /hugosessions/{id}`
- `GET /hugosessions/{id}/progress`
- `GET /hugosessions/{id}/ui-state`
- `GET /hugosessions/{id}/posture`

Contrôles :
- réponse structurée ;
- UIState sans champ P0 brut ;
- gamification profile fallback ;
- cohérence progression / UIState.

### B2. Messages / tour
- `POST /hugosessions/{id}/messages`

Contrôles :
- mise à jour de `conversationprogress` après le tour ;
- pas de casse du noyau P0 ;
- présence des artefacts attendus en sandbox si activés.

### B3. Phase / classifier
- `PATCH /hugosessions/{id}/phase`
- `PATCH /hugosessions/{id}/classifier-config`

Contrôles :
- overrides pris en compte ;
- pas de régression sur le flux principal.

## C. Postures

- `POST /hugosessions/{id}/set-posture`

Contrôles :
- posture valide acceptée ;
- posture invalide rejetée ;
- transition interdite rejetée ;
- warning si maturité insuffisante quand prévu.

## D. Synthèse / évaluation

- endpoint `request-synthesis` ou équivalent
- endpoint `request-evaluation` ou équivalent

Contrôles :
- déclenchement réel ;
- réponse structurée ;
- conditionnement par éligibilité.

## E. Mémoire thématique

- `GET /hugosessions/{id}/memory-summary`

Contrôles :
- structure attendue ;
- pas de verbatim brut ;
- organisationid correct ;
- cohérence avec `LearnerThemeMemory`.

## F. Base de connaissances formateur

Si les routes existent :
- récupération questions d’élicitation ;
- sauvegarde réponses ;
- validation / rejet / édition item.

Contrôles :
- création d’items ;
- status correct ;
- validation humaine explicite ;
- pas d’auto-validation abusive.

## G. Analytics / observabilité

Si présents :
- routes analytics ;
- cohérence des signaux ;
- absence d’exposition non prévue de verbatim.

---

## 3. Campagne Chromium / Playwright

## A. Parcours LEARNER

### A1. Ouverture session
- se connecter en apprenant ;
- ouvrir une session Hugo ;
- vérifier chargement UI.

### A2. Envoi message
- envoyer un message ;
- vérifier la réponse ;
- vérifier la mise à jour visuelle de la progression.

### A3. Progress panel
- vérifier présence de la zone de progression ;
- relever `sceneLabel`, `questLabel`, état maturité ;
- vérifier si la progression varie entre session RED / ORANGE / GREEN.

### A4. Synthèse / évaluation
- vérifier apparition ou non des boutons selon maturité ;
- cliquer si disponibles ;
- capturer résultat et requêtes réseau.

## B. Parcours TUTOR / TRAINER

### B1. Accès dashboard / suivi
- vérifier l’existence des écrans ;
- vérifier la visibilité des traces partagées uniquement ;
- vérifier absence ou présence de modules de comptes.

### B2. Base de connaissances formateur
Si présente en UI :
- accéder à l’espace ;
- créer / éditer / valider un item ;
- capturer les états et les routes.

## C. Parcours ORGADMIN

### C1. Administration users / groups
- vérifier présence réelle d’un espace ;
- créer ou tenter de créer un compte ;
- rattacher à un groupe si possible ;
- capturer limitations.

## D. Parcours SUPERADMIN

### D1. Administration technique globale
- vérifier l’existence réelle de l’espace ;
- vérifier qu’il n’expose pas librement le contenu apprenant ;
- vérifier séparation admin technique / accès métier.

---

## 4. Assertions clés à intégrer dans les scripts

### API
- statut HTTP attendu ;
- schéma JSON attendu ;
- absence de champs interdits ;
- statut rôle / autorisation correct ;
- cohérence inter-endpoints.

### UI
- présence d’éléments visibles ;
- textes / labels attendus ;
- boutons actifs / inactifs ;
- chargements et erreurs ;
- requêtes réseau correspondantes.

### Sécurité
- non visibilité cross-tenant ;
- non exposition de champs P0 bruts ;
- non accès à des contenus non partagés.

---

## 5. Sorties attendues de la campagne

Produire :
- tableau de couverture des scénarios ;
- tableau `test -> résultat -> preuve` ;
- captures par rôle ;
- logs d’échec ;
- liste des endpoints effectivement touchés ;
- conclusion par scénario : conforme / non conforme / partiel / non observable.

---

## 6. Priorité des scénarios

### Priorité 1 — Bloquants
- gel P0 non cassé ;
- progression conversationnelle ;
- UIState ;
- front branché sur `/ui-state` ;
- RLS multi-tenant.

### Priorité 2 — Majeurs
- synthèse / évaluation ;
- postures ;
- mémoire thématique ;
- gestion rôles / comptes existante ou non.

### Priorité 3 — Compléments
- base de connaissance formateur ;
- observabilité cohorte ;
- écrans plus avancés si présents.
