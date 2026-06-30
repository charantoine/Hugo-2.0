# Prompt Cursor long — Audit Hugo 1.9

```text
Tu vas conduire un audit d’implémentation complet de Hugo, backend + frontend + rôles/comptes/admin + tests exécutables, en t’appuyant d’abord sur le pack documentaire fourni et non sur des suppositions.

OBJECTIF
Établir précisément :
1. ce qui est réellement implémenté,
2. ce qui est conforme aux specs actuelles,
3. ce qui diverge,
4. ce qui est seulement partiellement branché,
5. ce qui est hors périmètre documentaire,
6. ce qui relève d’une consigne contextuelle du fil et non d’une vieille spec formalisée.

IMPORTANT
Tu ne dois jamais confondre :
- la spec explicite,
- la spec implicite raisonnablement déductible,
- la consigne contextuelle du fil,
- ta propre interprétation.

Tu dois garder ces catégories visibles dans tous tes livrables.

PACK À LIRE DANS CET ORDRE
1. README_PACK_CURSOR.md
2. CONTEXTUALISATION_COMPLETE_HUGO_1_9.md
3. HORS_PERIMETRE_GAPS_ROADMAP.md
4. CHECKLIST_AUDIT_BACKEND.md
5. CHECKLIST_AUDIT_FRONTEND.md
6. PLAN_TESTS_API_CHROMIUM.md
7. PROMPT_CURSOR_AUDIT_LONG.md

HIÉRARCHIE DE DÉCISION
Quand tu rencontres une tension documentaire, applique la hiérarchie suivante :
1. SPEC POC v1.5 update 27/03/2026
2. Hugo 1.6 Cadrage Transformation du comportement
3. README Cursor des lots
4. Lots 0 à 6
5. Code réel / branches / migrations / tests / UI
6. Pack d’audit consolidé

RÈGLES IMPÉRATIVES
- Ne jamais conclure à partir d’un seul lot isolé.
- Front : niveau d’attention maximal.
- Les changements front attendus dans cette série ne devaient être appliqués que sur la branche déjà améliorée ergonomiquement pour être plus montrable. Tu dois vérifier explicitement ce point.
- Ne déclare pas un élément “implémenté” s’il existe seulement dans le repo sans être branché ou observable.
- Si une question n’est pas suffisamment spécifiée, tu la classes “à arbitrer” ou “hors périmètre documentaire”, tu ne l’inventes pas.
- Si un besoin est formulé dans le fil mais pas dans les docs, tu l’étiquettes “consigne contextuelle du fil”.

CE QUE TU DOIS PRODUIRE

LIVRABLE 1 — TABLEAU SOURCES ET PRIORITÉS
Tu construis un tableau contenant :
- source
- niveau hiérarchique
- zone couverte
- ce que la source fixe vraiment
- ce qu’elle ne fixe pas
- priorité de lecture

LIVRABLE 2 — BASE DE DÉCISION DOCUMENTAIRE EXHAUSTIVE
Tu construis une base de décision documentaire avec, pour chaque point important :
- identifiant
- thème
- formulation consolidée
- verbatim utile si nécessaire
- source principale
- sources secondaires
- type : spec explicite / spec implicite / consigne contextuelle du fil / interprétation
- impact back
- impact front
- méthode d’audit associée

LIVRABLE 3 — MATRICE DE CRITÈRES AUDITABLES
Tu transformes toutes les specs pertinentes en critères auditables avec :
- identifiant
- intitulé court
- nature : backend / frontend / API / data / sécurité / rôles / UX / tests
- source
- méthode de vérification
- preuve attendue
- résultat observé
- statut : conforme / non conforme / partiel / non observable / hors périmètre documentaire / à arbitrer
- criticité : bloquant / majeur / mineur / ambigu

LIVRABLE 4 — RAPPORT BACKEND
Le rapport backend doit couvrir au minimum :
- structure des dataclasses et enums canoniques
- respect du gel P0
- migrations et modèles ajoutés
- endpoints nouveaux ou modifiés
- désérialisation JSONB
- stockage canonique des enums `.value`
- mémoire thématique post-conversation
- base de connaissance formateur
- observabilité / analytics si présents
- RLS / organisationid avec s
- conformité des tests

LIVRABLE 5 — RAPPORT FRONTEND
Le rapport frontend doit couvrir au minimum :
- branche réellement auditée
- lien avec la branche ergonomique montrable
- composants créés ou modifiés
- usage effectif de UIState
- intégration réelle du panneau de progression
- synthèse / évaluation visibles et branchées
- régression ou stagnation visuelle éventuelle
- exposition interdite éventuelle de champs P0
- fonctionnement réel en navigation simulée

LIVRABLE 6 — RAPPORT COMPTES / RÔLES / ADMIN
Tu dois cartographier précisément :
- qui peut créer quels comptes
- endpoints existants
- écrans existants
- ce qui relève de Django admin ou d’une interface technique uniquement
- ce qui est réellement disponible côté ORGADMIN
- ce qui est réellement disponible côté SUPERADMIN
- ce qui existe ou non côté tuteur / formateur pour gérer apprenants / tuteurs / rattachements / consignes pédagogiques
- ce qui est spécifié mais absent
- ce qui est demandé dans le fil mais non suffisamment balisé

LIVRABLE 7 — RAPPORT TESTS API + CHROMIUM
Tu dois préparer et si possible exécuter :
- tests API fonctionnels
- tests d’intégration back/front
- tests navigateur type Chromium / Playwright
- captures d’écran des écrans clés
- preuves d’exécution
- logs d’échec exploitables

LIVRABLE 8 — SYNTHÈSE DES ÉCARTS CRITIQUES
Tu produis une synthèse finale classant les écarts :
- bloquants
- majeurs
- mineurs
- ambigus

Chaque écart doit inclure :
- source de la règle
- constat observé
- preuve
- niveau de confiance
- proposition d’action

POINTS D’AUDIT À CONTRÔLER OBLIGATOIREMENT

A. FONDATIONS / P0
- Aucun champ P0 existant modifié dans turnstatev17.py ou decisionenginev17.py.
- Orchestrateur et promptrenderer seulement en patch additif.
- Imports canoniques depuis conversationprofile.py.
- UIState sans champ P0 brut.
- Tests NR-07 et NR-09 présents et pertinents.

B. LOT 0 / LOT 1
- conversationprofile.py / reasoncodes.py / tutorprofiles.py stub au départ.
- migration conversationprogress sur HugoSession.
- endpoints /progress /ui-state /posture.
- ConversationProgressCalculator réellement branché après decideconversation.
- deserialize_conversation_progress réellement utilisé partout où nécessaire.

C. FRONT LOT 2
- progressionLabels.js présent.
- engagementUiModel.js réellement remplacé.
- HugoProgressPanel.jsx présent, utilisé, visible.
- consommation de /ui-state.
- gestion de gamification_profile.
- synthèse / évaluation branchées.
- branchage sur la bonne branche ergonomique montrable.

D. LOT 3
- postureselector.py présent.
- tutorprofiles.py stub remplacé complètement.
- set-posture présent.
- transitions de posture respectées.
- synthèse et évaluation passent par synthesisservice.py.

E. LOT 4
- LearnerThemeMemory présent avec organisationid.
- consolidate_session post-conversation uniquement.
- normalize_knowledge_status présent.
- pas d’auto-upgrade derived_provisional -> validated_trainer.
- memory-summary présent.
- feature flag USETHEMEMEMORY géré proprement.

F. LOT 5
- TrainerKnowledgeItem présent.
- pipeline documentingestor.py.
- questionnaire dialogique formateur.
- validation humaine obligatoire avant status validated_trainer.
- vues trainer présentes ou absentes, et si absentes le signaler.

G. LOT 6
- ConversationQualitySignal.
- qualitytracker.py.
- cohortdashboard / views analytics.
- signaux réellement produits et consommés ou non.

H. COMPTES / ADMIN / RÔLES
- création manuelle des comptes POC.
- endpoints admin organisations / users / groups.
- capacités réelles ORGADMIN.
- capacités réelles SUPERADMIN.
- espaces UI disponibles ou non.
- gestion apprenant / tuteur / rattachement formation / consignes pédagogiques : existant, partiel, absent, ou non balisé.

MÉTHODE D’EXÉCUTION
1. Cartographier branches, fichiers, migrations, endpoints, composants, tests.
2. Vérifier la séquence réelle des lots.
3. Distinguer présence du code, branchement, usage, visibilité.
4. Vérifier par tests et navigation simulée.
5. Produire les livrables dans l’ordre demandé.
6. Ne jamais masquer une incertitude : la classer explicitement.

FORMAT DE SORTIE
Tu organises ta sortie avec les sections suivantes :
1. Sources et hiérarchie
2. Base de décision documentaire
3. Matrice de critères auditables
4. Rapport backend
5. Rapport frontend
6. Rapport comptes / rôles / administration
7. Rapport tests API + Chromium
8. Écarts critiques et recommandations

ATTENTION FINALE
Si le front a très peu changé alors que LOT 2 et le README des lots annoncent plusieurs modifications visibles, tu dois traiter cela comme un signal de non-conformité possible et le vérifier activement, pas comme un détail.
```
