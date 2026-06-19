# INSTRUCTIONS DE MISE EN FORME WORD

**Après avoir copié le contenu ci-dessous dans Word :**

1. **Sélectionner tout** (Ctrl+A)
2. **Police** : Calibri ou Arial, taille 11
3. **Appliquer les styles** :
   - Titre 1 (lignes commençant par `#`) : Police 18, gras, couleur bleu foncé
   - Titre 2 (lignes commençant par `##`) : Police 16, gras
   - Titre 3 (lignes commençant par `###`) : Police 14, gras
4. **Tableaux** : Sélectionner les tableaux → Création → Style de tableau "Grille claire"
5. **Blocs de code** : Police Consolas, taille 9, fond gris clair
6. **Insérer table des matières** : Références → Table des matières → Automatique

---

# Hugo, Julia, Felix et Hector
## Synopsis — Version 1.4

**Document de communication**  
Destiné aux parties prenantes non techniques

**Version** : 1.4  
**Date** : 19 février 2026  
**Référence technique** : Spécification POC v1.4

---

## En bref

Ce document présente **Hugo**, un assistant numérique pour l'accompagnement des apprenants en situation de travail (AFEST). Hugo fait partie d'une famille d'assistants (Hugo, Julia, Felix, Hector) qui forment ensemble une plateforme d'apprentissage innovante.

**Public visé** : Organismes de formation, responsables pédagogiques, chefs de projet formation, directions RH

---

## 1. Vue d'ensemble de la plateforme

Nous développons une **plateforme multi-organismes** qui regroupe plusieurs assistants numériques spécialisés, fonctionnant ensemble sous une marque commune.

### Les quatre assistants

| Assistant | Son rôle | Disponibilité |
|-----------|----------|---------------|
| **Hugo** | Accompagne l'apprenant par des questions ciblées, génère des traces d'apprentissage structurées | **Disponible dans le POC** |
| **Julia** | Gère l'organisation des classes, des groupes d'apprenants et des parcours | Après le POC |
| **Felix** | Produit les exports administratifs (financeurs, Qualiopi, suivi) | Exports disponibles dans le POC, assistant conversationnel après |
| **Hector** | Aide à trouver des ressources et de la documentation | Après le POC |

### Compatibilité avec votre écosystème existant

La plateforme s'intègre avec vos outils actuels :
- **Logiciels de gestion OF** (Digiforma, Dendreo, etc.) : pour l'administration
- **LMS** (Moodle, 360Learning, etc.) : pour les contenus e-learning
- **SIRH** : pour le suivi RH et compétences

**Important** : Hugo ne remplace pas ces outils, il les complète en apportant une spécialisation AFEST.

---

## 2. Le POC : livraison cible 2 mars 2026

### Ce qui sera disponible

**Pour les apprenants** :
- Conversations guidées avec Hugo (1 question à la fois, adaptée au contexte)
- Ajout de photos comme preuves (depuis smartphone)
- Consultation de leur historique d'apprentissage
- Partage sélectif avec leurs tuteurs/formateurs

**Pour les tuteurs et formateurs** :
- Visualisation des traces partagées par les apprenants
- Suivi de la progression par compétences
- Validation des acquis
- Exports pour vos tableaux de bord

**Pour les organismes de formation** :
- Exports CSV/Excel compatibles avec vos outils
- Pack audit Qualiopi "allégé" (version complète après le POC)
- Multi-organismes : plusieurs OF sur une même instance, données strictement séparées

### Protection des données personnelles

**Confidentialité par défaut** :
- Les conversations de l'apprenant restent privées
- Le tuteur/formateur ne voit QUE ce que l'apprenant choisit de partager
- Pas de stockage des conversations complètes (uniquement des synthèses structurées)
- Données GPS des photos : uniquement sur demande explicite de l'apprenant

---

## 3. Comment fonctionne Hugo ?

### Un accompagnement personnalisé

Hugo s'appuie sur trois sources d'information :

1. **L'historique structuré de l'apprenant**
   - Compétences déjà validées
   - Compétences en cours
   - Plans d'action en cours

2. **La bibliothèque documentaire de la classe**
   - Procédures de sécurité
   - Fiches techniques
   - Documentation métier
   - Consignes internes

3. **Le référentiel de compétences**
   - Référentiels RNCP/RS officiels
   - Adaptations spécifiques à votre classe
   - Critères d'évaluation détaillés

### Une conversation structurée

