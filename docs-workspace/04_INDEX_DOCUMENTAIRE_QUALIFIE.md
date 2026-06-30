# Index documentaire qualifié — Workspace Hugo

**Workspace :** `/Users/machin/Desktop/Zone de travail Hugo`  
**Recensement :** `find … -name "*.md" -not -path "*/venv/*"` — **120 fichiers** hors venv (juin 2026, dont 11 dans `docs-workspace/`).  
**Indexés §2.1–2.8 :** **109 fichiers** hors `docs-workspace/` et `venv/`.  
**Indexés §2.9 :** **11 fichiers** `docs-workspace/` (bibliothèque canonique 00–10).  
**S'appuie sur :** `00_HIERARCHIE_DOCUMENTAIRE.md`, `01_CARTOGRAPHIE_WORKSPACE_REEL.md`

**Couche démo / runtime opérationnel :** docs `07`–`10` — complètent `02`/`03` ; doc `10` = inspection HTTP Encoors (flags env partiellement **VRIFIER**).

---

## 1. Mode d'emploi de l'index

### Colonnes

| Colonne | Signification |
|---------|---------------|
| **Chemin** | Relatif à la racine workspace |
| **Titre court** | Intitulé fonctionnel |
| **Rôle** | Fonction documentaire (pas le dossier physique) |
| **Statut** | IMPLÉMENTÉ / CRÉDIBLE / CIBLE / ARCHIVE / AMBIGU |
| **Fiabilité** | FORT / MOYEN / FAIBLE / DANGEREUX |
| **Action** | GARDER / RENOMMER / FUSIONNER / ARCHIVER / RÉÉCRIRE |
| **Danger principal** | Risque si lu seul comme vérité runtime |
| **Doublon de** | Entrée canonique ; `—` = canonique ; sinon chemin de référence |

### Règle de dédoublonnage

