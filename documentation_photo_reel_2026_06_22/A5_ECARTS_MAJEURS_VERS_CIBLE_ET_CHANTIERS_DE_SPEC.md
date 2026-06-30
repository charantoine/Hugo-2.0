# A5 — Écarts majeurs vers cible et chantiers de spec

**Date :** 22 juin 2026  
**Orientation :** futur espace Perplexity — spécification des prochaines fonctions.

---

## 1. Écarts majeurs réel ↔ cible (synthèse)

| # | Écart | Niveau | Domaine |
|---|-------|--------|---------|
| 1 | Injection `LearnerThemeMemory` au tour | **ÉCART CONFIRMÉ** | 20 |
| 2 | Injection `session_memory` dans prompt LLM | **ÉCART CONFIRMÉ** (lot courant) | 20 |
| 3 | RAG vectoriel / embeddings indexation | **ÉCART CONFIRMÉ** | 30 |
| 4 | Double stack P0 legacy/v17 non arbitrée | **ÉCART CONFIRMÉ** | 10 |
| 5 | `EvaluationTrace` unifié vs objets dispersés | **PARTIEL** | 70 |
| 6 | Payload `generate-trace` minimal | **ÉCART CONFIRMÉ** | 70 |
| 7 | Matrice bascule posture SW-xx | **CIBLE** | 31 |
| 8 | Intercalaires v1 | **CIBLE** (aucun réel) | 120 |
| 9 | Catalogue signaux qualité canonique | **CIBLE** | 80 |
| 10 | Parité Encoors vs local récent | **A_VERIFIER** | transversal |
| 11 | RLS Postgres effectif prod | **A_VERIFIER** | 90 |
| 12 | Workspace monorepo cassé (`backend/` vide) | **ÉCART CONFIRMÉ** | infra |
| 13 | Hiérarchie contexte 2.0 non contractualisée | **PARTIEL** | 30 |
| 14 | CTA libellés × posture | **CIBLE** | 10 |
| 15 | Choix profil affichage par formateur (IFT-042) | **CIBLE** | 110 |

---

## 2. Éléments déjà solides (ne pas sur-spécifier)

- Pipeline P0 legacy testé et calibré.
- UIState backend-driven + CTA synthèse/évaluation.
- Parcours `/app` complet (chat, progression, actions terminales).
- TutorConductProfiles + resolver.
- Mémoire intra-session API + panneau.
- RAG lexical avec citations.
- Multi-tenant modèle + middleware + tests.
- Confidentialité tuteur verbatim (B1-01).
- Profils globaux apprenant (juin 2026).
- Exports CSV/JSON + EvidenceBundle (local testé).

---

## 3. Éléments partiels (priorité spec)

| Élément | État | Spec probable |
|---------|------|---------------|
| Sélecteur posture prod | PARTIEL+ local | Matrice verrous + messages refus |
| 3 grammaires `learner_display_profile` | PARTIEL+ | IFT-042 choix cohorte |
| Workflow formateur | PARTIEL+ | Script F2–F4 bout-en-bout |
| Surface tuteur | PARTIEL | Checklist B1 parcours complet |
| Trace riche / pivot | PARTIEL | Contrat `trace_rich_v1` critères |
| D9bis observabilité | PARTIEL backend | Frontière export technique vs métier |
| Policies évaluation groupe | PARTIEL | UI admin dédiée |
| memory-summary schéma | PARTIEL | D2-M04 plat vs nested |

---

## 4. Zones ambiguës

- `PersistentObjects` : champ ui-state vs objet doctrinal.
- `build_ui_state` vs `build_contract_ui_state` : quel contrat canonique ?
- Runtime référence officiel : baseline A vs B.
- MEMO CTO 1.9 : 5/10 écarts obsolètes localement — à archiver ou réécrire.
- Équivalence `hugo-main` / `hugo-hugolucia` git.

---

## 5. Points ouverts (décisions CTO)

1. **Runtime de référence** : Encoors vs local pour « Hugo aujourd'hui ».
2. **P0 prod** : rester legacy ou activer v17/classifieur.
3. **Mémoire lot 2** : injecter session_memory dans prompt ? réouvrir LTM ?
4. **Monorepo** : réintégrer `hugo_back` ou garder 3 dossiers.
5. **RAG** : renforcer lexical ou investir vectoriel (couronne).
6. **DEBUG prod** : `DEBUG=True` observé Encoors — correction infra.

