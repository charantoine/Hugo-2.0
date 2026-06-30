# Mémo CTO — Travaux depuis le dernier dépôt GitHub

**Date du mémo :** 30 juin 2026  
**Public :** direction technique, lead dev, produit  
**Workspace :** `/Users/machin/Desktop/Zone de travail Hugo`

---

## Résumé exécutif

**Dernier dépôt GitHub confirmé : 20 juin 2026.**

Tout le travail décrit ci-dessous est **post-push** : il existe localement (code + documentation `docs-workspace`) mais **n’a pas encore été intégré** au dépôt distant à la date de rédaction de ce mémo.

Environ **10 jours** de convergence non poussée, regroupables en **cinq vagues** :

| Vague | Période (approx.) | Thème principal |
|-------|-------------------|-----------------|
| **A** | 21–23 juin | Recalage doc runtime admin ; audit UI `/dashboard`, `/users`, hub conversation |
| **B** | 26 juin | Audits superadmin, wizard onboarding, suffixe mk1/mk2, organisation active front admin |
| **C** | 29 juin | Fiche comptes démo (doc 11) ; protocole E2E Playwright — **23 PASS / 0 FAIL** |
| **D** | fin juin | Bibliothèque formateur — fiabilité documentaire, RAG, tests ; audit front formateur (4 docs) |
| **E** | 30 juin | Front apprenant v2 ; seeds `OF_test_2` ; ACL formateur `GET /groups/` ; **navigation formateur prod** (entrée `/app/trainer/knowledge`, référentiels shell prod, topbar « Chat apprenant ») ; doc seed + ce mémo |

**Impact produit :** parcours admin mieux documenté et partiellement amélioré en local ; protocole E2E reproductible ; UX apprenant bêta simplifiée ; biblio formateur plus fiable ; jeu de comptes testeurs externes (`OF_test_2`) reproductible.

**Impact technique :** dette seed partiellement réduite ; incohérence ACL TRAINER corrigée ; couverture tests library + seed renforcée ; documentation workspace considérablement enrichie **hors git**.

**Risque principal :** **écart croissant** entre GitHub (photo du 20/06) et l’état local réel — push et release note nécessaires avant toute démo « officielle » ou handover distant.

---

## Référence git utilisée

| Élément | Valeur | Confiance |
|---------|--------|-----------|
| **Dernier dépôt GitHub** | **2026-06-20** | **Haute** — confirmé par le porteur de projet |
| Contenu probable du push du 20/06 | Profils conversationnels globaux apprenant ; campagne tests 20/06 PM (archive `tests_hugo_2_0_2026-06-18_20.md` §2 bis) ; mise à jour `README` docs-workspace (§7.6 pipes conversationnels) | **Moyenne** — déduit de la doc datée 20/06 |
| État comparé | Workspace local au **2026-06-30** | **Haute** (fichiers présents) |
| Métadonnées `.git` locales | Absentes dans cette copie workspace | **Constat** — pas de `git diff` automatique |

**Méthode :** point zéro = **20/06/2026 push GitHub** ; périmètre = documents datés post-20/06 + modules code modifiés observés + fils de travail Cursor.

**Non affirmé sans preuve git :** liste exacte des fichiers contenus dans le commit du 20/06 — à recouper avec `git log --since=2026-06-20` sur les dépôts distants.

---

## Périmètre des changements (vue d’ensemble)

### Documentation `docs-workspace` (post-20/06)

| Document / lot | Date | Objet |
|----------------|------|--------|
| `DOC_RUNTIME_UPDATE_2026-06.md` | 23/06 | Recalage audit UI admin/superadmin |
| `audit-ui-runtime-2026-06/` | 23/06 | Audit admin + QA post-UX |
| `VERIF_COHERENCE_SUPERADMIN_2026-06-26.md` | 26/06 | Cohérence mode superadmin |
| `AUDIT_ORGANISATION_ACTIVE_FRONT_ADMIN_2026-06-26.md` | 26/06 | Org active côté front admin |
| `PROTOTYPE_WIZARD_ONBOARDING_SAFE_2026-06-26.md` | 26/06 | Wizard onboarding |
| `WIZARD_ORG_GROUP_UPDATE_2026-06-26.md` | 26/06 | Mise à jour wizard org/groupe |
| `VERIF_SUFFIXE_MK1_MK2_2026-06-26.md` | 26/06 | Clarification suffixe mk1 (fixture, pas métier) |
| `audit-ui-runtime-front-admin-2026-06-26.md` | 26/06 | Audit front admin complémentaire |
| `11_FICHE_COMPTES_ET_DONNEES_DEMO.md` | 29/06 | Comptes, bootstrap, checklist pré-démo |
| `e2e-protocol-runtime/RAPPORT_E2E_PROTOCOL.md` | 29/06 | 23 tests E2E PASS |
| `audit_front_formateur_00` à `04` | juin (post-20/06) | Audit + matrice + backlog + conception RAG formateur |
| `seed-strategies.md` | 30/06 | Stratégies seed consolidées |
| `DOC_RUNTIME_UPDATE_2026-06-30.md` | 30/06 | Passe doc seeds / learner v2 / fiabilité |
| Mises à jour `03`, `08`, `09`, `00`, `README`, écarts 31/40 | 30/06 | Alignement état réel |