Hugo pose **une seule question à la fois**, adaptée à :
- Ce que l'apprenant a déjà fait
- Les compétences à développer
- Le contexte de travail
- Les procédures de sécurité pertinentes

Après l'échange, Hugo génère une **trace d'apprentissage** structurée qui :
- Résume la situation de travail
- Identifie les compétences mobilisées
- Liste les preuves fournies (photos, descriptions)
- Propose des axes de progression

---

## 4. Intégration dans votre organisation

### Vos référentiels de compétences

Vous pouvez importer :
- Les référentiels officiels RNCP/RS
- Vos référentiels internes
- Des adaptations par classe (exemples spécifiques, erreurs fréquentes, questions de relance)

### Vos documents de classe

Hugo utilise votre documentation existante :
- Procédures de sécurité
- Modes opératoires
- Fiches techniques
- Documents qualité

**Type de documents supportés** : PDF (texte), documents Word convertis en PDF

### Export de données

**Formats disponibles** :
- **CSV** : compatible Excel, séparateur point-virgule, encodage français
- **JSON** : pour intégrations techniques futures

**Contenu des exports** :
- Traces d'apprentissage par apprenant
- Évaluations par compétence
- Preuves associées
- Validations tuteur/formateur

---

## 5. Respect de la réglementation

### Qualiopi

**Dans le POC** : Pack audit "allégé" contenant :
- Export des traces et validations
- Liste des référentiels utilisés
- Documents de classe indexés
- Journal d'audit (validations, partages, exports)

**Après le POC** : Cartographie complète des 32 indicateurs du Référentiel National Qualité

### RGPD

