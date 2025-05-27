"""
main.py

Phase 3: We integrate ReflectionEngine, PatchCore triggers, and EGO_CORE emotional overlay.
"""

from pipelines.data_pipeline import data_pipeline_init, fetch_sol_price
from pipelines.execution_engine import execution_engine_init, execute_trade
from agents.synergy_conductor import synergy_conductor_init, synergy_conductor_run

# New imports
from core.reflection_engine.reflection_engine import reflection_engine_init, log_trade_outcome, analyze_history_and_trigger_patch
from core.patch_core.patch_core import patch_core_init, request_autopatch
from core.ego_core.ego_core import ego_core_init

def main():
    # Initialize components
    data_pipeline_init()
    execution_engine_init()
    synergy_conductor_init()
    reflection_engine_init()
    patch_core_init()
    ego_core_init()

    # For demonstration, let's define an arbitrary emotional_state
    # You can toggle this between 'rage', 'fear', or 'neutral' to see the effect
    emotional_state = "neutral"

    # Fetch market data
    market_data = fetch_sol_price()
    print(f"[Main] Market data fetched: {market_data}")

    # Run synergy logic WITH emotional overlay
    decision = synergy_conductor_run(market_data, emotional_state)
    print(f"[Main] Synergy Conductor Decision: {decision}")

    # Execute trade (placeholder logic)
    execute_trade(decision)

    # Let's pretend we have a dummy profit/loss for demonstration
    # If synergy says BUY, let's randomly assign a small "profit" or "loss" for logging
    # For now, just set it to  -10 if we didn't BUY, +5 if we did
    if "BUY" in decision:
        profit_loss = 5.0
    else:
        profit_loss = -10.0

    # ReflectionEngine logs the outcome
    sol_price = market_data.get("sol_price", 0.0)
    log_trade_outcome(decision, sol_price, profit_loss)

    # Check if we need to trigger a patch
    should_patch = analyze_history_and_trigger_patch()
    if should_patch:
        request_autopatch()

if __name__ == "__main__":
    main()
