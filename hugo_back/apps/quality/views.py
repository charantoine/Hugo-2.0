"""Quality: audit_log helper, evidence-bundle (ZIP)."""
import io
import uuid
import zipfile
import json
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse
from django.utils import timezone

from .models import AuditLog
from app_core.tenant_context import tenant_organisation_id
from apps.hugo.models import Trace, HugoSession
from apps.referentials.models import Referential
from apps.referentials.access_control import is_admin_like
from apps.library.models import GroupDocument


def log_audit(request, action, resource_type, resource_id):
    """Write audit_log (metadata only)."""
    org_id = tenant_organisation_id(request) or getattr(request.user, "organisation_id", None)
    AuditLog.objects.create(
        organisation_id=org_id,
        actor=request.user,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
    )


class EvidenceBundleView(APIView):
    """POST /quality/qualiopi/evidence-bundle — ZIP: CSV/JSON, audit_log, referentials, ACTIVE docs."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not is_admin_like(request.user):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)
        organisation_id = tenant_organisation_id(request)
        bundle_id = uuid.uuid4()
        log_audit(request, "evidence_bundle_requested", "qualiopi_bundle", bundle_id)
        period = request.data.get("period", {})
        from_date = period.get("from")
        to_date = period.get("to")
        group_ids = request.data.get("group_ids", [])
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            traces = Trace.objects.filter(organisation_id=organisation_id)
            if from_date:
                traces = traces.filter(created_at__date__gte=from_date)
            if to_date:
                traces = traces.filter(created_at__date__lte=to_date)
            if group_ids:
                traces = traces.filter(session__group_id__in=group_ids)
            rows = []
            for t in traces:
                rows.append({
                    "trace_id": str(t.id),
                    "session_id": str(t.session_id),
                    "learner_id": str(t.session.learner_id),
                    "validated_at": t.validated_at.isoformat() if t.validated_at else None,
                    "created_at": t.created_at.isoformat(),
                })
            zf.writestr("traces.json", json.dumps(rows, ensure_ascii=False, indent=2))
            logs = list(AuditLog.objects.filter(organisation_id=organisation_id).order_by("-created_at")[:1000])
            zf.writestr("audit_log.json", json.dumps([
                {"action": l.action, "resource_type": l.resource_type, "resource_id": str(l.resource_id), "created_at": l.created_at.isoformat()}
                for l in logs
            ], ensure_ascii=False, indent=2))
            refs = Referential.objects.filter(organisation_id=organisation_id)
            zf.writestr("referentials.json", json.dumps([{"id": str(r.id), "name": r.name} for r in refs], ensure_ascii=False, indent=2))
            gds = GroupDocument.objects.filter(organisation_id=organisation_id, status=GroupDocument.Status.ACTIVE)
            zf.writestr("active_documents.json", json.dumps([{"id": str(gd.id), "document_id": str(gd.document_id)} for gd in gds], ensure_ascii=False, indent=2))
            zf.writestr("summary.txt", "Evidence bundle generated at %s\nTraces: %d\nAudit log entries: %d\n" % (
                timezone.now().isoformat(), len(rows), len(logs)
            ))
        buf.seek(0)
        resp = HttpResponse(buf.read(), content_type="application/zip")
        resp["Content-Disposition"] = 'attachment; filename="qualiopi_evidence_bundle.zip"'
        return resp
