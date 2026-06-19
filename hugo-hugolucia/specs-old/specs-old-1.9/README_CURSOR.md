# Hugo — Cursor Docs : vue d'ensemble et calendrier

## Contexte

Ces 7 fichiers Cursor couvrent les 4 prochaines vagues d'évolution de Hugo,
depuis les fondations d'état jusqu'à l'observabilité cohorte.
Ils sont conçus pour être implémentés **en séquence stricte**, chaque lot validant
sa checklist avant que le suivant commence.

---

## Principe de sécurité commun à tous les lots

1. **Aucun champ P0 modifié.** `turnstate_v17.py` et `decision_engine_v17.py` ne sont jamais modifiés directement.
2. **Source de vérité unique des enums.** `ConversationPosture`, `SessionMaturityLevel`, `KnowledgeItemStatus` sont définis **uniquement** dans `conversation_profile.py` et importés partout ailleurs.
3. **UIState propre.** `UIState` ne doit jamais exposer un champ P0 brut (vérifié par NR-07).
4. **RLS orthographe canonique.** `organisation_id` (avec s, SPEC v1.5 section 13) dans tous les modèles, migrations et helpers.
5. **Consolidation et analytics post-conversation uniquement.** Jamais pendant un tour.
6. **Critères provisoires non auto-upgradés.** `DERIVED_PROVISIONAL` → `VALIDATED_TRAINER` requiert une action humaine explicite.
7. Toute reconstruction d'un objet dataclass depuis un JSONB doit passer par une fonction explicite de désérialisation ; ne jamais utiliser directement `ConversationProgress(**raw)` si des enums ou objets imbriqués sont présents.
8. Toute enum stockée en base Django est persistée sous forme de string `.value`, puis reconstruite explicitement en code métier.

---

## Tableau des lots

| Lot | Nom | Durée | Risque | Bloquant | Fichiers Cursor |
|-----|-----|-------|--------|----------|-----------------|
| **0** | Contrats et fondations | 2–3 j | Très faible | Oui (tous les suivants) | `LOT0_contrats_fondations.md` |
| **1** | Moteur de progression conversationnelle | 3–4 j | Faible | Oui (LOT 2, 3) | `LOT1_progression_conversationnelle.md` |
| **2** | Adaptateur UI 1.8 | 2–3 j | Faible | Non | `LOT2_adaptateur_ui.md` |
| **3** | Modes de conduite de séance | 4–5 j | Modéré | Non | `LOT3_modes_postures.md` |
| **4** | Mémoire thématique inter-session | 4–5 j | Modéré | Non | `LOT4_memoire_inter_session.md` |
| **5** | Base de connaissances formateur | 5–7 j | Modéré | Non | `LOT5_base_connaissances_formateur.md` |
| **6** | Observabilité et métriques cohorte | 3–4 j | Faible | Non | `LOT6_observabilite_cohorte.md` |

**Total estimé : 23–31 jours ouvrés.**

---

## Séquence recommandée

```
LOT 0 ──► LOT 1 ──► LOT 2 ──► LOT 3
                              │
                              ├──► LOT 4 (mémoire)
                              ├──► LOT 5 (formateur)
                              └──► LOT 6 (métriques — peut démarrer dès LOT 1)
```

LOT 6 peut commencer dès que LOT 1 est vert (les signaux clés viennent de `ConversationProgress`).
LOT 4 et LOT 5 peuvent tourner en parallèle après LOT 3.

---

## Checkpoints inter-lots (règle stricte)

Avant de passer au lot suivant, vérifier :

| Condition | Responsable |
|-----------|-------------|
| Les **9 tests NR** du LOT 0 passent sur main | Dev |
| Les tests du lot en cours passent | Dev |
| Aucun champ de `P0_CORE_FIELDS` dans UIState (NR-07) | Dev |
| `organisation_id` (avec s) dans la migration | Dev |
| Aucune modification dans `decision_engine_v17.py` | CTO review |
| Les enums sont importés depuis `conversation_profile.py` (NR-09) | Dev |

---

## Fichiers P0 en lecture seule (ne jamais modifier)

```
backend/apps/hugo/domain/turnstate_v17.py
backend/apps/hugo/services/decision_engine_v17.py
backend/apps/hugo/services/hugo_orchestrator.py   ← patches additifs uniquement
backend/apps/hugo/services/prompt_renderer.py      ← patches additifs uniquement
```

---

## Nouveaux fichiers créés (par lot)

### LOT 0
- `backend/apps/hugo/domain/conversation_profile.py`
- `backend/apps/hugo/domain/reason_codes.py`
- `backend/apps/hugo/domain/tutor_profiles.py` (stub)
- `backend/apps/hugo/tests/test_p0_non_regression.py`
- Migration : `conversation_progress` sur `HugoSession`

### LOT 1
- `backend/apps/hugo/services/conversation_progress_calculator.py`
- `backend/apps/hugo/tests/test_conversation_progress.py`
- Patch orchestrateur (additif)
- Patch endpoints
- Note d'implémentation LOT 1 :
- `ConversationProgress` stocké en JSONB doit être reconstruit via `deserialize_conversation_progress()`.
- Les endpoints `/progress` et `/ui-state` ne doivent jamais parser directement `raw` sans recast des enums et des branches.

### LOT 2
- `frontend/src/hugo/progressionLabels.js`
- `frontend/src/hugo/engagementUiModel.js` (remplacement)
- `frontend/src/hugo/components/HugoProgressPanel.jsx`
- Endpoints `/request-synthesis` et `/request-evaluation`

### LOT 3
- `backend/apps/hugo/services/posture_selector.py`
- `backend/apps/hugo/domain/tutor_profiles.py` (remplace stub LOT 0)
- `backend/apps/hugo/domain/posture_transitions.py`
- `backend/apps/hugo/services/synthesis_service.py`
- `backend/apps/hugo/tests/test_posture_modes.py`
- Endpoint `/set-posture`
- Patches additifs orchestrateur + prompt_renderer

### LOT 4
- `backend/apps/hugo/models.py` : `LearnerThemeMemory`
- `backend/apps/hugo/services/memory_consolidator.py`
- `backend/apps/hugo/tests/test_memory_consolidation.py`
- Migration + endpoint `/memory-summary`
- Note d'implémentation LOT 4 :
- `knowledge_status` est stocké en base comme string canonique (`declared`, `derived_provisional`, `validated_trainer`).
- La consolidation ne modifie jamais automatiquement un `derived_provisional` en `validated_trainer`.

### LOT 5
- `backend/apps/hugo/models.py` : `TrainerKnowledgeItem`
- `backend/apps/hugo/services/document_ingestor.py`
- `backend/apps/hugo/views/trainer.py`
- Migration

### LOT 6
- `backend/apps/hugo/models.py` : `ConversationQualitySignal`
- `backend/apps/hugo/services/quality_tracker.py`
- `backend/apps/hugo/analytics/cohort_dashboard.py`
- `backend/apps/hugo/views/analytics.py`
- `backend/apps/hugo/tests/test_quality_signals.py`

---

## Ce que ces docs ne couvrent pas (hors périmètre)

- Interface formateur de suivi et co-construction (post LOT 5)
- Mémoire formation complète multi-cohortes (post LOT 4 V2)
- Agents dynamiques recomposables (après validation des 3 modes LOT 3)
- Intégration Julia et autres acteurs de l'écosystème
- RAG complet (dépend de l'architecture bibliothèque active — lot ultérieur)
