# R5 — Écarts depuis baseline 2026-06-22

**Date :** 1er juillet 2026  
**Référence :** baseline `documentation_photo_reel_2026_06_22/` (A0–A7, B0) + docs-workspace juin.  
**Compare à :** lot R1–R4 (état réel 01/07/2026).

---

## Légende colonne « Nature »

| Nature | Signification |
|--------|---------------|
| **confirmé** | L'écart baseline reste vrai |
| **corrigé** | Livraison ou preuve post-22/06 comble l'écart |
| **obsolète** | Le constat baseline n'est plus exact |
| **complété** | Baseline incomplète ; enrichissement documenté |
| **toujours ouvert** | Non résolu ; peut être confirmé ou élargi |

---

## 1. Tableau des écarts majeurs

| ID | Sujet | Baseline (A*/docs) | État 01/07/2026 | Nature | Fichiers historiques | Impact specs |
|----|-------|-------------------|-----------------|--------|----------------------|--------------|
| E01 | Stack vérité moteur | `hugo_back` seul backend | Inchangé | **confirmé** | A1 | Aucun — continuer backend-first |
| E02 | Monorepo backend vide | Non moteur | Inchangé | **confirmé** | 00, 01 | Ne pas spec sur compose monorepo |
| E03 | P0 legacy par défaut | v17 off | Inchangé code | **confirmé** | A1, A4, 02 | Specs sur legacy sauf flag explicite |
| E04 | UIState sans P0 front | INV-01 | Tests renforcés C16 | **complété** | A4, cluster 3 | Garde-fou maintenu |
| E05 | Double schéma UIState | Mentionné | Toujours présent | **confirmé** | A4, cluster 2 | Specs doivent nommer contract vs tour |
| E06 | Mémoire non injectée LLM | Cluster 9–10 | Toujours absent prompts | **confirmé** | A4, ecarts 20 | Ne pas spec injection comme livré |
| E07 | memory-summary front | Absent apprenant (pré-C15) | LearnerMemoryPanel | **corrigé** | A2, C15 | Specs UX mémoire possibles |
| E08 | theme_memories dans API | Écart ADR | Toujours présent | **toujours ouvert** | contrat memory, ecarts 20 | Param scope ou doc produit |
| E09 | Posture lecture seule | A2 juin 22 | set-posture + selector | **corrigé** | A2, C15/C16 | Specs posture = backend gouverné |
| E10 | Profils globaux apprenant | Non dans A1 | API + admin | **complété** | —, matrice V6 | Nouveau périmètre admin |
| E11 | Formateur validation | Basique | workflow C15 | **corrigé** | A2, audit formateur | Specs trainer alignées C15 |
| E12 | Élicitation formateur | Absent / partiel | Vue V0 | **corrigé** | audit formateur 04 | Atelier V0 cadré |
| E13 | RAG vectoriel | Inactif | Toujours lexical | **confirmé** | A1, ecarts 30 | Pas de spec pgvector actif |
| E14 | Chaîne EVAL1 local | Partiel juin | cluster 11 PASS | **corrigé** | A5, ecarts 70 | Pivot v1 = référence export |
| E15 | EVAL1 Encoors | Non prouvé | Toujours sans oracle auth | **toujours ouvert** | doc 10, cluster 11 | Bloquer spec « prod EVAL1 » |
| E16 | conduct-profiles Encoors | Absent 12/06 | Pas re-inspecté | **toujours ouvert** | doc 10 | Mode testeur sur distant |
| E17 | CORS localhost → Encoors | Bloqué 12/06 | Pas re-probe | **toujours ouvert** | doc 10 | Démo locale ≠ distant |
| E18 | DEBUG prod Encoors | True 12/06 | Pas re-probe | **toujours ouvert** | doc 10 | OPS / sécurité |
| E19 | Front .env → Encoors | Distant par défaut | Inchangé commité | **confirmé** | 07, 08 | Baseline A toujours défaut repo |
| E20 | E2E protocole | N'existait pas | 23 PASS 29/06 | **complété** | — | Référence non-régression |
| E21 | Campagne multi-tenant | Partielle | Rapport 30/06 + tests | **complété** | A6 | Bandeau org documenté |
| E22 | ACL trainer learners | Peu documenté | `[]` dashboard — INC-02 | **toujours ouvert** | — | **Geler** spec visibilité learners |
| E23 | Dual DB local | Ambigu | Diagnostic INC-04 | **complété** | rapport 30/06 | Toujours tracer stack |
| E24 | Interface apprenant C16 | En cours juin | 25 tests auto PASS | **corrigé** | A5 chantiers | Socle apprenant stabilisé |
| E25 | spec_canonique_hugo_2_0 | Cible | Toujours CIBLE | **confirmé** | A5, glossaire | Jamais preuve livraison |
| E26 | LearnerThemeMemory injection tour | Doctrine hors lot | Toujours hors injection | **confirmé** | ecarts 20, B0 | Inter-session = préparation |
| E27 | D9bis superadmin | Partiel | Routes local OK | **complété** | ecarts 80 | Canal séparé maintenu |
| E28 | Exports D2-M06 | Partiel | Tests PASS | **corrigé** | ecarts 100 | Exports specifiables |
| E29 | Playwright scaffold L5–L11 | — | 5 SKIP données | **toujours ouvert** | E2E rapport | Données démo à enrichir |
| E30 | Staging / prod hors Encoors | Non documenté | Non inspecté | **toujours ouvert** | — | **À VÉRIFIER** si existe |

