"""Evidence upload — EXIF stripped, GPS opt-in; must link trace or session."""
import uuid
import os
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from app_core.tenant_context import tenant_organisation_id

from .models import Evidence, Trace, HugoSession
from .services.evidence_media import evidence_meta_from_request, is_image_upload, strip_image_metadata


class EvidenceCreateView(APIView):
    """POST /evidence — upload photo; trace_id or session_id required."""
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        trace_id = request.data.get("trace_id") or request.FILES.get("trace_id")
        session_id = request.data.get("session_id")
        if not trace_id and not session_id:
            return Response(
                {"detail": "Either trace_id or session_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        trace = None
        session = None
        if trace_id:
            trace = Trace.objects.filter(
                id=trace_id,
                organisation_id=tenant_organisation_id(request),
            ).first()
            if not trace:
                return Response({"detail": "Trace not found."}, status=status.HTTP_404_NOT_FOUND)
        if session_id:
            session = HugoSession.objects.filter(
                id=session_id,
                organisation_id=tenant_organisation_id(request),
                learner=request.user,
            ).first()
            if not session:
                return Response({"detail": "Session not found."}, status=status.HTTP_404_NOT_FOUND)
        if not trace and not session:
            return Response(
                {"detail": "Either trace_id or session_id must be valid."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        file_obj = request.FILES.get("file")
        if not file_obj:
            return Response({"detail": "file required."}, status=status.HTTP_400_BAD_REQUEST)

        upload_name = getattr(file_obj, "name", "") or "evidence.bin"
        ext = os.path.splitext(upload_name)[-1] or ""
        if is_image_upload(upload_name):
            file_to_save = strip_image_metadata(file_obj)
        else:
            file_to_save = file_obj
            if hasattr(file_to_save, "seek"):
                file_to_save.seek(0)

        rel_path = "evidence/%s/%s%s" % (tenant_organisation_id(request), uuid.uuid4().hex, ext)
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile

        if isinstance(file_to_save, ContentFile):
            path = default_storage.save(rel_path, file_to_save)
        elif hasattr(file_to_save, "read"):
            path = default_storage.save(rel_path, ContentFile(file_to_save.read()))
        else:
            path = default_storage.save(rel_path, file_to_save)

        meta = evidence_meta_from_request(request.data)
        ev = Evidence.objects.create(
            organisation_id=tenant_organisation_id(request),
            trace=trace,
            session=session,
            file_path=path,
            meta=meta,
        )
        return Response(
            {"id": str(ev.id), "file_path": ev.file_path, "meta": ev.meta},
            status=status.HTTP_201_CREATED,
        )