### Code backend (post-20/06 — observé)

| Zone | Changements significatifs |
|------|---------------------------|
| `apps/library/` | Fiabilité `document.meta`, scoring RAG, réindexation ; tests `test_reliability_rag_and_reindex.py` |
| `apps/accounts/seeds/` | Scénario `demo_test_2`, `group_attachments.py`, `bootstrap_demo_test_2` |
| `apps/referentials/views_groups.py` | ACL `GET /groups/` pour `TRAINER` |
| `apps/hugo/` | Playbook formateur, `rag_support`, meta knowledge (`0021_trainer_knowledge_item_meta`) |
| Tests | `test_demo_test_2_seed`, `test_trainer_group_list`, library tests (50/50 au chantier fiabilité) |

### Code frontend `frontend_1.8` (post-20/06 — observé)

| Zone | Changements significatifs |
|------|---------------------------|
| Apprenant | Layout v2 (`VITE_LEARNER_UI_V2`, défaut ON) — `LearnerConversationFeed`, `LearnerActionSidebar`, `ProdLearnerWorkspace` |
| Formateur | `ProdTrainerLibraryView` — fiabilité inline + réindex auto ; `trainerLibrary.js` |
| Tests | `trainer_library_reliability.spec.ts` (TLIB-REL-01/02 PASS) ; `trainerLibrary.test.js` |

---

## Travaux réalisés (détail par thème)

### 1. Documentation et gouvernance (vagues A–C)

**Réel confirmé (docs datées post-20/06) :**

- Recalage runtime admin : création TRAINER depuis superadmin, hub conversation vs legacy, parcours onboarding partiellement documentés (`DOC_RUNTIME_UPDATE_2026-06`).
- Audits 26/06 : superadmin, wizard org/groupe, clarification **mk1** = suffixe fixture interne (pas concept UI).
- **Fiche comptes 11** : inventaire smoke / demo / tenant ; commandes `bootstrap_*` ; checklist pré-démo 5 min.
- **Protocole E2E** (29/06) : 23 PASS, 5 SKIP — preuve login `demo.superadmin`, parcours smoke, switch org.

**Impact :** meilleure traçabilité démo locale ; réduction des collisions de vocabulaire (mk1, prompt apprenant vs tuteur).

### 2. Bibliothèque formateur — fiabilité et RAG (vague D)

**Réel confirmé :**

- `trainer_reliability` dans `document.meta` influence `safety_or_quality_risk_level` en contexte RAG.
- Front réindexe après PATCH fiabilité (évite chunks stale).
- Tests backend dédiés + E2E TLIB-REL-01/02 PASS.
- Audit front formateur (4 documents) : matrice écarts, backlog, conception RAG conversation.

**Écart connu :** `TLIB-RAG-01` (gate RAG AFEST) — **échec non corrigé** dans ce lot.

### 3. Front apprenant 2.0 — affichage (vague E)

**Réel confirmé :**

- Flag `VITE_LEARNER_UI_V2` (défaut `true`) — layout fil central + sidebar droite.
- **Pas de changement** endpoints / orchestrateur / UIState.

**Cible 2.0 :** **PARTIEL** — chrome UX uniquement.

### 4. Seeds et rattachements org / groupe (vague E)

**Réel confirmé :**

- Commande `bootstrap_demo_test_2` — org `OF_test_2`, comptes `*_test_2` / `demo123`, RNCP38878, clone profil mk1.
- Helpers `group_attachments.py` ; tests rattachements.
- Correction ACL : formateur voit tous les groupes org dans `GET /groups/` (aligné biblio org-wide).

**Documentation :** `seed-strategies.md` ; mise à jour doc 11 §4.4.

### 5. Navigation formateur — shell prod (vague E, fin juin)

**Réel confirmé :**

- `resolveAuthenticatedHome()` : TRAINER pur → `/app/trainer/knowledge` (plus `/dashboard` par défaut en mode `tester`).
- Routes prod : `/app/trainer/referentials` (+ import) — réutilisation vues existantes, layout prod.
- Topbar : « Mon espace » renommé **« Chat apprenant »**, déplacé à droite ; lien **« Espace formateur »** inchangé (hub).
- Navbar testeur : lien « Référentiels » réservé aux org admins (`TesterLayout`).
- Tests : `frontendConfig.test.js` (3 tests) ; suite front 42/42 PASS.

