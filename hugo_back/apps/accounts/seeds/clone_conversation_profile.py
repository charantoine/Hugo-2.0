"""Clone LearnerConversationGlobalProfile and related prompts from a source organisation."""
from __future__ import annotations

from django.db import transaction

from apps.hugo.models import (
    EvaluationPolicy,
    EvaluationPromptProfile,
    LearnerConversationGlobalProfile,
    TutorConductProfile,
    TutorPrompt,
)


def _copy_model_fields(instance, exclude: frozenset[str] | None = None):
    exclude = exclude or frozenset()
    data = {}
    for field in instance._meta.fields:
        if field.primary_key or field.name in exclude:
            continue
        data[field.name] = getattr(instance, field.name)
    return data


def clone_tutor_prompt(source: TutorPrompt, target_org_id) -> TutorPrompt:
    defaults = _copy_model_fields(source, exclude=frozenset({"organisation", "ovh_llm"}))
    defaults["organisation_id"] = target_org_id
    if source.ovh_llm_id and source.ovh_llm.organisation_id == target_org_id:
        defaults["ovh_llm_id"] = source.ovh_llm_id
    else:
        defaults["ovh_llm_id"] = None
    prompt, _ = TutorPrompt.objects.update_or_create(
        organisation_id=target_org_id,
        code=source.code,
        defaults=defaults,
    )
    return prompt


def clone_conduct_profile(source: TutorConductProfile, target_org_id) -> TutorConductProfile:
    defaults = _copy_model_fields(source, exclude=frozenset({"organisation"}))
    defaults["organisation_id"] = target_org_id
    profile, _ = TutorConductProfile.objects.update_or_create(
        organisation_id=target_org_id,
        posture=source.posture,
        defaults=defaults,
    )
    return profile


def clone_evaluation_prompt_profile(source: EvaluationPromptProfile, target_org_id) -> EvaluationPromptProfile:
    defaults = _copy_model_fields(source, exclude=frozenset({"organisation"}))
    defaults["organisation_id"] = target_org_id
    profile, _ = EvaluationPromptProfile.objects.update_or_create(
        organisation_id=target_org_id,
        code=source.code,
        defaults=defaults,
    )
    return profile


def clone_evaluation_policy(source: EvaluationPolicy, target_org_id, target_group_id=None) -> EvaluationPolicy | None:
    group_id = target_group_id if source.group_id else None
    defaults = _copy_model_fields(source, exclude=frozenset({"organisation", "group"}))
    defaults["organisation_id"] = target_org_id
    defaults["group_id"] = group_id
    policy, _ = EvaluationPolicy.objects.update_or_create(
        organisation_id=target_org_id,
        group_id=group_id,
        defaults=defaults,
    )
    return policy


@transaction.atomic
def clone_global_profile(
    source_profile: LearnerConversationGlobalProfile,
    target_org_id,
    *,
    target_name: str,
    target_group_id=None,
) -> LearnerConversationGlobalProfile:
    prompt_fields = (
        "diagnostic_tutor_prompt",
        "reflective_tutor_prompt",
        "knowledge_review_tutor_prompt",
    )
    conduct_fields = (
        "diagnostic_conduct_profile",
        "reflective_conduct_profile",
        "knowledge_review_conduct_profile",
    )
    cloned_prompts = {}
    for field in prompt_fields:
        source_prompt = getattr(source_profile, field)
        cloned_prompts[field] = (
            clone_tutor_prompt(source_prompt, target_org_id) if source_prompt else None
        )

    cloned_conduct = {}
    for field in conduct_fields:
        source_conduct = getattr(source_profile, field)
        cloned_conduct[field] = (
            clone_conduct_profile(source_conduct, target_org_id) if source_conduct else None
        )

    eval_prompt = None
    if source_profile.evaluation_prompt_profile:
        eval_prompt = clone_evaluation_prompt_profile(
            source_profile.evaluation_prompt_profile,
            target_org_id,
        )

    eval_policy = None
    if source_profile.evaluation_policy:
        eval_policy = clone_evaluation_policy(
            source_profile.evaluation_policy,
            target_org_id,
            target_group_id=target_group_id,
        )

    profile, _ = LearnerConversationGlobalProfile.objects.update_or_create(
        organisation_id=target_org_id,
        name=target_name,
        defaults={
            "description": source_profile.description,
            "status": source_profile.status,
            "is_default": True,
            **cloned_prompts,
            **cloned_conduct,
            "evaluation_prompt_profile": eval_prompt,
            "evaluation_policy": eval_policy,
        },
    )
    return profile


def resolve_source_profile(
    source_org,
    *,
    profile_name: str,
    source_group_name: str,
    source_learner_username: str,
):
    from apps.hugo.models import HugoSession
    from apps.referentials.models import Group
    from django.contrib.auth import get_user_model

    User = get_user_model()
    profile = (
        LearnerConversationGlobalProfile.objects.filter(
            organisation=source_org,
            name=profile_name,
        )
        .select_related(
            "diagnostic_tutor_prompt",
            "reflective_tutor_prompt",
            "knowledge_review_tutor_prompt",
            "diagnostic_conduct_profile",
            "reflective_conduct_profile",
            "knowledge_review_conduct_profile",
            "evaluation_prompt_profile",
            "evaluation_policy",
        )
        .first()
    )
    if profile:
        return profile, f"profile:{profile_name}"

    group = Group.objects.filter(organisation=source_org, name=source_group_name).first()
    if group and group.default_learner_conversation_profile_id:
        profile = LearnerConversationGlobalProfile.objects.filter(
            id=group.default_learner_conversation_profile_id,
        ).first()
        if profile:
            return profile, f"group:{source_group_name}"

    learner = User.objects.filter(username=source_learner_username, organisation=source_org).first()
    if learner:
        session = (
            HugoSession.objects.filter(learner=learner, organisation=source_org)
            .select_related("learner_conversation_profile", "group")
            .order_by("-updated_at")
            .first()
        )
        if session and session.learner_conversation_profile_id:
            profile = session.learner_conversation_profile
            return profile, f"learner_session:{source_learner_username}"

    return None, "not_found"
