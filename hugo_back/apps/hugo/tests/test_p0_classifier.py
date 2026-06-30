from types import SimpleNamespace
from unittest.mock import patch

import pytest
from django.test import SimpleTestCase, override_settings
from django.urls import reverse

from apps.hugo.models import HugoMessage, HugoSession, TutorPrompt
from apps.hugo.services.hugo_orchestrator import build_hugo_turn
from apps.hugo.services.p0_classifier import (
    _extract_json_object,
    classify_p0_turn_state,
    resolve_p0_classifier_runtime_config,
)
from apps.hugo.services.turn_state_analyzer import analyze_turn_state


def _session_stub(
    *,
    backend: str = "ollama",
    message_count: int = 0,
    current_phase: str = "exploration",
    group_cfg: dict | None = None,
    session_cfg: dict | None = None,
):
    group_defaults = {
        "llm_backend": backend,
        "p0_classifier_enabled": None,
        "p0_classifier_max_tokens": None,
        "p0_classifier_min_confidence": None,
        "p0_classifier_max_input_chars": None,
    }
    if group_cfg:
        group_defaults.update(group_cfg)
    session_defaults = {
        "current_phase": current_phase,
        "messages": SimpleNamespace(count=lambda: message_count),
        "group": SimpleNamespace(**group_defaults),
        "p0_classifier_enabled": None,
        "p0_classifier_max_tokens": None,
        "p0_classifier_min_confidence": None,
        "p0_classifier_max_input_chars": None,
    }
    if session_cfg:
        session_defaults.update(session_cfg)
    return SimpleNamespace(**session_defaults)


def _ctx_stub(summary: str | None = None, traces: list[str] | None = None, docs: list[str] | None = None):
    return SimpleNamespace(
        learner_summary=summary,
        recent_traces_info=traces or [],
        class_documents=docs or [],
    )


class P0ClassifierRuntimeTests(SimpleTestCase):
    @override_settings(
        HUGO_P0_CLASSIFIER_ENABLED=True,
        HUGO_P0_CLASSIFIER_MAX_TOKENS=180,
        HUGO_P0_CLASSIFIER_MIN_CONFIDENCE=0.6,
        HUGO_P0_CLASSIFIER_MAX_INPUT_CHARS=900,
    )
    def test_runtime_resolver_uses_session_over_group_over_settings(self):
        session = _session_stub(
            group_cfg={
                "p0_classifier_enabled": False,
                "p0_classifier_max_tokens": 120,
                "p0_classifier_min_confidence": 0.45,
                "p0_classifier_max_input_chars": 650,
            },
            session_cfg={
                "p0_classifier_enabled": True,
                "p0_classifier_max_tokens": 90,
                "p0_classifier_min_confidence": 0.82,
                "p0_classifier_max_input_chars": 420,
            },
        )
        runtime_cfg, runtime_src = resolve_p0_classifier_runtime_config(session)
        self.assertEqual(runtime_cfg["p0_classifier_enabled"], True)
        self.assertEqual(runtime_cfg["p0_classifier_max_tokens"], 90)
        self.assertEqual(runtime_cfg["p0_classifier_min_confidence"], 0.82)
        self.assertEqual(runtime_cfg["p0_classifier_max_input_chars"], 420)
        self.assertEqual(runtime_src["effective"], "session")

    @override_settings(
        HUGO_P0_CLASSIFIER_ENABLED=False,
        HUGO_P0_CLASSIFIER_MAX_TOKENS=180,
        HUGO_P0_CLASSIFIER_MIN_CONFIDENCE=0.6,
        HUGO_P0_CLASSIFIER_MAX_INPUT_CHARS=900,
    )
    def test_runtime_resolver_uses_settings_fallback(self):
        runtime_cfg, runtime_src = resolve_p0_classifier_runtime_config(_session_stub())
        self.assertEqual(runtime_cfg["p0_classifier_enabled"], False)
        self.assertEqual(runtime_cfg["p0_classifier_max_tokens"], 180)
        self.assertEqual(runtime_cfg["p0_classifier_min_confidence"], 0.6)
        self.assertEqual(runtime_cfg["p0_classifier_max_input_chars"], 900)
        self.assertEqual(runtime_src["effective"], "settings")