1. **Contenu identique** (`diff` vide) entre `hugo-main` et `hugo-hugolucia` → canonique **hugo-hugolucia** (sauf specs 1.8 actives : canonique **hugo-main/specs/**).
2. **Copie archivée** dans `specs-old/` → `Doublon de` pointe vers la version active ou la racine la plus récente.
3. **`hugo_back/docs/`** prime sur les copies racine pour les docs techniques moteur — mais chemins `backend/apps/…` obsolètes → fiabilité MOYEN.
4. **`docs-workspace/`** prime sur tout le reste pour l'état réel recalé (02, 03) et la préparation démo (07–09).
5. Ne pas compter une copie comme preuve indépendante.

---

## 2. Index par rôle documentaire

### 2.1 Doctrine structurante

| Chemin | Titre court | Rôle | Statut | Fiabilité | Action | Danger principal | Doublon de |
|--------|-------------|------|--------|-----------|--------|------------------|------------|
| `hugo-hugolucia/SPEC_POC_v1.5.md` | SPEC POC v1.5 | Contrat POC multi-tenant, périmètre Hugo | CIBLE | MOYEN | GARDER (canonique) | Décrit périmètre, pas implémentation | — |
| `hugo-main/SPEC_POC_v1.5.md` | SPEC POC v1.5 (copie) | Idem | CIBLE | MOYEN | ARCHIVER | Idem | `hugo-hugolucia/SPEC_POC_v1.5.md` |
| `hugo-hugolucia/SPEC Hugo 1.6.2 – Noyau d'état prioritaire et décision conversationnelle.md` | SPEC P0 / noyau 1.6.2 | Doctrine TurnState / décision cible | CIBLE | FAIBLE | ARCHIVER | **DANGEREUX** : pris pour état implémenté | — |
| `hugo-main/SPEC Hugo 1.6.2 – Noyau d'état prioritaire et décision conversationnelle.md` | SPEC 1.6.2 (copie) | Idem | CIBLE | FAIBLE | ARCHIVER | Idem | `hugo-hugolucia/SPEC Hugo 1.6.2…md` |
| `hugo-hugolucia/Synopsis-Hugo-v1.5.md` | Synopsis v1.5 | Vision produit Hugo + écosystème | CRÉDIBLE | MOYEN | GARDER | Mélange POC et POST-POC | — |
| `hugo-main/Synopsis-Hugo-v1.5.md` | Synopsis (copie) | Idem | CRÉDIBLE | MOYEN | ARCHIVER | Idem | `hugo-hugolucia/Synopsis-Hugo-v1.5.md` |
| `hugo-hugolucia/Personas-CasUsage1.5.md` | Personas v1.5 | Personas métier | CRÉDIBLE | MOYEN | GARDER | — | — |
| `hugo-main/Personas-CasUsage1.5.md` | Personas (copie) | Idem | CRÉDIBLE | MOYEN | ARCHIVER | — | `hugo-hugolucia/Personas-CasUsage1.5.md` |
| `hugo-hugolucia/specs-old/specs-old-1.6/SPEC_POC_v1.4.md` | SPEC POC v1.4 | Doctrine archivée | ARCHIVE | FAIBLE | ARCHIVER | Version obsolète | — |
| `hugo-main/specs-old-1.6/SPEC_POC_v1.4.md` | SPEC v1.4 (copie) | Idem | ARCHIVE | FAIBLE | ARCHIVER | — | `hugo-hugolucia/specs-old/specs-old-1.6/SPEC_POC_v1.4.md` |
| `hugo-hugolucia/specs-old/specs-old-1.6/Synopsis-Hugo-v1.4-Non-Technique.md` | Synopsis v1.4 | Archive vision | ARCHIVE | FAIBLE | ARCHIVER | — | — |
| `hugo-main/specs-old-1.6/Synopsis-Hugo-v1.4-Non-Technique.md` | Synopsis v1.4 (copie) | Idem | ARCHIVE | FAIBLE | ARCHIVER | — | `hugo-hugolucia/specs-old/specs-old-1.6/Synopsis-Hugo-v1.4-Non-Technique.md` |
| `hugo-hugolucia/specs-old/specs-old-1.6/Personas-CasUsage1.4.md` | Personas v1.4 | Archive personas | ARCHIVE | FAIBLE | ARCHIVER | — | — |
| `hugo-main/specs-old-1.6/Personas-CasUsage1.4.md` | Personas v1.4 (copie) | Idem | ARCHIVE | FAIBLE | ARCHIVER | — | `hugo-hugolucia/specs-old/specs-old-1.6/Personas-CasUsage1.4.md` |

---

### 2.2 État moteur / technique P0

| Chemin | Titre court | Rôle | Statut | Fiabilité | Action | Danger principal | Doublon de |
|--------|-------------|------|--------|-----------|--------|------------------|------------|
| `docs-workspace/02_ETAT_MOTEUR_REEL.md` | État moteur recalé | Vérité moteur `hugo_back` | IMPLÉMENTÉ | FORT | GARDER | — | — |
| `hugo_back/docs/p0_description_technique_actuelle.md` | P0 technique actuel | Description pipeline P0 | CRÉDIBLE | MOYEN | RÉÉCRIRE → obsolète après 02 | Chemins `backend/apps/…` | — |
| `hugo-hugolucia/p0_description_technique_actuelle.md` | P0 technique (copie racine) | Idem | CRÉDIBLE | MOYEN | FUSIONNER / ARCHIVER | Idem | `hugo_back/docs/p0_description_technique_actuelle.md` |
| `hugo-main/p0_description_technique_actuelle.md` | P0 technique (copie) | Idem | CRÉDIBLE | MOYEN | ARCHIVER | Idem | `hugo_back/docs/p0_description_technique_actuelle.md` |
| `hugo-hugolucia/p0_description_technique_actuelle_mise_a_jour.md` | P0 technique MAJ | Mise à jour P0 | CRÉDIBLE | MOYEN | FUSIONNER | Peut contredire 02 | — |
| `hugo-main/p0_description_technique_actuelle_mise_a_jour.md` | P0 MAJ (copie) | Idem | CRÉDIBLE | MOYEN | ARCHIVER | — | `hugo-hugolucia/p0_description_technique_actuelle_mise_a_jour.md` |
| `hugo-main/specs/p0_description_technique_actuelle_mise_a_jour.md` | P0 MAJ (copie specs) | Idem | CRÉDIBLE | MOYEN | ARCHIVER | — | `hugo-hugolucia/p0_description_technique_actuelle_mise_a_jour.md` |
| `hugo-hugolucia/specs-old/specs-old-1.8/p0_description_technique_actuelle_mise_a_jour.md` | P0 MAJ (archive 1.8) | Idem | ARCHIVE | FAIBLE | ARCHIVER | — | `hugo-hugolucia/p0_description_technique_actuelle_mise_a_jour.md` |
| `hugo_back/docs/p0_guide_testeurs_pedagogiques.md` | Guide testeurs P0 | Usage testeurs pédagogiques | CRÉDIBLE | MOYEN | GARDER | — | — |
| `hugo_back/docs/referential_import_mvp_activities_tasks.md` | Import référentiel MVP | Import activités/tâches | IMPLÉMENTÉ | FORT | GARDER | — | — |
| `hugo_back/README.md` | README backend | Setup `hugo_back` | CRÉDIBLE | MOYEN | RÉÉCRIRE | Réf. SPEC v1.4, lien monorepos flou | — |
| `hugo_back/apps/referentials/fixtures/README.md` | README fixtures RNCP | Fixture import référentiel | CRÉDIBLE | FORT | GARDER | — | — |

---

### 2.3 État produit / 1.8

| Chemin | Titre court | Rôle | Statut | Fiabilité | Action | Danger principal | Doublon de |
|--------|-------------|------|--------|-----------|--------|------------------|------------|
| `docs-workspace/03_ETAT_PRODUIT_REEL.md` | État produit recalé | Vérité prod `frontend_1.8` hugolucia | IMPLÉMENTÉ | FORT | GARDER | — | — |
| `hugo-main/specs/hugo-1.8-spec-finale.md` | Spec finale 1.8 | Spec prod montrable 1.8 (active) | CIBLE | MOYEN | ARCHIVER | Décrit cible, pas hugolucia à jour | — |
| `hugo-hugolucia/specs-old/specs-old-1.8/hugo-1.8-spec-finale.md` | Spec finale 1.8 (archive) | Copie archivée | ARCHIVE | FAIBLE | ARCHIVER | — | `hugo-main/specs/hugo-1.8-spec-finale.md` |
| `hugo-main/specs/Hugo 1.8 – branche prod montrable V1.md` | Branche prod montrable V1 | Vision livraison 1.8 | CIBLE | MOYEN | ARCHIVER | — | — |
| `hugo-hugolucia/specs-old/specs-old-1.8/Hugo 1.8 – branche prod montrable V1.md` | Branche prod (archive) | Copie | ARCHIVE | FAIBLE | ARCHIVER | — | `hugo-main/specs/Hugo 1.8 – branche prod montrable V1.md` |
| `hugo-main/specs/Hugo 1.8 — Spec exécutable pour branche prod montr.md` | Spec exécutable 1.8 | Tickets / exécution 1.8 | CIBLE | MOYEN | ARCHIVER | Backlog historique | — |
| `hugo-hugolucia/specs-old/specs-old-1.8/Hugo 1.8 — Spec exécutable…md` | Spec exéc. (archive) | Copie | ARCHIVE | FAIBLE | ARCHIVER | — | `hugo-main/specs/Hugo 1.8 — Spec exécutable…md` |
| `hugo-main/specs/hugo-1.8-adr.md` | ADR 1.8 | Décisions architecture prod | CIBLE | MOYEN | GARDER (archive) | — | — |
| `hugo-hugolucia/specs-old/specs-old-1.8/hugo-1.8-adr.md` | ADR 1.8 (archive) | Copie | ARCHIVE | FAIBLE | ARCHIVER | — | `hugo-main/specs/hugo-1.8-adr.md` |
| `hugo-main/specs/hugo-1.8-checklist-tickets.md` | Checklist tickets 1.8 | Backlog 1.8 | CIBLE | FAIBLE | ARCHIVER | Tickets datés | — |
| `hugo-hugolucia/specs-old/specs-old-1.8/hugo-1.8-checklist-tickets.md` | Checklist (archive) | Copie | ARCHIVE | FAIBLE | ARCHIVER | — | `hugo-main/specs/hugo-1.8-checklist-tickets.md` |
| `hugo-main/specs/hugo-1.8-prompt-cursor-cto-ready.md` | Prompt Cursor CTO 1.8 | Prompt historique livraison | ARCHIVE | FAIBLE | ARCHIVER | — | — |
| `hugo-hugolucia/specs-old/specs-old-1.8/hugo-1.8-prompt-cursor-cto-ready.md` | Prompt CTO (archive) | Copie | ARCHIVE | FAIBLE | ARCHIVER | — | `hugo-main/specs/hugo-1.8-prompt-cursor-cto-ready.md` |
| `hugo-hugolucia/frontend_1.8/README.md` | README frontend 1.8 | Run Vite / npm test | IMPLÉMENTÉ | FORT | GARDER | — | — |
| `hugo-main/frontend_1.8/README.md` | README 1.8 (copie) | Idem | IMPLÉMENTÉ | FORT | ARCHIVER | — | `hugo-hugolucia/frontend_1.8/README.md` |
| `hugo-hugolucia/frontend/README.md` | README frontend testeur | Run front testeur | IMPLÉMENTÉ | FORT | GARDER | — | — |
| `hugo-main/frontend/README.md` | README testeur (copie) | Idem | IMPLÉMENTÉ | FORT | ARCHIVER | — | `hugo-hugolucia/frontend/README.md` |

---

### 2.4 Cible 1.9

| Chemin | Titre court | Rôle | Statut | Fiabilité | Action | Danger principal | Doublon de |
|--------|-------------|------|--------|-----------|--------|------------------|------------|
| `hugo-hugolucia/specs/MEMO_CTO_Hugo1.9_v2.md` | Mémo CTO 1.9 v2 | Bilan écarts / plan 1.9 | CIBLE | MOYEN | RÉÉCRIRE → alimenter 05 | **DANGEREUX** : écarts partiellement obsolètes vs `hugo_back` | — |
| `hugo-hugolucia/specs/SPEC_IMPLEMENTATION_COMPLETE_v2.md` | Spec implémentation 1.9 | Spec globale 1.9 | CIBLE | FAIBLE | ARCHIVER | Spec seule | — |
| `hugo-hugolucia/specs/LOT7_moteur_evaluation_FINAL.md` | LOT7 évaluation | Moteur évaluation 1.9 | CIBLE | MOYEN | ARCHIVER | — | — |
| `hugo-hugolucia/specs/SPEC_TUTORCONDUCTPROFILES.md` | Spec ConductProfiles | Cible admin profils conduite | CIBLE | MOYEN | GARDER (cible) | Back partiellement implémenté | — |
| `hugo-hugolucia/specs/SPEC_ADMIN_COMPTES_v2.md` | Spec admin comptes | Admin ORGADMIN / comptes | CIBLE | FAIBLE | ARCHIVER | — | — |
| `hugo-hugolucia/specs/MATRICE_CRITERES_AUDITABLES_v2.md` | Matrice critères audit | Critères audit 1.9 | CIBLE | MOYEN | GARDER | — | — |
| `hugo-hugolucia/specs/PROMPT_CURSOR_AUDIT_v2.md` | Prompt audit v2 | Prompt Cursor audit | ARCHIVE | FAIBLE | ARCHIVER | — | — |
| `hugo-hugolucia/specs-old/specs-old-1.9/LOT0_contrats_fondations(2).md` | LOT0 fondations | Contrats fondations 1.9 | CIBLE | FAIBLE | ARCHIVER | — | — |
| `hugo-hugolucia/specs-old/specs-old-1.9/LOT1_progression_conversationnelle V1.9.md` | LOT1 progression | Progression conversationnelle | CIBLE | FAIBLE | ARCHIVER | — | — |
| `hugo-hugolucia/specs-old/specs-old-1.9/LOT2_adaptateur_ui1.9.md` | LOT2 adaptateur UI | Contrat UI / ui-state | CIBLE | MOYEN | ARCHIVER | Utile contexte, pas vérité | — |
| `hugo-hugolucia/specs-old/specs-old-1.9/LOT3_modes_postures.md` | LOT3 postures | Modes / postures | CIBLE | FAIBLE | ARCHIVER | — | — |
| `hugo-hugolucia/specs-old/specs-old-1.9/LOT4_memoire_inter_session.md` | LOT4 mémoire | Mémoire inter-session | CIBLE | MOYEN | ARCHIVER | **DANGEREUX** : injection orchestrateur | — |
| `hugo-hugolucia/specs-old/specs-old-1.9/LOT5_base_connaissances_formateur.md` | LOT5 base formateur | Trainer knowledge | CIBLE | MOYEN | ARCHIVER | Partiellement implémenté | — |
| `hugo-hugolucia/specs-old/specs-old-1.9/LOT6_observabilite_cohorte.md` | LOT6 observabilité | Analytics cohorte | CIBLE | MOYEN | ARCHIVER | — | — |
| `hugo-hugolucia/specs-old/specs-old-1.9/README_CURSOR.md` | README Cursor 1.9 | Index pack LOTs | ARCHIVE | FAIBLE | ARCHIVER | — | — |
| `hugo-hugolucia/specs-old/specs-old-1.9/rapport_audit_hugo_1_9_2026-05-19.md` | Rapport audit 1.9 | Audit mai 2026 | ARCHIVE | MOYEN | ARCHIVER | **DANGEREUX** : daté | — |
| `hugo-hugolucia/specs-old/specs-old-1.9/executive_summary_audit_hugo_1_9_2026-05-20.md` | Executive summary 1.9 | Synthèse audit | ARCHIVE | MOYEN | ARCHIVER | — | — |
| `hugo-hugolucia/specs-old/specs_audit_1.9/rapport_audit_hugo_1_9_2026-05-19.md` | Rapport audit (pack) | Copie pack audit | ARCHIVE | MOYEN | ARCHIVER | — | `specs-old/specs-old-1.9/rapport_audit_hugo_1_9_2026-05-19.md` |
| `hugo-hugolucia/specs-old/specs_audit_1.9/executive_summary_audit_hugo_1_9_2026-05-20.md` | Executive summary (pack) | Copie | ARCHIVE | MOYEN | ARCHIVER | — | `specs-old/specs-old-1.9/executive_summary…md` |
| `hugo-hugolucia/specs-old/specs_audit_1.9/CONTEXTUALISATION_COMPLETE_HUGO_1_9.md` | Contextualisation 1.9 | Contexte audit Cursor | ARCHIVE | MOYEN | ARCHIVER | — | — |
| `hugo-hugolucia/specs-old/specs_audit_1.9/CHECKLIST_AUDIT_BACKEND.md` | Checklist audit back | Grille audit backend | ARCHIVE | MOYEN | ARCHIVER | — | — |
| `hugo-hugolucia/specs-old/specs_audit_1.9/CHECKLIST_AUDIT_FRONTEND.md` | Checklist audit front | Grille audit frontend | ARCHIVE | MOYEN | ARCHIVER | — | — |
| `hugo-hugolucia/specs-old/specs_audit_1.9/HORS_PERIMETRE_GAPS_ROADMAP.md` | Hors périmètre / gaps | Roadmap gaps | CIBLE | MOYEN | ARCHIVER | — | — |
| `hugo-hugolucia/specs-old/specs_audit_1.9/PLAN_TESTS_API_CHROMIUM.md` | Plan tests Chromium | E2E prévu | CIBLE | FAIBLE | ARCHIVER | Non implémenté | — |
| `hugo-hugolucia/specs-old/specs_audit_1.9/PROMPT_CURSOR_AUDIT_LONG.md` | Prompt audit long | Prompt Cursor | ARCHIVE | FAIBLE | ARCHIVER | — | — |
| `hugo-hugolucia/specs-old/specs_audit_1.9/README_PACK_CURSOR.md` | README pack audit | Index pack | ARCHIVE | FAIBLE | ARCHIVER | — | — |

---

### 2.5 Déploiement / infra

| Chemin | Titre court | Rôle | Statut | Fiabilité | Action | Danger principal | Doublon de |
|--------|-------------|------|--------|-----------|--------|------------------|------------|
| `hugo-hugolucia/docs/DEPLOY_S0.md` | Déploiement S0 | Procédure infra S0 | CRÉDIBLE | MOYEN | RÉÉCRIRE | Suppose `backend/` peuplé | — |
| `hugo-main/docs/DEPLOY_S0.md` | DEPLOY S0 (copie) | Idem | CRÉDIBLE | MOYEN | ARCHIVER | Idem | `hugo-hugolucia/docs/DEPLOY_S0.md` |
| `hugo-hugolucia/docs/DEPLOY_VM.md` | Déploiement VM | Procédure VM | CRÉDIBLE | MOYEN | GARDER | Idem | — |
| `hugo-main/docs/DEPLOY_VM.md` | DEPLOY VM (copie) | Idem | CRÉDIBLE | MOYEN | ARCHIVER | — | `hugo-hugolucia/docs/DEPLOY_VM.md` |
| `hugo-hugolucia/docs/RAG_GROUP_LIBRARY.md` | RAG bibliothèque groupe | Doc technique RAG / library | CRÉDIBLE | MOYEN | GARDER | Chemins `backend/` | — |
| `hugo-main/docs/RAG_GROUP_LIBRARY.md` | RAG group (copie) | Idem | CRÉDIBLE | MOYEN | ARCHIVER | — | `hugo-hugolucia/docs/RAG_GROUP_LIBRARY.md` |
| `hugo-hugolucia/docs/TUTOR_PROMPT_PLACEHOLDERS.md` | Placeholders TutorPrompt | Doc placeholders prompts | CRÉDIBLE | MOYEN | GARDER | — | — |
| `hugo-main/docs/TUTOR_PROMPT_PLACEHOLDERS.md` | Placeholders (copie) | Idem | CRÉDIBLE | MOYEN | ARCHIVER | — | `hugo-hugolucia/docs/TUTOR_PROMPT_PLACEHOLDERS.md` |
| `hugo-hugolucia/specs-old/specs-old-1.7/note déploiement 1.7.md` | Note déploiement 1.7 | Archive deploy 1.7 | ARCHIVE | FAIBLE | ARCHIVER | — | — |
| `hugo-main/specs-old-1.7/note déploiement 1.7.md` | Note deploy 1.7 (copie) | Idem | ARCHIVE | FAIBLE | ARCHIVER | — | `hugo-hugolucia/specs-old/specs-old-1.7/note déploiement 1.7.md` |

---

### 2.6 Stratégie / marché / Hugo & Cie (extension)

| Chemin | Titre court | Rôle | Statut | Fiabilité | Action | Danger principal | Doublon de |
|--------|-------------|------|--------|-----------|--------|------------------|------------|
| `hugo-hugolucia/Integrations-LMS-SIRH-v1.5.md` | Intégrations LMS/SIRH | Extension POST-POC | CIBLE | MOYEN | GARDER | Hors périmètre POC actuel | — |
| `hugo-main/Integrations-LMS-SIRH-v1.5.md` | Intégrations (copie) | Idem | CIBLE | MOYEN | ARCHIVER | — | `hugo-hugolucia/Integrations-LMS-SIRH-v1.5.md` |
| `hugo-hugolucia/specs-old/specs-old-1.6/Integrations-LMS-SIRH-v1.4.md` | Intégrations v1.4 | Archive | ARCHIVE | FAIBLE | ARCHIVER | — | — |
| `hugo-main/specs-old-1.6/Integrations-LMS-SIRH-v1.4.md` | Intégrations v1.4 (copie) | Idem | ARCHIVE | FAIBLE | ARCHIVER | — | `hugo-hugolucia/specs-old/specs-old-1.6/Integrations-LMS-SIRH-v1.4.md` |

*Vision Hugo & Cie (Julia, Felix, Hector, Jérémy) : principalement dans `Synopsis-Hugo-v1.5.md` — extension, pas base de vérité.*

---

### 2.7 Corpus données (RAG Melec)

9 fichiers identiques × 2 copies. Canonique : **hugo-hugolucia/RAG Melec/**.

| Chemin | Titre court | Rôle | Statut | Fiabilité | Action | Danger principal | Doublon de |
|--------|-------------|------|--------|-----------|--------|------------------|------------|
| `hugo-hugolucia/RAG Melec/Base_BacProMELEC_cartographie-globale-A1-A5_Sxx.yaml.md` | Cartographie globale MELEC | Données corpus démo | CRÉDIBLE | FORT | GARDER | Données, pas runtime | — |
| `hugo-main/RAG Melec/Base_BacProMELEC_cartographie-globale-A1-A5_Sxx.yaml.md` | Cartographie (copie) | Idem | CRÉDIBLE | FORT | ARCHIVER | — | `hugo-hugolucia/RAG Melec/…cartographie…` |
| `hugo-hugolucia/RAG Melec/Base_BacProMELEC_index-difficultes-transversales.yaml.md` | Index difficultés | Données corpus | CRÉDIBLE | FORT | GARDER | — | — |
| `hugo-main/RAG Melec/Base_BacProMELEC_index-difficultes-transversales.yaml.md` | Index diff. (copie) | Idem | CRÉDIBLE | FORT | ARCHIVER | — | `hugo-hugolucia/RAG Melec/…index-difficultes…` |
| `hugo-hugolucia/RAG Melec/Base_BacProMELEC_meta-usage_situations_S01-a-S30.yaml.md` | Meta usage situations | Données corpus | CRÉDIBLE | FORT | GARDER | — | — |
| `hugo-main/RAG Melec/Base_BacProMELEC_meta-usage_situations_S01-a-S30.yaml.md` | Meta usage (copie) | Idem | CRÉDIBLE | FORT | ARCHIVER | — | `hugo-hugolucia/RAG Melec/…meta-usage…` |
| `hugo-hugolucia/RAG Melec/Base_BacProMELEC_preparation_S01-a-S06.yaml.md` | Préparation S01–S06 | Données corpus | CRÉDIBLE | FORT | GARDER | — | — |
| `hugo-main/RAG Melec/Base_BacProMELEC_preparation_S01-a-S06.yaml.md` | Prep S01–S06 (copie) | Idem | CRÉDIBLE | FORT | ARCHIVER | — | `hugo-hugolucia/RAG Melec/…S01-a-S06…` |
| `hugo-hugolucia/RAG Melec/Base_BacProMELEC_preparation_S07-a-S012.yaml.md` | Préparation S07–S12 | Données corpus | CRÉDIBLE | FORT | GARDER | — | — |
| `hugo-main/RAG Melec/Base_BacProMELEC_preparation_S07-a-S012.yaml.md` | Prep S07–S12 (copie) | Idem | CRÉDIBLE | FORT | ARCHIVER | — | `hugo-hugolucia/RAG Melec/…S07-a-S012…` |
| `hugo-hugolucia/RAG Melec/Base_BacProMELEC_preparation_S13-a-S018.md` | Préparation S13–S18 | Données corpus | CRÉDIBLE | FORT | GARDER | — | — |
| `hugo-main/RAG Melec/Base_BacProMELEC_preparation_S13-a-S018.md` | Prep S13–S18 (copie) | Idem | CRÉDIBLE | FORT | ARCHIVER | — | `hugo-hugolucia/RAG Melec/…S13-a-S018.md` |
| `hugo-hugolucia/RAG Melec/Base_BacProMELEC_preparation_S19-a-S24.md` | Préparation S19–S24 | Données corpus | CRÉDIBLE | FORT | GARDER | — | — |
| `hugo-main/RAG Melec/Base_BacProMELEC_preparation_S19-a-S24.md` | Prep S19–S24 (copie) | Idem | CRÉDIBLE | FORT | ARCHIVER | — | `hugo-hugolucia/RAG Melec/…S19-a-S24.md` |
| `hugo-hugolucia/RAG Melec/Base_BacProMELEC_preparation_S25-a-S30.md` | Préparation S25–S30 | Données corpus | CRÉDIBLE | FORT | GARDER | — | — |
| `hugo-main/RAG Melec/Base_BacProMELEC_preparation_S25-a-S30.md` | Prep S25–S30 (copie) | Idem | CRÉDIBLE | FORT | ARCHIVER | — | `hugo-hugolucia/RAG Melec/…S25-a-S30.md` |
| `hugo-hugolucia/RAG Melec/Base_BacProMELEC_profils-RAG_par-bloc.yaml.md` | Profils RAG par bloc | Données corpus | CRÉDIBLE | FORT | GARDER | — | — |
| `hugo-main/RAG Melec/Base_BacProMELEC_profils-RAG_par-bloc.yaml.md` | Profils RAG (copie) | Idem | CRÉDIBLE | FORT | ARCHIVER | — | `hugo-hugolucia/RAG Melec/…profils-RAG…` |

---

### 2.8 Archives / audits / prompts Cursor

| Chemin | Titre court | Rôle | Statut | Fiabilité | Action | Danger principal | Doublon de |
|--------|-------------|------|--------|-----------|--------|------------------|------------|
| `hugo-hugolucia/message_cursor_modif_P0_Hugo_optimise.md` | Prompt Cursor P0 | Prompt historique refactor P0 | ARCHIVE | FAIBLE | ARCHIVER | **DANGEREUX** : instructions obsolètes | — |
| `hugo-main/message_cursor_modif_P0_Hugo_optimise.md` | Prompt P0 (copie) | Idem | ARCHIVE | FAIBLE | ARCHIVER | Idem | `hugo-hugolucia/message_cursor_modif_P0_Hugo_optimise.md` |
| `hugo-hugolucia/specs-old/specs-old-1.7/CURSOR INSTRUCTION 1 — Refactor P0…V3.md` | Instruction Cursor 1.7 #1 | Archive refactor P0 | ARCHIVE | FAIBLE | ARCHIVER | **DANGEREUX** | — |
| `hugo-main/specs-old-1.7/CURSOR INSTRUCTION 1 — Refactor P0…V3.md` | Instr. 1.7 #1 (copie) | Idem | ARCHIVE | FAIBLE | ARCHIVER | — | `hugo-hugolucia/specs-old/specs-old-1.7/CURSOR INSTRUCTION 1…` |
| `hugo-hugolucia/specs-old/specs-old-1.7/CURSOR INSTRUCTION 2 — Contrats d'interface 1.7…V3.md` | Instruction Cursor 1.7 #2 | Archive contrats 1.7 | ARCHIVE | FAIBLE | ARCHIVER | — | — |
| `hugo-main/specs-old-1.7/CURSOR INSTRUCTION 2 — Contrats d'interface 1.7…V3.md` | Instr. 1.7 #2 (copie) | Idem | ARCHIVE | FAIBLE | ARCHIVER | — | `hugo-hugolucia/specs-old/specs-old-1.7/CURSOR INSTRUCTION 2…` |
| `hugo-hugolucia/docs/rapport_audit_dossier_probatoire_2026-05-18.md` | Audit probatoire | Rapport juridique / probatoire | ARCHIVE | MOYEN | ARCHIVER | Daté mai 2026 | — |
| `hugo-hugolucia/docs/rapport_audit_dossier_probatoire_depot_e-soleau_2026-05-18.md` | Audit e-Soleau | Dépôt probatoire | ARCHIVE | MOYEN | ARCHIVER | — | — |
| `hugo-hugolucia/README.md` | README monorepo | `# hugo_poc` seul | AMBIGU | FAIBLE | RÉÉCRIRE | Inutilisable seul | — |
| `hugo-main/README.md` | README (copie) | Idem | AMBIGU | FAIBLE | ARCHIVER | — | `hugo-hugolucia/README.md` |

*Fichiers non-.md présents mais hors index : `*.docx` (2×2), `shell-heredoc-v1.5.txt` (2×1) — rapports comité / présentations, à traiter hors Space technique.*

---

### 2.9 Bibliothèque docs-workspace (canonique)

| Chemin | Titre court | Rôle | Statut | Fiabilité | Action | Danger principal | Doublon de |
|--------|-------------|------|--------|-----------|--------|------------------|------------|
| `docs-workspace/00_HIERARCHIE_DOCUMENTAIRE.md` | Hiérarchie documentaire | Règles de lecture / vérité | IMPLÉMENTÉ | FORT | GARDER | — | — |
| `docs-workspace/01_CARTOGRAPHIE_WORKSPACE_REEL.md` | Cartographie workspace | Géographie dépôt | IMPLÉMENTÉ | FORT | GARDER | — | — |
| `docs-workspace/02_ETAT_MOTEUR_REEL.md` | État moteur réel | Vérité `hugo_back` | IMPLÉMENTÉ | FORT | GARDER | Remplace `p0_description*` pour le moteur | — |
| `docs-workspace/03_ETAT_PRODUIT_REEL.md` | État produit réel | Vérité `frontend_1.8` hugolucia | IMPLÉMENTÉ | FORT | GARDER | Remplace specs 1.8 pour le produit | — |
| `docs-workspace/04_INDEX_DOCUMENTAIRE_QUALIFIE.md` | Index documentaire | Ce document | IMPLÉMENTÉ | FORT | GARDER | — | — |
| `docs-workspace/05_ECARTS_DOC_CODE_PRODUIT.md` | Écarts doc / code / produit | Divergences factuelles | IMPLÉMENTÉ | FORT | GARDER | MEMO CTO obsolète partiellement | — |
| `docs-workspace/06_PREPARATION_CIBLE_1_9.md` | Préparation cible 1.9 | Garde-fous avant backlog 1.9 | IMPLÉMENTÉ | FORT | GARDER | — | — |
| `docs-workspace/07_RUNTIME_DEMO_REFERENCE.md` | Runtime démo | Baselines stack A/B/C | IMPLÉMENTÉ | FORT | GARDER | Compléter par doc 10 pour Encoors | — |
| `docs-workspace/08_FLAGS_ET_ENVIRONNEMENT_DEMO.md` | Flags et env démo | Reproductibilité démo | IMPLÉMENTÉ | FORT | GARDER | — | — |
| `docs-workspace/09_PARCOURS_DEMO_ET_SCENARIOS.md` | Parcours démo | Scénarios apprenant / testeur | IMPLÉMENTÉ | FORT | GARDER | — | — |
| `docs-workspace/10_FICHE_RUNTIME_PROD_ENCOORS.md` | Fiche runtime Encoors | Inspection HTTP prod distante | IMPLÉMENTÉ | MOYEN | GARDER | Flags env non lus ; CORS localhost | — |

| `docs-workspace/11_FICHE_COMPTES_ET_DONNEES_DEMO.md` | Fiche comptes démo | Comptes, orgs, bootstrap, confiance | IMPLÉMENTÉ | FORT | GARDER | — | — |

---

## 3. Synthèse quantitative

### Par dossier racine (tous .md hors venv)

| Dossier | Fichiers .md |
|---------|--------------|
| `docs-workspace/` | 11 |
| `hugo-hugolucia/` | 66 |
| `hugo-main/` | 38 |
| `hugo_back/` | 5 |
| **Total** | **120** |

### Par rôle documentaire (entrées indexées §2)

| Rôle | Entrées (lignes tableau) | Canoniques ~ | Copies ~ |
|------|---------------------------|--------------|----------|
| 2.1 Doctrine | 14 | 7 | 7 |
| 2.2 Moteur / P0 | 12 | 6 | 6 |
| 2.3 Produit / 1.8 | 17 | 9 | 8 |
| 2.4 Cible 1.9 | 26 | 26 | 0* |
| 2.5 Déploiement | 10 | 5 | 5 |
| 2.6 Hugo & Cie | 4 | 2 | 2 |
| 2.7 RAG Melec | 18 | 9 | 9 |
| 2.8 Archives / prompts | 10 | 6 | 4 |
| 2.9 docs-workspace | 11 | 11 | 0 |
| **Total indexé** | **122** | **~81** | **~41** |

\*Dont doublons internes hugolucia (rapport audit ×2, executive summary ×2).

### Doublons

- **Paires main ↔ hugolucia identiques :** ~35 fichiers (racine, docs, RAG Melec, specs-old-1.6/1.7, message_cursor, README).
- **Specs 1.8 :** 7 fichiers actifs `hugo-main/specs/` + 7 copies `hugo-hugolucia/specs-old/specs-old-1.8/`.
- **p0_description* :** jusqu'à 4 emplacements pour la même famille de docs.

### Top 10 docs dangereux si lus seuls

| # | Chemin | Danger |
|---|--------|--------|
| 1 | `hugo-hugolucia/SPEC Hugo 1.6.2…md` | Doctrine P0 prise pour implémentation |
| 2 | `hugo-hugolucia/specs/MEMO_CTO_Hugo1.9_v2.md` | Écarts listés partiellement obsolètes |
| 3 | `hugo-hugolucia/specs-old/specs_audit_1.9/rapport_audit_hugo_1_9_2026-05-19.md` | État mai 2026 comme actuel |
| 4 | `hugo-hugolucia/message_cursor_modif_P0_Hugo_optimise.md` | Instructions Cursor historiques |
| 5 | `hugo-hugolucia/p0_description_technique_actuelle.md` | Chemins obsolètes, peut contredire 02 |
| 6 | `hugo-hugolucia/specs-old/specs-old-1.9/LOT4_memoire_inter_session.md` | Affirme comportements non vérifiés |
| 7 | `hugo-hugolucia/docs/DEPLOY_S0.md` | Stack complète alors que `backend/` vide |
| 8 | `hugo-main/specs/hugo-1.8-spec-finale.md` | Cible 1.8 ≠ prod hugolucia actuelle |
| 9 | `hugo-hugolucia/specs/SPEC_IMPLEMENTATION_COMPLETE_v2.md` | Spec globale 1.9 sans recoupement code |
| 10 | `hugo-hugolucia/README.md` | Quasi vide, masque l'absence de guide |

---

## 4. Recommandations de consolidation

### Fusions / archivages prioritaires (sans exécuter)

1. **Archiver toutes les copies `hugo-main/`** dont le canonique est `hugo-hugolucia/` (35+ fichiers) — ou supprimer du Space Perplexity les chemins `hugo-main/` redondants.
2. **Fusionner `p0_description_technique_actuelle*`** → remplacé par `02_ETAT_MOTEUR_REEL.md` ; archiver les 4 emplacements.
3. **Archiver `hugo-hugolucia/specs-old/specs-old-1.8/`** entier — doublon de `hugo-main/specs/`.
4. **Archiver pack `specs_audit_1.9/`** — garder une seule copie des rapports (déjà dans `specs-old-1.9/`).
5. **Archiver prompts Cursor** (`message_cursor_modif_*`, `CURSOR INSTRUCTION*`, `PROMPT_CURSOR_*`).
6. **Une seule copie `RAG Melec/`** — conserver hugolucia.
7. **Réécrire README** racine monorepo + `hugo_back/README.md` avec renvoi vers `docs-workspace/`.

### Obsolescence après docs-workspace 02–09

| Document(s) | Remplacé par |
|-------------|--------------|
| `p0_description_technique_actuelle*.md` (tous emplacements) | `02_ETAT_MOTEUR_REEL.md` |
| Specs 1.8 actives (`hugo-main/specs/hugo-1.8-*`) | `03_ETAT_PRODUIT_REEL.md` |
| `MEMO_CTO_Hugo1.9_v2.md` (comme vérité écarts) | `05_ECARTS_DOC_CODE_PRODUIT.md` |
| Audits mai 2026 (comme état actuel) | `05_ECARTS` + `06_PREPARATION` |
| `SPEC Hugo 1.6.2` (comme état P0) | `02_ETAT_MOTEUR_REEL.md` |
| Guides démo / deploy implicites (README, `DEPLOY_S0` seul) | `07_RUNTIME_DEMO_REFERENCE.md` + `09_PARCOURS_DEMO_ET_SCENARIOS.md` |
| Listes flags env éparpillées | `08_FLAGS_ET_ENVIRONNEMENT_DEMO.md` |
| État API distante « non inspectée » (générique) | `10_FICHE_RUNTIME_PROD_ENCOORS.md` (inspection datée ; flags env partiels) |

---

## 5. Renvoi

- **Écarts doc / code / produit :** `05_ECARTS_DOC_CODE_PRODUIT.md`
- **Préparation cible 1.9 :** `06_PREPARATION_CIBLE_1_9.md`
- **Démo / runtime :** `07_RUNTIME_DEMO_REFERENCE.md`, `08_FLAGS_ET_ENVIRONNEMENT_DEMO.md`, `09_PARCOURS_DEMO_ET_SCENARIOS.md`, `10_FICHE_RUNTIME_PROD_ENCOORS.md`
- **Règles de lecture :** `00_HIERARCHIE_DOCUMENTAIRE.md`

---

*Document 04 — index recalé juin 2026. 109 .md hors venv et docs-workspace ; 120 .md hors venv au total (11 en docs-workspace).*
