# Personas & Cas d'usage métier — v1.5 (alignée SPEC_POC_v1.5)

Document complémentaire : `SPEC_POC_v1.5.md` (source de vérité)
Date : 19 février 2026
Version : 1.5 — Alignement endpoints v1.5 + conservation workflows + ajout cas d’usage Jérémy (planning POST-POC)

---

## Objectif du document

Ce document détaille les personas métier et leurs cas d'usage concrets dans le contexte de la plateforme multi-tenant Hugo (POC centré AFEST).

Public cible :
- Product Owners / Chefs de projet
- UX Designers
- Développeurs (parcours utilisateurs)
- Référents Qualité / Auditeurs

Alignement avec la SPEC :
- Section 20 : Personas & cas d'usage métier
- Section 15 : API endpoints MVP
- Section 6 : Rôles et visibilité

---

## Conventions (importantes)

1) Conventions de nommage (cohérence SPEC)
- Champs et flags en snakecase

2) Endpoints dans ce document
- Les endpoints listés sont ceux du MVP POC (section 15), sauf mention explicite.
- Tag `[SPEC-GAP]` : l’endpoint est requis par les parcours/sections produit mais n’est pas listé dans la section 15 (à corriger dans la SPEC pour éviter toute ambiguïté). Actuellement (v1.5) : aucun endpoint n’est marqué `[SPEC-GAP]`.
3) Audit log (POC) — pas d’endpoint direct
- En POC, il n’y a **pas** d’endpoint de lecture directe de l’audit log (pas de `GET /admin/audit-log`).
- La traçabilité est consultée **via des artefacts** :
  - Exports (`POST /exports/run` + téléchargement)
  - Pack Qualiopi lite (`POST /quality/qualiopi/evidence-bundle`) qui inclut des extraits de `audit_log` filtrés.
- Rappel : l’audit log reste **métadonnées uniquement** (IDs, timestamps, actions, statuts, erreurs), jamais de verbatim.


---

## Structure du document

1. Principes transverses
2. Personas opérationnels (utilisateurs directs)
3. Personas stratégiques (pilotage)
4. Personas techniques (intégration SI)
5. Personas externes (audit/financement)
6. Matrice persona × fonctionnalités
7. Changelog

---

## 1) Principes transverses

### 1.1 Confidentialité-first (doctrine non négociable)

Partage par défaut :
- `share_summary=false`
- `share_evidence=false`
- `share_verbatim=false`

Workflow guidé POC :
Au moment de la validation de trace, message explicite à l'apprenant :
"Votre tuteur/formateur a besoin de votre synthèse pour vous accompagner. Souhaitez-vous la partager ?"

