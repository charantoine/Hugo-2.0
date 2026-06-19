

## Cluster 5 – « Surfaces apprenant complètes »

**But** : finir tout ce qui touche l’apprenant, de façon industrialisable.

Périmètre :

- Profils d’affichage 3 grammaires (D2‑M08 finalisé).
- conversation_mode exploité proprement (bandeau, copy, états “degradé” type G1‑01).
- CTA synthèse / évaluation full story (UI + tests), mais sans toucher à la doctrine d’évaluation (déjà actée).

Automation :

- Pack Jest front centré A1/A2/A3 :
    - DSP‑01..04, DSP‑07, INV‑07/08, A1‑08, G1‑01/04.[^1]
- Pack pytest “UIState + CTA + mémoire” :
    - tests CTA, tests session_memory_contract, tests UIState cluster 4.[^2][^3]

Livrables :

- Design doc “Front apprenant 3 grammaires”.
- Pack tests front “A1/A2/A3” + script `npm test` unique.
- Patch matrice (domaines 10 / 110) pour passer D2‑M01 / D2‑M08 en statut quasi stable.[^4]

**Retex à caler** :

- À la fin de C5 : **Retex “surfaces apprenant”** (P0, progression, mémoire, CTA, UI apprenant).
- Objectif : vérifier qu’on n’a pas recréé des doubles contrats (UIState vs engagementUiModel), ni laissé des oracles UI non couverts.

***

## Cluster 6 – « Rôles, confidentialité, exports » (D2‑M07, D2‑M12, partie D2‑M11)

**But** : verrouiller les **surfaces encadrants** (tuteur, formateur, ORGADMIN, superadmin) et les exports, avec une matrice rôles qui colle au code et aux tests.

Périmètre :

- D2‑M07 : matrice rôles / visibilité / partage, oracles B1, D1, G3, F1.[^1][^4]
- D2‑M12 : frontière ORGADMIN / superadmin (surface debug, export‑md, etc.).[^4]
- D2‑M11 (taxonomie des exports) : au moins un premier alignement UI/API doc.

Automation :

- Pack pytest “multi‑rôles” :
    - timeline tuteur (B1‑01/02),
    - EvidenceBundle (D1‑02, G3‑02),
    - IDOR (G3‑01),
    - exports interdits (G3‑03, D1‑04),
    - absence d’artefacts LLM sur surfaces non techniques (D1‑06, F1‑02).[^1]
- Optionnel : petit pack de tests API d’exports pour D1/D2 (period filters, scope tenant).

Livrables :

- Doc “Matrice rôles/visibilité V2” (reprend et prolonge ce que tu as déjà commencé dans la matrice / écarts 90/100).[^4]
- Tests pytest D2‑M07 + ajustements des tests existants.

**Retex à caler** :

- À la fin de C6 : **Retex “multi‑rôles \& exports”**.
- Ce Retex doit juger si la frontière ORGADMIN/superadmin est enfin claire, et décider si on a besoin d’un cluster dédié superadmin/ops ou si c’est “assez bon”.

***

## Cluster 7 – « Analytique \& D9bis encadré »

**But** : ouvrir D9bis, mais dans un cadre très contrôlé, sans casser la sobriété actuelle.

Périmètre :

- D2‑M06 / D9bis :
    - définir ce qui est un artefact LLM d’analyse (ConversationTurnLLMAnalysis, ConversationLLMAnalysis, exports analytiques),
    - surfaces superadmin/testeur uniquement,
    - zéro fuite vers apprenant/tuteur/ORGADMIN.[^4]
- D2‑M11 (taxonomie exports) : finaliser la catégorisation exports techniques vs exports métier.

Automation :

- Pack pytest “D9bis” :
    - tests sur endpoints internes/exports analytiques,
    - tests de permissions par rôle (seul SUPERADMIN / tester).
- Scripts d’export pour vérifier le contenu de `llmresponsepayload`/traces, ancrés dans les oracles F1 (superadmin).

