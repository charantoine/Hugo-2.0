# R7 — Mode d'emploi pour specs fidèles

**Date :** 1er juillet 2026  
**Successeur de :** `A7_MODE_EMPLOI_POUR_FUTUR_ESPACE_PERPLEXITY.md` (22/06/2026).  
**Public :** sessions Cursor, Perplexity, rédaction mini-specs / backlogs DOC·CODE·OPS.

---

## 1. Comment utiliser le lot R0–R6

| Besoin | Lire en ordre |
|--------|---------------|
| Première immersion | R0 → R1 → R4 |
| Spec domaine fonctionnel | R7 (ce doc) → R2 §domaine → R4 si contrat API |
| Spec pipeline / P0 | R3 → code `hugo_orchestrator.py` → tests cluster 3/16 |
| Spec front apprenant | R2 §31 → R4 UIState → `cluster16_*` |
| Spec formateur | R2 §40–50 → `cluster15_*` → **vérifier INC-02** |
| Écart vs juin 2026 | R5 |
| Preuve manquante / gel | R6 |
| Démo | doc 07 + 11 + R1 § baselines |

**Ne jamais sauter R0** pour la hiérarchie de vérité.

---

## 2. Quels fichiers lire selon la question

| Question | Fichiers prioritaires | Ne pas lire seul |
|----------|----------------------|------------------|
| Comment fonctionne P0 ? | R3 §2–3, `hugo_orchestrator.py`, `test_cluster3_oracles.py` | B0, spec 2.0 |
| Qu'est-ce que UIState ? | R4 §3, `ui_state_builder.py`, B16 tests | A3 seul |
| Mémoire apprenant ? | R3 §6, R4 §4, `contrat_api_memory_summary_v1.md` | LOT4 inter-session |
| RAG ? | R3 §7, `rag_support.py` | Corpus RAG Melec |
| CTA synthèse/éval ? | R4 §5, `cta_ui_state.py` | Spec évaluation 2.0 |
| Multi-tenant ? | R2 §90, `rapport_test_30juin.md` | Hypothèse RLS |
| Formateur workflow ? | `cluster15_interfaces_apprenant_formateur_resultats.md` | Audit mai 2026 |
| Prod Encoors ? | R6 PM-*, doc 10 (12/06) | `.env` front comme preuve moteur |
| Hugo 2.0 complet ? | `spec_canonique_hugo_2_0.md` (**CIBLE**) | Jamais sans R5/R6 |

---

## 3. Prompts types pour une spec fidèle au réel

### 3.1 Mini-spec domaine (template)

```
Contexte : lot recalage R0–R7 (01/07/2026). Evidence-first.

Domaine : [ex. 31 front apprenant posture]

Lire obligatoirement :
- R2 §[domaine]
- R4 §[contrat]
- ecarts — [domaine].md
- tests : [fichiers pytest]

Produire :
1. Sources mobilisées (avec dates de preuve)
2. Réel confirmé (tag REL OBSERV)
3. Cible 2.0 (tag CIBLE)
4. Écarts confirmés
5. À VÉRIFIER
6. Contrat minimal codable (JSON ou états)
7. Backlog DOC / CODE / OPS

Interdits :
- Présenter spec_canonique_hugo_2_0 comme livré
- Fusionner local et Encoors
- Exposer P0 au front /app
- Speculer injection mémoire LLM
```

### 3.2 Audit écart code vs doc

```
Comparer [fichier doc historique A* ou ecarts — X] au code hugo_back + tests [liste].

Classer chaque assertion : confirmé | obsolète | complété | À VÉRIFIER.
Citer fichier:ligne ou test nommé.
Baseline : [local B | Encoors | les deux séparés].
```

### 3.3 Prompt front (composant)

```
Composant : [ex. PostureSelector.vue]

Contrat backend unique : GET ui-state conversation_mode + POST set-posture.
Le front ne calcule pas l'éligibilité (can_switch backend only).

Preuves : cluster 15 A1, B16-P2/P3, R4 §3 et §8.
Lister champs UIState consommés et erreurs API mappées.

**Décision B (01/07)** : pour specs tuteur/formateur, ne pas prescrire `GET /ui-state/` comme pilotage UI ;
référencer `addendum_exploration_baseline_B_2026_07_01.md` §3.
```

### 3.4 Prompt OPS / Encoors

