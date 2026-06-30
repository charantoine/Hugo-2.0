import uuid

import pytest
from django.utils import timezone

from apps.hugo.models import HugoSession, TutorPrompt
from apps.hugo.services.context_builder import HugoContext, build_afest_prompts


@pytest.mark.django_db
def test_build_afest_prompts_fallbacks_to_legacy_when_no_tutorprompt(django_user_model, organisation, group):
    learner = django_user_model.objects.create(username="learner1", organisation=organisation)
    session = HugoSession.objects.create(
        organisation=organisation,
        learner=learner,
        group=group,
    )
    ctx = HugoContext(
        referential_name=None,
        referential_source_ref=None,
        items_to_focus=[],
        items_already_covered=[],
        learner_summary=None,
        recent_traces_info=[],
        class_documents=[],
    )
    system_legacy, user_legacy = build_afest_prompts(session, "Une situation", ctx)
    assert "Tu es Hugo, assistant AFEST pour un apprenant." in system_legacy
    assert "Situation décrite par l'apprenant" in user_legacy


@pytest.mark.django_db
def test_build_afest_prompts_uses_default_tutorprompt(django_user_model, organisation, group):
    learner = django_user_model.objects.create(username="learner2", organisation=organisation)
    session = HugoSession.objects.create(
        organisation=organisation,
        learner=learner,
        group=group,
    )
    tp = TutorPrompt.objects.create(
        id=uuid.uuid4(),
        organisation=organisation,
        code="default-afest",
        name="Default AFEST",
        description="Default AFEST prompt",
        prompt_type=TutorPrompt.PromptType.AFEST_HUGO,
        is_default=True,
        system_template="{base_system_intro}\n{referential_block}\n{learner_block}\n{documents_block}",
        user_template="Situation décrite par l'apprenant : {situation_content}",
        created_at=timezone.now(),
        updated_at=timezone.now(),
    )
    ctx = HugoContext(
        referential_name=None,
        referential_source_ref=None,
        items_to_focus=[],
        items_already_covered=[],
        learner_summary=None,
        recent_traces_info=[],
        class_documents=[],
    )
    system_prompt, user_prompt = build_afest_prompts(session, "Une nouvelle situation", ctx)
    assert "Default AFEST" not in system_prompt  # Only templates, not description
    assert "Une nouvelle situation" in user_prompt

