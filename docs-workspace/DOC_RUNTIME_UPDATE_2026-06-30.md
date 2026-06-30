# DOC_RUNTIME_UPDATE_2026-06-30 — Passe documentaire (depuis push GitHub 20/06)

**Date :** 30 juin 2026  
**Dernier dépôt GitHub confirmé :** **20 juin 2026**  
**Référence documentaire immédiate :** `DOC_RUNTIME_UPDATE_2026-06.md` (23 juin), travaux 26–29 juin (audits, fiche 11, E2E)

---

## Sources mobilisées

| Source | Rôle |
|--------|------|
| Confirmation porteur projet | Dernier push = **2026-06-20** |
| Code `hugo_back` / `frontend_1.8` | Réel confirmé (seeds, library, ACL, learner v2) |
| Docs datées 21–29 juin dans `docs-workspace/` | Travaux doc post-push non encore sur GitHub |
| Tests pytest + Playwright | Preuves locales |
| `memo-cto-depuis-dernier-push.md` | Synthèse CTO complète |

**Note :** pas de `.git` local — pas de diff automatique vs commit du 20/06.

---

## Périmètre « depuis le 20/06 »

| Période | Livrables principaux (doc + code) |
|---------|-----------------------------------|
| **20/06** | **Dernier push GitHub** — profils globaux apprenant, campagne tests 20/06 (probable) |
| **23/06** | `DOC_RUNTIME_UPDATE_2026-06`, audit UI admin |
| **26/06** | Audits superadmin, wizard, mk1/mk2, org active front |
| **29/06** | `11_FICHE_COMPTES`, protocole E2E 23 PASS |
| **30/06** | Seeds `OF_test_2`, learner v2, fiabilité formateur, **navigation formateur prod**, `seed-strategies.md`, ce document |

---

## Fichiers créés (passe 30/06)

| Fichier | Objet |
|---------|--------|
| `seed-strategies.md` | Stratégies seed consolidées |
| `memo-cto-depuis-dernier-push.md` | Mémo CTO (ancré 20/06) |
| `DOC_RUNTIME_UPDATE_2026-06-30.md` | Ce document |

---

## Fichiers mis à jour (passe 30/06)

| Fichier | Modification |
|---------|--------------|
| `README.md` (docs-workspace) | Liens seed + mémo ; historique |
| `11_FICHE_COMPTES_ET_DONNEES_DEMO.md` | §4.4 OF_test_2 |
| `03_ETAT_PRODUIT_REEL.md` | §2.3 navigation formateur |
| `08_FLAGS_ET_ENVIRONNEMENT_DEMO.md` | `VITE_LEARNER_UI_V2` |
| `09_PARCOURS_DEMO_ET_SCENARIOS.md` | Parcours bêta test_2 |
| `00_HIERARCHIE_DOCUMENTAIRE.md` | Renvoi seed-strategies |
| `ecarts — 31` / `40` | Bandeaux juin 30 |
| `hugo_back/apps/accounts/seeds/README.md` | Lien doc workspace |

---

## Réel confirmé (synthèse technique 30/06)

| Sujet | Constat |
|-------|---------|
| Seed OF_test_2 | Idempotent ; rattachements org + membership + tutor-link |
| ACL formateur | `TRAINER` → tous les groupes org dans `GET /groups/` |
| Navigation formateur | Entrée `/app/trainer/knowledge` ; référentiels `/app/trainer/referentials*` ; topbar « Chat apprenant » ; **« Retour orchestrateur »** sur library / élicitation / référentiels → hub |
| Learner UI v2 | Flag front, défaut ON |
| Fiabilité biblio | PATCH + réindex auto ; tests backend + E2E REL |

---

## A_VÉRIFIER

- Liste exacte des fichiers du commit GitHub du **20/06**.
- Encoors pour l’ensemble des changements post-20/06.
- Config référentiel par groupe `/group/:id/referential` — shell testeur uniquement (limite connue).

---

## Prochaine sortie utile

**Push GitHub** structuré de tout le delta depuis le **20/06** + release note (voir `memo-cto-depuis-dernier-push.md`).
