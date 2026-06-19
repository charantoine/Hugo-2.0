from rest_framework import serializers
from .models import (
    Group,
    GroupMembership,
    TutorLearnerLink,
    Referential,
    ReferentialItem,
    ReferentialCriterion,
    ReferentialActivity,
    ReferentialTask,
    ReferentialCompetencyTask,
)


class GroupSerializer(serializers.ModelSerializer):
    def validate_phase_classifier_min_confidence(self, value):
        if value is None:
            return value
        if value < 0 or value > 1:
            raise serializers.ValidationError("Must be between 0 and 1.")
        return value

    def validate_phase_classifier_max_tokens(self, value):
        if value is None:
            return value
        if value <= 0:
            raise serializers.ValidationError("Must be greater than 0.")
        return value

    def validate_phase_classifier_max_input_chars(self, value):
        if value is None:
            return value
        if value <= 0:
            raise serializers.ValidationError("Must be greater than 0.")
        return value

    def validate_p0_classifier_min_confidence(self, value):
        if value is None:
            return value
        if value < 0 or value > 1:
            raise serializers.ValidationError("Must be between 0 and 1.")
        return value

    def validate_p0_classifier_max_tokens(self, value):
        if value is None:
            return value
        if value <= 0:
            raise serializers.ValidationError("Must be greater than 0.")
        return value

    def validate_p0_classifier_max_input_chars(self, value):
        if value is None:
            return value
        if value <= 0:
            raise serializers.ValidationError("Must be greater than 0.")
        return value

    def validate_learner_display_profile(self, value):
        allowed = {"youth", "adult", "professional"}
        normalized = str(value or "professional").strip().lower()
        if normalized not in allowed:
            raise serializers.ValidationError("Must be one of: youth, adult, professional.")
        return normalized

    class Meta:
        model = Group
        fields = [
            "id",
            "name",
            "organisation_id",
            "llm_backend",
            "default_tutor_prompt",
            "learner_display_profile",
            "phase_classifier_enabled",
            "phase_classifier_max_tokens",
            "phase_classifier_min_confidence",
            "phase_classifier_max_input_chars",
            "p0_classifier_enabled",
            "p0_classifier_max_tokens",
            "p0_classifier_min_confidence",
            "p0_classifier_max_input_chars",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "organisation_id", "created_at", "updated_at"]


class GroupMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMembership
        fields = ["id", "group", "user", "created_at"]
        # `group` is inferred from the URL (/groups/<group_id>/members/) and
        # set in the view's `perform_create`, so it should not be required
        # in the payload.
        read_only_fields = ["id", "created_at", "group"]


class TutorLearnerLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = TutorLearnerLink
        fields = ["id", "group", "tutor", "learner", "created_at"]
        read_only_fields = ["id", "created_at", "group"]


class ReferentialSerializer(serializers.ModelSerializer):
    items_count = serializers.IntegerField(read_only=True)
    activities_count = serializers.IntegerField(read_only=True)
    tasks_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Referential
        fields = [
            "id",
            "name",
            "source_ref",
            "created_at",
            "updated_at",
            "items_count",
            "activities_count",
            "tasks_count",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "items_count",
            "activities_count",
            "tasks_count",
        ]


class ReferentialCriterionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferentialCriterion
        fields = [
            "id",
            "referential_item",
            "code",
            "label",
            "order_index",
            "expected_evidence",
            "question_seeds",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "referential_item"]


class ReferentialActivitySerializer(serializers.ModelSerializer):
    tasks_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ReferentialActivity
        fields = [
            "id",
            "referential",
            "code",
            "label",
            "order_index",
            "tasks_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "referential", "tasks_count"]


class ReferentialTaskSerializer(serializers.ModelSerializer):
    activity_code = serializers.CharField(source="activity.code", read_only=True)
    activity_label = serializers.CharField(source="activity.label", read_only=True)

    class Meta:
        model = ReferentialTask
        fields = [
            "id",
            "activity",
            "activity_code",
            "activity_label",
            "code",
            "label",
            "order_index",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "activity_code", "activity_label"]


class ReferentialCompetencyTaskSerializer(serializers.ModelSerializer):
    task_code = serializers.CharField(source="task.code", read_only=True)
    task_label = serializers.CharField(source="task.label", read_only=True)
    activity_code = serializers.CharField(source="task.activity.code", read_only=True)
    activity_label = serializers.CharField(source="task.activity.label", read_only=True)

    class Meta:
        model = ReferentialCompetencyTask
        fields = [
            "id",
            "referential_item",
            "task",
            "task_code",
            "task_label",
            "activity_code",
            "activity_label",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ReferentialItemSerializer(serializers.ModelSerializer):
    criteria = ReferentialCriterionSerializer(many=True, read_only=True)
    tasks = serializers.SerializerMethodField()

    def get_tasks(self, obj):
        rows = (
            obj.competency_tasks.select_related("task", "task__activity")
            .order_by("task__activity__order_index", "task__order_index", "task__code")
        )
        return [
            {
                "code": row.task.code,
                "label": row.task.label,
                "activity_code": row.task.activity.code,
                "activity_label": row.task.activity.label,
            }
            for row in rows
        ]

    class Meta:
        model = ReferentialItem
        fields = [
            "id",
            "referential",
            "code",
            "title",
            "block_code",
            "block_label",
            "evaluation_criteria",
            "evaluation_modalities",
            "expected_evidence",
            "source_ref",
            "criteria",
            "tasks",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "referential", "criteria", "tasks"]
