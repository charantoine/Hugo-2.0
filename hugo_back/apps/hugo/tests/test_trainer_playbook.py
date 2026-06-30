"""Tests for trainer playbook resolver and prompt injection."""
from types import SimpleNamespace

from django.test import TestCase

from apps.accounts.models import Organisation, Role, User
from apps.hugo.domain.conversation_profile import KnowledgeItemStatus
from apps.hugo.models import TrainerKnowledgeItem, HugoSession
from apps.hugo.services.prompt_renderer import render_with_tutor_prompt
from apps.hugo.services.trainer_playbook_resolver import load_trainer_playbook_for_session
from apps.referentials.models import Group


class TrainerPlaybookResolverTests(TestCase):
    def setUp(self):
        self.organisation = Organisation.objects.create(name="Org Playbook")
        self.group = Group.objects.create(organisation=self.organisation, name="G1")
        self.other_group = Group.objects.create(organisation=self.organisation, name="G2")
        self.learner = User.objects.create_user(
            username="learner_pb",
            password="pass",
            organisation=self.organisation,
            role=Role.LEARNER,
        )

    def test_load_validated_items_for_session_group(self):
        TrainerKnowledgeItem.objects.create(
            organisation=self.organisation,
            content="Ne pas oublier la consignation.",
            content_type="reference_rule",
            status=KnowledgeItemStatus.VALIDATED_TRAINER.value,
            meta={"situation_cue": "oubli consignation", "desired_response": "rappeler la procédure"},
        )
        TrainerKnowledgeItem.objects.create(
            organisation=self.organisation,
            content="Item autre groupe",
            content_type="frequent_error",
            status=KnowledgeItemStatus.VALIDATED_TRAINER.value,
            meta={"scope_group_ids": [str(self.other_group.id)]},
        )
        TrainerKnowledgeItem.objects.create(
            organisation=self.organisation,
            content="Non validé",
            content_type="frequent_error",
            status=KnowledgeItemStatus.DECLARED.value,
        )
        session = HugoSession.objects.create(
            organisation=self.organisation,
            group=self.group,
            learner=self.learner,
        )
        playbook = load_trainer_playbook_for_session(session)
        self.assertFalse(playbook.is_empty())
        self.assertIn("consignation", playbook.block_text.lower())
        self.assertEqual(len(playbook.items), 1)

    def test_scoped_item_included_when_group_matches(self):
        TrainerKnowledgeItem.objects.create(
            organisation=self.organisation,
            content="Erreur fréquente X",
            content_type="frequent_error",
            status=KnowledgeItemStatus.VALIDATED_TRAINER.value,
            meta={
                "scope_group_ids": [str(self.group.id)],
                "situation_cue": "erreur X",
                "desired_response": "reformuler et guider",
            },
        )
        session = HugoSession.objects.create(
            organisation=self.organisation,
            group=self.group,
            learner=self.learner,
        )
        playbook = load_trainer_playbook_for_session(session)
        self.assertIn("erreur X", playbook.block_text)
        self.assertIn("reformuler", playbook.block_text)


class PromptPlaybookInjectionTests(TestCase):
    def test_render_with_tutor_prompt_includes_playbook_block(self):
        from types import SimpleNamespace

        tutor_prompt = SimpleNamespace(
            system_template="{base_system_intro}\n\n{documents_block}",
            user_template="{situation_content}",
        )
        session = SimpleNamespace(id="s1", organisation_id="o1", group_id="g1", learner_id="l1")
        ctx = SimpleNamespace(
            referential_name="",
            referential_source_ref="",
            items_to_focus=[],
            items_already_covered=[],
            learner_summary="",
            recent_traces_info=[],
            class_documents=[],
            referential_block="",
            learner_block="",
            documents_block="",
            history_block="",
            situation_content="message apprenant",
            learner_name="Apprenant",
            group_name="Groupe",
        )
        block = "Consignes formateur (bloc interne) :\n- [frequent_error] Ne pas confondre phase et neutre"
        rendered = render_with_tutor_prompt(
            tutor_prompt=tutor_prompt,
            session=session,
            ctx=ctx,
            content="message apprenant",
            trainer_playbook_block=block,
        )
        self.assertIn("Consignes formateur", rendered.system_prompt)
        self.assertIn("frequent_error", rendered.system_prompt)