Opt-in typique :
- `share_summary=true`, `share_evidence=false`, `share_verbatim=false` (l'apprenant contrôle chaque niveau)

### 1.2 Multi-tenant RLS (isolation stricte)

Tous les personas opèrent dans un contexte cloisonné par organisation (`organisation_id`).

Tests obligatoires :
- Organisation A ne lit/écrit jamais de données de l’organisation B.

### 1.3 CPU-only (contrainte technique POC)

- Latence cible : 3 s
- Latence occasionnelle acceptable : jusqu’à 15 s (usage ponctuel)
- LLM : self-hosted (pas d’API externe) ou API OVH AI Endpoints

### 1.4 Planning & cohérence pédagogique (POST-POC Jérémy)

Les cas d’usage liés à la **programmation pédagogique** et au planning (remplacements, décalages, prérequis, temps morts, surcharges) sont pris en compte au **niveau design POST-POC** via l’assistant Jérémy et les tables / endpoints de planning (`schedule_proposal`, `resource_booking`, etc., voir SPEC_POC_v1.5 sections 10.4, 14.2, 15.12).  
Le POC reste centré sur Hugo, mais les personas intègrent dès v1.5 des scénarios récurrents d’absurdités planning constatés en OF : annulations non rattrapées, enchaînements incohérents, prérequis non respectés, temps d’attente excessifs entre séances, sous‑utilisation de certains formateurs ou ressources. 

---

## 2) Personas opérationnels (utilisateurs directs)

### 2.1 Apprenant / Apprenti (formation initiale ou continue)

Contexte métier :
- Alternance, formation AFEST, apprentissage en situation de travail
- Veut prouver sa progression sans surpartager avec tuteur/formateur
- Besoin de contrôle fin sur ce qui est partagé

Motivations :
- Valider ses compétences progressivement
- Constituer un livret de preuves pour son école/entreprise
- Réfléchir sur sa pratique (dimension réflexive AFEST)

Frustrations :
- Outils trop scolaires
- Impression de surveillance si partage forcé
- Difficulté à traduire ce qu’il fait en compétences

Cas d'usage détaillés :

| # | Cas d'usage | Description | Endpoints utilisés |
|---|------------|-------------|-------------------|
| U1 | Réaliser entretien réflexif AFEST guidé | Hugo pose 1 question à la fois, relances situées via RAG + référentiel | `POST /hugo/sessions`, `POST /hugo/sessions/{session_id}/messages` |
| U2 | Générer trace structurée | À partir du chat, générer `trace_rich_v1` avec couverture référentiel | `POST /hugo/sessions/{session_id}/generate-trace` |
| U3 | Valider trace personnelle | L’apprenant valide la trace avant partage optionnel | `POST /traces/{trace_id}/validate` |
| U4 | Partager sélectivement | Choisir ce qui est partagé (synthèse / preuves / verbatim) | `POST /hugo/sessions/{session_id}/share` |
| U5 | Ajouter preuve photo | Upload photo smartphone (EXIF supprimés, GPS opt-in) | `POST /evidence` |
| U6 | Visualiser timeline personnelle | Sessions/traces/compétences + manques de couverture | `GET /learners/sessions`, `GET /learners/traces` |
| U7 | Exporter livret personnel | CSV/JSON pour dossier école/entreprise | `POST /exports/run`, `GET /exports/download/{run_id}` |

Workflow type (semaine d'alternance) :
```
Lundi : Situation de travail réelle
   ↓
Mardi soir : Entretien Hugo (15 min, 1 question à la fois)
   ↓
Mercredi : Génération trace + ajout photo preuve
   ↓
Jeudi : Validation personnelle + opt-in partage synthèse
   ↓
Vendredi : Point tuteur (accès synthèse partagée uniquement)
```
| U8 | Signaler un problème de planning (temps d’attente, chevauchement) | L’apprenant remonte via la plateforme qu’il subit des temps d’attente excessifs entre deux cours ou des chevauchements avec d’autres obligations (travail, transport). Le signalement est récupéré côté coordo/Jérémy pour générer des scénarios d’ajustement. | UI front (formulaire de feedback) + traitement côté Jérémy (analyse des `resource_booking` et propositions dans un `schedule_change_set`). |

---

### 2.2 Tuteur AFEST (entreprise)

Contexte métier :
- Salarié expérimenté, pas forcément formateur diplômé
- Suit 1 à N apprenants sur le terrain
- Besoin de preuves et relances situées, sans accéder à tout

Motivations :
- Accompagner efficacement sans épier
- Détecter manques de couverture (compétences non observées)
- Préparer points hebdo avec éléments concrets

Frustrations :
- Outils trop école
- Surcharge si doit tout valider
- Manque de visibilité sur progression réelle si rien n’est partagé

Cas d'usage détaillés :

| # | Cas d'usage | Description | Endpoints utilisés |
|---|------------|-------------|-------------------|
| T1 | Accéder éléments partagés uniquement | Voir synthèse / preuves selon opt-in apprenant | `GET /dashboard/groups/{group_id}/learners/{learner_id}/timeline` |
| T2 | Valider trace apprenant | Workflow validation tuteur | `POST /traces/{trace_id}/validate` |
| T3 | Préparer point hebdo | Vue classe, éléments concrets partagés | `GET /dashboard/groups/{group_id}/learners` |
| T4 | Détecter manques couverture | Appui sur `learner_state ` (skills matrix, missing coverage) | `GET /dashboard/groups/{group_id}/learners/{learner_id}/timeline` |
| T5 | Consulter preuves partagées | Accès aux preuves si partagées | `GET /learners/evidence` |
| T6 | Exporter suivi interne | CSV prêt à intégrer au suivi entreprise | `POST /exports/run` |

Workflow type (suivi hebdomadaire) :
```
Lundi : Consulter dashboard (timeline apprenant)
   ↓
Mardi : Identifier manques de couverture (skills matrix)
   ↓
Mercredi : Point hebdo avec apprenant (synthèse partagée)
   ↓
Jeudi : Valider traces (si rôle prévu)
   ↓
Vendredi : Export CSV pour reporting RH entreprise
```

---

### 2.3 Formateur / Enseignant (OF/OFA/CFA)

Contexte métier :
- Pilotage pédagogie + évaluations
- Préparer éléments auditables Qualiopi
- Gérer référentiels RNCP/RS + bibliothèque documentaire

Motivations :
- Prouver qualité pédagogique
- Adapter dispositif par classe (overlay)
- Suivre progression collective

Frustrations :
- Outils trop génériques (pas RNCP/RS)
- Difficulté à prouver individualisation
- Temps perdu en exports/reporting

Cas d'usage détaillés :

| # | Cas d'usage | Description | Endpoints utilisés |
|---|------------|-------------|-------------------|
| F1 | Importer référentiel RNCP/RS | JSON `referential_import_v2` (critères/modalités/preuves) | `POST /referentials/import-v2` |
| F2 | Configurer overlay par classe | Exemples, questions, erreurs fréquentes | `PUT /groups/{group_id}/referential-config`, `PUT /groups/{group_id}/referentials/{ref_id}/items/{item_id}/overlay` |
| F3 | Activer bibliothèque classe | Docs ACTIVE pour RAG (procédures/sécurité) | `POST /documents`, `POST /documents/{document_id}/index`, `POST /groups/{group_id}/library` |
| F4 | Valider traces | Compléter justification évaluation (niveau/critères) | `POST /traces/{trace_id}/validate` |
| F5 | Suivre classe via dashboard | Progression cohorte + compétences | `GET /dashboard/groups/{group_id}/learners`, `GET /dashboard/groups/{group_id}/competences` |
| F6 | Exporter CSV pivot | 1 ligne par trace × item | `POST /exports/run` |
| F7 | Générer pack audit lite | ZIP minimal exploitable | `POST /quality/qualiopi/evidence-bundle` |

Workflow type (préparation dispositif) :
```
Semaine -2 : Import référentiel RNCP/RS (JSON)
   ↓
Semaine -1 : Configuration overlay classe (exemples/questions)
   ↓
Semaine 0 : Activation bibliothèque classe (procédures/sécurité)
   ↓
Semaines 1-N : Suivi dashboard + validations
   ↓
Fin dispositif : Export CSV pivot (analyse Excel/qualité)
```
#### Cas d’usage POST-POC (Formateur × Jérémy)

| # | Cas d'usage | Description | Fonctions / endpoints |
|---|------------|-------------|-----------------------|
| F8 | Signaler une erreur de programmation (prérequis non respectés) | Le formateur constate qu’une séance a été planifiée avant le module de prérequis (ex. évaluation finale avant les séquences d’apprentissage). Il signale l’anomalie, Jérémy la remonte dans un `schedule_change_set` avec des options de correction. | Signalement via UI interne (pas nécessairement un endpoint dédié), production d’un change set côté Jérémy, validation/appliquer par le coordo via `/schedules/change-sets/*`. |
| F9 | Proposer un rattrapage pour un groupe absent | Une cohorte a manqué une séance pour motif valable (site fermé, déplacement professionnel, etc.). Le formateur, avec le coordo, lance une demande de rattrapage : Jérémy cherche des créneaux (sur site ou en mixant avec une autre cohorte) pour que les apprenants suivent quand même l’activité. | Recherche de créneaux libres dans `resource_booking` pour la cohorte et le formateur concerné (ou formateur substitut), proposition de slots + éventuelle mutualisation, approbation coordo. |
| F10 | Ajuster la cadence pédagogique | Le formateur observe que les évaluations intermédiaires sont mauvaises sur un bloc de compétences (point bloquant non acquis). Il veut “refaire une passe” : Jérémy propose des reprogrammations pour insérer des séances de renforcement (sans augmenter la surcharge globale). | Croisement des résultats (via exports / dashboard) avec la structure de planning, suggestion de créneaux de renforcement, change set à valider. |

---

## 3) Personas stratégiques (pilotage)

### 3.1 Coordinateur pédagogique / Responsable de dispositif

Contexte métier :
- Cohérence multi-groupes, pilotage, reporting
- Limiter risques confidentialité (privacy-first)
- Suivi cross-classe pour consolidation

Motivations :
- Vue d’ensemble multi-dispositifs
- Anticiper problèmes (LOW_TEXT, couverture faible)
- Reporting périodique prêt à présenter

Frustrations :
- Outils fragmentés
- Risques RGPD si mauvaise config de partage
- Difficulté à comparer classes/dispositifs

Cas d'usage détaillés :

| # | Cas d'usage | Description | Endpoints utilisés |
|---|------------|-------------|-------------------|
| C1 | Créer groupes/classes | Gérer memberships + liens tuteur↔apprenant | `POST /groups`, `POST /groups/{group_id}/members`, `POST /groups/{group_id}/tutor-links` |
| C2 | Gérer bibliothèque de classe | Ajouter/consulter/activer-désactiver des docs | `POST /groups/{group_id}/library`, `GET /groups/{group_id}/library`, `PUT /groups/{group_id}/library/{group_document_id}` |
| C3 | Indexer des documents | Extraction + embeddings (best effort) | `POST /documents/{document_id}/index` |
| C4 | Exports périodiques consolidés | CSV Felix-ready multi-groupes | `POST /exports/run` |
| C5 | Vérifier isolement multi-OF | Tests cross-tenant A/B (RLS) | Tests manuels/automatisés (hors API) |


Workflow type (pilotage mensuel) :
```
Début mois : Création classes/groupes nouveaux dispositifs
   ↓
Semaine 1 : Configuration bibliothèque + règles partage
   ↓
Semaines 2-4 : Monitoring statuts extraction + dashboard
   ↓
Fin mois : Export consolidé (reporting direction)
```
#### Cas d’usage POST-POC (Jérémy — planning & corrections)

> Ces cas d’usage s’appuient sur Jérémy et les endpoints `/schedules/*` (SPEC_POC_v1.5 section 15.12). Ils sont **POST-POC** (non livrés dans le POC Hugo), mais structurent le besoin métier.

| # | Cas d'usage | Description | Fonctions / endpoints |
|---|------------|-------------|-----------------------|
| C6 | Remplacer un formateur malade | Un formateur prévient son absence la veille. Le coordo demande à Jérémy de proposer des scénarios de remplacement : autre formateur disponible sur le même site, ou mutualisation avec une autre cohorte (fusion partielle de séance), en respectant les contraintes de salles, de charge de travail et de prérequis. | Recherche de créneaux libres dans `resource_booking`, génération d’un `schedule_change_set` avec plusieurs options, validation humaine via `POST /schedules/change-sets/{id}/approve` puis `.../apply`. |
| C7 | Reprogrammer un TP annulé (manque matériel) | Une séance de TP est annulée faute de matériel disponible. Le coordo demande à Jérémy de reprogrammer le TP en utilisant un créneau un mois plus tard, tout en évitant de casser la logique pédagogique (pas mettre tous les TP en fin de parcours) et en respectant les contraintes matériels (slots `SCHED_CONSTRAINT` sur `group_document`). | Utilisation des contraintes `SCHED_CONSTRAINT` (ex. `OPENING_HOURS`, `BLACKOUT_DATES`, `COHORT_RHYTHM_RULES`), proposition de nouveaux créneaux via `POST /schedules/change-sets`, application après validation. |
| C8 | Réparer une incohérence de prérequis | Un formateur signale qu’une activité a été programmée avant que les prérequis ne soient vus (ex. TP avancé avant le module théorique). Le coordo lance une demande de “réparation” : Jérémy propose un ou plusieurs remaniements qui réordonnent les séances concernées sans créer de conflits horaires. | Analyse de séquence (ordre des séances vs. prérequis définis dans le référentiel/overlay), génération d’un `schedule_change_set` ciblé, application après validation humaine. |
| C9 | Réduire des temps morts excessifs | Les élèves remontent qu’ils attendent 2 h entre deux cours chaque semaine. Le coordo demande à Jérémy de proposer des variantes d’emploi du temps plus resserrées (within la même semaine) sans dépasser les plafonds horaires journaliers et en respectant les contraintes de ressources. | Analyse des `resource_booking` par cohorte (trous dans l’emploi du temps), génération de propositions alternatives de `schedule_proposal` avec contraintes de durée/pauses, log détaillé dans `schedule_event_log`. |
| C10 | Vérifier la cohérence globale de la programmation | Le coordo veut une vue macro : séances prévues vs. prérequis, densité par semaine, périodes surchargées ou sous‑chargées, cohérence sites/cohortes (éviter des trous dans un site et la surcharge dans un autre). Jérémy génère un rapport de cohérence et met en avant des “zones rouges” (ex. trop de séances longues en fin de journée, prérequis non respectés, TP trop regroupés). | Lecture agrégée de `schedule_proposal` et `resource_booking`, indicateurs de cohérence (pré-requis, densité, équilibre), génération d’un rapport synthétique (tableau + graphes dans le SI externe), pas forcément exposé comme endpoint public dans le POC. |

---

### 3.2 Référent Qualité / Responsable Qualiopi (OF)

Contexte métier :
- Prépare audits Qualiopi (initial/surveillance/renouvellement)
- Prouver processus appliqués (7 critères, 32 indicateurs RNQ)
- Besoin de dossier de preuves exploitable

Motivations :
- Sécuriser certification Qualiopi
- Prouver démarche qualité continue
- Minimiser charge audit (preuves vivantes)

Frustrations :
- Preuves éparpillées, difficile à consolider
- Risque d’incohérence dans les exports
- Temps perdu à reconstituer un dossier

Cas d'usage détaillés :

| # | Cas d'usage | Description | Endpoints utilisés |
|---|------------|-------------|-------------------|
| Q1 | Construire dossier de preuves | Traces/validations/preuves sur période | `POST /exports/run` |
| Q2 | Prouver suivi et progression | Timelines apprenants et statuts validations | `GET /dashboard/groups/{group_id}/learners/{learner_id}/timeline` |
| Q3 | Générer pack audit anonymisable | ZIP minimal (RGPD minimisation) incluant audit_log filtré | `POST /quality/qualiopi/evidence-bundle` |
| Q4 | Démontrer adaptation du dispositif | Référentiel + overlay + traces | `POST /referentials/import-v2`, `PUT /groups/{group_id}/referentials/{ref_id}/items/{item_id}/overlay` |

Workflow type (préparation audit Qualiopi) :
```
J-30 : Identification indicateurs RNQ cibles (ex. 3, 7, 11, 18, 22)
   ↓
J-20 : Exports CSV/JSON période concernée (traces + validations + preuves)
   ↓
J-10 : Génération pack audit lite (ZIP par indicateur, anonymize si besoin)
   ↓
J-5  : Revue cohérence
   ↓
Jour J : Dossier prêt pour auditeur (preuves vivantes)
```

---

### 3.3 Responsable Formation / L&D (entreprise privée)

Contexte métier :
- Upskilling, onboarding, intégration SI RH
- Prouver montée en compétences (ROI formation)
- Besoin d’intégration SIRH/LMS existants

Motivations :
- Déployer parcours AFEST sur le poste
- Suivre progression par compétences
- Alimenter SIRH pour reporting RH

Frustrations :
- Outils formation déconnectés du SIRH
- Difficulté à prouver impact formation
- Double saisie

Cas d'usage détaillés :

| # | Cas d'usage | Description | Endpoints utilisés |
|---|------------|-------------|-------------------|
| L1 | Déployer parcours AFEST | Réflexivité + preuves probantes | `POST /hugo/sessions`, `POST /traces/{trace_id}/validate` |
| L2 | Suivre progression | Matrice, niveaux, tendance (via vues dashboard) | `GET /dashboard/groups/{group_id}/learners`, `GET /dashboard/groups/{group_id}/competences` |
| L3 | Exporter vers SIRH | CSV/JSON pour reporting RH | `POST /exports/run` |
| L4 | Gérer SSO et provisioning | Attendus LMS/SIRH | POST-POC (OIDC/SAML, SCIM) |
| L5 | Centraliser preuves partagées | Photos/documents avec consentements | `GET /learners/evidence` |
| L6 | Alimenter LMS existant | Standards e-learning | POST-POC (xAPI, LTI) |

Workflow type (intégration SIRH) :
```
Phase 1 (POC) : Export CSV manuel vers SIRH (template)
   ↓
Phase 2 (POST-POC) : SSO OIDC + import apprenants/groupes
   ↓
Phase 3 (POST-POC) : API sync progression temps réel (webhooks)
   ↓
Phase 4 (POST-POC) : xAPI statements vers LRS
```

---

## 4) Personas techniques (intégration SI)

### 4.1 Admin SI (SIRH/LMS/IT Sec)

Contexte métier :
- Réduire risques (données perso, secrets industriels)
- Maîtriser intégrations/accès
- Conformité RGPD + sécurité

Motivations :
- Hébergement souverain (pas d’API LLM externes ou API OVH AI Endpoints)
- Politiques rétention/suppression maîtrisées
- Auditer isolation tenant (RLS)

Frustrations :
- SaaS boîte noire
- Risques de fuite verbatim dans logs
- Intégrations SI complexes (SSO/SCIM)

Cas d'usage détaillés :

| # | Cas d'usage | Description | Endpoints / moyens |
|---|------------|-------------|-------------------|
| S1 | Mettre en place SSO | SAML/OIDC + cycle de vie comptes | POST-POC |
| S2 | Auditer isolation tenant | RLS + contrôles applicatifs | Tests cross-tenant (hors API) |
| S3 | Valider hébergement souverain | Pas d’appel LLM externe sauf API OVH AI Endpoints| Audit infra |
| S4 | Politiques rétention/suppression | Preuves, verbatim, exports | Configuration MinIO |
| S5 | Contrôler effets de bord MinIO | Durée vie liens, permissions | Bucket policies |
| S6 | Limites anti-fuite | Pas de verbatim en logs, métadonnées seulement | Vérification via exports/pack Qualiopi (audit_log filtré inclus) |

Workflow type (déploiement sécurisé) :
```
Phase 0 : Audit architecture (RLS, CPU-only, ou API OVH AI Endpoints)
   ↓
Phase 1 : Tests cross-tenant A/B (organisation_id isolation)
   ↓
Phase 2 : Configuration SSO (OIDC IdP client)
   ↓
Phase 3 : Politiques rétention MinIO (lifecycle)
   ↓
Phase 4 : Audit exports/logs (pas de verbatim)
   ↓
Phase 5 : Validation RGPD (minimisation, consentements GPS)
```

---

## 5) Personas externes (audit/financement)

### 5.1 Auditeur Qualiopi / Financeur (OPCO)

Contexte métier :
- N’utilise pas l’outil au quotidien
- Exige des éléments probants cohérents
- Vérifie conformité RNQ (7 critères, 32 indicateurs)

Motivations :
- Preuves vivantes, horodatées
- Traçabilité validations/partages
- Protection données (RGPD)

Frustrations :
- Dossiers incomplets/incohérents
- Preuves fabriquées pour l’audit
- Difficulté à vérifier l’effectivité

Cas d'usage détaillés :

| # | Cas d'usage | Description | Preuves / endpoints |
|---|------------|-------------|--------------------|
| A1 | Accéder exports horodatés cohérents | Preuves vivantes avec timestamps | `POST /exports/run` + téléchargement |
| A2 | Vérifier justification par trace | Justification + critères | Export JSON `trace_rich_v1` (via exports) |
| A3 | Recevoir pack audit (POC lite) | ZIP par indicateur, audit_log filtré | `POST /quality/qualiopi/evidence-bundle` |
| A4 | Vérifier traçabilité actions | Validations/partages/exports | audit_log filtré inclus dans pack |
| A5 | Vérifier protection des données | Pas de verbatim par défaut | Règles privacy-first + partage opt-in |

Workflow type (audit Qualiopi AFEST) :
```
J-1 : Réception pack audit ZIP (indicateurs cibles)
   ↓
Jour J : Échantillonnage traces (3–5 apprenants)
   ↓
Vérif 1 : Référentiel RNCP/RS + critères d'évaluation présents
   ↓
Vérif 2 : Évaluations justifiées (niveau + critères)
   ↓
Vérif 3 : Preuves attachées (photos/docs) avec horodatage
   ↓
Vérif 4 : Traçabilité (audit_log cohérent)
   ↓
Vérif 5 : Protection données (pas de verbatim sauf opt-in)
```

---

## 6) Matrice persona × fonctionnalités

Légende :
- Primaire : fonctionnalité cœur
- Accès : consultation selon droits / partage
- Contrôle : configuration / décision
- Bénéfice : usage indirect

| Fonctionnalité | Apprenant | Tuteur | Formateur | Coordo | Qualité | L&D | Admin SI | Auditeur |
|---|---|---|---|---|---|---|---|---|
| Hugo chat (1 question) | Primaire | Accès | Accès | - | - | - | - | - |
| Génération trace | Primaire | - | Accès | - | - | - | - | - |
| Partage opt-in (3 flags) | Contrôle | Accès | Accès | Accès | Accès | - | - | - |
| Validation trace | Primaire | Accès | Accès | - | - | - | - | - |
| Preuves photo | Primaire | Accès | Accès | Accès | Accès | Accès | - | Accès |
| Timeline / dashboard | Accès | Primaire | Primaire | Primaire | Accès | Accès | - | - |
| Référentiels + overlay | - | - | Primaire | Contrôle | Accès | - | - | Accès |
| Bibliothèque classe + RAG | - | Accès | Primaire | Contrôle | Accès | - | - | Accès |
| Exports CSV/JSON | Primaire | Primaire | Primaire | Primaire | Primaire | Primaire | - | Accès |
| Planning Jérémy (proposals, change sets, bookings) | Bénéfice (moins d’absurdités planning, rattrapages possibles) | Bénéfice (meilleure cohérence séances/prérequis) | Bénéfice (outil de réparation planning, moins d’annulations et de trous) | Contrôle (valide/applique les propositions Jérémy) | Bénéfice (meilleure démonstration d’adéquation moyens / continuité pédagogique) | Bénéfice (visibilité sur la charge formation) | Contrôle (intégrations SI, pas d’exposition verbatim) | Accès (via rapports fournis par l’OF) |
| Pack Qualiopi lite (ZIP) | - | - | Accès | Accès | Primaire | - | - | Primaire |
| SSO / SCIM / xAPI / LTI | - | - | - | - | - | Accès | Primaire | - |
| Tests RLS / conformité | - | - | - | - | - | - | Primaire | Accès |

---

## 7) Changelog

### v1.5 — 19 février 2026
- Alignement sur `SPEC_POC_v1.5.md` (SoT, références sections 10.4, 14.2, 15.12).
- Ajout de cas d’usage POST-POC pour Jérémy (planning séances/ressources) côté Coordinateur et Formateur : remplacements de formateurs, rattrapage de TP, réparation de prérequis non respectés, réduction des temps morts, cohérence globale des programmations.
- Ajout d’un cas d’usage Apprenant pour la remontée de problèmes de planning (temps d’attente excessifs, chevauchements).
- Mise à jour de la matrice persona × fonctionnalités pour inclure « Planning Jérémy (proposals, change sets, bookings) » comme fonctionnalité POST-POC.
- Rappel explicite : tous les cas d’usage Jérémy sont de **design POST-POC** et ne changent pas le périmètre du POC Hugo (Hugo, RAG classe, exports Felix-ready, Qualiopi lite).

