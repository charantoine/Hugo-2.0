"""Library: documents, index, group library."""
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from app_core.tenant_context import tenant_organisation_id

from .chunking import split_into_chunks
from .indexing import index_document_chunks
from .models import Document, GroupDocument, DocumentChunk
from .pdf_extract import extract_pdf_text
from .serializers import (
    DocumentDetailSerializer,
    DocumentListSerializer,
    DocumentSerializer,
)
from django.db.models import Q

from apps.accounts.models import Role
from apps.accounts.permissions import IsOrgAdminOrSuperadmin, IsOrgAdminSuperadminOrTrainer
from apps.hugo.models import HugoSession
from apps.referentials.models import Group, GroupMembership, TutorLearnerLink


def _can_manage_library(request, view) -> bool:
    """Écriture réservée aux admins org, superadmins et formateurs (TRAINER)."""
    return IsOrgAdminSuperadminOrTrainer().has_permission(request, view)


def _can_read_group_library(request, group, view) -> bool:
    """
    Lecture : même organisation, puis tout acteur du groupe (adhésion, lien tuteur/apprenant,
    session Hugo) ou formateur (TRAINER) sur l’org, ou admin / superadmin.
    """
    user = request.user
    if not user.is_authenticated:
        return False
    org_id = user.organisation_id
    if group.organisation_id != org_id:
        return False
    if IsOrgAdminOrSuperadmin().has_permission(request, view):
        return True
    if user.role == Role.TRAINER:
        return True
    if GroupMembership.objects.filter(
        group_id=group.id,
        user_id=user.id,
        organisation_id=org_id,
    ).exists():
        return True
    if TutorLearnerLink.objects.filter(
        Q(tutor_id=user.id) | Q(learner_id=user.id),
        group_id=group.id,
        organisation_id=org_id,
    ).exists():
        return True
    return HugoSession.objects.filter(
        learner_id=user.id,
        group_id=group.id,
        organisation_id=org_id,
    ).exists()


class DocumentListCreate(generics.ListCreateAPIView):
    """GET/POST /documents — org-scoped documents (admin)."""

    permission_classes = [IsOrgAdminSuperadminOrTrainer]

    def get_queryset(self):
        return Document.objects.filter(organisation_id=tenant_organisation_id(self.request))

    def get_serializer_class(self):
        if self.request.method == "POST":
            return DocumentSerializer
        return DocumentListSerializer

    def perform_create(self, serializer):
        serializer.save(organisation_id=tenant_organisation_id(self.request))

    def get_serializer_context(self):
        return {**super().get_serializer_context(), "request": self.request}


class DocumentRetrieveUpdate(generics.RetrieveUpdateAPIView):
    """GET/PATCH /documents/{document_id}/ — read or update title / source_text."""

    permission_classes = [IsOrgAdminSuperadminOrTrainer]
    serializer_class = DocumentDetailSerializer
    lookup_field = "id"
    lookup_url_kwarg = "document_id"

    def get_queryset(self):
        return Document.objects.filter(organisation_id=tenant_organisation_id(self.request))

    def get_serializer_context(self):
        return {**super().get_serializer_context(), "request": self.request}


class DocumentIndexView(APIView):
    """POST /documents/{document_id}/index — build chunks from persisted source_text."""

    permission_classes = [IsOrgAdminSuperadminOrTrainer]

    def post(self, request, document_id):
        doc = get_object_or_404(Document, id=document_id, organisation_id=tenant_organisation_id(request))
        try:
            chunk_size = int(request.data.get("chunk_size") or request.query_params.get("chunk_size") or 500)
        except (TypeError, ValueError):
            chunk_size = 500
        try:
            overlap = int(request.data.get("overlap") or request.query_params.get("overlap") or 50)
        except (TypeError, ValueError):
            overlap = 50
        result = index_document_chunks(doc, chunk_size=chunk_size, overlap=overlap)
        return Response(result)


