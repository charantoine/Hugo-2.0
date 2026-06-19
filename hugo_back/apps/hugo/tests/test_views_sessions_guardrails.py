from django.test import SimpleTestCase

from apps.hugo.models import TutorPrompt
from apps.hugo.views_sessions import (
    _apply_output_guardrails,
    _apply_meta_response_guardrail,
    _build_indexed_alignment_content,
    _derive_output_mode,
    _parse_indexed_lines,
    _truncate_numbered_questions,
)


class ViewsSessionsGuardrailsTests(SimpleTestCase):
    def test_truncate_numbered_questions_respects_limit(self):
        text = "1. Question A ?\n2. Question B ?\n3. Question C ?"
        result = _truncate_numbered_questions(text, 2)
        self.assertEqual(result, "1. Question A ?\n2. Question B ?")

    def test_phase_forces_reflection_mode(self):
        mode = _derive_output_mode(
            TutorPrompt.OutputFormatMode.MULTI_QUESTION_NUMBERED,
            "potential_closure",
            2,
        )
        self.assertEqual(mode, TutorPrompt.OutputFormatMode.REFLECTION_BLOCK)

    def test_reflection_block_prompt_keeps_reflection_layout_when_cap_is_one(self):
        mode = _derive_output_mode(
            TutorPrompt.OutputFormatMode.REFLECTION_BLOCK,
            "exploration",
            1,
        )
        self.assertEqual(mode, TutorPrompt.OutputFormatMode.REFLECTION_BLOCK)

    def test_single_question_mode_has_priority(self):
        mode = _derive_output_mode(
            TutorPrompt.OutputFormatMode.SINGLE_QUESTION,
            "deepening",
            1,
        )
        self.assertEqual(mode, TutorPrompt.OutputFormatMode.SINGLE_QUESTION)

    def test_constraints_can_force_single_question_mode(self):
        mode = _derive_output_mode(
            TutorPrompt.OutputFormatMode.MULTI_QUESTION_NUMBERED,
            "deepening",
            2,
            question_style="single_safe",
            response_constraints=["single_question_only", "no_question_stacking"],
        )
        self.assertEqual(mode, TutorPrompt.OutputFormatMode.SINGLE_QUESTION)

    def test_reflection_block_is_short_and_question_capped(self):
        text = (
            "Tu sembles avoir priorise vite dans un contexte instable.\n"
            "Qu'as-tu observe en premier ?\n"
            "Pourquoi ce choix initial ?\n"
            "Que ferais-tu autrement ?"
        )
        result = _apply_output_guardrails(
            text=text,
            output_mode=TutorPrompt.OutputFormatMode.REFLECTION_BLOCK,
            max_questions=3,
        )
        self.assertIn("Tu sembles avoir priorise vite", result)
        self.assertIn("1. Qu'as-tu observe en premier ?", result)
        self.assertIn("2. Pourquoi ce choix initial ?", result)
        self.assertNotIn("Que ferais-tu autrement", result)

    def test_reflection_block_keeps_short_tone_with_one_question(self):
        text = (
            "C'est toujours un choc quand un gros court-circuit arrive.\n"
            "Peux-tu me dire ce qui t'a fait penser qu'il fallait changer cette prise ?\n"
            "Qu'as-tu verifie avant de couper l'alimentation ?"
        )
        result = _apply_output_guardrails(
            text=text,
            output_mode=TutorPrompt.OutputFormatMode.REFLECTION_BLOCK,
            max_questions=1,
        )
        self.assertIn("C'est toujours un choc quand un gros court-circuit arrive.", result)
        self.assertIn("1. Peux-tu me dire ce qui t'a fait penser qu'il fallait changer cette prise ?", result)
        self.assertNotIn("Qu'as-tu verifie avant de couper l'alimentation", result)

    def test_question_mode_extracts_two_questions_when_not_numbered(self):
        text = "Quelle etait ta contrainte principale ? Pourquoi ce choix ? Que verifier ensuite ?"
        result = _apply_output_guardrails(
            text=text,
            output_mode=TutorPrompt.OutputFormatMode.MULTI_QUESTION_NUMBERED,
            max_questions=2,
        )
        self.assertEqual(
            result,
            "1. Quelle etait ta contrainte principale ?\n2. Pourquoi ce choix ?",
        )

    def test_question_mode_with_one_question_does_not_inject_summary_line(self):
        text = (
            "C'est toujours un choc quand un gros court-circuit arrive.\n"
            "Peux-tu me dire ce qui t'a fait penser qu'il fallait changer cette prise ?\n"
            "Qu'as-tu verifie avant de couper l'alimentation ?"
        )
        result = _apply_output_guardrails(
            text=text,
            output_mode=TutorPrompt.OutputFormatMode.MULTI_QUESTION_NUMBERED,
            max_questions=1,
        )
        self.assertEqual(
            result,
            "1. Peux-tu me dire ce qui t'a fait penser qu'il fallait changer cette prise ?",
        )

    def test_single_safe_style_shortens_question(self):
        text = (
            "Peux-tu me decrire tres precisement ce qui s'est passe, dans quel ordre, "
            "avec quelles contraintes et ce que tu voulais verifier en premier sur le chantier ?"
        )
        result = _apply_output_guardrails(
            text=text,
            output_mode=TutorPrompt.OutputFormatMode.SINGLE_QUESTION,
            max_questions=2,
            question_style="single_safe",
            response_constraints=["single_question_only"],
        )
        self.assertIn("Peux-tu me decrire tres precisement ce qui s'est passe", result)
        self.assertLessEqual(len(result), 141)

    def test_no_question_guardrail_keeps_only_non_question_text(self):
        text = "D'accord, on peut s'arreter ici.\nVeux-tu ajouter quelque chose ?"
        result = _apply_output_guardrails(
            text=text,
            output_mode=TutorPrompt.OutputFormatMode.REFLECTION_BLOCK,
            max_questions=0,
            question_style="no_question",
            response_constraints=["no_question_final"],
        )
        self.assertEqual(result, "D'accord, on peut s'arreter ici.")

    def test_meta_guardrail_replaces_internal_prompt_leak(self):
        result = _apply_meta_response_guardrail(
            reply="Je vois que vous me demandez de rebondir sur le dernier message de l'apprenant.",
            turn_state={"closure_signal": "explicit"},
            conversation_decision={"should_close": True, "number_of_questions": 0},
        )
        self.assertEqual(result, "D'accord, on peut s'arrêter ici.")

    def test_parse_indexed_lines_supports_colon_and_spaces(self):
        text = "1: oui\n2 : non\n3- peut-etre"
        parsed = _parse_indexed_lines(text)
        self.assertEqual(parsed[1], "oui")
        self.assertEqual(parsed[2], "non")
        self.assertEqual(parsed[3], "peut-etre")

    def test_build_indexed_alignment_content_pairs_answers_to_previous_questions(self):
        prev = "1. As-tu verifie le disjoncteur ?\n2. As-tu controle la terre ?"
        learner = "1 oui, 16A\n2 non, pas de terre"
        enriched, meta = _build_indexed_alignment_content(learner, prev)
        self.assertTrue(meta["applied"])
        self.assertEqual(meta["pairs_count"], 2)
        self.assertIn("Q1: As-tu verifie le disjoncteur ?", enriched)
        self.assertIn("R2: non, pas de terre", enriched)

    def test_build_indexed_alignment_content_ignores_unmatched_indexes(self):
        prev = "1. Question une ?"
        learner = "2 non"
        enriched, meta = _build_indexed_alignment_content(learner, prev)
        self.assertFalse(meta["applied"])
        self.assertEqual(meta["pairs_count"], 0)
        self.assertEqual(enriched, learner)

    def test_truncate_numbered_questions_removes_double_numbering(self):
        text = "1. 1. Question A ?\n2. 2) Question B ?"
        result = _truncate_numbered_questions(text, 2)
        self.assertEqual(result, "1. Question A ?\n2. Question B ?")
