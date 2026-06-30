# Pack Cursor — Audit Hugo 1.9 enrichi

## Objet du pack

Ce pack a été préparé pour permettre à Cursor de travailler **sans avoir à fouiller dans de vieilles specs dispersées**. Il regroupe dans une forme opérationnelle :

- l’ordonnancement documentaire ;
- la hiérarchie de décision ;
- les invariants techniques ;
- les points d’attention front ;
- la question des comptes / rôles / administration ;
- les checklists d’audit ;
- le plan de tests API + Chromium ;
- les hors périmètre et gaps roadmap ;
- un document long de contextualisation récapitulant les specs actuelles connues ;
- un prompt Cursor long prêt à copier-coller.

## Fichiers du pack

1. `README_PACK_CURSOR.md`
   - Point d’entrée.
   - Explique l’ordre de lecture et le mode d’exploitation du pack.

2. `PROMPT_CURSOR_AUDIT_LONG.md`
   - Prompt long prêt à copier-coller dans Cursor.
   - Inclut les règles de méthode, de qualification et de restitution.

3. `CHECKLIST_AUDIT_BACKEND.md`
   - Checklist détaillée d’audit backend.
   - À exécuter point par point, avec statut et preuve.

4. `CHECKLIST_AUDIT_FRONTEND.md`
   - Checklist détaillée d’audit frontend.
   - Très orientée branche ergonomique, UIState, visibilité réelle et tests UI.

5. `PLAN_TESTS_API_CHROMIUM.md`
   - Plan de tests API, intégration et navigation Chromium / Playwright.
   - Contient parcours, fixtures, preuves attendues et stratégie d’exécution.

6. `HORS_PERIMETRE_GAPS_ROADMAP.md`
   - Ce qui n’est pas spécifié, pas assez balisé ou explicitement hors périmètre de ce paquet de lots.
   - Sert à éviter les inventions et les faux positifs d’audit.

7. `CONTEXTUALISATION_COMPLETE_HUGO_1_9.md`
   - Document long et ordonné, récapitulant les specs actuelles connues.
   - Distingue soigneusement : spec écrite, consigne contextuelle du fil, interprétation raisonnable, zones à arbitrer.

## Ordre de lecture imposé à Cursor

Cursor doit lire dans cet ordre :

1. `README_PACK_CURSOR.md`
2. `CONTEXTUALISATION_COMPLETE_HUGO_1_9.md`
3. `HORS_PERIMETRE_GAPS_ROADMAP.md`
4. `CHECKLIST_AUDIT_BACKEND.md`
5. `CHECKLIST_AUDIT_FRONTEND.md`
6. `PLAN_TESTS_API_CHROMIUM.md`
7. `PROMPT_CURSOR_AUDIT_LONG.md`

## Règles de décision obligatoires

### 1. Hiérarchie documentaire
Toujours appliquer la hiérarchie suivante :

1. SPEC POC v1.5 update 27/03/2026
2. Hugo 1.6 Cadrage Transformation du comportement
3. README Cursor des lots
4. Lots 0 à 6
5. Code réel, tests, migrations, composants, branches
6. Ce pack d’audit comme document de travail consolidé

### 2. Ne jamais conclure depuis un lot isolé
Les lots sont additifs et fortement interdépendants. Beaucoup d’erreurs d’audit viennent d’une lecture trop locale.

### 3. Distinguer quatre natures d’énoncés
Pour chaque point, Cursor doit utiliser l’un des quatre statuts suivants :

- `Spec explicite`
- `Spec implicite raisonnable`
- `Consigne contextuelle du fil`
- `Interprétation Cursor`

### 4. Distinguer présence de code et implémentation réelle
Un élément ne compte comme implémenté que s’il est :

- présent dans le repo ;
- branché ;
- exécuté ;
- observable ;
- cohérent avec la spec.

### 5. Front : vigilance maximale
Le front est un point d’audit prioritaire. Une implémentation qui a peu changé visuellement alors que LOT 2 attend plusieurs évolutions visibles doit être considérée comme potentiellement incomplète.

### 6. Branche front de référence
Les changements front de cette série devaient s’appliquer sur la branche déjà retravaillée ergonomiquement pour rendre Hugo plus montrable. Si ce n’est pas la branche auditée ou intégrée, Cursor doit le signaler comme écart majeur de méthode et de conformité.

## Livrables minimum exigés de Cursor

Cursor doit produire :

1. un tableau `sources / priorités / hiérarchie` ;
2. une base de décision documentaire exhaustive ;
3. une matrice de critères auditables ;
4. un rapport backend ;
5. un rapport frontend ;
6. un rapport comptes / rôles / administration ;
7. un rapport tests API + Chromium ;
8. une synthèse finale des écarts critiques.

## Question sensible : comptes / rôles / administration
Le pack impose à Cursor de distinguer :

- ce qui est spécifié dans la SPEC POC ;
- ce qui n’est pas détaillé dans les lots ;
- ce qui relève d’un besoin produit formulé dans le fil ;
- ce qui peut être lancé tout de suite ;
- ce qui doit d’abord être balisé avant construction.

Cursor ne doit pas inventer un back-office comptes complet s’il n’est pas réellement balisé. Il doit d’abord cartographier l’existant et qualifier les manques.

## Mode d’usage conseillé

### Option A — Audit pur
Utiliser le prompt long et demander à Cursor de produire uniquement les rapports d’audit.

### Option B — Audit + préparation de correctifs
Après l’audit, demander à Cursor de transformer les écarts confirmés en patchs précis, lot par lot, en respectant le gel P0.

### Option C — Audit + simulation exécutable
Lancer la campagne de tests API + Chromium définie dans le plan, avec captures et preuves d’exécution.

## Check de complétude du pack

Ce pack est considéré comme autoportant pour Cursor si :

- la hiérarchie documentaire est rappelée ;
- les invariants P0 sont rappelés ;
- le front est traité explicitement ;
- la contrainte de branche ergonomique front est explicite ;
- la question comptes / rôles / administration est intégrée ;
- les hors périmètre sont identifiés ;
- les tests exécutables sont prévus ;
- le long document de contextualisation est lu avant toute conclusion.

Si Cursor saute le document de contextualisation, l’audit risque de surinterpréter les lots.
