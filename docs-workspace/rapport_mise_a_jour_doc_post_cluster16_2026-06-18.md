# Rapport — mise à jour documentaire post-cluster 16

**Date :** 2026-06-18  
**Périmètre :** convergence Hugo 2.0 — domaines 10, 20, 30, 31, 40, 50, 60, 70, 80, 90, 100, 110, 120  
**Preuves :** cluster 16 (15 backend + 10 Playwright PASS), `cluster16_interface_apprenant_resultats_tests.md`, `cluster16_interface_apprenant_spec_conformite_resultats.md`

---

## 1. Synthèse

Le cluster 16 a livré le **polish interface apprenant** conforme spec 2.0 (posture, profils, mémoire, CTA advisory, scène/branche/dispersion) sans modifier la doctrine backend-first. La passe documentaire met à jour la matrice V5 et les bandeaux d’écarts avec des **modifications minimales** (statuts, justifications, références tests).

**Verdict documentaire :** alignement renforcé sur **10, 20, 31, 70, 110** ; domaines **30, 40, 50, 60, 80, 90, 100, 120** marqués « pas d’impact direct C16 » avec statut inchangé.

---

## 2. Fichiers modifiés

| Fichier | Nature des changements |
|---------|------------------------|
| `cluster2_matrice_runtime_vs_cible.md` | V4 → **V5** ; synthèse §0 ; lignes 10/20/31/70/110 ; §18 cluster 16 |
| `ecarts —10_runtime_p0_progression_uistate.md` | Bandeau C16 : transitions, dispersion, advisory |
| `ecarts — 20_memoire_gouvernee.md` | PARTIEL → **PARTIEL+** panneau mémoire |
| `ecarts — 30_referentiel_documentaire_rag.md` | Bandeau : pas d’impact C16 |
| `ecarts — 31_front_apprenant_postures_et_bascule.md` | PARTIEL+ ; tableau fin cluster 12 |
| `ecarts — 40…60, 80, 90, 100, 120` | Bandeaux : pas d’impact ou note transversale |
| `ecarts — 70_evaluation_traces_preuves.md` | CTA `ui.advisory` |
| `ecarts — 110_interfaces_formateur_tuteur.md` | Apprenant PARTIEL+ ; IFT-026, IFT-041 |
| `cluster2_oracles_test_par_persona.md` | A1-08 OK ; A2-05/A3-04 PARTIEL ; §21 C16 |
| `protocole_tests_interfaces_apprenant_formateur_v1.md` | §7 statut post-C16 |
| `cluster16_protocole_tests_interface_apprenant_v1.md` | §7 statut post-C16 |
| `spec_canonique_hugo_2_0.md` | Note statut runtime → matrice V5 |
| `specs interface 2.0.md` | Bandeau PARTIEL+ clusters 15–16 |

**Non modifiés (inchangés ou déjà à jour) :** `DOC_METHODO_*`, notes lot 10/20, rapports cluster 15, `rapport_mise_a_jour_doc_post_tests_2026-06-18.md` (conservé comme référence C15).

---

## 3. Changements par domaine

| Domaine | Avant C16 (doc) | Après C16 | Preuve |
|---------|-----------------|-----------|--------|
| **10** | UIState + CTA IMPLÉMENTÉ ; posture UI PARTIEL | + `allowed_posture_transitions`, `dispersion_risk`, `ui.advisory` ; posture **PARTIEL+** | B16-P*, B16-S1 |
| **20** | API IMPLÉMENTÉ ; panneau PARTIEL | Panneau **PARTIEL+** (ExpandableText, vouvoiement) | B16-M*, U16-S3 |
| **30** | Inchangé | Inchangé | — |
| **31** | Posture/profils PARTIEL | **PARTIEL+** ; bandeau scène ; E2E profils | U16-S/P |
| **40–60** | C15 PARTIEL+ formateur | Inchangé (note bandeau) | — |
| **70** | CTA IMPLÉMENTÉ | + état advisory documenté | B16-C2 |
| **80–100** | Statuts post-C15 | Inchangé (note bandeau) | — |
| **110** | Apprenant PARTIEL+ C15 | Apprenant **PARTIEL+ C16** ; formateur/tuteur inchangés | IFT-026/041 |
| **120** | CIBLE | CIBLE inchangé | — |

---

## 4. Écarts et backlogs restants (vague 2.1+)

| ID / thème | Domaine | Statut | Action suivante |
|------------|---------|--------|-----------------|
| Verrou posture phase/tours | 10/31 | **PARTIEL** | Champ backend explicite ou règle séance avancée |
| Matrice SW-xx bascule | 31 | **CIBLE** | Contrat annexe spec interface |
| IFT-042 choix profil cohorte | 110 | **CIBLE** | Surface ORGADMIN minimale |
| U16-S2b Playwright advisory | 31/70 | **Ouvert** | Fixture session orange + advisory |
| Scénarios manuels S16-A1→A5 | 110 | **Ouvert** | QA persona A1/A2/A3 |
| Encoors parité | transversal | **A_VÉRIFIER** | Oracle prod |
| Injection mémoire prompt | 20 | **CIBLE** | Décision doc hors lot 1 |
| RAG vectoriel, intercalaires, D9bis | 30/80/120 | **CIBLE** | Couronne |

---

## 5. Campagnes de tests — état consolidé

| Campagne | Résultat | Référence |
|----------|----------|-----------|
| Cluster 15 pytest (90 tests) | PASS 2026-06-18 | `rapport_mise_a_jour_doc_post_tests_2026-06-18.md` |
| Cluster 16 backend (15 tests) | PASS | `cluster16_interface_apprenant_resultats_tests.md` |
| Cluster 16 Playwright (10 tests) | PASS | idem |
| Scénarios manuels §4 protocoles | **Non exécutés** | S16-A*, check-lists C15 |

---

## 6. Addendum 2026-06-20 — profils globaux apprenant & pipes admin

**Hors périmètre C16** mais aligné sur domaines **10, 31, 70, 110** :

| Livrable | Statut doc | Référence |
|----------|------------|-----------|
| `LearnerConversationGlobalProfile` + résolveurs | **ALIGNE** | `MINI_SPEC_PROFILS_CONVERSATIONNELS_APPRENANT.md`, matrice V6 §19 |
| Admin Super Admin / OrgAdmin | **ALIGNE** | `/admin/conversation/learner/profiles`, `GroupAdminDetailView` |
| Tests automatisés | **12 pytest + 4 Playwright admin + 11 tenant** | archive §2 bis ; `test_final_complétude_améliorations.md` §10 |
| Fallback legacy TutorPrompt | **Documenté actif** | Ne pas présenter comme supprimé |

**Matrice :** V5 → **V6** (`cluster2_matrice_runtime_vs_cible.md`).  
**Briefing CTO :** régénéré post-20/06 (`generate_cto_briefing_docx.py`).

**Trous restants (non C16) :** synthèse admin, orchestrateur statique, starter prompts, policies eval groupe — voir matrice §19.

---

## 7. Prochaine sortie utile

1. Exécuter scénarios manuels S16-A1→A5 et mettre à jour `cluster16_interface_apprenant_resultats_tests.md` § manuels.
2. Oracle Encoors sur posture, CTA advisory, profils globaux et profils d’affichage (domaines 10/31/110).
3. Backlog IFT-042 + test Playwright U16-S2b si priorité produit.
4. P1 pipes : admin synthèse ; UI policies évaluation groupe.

---

*Rapport généré après passe documentaire transversale post-cluster 16 — addendum 20/06 profils globaux.*
