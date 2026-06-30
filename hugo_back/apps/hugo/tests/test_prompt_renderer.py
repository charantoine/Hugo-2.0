from types import SimpleNamespace
from uuid import uuid4

from django.test import SimpleTestCase

from apps.hugo.domain.schemas import TeachingPlan, CompetenceBrief
from apps.hugo.services.context_builder import HugoContext
from apps.hugo.services.prompt_renderer import render_with_tutor_prompt


class PromptRendererTests(SimpleTestCase):
    def test_render_injects_teaching_plan_and_competence_brief(self):
        tutor_prompt = SimpleNamespace(
            system_template=(
                "{base_system_intro}\n"
                "phase={session_phase}\n"
                "focus={ui_focus_label}\n"
                "maxq={max_questions_this_turn}"
            ),
            user_template=(
                "situation={situation_content}\n"
                "comp={focus_competence}\n"
                "crit={competence_brief}"
            ),
        )
        session = SimpleNamespace(organisation_id=uuid4(), id=uuid4())
        ctx = HugoContext(
            referential_name="RNCP Demo",
            referential_source_ref="RNCP-001",
            items_to_focus=[],
            items_already_covered=[],
            learner_summary="Progression stable",
            recent_traces_info=[],
            class_documents=[],
        )
        teaching_plan = TeachingPlan(
            conversation_profile="reflective_afest",
            session_phase="exploration",
            focus_competence={"item_id": "i1", "label": "Analyser la situation"},
            learning_stage="intermediate",
            expected_level_now="participe",
            current_level="intermediate",
            coverage_status="ok",
            regulation_targets={"task": 0.3, "reasoning": 0.5, "metacognition": 0.2},
            open_action_items=[],
            critical_mistakes=[],
            coach_questions_candidates=[],
            rag_mode="none",
            ui_focus_label="Analyser les decisions prises",
            max_questions_this_turn=2,
        )
        competence_brief = CompetenceBrief(
            item_id="i1",
            label="Analyser la situation",
            key_criteria=["Identifier le contexte"],
            expected_evidence=["Preuve de priorisation"],
            critical_mistakes=[],
            typical_situations=[],
            preferred_coach_questions=[],
        )

        rendered = render_with_tutor_prompt(
            tutor_prompt=tutor_prompt,
            session=session,
            ctx=ctx,
            content="J'ai gere un incident",
            teaching_plan=teaching_plan,
            competence_brief=competence_brief,
        )

        self.assertIn("phase=exploration", rendered.system_prompt)
        self.assertIn("maxq=2", rendered.system_prompt)
        self.assertIn("Analyser les decisions prises", rendered.system_prompt)
        self.assertIn("J'ai gere un incident", rendered.user_prompt)
        self.assertIn("Analyser la situation", rendered.user_prompt)

    def test_render_injects_focus_guidance_into_referential_block(self):
        tutor_prompt = SimpleNamespace(
            system_template="{referential_block}",
            user_template="{situation_content}",
        )
        session = SimpleNamespace(organisation_id=uuid4(), id=uuid4())
        ctx = HugoContext(
            referential_name="RNCP Demo",
            referential_source_ref="RNCP-001",
            items_to_focus=[
                SimpleNamespace(
                    id="item-1",
                    code="C1",
                    title="Installer un equipement",
                    evaluation_criteria=["Verifier la compatibilite electrique", "Verifier la mise a la terre"],
                    expected_evidence=["Mesure de puissance totale"],
                )
            ],
            items_already_covered=[],
            learner_summary="Progression stable",
            recent_traces_info=[],
            class_documents=[],
        )
        teaching_plan = TeachingPlan(
            conversation_profile="reflective_afest",
            session_phase="exploration",
            focus_competence={
                "item_id": "item-1",
                "label": "Installer un equipement",
                "criterion_code": "C1.1",
                "criterion_label": "Verifier la compatibilite electrique",
                "covered_criteria_codes": ["C1.0"],
            },
            learning_stage="intermediate",
            expected_level_now="participe",
            current_level="intermediate",
            coverage_status="partial",
            regulation_targets={"task": 0.2, "reasoning": 0.7, "metacognition": 0.1},
            open_action_items=["Confirmer le dimensionnement de la ligne"],
            critical_mistakes=[],
            coach_questions_candidates=[],
            rag_mode="none",
            ui_focus_label="Justifier ses choix",
            max_questions_this_turn=2,
            next_session_phase="conceptualization",
        )
        rendered = render_with_tutor_prompt(
            tutor_prompt=tutor_prompt,
            session=session,
            ctx=ctx,
            content="texte",
            teaching_plan=teaching_plan,
        )
        self.assertIn("Focalisation pedagogique du tour", rendered.system_prompt)
        self.assertIn("Competence focus : Installer un equipement", rendered.system_prompt)
        self.assertIn("Critere focus : C1.1 - Verifier la compatibilite electrique", rendered.system_prompt)
        self.assertIn("Regle anti-boucle", rendered.system_prompt)
        self.assertIn("Criteres prioritaires", rendered.system_prompt)
        self.assertIn("Preuve attendue prioritaire", rendered.system_prompt)
