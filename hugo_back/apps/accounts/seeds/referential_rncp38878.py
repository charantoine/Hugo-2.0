"""Import RNCP38878 JSON payload into an organisation (idempotent by source_ref)."""
from __future__ import annotations

import json
from pathlib import Path

from apps.referentials.models import (
    Referential,
    ReferentialActivity,
    ReferentialCompetencyTask,
    ReferentialCriterion,
    ReferentialItem,
    ReferentialTask,
)


def _fixture_paths() -> list[Path]:
    root = Path(__file__).resolve().parents[3]
    return [
        root / "apps" / "referentials" / "fixtures" / "RNCP38878_enriched.json",
        root.parent / "docs-workspace" / "RNCP38878.json",
        root / "apps" / "referentials" / "fixtures" / "RNCP38878.json",
    ]


def resolve_rncp38878_json_path() -> Path:
    for path in _fixture_paths():
        if path.is_file():
            return path
    raise FileNotFoundError(
        "RNCP38878 fixture not found. Expected one of: "
        + ", ".join(str(p) for p in _fixture_paths())
    )


def find_referential_by_source_ref(organisation_id, source_ref: str) -> Referential | None:
    return (
        Referential.objects.filter(
            organisation_id=organisation_id,
            source_ref=source_ref,
        )
        .order_by("-created_at")
        .first()
    )


def import_referential_v2_payload(organisation_id, data: dict) -> Referential:
    """Mirror of POST /referentials/import-v2/ (no HTTP)."""

    def _stripped(value):
        return str(value or "").strip()

    def _normalize_task_code(value):
        return _stripped(value).upper()

    def _normalize_item_code(value):
        return _stripped(value).upper()

    name = data.get("name") or "Referential"
    source_ref = data.get("source_ref", "")
    ref = Referential.objects.create(
        organisation_id=organisation_id,
        name=name,
        source_ref=source_ref,
    )
    item_by_code = {}
    activity_by_code = {}
    task_by_code = {}
    items_data = data.get("items", [])

    for it in items_data:
        item = ReferentialItem.objects.create(
            organisation_id=organisation_id,
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
                    organisation_id=organisation_id,
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
            organisation_id=organisation_id,
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
                    organisation_id=organisation_id,
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
            organisation_id=organisation_id,
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
                organisation_id=organisation_id,
                referential_item=item,
                task=db_task,
            )

    for link in data.get("competency_tasks", []):
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
            organisation_id=organisation_id,
            referential_item=item,
            task=task,
        )
    return ref


def ensure_rncp38878_for_org(organisation_id, *, force_reimport: bool = False) -> Referential:
    existing = find_referential_by_source_ref(organisation_id, "RNCP38878")
    if existing and not force_reimport:
        return existing
    payload = json.loads(resolve_rncp38878_json_path().read_text(encoding="utf-8"))
    return import_referential_v2_payload(organisation_id, payload)
