"""
agents/johan_agent.py
────────────────────────────────────────────────────────────────────────────
Johan Liebert – meta-agent / paranoia filter (V1)

• Computes a 0-1 “paranoia score” from three signals  
    ① agent group-think ratio  
    ② recent loss streak  
    ③ current emotional state (rage / fear)

• Maps that score to one of three actions
      0.00-0.39  → no interference
      0.40-0.69  → damp BUY ⇒ BUY_LOW_CONF
      0.70-1.00  → force HOLD

Execution-engine treats BUY_LOW_CONF as a half-size BUY (mock/dev-net),
or a normal BUY on main-net once live routing is added.
"""
from __future__ import annotations

from typing import List

from core.ego_core.ego_core import EgoState, apply_emotional_overlay
from core.reflection_engine.reflection_engine import trade_history

# --------------------------------------------------------------------------- #
def _recent_loss_streak(n: int = 3) -> bool:
    """True if LAST *n* trades all lost money."""
    if len(trade_history) < n:
        return False
    return all(t["profit_loss"] < 0 for t in trade_history[-n:])


def paranoia_score(agent_votes: List[str], emotional_state: str) -> float:
    """
    Return a float ∈ [0,1].  >0.7 means high risk.
    """
    buy_ratio = agent_votes.count("BUY") / max(len(agent_votes), 1)
    group_think = 1.0 if buy_ratio >= 0.75 else 0.0

    loss_streak = 1.0 if _recent_loss_streak() else 0.0

    emo_flag = 1.0 if emotional_state.lower() in (EgoState.RAGE, EgoState.FEAR) else 0.0

    score = 0.3 * group_think + 0.3 * loss_streak + 0.3 * emo_flag
    return min(score, 1.0)


def johan_override(base_decision: str,
                   agent_votes: List[str],
                   emotional_state: str) -> str:
    """
    Return possibly modified decision:
        • “BUY_LOW_CONF”  (means scale size)
        • “HOLD”
        • original base_decision
    """
    p = paranoia_score(agent_votes, emotional_state)

    if p >= 0.7 and base_decision == "BUY":
        print("[Johan] PARANOIA HIGH → FORCE_HOLD")
        return "HOLD"

    if p >= 0.4 and base_decision == "BUY":
        print("[Johan] PARANOIA MED  → BUY_LOW_CONF")
        return "BUY_LOW_CONF"

    return base_decision