---

## 6. Contrats minimaux probablement à spécifier

| Contrat | Contenu attendu | Priorité |
|---------|-----------------|----------|
| UIState v2 stabilisé | Un seul builder, champs normés, versioning | Haute |
| Mémoire intra prompt | Schéma injection `session_memory` dans vars_dict | Haute (si lot 2) |
| Tableau posture → RAG → maturité → CTA | D2-M02 | Haute |
| Matrice rôle × visibilité | D2-M07 | Haute |
| memory-summary v1 | Aligner plat/nested | Moyenne |
| DocumentContextBundle | Hiérarchie contexte RAG | Moyenne |
| EvaluationTrace pivot | Mapping export unifié | Moyenne |
| Catalogue signaux qualité | Enum + producteurs | Basse (couronne) |
| Intercalaire v1 | Producteur post-tour, effet nul P0 | Basse (couronne) |

---

## 7. Chantiers recommandés par priorité

### P0 — Bloquants gouvernance / risque

1. Trancher runtime référence + fiche version Encoors.
2. Archiver ou réécrire MEMO CTO obsolète.
3. Corriger doc deploy (`backend/` vide).
4. Décision DEBUG/CORS prod (doc 10).

### P1 — Convergence cœur (Vagues 1–3 plan CTO)

1. D2-M02 : tableau posture/RAG/maturité/CTA.
2. D2-M07 : matrice confidentialité rôles (compléter pytest existant).
3. D2-M10 : documenter flags v17 dans fiche runtime.
4. D2-M12 : frontière ORGADMIN/SUPERADMIN exports.
5. Finaliser contrat UIState unique (fusion builders).
6. Enrichir `generate-trace` ou assumer minimal + pivot.

### P2 — Surfaces encadrants

1. D2-M09 : checklist parcours tuteur B1 bout-en-bout.
2. Workflow formateur F2–F4 spec exécutable.
3. IFT-042 : choix profil affichage formateur.
4. UI policies évaluation par groupe.

### P3 — Couronne (post-cœur)

1. RAG vectoriel si validé ROI.
2. D9bis dashboards produit.
3. Intercalaires v1.
4. Injection mémoire inter-sessions (hors lot courant actuel).

---

## 8. Risques documentaires à éviter

| Risque | Mitigation |
|--------|------------|
| Lire spec 2.0 comme preuve livrée | Tag CIBLE systématique |
| Glossaire = implémentation | Pont vocabulaire uniquement |
| Front = vérité moteur | Toujours partir `hugo_back` |
| Démo Encoors = code local | Baseline nommée + A_VERIFIER |
| MEMO CTO mai-juin | Croiser 05 + cluster 2 |
| Spec 1.6.2 / audits mai 2026 | ARCHIVE — utiliser 02/03 |
| Verbatim comme mémoire | Doctrine lot 20 |
| Certification autonome évaluation | Rappel validation humaine |

---

## 9. Backlog documentaire cluster 2 (extrait actif)

| ID | Statut juin 2026 | Action spec |
|----|-------------------|-------------|
| D2-M01 conversation_mode | Livré C4/C16 | Maintenir |
| D2-M02 tableau posture/CTA | Ouvert | **Spec prioritaire** |
| D2-M03 set-posture | Partiel livré | Compléter verrous |
| D2-M04 memory-summary | Ouvert | Contrat schéma |
| D2-M05 EvaluationTrace | Livré doc pivot | Implémenter enrichissement |
| D2-M07 matrice rôles | Partiel 10 tests | Étendre |
| D2-M08 profils affichage | Partiel+ C16 | IFT-042 |
| D2-M10 flag v17 doc | Ouvert | Fiche flags prod |
| D2-M11 taxonomie exports | Partiel C7 | Compléter E1–E6 |
| D2-M12 ORGADMIN/superadmin | Ouvert | Spec frontière |

Source : `cluster2_matrice_runtime_vs_cible.md` §14.

---

*Comparaison cible via spec_canonique_hugo_2_0.md et compléments — jamais présentée comme livrée.*