Livrables :

- Spec “D9bis” (une page claire), reconnectée à la matrice domaine 80/100.
- Tests D9bis isolés, facilement désactivables en prod si besoin.

**Retex à caler** :

- **Obligatoire à la fin de C7**, car c’est là que tu touches au périmètre le plus risqué (analyse LLM, logs, exports).
- Retex “analytique et surfaces techniques” : si tu détectes trop de friction, tu peux décider un mini‑replay de ce cluster avec plus de séparation.

***

## Cluster 8 – « Parcours encadrants \& démos canonique » (B1, C1, D1)

**But** : terminer sur des **parcours bout‑en‑bout** qui démontrent la convergence, plutôt que sur des briques abstraites.

Périmètre :

- D2‑M09 (checklist parcours tuteur B1).
- Compléter les interfaces formateur (C1) et ORGADMIN (D1) à partir des oracles / scénarios déjà décrits.[^1]
- S’assurer que les démos “A1 + B1 + D1” sont scriptables et reproductibles (cluster 2 oracles déjà là).

Automation :

- Pack pytest/API + éventuellement scripts “demo runner” (pas forcément UI, mais au moins API) pour :
    - S1–S4 A1 (déjà amorcé),
    - B1 (timeline, synthèse/éval, traces),
    - D1 (exports, bundles, config).[^1]
- Checklists UI (moins automatisables, mais au moins décrites).

Livrables :

- Doc “Parcours canoniques A1/B1/D1”.
- Batteries automatisées minimales pour valider ces parcours à chaque changement.

**Retex à caler** :

- **Retex final** après C8 : verifier qu’on n’a pas laissé de domaines “AMBIGU” ou “ABSENT_NOUVEAU_CONTRAT” critiques dans la matrice, et décider si un replay partiel est nécessaire (par exemple sur D9bis ou un sous‑ensemble des exports).

***

## Où mettre les Retex pour pouvoir “refaire plus propre”

Vu ta stratégie gros paquets + automation, je mettrais trois Retex structurants :

1. **Après C5 (apprenant)**
    - Retex “UI apprenant \& états” :
        - On vérifie qu’on n’a pas recréé une double pile UIState / engagement,
        - On vérifie que les profils d’affichage sont vraiment un skin, pas un second contrat.
    - Si c’est sale : tu peux **rejouer C5** sans casser le reste (rôles, D9bis pas encore touchés).
2. **Après C6 (rôles/confidentialité)**
    - Retex “multi‑rôles \& exports” :
        - On vérifie que la matrice domaine 90/100 est lisible et raccord avec les tests,
        - On vérifie qu’il n’y a plus d’IDOR ou de fuite P0/verbatim sur les surfaces apprenant/tuteur/orgadmin.
    - Si tu détectes trop de bricolage, tu peux refaire un C6’ sans impacter D9bis ni les parcours encadrants.
3. **Après C7 (D9bis/analytique)**
    - Retex “analytique et surfaces techniques” :
        - On tranche si les artefacts LLM sont correctement parqués,
        - On voit si la taxonomie d’exports tient,
        - On décide si ça mérite un replay (C7 bis) avant de script les démos B1/C1/D1.

Le Retex final après C8 est plus un **bilan** qu’un point de “refaire ou pas” ; les vrais embranchements de replay se situent plutôt après C5, C6 et C7.

Si tu veux, je peux t’écrire un **template unique de Retex** (comme celui qu’on a pour clusters 1–4) que tu pourras réutiliser pour C5/C6/C7 pour garder la même structure.

<div align="center">⁂</div>

[^1]: Cluster-2-Oracles-de-test-par-persona-validation-courte.md

[^2]: 10_runtime_p0_progression_uistate_note_lot_courant_cta_synthese_evaluation.md

[^3]: backlog_lot_1.md

[^4]: cluster2_matrice_runtime_vs_cible.md