---

## 2. Écarts par document historique

### A1 — Socle réel

| Statut | Détail |
|--------|--------|
| **Conservé valide** | Stack, flags P0, apps Django, pipeline ordre |
| **Obsolète** | Interfaces apprenant/formateur (pré-C15/16), profils globaux absents |
| **À jour via** | **R1** |

### A2 — Cartographie fonctionnelle

| Statut | Détail |
|--------|--------|
| **Obsolète partiel** | Posture, mémoire front, formateur workflow |
| **Conservé valide** | RAG lexical, séparation rôles, tuteur partiel |
| **À jour via** | **R2** |

### A3 — Objets et contrats

| Statut | Détail |
|--------|--------|
| **Archive de référence** | Variables prompting, objets métier |
| **Complété par** | **R4**, `contrat_api_memory_summary_v1.md`, cluster 4/16 |

### A4 — Architecture et pipelines

| Statut | Détail |
|--------|--------|
| **Conservé valide** | Ordre pipeline, legacy/v17, RAG lexical |
| **Complété** | UIState contract, set-posture, profils globaux |
| **À jour via** | **R3** |

### A5 — Écarts vers cible

| Statut | Détail |
|--------|--------|
| **Archive** | Chantiers juin ; plusieurs **corrigés** (E07, E09, E11–E14, E24) |
| **À jour via** | **R5** (ce doc) + `cluster2_matrice` V6 |

### A6 — Preuves manquantes

| Statut | Détail |
|--------|--------|
| **Remplacé** | **R6** — liste actualisée |

### A7 — Mode d'emploi

| Statut | Détail |
|--------|--------|
| **Remplacé** | **R7** |

### B0 — Monographie

| Statut | Détail |
|--------|--------|
| **Référence historique** | Vocabulaire scientifique ; ne pas inférer livraison |

### docs-workspace 02, 03, 05, 07–11

| Doc | Statut 01/07 |
|-----|--------------|
| 02 moteur | **REL OBSERV PARTIEL** — flags OK ; routes enrichies |
| 03 produit | **REL OBSERV PARTIEL** — C15/16 non intégrés au doc |
| 05 écarts | **À mettre à jour** post-R5 |
| 07–08 runtime | **Confirmés** baselines A/B |
| 10 Encoors | **Périmé partiel** — date 12/06 |
| 11 comptes | **Complété** INC-04 dual stack (30/06) |

---

## 3. Écarts confirmés encore bloquants pour specs « prod globale »

1. **Encoors non ré-oraclisé** depuis 12–18/06 (E15–E18).
2. **ACL formateur learners** sans décision CTO (E22).
3. **theme_memories** dans API sans filtre scope (E08).
4. **Synthèse/éval E2E** non couverte automatiquement (E29).

---

## 4. Impact sur prochaines specs

| Si la spec touche… | S'appuyer sur… | Éviter… |
|-------------------|----------------|---------|
| Apprenant UX | R2 domaine 31, R4 UIState, tests C16 | Spec 2.0 seule |
| Mémoire | R3 §6, R4 memory-summary, ecarts 20 | LearnerThemeMemory au tour |
| Formateur | C15 résultats, R2 §40–50 | Dashboard learners sans INC-02 |
| Runtime prod | R6 plan Encoors | doc 10 comme état juillet |
| P0 / v17 | R3 §3–4, flags 08 | Présenter v17 comme défaut |
| Hugo 2.0 global | glossaire + **CIBLE** | spec_canonique comme preuve |

---

*Suite : **R6** (plan acquisition preuves).*
