# Protocole de tests – Cluster 16 Interface apprenant conforme spec 2.0

Workspace : `Zone de travail Hugo`  
Périmètre : interface apprenant (posture/mode, profils d’affichage, mémoire visible, CTA, scène/branche/progression)  
Version : 1 – alignée sur le cluster 16 spec 2.0

---

## 0. Objectifs du protocole

- Vérifier que l’interface apprenant :
  - respecte le contrat UIState et les specs 2.0 (posture, CTA, mémoire, scène/branche),
  - différencie proprement les trois profils d’affichage (`youth`, `adult`, `professional`) **sans** divergence de logique métier,
  - ne réintroduit pas de P0, TurnState ou verbatim brut.
- Couvrir :
  - des tests backend (contrats UIState, memory, CTA),
  - des tests UI automatisés Playwright,
  - quelques scénarios manuels ciblés par persona (A1/A2/A3).

---

## 1. Pré-requis et données de test

### 1.1 Environnement

- **ENVIRONMENT** : `local`
- **BRANCH** : branche contenant les implémentations du cluster 16
- **Backend** : `hugo_back` — `pytest`
- **Front** : `hugo-hugolucia/frontend_1.8` — `ProdLearnerWorkspace` accessible

### 1.2 Sessions et profils

Préparer via :

```bash
cd hugo_back
python manage.py bootstrap_smoke_playwright
```

Le fichier `tests_playwright/smoke-fixtures.json` expose :

- `session_id` — session smoke générique
- `cluster16_sessions.youth|adult|professional` — une session par profil d’affichage

Chaque session cluster 16 a un fil avec `session_memory` alimenté et un `conversation_progress` orange avec branche active.

---

## 2. Batteries de tests backend

**Fichier** : `apps/hugo/tests/test_cluster16_interface_apprenant_backend.py`

| ID | Test pytest | Objet |
|----|-------------|-------|
| B16-P1 | `test_b16_p1_*` | UIState posture/mode, pas de P0 |
| B16-P2 | `test_b16_p2_set_posture_valid_updates_ui_state` | Bascule autorisée |
| B16-P3 | `test_b16_p3_*` | Bascule refusée, UIState cohérent |
| B16-C1 | `test_b16_c1_cta_contracts_main_fields` | Contrats CTA synthèse/évaluation |
| B16-C2 | `test_b16_c2_*` | Évaluation advisory (déconseillé mais possible) |
| B16-M1 | `test_b16_m1_memory_summary_minimal_structure` | Structure `session_memory` |
| B16-M2 | `test_b16_m2_memory_summary_excludes_verbatim` | Absence verbatim |
| B16-L1 | `test_b16_l1_*` (paramétré) | Enum `learner_display_profile` |
| B16-S1 | `test_b16_s1_ui_state_scene_dispersion_and_priority_branch` | Scène/branche/dispersion |

---

## 3. Tests UI automatisés (Playwright)

**Fichier** : `tests_playwright/e2e/cluster16_learner_interface.spec.ts`

| ID | Scénario |
|----|----------|
| U16-S1 | Posture/mode visible |
| U16-S2 | CTA respectent état disabled |
| U16-S3 | Mémoire gouvernée sans verbatim |
| U16-S4 | Bandeau scène + progression |
| U16-P1 | Mêmes blocs structurels (youth/adult/professional) |
| U16-P2 | Classe CSS profil (`prod-panel--{profile}`) |

**Commande** :

```bash
cd hugo-hugolucia/frontend_1.8
npm run test:smoke -- tests_playwright/e2e/cluster16_learner_interface.spec.ts
```

Prérequis : backend local + bootstrap smoke.

---

## 4. Scénarios manuels par persona

### A1 — youth

- **S16-A1** : début de fil, sélecteur posture, bascule une fois
- **S16-A2** : milieu de fil, posture limitée + message prudence
- **S16-A3** : CTA évaluation advisory (bouton actif + helper)

### A2 — adult

- **S16-A4** : mêmes infos que A1, densité intermédiaire

### A3 — professional

- **S16-A5** : blocs présents, textes plus explicites, moins d’iconographie jeune

---

## 5. Critères de succès

1. Tous les tests backend `test_cluster16_interface_apprenant_backend.py` passent.
2. Tests Playwright U16-S1 à U16-S4 et U16-P1/P2 passent (après bootstrap).
3. Scénarios manuels A1/A2/A3 sans divergence métier, sans P0/verbatim, CTA cohérents avec UIState.

---

## 6. Commande consolidée

```bash
cd hugo_back
python -m pytest apps/hugo/tests/test_cluster16_interface_apprenant_backend.py -q

cd ../hugo-hugolucia/frontend_1.8
npm run test:smoke -- tests_playwright/e2e/cluster16_learner_interface.spec.ts
```

Compte-rendu : `docs-workspace/cluster16_interface_apprenant_resultats_tests.md`

---

## 7. Statut post-cluster 16 (2026-06-18)

| ID | Couverture auto | Reste manuel |
|----|-----------------|--------------|
| B16-P1→P3 posture | `test_cluster16_interface_apprenant_backend.py` | S16-A1, S16-A2 |
| B16-C1/C2 CTA | idem + B16-C2 advisory | S16-A3 |
| B16-M1/M2 mémoire | idem + U16-S3 | — |
| B16-L1 profils | paramétré youth/adult/pro | — |
| U16-S1→S4 scène/CTA/mémoire | Playwright 10/10 PASS | U16-S2b advisory dédié |
| U16-P1/P2 profils | Playwright 6 tests | S16-A4, S16-A5 |

**Verdict tests auto :** SUCCÈS (critères §5.1–5.2). **Scénarios manuels §4 :** ouverts.

---

## 8. Périmètre exclu de ce protocole (2026-06-20)

Le cluster 16 couvre l’**interface apprenant prod** (`/app/session/*`), pas l’**administration conversationnelle** :

| Sujet | Où tester / documenter |
|-------|------------------------|
| Profils conversationnels globaux apprenant | Admin `/admin/conversation/learner/profiles` — `test_learner_conversation_global_profile.py`, Playwright `admin_learner_profiles.spec.ts` |
| Affectation profil au groupe | `/groups-admin/:id` — Playwright `admin_conversation_pipeline.spec.ts` |
| Hubs legacy par posture | `/admin/conversation/learner/:postureCode` |
| Clôture / évaluation org | `/admin/conversation/learner/closing` |

**Distinction terminologique :** le cluster 16 valide le **mode conversationnel** côté apprenant ; la **composition admin du profil global** (4 sous-blocs) relève d’un lot séparé — voir `MINI_SPEC_PROFILS_CONVERSATIONNELS_APPRENANT.md`.
