# A7 — Mode d'emploi pour futur espace Perplexity

**Date :** 22 juin 2026

---

## 1. Comment exploiter A0–A6

### Grille de lecture rapide

| Besoin | Fichiers |
|--------|----------|
| Recalage 10 min | A0 → A1 → A6 |
| Spec une feature | A2 (domaine) → A3 (objets) → A4 (si moteur) → A5 (écarts) |
| Audit écart | A5 + `ecarts — <domaine>.md` + cluster2 ligne domaine |
| Onboarding CTO | A1 + B0 sections 1–3 |
| Variables P0 / prompting | B0 section 7 + `variables_prompting.md` |
| Démo / runtime | A1 §5–6 + docs 07–10 |

### Règle d'or

Chaque réponse Perplexity doit **tagger** chaque affirmation : RÉEL OBSERVÉ | CIBLE | ÉCART CONFIRMÉ | A_VERIFIER | HYPOTHÈSE.

---

## 2. Prompts types à lancer (ordre suggéré)

### Session 1 — Calage espace

```
En t'appuyant sur documentation_photo_reel_2026_06_22/A1 et cluster2_matrice_runtime_vs_cible.md,
liste les 10 écarts confirmés les plus impactants pour la spec des prochaines fonctions.
Sépare réel local et A_VERIFIER Encoors.
```

### Session 2 — Contrat UIState

```
À partir de A3, A4 et ecarts —10_runtime_p0_progression_uistate.md,
rédige un contrat minimal UIState v2 (champs, producteur, consommateurs, interdits).
Ne pas inclure TurnState ni P0 brut. Taguer chaque champ RÉEL ou CIBLE.
```

### Session 3 — Mémoire

```
Lot courant = mémoire intra-conversation uniquement.
À partir de ecarts — 20_memoire_gouvernee.md et A3,
propose un contrat d'injection session_memory dans prompt_renderer (si lot 2).
Distingue ce qui est déjà livré (API, panneau) de ce qui est écart confirmé.
```

### Session 4 — Posture et CTA

```
Spec D2-M02 : tableau posture → RAG → maturité → CTA.
Sources : A2 domaines 1–3, cluster2 §1, spec interface 2.0 (CIBLE).
```

### Session 5 — Encadrants

```
Parcours tuteur B1 et formateur C1 : état réel vs cible specs formateur+tuteur 2.0.
Marquer A_VERIFIER tout ce qui dépend d'Encoors.
```

### Session 6 — Confidentialité

```
Matrice rôle × visibilité × partage (D2-M07).
Partir de ecarts — 90_confidentialite_partage_multitenant_roles.md et tests cluster 3/6.
```

---

## 3. Ordre de traitement des questions

1. **Infrastructure vérité** : runtime référence, flags, Encoors (A6).
2. **Noyau conversationnel** : P0, UIState, progression (A4, B0 §6–7).
3. **CTA terminaux** : synthèse, évaluation (A2 §6–7).
4. **Mémoire lot courant** (A2 §4, ecarts-20).
5. **RAG lexical** (ne pas sur-vendre vectoriel).
6. **Surfaces encadrants** (partiel — spec incrémentale).
7. **Couronne** : observabilité produit, intercalaires, RAG vectoriel.

---

## 4. Comment séparer réel / cible / backlog

### Template de réponse Perplexity

```markdown
## Sources mobilisées
- …

## Réel confirmé
- …

## Cible 2.0
- …

## Écarts
- …

## A_VERIFIER
- …

## Prochaine sortie utile
- …
```

### Interdictions

- Ne pas écrire « Hugo 2.0 livre X » sans preuve code.
- Ne pas utiliser le glossaire seul comme citation d'implémentation.
- Ne pas déduire le moteur depuis `ProdLearnerWorkspace.vue` seul.
- Ne pas fusionner baseline A et B sans le dire.

---

## 5. Questions à traiter en premier (backlog spec)

| Priorité | Question | Fichiers d'entrée |
|----------|----------|-------------------|
| 1 | Quel runtime fait foi pour « Hugo aujourd'hui » ? | A6 §1, 07, 10 |
| 2 | Contrat UIState unique ? | A3 §6, A5 §6 |
| 3 | Tableau posture/RAG/CTA (D2-M02) | A2, cluster2 §1 |
| 4 | Matrice rôles confidentialité (D2-M07) | A2 §8–9, ecarts-90 |
| 5 | Enrichissement trace ou pivot suffisant ? | A2 §8, ecarts-70 |
| 6 | Injection mémoire prompt — lot 2 ou hors scope ? | ecarts-20, A6 §6 |
| 7 | v17 : activer, documenter ou retirer ? | A4 §20, A6 §8 |
| 8 | Parité Encoors : plan de test authentifié | A6 §1, 10 |

---

## 6. Pièges documentaires (checklist avant publication spec)

- [ ] Aucune référence `[file:nn]` ou marqueur machine
- [ ] MEMO CTO cité comme obsolète si écarts 1–3–5–6
- [ ] `backend/` monorepo signalé vide si deploy discuté
- [ ] Mémoire inter-session non présentée comme injectée au tour
- [ ] RAG vectoriel tagué CIBLE
- [ ] Certification autonome évaluation explicitement interdite
- [ ] Distinction 3 scènes UI vs 5 jalons moteur
- [ ] Encoors : date inspection et limites rappelées

---

## 7. Corpus complémentaire hors dossier A/B

À attacher à l'espace Perplexity comme sources secondaires :

| Fichier | Usage |
|---------|-------|
| `spec_canonique_hugo_2_0.md` | Cible uniquement |
| `glossaire_alignement_hugo_reel_vs_spec.md` | Pont vocabulaire |
| `DOC_METHODO_REFERENCE_CONVERGENCE_HUGO_REVISE.md` | Méthode |
| `plan_documentation_cto_convergence_hugo.md` | Trajectoire vagues |
| `cluster2_matrice_runtime_vs_cible.md` | Matrice domaines |
| `ecarts — *.md` | Détail par domaine |
| `variables_prompting.md` | Variables P0/prompt |
| `02`–`10` docs-workspace | Socle réel |

---

## 8. Exploitation de B0

`B0_MONOGRAPHIE_SCIENTIFIQUE_HUGO_REEL_2026_06_22.md` sert de :

- document autoportant pour chercheur / analyste ;
- source unique pour sections P0 détaillées (§7) ;
- index routes/objets (annexes).

Ne pas dupliquer B0 dans Perplexity — le citer comme référence monographique.

---

*Mode opératoire aligné sur DOC_METHODO_REFERENCE_CONVERGENCE_HUGO_REVISE.md.*
