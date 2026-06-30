# LOT 6 — Observabilité et métriques cohorte

**Durée estimée :** 3–4 jours  
**Risque :** faible — additif, aucune modification comportementale  
**Dépendance :** LOT 1 (pour ConversationProgress) ; LOT 3 recommandé

---

## Objectif

Instrumenter le système pour détecter automatiquement les 7 signaux critiques à l'arrivée
des premières cohortes, sans journaliser de texte brut.

---

## Règle de sécurité du lot

- Aucun texte verbatim en base ni en log.
- `ConversationPosture`, `SessionMaturityLevel` importés depuis `conversation_profile.py`.
- Champ RLS : `organisation_id` (avec s).
- Toutes les métriques sont agrégées, anonymisables.

---

## Les 7 signaux critiques à mesurer

| # | Signal | Problème détecté |
|---|--------|-----------------|
| 1 | `avg_branches_per_session > 2.5` | Dispersion thématique excessive |
| 2 | `pct_stuck_red > 0.40` | Conversations bloquées en exploration |
| 3 | `pct_forced_reflective_red > 0.20` | Apprenants forcent synthèse trop tôt |
| 4 | `pct_knowledge_single_branch < 0.80` | Mode bûchage dépasse 1 branche active |
| 5 | `false_evaluation_rate > 0.10` | Évaluations déclenchées hors éligibilité |
| 6 | `posture_switch_mid_session > 0.30` | Changements de posture fréquents en cours |
| 7 | `provisional_criteria_unvalidated > 0.25` | Critères provisoires jamais validés |

---

## Modèle Django `ConversationQualitySignal`

```python
# backend/apps/hugo/models.py — ajouter

class ConversationQualitySignal(models.Model):
    """
    Snapshot des métriques qualité post-conversation.
    Aucun verbatim. Données agrégées uniquement.
    """
    session_id          = models.CharField(max_length=128, unique=True)
    organisation_id     = models.CharField(max_length=128, db_index=True)   # avec s
    learner_id          = models.CharField(max_length=128, db_index=True)
    posture             = models.CharField(max_length=64, blank=True, default="")
    total_turns         = models.IntegerField(default=0)
    active_branches_max = models.IntegerField(default=0)
    final_maturity      = models.CharField(max_length=32, default="red")
    posture_switches    = models.IntegerField(default=0)
    synthesis_requested = models.BooleanField(default=False)
    evaluation_requested = models.BooleanField(default=False)
    evaluation_was_eligible = models.BooleanField(default=False)
    dispersion_turns    = models.IntegerField(default=0)
    stuck_red_turns     = models.IntegerField(default=0)
    created_at          = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Signal qualité tutorale"
```

---

## `backend/apps/hugo/services/quality_tracker.py`

```python
from backend.apps.hugo.domain.conversation_profile import (
    ConversationProgress, SessionMaturityLevel,
)
from backend.apps.hugo.models import ConversationQualitySignal


def record_session_signal(session, progress: ConversationProgress, turn_count: int = 0) -> ConversationQualitySignal:
    """Appelé post-conversation, juste avant ou après consolidate_session."""
    signal, _ = ConversationQualitySignal.objects.update_or_create(
        session_id=str(session.id),
        defaults={
            "organisation_id":       str(session.organisation_id),   # avec s
            "learner_id":            str(session.learner_id),
            "posture":               getattr(session, "posture", "") or "",
            "total_turns":           turn_count,
            "active_branches_max":   progress.active_branches_count,
            "final_maturity":        progress.overall_maturity.value,
            "posture_switches":      getattr(session, "_posture_switch_count", 0),
            "synthesis_requested":   getattr(session, "_synthesis_requested", False),
            "evaluation_requested":  getattr(session, "_evaluation_requested", False),
            "evaluation_was_eligible": progress.evaluation_eligible,
            "dispersion_turns":      1 if progress.dispersion_risk else 0,
            "stuck_red_turns":       1 if progress.overall_maturity == SessionMaturityLevel.RED else 0,
        },
    )
    return signal
```

---

## `backend/apps/hugo/analytics/cohort_dashboard.py`

