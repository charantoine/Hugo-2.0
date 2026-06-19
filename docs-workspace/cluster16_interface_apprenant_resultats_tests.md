# Cluster 16 — Résultats campagne de tests

Date : 2026-06-18  
Environnement : `local`  
Protocole : [`cluster16_protocole_tests_interface_apprenant_v1.md`](cluster16_protocole_tests_interface_apprenant_v1.md)

---

## Synthèse

| Campagne | Résultat | Détail |
|----------|----------|--------|
| Backend B16-* | **15/15 PASS** | `test_cluster16_interface_apprenant_backend.py` |
| Playwright U16-* | **10/10 PASS** | `cluster16_learner_interface.spec.ts` |
| Scénarios manuels A1/A2/A3 (S16-A1→A5) | **Non exécutés** | Checklist §4 protocole C16 |

**Verdict cluster 16 (tests auto)** : **SUCCÈS** selon critères §5.1 et §5.2 du protocole.  
**Doc alignée :** `rapport_mise_a_jour_doc_post_cluster16_2026-06-18.md`, matrice V5.

---

## Backend — détail

Commande :

```bash
cd hugo_back && python -m pytest apps/hugo/tests/test_cluster16_interface_apprenant_backend.py -q
```

| ID protocole | Test | Statut |
|--------------|------|--------|
| B16-P1 | `test_b16_p1_ui_state_conversation_mode_present_without_p0` | PASS |
| B16-P1 | `test_b16_p1_allowed_posture_transitions_shape` | PASS |
| B16-P2 | `test_b16_p2_set_posture_valid_updates_ui_state` | PASS |
| B16-P3 | `test_b16_p3_set_posture_refused_keeps_ui_state_coherent` | PASS |
| B16-P3 | `test_b16_p3_switch_locked_reason_when_no_transitions_allowed` | PASS |
| B16-C1 | `test_b16_c1_cta_contracts_main_fields` | PASS |
| B16-C2 | `test_b16_c2_evaluation_advisory_eligible_with_helper` | PASS |
| B16-C2 | `test_b16_c2_evaluation_not_advisory_when_fully_eligible` | PASS |
| B16-M1 | `test_b16_m1_memory_summary_minimal_structure` | PASS |
| B16-M2 | `test_b16_m2_memory_summary_excludes_verbatim` | PASS |
| B16-L1 | `test_b16_l1_learner_display_profile_enum_in_ui_state[youth/adult/professional]` | PASS ×3 |
| B16-S1 | `test_b16_s1_ui_state_scene_dispersion_and_priority_branch` | PASS |
| — | `test_b16_unit_conversation_mode_lists_non_current_postures` | PASS |

Durée observée : ~9–10 s.

---

## Playwright — détail

Prérequis exécutés :

```bash
cd hugo_back && python manage.py bootstrap_smoke_playwright
```

Sessions générées (`smoke-fixtures.json` → `cluster16_sessions`) :

- youth : `16d95c02-e15e-4e83-876c-5259fc5b385f`
- adult : `4527fd37-795e-4d61-80a2-70ac2b913948`
- professional : `f4b69d8c-cef0-4418-ae61-059a1d191b2c`

Commande :

```bash
cd hugo-hugolucia/frontend_1.8
npm run test:smoke -- tests_playwright/e2e/cluster16_learner_interface.spec.ts
```

| ID protocole | Statut |
|--------------|--------|
| U16-S1 | PASS |
| U16-S2 | PASS |
| U16-S3 | PASS (oracle limité au panneau mémoire, pas au fil chat) |
| U16-S4 | PASS |
| U16-P1 youth/adult/professional | PASS ×3 |
| U16-P2 youth/adult/professional | PASS ×3 |

Durée observée : ~13 s.

---

## Notes et écarts

- **U16-S3** : le verbatim smoke reste visible dans le fil de conversation (message apprenant) ; le panneau `LearnerMemoryPanel` n’expose pas le marqueur — conforme au contrat mémoire gouvernée.
- **U16-S2 advisory explicite** : non couvert en E2E automatique (nécessite session en état `cta_evaluation.ui.advisory=true` visible) — couvert côté backend B16-C2 ; scénario manuel **S16-A3** recommandé.
- **Verrou posture séance avancée** : B16-P3 couvre refus API + `switch_locked_reason` unitaire ; scénario manuel **S16-A2** pour validation UX ressenti.
- **Encoors / prod** : **A_VÉRIFIER** — campagne exécutée en local uniquement.

---

## Prochaine sortie utile

1. Exécuter checklist manuelle §4 (S16-A1 à S16-A5) sur les trois sessions bootstrap.
2. Ajouter un test Playwright dédié **U16-S2b** avec session orange + `advisory=true` (fixture backend dédiée).
3. Mettre à jour `cluster2_matrice_runtime_vs_cible.md` domaine 110 si validation manuelle OK.
