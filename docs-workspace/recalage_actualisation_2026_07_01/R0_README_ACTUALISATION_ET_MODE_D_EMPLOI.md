# R0 — Actualisation et mode d'emploi

**Date de production :** 1er juillet 2026  
**Périmètre :** workspace `/Users/machin/Desktop/Zone de travail Hugo`  
**Objet :** porte d'entrée du lot de recalage documentaire R0–R7, successeur opérationnel de la baseline historique du 22 juin 2026.

---

## 1. Objectif

Ce lot **n'est pas une réécriture** des documents A0–A7 / B0. Il constitue une **nouvelle génération** ancrée sur :

1. la baseline historique du 22 juin 2026 (photo figée, secondaire par défaut) ;
2. le corpus `docs-workspace/` et les clusters de convergence (juin 2026) ;
3. les **preuves fraîches** disponibles au 1er juillet 2026 : code `hugo_back`, front `frontend_1.8`, tests pytest, Playwright, rapports E2E et campagne du 30 juin.

Règle absolue : **evidence-first** — aucune spec, monographie ou glossaire ne prouve un comportement courant sans artefact récent (code, test, runtime, contrat JSON observé, écran servi).

---

## 2. Hiérarchie de vérité (inchangée dans l'esprit, précisée)

| Rang | Source | Tag documentaire | Rôle |
|------|--------|------------------|------|
| 1 | Code `hugo_back/` | **REL OBSERV** | Backend Python unique du workspace |
| 2 | Tests `hugo_back/` pytest | **REL OBSERV** | Comportement attendu et couvert |
| 3 | Front `hugo-hugolucia/frontend_1.8/` | **REL OBSERV** | Produit montrable, consommation API réelle |
| 4 | Tests Playwright / protocole E2E | **REL OBSERV** / **REL OBSERV PARTIEL** | Parcours UI ; dépend des fixtures et de la stack |
| 5 | Docs workspace récentes (clusters, rapports juin) | **REL OBSERV PARTIEL** | Synthèse auditée ; à recouper avec code |
| 6 | Baseline historique A0–A7, B0, docs 00–10 juin | **BASELINE HISTORIQUE** | Photo 22/06 ; obsolète si non reconfirmée |
| 7 | `spec_canonique_hugo_2_0.md`, specs interface 2.0 | **CIBLE** | Jamais preuve de livraison |
| 8 | Runtime distant `hugoback.encoors.com` | **À VÉRIFIER** | Dernière inspection HTTP authentifiée : **12 juin 2026** (doc 10) ; oracle cluster 11 **sans credentials** (18 juin) |

**Ne jamais fusionner silencieusement** : local `hugo_poc` (postgres dev) ≠ sqlite smoke ≠ Encoors ≠ staging ≠ prod.

---

## 3. Corpus historique désormais secondaire

### 3.1 Baseline Perplexity / photo réel (22 juin 2026)

Dossier : `documentation_photo_reel_2026_06_22/`

| Fichier | Statut au 01/07/2026 |
|---------|----------------------|
| `A0_README_OUVERTURE_ESPACE_PERPLEXITY.md` | **Conservé archive** — méthode toujours valide ; remplacé fonctionnellement par **R0** |
| `A1_SOCLE_REEL_OBSERVE.md` | **Partiellement obsolète** — socle stack/P0 encore valide ; manque clusters 15–16, profils globaux, campagne 30/06 → **R1** |
| `A2_CARTOGRAPHIE_FONCTIONNELLE_EXISTANT.md` | **Partiellement obsolète** — interfaces apprenant/formateur enrichies → **R2** |
| `A3_CARTOGRAPHIE_OBJETS_CONTRATS_ET_VARIABLES.md` | **Conservé archive de référence** — complété par **R4** (contrats observés) |
| `A4_ARCHITECTURE_LOGIQUE_ET_PIPELINES.md` | **Partiellement obsolète** — pipeline core inchangé ; UIState contract, posture, mémoire front → **R3** |
| `A5_ECARTS_MAJEURS_VERS_CIBLE_ET_CHANTIERS_DE_SPEC.md` | **Conservé archive** — écarts runtime partiellement clos (C15/C16) ; tableau actualisé → **R5** |
| `A6_QUESTIONS_OUVERTES_PREUVES_MANQUANTES_ET_A_VERIFIER.md` | **Remplacé** par **R6** |
| `A7_MODE_EMPLOI_POUR_FUTUR_ESPACE_PERPLEXITY.md` | **Remplacé** par **R7** |
| `B0_MONOGRAPHIE_SCIENTIFIQUE_HUGO_REEL_2026_06_22.md` | **Référence monographique historique** — non reconduit à l'identique ; utile pour vocabulaire, pas pour preuve runtime |
| `variables_prompting.md` (docs-workspace) | **REL OBSERV PARTIEL** — variables prompt ; à recouper code à chaque chantier |

