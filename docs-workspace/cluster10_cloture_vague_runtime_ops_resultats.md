# Cluster 10 — Clôture vague runtime / OPS

> Exécution backlog C9-* + livrables DOC + ADR  
> Date : 2026-06-18

---

## 1. Synthèse exécution

| Item backlog | Statut cluster 10 | Résultat |
|--------------|-------------------|----------|
| C9-OPS-01 RLS rôle applicatif | **Exécuté** | Test `test_rls_cross_tenant_session_isolation_app_role` **PASS** |
| C9-OPS-02 Oracle Encoors auth | **Partiel** | Script ajusté ; exécution sans credentials → probes 404 uniquement |
| C9-OPS-03 Smoke memory-summary | **Exécuté** | `test_memory_summary_smoke.py` **PASS** |
| C9-DOC-01 à 04 | **Livré** | 4 fichiers docs-workspace |
| C9-CODE-02 / 03 | **ADR seulement** | Pas de patch code (décision CTO en attente) |

---

## 2. Fichiers créés / modifiés

### Code / tests / scripts

| Fichier | Action |
|---------|--------|
| `hugo_back/scripts/setup_rls_app_role.sql` | Créé — rôle `hugo_app_tenant_test` |
| `hugo_back/apps/hugo/tests/test_rls_postgres_minimal.py` | Étendu — test rôle applicatif |
| `hugo_back/apps/hugo/tests/test_memory_summary_smoke.py` | Créé — C9-OPS-03 |
| `hugo_back/scripts/encoors_oracle.py` | Ajusté — metadata_only query param, détail EVAL1 |

### Documentation

| Fichier | Item |
|---------|------|
| `contrat_api_memory_summary_v1.md` | C9-DOC-01 |
| `fiche_trace_exploitable_pivot_v1.md` | C9-DOC-02 |
| `matrice_role_visibilite_v2.md` | C9-DOC-03 |
| `note_frontiere_observabilite_base_vs_d9bis.md` | C9-DOC-04 |
| `adr_c9_code02_memory_summary_scope.md` | C9-CODE-02 |
| `adr_c9_code03_exports_orgadmin_superadmin.md` | C9-CODE-03 |
| `encoors_oracle_cluster10.generated.json` | Sortie oracle (non auth) |

### Plan / matrice

- `plan_documentation_cto_convergence_hugo.md` — § cluster 10
- `cluster2_matrice_runtime_vs_cible.md` — statut clôture vague

---

## 3. Blocs shell (reproduction)

### RLS rôle applicatif (C9-OPS-01)

```bash
cd ~/Desktop/Zone\ de\ travail\ Hugo/hugo_back
source .venv/bin/activate
DJANGO_SETTINGS_MODULE=config.settings.test python manage.py migrate --noinput
psql -U postgres -d hugo_poc_test -f scripts/setup_rls_app_role.sql
psql -U postgres -d hugo_poc_test -c "GRANT SELECT ON TABLE hugo_session, hugo_message, trace, evidence, export_run, learner_state TO hugo_app_tenant_test;"
pytest apps/hugo/tests/test_rls_postgres_minimal.py -q
```

Attendu : **4 passed, 2 skipped** (dont skip superuser SQL legacy).

### Smoke memory-summary (C9-OPS-03)

```bash
pytest apps/hugo/tests/test_memory_summary_smoke.py -q
```

Attendu : **1 passed**.

### Oracle Encoors (C9-OPS-02 — optionnel)

```bash
export ENCOORS_BASE_URL=https://hugoback.encoors.com
export ENCOORS_USERNAME="..."
export ENCOORS_PASSWORD="..."
export ENCOORS_ORACLE_OUT=~/Desktop/Zone\ de\ travail\ Hugo/docs-workspace/encoors_oracle_cluster10.generated.json
python scripts/encoors_oracle.py
```

Sans credentials : probes non auth seulement → **A_VÉRIFIER**, non bloquant.

---

## 4. Lien plan CTO

La vague runtime/OPS (clusters 8 → 10) couvre :

- Smokes UI navigateur (cluster 8)
- Consolidation contrats transverses (cluster 9)
- Exécution OPS critique + DOC + clôture (cluster 10)

**Couronne assumée pour vague suivante** : parité Encoors authentifiée, Option A memory-summary si arbitrage, dashboards, intercalaires, RAG vectoriel.

---

## 5. Prochaine sortie utile

Backlog final C10 (6 lignes max) dans le rapport utilisateur — voir section dédiée du livrable cluster 10.
