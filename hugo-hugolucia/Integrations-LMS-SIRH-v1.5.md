# Intégrations & Effets de bord (LMS/SIRH) — v1.5

**Document complémentaire** : `SPEC_POC_v1.5.md` (source de vérité / SoT)  
**Date** : 19 février 2026  
**Version** : 1.5 — Aligné avec SPEC v1.5 (Hugo POC) + design POST-POC (Julia, Felix, Hector, Jérémy)

---

## Objectif du document

Ce document décrit l'**écosystème logiciel** des organismes de formation (OF/OFA/CFA) et entreprises, les **effets de bord** identifiés lors de l'intégration de Hugo, et la **stratégie d'intégration** POST-POC.

**Public cible** :
- Architectes SI / DSI
- Chefs de projet intégration
- Administrateurs SIRH/LMS
- Product Owners / Directeurs OF

**Alignement avec SPEC** :
- Section 21 de `SPEC_POC_v1.5.md` (Intégrations & effets de bord LMS/SIRH)
- Architecture section 5 (Architecture technique)
- Doctrine section 3 (Confidentialité-first, RLS, CPU-only)

---

## Structure du document

1. [Principe architectural : Hugo = module AFEST intégrable](#1-principe-architectural--hugo--module-afest-intégrable)
2. [Écosystème logiciel OF/OFA/Entreprise](#2-écosystème-logiciel-ofofa-entreprise)
3. [Effets de bord identifiés](#3-effets-de-bord-identifiés)
4. [Stratégie d'intégration POST-POC](#4-stratégie-dintégration-post-poc)
5. [Standards e-learning (xAPI, LTI)](#5-standards-e-learning-xapi-lti)
6. [SSO & Provisioning (OIDC, SAML, SCIM)](#6-sso--provisioning-oidc-saml-scim)
7. [Impact sur modèle de données POST-POC](#7-impact-sur-modèle-de-données-post-poc)
8. [Architecture d'intégration cible](#8-architecture-dintégration-cible)
9. [Checklist intégration (avant déploiement client)](#9-checklist-intégration-avant-déploiement-client)

---

## 1) Principe architectural : Hugo = module AFEST intégrable

### 1.1 Positionnement produit

**Hugo n'est PAS** :
- ❌ Un ERP OF complet (pas de conventions, émargements, facturation)
- ❌ Un LMS généraliste (pas de SCORM, quiz, parcours e-learning classiques)
- ❌ Un SIRH (pas de gestion paie, congés, recrutement)
- ❌ Une suite tout-en-un (volontairement focalisé)

**Hugo EST** :
- ✅ Un **module AFEST réflexif** spécialisé (entretiens guidés, traces structurées)
- ✅ Un **générateur de preuves probantes** (photos, évaluations, référentiels RNCP/RS)
- ✅ Un **outil de montée en compétences** (RAG situationnel, critères d'évaluation)
- ✅ **Intégrable** dans un écosystème existant (exports CSV/JSON, API REST, SSO)

**Les autres assistants (POST-POC)** :
- Julia : import/normalisation référentiels + mapping LMS/SIRH.
- Felix : guidage Qualiopi + exports financeurs.
- Hector : support documentaire sur la bibliothèque.
- Jérémy : planification séances/ressources, propositions de remaniement et artefacts de planning auditables (snapshots, bookings), intégrables dans l’écosystème OF/SIRH.

### 1.2 Doctrine d'intégration

**Confidentialité-first** :
- Pas de synchronisation "aspirateur" (Hugo ne récupère pas toutes les données SIRH/LMS)
- Export opt-in (l'apprenant/OF décide ce qui sort)
- Partage par défaut : `share_summary=false`, `share_evidence=false`, `share_verbatim=false`
- Workflow guidé POC : au moment de la validation, proposer explicitement le partage de la synthèse (sans jamais forcer)
- Minimisation RGPD : aucun log du contenu brut (ex. `hugo_message.content`), uniquement métadonnées (IDs, timestamps, statuts, erreurs)

**Multi-tenant RLS** :
- Isolation stricte par `organisation_id`
- Contexte tenant Postgres : `SET LOCAL app.organisation_id = '{organisation_id}'` (transaction-scoped)
- Pas de "vue globale" cross-organisations (même pour SUPERADMIN)

**CPU-only souverain** :
- Pas d'API LLM externes sauf OVH endpoints
- Hébergeable on-premise ou cloud privé

---

## 2) Écosystème logiciel OF/OFA/Entreprise

### 2.1 Typologie d'outils (France)

| **Fonction** | **Outils typiques** | **Rôle** | **Relation avec Hugo** |
|-------------|-------------------|---------|----------------------|
| **Gestion administrative OF** | Digiforma, Dendreo, TousQuali, Edof, Ymag | Conventions, émargements, attestations, facturation, dossiers Qualiopi | **Complémentaire** : Hugo produit traces/preuves, ERP gère administratif |
| **LMS (Learning Management System)** | 360Learning, Moodle, Rise Up, E-TIPI, Talentsoft LMS | Contenu e-learning, SCORM, xAPI, parcours digitaux, quiz | **Complémentaire** : Hugo = AFEST réflexif, LMS = contenu/quiz. Intégration xAPI/LTI possible |
| **SIRH (SI RH entreprise)** | Workday, SAP SuccessFactors, Talentsoft, Cornerstone OnDemand, Lucca | Gestion collaborateurs, compétences, plan de formation, reporting RH | **Intégration prioritaire** : export CSV/API progression Hugo → SIRH |
| **Signature électronique** | DocuSign, Yousign, Universign | Signature conventions, bilans, attestations | **Complémentaire** : validation dans Hugo (workflow), signature administrative externe |

### 2.2 Constat : Hugo s'insère, ne remplace pas

**Modèle d'adoption** :
```
Avant Hugo :
ERP OF (admin) + LMS (e-learning) + SIRH (compétences)
   ↓
Après Hugo :
ERP OF (admin) + LMS (e-learning) + HUGO (AFEST réflexif) + SIRH (compétences)
              ↑                              ↑
         Complémentaires               Exports CSV/API
```

**Risques à éviter** :
- ❌ "Hugo va remplacer le LMS" → NON, Hugo = AFEST, LMS = e-learning
- ❌ "Hugo va gérer les conventions" → NON, ERP OF conserve l'administratif
- ❌ "Hugo va remplacer le SIRH" → NON, Hugo alimente le SIRH (flux sortant)

---

## 3) Effets de bord identifiés

### 3.1 Tableau synthétique effets de bord

| **Effet de bord** | **Risque** | **Mitigation POC** | **Mitigation POST-POC** |
|------------------|----------|-------------------|----------------------|
| **Double saisie apprenants** | Formateur crée apprenants dans Hugo ET ERP OF | Création manuelle POC (acceptable temporaire) | Import CSV apprenants, provisioning SCIM, API sync |
| **Divergence référentiels** | Mêmes compétences nommées différemment (Hugo/LMS/SIRH) | Import RNCP/RS manuel (nomenclature officielle) | Table `referential_mapping`, harmonisation RNCP/RS cross-systèmes |
| **Conflit "confidentialité vs preuve"** | Partage trop opt-in → formateur/qualité ne voient rien | **Workflow guidé** : message explicite apprenant, option UI pré-sélectionnée "synthèse uniquement" (mais aucun flag n'est à `true` sans confirmation) | Profils partage par dispositif (template "partage OF", "partage entreprise") |
| **Duplication documents** | Même doc dans Hugo ET LMS/Digiforma | MinIO Hugo : docs classe uniquement (pas de GED globale) | GED centralisée (intégration MinIO ↔ LMS via API) ou référencement (Hugo pointe vers LMS) |
| **Incompatibilité exports** | CSV Hugo ≠ CSV SIRH/ERP (colonnes, séparateur, encodage) | CSV configurable (séparateur `;`, encodage UTF-8 BOM par défaut) | Templates export (`export_template`, mapping colonnes JSONB) |
| **Authentification multiples** | Comptes séparés Hugo/LMS/SIRH (mauvaise UX) | Comptes créés manuellement POC | SSO (OIDC/SAML), provisioning automatique (SCIM 2.0) |
| **Suivi temporel désynchronisé** | Trace Hugo validée mais SIRH pas notifié → décalage | Export CSV périodique manuel (hebdo/mensuel) | Webhooks temps réel (progression Hugo → SIRH/LMS) |
| **Confusion "qui valide quoi"** | Tuteur valide dans Hugo, formateur valide dans ERP OF | Workflow clair POC : tuteur→trace, formateur→attestation ERP | Signature électronique intégrée POST-POC (lien Hugo→DocuSign) |
| **Cohérence planning & prérequis** | Séances AFEST programmées en décalage avec le reste du dispositif (pré-requis non respectés, temps morts importants, créneaux de rattrapage non planifiés) | POC : gestion manuelle du planning dans les outils existants (ERP OF, outils maison), Hugo reste centré traces/AFEST | POST-POC : assistant Jérémy exploite un modèle de planning (schedule_proposal, resource_booking, schedule_change_set) pour proposer des corrections cohérentes, les décisions restant prises dans l’ERP OF/SIRH ou par le coordo (intégration via exports ou API). |


### 3.2 Effets de bord "confidentialité-first" (spécifiques Hugo)

**Effet de bord** : Partage par défaut `share_summary=false` → tuteur/formateur ne voient **rien** tant que l'apprenant n'a pas explicitement partagé.

**Risque** :
- Tuteur frustré ("je ne vois pas la progression")
- Formateur ne peut pas évaluer sans preuves
- OF en difficulté pour prouver suivi (Qualiopi)

**Mitigation POC** :
- **Workflow guidé** : Au moment de la validation de trace, message explicite à l'apprenant :
  > "Votre tuteur/formateur a besoin de votre synthèse pour vous accompagner. Souhaitez-vous la partager ?"
- **Opt-in typique** : `share_summary=true`, `share_evidence=false`, `share_verbatim=false` (compromis)
- **Dashboard tuteur/formateur** : Affiche clairement "Aucune trace partagée" vs "3 traces partagées" (visibilité état)

**Mitigation POST-POC** :
- **Profils partage par dispositif** : "Profil OF" (partage synthèse + preuves par défaut), "Profil entreprise" (tout privé par défaut)
- **Partage automatique conditionnel** : "Si tuteur lié + validation apprenant → partage synthèse auto" (configurable)
- **Audit trail partage** : `audit_log` trace qui a partagé quoi, quand (preuve opt-in pour Qualiopi)

### 3.3 Effets de bord RLS multi-tenant (spécifiques Hugo)

**Effet de bord** : Organisation A et B sur même instance, mais **cloisonnement strict** RLS.

**Risque** :
- Intégrations cross-organisations impossibles (ex. réseau OF mutualisant données)
- Benchmarking anonymisé impossible (pas de stats "tous OF")
- Support technique limité (SUPERADMIN ne voit pas données métier)

**Mitigation POC** :
- **Tests cross-tenant obligatoires** : Org A ne lit/écrit JAMAIS org B
- **Support via audit_log** : Logs métadonnées (pas de verbatim) accessibles SUPERADMIN

**Mitigation POST-POC** :
- **Données anonymisées agrégées** : Table séparée hors RLS (opt-in explicite OF) pour benchmarking
- **Fédération multi-OF** : Si besoin réseau, architecture séparée (Hugo = instances isolées + data warehouse centralisé opt-in)

---

## 4) Stratégie d'intégration POST-POC

Cette stratégie vise une montée en puissance **progressive** des intégrations, sans transformer Hugo en ERP OF / LMS / SIRH “tout-en-un”, et en restant compatible avec la doctrine **confidentialité-first** et multi-tenant RLS. 
Le principe directeur est : d’abord garantir l’**interopérabilité minimale** (exports), puis unifier l’**identité** (SSO/SCIM), puis automatiser les **flux** (API/webhooks), et enfin standardiser côté e-learning (xAPI/LTI) si le client a un LMS/LRS.

### 4.1 Principe : intégrations progressives (priorités P0–P3)

Prioriser les intégrations permet d’éviter le “big bang” SI et de livrer vite de la valeur (Excel/ERP/SIRH) avant d’industrialiser (SSO, SCIM, temps réel). 

| **Priorité** | **Intégration** | **Standard/techno** | **Effort** | **Bénéfice** | **Risque si absent** |
|------------|---------------|------------------|----------|------------|-------------------|
| **P0** | Export CSV/JSON flexible | Templates configurables (`export_template`) | 2j | Interopérabilité immédiate Excel, import manuel SIRH/ERP | Incompatibilité exports → double saisie |
| **P1** | SSO authentification | OIDC (Keycloak, Auth0, Entra ID) | 3-5j | UX fluide, sécurité renforcée, réduction comptes orphelins | Comptes multiples → mauvaise UX, risque sécurité |
| **P1** | Import apprenants/groupes CSV | Endpoint bulk import | 2j | Évite double saisie manuelle | Double saisie OF → erreurs, charge formateur |
| **P2** | Provisioning automatique | SCIM 2.0 | 5j | Cycle vie comptes automatisé (création/désactivation) | Comptes orphelins, risque sécurité |
| **P2** | API synchronisation progression | REST API + webhooks | 3-5j | Temps réel SIRH/LMS (progression, validation) | Décalage temporel Hugo↔SIRH → reporting faux |
| **P3** | Standards e-learning (xAPI) | xAPI statements (traces → LRS) | 5-8j | Consolidation LMS/Hugo, reporting unifié | Données formation fragmentées |
| **P3** | LTI intégration LMS | LTI 1.3 (launch Hugo depuis LMS) | 5-8j | UX seamless, contexte apprenant automatique | Friction UX (double connexion) |

**Total POST-POC (P0–P3)** : ~25-35 jours (4-5 semaines sprint).

### 4.2 Séquencement recommandé

Le séquencement ci-dessous est celui qui minimise le risque : on sécurise d’abord le “format de sortie” (exports), puis l’identité, puis l’automatisation des flux, puis les standards LMS.


```
Sprint 1 (P0) : Templates export CSV/JSON configurables
   ↓ Livrable : Export SIRH/ERP "prêt à l'emploi"
   ↓
Sprint 2 (P1) : SSO OIDC + Import CSV apprenants
   ↓ Livrable : Authentification unifiée + réduction double saisie
   ↓
Sprint 3 (P2) : Provisioning SCIM + API sync progression
   ↓ Livrable : Cycle vie comptes auto + notifications temps réel
   ↓
Sprint 4 (P3) : xAPI + LTI (si LMS existant)
   ↓ Livrable : Intégration LMS complète
```

**Condition de passage** : Chaque sprint validé par tests d'intégration avant passage au suivant.

### 4.3 Note POST-POC : intégration planning (Jérémy)

Le module de planning **Jérémy** s’inscrit dans la même logique “objet métier intégrable” et dans la même doctrine de minimisation (pas de verbatim ni de contenus bruts, seulement des artefacts structurés et auditables).
Côté OF/ERP OF, l’intégration cible est un export ou une API de synchronisation des **séances planifiées** et des **bookings ressources** (formateurs, salles, cohortes) générés et validés via Jérémy.  
Côté SIRH, l’intégration peut exposer la **charge de formation** (temps planifié par collaborateur/équipe/site) à partir des artefacts “proposals acceptés / resource_bookings”, sans dupliquer l’administratif RH.  
Côté LMS, il n’y a pas d’impact direct obligatoire : la cohérence attendue est surtout entre les séances AFEST planifiées (Jérémy) et la progression/visibilité côté LMS via xAPI/LTI quand ces standards sont en place. 

---

## 5) Standards e-learning (xAPI, LTI)

### 5.1 xAPI (Experience API) — Traçabilité cross-systèmes

**Objectif** : Hugo émet des "statements" xAPI vers un **LRS** (Learning Record Store) pour tracer la progression de manière standardisée.

**Cas d'usage** :
- Consolidation Hugo + LMS (ex. Moodle + Hugo = vue unifiée apprenant)
- Reporting RH cross-systèmes (formation formelle LMS + AFEST Hugo)
- Analytics avancés (parcours apprenant multi-sources)

**Exemple statement xAPI (trace validée)** :

```json
{
  "actor": {
    "mbox": "mailto:apprenant@example.com",
    "name": "Jean Dupont"
  },
  "verb": {
    "id": "http://adlnet.gov/expapi/verbs/completed",
    "display": {"fr": "a terminé"}
  },
  "object": {
    "id": "https://hugo.example.com/traces/{trace_id}",
    "definition": {
      "name": {"fr": "Trace AFEST - Installation électrique"},
      "type": "http://adlnet.gov/expapi/activities/assessment"
    }
  },
  "result": {
    "completion": true,
    "success": true,
    "score": {"scaled": 0.75},
    "extensions": {
      "http://hugo.example.com/extensions/referential_item_id": "uuid-competence",
      "http://hugo.example.com/extensions/evaluation_level": "réalise"
    }
  },
  "context": {
    "contextActivities": {
      "parent": [{"id": "https://hugo.example.com/referentials/{ref_id}"}],
      "grouping": [{"id": "https://hugo.example.com/groups/{group_id}"}]
    },
    "extensions": {
      "http://hugo.example.com/extensions/tutor_validated": true,
      "http://hugo.example.com/extensions/evidence_count": 2
    }
  },
  "timestamp": "2026-02-17T18:30:00.000Z"
}
```

**Événements xAPI proposés** :
- `completed` : Trace validée par apprenant
- `validated` : Trace validée par tuteur/formateur
- `shared` : Trace partagée avec tuteur/formateur
- `assessed` : Évaluation compétence (niveau)

**Effort POST-POC** : **5-8j** (librairie `tincan`, endpoints `/xapi/statements`)

**Note SCORM** : Hugo n'implémente **pas** SCORM (format legacy, inadapté AFEST asynchrone). Si un parcours SCORM existe, il reste côté LMS ; Hugo s'intègre via xAPI/LTI.

### 5.2 LTI (Learning Tools Interoperability) — Lancement Hugo depuis LMS

**Objectif** : Permettre de **lancer Hugo depuis un LMS** (Moodle, 360Learning) avec SSO et contexte (groupe, apprenant).

**Cas d'usage** :
- Apprenant se connecte au LMS, clique "Entretien AFEST Hugo" → lancement Hugo avec contexte
- Pas de double authentification (SSO LTI)
- Retour progression vers LMS (gradebook LTI)

**Flow LTI 1.3** :
```
LMS (Moodle) : Apprenant clique "Entretien AFEST"
   ↓ LTI launch request (JWT signé)
   ↓
Hugo : Valide JWT, crée session, redirige vers /hugo/sessions/{id}
   ↓
Apprenant : Entretien Hugo (1 question à la fois)
   ↓
Hugo : Génération trace + validation
   ↓ LTI Assignment and Grade Services (AGS)
   ↓
LMS : Mise à jour gradebook (score, completion)
```

**Effort POST-POC** : **5-8j** (librairie `pylti1p3`, endpoints LTI provider)

**Attention** : LTI = intégration technique (pas de contenu SCORM). Hugo reste autonome, LMS = point d'entrée uniquement.

---

## 6) SSO & Provisioning (OIDC, SAML, SCIM)

### 6.1 SSO (Single Sign-On) — Authentification unifiée

**Objectifs** :
- Réduire comptes multiples (Hugo / LMS / SIRH)
- Améliorer sécurité (pas de mots de passe Hugo)
- Améliorer UX (1 connexion = accès Hugo)

**Standards** :

| **Standard** | **Usage** | **Techno** | **Effort** |
|-------------|----------|-----------|----------|
| **OIDC (OpenID Connect)** | Standard moderne, recommandé | Keycloak, Auth0, Entra ID (Azure AD), Google Workspace | 3-5j |
| **SAML 2.0** | Standard legacy, grands groupes | ADFS, Shibboleth, Entra ID | 5j |

**Flow OIDC** :
```
Apprenant : Clique "Se connecter avec Azure AD"
   ↓
Hugo : Redirige vers IdP (Entra ID)
   ↓
IdP : Authentification + consent
   ↓
IdP : Callback Hugo avec code authorization
   ↓
Hugo : Échange code contre access token + id token
   ↓
Hugo : Extrait claims (email, nom, rôles), crée/met à jour user
   ↓
Hugo : Délivre JWT Hugo (session)
   ↓
Apprenant : Accès Hugo (authentifié)
```

**Claims OIDC utilisés** :
- `sub` : Identifiant unique utilisateur (mapping `external_identity`)
- `email` : Email utilisateur
- `given_name`, `family_name` : Nom/prénom
- `groups` ou `roles` : Rôles (mapping LEARNER, TUTOR, TRAINER)

**Effort POST-POC** :
- OIDC : **3-5j** (librairie FastAPI `authlib` ou `python-social-auth`)
- SAML 2.0 : **5j** (librairie `python3-saml`)

### 6.2 Provisioning SCIM 2.0 — Cycle vie comptes automatisé

**Objectifs** :
- Créer/mettre à jour/désactiver comptes automatiquement depuis SIRH/annuaire
- Synchroniser groupes/classes depuis SIRH
- Éviter comptes orphelins (employé parti = compte désactivé auto)

**Standard SCIM 2.0** : API REST standardisée pour provisioning.

**Endpoints SCIM Hugo (POST-POC)** :

| **Endpoint** | **Méthode** | **Rôle** |
|-------------|-----------|---------|
| `/scim/v2/Users` | GET, POST, PUT, PATCH, DELETE | Gestion utilisateurs |
| `/scim/v2/Groups` | GET, POST, PUT, PATCH, DELETE | Gestion groupes/classes |
| `/scim/v2/ServiceProviderConfig` | GET | Config Hugo (capacités SCIM) |
| `/scim/v2/Schemas` | GET | Schémas SCIM supportés |

**Exemple création utilisateur SCIM** :

```json
POST /scim/v2/Users
{
  "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
  "externalId": "emp12345",
  "userName": "jdupont@example.com",
  "name": {
    "givenName": "Jean",
    "familyName": "Dupont"
  },
  "emails": [{"value": "jdupont@example.com", "primary": true}],
  "active": true,
  "roles": [{"value": "LEARNER"}],
  "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User": {
    "organization": "uuid-organisation-id"
  }
}
```

**Effort POST-POC** : **5j** (librairie `scim2-server`, endpoints SCIM 2.0)

**Attention** : SCIM = provisioning unidirectionnel (SIRH → Hugo). Hugo ne modifie pas SIRH.

---

## 7) Impact sur modèle de données POST-POC

### 7.1 Tables à ajouter

**Table `referential_mapping` (harmonisation référentiels)** :

```sql
CREATE TABLE referential_mapping (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organisation_id UUID NOT NULL,
  source_system TEXT NOT NULL,  -- 'HUGO', 'LMS', 'SIRH', 'ERP'
  source_ref TEXT NOT NULL,     -- Ex. 'RNCP38565', 'SIRH_COMP_001'
  target_referential_id UUID REFERENCES referential(id),
  target_item_id UUID REFERENCES referential_item(id),
  mapping_rules JSONB,          -- Règles transformation (ex. niveau Hugo → niveau SIRH)
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS policy
CREATE POLICY referential_mapping_tenant_isolation ON referential_mapping
USING (organisation_id = current_setting('app.organisation_id', true)::uuid)
WITH CHECK (organisation_id = current_setting('app.organisation_id', true)::uuid);
```

**Table `export_template` (enrichie POST-POC)** :

```sql
CREATE TABLE export_template (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organisation_id UUID NOT NULL,
  name TEXT NOT NULL,
  target_system TEXT,           -- 'SIRH', 'ERP', 'LMS', 'QUALIOPI'
  format TEXT NOT NULL,         -- 'CSV', 'JSON', 'XML', 'PDF'
  column_mapping JSONB,         -- {"apprenant_nom": "user.last_name", "niveau": "trace.referential[0].items[0].evaluation.level"}
  separator TEXT DEFAULT ';',
  encoding TEXT DEFAULT 'UTF-8',
  include_bom BOOLEAN DEFAULT TRUE,
  date_format TEXT DEFAULT 'YYYY-MM-DD',  -- ISO 8601 par défaut
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS policy
CREATE POLICY export_template_tenant_isolation ON export_template
USING (organisation_id = current_setting('app.organisation_id', true)::uuid)
WITH CHECK (organisation_id = current_setting('app.organisation_id', true)::uuid);
```

**Table `external_identity` (provisioning SCIM)** :

```sql
CREATE TABLE external_identity (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES "user"(id) ON DELETE CASCADE,
  external_system TEXT NOT NULL,  -- 'AZURE_AD', 'OKTA', 'LDAP', 'GOOGLE'
  external_id TEXT NOT NULL,      -- ID utilisateur dans système externe (sub OIDC, employeeNumber LDAP)
  sync_status TEXT DEFAULT 'ACTIVE',  -- 'ACTIVE', 'SUSPENDED', 'DELETED'
  last_sync_at TIMESTAMPTZ,
  metadata JSONB,                 -- Claims OIDC, attributs LDAP
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(external_system, external_id)
);

-- IMPORTANT (multi-tenant) :
-- Si `external_identity` reste sans `organisation_id`, interdire toute lecture applicative "globale".
-- Appliquer un contrôle/policy via join vers `user.organisation_id` (ou restreindre strictement à SUPERADMIN technique sans exposition métier).
```

### 7.2 Modifications tables existantes

**Table `user` (ajout colonne SSO)** :

```sql
ALTER TABLE "user" ADD COLUMN sso_provider TEXT;  -- 'OIDC', 'SAML', 'LOCAL'
ALTER TABLE "user" ADD COLUMN sso_subject TEXT;   -- Identifiant unique IdP (claim sub)
ALTER TABLE "user" ADD COLUMN last_login_at TIMESTAMPTZ;
```

**Table `audit_log` (traçage intégrations)** :

```sql
-- Ajouter types d'événements intégration
-- event_type : 'SCIM_USER_CREATED', 'SCIM_USER_UPDATED', 'SCIM_USER_DELETED',
--              'XAPI_STATEMENT_SENT', 'EXPORT_SIRH_GENERATED', 'SSO_LOGIN'
```

---

## 8) Architecture d'intégration cible

### 8.1 Diagramme architecture POST-POC

```
┌─────────────────────────────────────────────────────────────────┐
│                      Écosystème OF/Entreprise                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐        │
│  │  ERP OF      │   │  LMS         │   │  SIRH        │        │
│  │  (Digiforma) │   │  (360Learn)  │   │  (Workday)   │        │
│  └──────┬───────┘   └──────┬───────┘   └──────┬───────┘        │
│         │                  │                  │                 │
│         │ CSV/API          │ xAPI/LTI         │ CSV/API         │
│         │ (apprenants,     │ (progression)    │ (compétences)   │
│         │  groupes)        │                  │                 │
│         ▼                  ▼                  ▼                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Hugo (Plateforme FamilleIA)                │   │
│  │  ┌─────────────────────────────────────────────────┐   │   │
│  │  │  Core POC (CPU-only, RLS, confidentialité)     │   │   │
│  │  │  - Hugo (AFEST réflexif) + traces + preuves    │   │   │
│  │  │  - RAG bibliothèque classe (pgvector)          │   │   │
│  │  │  - Exports CSV/JSON (UTF-8 BOM, ; sep)         │   │   │
│  │  └─────────────────────────────────────────────────┘   │   │
│  │  ┌─────────────────────────────────────────────────┐   │   │
│  │  │  Intégrations POST-POC                          │   │   │
│  │  │  - SSO (OIDC/SAML) + provisioning (SCIM)       │   │   │
│  │  │  - xAPI statements → LRS                        │   │   │
│  │  │  - LTI 1.3 provider (launch depuis LMS)        │   │   │
│  │  │  - Webhooks progression (REST API)             │   │   │
│  │  │  - Templates export configurables (JSONB)      │   │   │
│  │  └─────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────┐                                               │
│  │  IdP         │ ← SSO OIDC/SAML                               │
│  │  (Entra ID)  │                                               │
│  └──────────────┘                                               │
│                                                                   │
│  ┌──────────────┐                                               │
│  │  LRS         │ ← xAPI statements                             │
│  │  (Learning   │                                               │
│  │   Locker)    │                                               │
│  └──────────────┘                                               │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```
Dans la cible POST-POC, on ajoute :

- un **bloc fonctionnel Jérémy** accroché à Hugo (mêmes contraintes RLS/confidentialité),  
- des **connecteurs sortants** depuis les artefacts de planning (proposals acceptés, bookings) vers :
  - ERP OF / outils planning existants (mise à jour des emplois du temps officiels),
  - SIRH (indicateurs de charge formation et cohérence planning).

### 8.2 Flux de données typiques

**Flux 1 : Provisioning utilisateurs (SIRH → Hugo)** :
```
SIRH (Workday) : Nouvel employé créé
   ↓ SCIM POST /scim/v2/Users
   ↓
Hugo : Création user + external_identity
   ↓ Notification email (optionnel)
   ↓
Apprenant : Reçoit lien activation compte
```

**Flux 2 : Authentification SSO (Hugo ↔ IdP)** :
```
Apprenant : Clique "Se connecter avec Entra ID"
   ↓ Redirect IdP (OIDC)
   ↓
IdP (Entra ID) : Authentification + consent
   ↓ Callback Hugo (code)
   ↓
Hugo : Échange code contre tokens, crée/met à jour user
   ↓ Session Hugo (JWT)
   ↓
Apprenant : Accès Hugo (authentifié)
```

**Flux 3 : Progression Hugo → SIRH (xAPI)** :
```
Apprenant : Valide trace Hugo
   ↓ Event trace_validated
   ↓
Hugo : Génère xAPI statement
   ↓ POST /xapi/statements (LRS)
   ↓
LRS : Stocke statement
   ↓ Webhook (optionnel)
   ↓
SIRH : Notification progression (API REST ou webhook)
```

**Flux 4 : Export CSV vers ERP OF** :
```
Formateur : Clique "Exporter pour Digiforma"
   ↓ POST /exports/run (template "Digiforma")
   ↓
Hugo : Génère CSV (mapping colonnes Digiforma)
   ↓ MinIO (fichier CSV)
   ↓
Formateur : Télécharge CSV
   ↓ Import manuel Digiforma
   ↓
ERP OF : Données Hugo intégrées (traces, validations)
```

---

## 9) Checklist intégration (avant déploiement client)

### 9.1 Checklist technique

- [ ] **Export CSV configurable** : Séparateur, colonnes, encodage testés avec client
- [ ] **SSO OIDC/SAML configuré** : IdP client (Entra ID, Okta, Keycloak) testé en pré-prod
- [ ] **Import CSV apprenants/groupes testé** : Fichier exemple client importé sans erreur
- [ ] **Mapping référentiels client** : RNCP/RS → nomenclature interne SIRH/LMS harmonisée
- [ ] **Tests cross-tenant isolement** : Si client multi-filiales, tests A/B validés
- [ ] **Politique rétention données validée** : RGPD client (durée conservation traces/preuves/exports)
- [ ] **Documentation API synchronisation** : Si SIRH/LMS attend API/webhooks, doc fournie
- [ ] **Webhooks progression configurés** : Si LMS/SIRH attend notifications, endpoints testés
- [ ] **Templates export validés** : Client valide colonnes/format CSV/JSON (1 export test par système cible)
- [ ] **Provisioning SCIM testé** : Création/mise à jour/désactivation users depuis SIRH validée
- [ ] **xAPI statements testés** : Si LRS client, statements envoyés et validés (format conforme)
- [ ] **LTI launch testé** : Si LMS client, lancement Hugo depuis LMS validé (SSO + contexte)

### 9.2 Checklist métier

- [ ] **Personas identifiés** : Rôles client (LEARNER, TUTOR, TRAINER, COORDO) mappés
- [ ] **Workflow partage validé** : Client valide règles partage par défaut (confidentialité-first ou adaptée)
- [ ] **Référentiels importés** : RNCP/RS client importés + overlay configuré par classe
- [ ] **Bibliothèque documentaire** : Docs procédures/sécurité client indexés (statut `ACTIVE`)
- [ ] **Tests acceptation** : Client valide entretien Hugo (1 question) + génération trace + export
- [ ] **Formation utilisateurs** : Apprenant, tuteur, formateur formés (3 sessions pilotes)
- [ ] **Support niveau 1** : Équipe client formée (création comptes, exports, troubleshooting)
- [ ] (POST-POC) Si Jérémy est utilisé : valider le **rôle du SI client comme “planning maître”** (ERP OF, outil interne, SIRH) et définir clairement :
  - quels artefacts planning Hugo/Jérémy sont exportés (propositions acceptées, bookings),
  - à quel rythme (temps réel via API/webhooks ou batch),
  - et comment on évite les doubles sources de vérité sur les emplois du temps.


### 9.3 Checklist juridique/RGPD

- [ ] **DPA (Data Processing Agreement) signé** : Si Hugo hébergé par nous (sous-traitant)
- [ ] **Registre traitements** : Hugo déclaré dans registre RGPD client
- [ ] **Mentions légales** : Informations RGPD affichées dans Hugo (traitement données, droits)
- [ ] **Consentements GPS** : Workflow opt-in GPS validé avec DPO client
- [ ] **Durée conservation** : Politique rétention traces/preuves/exports validée (ex. 3 ans)
- [ ] **Droit à l'oubli** : Procédure suppression données apprenant documentée
- [ ] **Sécurité** : Tests RLS validés, pas de logs verbatim, chiffrement TLS actif

---

## Changelog

### v1.5 — 19 février 2026

- Alignement sur `SPEC_POC_v1.5.md` comme source de vérité (sections 5, 7, 10.4, 14.2, 15.12).
- Ajout d’un effet de bord “Cohérence planning & prérequis” et de sa mitigation POST-POC via Jérémy (planning séances/ressources).
- Ajout d’un sous-chapitre sur l’intégration des artefacts planning Jérémy (exports / API vers ERP OF, SIRH, outils planning).
- Rappel explicite que Jérémy reste **POST-POC** : aucun changement du périmètre POC Hugo (AFEST, RAG bibliothèque de classe, exports Felix-ready, Qualiopi lite).


---

**FIN DU DOCUMENT — Intégrations & Effets de bord (LMS/SIRH) v1.5**
