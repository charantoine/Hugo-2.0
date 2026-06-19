# Mémo CTO — Hugo 1.9 : état, constats, nouveau chantier TutorConductProfiles

**Date :** 1 juin 2026
**Objet :** Bilan travaux Cursor + nouveau point de spec + plan de travail consolidé
**Audit de référence :** 19/05/2026 (branche hugo-lucia, front frontend1.8)

---

## 1. Ce qui est solide (audit confirmé)

- Contrats de données (ConversationProgress, UIState, enums) : propres et conformes
- Modèles additifs sans casser P0 : LearnerThemeMemory, TrainerKnowledgeItem, ConversationQualitySignal
- 19/21 tests NR passants (2 échecs SQLite attendus)
- Endpoint set-posture présent et testé
- RLS middleware en place (non vérifié sous Postgres réel)

---

## 2. Écarts à corriger

| # | Écart | Niveau | Zone |
|---|-------|--------|------|
| 1 | Front calcule encore ses propres signaux P0 au lieu de consommer UIState pur | Bloquant | Front |
| 2 | Boutons Synthèse / Évaluation non branchés | Bloquant | Front |
| 3 | synthesisservice.py ne produit que synthesis_queued (stub) | Bloquant | Back |
| 4 | Injection LearnerThemeMemory absente de l'orchestrateur | Majeur | Back |
| 5 | Consolidation mémoire uniquement sur generate-trace, pas post-conversation normale | Majeur | Back |
| 6 | Snapshot qualité non déclenché post-session | Majeur | Back |
| 7 | Interface admin comptes incomplète (création/suppression apprenants, tuteurs) | Majeur | Front/Back |
| 8 | TutorConductProfiles non administrables (modes conduite codés en dur) | Nouveau | Front/Back |
| 9 | Tests Playwright absents | Majeur | Tests |
| 10 | RLS cross-tenant non vérifié sous Postgres | Bloquant | Infra |

---

## 3. Nouveau point de spec : TutorConductProfiles

### Pourquoi ce terme

Hugo a 3 postures de conduite de séance (DIAGNOSTIC, REFLECTIVE_AFEST, KNOWLEDGE_REVIEW).
Leurs paramètres comportementaux sont codés en dur dans tutorprofiles.py.

Terme retenu : TutorConductProfile (à distinguer de TutorPrompt qui personnalise le contexte textuel).

| Objet | Portée | Modifiable par | Contenu |
|---|---|---|---|
| TutorPrompt | Session / Groupe / Org | Tuteur, ORGADMIN | Texte de personnalisation contextuelle |
| TutorConductProfile | Posture / Org | ORGADMIN, SUPERADMIN | system_template, user_template, max_questions, forbidden_moves, closure_policy |

### Ce que l'administrateur pourra faire

- Lire les 3 profils de conduite de son organisation
- Modifier les paramètres comportementaux (system_template, règles, limites)
- Comparer profil organisation vs profil système par défaut
- Réinitialiser au profil système

### Règles invariantes

- TutorConductProfile ne modifie pas P0
- Il s'insère dans la couche de rendu prompt (build_posture_block)
- Héritage : profil organisation → profil système fallback → tutorprofiles.py statique

---

## 4. Plan de travail — 6 phases

| Phase | Objet | Durée |
|---|---|---|
| 1 | Corrections bloquantes front (P0 fallback, boutons Synthèse/Éval) sur frontend1.8 | 4-6 j |
| 2 | Synthèse/Évaluation réelles (LLM dans synthesisservice.py) | 3-5 j |
| 3 | Mémoire et observabilité (consolidation post-session, injection mémoire) | 3-5 j |
| 4 | TutorConductProfiles (modèle, resolver, endpoints, UI back-office) | 4-6 j |
| 5 | Interface admin comptes (ORGADMIN, tuteur) | 4-6 j |
| 6 | Tests Playwright + RLS Postgres | 2-3 j |

**Durée totale estimée : 20-31 jours ouvrés**

---

## 5. Point opérationnel critique

Toutes les modifications front s'appliquent sur la branche frontend1.8 (branche montrable ergonomiquement retravaillée), jamais sur main ni frontend. C'est une consigne explicite du fil qui doit être transmise à Cursor sans ambiguïté.

---

## 6. Question en suspens à arbitrer aujourd'hui

Gestion des comptes : qui peut créer des apprenants ?
- Option A : ORGADMIN seulement (plus propre, moins de surface d'erreur)
- Option B : Tuteur avec délégation explicite par ORGADMIN

Ce choix détermine le périmètre de l'interface tuteur.

