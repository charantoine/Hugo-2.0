from django.test import SimpleTestCase

from apps.hugo.domain import tutor_profiles
from apps.hugo.domain.conversation_profile import (
    ConversationPosture,
    KnowledgeItemStatus,
    SessionMaturityLevel,
    UIState,
    deserialize_conversation_progress,
)
from apps.hugo.domain.schemas import P0_CORE_FIELDS, P0_LLM_FIELDS
from apps.hugo.services import posture_selector


class P0NonRegressionTests(SimpleTestCase):
    def test_ui_state_contract_does_not_expose_p0_fields(self):
        ui_keys = set(UIState().to_dict().keys())
        self.assertTrue(ui_keys.isdisjoint(P0_CORE_FIELDS))
        self.assertTrue(ui_keys.isdisjoint(P0_LLM_FIELDS))

    def test_enums_are_imported_from_canonical_module(self):
        self.assertIs(tutor_profiles.ConversationPosture, ConversationPosture)
        self.assertIs(posture_selector.ConversationPosture, ConversationPosture)

    def test_deserialize_conversation_progress_recovers_enums(self):
        progress = deserialize_conversation_progress(
            {
                "session_id": "session-1",
                "posture": "diagnostic",
                "active_branches": [
                    {
                        "branch_id": "b1",
                        "theme_label": "Circuit",
                        "objective_label": "exploration",
                        "exploration_level": "orange",
                    }
                ],
                "active_branches_count": 1,
                "overall_maturity": "green",
                "synthesis_eligible": True,
                "evaluation_eligible": True,
                "reason_codes": ["evaluation_eligible"],
            }
        )
        self.assertEqual(progress.posture, ConversationPosture.DIAGNOSTIC)
        self.assertEqual(progress.overall_maturity, SessionMaturityLevel.GREEN)
        self.assertEqual(progress.active_branches[0].exploration_level, SessionMaturityLevel.ORANGE)

    def test_knowledge_item_status_values_are_canonical(self):
        self.assertEqual(KnowledgeItemStatus.DECLARED.value, "declared")
        self.assertEqual(KnowledgeItemStatus.DERIVED_PROVISIONAL.value, "derived_provisional")
        self.assertEqual(KnowledgeItemStatus.VALIDATED_TRAINER.value, "validated_trainer")