### 3.2 Corpus docs-workspace (juin 2026)

Toujours utiles comme **ponts d'audit**, avec date de preuve :

- Méthode : `00_HIERARCHIE_DOCUMENTAIRE.md`, `DOC_METHODO_REFERENCE_CONVERGENCE_HUGO_REVISE.md`
- Réel synthétique juin : `02_ETAT_MOTEUR_REEL.md`, `03_ETAT_PRODUIT_REEL.md`, `05_ECARTS_DOC_CODE_PRODUIT.md`
- Runtime : `07`–`11`, `10_FICHE_RUNTIME_PROD_ENCOORS.md` (inspection **12/06**)
- Matrice convergence : `cluster2_matrice_runtime_vs_cible.md` (**V6, 20/06**)
- Clusters livrés : 15 (interfaces apprenant/formateur), 16 (interface apprenant), 11 (runtime vs Encoors)
- Campagnes récentes : `rapport_test_30juin.md`, `memo_cto_2026-06-30.md`, `e2e-protocol-runtime/RAPPORT_E2E_PROTOCOL.md` (**29/06**)
- Écarts domaine : `ecarts — <domaine>.md` — à croiser avec **R5**

---

## 4. Nouveaux artefacts exploités (preuves dominantes 01/07/2026)

| Artefact | Date | Apport |
|----------|------|--------|
| `hugo_back/apps/hugo/urls.py` | code courant | Inventaire routes API structurantes |
| `hugo_back/config/settings/base.py` | code courant | Flags P0/phase/LLM |
| `hugo_back/apps/hugo/services/ui_state_builder.py` | code courant | Contrat UIState `build_contract_ui_state` |
| `hugo_back/apps/hugo/services/rag_support.py` | code courant | RAG **lexical** actif |
| `hugo_back/apps/hugo/services/hugo_orchestrator.py` | code courant | Pipeline tour ; mémoire attachée au turn, pas aux prompts |
| `cluster15_interfaces_apprenant_formateur_resultats.md` | 18/06 | Posture, mémoire panneau, formateur B1–B3 |
| `cluster16_interface_apprenant_resultats_tests.md` | 18/06 | 15/15 backend + 10/10 Playwright apprenant |
| `cluster2_matrice_runtime_vs_cible.md` V6 | 20/06 | Profils conversationnels globaux |
| `cluster11_verrouillage_runtime_vs_encoors_resultats.md` | 18/06 | Écarts local vs Encoors ; oracle sans auth |
| `contrat_api_memory_summary_v1.md` | 18/06 | Shape memory-summary |
| `e2e-protocol-runtime/RAPPORT_E2E_PROTOCOL.md` | 29/06 | 23 PASS / 0 FAIL / 5 SKIP (stack locale) |
| `rapport_test_30juin.md` | 30/06 | Multi-tenant, formateur, dual DB |
| `memo_cto_2026-06-30.md` | 30/06 | INC-01 à 05 ; INC-02 ACL formateur **ouvert** |
| `frontend_1.8/src/router/index.js` | code courant | Surfaces prod + testeur |
| `frontend_1.8/.env.development` | commité | `VITE_API_URL=https://hugoback.encoors.com` |
| `addendum_front_chats_lots_ABC_2026_07_01.md` | 01/07 | Lots A+B+C shells / `useHugoSessionChat` |
| `addendum_exploration_baseline_B_2026_07_01.md` | 01/07 | Exploration fails, Décision B ui-state, rejeux tests, cartographie pipes |
| `matrice_endpoint_role.md` | 01/07 | Matrice endpoint × rôle (apprenant / tuteur / formateur / admin) |
| `plan_tests_chats_tuteur_formateur.md` (§ Gate Postgres, persona sqlite, INC-02) | 01/07 | OPS tests baseline B |

---

## 5. Nouveaux documents produits (ce lot)

| Fichier | Rôle |
|---------|------|
| **R0** (ce document) | Porte d'entrée, méthode, correspondances |
| **R1** | État réel actualisé — remplace fonctionnellement A1 |
| **R2** | Cartographie fonctionnelle — remplace fonctionnellement A2 |
| **R3** | Architecture et pipelines — remplace fonctionnellement A4 |
| **R4** | Contrats et preuves runtime |
| **R5** | Écarts depuis baseline 22/06/2026 |
| **R6** | Preuves manquantes et plan de recalage — successeur A6 |
| **R7** | Mode d'emploi specs fidèles — successeur A7 |