**Protection des données** :
- Hébergement en France (ou cloud privé contrôlé)
- Isolation stricte des données entre organismes
- Pas de transmission à des tiers (pas d'API externe)
- Droit d'accès et suppression des données
- Durée de conservation paramétrable

**Consentements** :
- GPS des photos : opt-in explicite
- Partage avec tuteur/formateur : opt-in explicite
- Export de données : contrôlé par l'organisme de formation

---

## 6. Aspects techniques (synthèse)

### Infrastructure

- **Hébergement** : serveur unique, architecture conteneurisée (Docker)
- **Intelligence artificielle** : modèle Mistral 7B, hébergé sur vos serveurs (pas de cloud externe)
- **Base de données** : PostgreSQL avec isolation stricte multi-organismes
- **Stockage fichiers** : MinIO (compatible Amazon S3)

### Sécurité

- **Accès** : HTTPS obligatoire, authentification sécurisée
- **Isolation** : chaque organisme ne voit QUE ses données
- **Logs** : pas de stockage des conversations complètes
- **Photos** : suppression automatique des métadonnées sensibles (EXIF)

### Performance

- **Temps de réponse** : objectif 3 secondes, acceptable jusqu'à 15 secondes
- **Capacité** : plusieurs organismes et centaines d'apprenants par instance

---

## 7. Calendrier de déploiement (3 semaines)

### Semaine 1 : Infrastructure et bases
- Mise en place des serveurs
- Configuration de la sécurité multi-organismes
- Gestion des utilisateurs et authentification
- Création des classes et liens tuteurs

### Semaine 2 : Hugo opérationnel
- Conversations Hugo fonctionnelles
- Génération des traces d'apprentissage
- Système de partage et validation
- Import des référentiels de compétences

### Semaine 3 : Finalisation
- Preuves photos depuis smartphone
- Recherche documentaire complète
- Exports CSV/JSON
- Dashboard de suivi classe

---

## 8. Tests et validation

### Tests obligatoires avant mise en production

**Sécurité multi-organismes** :
- Vérification : l'organisme A ne peut pas voir les données de l'organisme B
- Vérification : l'organisme A ne peut pas modifier les données de l'organisme B

**Confidentialité** :
- Vérification : le tuteur ne voit rien sans partage explicite de l'apprenant
- Vérification : seules les informations partagées sont accessibles

**Fonctionnel Hugo** :
- Conversation 1 question à la fois
- Génération de trace structurée
- Validation tuteur/formateur
- Exports CSV et JSON exploitables

**Recherche documentaire** :
- Au moins 8 recherches sur 10 concernant des procédures doivent trouver le bon document

**Gestion photos** :
- Métadonnées EXIF supprimées
- PDF scanné détecté (sans reconnaissance de texte automatique)

---

## 9. Support et accompagnement

### Documentation fournie

1. **Spécification technique complète** (développeurs)
2. **Guide d'implémentation** (développeurs)
3. **Documentation API** (intégrations)
4. **Schémas de données** (référentiels, traces, exports)
5. **Guide Qualiopi** (conformité réglementaire)
6. **Personas et cas d'usage** (formation utilisateurs)
7. **Guide intégrations LMS/SIRH** (après POC)

### Formations recommandées

**Pour les apprenants** : 30 minutes
- Démarrer une conversation avec Hugo
- Ajouter des preuves photos
- Partager avec son tuteur

**Pour les tuteurs/formateurs** : 1 heure
- Suivre la progression des apprenants
- Valider les traces
- Exporter les données

**Pour les coordinateurs pédagogiques** : 2 heures
- Créer et gérer les classes
- Importer les référentiels
- Configurer la bibliothèque documentaire
- Générer les exports Qualiopi

---

## 10. Évolutions futures (après POC)

### Intégrations avancées

**Authentification unique (SSO)** :
- Connexion avec vos comptes existants (Azure AD, Google Workspace, etc.)
- Plus besoin de créer des comptes séparés

**Synchronisation automatique** :
- Import automatique des apprenants depuis votre SIRH
- Export automatique de la progression vers votre LMS
- Connexion aux standards e-learning (xAPI, LTI)

### Fonctionnalités étendues

**Julia (gestion avancée)** :
- Parcours partiels personnalisés
- Analytics prédictifs
- Variantes de référentiels

**Felix (exports enrichis)** :
- Assistant conversationnel pour générer des exports sur mesure
- Templates configurables par type de financeur
- Cartographie complète Qualiopi (32 indicateurs)

**Hector (ressources)** :
- Recherche avancée dans la documentation
- Recommandations de ressources pédagogiques
- Support multimédia (vidéos, podcasts)

---

## Questions fréquentes

**Hugo va-t-il remplacer nos formateurs ?**
Non. Hugo accompagne l'apprenant entre les sessions avec le formateur. Il structure les traces et facilite le suivi, mais le rôle du formateur reste central.

**Nos données sont-elles sécurisées ?**
Oui. Isolation stricte multi-organismes, hébergement contrôlé, pas d'API externe, conformité RGPD.

**Pouvons-nous utiliser nos propres référentiels ?**
Oui. Import des référentiels RNCP/RS officiels ET de vos référentiels internes, avec possibilité d'adaptation par classe.

**Combien de temps pour déployer ?**
3 semaines pour le POC complet. Intégrations avancées (SSO, synchronisation automatique) : 4-5 semaines supplémentaires.

**Hugo fonctionne-t-il hors ligne ?**
Non dans le POC. Une connexion internet est nécessaire. Évolution possible après POC pour mode dégradé hors ligne.

**Combien d'apprenants par instance ?**
Plusieurs centaines d'apprenants répartis sur plusieurs organismes de formation. Dimensionnement selon vos besoins.

---

## Glossaire

**AFEST** : Action de Formation En Situation de Travail. Modalité pédagogique où l'apprentissage se fait directement en situation professionnelle.

**CPU-only** : Calcul uniquement sur processeur (pas de carte graphique), permet un hébergement sur serveurs standards.

**LMS** : Learning Management System. Plateforme de gestion de l'apprentissage (Moodle, 360Learning, etc.).

**Multi-tenant** : Architecture permettant à plusieurs organisations d'utiliser la même instance logicielle avec isolation stricte des données.

**OF** : Organisme de Formation.

**POC** : Proof of Concept. Preuve de concept, version de démonstration fonctionnelle.

**Qualiopi** : Certification qualité des organismes de formation en France.

**RAG** : Retrieval-Augmented Generation. Technique permettant à l'IA d'utiliser votre documentation pour ses réponses.

**RGPD** : Règlement Général sur la Protection des Données.

**RLS** : Row Level Security. Sécurité au niveau ligne dans la base de données, garantit l'isolation multi-organismes.

**RNCP** : Répertoire National des Certifications Professionnelles.

**RS** : Répertoire Spécifique des certifications et habilitations.

**SIRH** : Système d'Information des Ressources Humaines.

**SSO** : Single Sign-On. Authentification unique permettant d'accéder à plusieurs applications avec un seul compte.

---

**Contact et information** : Ce document est une synthèse de communication. Pour la documentation technique complète, référez-vous à la spécification POC v1.4.

---

**Version** : 1.4  
**Date** : 19 février 2026  
**Statut** : Document de communication POC
