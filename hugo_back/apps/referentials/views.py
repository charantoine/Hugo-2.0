"""Referentials: list, import-v2 (JSON), overlay, config."""
from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from app_core.tenant_context import tenant_organisation_id

from .models import (
    Referential,
    ReferentialItem,
    ReferentialCriterion,
    ReferentialActivity,
    ReferentialTask,
    ReferentialCompetencyTask,
    ReferentialConfig,
    ReferentialItemOverlay,
    Group,
    Scale,
    ScaleLevel,
)
from .serializers import (
    ReferentialSerializer,
    ReferentialItemSerializer,
    ReferentialCriterionSerializer,
    ReferentialActivitySerializer,
    ReferentialTaskSerializer,
    ReferentialCompetencyTaskSerializer,
)


class ReferentialListView(generics.ListAPIView):
    """GET /referentials/ — list referentials for current organisation."""

    serializer_class = ReferentialSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Referential.objects.filter(organisation_id=tenant_organisation_id(self.request))
            .annotate(
                items_count=Count("items", distinct=True),
                activities_count=Count("activities", distinct=True),
                tasks_count=Count("activities__tasks", distinct=True),
            )
            .order_by("name")
        )


class ImportV2View(APIView):
    """POST /referentials/import-v2 — import JSON (evaluation_criteria, evaluation_modalities, expected_evidence, source_ref)."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        def _stripped(value):
            return str(value or "").strip()

        def _normalize_task_code(value):
            return _stripped(value).upper()

        def _normalize_item_code(value):
            return _stripped(value).upper()

        data = request.data
        name = data.get("name") or "Referential"
        source_ref = data.get("source_ref", "")
        ref = Referential.objects.create(
            organisation_id=tenant_organisation_id(request),
            name=name,
            source_ref=source_ref,
        )
        item_by_code = {}
        activity_by_code = {}
        task_by_code = {}
        items_data = data.get("items", [])
        for it in items_data:
            item = ReferentialItem.objects.create(
                organisation_id=tenant_organisation_id(request),
                referential=ref,
                code=it.get("code", ""),
                title=it.get("title", ""),
                block_code=it.get("block_code", ""),
                block_label=it.get("block_label", ""),
                evaluation_criteria=it.get("evaluation_criteria", []),
                evaluation_modalities=it.get("evaluation_modalities", []),
                expected_evidence=it.get("expected_evidence", []),
                source_ref=it.get("source_ref", ""),
            )
            item_by_code[_normalize_item_code(item.code)] = item
            criteria = it.get("criteria")
            if isinstance(criteria, list) and criteria:
                for idx, criterion in enumerate(criteria):
                    if isinstance(criterion, dict):
                        label = str(criterion.get("label") or "").strip()
                        code = str(criterion.get("code") or f"{item.code}.{idx + 1}").strip()
                        expected_evidence = criterion.get("expected_evidence", [])
                        question_seeds = criterion.get("question_seeds", [])
                    else:
                        label = str(criterion or "").strip()
                        code = f"{item.code}.{idx + 1}"
                        expected_evidence = []
                        question_seeds = []
                    if not label:
                        continue
                    ReferentialCriterion.objects.create(
                        organisation_id=tenant_organisation_id(request),
                        referential_item=item,
                        code=code,
                        label=label,
                        order_index=idx,
                        expected_evidence=expected_evidence if isinstance(expected_evidence, list) else [],
                        question_seeds=question_seeds if isinstance(question_seeds, list) else [],
                        is_active=True,
                    )
        activities_data = data.get("activities", [])
        for idx, activity in enumerate(activities_data):
            if not isinstance(activity, dict):
                continue
            activity_code = _stripped(activity.get("code"))
            activity_label = _stripped(activity.get("label"))
            if not activity_code or not activity_label:
                continue
            order_index = activity.get("order_index", idx)
            db_activity, _ = ReferentialActivity.objects.update_or_create(
                organisation_id=tenant_organisation_id(request),
                referential=ref,
                code=activity_code,
                defaults={
                    "label": activity_label,
                    "order_index": int(order_index) if str(order_index).isdigit() else idx,
                },
            )
            activity_by_code[_stripped(db_activity.code).upper()] = db_activity
            nested_tasks = activity.get("tasks", [])
            if isinstance(nested_tasks, list):
                for task_idx, task in enumerate(nested_tasks):
                    if isinstance(task, dict):
                        task_code = _normalize_task_code(task.get("code"))
                        task_label = _stripped(task.get("label"))
                        task_order = task.get("order_index", task_idx)
                    else:
                        task_code = _normalize_task_code(task)
                        task_label = _stripped(task)
                        task_order = task_idx
                    if not task_code or not task_label:
                        continue
                    db_task, _ = ReferentialTask.objects.update_or_create(
                        organisation_id=tenant_organisation_id(request),
                        activity=db_activity,
                        code=task_code,
                        defaults={
                            "label": task_label,
                            "order_index": int(task_order) if str(task_order).isdigit() else task_idx,
                        },
                    )
                    task_by_code[_normalize_task_code(db_task.code)] = db_task

        tasks_data = data.get("tasks", [])
        for idx, task in enumerate(tasks_data):
            if not isinstance(task, dict):
                continue
            task_code = _normalize_task_code(task.get("code"))
            task_label = _stripped(task.get("label"))
            activity_code = _stripped(task.get("activity_code")).upper()
            if not task_code or not task_label or not activity_code:
                continue
            db_activity = activity_by_code.get(activity_code)
            if not db_activity:
                continue
            task_order = task.get("order_index", idx)
            db_task, _ = ReferentialTask.objects.update_or_create(
                organisation_id=tenant_organisation_id(request),
                activity=db_activity,
                code=task_code,
                defaults={
                    "label": task_label,
                    "order_index": int(task_order) if str(task_order).isdigit() else idx,
                },
            )
            task_by_code[_normalize_task_code(db_task.code)] = db_task

        for raw_item in items_data:
            if not isinstance(raw_item, dict):
                continue
            item = item_by_code.get(_normalize_item_code(raw_item.get("code")))
            if not item:
                continue
            inline_tasks = raw_item.get("tasks", [])
            if not isinstance(inline_tasks, list):
                continue
            for task_ref in inline_tasks:
                if isinstance(task_ref, dict):
                    task_code = _normalize_task_code(task_ref.get("code"))
                else:
                    task_code = _normalize_task_code(task_ref)
                db_task = task_by_code.get(task_code)
                if not db_task:
                    continue
                ReferentialCompetencyTask.objects.get_or_create(
                    organisation_id=tenant_organisation_id(request),
                    referential_item=item,
                    task=db_task,
                )

        competency_tasks = data.get("competency_tasks", [])
        for link in competency_tasks:
            if not isinstance(link, dict):
                continue
            item_code = _normalize_item_code(
                link.get("competency_code") or link.get("item_code") or link.get("code")
            )
            task_code = _normalize_task_code(link.get("task_code"))
            if not item_code or not task_code:
                continue
            item = item_by_code.get(item_code)
            task = task_by_code.get(task_code)
            if not item or not task:
                continue
            ReferentialCompetencyTask.objects.get_or_create(
                organisation_id=tenant_organisation_id(request),
                referential_item=item,
                task=task,
            )
        return Response(
            {
                "id": str(ref.id),
                "name": ref.name,
                "items_count": ref.items.count(),
                "activities_count": ref.activities.count(),
                "tasks_count": ReferentialTask.objects.filter(activity__referential=ref).count(),
            },
            status=status.HTTP_201_CREATED,
        )


class ReferentialItemListView(generics.ListAPIView):
    serializer_class = ReferentialItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ReferentialItem.objects.filter(
            referential_id=self.kwargs["ref_id"],
            organisation_id=tenant_organisation_id(self.request),
        ).prefetch_related("criteria", "competency_tasks__task", "competency_tasks__task__activity")


class ReferentialCriterionListCreateView(generics.ListCreateAPIView):
    serializer_class = ReferentialCriterionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ReferentialCriterion.objects.filter(
            organisation_id=tenant_organisation_id(self.request),
            referential_item_id=self.kwargs["item_id"],
            referential_item__referential_id=self.kwargs["ref_id"],
        ).order_by("order_index", "code")

    def perform_create(self, serializer):
        item = get_object_or_404(
            ReferentialItem,
            id=self.kwargs["item_id"],
            referential_id=self.kwargs["ref_id"],
            organisation_id=tenant_organisation_id(self.request),
        )
        serializer.save(
            organisation_id=tenant_organisation_id(self.request),
            referential_item=item,
        )


class ReferentialCriterionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReferentialCriterionSerializer
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = "criterion_id"
    lookup_field = "id"

    def get_queryset(self):
        return ReferentialCriterion.objects.filter(
            organisation_id=tenant_organisation_id(self.request),
            referential_item_id=self.kwargs["item_id"],
            referential_item__referential_id=self.kwargs["ref_id"],
        )


class ReferentialActivityListView(generics.ListAPIView):
    serializer_class = ReferentialActivitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            ReferentialActivity.objects.filter(
                organisation_id=tenant_organisation_id(self.request),
                referential_id=self.kwargs["ref_id"],
            )
            .annotate(tasks_count=Count("tasks", distinct=True))
            .order_by("order_index", "code")
        )


class ReferentialActivityTaskListView(generics.ListAPIView):
    serializer_class = ReferentialTaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ReferentialTask.objects.filter(
            organisation_id=tenant_organisation_id(self.request),
            activity_id=self.kwargs["activity_id"],
            activity__referential_id=self.kwargs["ref_id"],
        ).order_by("order_index", "code")


class ReferentialItemTaskListView(generics.ListAPIView):
    serializer_class = ReferentialCompetencyTaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ReferentialCompetencyTask.objects.filter(
            organisation_id=tenant_organisation_id(self.request),
            referential_item_id=self.kwargs["item_id"],
            referential_item__referential_id=self.kwargs["ref_id"],
        ).select_related("task", "task__activity", "referential_item")


class ReferentialConfigView(APIView):
    """GET/PUT /groups/{group_id}/referential-config."""

    permission_classes = [IsAuthenticated]

    def get(self, request, group_id):
        group = get_object_or_404(Group, id=group_id, organisation_id=tenant_organisation_id(request))
        config = (
            ReferentialConfig.objects.select_related("referential", "scale")
            .filter(group=group, organisation_id=tenant_organisation_id(request))
            .first()
        )
        if not config:
            return Response({}, status=status.HTTP_200_OK)
        data = {
            "id": str(config.id),
            "referential": {
                "id": str(config.referential_id),
                "name": config.referential.name,
                "source_ref": config.referential.source_ref,
            },
            "scale": None,
        }
        if config.scale_id:
            data["scale"] = {
                "id": str(config.scale_id),
                "name": config.scale.name,
            }
        return Response(data)

    def put(self, request, group_id):
        group = get_object_or_404(Group, id=group_id, organisation_id=tenant_organisation_id(request))
        referential_id = request.data.get("referential_id")
        scale_id = request.data.get("scale_id")
        if not referential_id:
            return Response({"detail": "referential_id required."}, status=status.HTTP_400_BAD_REQUEST)
        ref = get_object_or_404(Referential, id=referential_id, organisation_id=tenant_organisation_id(request))
        scale = None
        if scale_id:
            scale = get_object_or_404(Scale, id=scale_id, organisation_id=tenant_organisation_id(request))
        config, _ = ReferentialConfig.objects.update_or_create(
            group=group,
            referential=ref,
            defaults={"organisation_id": tenant_organisation_id(request), "scale": scale},
        )
        return Response({"id": str(config.id)})


class ReferentialItemOverlayView(APIView):
    """PUT /groups/{group_id}/referentials/{ref_id}/items/{item_id}/overlay."""

    permission_classes = [IsAuthenticated]

    def put(self, request, group_id, ref_id, item_id):
        group = get_object_or_404(Group, id=group_id, organisation_id=tenant_organisation_id(request))
        item = get_object_or_404(
            ReferentialItem,
            id=item_id,
            referential_id=ref_id,
            referential__organisation_id=tenant_organisation_id(request),
        )
        overlay, _ = ReferentialItemOverlay.objects.update_or_create(
            group=group,
            referential_item=item,
            defaults={
                "organisation_id": tenant_organisation_id(request),
                "enabled": request.data.get("enabled", True),
                "example_situations": request.data.get("example_situations", []),
                "example_evidence": request.data.get("example_evidence", []),
                "common_mistakes": request.data.get("common_mistakes", []),
                "coach_questions": request.data.get("coach_questions", []),
                "linked_documents": request.data.get("linked_documents", []),
            },
        )
        return Response({"id": str(overlay.id)})
