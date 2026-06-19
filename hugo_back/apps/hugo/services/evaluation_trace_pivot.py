"""EvaluationTrace pivot minimal (domaines 70/100) — agrégat JSON stable, non modèle unique."""
from __future__ import annotations

from typing import Any

from django.utils import timezone

from apps.hugo.models import Evidence, HugoSession, LearnerEvaluationRecord, Trace

PIVOT_SCHEMA = "evaluation_trace_pivot_v1"


def _evaluation_record_payload(record: LearnerEvaluationRecord | None) -> dict[str, Any] | None:
    if record is None:
        return None
    return {
        "record_id": str(record.id),
        "overall_status": record.overall_status,
        "trigger_maturity": record.trigger_maturity,
        "shared_with_tutor": bool(record.shared_with_tutor),
        "tutor_validated": record.tutor_validated,
        "items_count": len(record.items or []),
        "items": list(record.items or [])[:20],
        "recap_preview": str(record.recap_text or "")[:500],
        "evaluation_profile_used": record.evaluation_profile_used,
        "created_at": record.created_at.isoformat() if record.created_at else None,
        "updated_at": record.updated_at.isoformat() if record.updated_at else None,
    }


def _trace_payload(trace: Trace | None) -> dict[str, Any] | None:
    if trace is None:
        return None
    assessments = []
    for assessment in trace.criterion_assessments.select_related("criterion").all()[:50]:
        assessments.append(
            {
                "criterion_id": str(assessment.criterion_id),
                "status": assessment.status,
                "confidence": assessment.confidence,
                "notes": assessment.notes,
            }
        )
    return {
        "trace_id": str(trace.id),
        "referential_item_id": str(trace.referential_item_id) if trace.referential_item_id else None,
        "validated_at": trace.validated_at.isoformat() if trace.validated_at else None,
        "validated_by_id": str(trace.validated_by_id) if trace.validated_by_id else None,
        "created_at": trace.created_at.isoformat() if trace.created_at else None,
        "criterion_assessments": assessments,
    }


def _evidence_payload(session: HugoSession, trace: Trace | None) -> list[dict[str, Any]]:
    qs = Evidence.objects.filter(organisation_id=session.organisation_id)
    if trace is not None:
        qs = qs.filter(trace_id=trace.id)
    else:
        qs = qs.filter(session_id=session.id)
    return [
        {
            "evidence_id": str(item.id),
            "trace_id": str(item.trace_id) if item.trace_id else None,
            "session_id": str(item.session_id) if item.session_id else None,
            "meta": item.meta or {},
            "created_at": item.created_at.isoformat() if item.created_at else None,
        }
        for item in qs.order_by("created_at")[:50]
    ]


def build_evaluation_trace_pivot(
    session: HugoSession,
    *,
    trace: Trace | None = None,
) -> dict[str, Any]:
    """
    Pivot minimal EvaluationTrace — lie session, évaluation, trace, preuves.

    Ne remplace pas l'agrégat doctrinal 2.0 complet ; sert exports et lecture encadrant.
    """
    record = (
        LearnerEvaluationRecord.objects.filter(
            session_id=session.id,
            organisation_id=session.organisation_id,
        ).first()
    )
    if trace is None:
        trace = (
            Trace.objects.filter(session_id=session.id, organisation_id=session.organisation_id)
            .order_by("-created_at")
            .first()
        )

    human_validation = {
        "record_tutor_validated": record.tutor_validated if record else None,
        "record_tutor_validated_at": (
            record.tutor_validated_at.isoformat()
            if record and record.tutor_validated_at
            else None
        ),
        "trace_validated_at": trace.validated_at.isoformat() if trace and trace.validated_at else None,
    }

    return {
        "schema": PIVOT_SCHEMA,
        "generated_at": timezone.now().isoformat(),
        "session_id": str(session.id),
        "organisation_id": str(session.organisation_id),
        "learner_id": str(session.learner_id),
        "group_id": str(session.group_id) if session.group_id else None,
        "evaluation_record": _evaluation_record_payload(record),
        "trace": _trace_payload(trace),
        "evidence": _evidence_payload(session, trace),
        "human_validation": human_validation,
        "certification_disclaimer": "Artefact de suivi pédagogique — validation humaine requise ; non certifiant.",
    }


def enrich_trace_payload_with_pivot(session: HugoSession, payload: dict[str, Any], trace: Trace | None = None) -> dict[str, Any]:
    """Attach pivot to trace_rich_v1 payload without removing legacy keys."""
    enriched = dict(payload or {})
    enriched["evaluation_trace_pivot_v1"] = build_evaluation_trace_pivot(session, trace=trace)
    return enriched
