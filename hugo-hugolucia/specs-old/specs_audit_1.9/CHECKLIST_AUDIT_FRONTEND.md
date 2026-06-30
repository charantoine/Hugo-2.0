# Checklist d’audit frontend — Hugo 1.9

## Principe général

Cette checklist doit être exécutée avec une exigence forte sur deux points :

1. la **réalité visible** de l’implémentation ;
2. la **bonne branche de référence**, c’est-à-dire la branche déjà retravaillée ergonomiquement pour être plus montrable.

Un composant présent dans le repo mais non intégré à l’UI ne compte pas comme implémentation complète.

---

## A. Branche et base front

- [ ] Identifier la branche effectivement utilisée pour l’implémentation.
- [ ] Identifier la branche ergonomique “plus montrable”.
- [ ] Vérifier si les travaux LOT 2 ont été faits sur cette branche ou non.
- [ ] Qualifier l’écart si les travaux ont été faits sur une mauvaise base front.
- [ ] Vérifier s’il y a dette de merge ou divergence de design.

---

## B. Architecture UI attendue

### B1. Adaptation UI via UIState
- [ ] Le front consomme bien `UIState` comme modèle produit dérivé.
- [ ] Le front n’expose pas des champs P0 bruts.
- [ ] Les anciens signaux debug/techniques ont été retirés ou encapsulés.

### B2. Fichiers attendus
- [ ] `frontend/src/hugo/progressionLabels.js` présent.
- [ ] `frontend/src/hugo/engagementUiModel.js` réellement remplacé.
- [ ] `frontend/src/hugo/components/HugoProgressPanel.jsx` présent.
- [ ] CSS ou styles associés présents.

### B3. Intégration réelle
- [ ] `HugoProgressPanel` est monté dans la vue utile.
- [ ] Les données viennent réellement de `/ui-state`.
- [ ] Le composant n’est pas dormant / code mort.

---

## C. États visibles à vérifier

### C1. Progression de scène
- [ ] `sceneLabel` affiché.
- [ ] `sceneProgress` visible / utilisé.
- [ ] le libellé évolue de manière crédible (`Raconter`, `Explorer`, `Synthétiser` ou équivalent attendu).

### C2. Quête / focus actif
- [ ] `activeQuestLabel` affiché.
- [ ] `questProgress` visible ou utilisé.
- [ ] focus compréhensible pour un utilisateur non technique.

### C3. Maturité et actions
- [ ] `maturityColor` utilisé proprement.
- [ ] `synthesisButtonState` géré (`locked`, `possible`, `ready`).
- [ ] `evaluationButtonState` géré (`locked`, `possible`, `ready` selon design retenu).
- [ ] états visuels cohérents avec la progression.

### C4. Gamification profile
- [ ] prise en charge de `gamification_profile`.
- [ ] fallback front propre si valeur invalide.
- [ ] cohérence avec fallback backend sur `B`.

---

## D. Actions fonctionnelles

### D1. Synthèse
- [ ] bouton / action synthèse visible quand pertinent.
- [ ] état `possible` distinct de `ready` si prévu.
- [ ] appel réseau réel vers `request-synthesis` ou endpoint final câblé.
- [ ] rendu de réponse correct.

### D2. Évaluation
- [ ] bouton / action évaluation visible quand pertinent.
- [ ] appel réseau réel vers `request-evaluation` ou endpoint final câblé.
- [ ] gestion des états et erreurs.

### D3. Posture si exposée
- [ ] lecture de la posture actuelle si l’UI l’expose.
- [ ] changement de posture si l’UI le permet.
- [ ] gestion des warnings / transitions refusées.

---

## E. Ergonomie et montrabilité

### E1. Vérification visuelle globale
- [ ] le front montre réellement les nouveautés attendues.
- [ ] la progression conversationnelle est perceptible.
- [ ] la différence avec l’ancien front est significative.
- [ ] la qualité visuelle est compatible avec un usage “montrable”.

### E2. Régression potentielle
- [ ] pas de régression de la branche ergonomique.
- [ ] pas de perte de lisibilité.
- [ ] pas de retour à un état plus technique / moins démonstratif.

### E3. Responsive / rôles
- [ ] expérience LEARNER mobile crédible.
- [ ] expérience TUTOR / TRAINER desktop crédible.
- [ ] PWA / responsive non cassés sur les écrans clés.

---

## F. Réseau et intégration

- [ ] appels `/ui-state` observables en réseau.
- [ ] appels synthèse / évaluation observables.
- [ ] erreurs réseau gérées proprement.
- [ ] états chargement présents.
- [ ] données réellement rendues, pas mockées localement.

---

## G. Comptes / rôles côté front

- [ ] écran ORGADMIN identifiable ou non.
- [ ] écran SUPERADMIN identifiable ou non.
- [ ] écran gestion apprenants / tuteurs identifiable ou non.
- [ ] écran formateur de co-construction identifiable ou non.
- [ ] ce qui est absent est classé absent ou hors périmètre, pas oublié.

---

## H. Preuves à collecter

- [ ] captures avant / après si possible
- [ ] captures de l’écran apprenant
- [ ] captures écran tuteur / formateur
- [ ] captures écran admin éventuel
- [ ] vidéo courte ou suite de screenshots sur le parcours clef
- [ ] console errors éventuelles
- [ ] requêtes réseau pertinentes
- [ ] mapping composant -> endpoint -> état visible