class P0ClassifierUnitTests(SimpleTestCase):
    def test_extract_json_object_strips_markdown_fence(self):
        text = """Voici le resultat.
```json
{"confidence": 0.82, "episode_clarity": "low", "has_concrete_actions": false}
```
"""
        obj = _extract_json_object(text)
        self.assertIsNotNone(obj)
        self.assertEqual(obj.get("confidence"), 0.82)
        self.assertEqual(obj.get("episode_clarity"), "low")

    def test_extract_json_object_with_preamble(self):
        text = 'Analyse: {"confidence":0.5,"episode_clarity":"medium","has_concrete_actions":true,"problem_salience":"low","reflection_phase":"description","reflective_depth":"low","self_efficacy_signal":"neutral","affect_valence":"neutral","cognitive_load":"low","interaction_risk":"low","epistemic_balance":"balanced","zpd_estimate":"in","contradiction_status":"none"}'
        obj = _extract_json_object(text)
        self.assertIsNotNone(obj)
        self.assertEqual(obj.get("episode_clarity"), "medium")

    def test_classifier_returns_heuristic_state_when_disabled(self):
        session = _session_stub(session_cfg={"p0_classifier_enabled": False})
        ctx = _ctx_stub()
        user_input = {"content": "Je ne sais pas trop, c'etait vague."}
        heuristic_state = analyze_turn_state(session=session, user_input=user_input, ctx=ctx)

        result = classify_p0_turn_state(
            session=session,
            tutor_prompt=None,
            user_input=user_input,
            ctx=ctx,
            heuristic_state=heuristic_state,
        )

        self.assertEqual(result.source, "heuristic")
        self.assertEqual(result.fallback_reason, "classifier_desactive")
        self.assertEqual(result.turn_state.episode_clarity, heuristic_state.episode_clarity)

    @override_settings(HUGO_P0_CLASSIFIER_ENABLED=True)
    @patch("apps.hugo.services.p0_classifier.complete_with_provider")
    def test_classifier_merges_valid_json_and_recomputes_derived_fields(self, complete_mock):
        session = _session_stub(message_count=5)
        ctx = _ctx_stub(summary="progression stable", traces=["trace"], docs=["procedure"])
        user_input = {"content": "J'ai bien realise le branchement, mais je suis perdu et je doute."}
        heuristic_state = analyze_turn_state(session=session, user_input=user_input, ctx=ctx)
        complete_mock.return_value = (
            """
            {
              "confidence": 0.91,
              "episode_clarity": "high",
              "has_concrete_actions": true,
              "problem_salience": "high",
              "reflection_phase": "analysis",
              "reflective_depth": "medium",
              "self_efficacy_signal": "low",
              "affect_valence": "negative",
              "cognitive_load": "high",
              "interaction_risk": "medium",
              "epistemic_balance": "balanced",
              "zpd_estimate": "beyond",
              "contradiction_status": "none"
            }
            """,
            {"provider": "ollama", "model_used": "mistral", "request_payload": {"mock": True}, "raw_response": {"ok": True}},
        )

        result = classify_p0_turn_state(
            session=session,
            tutor_prompt=None,
            user_input=user_input,
            ctx=ctx,
            heuristic_state=heuristic_state,
        )

        self.assertEqual(result.source, "llm_classifier")
        self.assertEqual(result.turn_state.cognitive_load, "high")
        self.assertEqual(result.turn_state.action_feasibility, "low")
        self.assertTrue(result.turn_state.need_encouragement)
        self.assertEqual(result.source_by_field["cognitive_load"], "llm_classifier")
        self.assertNotIn("session_maturity", result.source_by_field)

    @override_settings(HUGO_P0_CLASSIFIER_ENABLED=True)
    @patch("apps.hugo.services.p0_classifier.complete_with_provider")
    def test_classifier_falls_back_when_json_is_invalid(self, complete_mock):
        session = _session_stub()
        ctx = _ctx_stub()
        user_input = {"content": "J'ai verifie puis j'ai choisi."}
        heuristic_state = analyze_turn_state(session=session, user_input=user_input, ctx=ctx)
        complete_mock.return_value = ("pas de json", {"provider": "ollama", "model_used": "mistral"})

        result = classify_p0_turn_state(
            session=session,
            tutor_prompt=None,
            user_input=user_input,
            ctx=ctx,
            heuristic_state=heuristic_state,
        )

        self.assertEqual(result.source, "heuristic")
        self.assertEqual(result.fallback_reason, "parse_invalide")
        self.assertEqual(result.turn_state.episode_clarity, heuristic_state.episode_clarity)

    @override_settings(HUGO_P0_CLASSIFIER_ENABLED=True)
    @patch("apps.hugo.services.p0_classifier.complete_with_provider")
    def test_classifier_llm_error_is_not_parse_invalide(self, complete_mock):
        session = _session_stub()
        ctx = _ctx_stub()
        user_input = {"content": "Bonjour."}
        heuristic_state = analyze_turn_state(session=session, user_input=user_input, ctx=ctx)
        complete_mock.return_value = (
            "",
            {"provider": "ovh_ai", "model_used": "mistral", "error": "timeout"},
        )

        result = classify_p0_turn_state(
            session=session,
            tutor_prompt=None,
            user_input=user_input,
            ctx=ctx,
            heuristic_state=heuristic_state,
        )

        self.assertEqual(result.source, "heuristic")
        self.assertEqual(result.fallback_reason, "llm_indisponible")


