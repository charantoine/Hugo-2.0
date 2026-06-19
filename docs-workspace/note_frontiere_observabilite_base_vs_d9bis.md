# Note — frontière observabilité base vs D9bis (C9-DOC-04)

> Domaine 80 (+ 100 canal technique)  
> Date : 2026-06-18

---

## RÉEL OBSERVÉ

### Observabilité base (ORGADMIN+, produit-safe)

| Élément | Détail |
|---------|--------|
| Endpoint | `GET /internal/hugo/sessions/{id}/observability/` |
| Guard | ORGADMIN / SUPERADMIN / tuteur lié (selon `views_internal`) |
| Contenu | `session_observability_v1` : compteurs tours, CTA blocked/requested, extrait `analytics_state`, signaux `ConversationQualitySignal` **sans verbatim** |
| Exposition UI apprenant | **Absente** (doctrine respectée) |
| Exports métier | **Absente** — pivot et exports Qualiopi lite n’incluent pas D9bis |

Producteur : `build_session_observability_snapshot` (`session_observability.py`).

### D9bis / observabilité avancée (SUPERADMIN only)

| Élément | Détail |
|---------|--------|
| Endpoints | `POST .../d9bis/build/`, `GET .../d9bis/export/`, `GET /internal/hugo/analytics/conversation-summary/` |
| Guard | `is_superadmin` uniquement |
| Modèles | `ConversationTurnLLMAnalysis`, `ConversationLLMAnalysis` (v4) |
| Canal | Export JSON technique — **hors** exports Felix-ready / bundle Qualiopi lite |
| Encoors | Routes **404** sans auth (cluster 8) — **A_VÉRIFIER** authentifié |

---

## CIBLE 2.0 (lot courant vs Couronne)

**Lot courant (livré local)** :

- Signaux qualité conversationnelle persistés (`ConversationQualitySignal`, `analytics_state`).
- Lecture admin org sur observabilité session.
- Séparation stricte : pas de scoring opaque exposé à l’apprenant.

**Couronne (non bloquant noyau)** :

- Catalogue signaux canonique exhaustif.
- Dashboards observabilité produit.
- Exposition D9bis côté produit (interdit aujourd’hui).

---

## Frontières à respecter

| Question | Réponse lot courant |
|----------|---------------------|
| L’apprenant voit-il la qualité LLM ? | **Non** |
| ORGADMIN voit-il D9bis ? | **Non** (403) |
| ExportRun inclut-il analytics LLM ? | **Non** (tests `test_analytics_absence_ui_exports`) |
| conversation-summary est-il une preuve Qualiopi ? | **Non** — canal SUPERADMIN technique |

---

## ÉCARTS / A_VÉRIFIER

| Point | Statut |
|-------|--------|
| Encoors v3/v4 déployé | **A_VÉRIFIER** |
| Métriques cohorte prod | **A_VÉRIFIER** |
| Catalogue signaux 2.0 | **CIBLE Couronne** |

---

## Références

- `views_internal.py`, `views_internal_analytics.py`
- `test_observabilite_base.py`, `test_observabilite_avancee_v1.py`
- `ecarts — 80_observabilite_qualite_conversationnelle.md`
