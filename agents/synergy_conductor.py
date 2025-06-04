"""
synergy_conductor.py   – Phase 8-B
Adds:
 • Neural composite score (price + meme)
 • Meme-hype fast-path: if hype>90 & price<IDEAL*1.05, Wick may force BUY
"""
from __future__ import annotations

from .machiavelli_agent import machiavelli_agent_logic
from .tywin_agent import tywin_agent_logic
from .wick_agent import wick_agent_logic
from .ozymandias_agent import ozymandias_agent_logic
from core.ego_core.ego_core import apply_emotional_overlay

from core.scoring_engine.neural_score import compute_score   # NEW

# IDEAL_PRICE used for fast-path check
from core.scoring_engine.scoring_engine import IDEAL_PRICE


def synergy_conductor_init() -> None:
    print("[SynergyConductor] Initialized.")


def _meme_fast_path(market: dict) -> str | None:
    """Return 'BUY' if extreme hype && price not over-extended, else None."""
    hype  = market.get("meme_hype", 0.0)
    price = market.get("sol_price", 0.0)
    if hype > 90 and price < IDEAL_PRICE * 1.05:
        print("[SynergyConductor] 🚀 Meme-hype fast-path fires (hype>90)")
        return "BUY"
    return None


def synergy_conductor_run(market_data: dict, ego_state: str = "neutral") -> str:
    """
    Combine agent votes + neural score + ego overlay.
    """

    # ── 1 · Meme fast-path (highest priority) ──────────────────
    fast = _meme_fast_path(market_data)
    if fast:
        return apply_emotional_overlay(fast, ego_state)

    # ── 2 · Agent votes ────────────────────────────────────────
    signals = [
        machiavelli_agent_logic(market_data),
        tywin_agent_logic(market_data),
        wick_agent_logic(market_data),
        ozymandias_agent_logic(market_data),
    ]
    buy_cnt = signals.count("BUY")
    base_decision = "BUY" if buy_cnt >= 2 else "HOLD"

    # ── 3 · Neural score tilt ──────────────────────────────────
    score = compute_score(market_data)
    print(f"[SynergyConductor] NEURAL score: {score:.2f}")

    if score < 30:
        base_decision = "HOLD"                   # dampen buying in bad regimes
    elif score > 70 and base_decision == "HOLD":
        base_decision = "BUY"                    # allow FOMO buy

    # ── 4 · Ego overlay ────────────────────────────────────────
    return apply_emotional_overlay(base_decision, ego_state)
