"""Exports: sync CSV/JSON run endpoint for POC."""
from __future__ import annotations
from app_core.tenant_context import tenant_organisation_id

import csv
import io
import json
import uuid
from datetime import date

from django.http import HttpResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.hugo.models import Trace
from apps.hugo.services.evaluation_trace_pivot import enrich_trace_payload_with_pivot
from apps.exports.models import ExportRun
from apps.quality.views import log_audit
from apps.referentials.access_control import is_admin_like
from apps.referentials.models import ReferentialItem


def _parse_iso_date(value: str | None, field_name: str) -> tuple[date | None, str | None]:
    if not value:
        return None, None
    try:
        return date.fromisoformat(str(value)), None
    except ValueError:
        return None, f"{field_name} must be ISO date YYYY-MM-DD."


def _as_bool(value, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        norm = value.strip().lower()
        if norm in {"1", "true", "yes", "y", "on"}:
            return True
        if norm in {"0", "false", "no", "n", "off"}:
            return False
    return bool(value)


def _parse_group_ids(group_ids_raw) -> tuple[list[str], str | None]:
    if group_ids_raw in (None, ""):
        return [], None
    if not isinstance(group_ids_raw, list):
        return [], "group_ids must be a list of UUIDs."
    parsed: list[str] = []
    for raw in group_ids_raw:
        try:
            parsed.append(str(uuid.UUID(str(raw))))
        except (ValueError, TypeError):
            return [], "group_ids must contain only valid UUIDs."
    return parsed, None


def _build_traces_queryset(
    organisation_id,
    from_date: date | None,
    to_date: date | None,
    group_ids: list[str],
):
    traces = (
        Trace.objects.filter(organisation_id=organisation_id)
        .select_related("session", "session__learner", "session__group")
        .order_by("created_at")
    )
    if from_date:
        traces = traces.filter(created_at__date__gte=from_date)
    if to_date:
        traces = traces.filter(created_at__date__lte=to_date)
    if group_ids:
        traces = traces.filter(session__group_id__in=group_ids)
    return traces


class BaseExportBuilder(APIView):
    permission_classes = [IsAuthenticated]

    def _build_json_response(self, traces, run_id: uuid.UUID, timestamp: str) -> HttpResponse:
        payload = []
        for trace in traces:
            structured = enrich_trace_payload_with_pivot(trace.session, trace.payload_structured or {}, trace=trace)
            payload.append(
                {
                    "trace_id": str(trace.id),
                    "session_id": str(trace.session_id),
                    "payload_structured": structured,
                    "evaluation_trace_pivot_v1": structured.get("evaluation_trace_pivot_v1"),
                }
            )
        content = json.dumps(
            {
                "run_id": str(run_id),
                "schema": "trace_rich_v1",
                "generated_at": timezone.now().isoformat(),
                "traces": payload,
            },
            ensure_ascii=False,
            indent=2,
        )
        response = HttpResponse(content, content_type="application/json; charset=utf-8")
        response["Content-Disposition"] = (
            f'attachment; filename="trace_rich_v1_{timestamp}.json"'
        )
        response["X-Export-Run-Id"] = str(run_id)
        return response

    def _build_csv_response(
        self,
        traces,
        separator: str,
        include_bom: bool,
        run_id: uuid.UUID,
        timestamp: str,
    ) -> HttpResponse:
        item_ids = [trace.referential_item_id for trace in traces if trace.referential_item_id]
        items_by_id = {
            str(item.id): item
            for item in ReferentialItem.objects.filter(
                organisation_id=tenant_organisation_id(self.request),
                id__in=item_ids,
            )
        }

        headers = [
            "run_id",
            "organisation_id",
            "group_id",
            "group_name",
            "learner_id",
            "learner_username",
            "session_id",
            "trace_id",
            "trace_created_at",
            "trace_validated_at",
            "trace_status",
            "referential_item_id",
            "item_code",
            "item_title",
        ]

        output = io.StringIO()
        writer = csv.writer(output, delimiter=separator, lineterminator="\n")
        writer.writerow(headers)

        for trace in traces:
            item = items_by_id.get(str(trace.referential_item_id))
            writer.writerow(
                [
                    str(run_id),
                    str(trace.organisation_id),
                    str(trace.session.group_id) if trace.session.group_id else "",
                    str(getattr(trace.session.group, "name", "") or ""),
                    str(trace.session.learner_id),
                    str(getattr(trace.session.learner, "username", "") or ""),
                    str(trace.session_id),
                    str(trace.id),
                    trace.created_at.isoformat(),
                    trace.validated_at.isoformat() if trace.validated_at else "",
                    "validated" if trace.validated_at else "draft",
                    str(trace.referential_item_id) if trace.referential_item_id else "",
                    str(getattr(item, "code", "") or ""),
                    str(getattr(item, "title", "") or ""),
                ]
            )

        content = output.getvalue()
        if include_bom:
            content = "\ufeff" + content

        response = HttpResponse(content, content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = (
            f'attachment; filename="felix_ready_trace_item_{timestamp}.csv"'
        )
        response["X-Export-Run-Id"] = str(run_id)
        return response

    def _render_response(
        self,
        export_format: str,
        traces,
        run_id: uuid.UUID,
        separator: str,
        include_bom: bool,
    ) -> HttpResponse:
        timestamp = timezone.now().strftime("%Y%m%dT%H%M%SZ")
        if export_format == "json":
            return self._build_json_response(traces=traces, run_id=run_id, timestamp=timestamp)
        return self._build_csv_response(
            traces=traces,
            separator=separator,
            include_bom=include_bom,
            run_id=run_id,
            timestamp=timestamp,
        )


class ExportRunView(BaseExportBuilder):
    """POST /exports/run — sync export for csv/json."""

    def post(self, request):
        if not is_admin_like(request.user):
            return Response(
                {"detail": "Forbidden."},
                status=status.HTTP_403_FORBIDDEN,
            )
        metadata_only = _as_bool(request.query_params.get("metadata_only"), default=False)
        export_format = str(request.data.get("format", "csv")).strip().lower()
        if export_format not in {"csv", "json"}:
            return Response(
                {"detail": "format must be 'csv' or 'json'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        period = request.data.get("period", {}) or {}
        from_date, from_error = _parse_iso_date(period.get("from"), "period.from")
        to_date, to_error = _parse_iso_date(period.get("to"), "period.to")
        if from_error:
            return Response({"detail": from_error}, status=status.HTTP_400_BAD_REQUEST)
        if to_error:
            return Response({"detail": to_error}, status=status.HTTP_400_BAD_REQUEST)

        group_ids, group_ids_error = _parse_group_ids(request.data.get("group_ids", []))
        if group_ids_error:
            return Response({"detail": group_ids_error}, status=status.HTTP_400_BAD_REQUEST)

        separator = str(request.data.get("separator", ";")) or ";"
        if len(separator) != 1:
            return Response(
                {"detail": "separator must be a single character."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        include_bom = _as_bool(request.data.get("include_bom"), default=True)

        traces = _build_traces_queryset(
            organisation_id=tenant_organisation_id(request),
            from_date=from_date,
            to_date=to_date,
            group_ids=group_ids,
        )
        run = ExportRun.objects.create(
            organisation_id=tenant_organisation_id(request),
            params={
                "format": export_format,
                "period": {
                    "from": from_date.isoformat() if from_date else None,
                    "to": to_date.isoformat() if to_date else None,
                },
                "group_ids": group_ids,
                "separator": separator,
                "include_bom": include_bom,
                "mode": "sync",
            },
            file_path="",
        )
        log_audit(request, "export_run", "export_run", run.id)
        if metadata_only:
            return Response(
                {
                    "run_id": str(run.id),
                    "format": export_format,
                    "mode": "sync",
                    "metadata_only": True,
                    "traces_count": traces.count(),
                    "download_url": f"/exports/download/{run.id}/",
                },
                status=status.HTTP_201_CREATED,
            )

        return self._render_response(
            export_format=export_format,
            traces=traces,
            run_id=run.id,
            separator=separator,
            include_bom=include_bom,
        )


class ExportDownloadView(BaseExportBuilder):
    """GET /exports/download/{run_id} — regenerate export from stored params."""

    def get(self, request, run_id):
        if not is_admin_like(request.user):
            return Response(
                {"detail": "Forbidden."},
                status=status.HTTP_403_FORBIDDEN,
            )
        run = ExportRun.objects.filter(
            id=run_id,
            organisation_id=tenant_organisation_id(request),
        ).first()
        if not run:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        params = run.params or {}
        export_format = str(params.get("format", "csv")).strip().lower()
        if export_format not in {"csv", "json"}:
            return Response({"detail": "Invalid export format."}, status=status.HTTP_400_BAD_REQUEST)

        period = params.get("period", {}) or {}
        from_date, from_error = _parse_iso_date(period.get("from"), "period.from")
        to_date, to_error = _parse_iso_date(period.get("to"), "period.to")
        if from_error or to_error:
            return Response({"detail": "Invalid stored period parameters."}, status=status.HTTP_400_BAD_REQUEST)

        group_ids, group_error = _parse_group_ids(params.get("group_ids", []))
        if group_error:
            return Response({"detail": "Invalid stored group_ids parameters."}, status=status.HTTP_400_BAD_REQUEST)

        separator = str(params.get("separator", ";")) or ";"
        include_bom = _as_bool(params.get("include_bom"), default=True)

        traces = _build_traces_queryset(
            organisation_id=tenant_organisation_id(request),
            from_date=from_date,
            to_date=to_date,
            group_ids=group_ids,
        )
        return self._render_response(
            export_format=export_format,
            traces=traces,
            run_id=run.id,
            separator=separator,
            include_bom=include_bom,
        )