@pytest.mark.django_db
@override_settings(HUGO_P0_CLASSIFIER_ENABLED=True)
@patch("apps.hugo.services.p0_classifier.complete_with_provider")
def test_build_hugo_turn_uses_p0_llm_classifier_before_decision(
    complete_mock, django_user_model, organisation, group
):
    learner = django_user_model.objects.create(username="learner_p0_llm", organisation=organisation)
    tutor_prompt = TutorPrompt.objects.create(
        organisation=organisation,
        code="afest_p0_llm",
        name="AFEST P0 LLM",
        prompt_type=TutorPrompt.PromptType.AFEST_HUGO,
        is_default=True,
        system_template="{base_system_intro}\n{decision_block}",
        user_template="{situation_content}",
    )
    session = HugoSession.objects.create(
        organisation=organisation,
        learner=learner,
        group=group,
        tutor_prompt=tutor_prompt,
        phase_classifier_enabled=False,
        p0_classifier_enabled=True,
    )
    complete_mock.return_value = (
        """
        {
          "confidence": 0.88,
          "episode_clarity": "high",
          "has_concrete_actions": true,
          "problem_salience": "high",
          "reflection_phase": "analysis",
          "reflective_depth": "medium",
          "self_efficacy_signal": "neutral",
          "affect_valence": "neutral",
          "cognitive_load": "high",
          "interaction_risk": "low",
          "epistemic_balance": "balanced",
          "zpd_estimate": "in",
          "contradiction_status": "none"
        }
        """,
        {"provider": "ollama", "model_used": "mistral", "request_payload": {"mock": True}},
    )

    turn = build_hugo_turn(
        session,
        {"content": "J'ai choisi ce controle parce que le risque etait eleve sur le chantier."},
    )

    assert turn.p0_classifier["source"] == "llm_classifier"
    assert turn.turn_state.cognitive_load == "high"
    assert turn.conversation_decision.question_style == "single_safe"


@pytest.mark.django_db
@override_settings(HUGO_P0_CLASSIFIER_ENABLED=True, HUGO_DEBUG_TRACING=True)
@patch("apps.hugo.views_sessions.complete_with_provider")
@patch("apps.hugo.services.p0_classifier.complete_with_provider")
def test_message_pipeline_persists_p0_classifier_trace(
    p0_mock, complete_mock, api_client, django_user_model, organisation, group
):
    learner = django_user_model.objects.create_user(
        username="learner_p0_pipeline",
        password="pass",
        organisation=organisation,
    )
    tutor_prompt = TutorPrompt.objects.create(
        organisation=organisation,
        code="afest_p0_pipeline",
        name="AFEST P0 pipeline",
        prompt_type=TutorPrompt.PromptType.AFEST_HUGO,
        is_default=True,
        system_template="{base_system_intro}\n{response_constraints_block}",
        user_template="{situation_content}",
    )
    session = HugoSession.objects.create(
        organisation=organisation,
        learner=learner,
        group=group,
        tutor_prompt=tutor_prompt,
        phase_classifier_enabled=False,
        p0_classifier_enabled=True,
    )
    p0_mock.return_value = (
        """
        {
          "confidence": 0.9,
          "episode_clarity": "medium",
          "has_concrete_actions": true,
          "problem_salience": "low",
          "reflection_phase": "analysis",
          "reflective_depth": "medium",
          "self_efficacy_signal": "neutral",
          "affect_valence": "neutral",
          "cognitive_load": "medium",
          "interaction_risk": "low",
          "epistemic_balance": "balanced",
          "zpd_estimate": "in",
          "contradiction_status": "none"
        }
        """,
        {"provider": "ollama", "model_used": "mistral", "request_payload": {"mock_p0": True}, "raw_response": {"p0": True}},
    )
    complete_mock.return_value = (
        "Que s'est-il passe ensuite ?",
        {"provider": "ollama", "model_used": "mistral", "request_payload": {"mock_reply": True}, "raw_response": {"reply": True}},
    )

    api_client.force_authenticate(user=learner)
    url = reverse("message_list_create", kwargs={"session_id": str(session.id)})
    response = api_client.post(
        url,
        {"content": "J'ai verifie le tableau puis j'ai choisi un controle."},
        format="json",
    )

    assert response.status_code == 200
    learner_msg = HugoMessage.objects.filter(session=session, role=HugoMessage.Role.LEARNER).latest("created_at")
    p0_payload = learner_msg.llm_request_payload["p0_classifier"]
    assert p0_payload["source"] == "llm_classifier"
    assert p0_payload["request_payload"] == {"mock_p0": True}
    assert p0_payload["raw_response"] == {"p0": True}