**Limite connue :** `/group/:groupId/referential` reste shell testeur — non migré.

**Micro-navigation (juin 2026) :** libellé unifié **« Retour orchestrateur »** (ex-« Retour connaissance ») sur bibliothèque, élicitation et référentiels shell prod ; cible `/app/trainer/knowledge`.

### 6. Passe documentaire de consolidation (30/06)

- Création `seed-strategies.md`, `DOC_RUNTIME_UPDATE_2026-06-30.md`, ce mémo (révisé avec ancrage 20/06).
- Mises à jour ciblées 03 / 08 / 09 / 11 / README / écarts 31 et 40.
- Balisage obsolète `restore_rncp38878_smoke.py`.

---

## Impacts produit et techniques

| Dimension | Depuis le 20/06 (non poussé) |
|-----------|------------------------------|
| **Démo / QA** | Protocole E2E 23 PASS documenté ; fiche comptes complète |
| **Admin** | Audits UI + wizard documentés ; patches superadmin analysés |
| **Apprenant** | UX v2 bêta activable/désactivable par flag |
| **Formateur** | Hub prod en entrée ; référentiels globaux shell prod ; fiabilité biblio + réindex ; visibilité groupes TRAINER |
| **Bêta externe** | Seed `OF_test_2` idempotent |
| **Dette** | ~10 jours de travail hors git ; smoke_playwright pas encore sur `group_attachments` |
| **Encoors** | **A_VÉRIFIER** pour l’ensemble des changements post-20/06 |

---

## Dette / risques / points ouverts

| Sujet | Statut | Action suggérée |
|-------|--------|-----------------|
| **Écart git local / GitHub** | **Critique** | Push structuré (backend + front + docs) avec release note datée |
| Encoors vs local | **A_VÉRIFIER** | Rejouer E2E protocol + seeds sur distant |
| TLIB-RAG-01 | Échec connu | Chantier gate RAG AFEST |
| Config référentiel par groupe en prod | **Ouvert** | `/group/:id/referential` reste testeur — migration shell prod à planifier |
| Admin user sans membership | Inchangé | Workflow doc 11 + `seed-strategies.md` |
| Hash exact commit 20/06 | **A_VÉRIFIER** | `git log` sur remote pour release note précise |

---

## Recommandations à court terme

1. **Push GitHub prioritaire** — regrouper en 2–3 commits logiques :
   - docs post-20/06 (`docs-workspace/`) ;
   - backend (library fiabilité, seeds, ACL formateur) ;
   - front (learner v2, trainer library, **navigation formateur prod**).
2. **Release note** depuis le 20/06 — s’appuyer sur ce mémo + `DOC_RUNTIME_UPDATE_2026-06-30.md`.
3. **Rejouer** `npm run test:protocol` + `bootstrap_demo_test_2` + `test_demo_test_2_seed` avant merge.
4. **Décider** statut `VITE_LEARNER_UI_V2` en démo client.
5. **Planifier** push Encoors ou documenter explicitement l’écart.

---

## Chronologie synthétique (depuis push 20/06)

```
2026-06-20  ████  DERNIER PUSH GITHUB (profils globaux / tests 20/06 — probable)
2026-06-23  ░░░░  DOC_RUNTIME_UPDATE + audit UI admin
2026-06-26  ░░░░  Audits superadmin, wizard, mk1/mk2
2026-06-29  ░░░░  Fiche comptes 11 + E2E protocol 23 PASS
2026-06-30  ░░░░  Learner v2, seeds OF_test_2, fiabilité formateur, **nav formateur prod**, doc seed, ce mémo
            ────  État local actuel (NON POUSSÉ)
```

---

## Renvois

| Document | Rôle |
|----------|------|
| `seed-strategies.md` | Référence seeds |
| `DOC_RUNTIME_UPDATE_2026-06-30.md` | Passe doc 30/06 |
| `DOC_RUNTIME_UPDATE_2026-06.md` | Passe doc 23/06 |
| `11_FICHE_COMPTES_ET_DONNEES_DEMO.md` | Comptes démo |
| `e2e-protocol-runtime/RAPPORT_E2E_PROTOCOL.md` | Preuves E2E 29/06 |
| `tests/archives/tests_hugo_2_0_2026-06-18_20.md` | Baseline probable du push 20/06 |

---

*Mémo CTO — ancrage dernier push GitHub : **2026-06-20** (confirmé). État local décrit au 2026-06-30.*
