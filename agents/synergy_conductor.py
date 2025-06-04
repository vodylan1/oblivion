# agents/synergy_conductor.py
"""
Synergy Conductor – Phase 9
────────────────────────────────────────────────────────────────────────────
• Combines votes from individual agents
• Tilts with neural composite score
• 🚀 Fast-path: BUY if meme-hype > 90 and price < 1.05 × IDEAL
• 🕵️ Johan meta-agent can damp / downgrade decisions
"""

from __future__ import annotations

# ── agent imports ─────────────────────────────────────────────────────────
from .machiavelli_agent import machiavelli_agent_logic
from .tywin_agent       import tywin_agent_logic
from .wick_agent        import wick_agent_logic
from .ozymandias_agent  import ozymandias_agent_logic
from .johan_agent       import johan_override          # NEW ✔

# ── core overlays / helpers ───────────────────────────────────────────────
from core.ego_core.ego_core           import apply_emotional_overlay
from core.scoring_engine.neural_score import compute_score
from core.scoring_engine.scoring_engine import IDEAL_PRICE


# ──────────────────────────────────────────────────────────────────────────
def synergy_conductor_init() -> None:
    print("[SynergyConductor] Initialized.")


# ------------------------------------------------------------------------- 
def _meme_fast_path(market: dict) -> str | None:
    """Return 'BUY' if extreme hype & not over-extended; else None."""
    hype  = market.get("meme_hype", 0.0)
    price = market.get("sol_price", 0.0)
    if hype > 90 and price < IDEAL_PRICE * 1.05:
        print("[SynergyConductor] 🚀 Meme-hype fast-path fires (hype>90)")
        return "BUY"
    return None


# ------------------------------------------------------------------------- 
def synergy_conductor_run(
    market_data : dict,
    ego_state   : str  = "neutral"
) -> str:
    """
    1) Meme fast-path          (highest priority)
    2) Majority vote of agents
    3) Neural score tilt
    4) Johan meta-agent override
    5) Ego overlay
    """
    # 1 ─ fast-path
    fp = _meme_fast_path(market_data)
    if fp:
        return apply_emotional_overlay(fp, ego_state)

    # 2 ─ agent votes
    signals = [
        machiavelli_agent_logic(market_data),
        tywin_agent_logic      (market_data),
        wick_agent_logic       (market_data),
        ozymandias_agent_logic (market_data),
    ]
    buy_votes = signals.count("BUY")
    base_decision = "BUY" if buy_votes >= 2 else "HOLD"

    # 3 ─ neural tilt
    score = compute_score(market_data)
    print(f"[SynergyConductor] NEURAL score: {score:.2f}")

    if score < 30:
        base_decision = "HOLD"
    elif score > 70 and base_decision == "HOLD":
        base_decision = "BUY"

    # 4 ─ Johan paranoia layer
    base_decision = johan_override(base_decision, signals, ego_state)

    # 5 ─ ego overlay and return
    return apply_emotional_overlay(base_decision, ego_state)
