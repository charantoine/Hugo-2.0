# ADR — Exports org ORGADMIN vs SUPERADMIN (C9-CODE-03)

> Statut : **PROPOSÉ** — maintien comportement actuel recommandé (P1)  
> Date : 2026-06-18

---

## Contexte (RÉEL OBSERVÉ)

| Endpoint | Guard actuel | Rôles effectifs |
|----------|--------------|-----------------|
| `POST /exports/run/` | `is_admin_like` | ORGADMIN, SUPERADMIN |
| `POST /quality/qualiopi/evidence-bundle/` | `is_admin_like` | ORGADMIN, SUPERADMIN |
| D9bis / conversation-summary | `is_superadmin` | SUPERADMIN seul |

`is_admin_like` = `Role.ORGADMIN | Role.SUPERADMIN` (`access_control.py`).

Front : `isOrgAdminLike` aligné (smoke cluster 8 OK).

---

## CIBLE 2.0 (specs interface)

- ORGADMIN : exports org, bundle Qualiopi lite, pilotage org.
- SUPERADMIN : analytics techniques, D9bis, opérations plateforme.
- D2-M12 ouvert : frontière exports org vs superadmin technique.

---

## Options

### Option 1 — **Maintien** (recommandé P1)

Garder ExportRun + EvidenceBundle sur `is_admin_like`.

**Justification**

- RÉEL OBSERVÉ : ORGADMIN est le consommateur métier des exports Qualiopi lite (GroupView, pytest O1).
- SUPERADMIN déjà isolé sur D9bis / conversation-summary.
- Risque faible : les deux rôles sont org-scoped via JWT + RLS + filtres `organisation_id`.

### Option 2 — Restreindre un export technique au SUPERADMIN

Exemple : si un futur export « debug md » (G3-03) est ajouté → `is_superadmin` only.

**Micro-patch** (non appliqué) :

```python
# exports/views.py — exemple futur route debug uniquement
if not is_superadmin(request.user):
    return Response({"detail": "Forbidden."}, status=403)
```

ExportRun / bundle : **inchangés**.

---

## Décision recommandée

**Option 1** — pas de patch cluster 10.  
Documenter la frontière dans `matrice_role_visibilite_v2.md`.  
Revoir D2-M12 uniquement si un export **technique** doit être retiré à ORGADMIN.

Priorité : **P1** (non bloquant clôture vague runtime/OPS).

---

## Références

- `exports/views.py`, `quality/views.py`
- `ecarts — 90`, `ecarts — 100`, matrice cluster 2 § D2-M12
