"""
synergy_conductor.py   – Phase 9
Adds:
 • Neural composite score (price + meme)
 • Meme-hype fast-path: if hype>90 & price<IDEAL*1.05, Wick may force BUY
 • Johan meta-agent override (paranoia dampening)
"""
from __future__ import annotations

from .machiavelli_agent import machiavelli_agent_logic
from .tywin_agent import tywin_agent_logic
from .wick_agent import wick_agent_logic
from .ozymandias_agent import ozymandias_agent_logic
from .johan_agent import johan_override                      # NEW ✅

from core.ego_core.ego_core import apply_emotional_overlay
from core.scoring_engine.neural_score import compute_score
from core.scoring_engine.scoring_engine import IDEAL_PRICE


# --------------------------------------------------------------------------- #
def synergy_conductor_init() -> None:
    print("[SynergyConductor] Initialized.")

# … _meme_fast_path() remains identical …

def synergy_conductor_run(market_data: dict, ego_state: str = "neutral") -> str:
    """Combine agent votes + neural score + Johan + ego overlay."""

    # 1 ─ Meme fast-path (highest prio) --------------------------------------
    fast = _meme_fast_path(market_data)
    if fast:
        return apply_emotional_overlay(fast, ego_state)

    # 2 ─ Agent votes --------------------------------------------------------
    signals = [
        machiavelli_agent_logic(market_data),
        tywin_agent_logic(market_data),
        wick_agent_logic(market_data),
        ozymandias_agent_logic(market_data),
    ]
    buy_cnt       = signals.count("BUY")
    base_decision = "BUY" if buy_cnt >= 2 else "HOLD"

    # 3 ─ Neural score tilt --------------------------------------------------
    score = compute_score(market_data)
    print(f"[SynergyConductor] NEURAL score: {score:.2f}")

    if score < 30:
        base_decision = "HOLD"
    elif score > 70 and base_decision == "HOLD":
        base_decision = "BUY"

    # 4 ─ Johan meta-filter --------------------------------------------------
▶   base_decision = johan_override(base_decision, signals, ego_state)

    # 5 ─ Ego overlay --------------------------------------------------------
    return apply_emotional_overlay(base_decision, ego_state)
