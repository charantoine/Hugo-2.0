from __future__ import annotations

from typing import Any, Optional
from uuid import uuid4

from apps.hugo.domain.conversation_profile import (
    ConversationBranch,
    ConversationPosture,
    ConversationProgress,
    SessionMaturityLevel,
    deserialize_conversation_progress,
)
from apps.hugo.domain.reason_codes import (
    RC_DISPERSION_RISK,
    RC_EVALUATION_BLOCKED_COGNITIVE_LOAD,
    RC_EVALUATION_BLOCKED_INTERACTION_RISK,
    RC_EVALUATION_BLOCKED_MATURITY,
    RC_EVALUATION_ELIGIBLE,
    RC_LOOP_RISK_HIGH,
    RC_NO_CAUSE_NAMED,
    RC_NO_CONCRETE_ACTIONS,
    RC_NO_TRANSFER_RULE,
    RC_NOT_ENOUGH_DESCRIPTION,
    RC_SYNTHESIS_BLOCKED_MATURITY,
    RC_SYNTHESIS_ELIGIBLE,
)
from apps.hugo.domain.tutor_profiles import MAX_ACTIVE_BRANCHES


def _as_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


class ConversationProgressCalculator:
    def __init__(self, posture: ConversationPosture = ConversationPosture.REFLECTIVE_AFEST):
        self.posture = posture

    def update(
        self,
        *,
        session_id: str,
        turn_state: Any,
        decision: Any,
        previous_progress: Optional[ConversationProgress] = None,
    ) -> ConversationProgress:
        previous = previous_progress or ConversationProgress(session_id=session_id, posture=self.posture)
        branches = self._update_branches(turn_state, previous.active_branches)
        active_count = len([branch for branch in branches if branch.is_active])
        dispersion_risk = active_count > MAX_ACTIVE_BRANCHES
        overall = self._compute_overall_maturity(branches)
        synthesis_eligible, evaluation_eligible = self._compute_eligibility(overall, turn_state)
        reason_codes = self._compute_reason_codes(turn_state, overall, dispersion_risk, synthesis_eligible, evaluation_eligible)
        return ConversationProgress(
            session_id=session_id,
            posture=self.posture,
            active_branches=branches,
            active_branches_count=active_count,
            priority_branch_id=self._elect_priority_branch(branches),
            dispersion_risk=dispersion_risk,
            overall_maturity=overall,
            synthesis_eligible=synthesis_eligible,
            evaluation_eligible=evaluation_eligible,
            missing_for_next_level=self._missing_for_next_level(turn_state, overall),
            reason_codes=reason_codes,
        )

    def _update_branches(self, turn_state: Any, previous_branches: list[ConversationBranch]) -> list[ConversationBranch]:
        branches = list(previous_branches or [])
        theme_label = str(getattr(turn_state, "conversation_goal", "") or "").strip()
        objective_label = str(getattr(turn_state, "current_phase", "") or getattr(turn_state, "session_phase", "") or "").strip()
        if not theme_label:
            theme_label = "Progression de séance"
        if not objective_label:
            objective_label = "exploration"

        existing = next(
            (
                branch
                for branch in branches
                if branch.theme_label == theme_label and branch.objective_label == objective_label and branch.is_active
            ),
            None,
        )
        if existing is None:
            existing = ConversationBranch(
                branch_id=str(uuid4()),
                theme_label=theme_label,
                objective_label=objective_label,
                exploration_level=SessionMaturityLevel.RED,
                is_active=True,
            )
            branches.append(existing)

        existing.exploration_level = self._branch_maturity(turn_state)
        existing.reason_codes = self._branch_reason_codes(turn_state)

        allowed_active = 1 if self.posture == ConversationPosture.KNOWLEDGE_REVIEW else MAX_ACTIVE_BRANCHES
        active_branches = [branch for branch in branches if branch.is_active]
        for branch in active_branches[allowed_active:]:
            branch.is_active = False
        return branches

    def _branch_maturity(self, turn_state: Any) -> SessionMaturityLevel:
        covered = set(_as_list(getattr(turn_state, "covered_points", [])))
        remaining = set(_as_list(getattr(turn_state, "remaining_open_points", [])))
        clarity = str(getattr(turn_state, "episode_clarity", "") or "").strip().lower()
        has_actions = bool(getattr(turn_state, "has_concrete_actions", False))
        has_cause = "cause_hypothesis_named" in covered or "cause_confirmed" in covered or "problem_named" in covered
        has_transfer = "future_action_named" in covered or "learning_rule_named" in covered

        if self.posture == ConversationPosture.KNOWLEDGE_REVIEW:
            if clarity in {"high", "medium"} and not remaining:
                return SessionMaturityLevel.GREEN
            if clarity in {"high", "medium"}:
                return SessionMaturityLevel.ORANGE
            return SessionMaturityLevel.RED

        if self.posture == ConversationPosture.DIAGNOSTIC:
            if has_actions and has_cause and not remaining:
                return SessionMaturityLevel.GREEN
            if has_actions or has_cause or clarity in {"high", "medium"}:
                return SessionMaturityLevel.ORANGE
            return SessionMaturityLevel.RED

        if has_actions and has_cause and has_transfer and not remaining:
            return SessionMaturityLevel.GREEN
        if has_actions and (has_cause or clarity in {"high", "medium"}):
            return SessionMaturityLevel.ORANGE
        return SessionMaturityLevel.RED

    def _branch_reason_codes(self, turn_state: Any) -> list[str]:
        reason_codes: list[str] = []
        covered = set(_as_list(getattr(turn_state, "covered_points", [])))
        if str(getattr(turn_state, "episode_clarity", "") or "").strip().lower() in {"", "low", "faible"}:
            reason_codes.append(RC_NOT_ENOUGH_DESCRIPTION)
        if not bool(getattr(turn_state, "has_concrete_actions", False)):
            reason_codes.append(RC_NO_CONCRETE_ACTIONS)
        if "cause_hypothesis_named" not in covered and "cause_confirmed" not in covered and "problem_named" not in covered:
            reason_codes.append(RC_NO_CAUSE_NAMED)
        if (
            self.posture == ConversationPosture.REFLECTIVE_AFEST
            and "future_action_named" not in covered
            and "learning_rule_named" not in covered
        ):
            reason_codes.append(RC_NO_TRANSFER_RULE)
        return reason_codes

    def _elect_priority_branch(self, branches: list[ConversationBranch]) -> Optional[str]:
        active = [branch for branch in branches if branch.is_active]
        if not active:
            return None
        order = {
            SessionMaturityLevel.RED: 3,
            SessionMaturityLevel.ORANGE: 2,
            SessionMaturityLevel.GREEN: 1,
        }
        return sorted(active, key=lambda branch: order.get(branch.exploration_level, 0), reverse=True)[0].branch_id

    def _compute_overall_maturity(self, branches: list[ConversationBranch]) -> SessionMaturityLevel:
        active = [branch for branch in branches if branch.is_active]
        if not active:
            return SessionMaturityLevel.RED
        levels = {branch.exploration_level for branch in active}
        if levels == {SessionMaturityLevel.GREEN}:
            return SessionMaturityLevel.GREEN
        if SessionMaturityLevel.ORANGE in levels or SessionMaturityLevel.GREEN in levels:
            return SessionMaturityLevel.ORANGE
        return SessionMaturityLevel.RED

    def _compute_eligibility(self, maturity: SessionMaturityLevel, turn_state: Any) -> tuple[bool, bool]:
        cognitive_load = str(getattr(turn_state, "cognitive_load", "") or "").strip().lower()
        interaction_risk = str(getattr(turn_state, "interaction_risk", "") or "").strip().lower()
        synthesis_eligible = maturity in {SessionMaturityLevel.ORANGE, SessionMaturityLevel.GREEN}
        evaluation_eligible = (
            maturity == SessionMaturityLevel.GREEN
            and cognitive_load not in {"high", "élevé", "eleve"}
            and interaction_risk not in {"high", "élevé", "eleve"}
        )
        return synthesis_eligible, evaluation_eligible

    def _missing_for_next_level(self, turn_state: Any, maturity: SessionMaturityLevel) -> list[str]:
        if maturity == SessionMaturityLevel.GREEN:
            return []
        missing: list[str] = []
        if str(getattr(turn_state, "episode_clarity", "") or "").strip().lower() in {"", "low", "faible"}:
            missing.append("Décrire plus précisément la situation.")
        if not bool(getattr(turn_state, "has_concrete_actions", False)):
            missing.append("Nommer des actions concrètes déjà réalisées.")
        covered = set(_as_list(getattr(turn_state, "covered_points", [])))
        if "cause_hypothesis_named" not in covered and "cause_confirmed" not in covered and "problem_named" not in covered:
            missing.append("Identifier une cause plausible ou un point qui bloque.")
        if self.posture == ConversationPosture.REFLECTIVE_AFEST and "future_action_named" not in covered:
            missing.append("Formuler une règle ou une prochaine action transférable.")
        return missing[:4]

    def _compute_reason_codes(
        self,
        turn_state: Any,
        maturity: SessionMaturityLevel,
        dispersion_risk: bool,
        synthesis_eligible: bool,
        evaluation_eligible: bool,
    ) -> list[str]:
        reason_codes = self._branch_reason_codes(turn_state)
        loop_risk = str(getattr(turn_state, "loop_risk", "") or "").strip().lower()
        cognitive_load = str(getattr(turn_state, "cognitive_load", "") or "").strip().lower()
        interaction_risk = str(getattr(turn_state, "interaction_risk", "") or "").strip().lower()
        if loop_risk in {"high", "élevé", "eleve"}:
            reason_codes.append(RC_LOOP_RISK_HIGH)
        if dispersion_risk:
            reason_codes.append(RC_DISPERSION_RISK)
        if synthesis_eligible:
            reason_codes.append(RC_SYNTHESIS_ELIGIBLE)
        else:
            reason_codes.append(RC_SYNTHESIS_BLOCKED_MATURITY)
        if evaluation_eligible:
            reason_codes.append(RC_EVALUATION_ELIGIBLE)
        else:
            if maturity != SessionMaturityLevel.GREEN:
                reason_codes.append(RC_EVALUATION_BLOCKED_MATURITY)
            if cognitive_load in {"high", "élevé", "eleve"}:
                reason_codes.append(RC_EVALUATION_BLOCKED_COGNITIVE_LOAD)
            if interaction_risk in {"high", "élevé", "eleve"}:
                reason_codes.append(RC_EVALUATION_BLOCKED_INTERACTION_RISK)
        unique: list[str] = []
        for code in reason_codes:
            if code not in unique:
                unique.append(code)
        return unique


def build_conversation_progress_contract(
    *,
    session_id: str,
    turn_state: Any,
    decision: Any,
    posture: ConversationPosture,
    previous_progress_raw: Optional[dict[str, Any]] = None,
) -> ConversationProgress:
    calculator = ConversationProgressCalculator(posture=posture)
    previous_progress = deserialize_conversation_progress(previous_progress_raw)
    return calculator.update(
        session_id=session_id,
        turn_state=turn_state,
        decision=decision,
        previous_progress=previous_progress,
    )
