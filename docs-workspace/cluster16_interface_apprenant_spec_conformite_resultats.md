# Cluster 16 — Interface apprenant conforme spec 2.0

Date : 2026-06-18  
Périmètre : polish UX apprenant (backend-first, pas de nouvelle navigation).

---

## Sources mobilisées

- `specs interface 2.0.md` (structure conversation, profils, CTA, mémoire)
- `10_runtime_p0_progression_uistate_note_lot_courant_cta_synthese_evaluation.md`
- `20_memoire_gouvernee_note_lot_courant_memoire_intra_conversation.md`
- `cluster2_matrice_runtime_vs_cible.md` (domaines 10, 20, 110)
- Code : `ProdLearnerWorkspace.vue`, `PostureSelector.vue`, `LearnerMemoryPanel.vue`, `HugoProgressPanel.vue`, `ui_state_builder.py`, `cta_ui_state.py`

---

## 1. Matrice champs UIState → front

| Champ backend | Composant front | Effet UI actuel (post C16) | Effet UI cible spec |
|---------------|-----------------|---------------------------|---------------------|
| `conversation_mode.code/label` | `PostureSelector`, `engagementUiModel` | Badge + description posture | **OK** |
| `conversation_mode.can_switch` | `PostureSelector` | Select désactivé + message si false | **OK** |
| `conversation_mode.allowed_posture_transitions` | `PostureSelector` | Options filtrées par `allowed` | **OK** |
| `conversation_mode.switch_locked_reason` | `PostureSelector` | Message prudence si verrouillé | **OK** |
| `conversation_mode.switch_warning` | `PostureSelector` | Alerte jaune AFEST | **OK** |
| `learner_display_profile` | classes CSS `prod-panel--*` | Typo/densité différenciée, mêmes blocs | **OK** |
| `scene_label`, `scene_progress` | `LearnerSceneContextBar`, `HugoProgressPanel` | Phase + rail progression | **OK** |
| `active_quest_label` | `LearnerSceneContextBar`, `HugoProgressPanel` | Objectif actif | **OK** |
| `maturity_color` | `LearnerSceneContextBar`, `HugoProgressPanel` | Badge 3 états + tooltip | **OK** |
| `dispersion_risk` | `LearnerSceneContextBar` | Alerte simple si true | **OK** |
| `priority_branch_label` | `LearnerSceneContextBar` | Fil en cours | **OK** |
| `cta_synthesis.*` | `HugoProgressPanel` via `engagementUiModel` | Bouton + helper | **OK** (inchangé) |
| `cta_evaluation.ui.advisory` | `HugoProgressPanel` | Bouton actif + icône + helper | **OK** |
| `session_memory` (endpoint séparé) | `LearnerMemoryPanel` | Sections gouvernées + Voir plus | **OK** |
| `theme_memories` | — | Ignoré apprenant | **OK** |

---

## 2. Fichiers modifiés

### Backend (`hugo_back`)

| Fichier | Changement |
|---------|------------|
| `domain/conversation_profile.py` | `dispersion_risk`, `priority_branch_label` sur `UIState` |
| `services/ui_state_builder.py` | `allowed_posture_transitions`, `switch_locked_reason`, branche prioritaire |
| `services/cta_ui_state.py` | `ui.advisory` + helper_text défaut évaluation déconseillée |
| `tests/test_cluster16_interface_apprenant_backend.py` | **nouveau** — 6 tests |
| `tests/test_cluster4_surface_contracts.py` | clés `conversation_mode` étendues |
| `tests/test_cluster15_interfaces_apprenant.py` | idem + `advisory` dans CTA UI |

### Front (`hugo-hugolucia/frontend_1.8`)

| Fichier | Changement |
|---------|------------|
| `PostureSelector.vue` | Transitions backend, sélecteur toujours visible, messages refus |
| `LearnerSceneContextBar.vue` | **nouveau** — bandeau phase/objectif/maturité/dispersion |
| `LearnerMemoryPanel.vue` | Vouvoiement, troncature `ExpandableText`, micro-copy intra-séance |
| `ExpandableText.vue` | **nouveau** |
| `HugoProgressPanel.vue` | Rendu CTA advisory |
| `ProdLearnerWorkspace.vue` | Intégration bandeau scène |
| `utils/engagementUiModel.js` | Transitions posture, advisory, dispersion, branche |
| `utils/displayProfilePresets.js` | Même contenu visible sur youth/adult/professional |
| `utils/displayProfileCopy.js` | Vouvoiement profil youth |
| `style.css` | Styles profils, scène, advisory, expandable |
| `tests_playwright/e2e/cluster16_learner_interface.spec.ts` | **squelette** E2E |

---

## 3. Tests

**Backend** (exécutés localement) :

```bash
cd hugo_back && python -m pytest apps/hugo/tests/test_cluster16_interface_apprenant_backend.py -v
```

**Front** : squelette Playwright `cluster16_learner_interface.spec.ts` (skip jusqu’à fixtures dédiées).

---

## 4. Points PARTIELS / CIBLE

| Sujet | Statut |
|-------|--------|
| Posture verrouillée par phase/tours | **PARTIEL** — `can_switch` suit les transitions posture/maturité ; pas encore de verrou explicite « séance avancée » hors transitions |
| Surface admin profil cohorte | **CIBLE** — non implémentée (hors cluster, suggestion ORGADMIN) |
| E2E Playwright cluster 16 | **PARTIEL** — squelette seulement |
| Encoors / prod | **A_VÉRIFIER** |

---

## 5. Synthèse conformité spec 2.0

L’interface apprenant consomme désormais explicitement les champs UIState pour la posture (`allowed_posture_transitions`, messages de refus), la scène (bandeau phase/objectif/maturité/dispersion), les CTA (état `advisory` pour « déconseillé mais possible »), et la mémoire intra-conversation (sections gouvernées, troncature, sans verbatim). Les trois profils d’affichage exposent les mêmes informations avec des variations de densité et de style uniquement. La doctrine backend-first est respectée : aucune logique métier de progression, d’éligibilité ou de transition n’est recalculée côté front.