```
Exécuter oracle Encoors selon R6 Phase 2.
Ne conclure parité qu'avec JSON authentifié daté.
Documenter écarts routes vs hugo_back/apps/hugo/urls.py.
```

---

## 4. Checklist anti-hallucination documentaire

Avant de livrer une spec ou une analyse :

- [ ] **Baseline nommée** (local B, Encoors A, smoke sqlite, etc.)
- [ ] Chaque comportement a un tag : REL OBSERV | PARTIEL | À VÉRIFIER | CIBLE
- [ ] Au moins une preuve **code ou test** pour chaque « IMPLÉMENTÉ »
- [ ] `spec_canonique_hugo_2_0.md` cité seulement en **CIBLE**
- [ ] Pas de champ P0 / verbatim dans contrat front apprenant
- [ ] Mémoire : distinguer `session_memory` vs `theme_memories` vs injection LLM
- [ ] UIState : préciser GET contract vs payload tour
- [ ] RAG : lexical seul sauf preuve contraire
- [ ] Encoors : date de dernière inspection citée (12/06 si pas de re-probe)
- [ ] Glossaire = pont vocabulaire, pas preuve
- [ ] Fichiers historiques A* : statut confirmé / obsolète / archive
- [ ] Sujets R6 « gelés » non présentés comme livrables

---

## 5. Règles de séparation réel / cible / backlog

### Réel (REL OBSERV)

- Décrire ce que font `hugo_back` et `frontend_1.8` **aujourd'hui** sur la baseline déclarée.
- S'appuyer sur tests nommés quand possible.

### Cible (CIBLE)

- Hugo 2.0, intercalaires, EvaluationTrace complète, RAG vectoriel, injection mémoire LLM, orchestrateurs scriptés F1–F4.
- Toujours labelliser **CIBLE** et lier à `spec_canonique_hugo_2_0.md` ou écarts domaine.

### Backlog

- Actions DOC/CODE/OPS issues des écarts **non fermés** (R5, R6).
- Format : verbe + fichier cible + dépendance preuve.

### À VÉRIFIER

- Tout ce qui dépend d'Encoors non ré-oraclisé, RLS prod, décision INC-02, E2E SKIP.

**Phrase interdite :** « Hugo fait X » sans baseline + preuve.

**Phrase autorisée :** « En baseline B (local dev, 01/07), le test `test_b16_p2` confirme que set-posture met à jour UIState. »

---

## 6. Patron de sortie spec (obligatoire)

Reprendre le patron méthodo workspace :

1. **Sources mobilisées** (R0–R6, code, tests, date)
2. **Réel confirmé**
3. **Cible 2.0**
4. **Écarts**
5. **À VÉRIFIER**
6. **Prochaine sortie utile**

Pour un chantier domaine complet, enchaîner :

1. Rapport d'écarts narratif  
2. Matrice d'écarts  
3. Décisions documentaires  
4. Backlog DOC/CODE/OPS  

---

## 7. Pièges connus (actualisés 01/07)

| Piège | Correction |
|-------|------------|
| `.env` front → Encoors = preuve moteur local | Faux — baseline A ≠ B |
| `LearnerThemeMemory` = mémoire du tour | Faux — consolidation inter-session |
| memory-summary = historique chat | Faux — résumé gouverné structuré |
| Cluster test PASS = prod OK | Faux — voir R6 Encoors |
| Deux DB locales équivalentes | Faux — `which-hugo-stack.sh` |
| Formateur voit tous les learners | **À VÉRIFIER** — souvent faux (INC-02) |
| C16 Playwright = preuve chat posture | Partiel — oracle panneau mémoire surtout |

---

## 8. Correspondance rapide ancien → nouveau mode d'emploi

| A7 (22/06) | R7 (01/07) |
|------------|------------|
| Ordre lecture docs 00–10 | R0 §8 + ce §2 |
| Tags vérité | R0 §9 (étendus) |
| Pièges Perplexity | §7 ci-dessus |
| Prompts audit | §3 templates |

---

## 9. Après une session de spec

1. Mettre à jour le fichier `ecarts — <domaine>.md` si nouvel écart confirmé.
2. Si preuve Encoors acquise : mettre à jour R4 §10 ou doc 10.
3. Ne pas dupliquer R1–R4 : pointer vers le lot recalage.

---

*Entrée du lot : **R0**. Socle réel : **R1**.*
