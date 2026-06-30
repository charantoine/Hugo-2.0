# Rapport d'exécution — protocole E2E Playwright Hugo

**Date :** 2026-06-29  
**Front :** http://localhost:5173  
**API :** http://127.0.0.1:8000  
**Résultats bruts :** [`playwright-results.json`](playwright-results.json)  
**Préconditions :** [`protocol-preconditions.json`](protocol-preconditions.json)

---

## Synthèse

| PASS | FAIL | SKIP |
|------|------|------|
| 23 | 0 | 5 |

---

## Préconditions (OK)


- Organisations : 6 (2+ requis pour switch : oui)
- Groupes org démo : 7
- bac pro melec : oui
- Rôles démo : {"SUPERADMIN":["demo.superadmin"],"ORGADMIN":[],"LEARNER":["apprenant_melec_3","apprenant_melec_2","apprenant_melec_1"],"TUTOR":["tuteur_melec_3","tuteur_melec_2","tuteur_melec_1"],"TRAINER":["formateur_melec_test","demo.formateur"]}
- Smoke fixtures : oui



---

## Résultats par lot

| Lot | Test | Statut | Classification |
|-----|------|--------|----------------|
| LOT 0 | L0-preconditions probe API + auth | passed | PASS |
| LOT 0 | L0-smoke login + dashboard + no fatal console | passed | PASS |
| LOT 0 | L0-smoke app learner route loads for smoke user if fixtures present | passed | PASS |
| LOT 1 | L1-banner /dashboard | passed | PASS |
| LOT 1 | L1-banner /users | passed | PASS |
| LOT 1 | L1-banner /groups-admin | passed | PASS |
| LOT 1 | L1-banner /groups-admin/29e5cdb9-de89-49b3-a36e-53b4b9bbbc50 | passed | PASS |
| LOT 1 | L1-banner /admin/onboarding | passed | PASS |
| LOT 1 | L1-org-switch changes group list (no silent leak) | passed | PASS |
| LOT 2 | L2-scope org + groupe à configurer + pas de référence démo | passed | PASS |
| LOT 2 | L2-query groupId pré-sélectionne le groupe | passed | PASS |
| LOT 2 | L2-changer groupe recalcule étape Groupe | passed | PASS |
| LOT 2 | L2-CTA créer groupe -> /groups-admin | passed | PASS |
| LOT 3 | L3-raccourci démo distinct du wizard | passed | PASS |
| LOT 4 | L4-users list wired to GET /users/ | passed | PASS |
| LOT 4 | L4-groups-admin list wired to GET /groups/ | passed | PASS |
| LOT 4 | L4-create group persists in list | passed | PASS |
| LOT 4 | L4-group detail members section loads | passed | PASS |
| LOT 5 | L5-tutor sees only linked learners | skipped | SKIP (données / scaffold) |
| LOT 6 | L6-profile assign persists on group | skipped | SKIP (données / scaffold) |
| LOT 7 | L7-RNCP38878 attached and library visible | skipped | SKIP (données / scaffold) |
| LOT 9 | L9-request-synthesis wired | skipped | SKIP (données / scaffold) |
| LOT 11 | L11-trainer knowledge route | skipped | SKIP (données / scaffold) |
| LOT 8 | L8-session ui-state wired | passed | PASS |
| LOT 8 | L8-memory-summary wired when panel open | passed | PASS |
| LOT 10 | L10-tutor timeline sans verbatim | passed | PASS |
| LOT 12 | L12-learner app sans debug P0 | passed | PASS |
| LOT 12 | L12-dashboard testeur séparé | passed | PASS |

---

## Écarts classés

| Type | Détail |
|------|--------|
| Bug confirmé | — |
| Scaffold / données manquantes | Lots 5–7, 9, 11 (skip volontaire) + tests skip fixtures |
| Fonctionnalité non couverte auto | Synthèse/évaluation bout-en-bout sans session préparée |

---

## Arborescence suite

```
tests_playwright/
  helpers.ts, helpers/demo-env.ts, helpers/protocol.ts
  e2e/protocol/
    lot00-preconditions-smoke.spec.ts
    lot01-org-active.spec.ts
    lot02-wizard.spec.ts
    lot03-dashboard-demo.spec.ts
    lot04-groups-users.spec.ts
    lot05-07-09-11-scaffold.spec.ts
    lot08-12-learner-tutor.spec.ts
```

Commande : `npm run test:protocol`
