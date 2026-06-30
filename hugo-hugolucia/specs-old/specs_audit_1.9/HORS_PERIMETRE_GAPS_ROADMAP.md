# Hors périmètre, gaps documentaires et points roadmap

## Objet

Ce document sert à empêcher Cursor de confondre :
- ce qui est spécifié ;
- ce qui est partiellement balisé ;
- ce qui est explicitement hors périmètre de ce paquet de lots ;
- ce qui a été demandé dans le fil mais n’est pas encore suffisamment formalisé.

---

## 1. Hors périmètre explicitement mentionné par le README des lots

Les éléments suivants sont signalés comme hors périmètre ou postérieurs à ce paquet documentaire :

- interface formateur de suivi et co-construction post LOT 5 ;
- mémoire formation complète multi-cohortes post LOT 4 V2 ;
- agents dynamiques recomposables après validation des 3 modes LOT 3 ;
- intégration Julia et autres acteurs de l’écosystème ;
- RAG complet dépendant d’une architecture bibliothèque active ultérieure.

Conséquence : si Cursor constate leur absence, il ne doit pas les qualifier comme “bug” mais comme `hors périmètre documentaire de ce paquet`, sauf si un élément plus haut dans la hiérarchie les rend obligatoires.

---

## 2. Gaps documentaires sur les comptes / administration métier

### Ce qui est balisé
- comptes créés manuellement dans le POC ;
- rôles LEARNER / TUTOR / TRAINER / COORDO / ORGADMIN / SUPERADMIN ;
- ORGADMIN peut administrer users, groups et exports ;
- SUPERADMIN = admin technique globale cadrée ;
- `POST /admin/users` est mentionné dans la SPEC.

### Ce qui n’est pas suffisamment détaillé dans les lots fournis
- espace UI complet de superadmin ;
- espace UI complet de gestion métier des comptes apprenants / tuteurs ;
- workflow détaillé création / suppression / rattachement formation / modification des consignes pédagogiques côté interface tuteur ;
- articulation exacte entre admin technique, admin OF et interface formateur.

### Consigne d’audit
Ces points doivent être classés en priorité comme :
- `partiellement spécifié` ;
- ou `demande du fil non encore suffisamment balisée` ;
- jamais comme si la spec détaillée existait déjà si ce n’est pas le cas.

---

## 3. Gaps sur le front et la branche ergonomique

La contrainte “les modifications front devaient être appliquées sur la branche déjà rendue plus montrable ergonomiquement” est une **consigne contextuelle du fil**, pas un point lisible tel quel dans les lots.

Conséquence :
- c’est un critère valide d’audit ;
- mais il doit être étiqueté `consigne contextuelle du fil`, pas `spec explicite du lot`.

---

## 4. Points à arbitrer explicitement si absents du code

Cursor doit marquer `à arbitrer` au lieu d’inventer quand il manque une réponse nette sur :

- branche front de référence métier montrable ;
- existence d’un espace superadmin réellement utilisable ;
- existence d’un espace métier tuteur / formateur de gestion des comptes ;
- niveau exact d’implémentation UI de LOT 5 ;
- niveau exact d’implémentation produit visible de LOT 6 ;
- politique de fusion entre branche ergonomique et branche fonctionnelle.

---

## 5. Roadmap probable issue du corpus

Sans surinterpréter, les trajectoires naturelles suggérées par le corpus sont :

### Court terme
- fiabiliser LOT 0 à LOT 4 ;
- vérifier que LOT 2 est réellement visible côté front ;
- clarifier la gestion des comptes et espaces admin existants ;
- produire une vraie cartographie de l’état code / UI / branches.

### Moyen terme
- pousser LOT 5 si la base trainer est réellement présente ;
- matérialiser l’interface formateur de suivi / co-construction ;
- compléter la gouvernance des comptes et rattachements de formation.

### Plus tard
- mémoire multi-cohorte enrichie ;
- agents recomposables ;
- intégrations écosystème ;
- RAG complet plus ambitieux.

---

## 6. Règle pratique pour Cursor

Quand un point n’est pas clairement couvert, toujours choisir parmi :

- `hors périmètre documentaire` ;
- `partiellement balisé` ;
- `consigne contextuelle du fil` ;
- `à arbitrer`.

Ne jamais le transformer automatiquement en “non conforme” sans préciser la base documentaire exacte.