class DocumentUploadView(APIView):
    """POST /documents/upload/ — multipart PDF upload with optional meta."""

    permission_classes = [IsOrgAdminSuperadminOrTrainer]

    def post(self, request):
        upload = request.FILES.get("file")
        title = str(request.data.get("title") or "").strip()
        if not upload:
            return Response({"detail": "file required."}, status=status.HTTP_400_BAD_REQUEST)
        if not title:
            title = str(getattr(upload, "name", "") or "Document").rsplit(".", 1)[0] or "Document"
        meta_raw = request.data.get("meta")
        meta: dict = {}
        if isinstance(meta_raw, dict):
            meta = meta_raw
        elif isinstance(meta_raw, str) and meta_raw.strip():
            import json

            try:
                parsed = json.loads(meta_raw)
                meta = parsed if isinstance(parsed, dict) else {}
            except json.JSONDecodeError:
                meta = {}
        from .serializers import DocumentSerializer

        serializer = DocumentSerializer(
            data={"title": title, "meta": meta, "source_text": ""},
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        doc = serializer.save(organisation_id=tenant_organisation_id(request))
        suffix = str(getattr(upload, "name", "") or "").lower()
        if suffix.endswith(".pdf"):
            import tempfile
            from pathlib import Path

            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                for chunk in upload.chunks():
                    tmp.write(chunk)
                tmp_path = Path(tmp.name)
            extracted = extract_pdf_text(tmp_path)
            try:
                tmp_path.unlink(missing_ok=True)
            except OSError:
                pass
            doc.source_text = extracted
            doc.file_path = str(getattr(upload, "name", "") or "")
            doc.quality_flag = "OK" if extracted else "LOW_TEXT"
            doc.extracted_chars = len(extracted)
            doc.save(update_fields=["source_text", "file_path", "quality_flag", "extracted_chars", "updated_at"])
        else:
            text = upload.read().decode("utf-8", errors="ignore")
            doc.source_text = text
            doc.file_path = str(getattr(upload, "name", "") or "")
            doc.extracted_chars = len(text)
            doc.quality_flag = "OK" if text.strip() else "LOW_TEXT"
            doc.save(update_fields=["source_text", "file_path", "extracted_chars", "quality_flag", "updated_at"])
        return Response(DocumentDetailSerializer(doc).data, status=status.HTTP_201_CREATED)


class GroupLibraryListCreate(APIView):
    """GET/POST /groups/{group_id}/library."""

    permission_classes = [IsAuthenticated]

    def get(self, request, group_id):
        group = get_object_or_404(Group, id=group_id, organisation_id=tenant_organisation_id(request))
        if not _can_read_group_library(request, group, self):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)
        gds = (
            GroupDocument.objects.filter(group_id=group_id, organisation_id=tenant_organisation_id(request))
            .select_related("document")
            .order_by("-created_at")
        )
        if not IsOrgAdminOrSuperadmin().has_permission(request, self):
            gds = gds.filter(status=GroupDocument.Status.ACTIVE)
        return Response({
            "items": [
                {
                    "id": str(gd.id),
                    "document_id": str(gd.document_id),
                    "status": gd.status,
                    "document_title": gd.document.title,
                    "document_meta": gd.document.meta or {},
                    "chunks_count": gd.document.chunks_count,
                    "quality_flag": gd.document.quality_flag,
                }
                for gd in gds
            ]
        })

    def post(self, request, group_id):
        if not _can_manage_library(request, self):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)
        group = get_object_or_404(Group, id=group_id, organisation_id=tenant_organisation_id(request))
        document_id = request.data.get("document_id")
        if not document_id:
            return Response({"detail": "document_id required."}, status=status.HTTP_400_BAD_REQUEST)
        doc = get_object_or_404(Document, id=document_id, organisation_id=tenant_organisation_id(request))
        gd, created = GroupDocument.objects.get_or_create(
            group=group,
            document=doc,
            defaults={"organisation_id": tenant_organisation_id(request), "status": GroupDocument.Status.ACTIVE},
        )
        if not created and gd.status != GroupDocument.Status.ACTIVE:
            gd.status = GroupDocument.Status.ACTIVE
            gd.save(update_fields=["status"])
        return Response(
            {
                "id": str(gd.id),
                "status": gd.status,
                "document_id": str(gd.document_id),
                "document_title": doc.title,
                "document_meta": doc.meta or {},
                "chunks_count": doc.chunks_count,
                "quality_flag": doc.quality_flag,
            },
            status=status.HTTP_201_CREATED,
        )


class GroupLibraryDocumentContentView(APIView):
    """GET /groups/{group_id}/library/documents/{document_id}/content/ — texte source (apprenant / admin)."""

    permission_classes = [IsAuthenticated]

    def get(self, request, group_id, document_id):
        group = get_object_or_404(Group, id=group_id, organisation_id=tenant_organisation_id(request))
        if not _can_read_group_library(request, group, self):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)
        gd = get_object_or_404(
            GroupDocument,
            group_id=group_id,
            document_id=document_id,
            organisation_id=tenant_organisation_id(request),
        )
        if not _can_manage_library(request, self):
            if gd.status != GroupDocument.Status.ACTIVE:
                return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        doc = gd.document
        return Response(
            {
                "id": str(doc.id),
                "title": doc.title,
                "source_text": doc.source_text or "",
                "meta": doc.meta or {},
            }
        )


class GroupLibraryUpdate(APIView):
    """PUT /groups/{group_id}/library/{group_document_id}."""

    permission_classes = [IsOrgAdminSuperadminOrTrainer]

    def put(self, request, group_id, group_document_id):
        gd = get_object_or_404(
            GroupDocument,
            id=group_document_id,
            group_id=group_id,
            organisation_id=tenant_organisation_id(request),
        )
        if "status" in request.data:
            gd.status = request.data["status"]
            gd.save()
        doc = gd.document
        return Response(
            {
                "id": str(gd.id),
                "status": gd.status,
                "document_id": str(gd.document_id),
                "document_title": doc.title,
                "document_meta": doc.meta or {},
                "chunks_count": doc.chunks_count,
                "quality_flag": doc.quality_flag,
            }
        )