### 5.1 Addendums post-lot R0–R7 (ne pas fusionner dans R1–R4)

| Fichier | Date | Objet |
|---------|------|--------|
| `addendum_front_chats_lots_ABC_2026_07_01.md` | 01/07 | Front réel lots A+B+C |
| `addendum_exploration_baseline_B_2026_07_01.md` | 01/07 | Exploration, tests, **Décision B** `/ui-state/`, persona sqlite |
| `matrice_endpoint_role.md` | 01/07 | Matrice endpoint × rôle (statuts par rôle) |

---

## 6. Table de correspondance baseline → recalage

| Historique | Nouveau lot | Relation |
|------------|-------------|----------|
| A0 | **R0** | Remplace (méthode + index) |
| A1 | **R1** | Remplace fonctionnellement |
| A2 | **R2** | Remplace fonctionnellement |
| A3 | — | **Conservé archive** ; contrats actualisés dans **R4** |
| A4 | **R3** | Remplace fonctionnellement |
| A5 | **R5** | Complété et actualisé (pas copie) |
| A6 | **R6** | Remplace |
| A7 | **R7** | Remplace |
| B0 | — | **Référence monographique historique** ; non reconduit |
| docs 00–11 | R1–R4 (citations) | Restent ponts ; **secondaires** si non reconfirmés |
| `spec_canonique_hugo_2_0.md` | — | **CIBLE** uniquement ; cité dans R2/R5/R7, jamais comme preuve |

---

## 7. Limites résiduelles (explicites)

| Sujet | Statut | Preuve manquante |
|-------|--------|------------------|
| Parité Encoors vs local post-16/06 | **À VÉRIFIER** | Oracle authentifié (EVAL1, M1, flags) |
| Flags P0/LLM sur Encoors | **À VÉRIFIER** | Variables env prod non exposées |
| SSE distant en conditions réelles | **À VÉRIFIER** | Test stream authentifié depuis `hugo.encoors.com` |
| Synthèse/évaluation bout-en-bout prod | **À VÉRIFIER** | E2E scaffold SKIP lots 9 ; pas de preuve LLM distant |
| RLS Postgres prod | **À VÉRIFIER** | `audit_rls_prod_template.sql` non exécuté ici |
| ACL formateur dashboard learners | **ÉCART CONFIRMÉ ouvert** | Décision CTO INC-02 (30/06) |
| Injection mémoire dans prompts LLM | **REL OBSERV** (absent) | Confirmé par absence dans services prompt |
| RAG vectoriel | **REL OBSERV** (inactif) | `test_preprod_garde_fou.py` lexical only |

---

## 8. Ordre de lecture recommandé

### Pour comprendre « Hugo aujourd'hui » (réel)

1. **R0** (ce fichier) → **R1** (socle) → **R4** (contrats/preuves)
2. Selon le domaine : **R2** (fonctionnel) ou **R3** (pipeline)
3. **R5** (écarts vs juin) puis **R6** (trous de preuve)

### Pour rédiger une spec fidèle

1. **R7** (checklist anti-hallucination)
2. **R4** + code `hugo_back` + test associé
3. Fichier `ecarts — <domaine>.md` + **R5**

### Pour une démo produit

1. **R1** § baselines A/B
2. `07_RUNTIME_DEMO_REFERENCE.md` + `11_FICHE_COMPTES_ET_DONNEES_DEMO.md`
3. **R6** § Encoors avant de présenter le distant comme preuve du local

---

## 9. Tags utilisés dans ce lot

| Tag | Signification |
|-----|---------------|
| **REL OBSERV** | Confirmé par code, test ou runtime inspecté récemment |
| **REL OBSERV PARTIEL** | Confirmé sur un sous-ensemble (ex. local seul, un rôle) |
| **CART CONFIRM** | Cartographie ou écart documenté et recoupé |
| **À VÉRIFIER** | Dépend d'un environnement ou d'une preuve non acquise |
| **CIBLE** | Hugo 2.0 / spec ; non prouvé livré |
| **HYPOTHÈSE** | Recommandation non validée par preuve |
| **BASELINE HISTORIQUE** | Document ou constat du 22/06 ou avant, non revalidé |

---

*Prochaine sortie utile après lecture de ce lot : ouvrir **R1** pour le socle runtime, ou **R7** pour cadrer une session de spec.*
