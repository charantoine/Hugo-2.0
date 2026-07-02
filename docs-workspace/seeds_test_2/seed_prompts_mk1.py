# Source extraite de: DB locale (config.settings.dev), apps/accounts/seeds/clone_conversation_profile.py
# Date: 2026-07-02
# Auteur: CTO kit
#
# Usage:
#   python manage.py shell < ../docs-workspace/seeds_test_2/seed_prompts_mk1.py

from apps.accounts.models import Organisation
from apps.hugo.models import LearnerConversationGlobalProfile, TutorPrompt


PROMPT_CODES = ("buchage_mk1", "diagnostic_mk1", "reflexif_mk1")
SOURCE_ORG_CANDIDATES = ("Demo Hugo Org", "OF_test_2")

TARGETS = [
    {"organisation_name": "Demo Hugo Org", "profile_name": "profil_conversationnel_mk1", "is_default": False},
    {"organisation_name": "OF_test_2", "profile_name": "profil_conversationnel_mk1", "is_default": True},
]


def _copy_prompt_from_source(target_org: Organisation, source_prompt: TutorPrompt) -> tuple[TutorPrompt, bool]:
    prompt_fields = {
        "name",
        "description",
        "prompt_type",
        "is_default",
        "sot_profile",
        "default_session_phase",
        "conversation_profile",
        "output_format_mode",
        "system_template",
        "user_template",
        "language",
        "tone",
        "regulation_bias_task",
        "regulation_bias_reasoning",
        "regulation_bias_metacognition",
        "max_questions_per_turn",
        "max_tokens",
        "allow_lists",
        "metadata",
        "is_active",
    }
    defaults = {}
    for field in prompt_fields:
        defaults[field] = getattr(source_prompt, field)

    prompt, created = TutorPrompt.objects.update_or_create(
        organisation=target_org,
        code=source_prompt.code,
        defaults=defaults,
    )
    return prompt, created


def _resolve_source_prompts() -> dict[str, TutorPrompt]:
    for org_name in SOURCE_ORG_CANDIDATES:
        source_org = Organisation.objects.filter(name=org_name).first()
        if not source_org:
            continue
        prompts = TutorPrompt.objects.filter(organisation=source_org, code__in=PROMPT_CODES)
        found = {p.code: p for p in prompts}
        if all(code in found for code in PROMPT_CODES):
            return found
    raise RuntimeError(
        "Impossible de retrouver les prompts mk1 source. "
        "Verifier la presence de Demo Hugo Org ou OF_test_2 avec codes mk1."
    )


def run() -> None:
    source_prompts = _resolve_source_prompts()

    for target in TARGETS:
        org, _ = Organisation.objects.get_or_create(name=target["organisation_name"])
        by_code = {}
        for code in PROMPT_CODES:
            prompt, created = _copy_prompt_from_source(org, source_prompts[code])
            by_code[code] = prompt
            status = "created" if created else "updated"
            print(
                f"[seed_prompts_mk1] org={org.name} prompt={prompt.name} "
                f"code={prompt.code} status={status}"
            )

        _, profile_created = LearnerConversationGlobalProfile.objects.update_or_create(
            organisation=org,
            name=target["profile_name"],
            defaults={
                "status": LearnerConversationGlobalProfile.Status.ACTIVE,
                "is_default": target["is_default"],
                "diagnostic_tutor_prompt": by_code["diagnostic_mk1"],
                "reflective_tutor_prompt": by_code["reflexif_mk1"],
                "knowledge_review_tutor_prompt": by_code["buchage_mk1"],
            },
        )
        print(
            f"[seed_prompts_mk1] org={org.name} profile={target['profile_name']} "
            f"created={profile_created}"
        )


run()