```python
"""
Agrégats pour dashboard qualité. Aucun texte brut.
"""

from django.db.models import Avg, Count, Q, F
from backend.apps.hugo.models import ConversationQualitySignal


def get_cohort_metrics(organisation_id: str, days: int = 30) -> dict:
    from django.utils import timezone
    from datetime import timedelta
    since = timezone.now() - timedelta(days=days)
    qs = ConversationQualitySignal.objects.filter(
        organisation_id=organisation_id,
        created_at__gte=since,
    )
    total = qs.count()
    if total == 0:
        return {"total_sessions": 0}

    agg = qs.aggregate(
        avg_branches=Avg("active_branches_max"),
        pct_stuck_red=Avg(
            (F("stuck_red_turns") * 1.0) / (F("total_turns") + 1)
        ),
    )
    false_eval = qs.filter(evaluation_requested=True, evaluation_was_eligible=False).count()
    eval_total = qs.filter(evaluation_requested=True).count()
    posture_switches = qs.filter(posture_switches__gt=0).count()
    green_sessions = qs.filter(final_maturity="green").count()

    return {
        "total_sessions":              total,
        "avg_branches_per_session":    round(agg["avg_branches"] or 0, 2),
        "pct_green_sessions":          round(green_sessions / total, 2),
        "false_evaluation_rate":       round(false_eval / eval_total, 2) if eval_total else 0,
        "posture_switch_mid_session":  round(posture_switches / total, 2),
        "alert_dispersion":            (agg["avg_branches"] or 0) > 2.5,
        "alert_false_eval":            (false_eval / eval_total > 0.10) if eval_total else False,
    }


def get_per_learner_progress(organisation_id: str, learner_id: str) -> list[dict]:
    """Retourne la progression par séance pour un apprenant (sans texte)."""
    from backend.apps.hugo.models import LearnerThemeMemory
    records = LearnerThemeMemory.objects.filter(
        organisation_id=organisation_id,
        learner_id=learner_id,
    ).order_by("-updated_at")
    return [{
        "theme":       r.theme_key,
        "status":      r.knowledge_status,
        "stabilised":  len(r.stabilised_points),
        "open":        len(r.open_loops),
        "difficulties":len(r.persistent_difficulties),
        "last_session":r.last_conversation_id,
    } for r in records]
```

---

## Endpoint analytics

```python
# backend/apps/hugo/views/analytics.py

from django.http import JsonResponse
from backend.apps.hugo.analytics.cohort_dashboard import get_cohort_metrics, get_per_learner_progress


def cohort_metrics(request):
    org_id = request.user.organisation_id   # avec s
    days   = int(request.GET.get("days", 30))
    return JsonResponse(get_cohort_metrics(org_id, days))


def learner_progress(request, learner_id):
    org_id = request.user.organisation_id   # avec s
    return JsonResponse({"learner_id": learner_id, "progress": get_per_learner_progress(org_id, learner_id)})
```

---

## Tests du LOT 6 (`test_quality_signals.py` — 5 tests)

```python
import pytest
from unittest.mock import MagicMock
from backend.apps.hugo.domain.conversation_profile import (
    ConversationPosture, ConversationProgress, SessionMaturityLevel,
)
from backend.apps.hugo.services.quality_tracker import record_session_signal


def make_session(org_id="org1"):
    s = MagicMock()
    s.id = "session-test"
    s.organisation_id = org_id
    s.learner_id = "learner1"
    s.posture = "reflective_afest"
    s._posture_switch_count = 0
    s._synthesis_requested = False
    s._evaluation_requested = False
    return s


def make_progress(maturity: SessionMaturityLevel, branches: int = 1, eval_eligible: bool = False):
    return ConversationProgress(
        session_id="session-test",
        posture=ConversationPosture.REFLECTIVE_AFEST,
        active_branches_count=branches,
        overall_maturity=maturity,
        evaluation_eligible=eval_eligible,
    )


@pytest.mark.django_db
def test_signal_created():
    sig = record_session_signal(make_session(), make_progress(SessionMaturityLevel.ORANGE), turn_count=5)
    assert sig.session_id == "session-test"
    assert sig.total_turns == 5


@pytest.mark.django_db
def test_organisation_id_with_s():
    sig = record_session_signal(make_session(org_id="org_test"), make_progress(SessionMaturityLevel.RED))
    assert sig.organisation_id == "org_test"


@pytest.mark.django_db
def test_false_eval_detected():
    session = make_session()
    session._evaluation_requested = True
    progress = make_progress(SessionMaturityLevel.RED, eval_eligible=False)
    sig = record_session_signal(session, progress)
    assert sig.evaluation_requested is True
    assert sig.evaluation_was_eligible is False


@pytest.mark.django_db
def test_green_session_recorded():
    sig = record_session_signal(make_session(), make_progress(SessionMaturityLevel.GREEN, eval_eligible=True))
    assert sig.final_maturity == "green"


@pytest.mark.django_db
def test_no_verbatim_in_signal():
    from backend.apps.hugo.models import ConversationQualitySignal
    from django.db.models.fields import TextField
    text_fields = [f.name for f in ConversationQualitySignal._meta.get_fields()
                   if isinstance(f, TextField)]
    assert not text_fields, f"ConversationQualitySignal contient des champs texte : {text_fields}"
```

---

## Checklist de sortie du LOT 6

- [ ] Les 9 tests NR LOT 0 restent verts.
- [ ] Les 5 tests `test_quality_signals.py` passent.
- [ ] `ConversationQualitySignal` ne contient aucun champ texte verbatim.
- [ ] `record_session_signal` appelé post-conversation uniquement.
- [ ] `organisation_id` (avec s) dans tous les filtres et le modèle.
- [ ] Dashboard `/analytics/cohort/` opérationnel avec les 7 indicateurs.
- [ ] Les alertes automatiques (`alert_dispersion`, `alert_false_eval`) testées.
