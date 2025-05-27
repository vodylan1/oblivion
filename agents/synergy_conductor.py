"""
synergy_conductor.py

Now we import and apply EGO_CORE's emotional overlay in Phase 3.
"""

from .machiavelli_agent import machiavelli_agent_logic
from .tywin_agent import tywin_agent_logic
from .wick_agent import wick_agent_logic
from .ozymandias_agent import ozymandias_agent_logic
from core.ego_core.ego_core import apply_emotional_overlay

def synergy_conductor_init():
    """Initialize synergy conductor (placeholder)."""
    print("[SynergyConductor] Initialized.")

def synergy_conductor_run(market_data: dict, emotional_state: str = "neutral"):
    """
    Collect signals from each agent and output a final recommendation.
    Now we also apply an emotional overlay from EGO_CORE.
    """
    signals = []
    signals.append(machiavelli_agent_logic(market_data))
    signals.append(tywin_agent_logic(market_data))
    signals.append(wick_agent_logic(market_data))
    signals.append(ozymandias_agent_logic(market_data))

    buy_count = signals.count("BUY")
    hold_count = signals.count("HOLD")

    if buy_count >= 2:
        final_decision = "BUY"
    else:
        final_decision = "HOLD"

    # Apply EGO_CORE overlay
    final_decision = apply_emotional_overlay(final_decision, emotional_state)

    return final_decision
