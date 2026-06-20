from __future__ import annotations
from app_core.tenant_context import tenant_organisation_id

import csv
from io import StringIO

from django.http import HttpResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.hugo.domain.conversation_profile import KnowledgeItemStatus
from apps.accounts.models import Role
from apps.hugo.models import LearnerEvaluationRecord, TrainerKnowledgeItem
from apps.hugo.services.document_ingestor import ingest_document
from apps.referentials.access_control import can_manage_trainer_knowledge

ELICITATION_QUESTIONS = [
    {"id": "q_mastery", "text": "Qu'est-ce qu'un apprenant qui maîtrise vraiment ce point est capable de faire ?"},
    {"id": "q_errors", "text": "Quelles erreurs fréquentes observes-tu ?"},
    {"id": "q_chains", "text": "Quelle chaîne de raisonnement attends-tu ?"},
    {"id": "q_rules", "text": "Existe-t-il des règles absolues à ne pas violer ?"},
    {"id": "q_situations", "text": "Peux-tu donner une situation professionnelle typique ?"},
]


def _content_type_for_question(question_id: str) -> str:
    return {
        "q_mastery": "mastery_criterion",
        "q_errors": "frequent_error",
        "q_chains": "reasoning_chain",
        "q_rules": "reference_rule",
        "q_situations": "procedure",
    }.get(question_id, "mastery_criterion")


def _can_manage_evaluations(user) -> bool:
    return bool(user and user.is_authenticated and user.role in {Role.TRAINER, Role.ORGADMIN, Role.SUPERADMIN})


def _forbidden_if_not_trainer_knowledge(user):
    if not can_manage_trainer_knowledge(user):
        return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)
    return None


def _usage_stats_for_item(item) -> dict:
    validated = item.status == KnowledgeItemStatus.VALIDATED_TRAINER.value
    return {
        "exploitable": validated,
        "source_type": item.source_type,
        "usage_count": None,
        "usage_note": (
            "Exploitable par le moteur après validation formateur."
            if validated
            else "Non exploitable tant que l’item n’est pas validé."
        ),
    }


def _serialize_trainer_item(item) -> dict:
    validated_by = item.validated_by
    return {
        "id": str(item.id),
        "referential_item_id": item.referential_item_id,
        "content": item.content,
        "content_type": item.content_type,
        "source_type": item.source_type,
        "status": item.status,
        "provenance_note": item.provenance_note,
        "validated_at": item.validated_at.isoformat() if item.validated_at else None,
        "validated_by": validated_by.email if validated_by else None,
        "created_at": item.created_at.isoformat() if item.created_at else None,
        "updated_at": item.updated_at.isoformat() if item.updated_at else None,
        "usage_stats": _usage_stats_for_item(item),
    }


class TrainerKnowledgeItemListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        denied = _forbidden_if_not_trainer_knowledge(request.user)
        if denied:
            return denied
        qs = TrainerKnowledgeItem.objects.filter(organisation_id=tenant_organisation_id(request)).select_related("validated_by")
        status_filter = str(request.query_params.get("status") or "").strip()
        if status_filter:
            qs = qs.filter(status=status_filter)
        items = [_serialize_trainer_item(item) for item in qs.order_by("-updated_at")[:200]]
        return Response({"items": items, "total": len(items)})


class TrainerElicitationQuestionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, referential_item_id):
        denied = _forbidden_if_not_trainer_knowledge(request.user)
        if denied:
            return denied
        return Response({"questions": ELICITATION_QUESTIONS, "referential_item_id": str(referential_item_id)})


class TrainerElicitationAnswersView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, referential_item_id):
        denied = _forbidden_if_not_trainer_knowledge(request.user)
        if denied:
            return denied
        answers = request.data.get("answers", {}) if isinstance(request.data, dict) else {}
        created_ids: list[str] = []
        for question_id, answer in dict(answers).items():
            content = str(answer or "").strip()
            if not content:
                continue
            item = TrainerKnowledgeItem.objects.create(
                organisation_id=tenant_organisation_id(request),
                referential_item_id=str(referential_item_id),
                content=content,
                content_type=_content_type_for_question(question_id),
                source_type="dialogue_elicited",
                status=KnowledgeItemStatus.DECLARED.value,
                provenance_note=f"Elicitation question: {question_id}",
            )
            created_ids.append(str(item.id))
        return Response({"created": created_ids}, status=status.HTTP_201_CREATED)


class TrainerKnowledgeValidationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, item_id):
        denied = _forbidden_if_not_trainer_knowledge(request.user)
        if denied:
            return denied
        item = TrainerKnowledgeItem.objects.filter(
            id=item_id,
            organisation_id=tenant_organisation_id(request),
        ).first()
        if not item:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        action = str(request.data.get("action") or "").strip().lower()
        if action == "validate":
            item.status = KnowledgeItemStatus.VALIDATED_TRAINER.value
            item.validated_by = request.user
            item.validated_at = timezone.now()
            item.save(update_fields=["status", "validated_by", "validated_at", "updated_at"])
            return Response({"status": "validated"})
        if action == "reject":
            reason = str(request.data.get("reason") or "").strip()
            if reason:
                item.provenance_note = f"{item.provenance_note}\nRejet: {reason}".strip()
                item.save(update_fields=["provenance_note", "updated_at"])
            item.delete()
            return Response({"status": "rejected"})
        if action == "mark_provisional":
            item.status = KnowledgeItemStatus.DERIVED_PROVISIONAL.value
            item.save(update_fields=["status", "updated_at"])
            return Response({"status": "derived_provisional"})
        if action == "edit":
            item.content = str(request.data.get("content") or item.content).strip() or item.content
            item.status = KnowledgeItemStatus.VALIDATED_TRAINER.value
            item.validated_by = request.user
            item.validated_at = timezone.now()
            item.save(update_fields=["content", "status", "validated_by", "validated_at", "updated_at"])
            return Response({"status": "validated", "content": item.content})
        return Response({"detail": "Unsupported action."}, status=status.HTTP_400_BAD_REQUEST)


class TrainerDocumentIngestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        denied = _forbidden_if_not_trainer_knowledge(request.user)
        if denied:
            return denied
        file_path = str(request.data.get("file_path") or "").strip()
        referential_item_id = str(request.data.get("referential_item_id") or "").strip()
        if not file_path:
            return Response({"detail": "file_path required."}, status=status.HTTP_400_BAD_REQUEST)
        raw_items = ingest_document(file_path, str(tenant_organisation_id(request)), referential_item_id)
        created_ids: list[str] = []
        for raw in raw_items:
            item = TrainerKnowledgeItem.objects.create(
                organisation_id=tenant_organisation_id(request),
                referential_item_id=raw.get("referential_item_id", ""),
                content=raw.get("content", ""),
                content_type=raw.get("content_type", "mastery_criterion"),
                source_type=raw.get("source_type", "document_extracted"),
                status=raw.get("status", KnowledgeItemStatus.DERIVED_PROVISIONAL.value),
                confidence_score=raw.get("confidence_score"),
                provenance_note=raw.get("provenance_note", ""),
            )
            created_ids.append(str(item.id))
        return Response({"created": created_ids}, status=status.HTTP_201_CREATED)


class TrainerEvaluationRecordListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not _can_manage_evaluations(request.user):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)
        qs = LearnerEvaluationRecord.objects.filter(organisation=request.user.organisation)
        group_id = str(request.query_params.get("group_id") or "").strip()
        status_filter = str(request.query_params.get("status") or "").strip()
        if group_id:
            qs = qs.filter(group_id=group_id)
        if status_filter:
            qs = qs.filter(overall_status=status_filter)
        records = list(
            qs.order_by("-created_at").values(
                "id",
                "session_id",
                "learner_id",
                "group_id",
                "overall_status",
                "recap_text",
                "items",
                "shared_with_tutor",
                "tutor_validated",
                "tutor_comment",
                "trigger_maturity",
                "evaluation_profile_used",
                "created_at",
            )
        )
        return Response({"records": records, "total": len(records)})


class TrainerEvaluationRecordValidationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, record_id):
        if not _can_manage_evaluations(request.user):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)
        record = LearnerEvaluationRecord.objects.filter(
            id=record_id,
            organisation=request.user.organisation,
        ).first()
        if not record:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        action = str(request.data.get("action") or "").strip().lower()
        comment = str(request.data.get("comment") or "").strip()
        if action == "validate":
            record.tutor_validated = True
            record.tutor_comment = comment
            record.tutor_validated_at = timezone.now()
            record.tutor_validated_by = request.user
            for item in list(record.items or []):
                if item.get("status") == "draft":
                    item["status"] = "tutor_validated"
            record.save(update_fields=["tutor_validated", "tutor_comment", "tutor_validated_at", "tutor_validated_by", "items", "updated_at"])
            return Response({"status": "validated"})
        if action == "reject":
            record.tutor_validated = False
            record.tutor_comment = comment
            record.tutor_validated_at = timezone.now()
            record.tutor_validated_by = request.user
            record.save(update_fields=["tutor_validated", "tutor_comment", "tutor_validated_at", "tutor_validated_by", "updated_at"])
            return Response({"status": "rejected"})
        if action == "comment":
            record.tutor_comment = comment
            record.save(update_fields=["tutor_comment", "updated_at"])
            return Response({"status": "commented"})
        return Response({"detail": "Unsupported action."}, status=status.HTTP_400_BAD_REQUEST)


class TrainerEvaluationRecordExportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not _can_manage_evaluations(request.user):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)
        qs = LearnerEvaluationRecord.objects.filter(organisation=request.user.organisation, shared_with_tutor=True)
        group_id = str(request.query_params.get("group_id") or "").strip()
        if group_id:
            qs = qs.filter(group_id=group_id)
        export_format = str(request.query_params.get("format") or "json").strip().lower()
        if export_format == "csv":
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(
                [
                    "session_id",
                    "learner_id",
                    "group_id",
                    "overall_status",
                    "trigger_maturity",
                    "recap_text",
                    "items_count",
                    "evaluation_profile_used",
                    "tutor_validated",
                    "created_at",
                ]
            )
            for record in qs.order_by("-created_at"):
                writer.writerow(
                    [
                        str(record.session_id),
                        str(record.learner_id),
                        str(record.group_id or ""),
                        record.overall_status,
                        record.trigger_maturity,
                        record.recap_text[:200],
                        len(record.items or []),
                        record.evaluation_profile_used,
                        record.tutor_validated,
                        record.created_at.isoformat(),
                    ]
                )
            response = HttpResponse(output.getvalue(), content_type="text/csv")
            response["Content-Disposition"] = "attachment; filename=evaluations.csv"
            return response

        records = list(
            qs.order_by("-created_at").values(
                "session_id",
                "learner_id",
                "group_id",
                "overall_status",
                "recap_text",
                "items",
                "trigger_maturity",
                "evaluation_profile_used",
                "tutor_validated",
                "tutor_comment",
                "created_at",
            )
        )
        return Response({"records": records})
