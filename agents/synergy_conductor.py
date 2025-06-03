"""
synergy_conductor.py

Now includes a scoring step from SCORING_ENGINE in deciding final action.
"""

from .machiavelli_agent import machiavelli_agent_logic
from .tywin_agent import tywin_agent_logic
from .wick_agent import wick_agent_logic
from .ozymandias_agent import ozymandias_agent_logic
from core.ego_core.ego_core import apply_emotional_overlay

# NEW import
from core.scoring_engine.scoring_engine import compute_score

def synergy_conductor_init():
    """Initialize synergy conductor (placeholder)."""
    print("[SynergyConductor] Initialized.")

def synergy_conductor_run(market_data: dict, emotional_state: str = "neutral"):
    """
    Phase 4: 
    1) Use agent logic to see if there's a 'BUY' majority.
    2) Also compute a SCORING_ENGINE score. 
    3) Final decision depends on both the agent majority AND the scoring result.
    4) Then apply EGO_CORE overlay.
    """

    # Agent signals
    signals = []
    signals.append(machiavelli_agent_logic(market_data))
    signals.append(tywin_agent_logic(market_data))
    signals.append(wick_agent_logic(market_data))
    signals.append(ozymandias_agent_logic(market_data))

    buy_count = signals.count("BUY")
    # hold_count = signals.count("HOLD")  # not strictly needed now

    # Basic agent-based decision
    if buy_count >= 2:
        agent_decision = "BUY"
    else:
        agent_decision = "HOLD"

    # SCORING_ENGINE step
    score = compute_score(market_data)
    print(f"[SynergyConductor] SCORING_ENGINE score: {score:.2f}")

    # If score > 50, we lean buy, else lean hold
    if score > 50:
        final_decision = "BUY" if agent_decision == "BUY" else "HOLD"
    else:
        # Even if agents want to buy, if score < 20 let's override to HOLD
        # or you can pick your own logic
        if score < 20:
            final_decision = "HOLD"
        else:
            final_decision = agent_decision

    # EGO_CORE overlay
    final_decision = apply_emotional_overlay(final_decision, emotional_state)

    return final_decision
