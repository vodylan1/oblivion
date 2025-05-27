"""
main.py

Phase 4: Integrate SCORING_ENGINE in synergy, add KILL_SWITCH checks after reflection.
"""

from pipelines.data_pipeline import data_pipeline_init, fetch_sol_price
from pipelines.execution_engine import execution_engine_init, execute_trade
from agents.synergy_conductor import synergy_conductor_init, synergy_conductor_run

from core.reflection_engine.reflection_engine import (
    reflection_engine_init,
    log_trade_outcome,
    analyze_history_and_trigger_patch,
    trade_history
)
from core.patch_core.patch_core import patch_core_init, request_autopatch
from core.ego_core.ego_core import ego_core_init

# NEW import
from security.kill_switch import kill_switch_init, check_kill_switch_conditions

def main():
    # Initialize
    data_pipeline_init()
    execution_engine_init()
    synergy_conductor_init()
    reflection_engine_init()
    patch_core_init()
    ego_core_init()
    kill_switch_init()

    # Example emotional state
    emotional_state = "neutral"

    # Fetch market data
    market_data = fetch_sol_price()
    print(f"[Main] Market data fetched: {market_data}")

    # Run synergy
    decision = synergy_conductor_run(market_data, emotional_state)
    print(f"[Main] Synergy Conductor Decision: {decision}")

    # Execute trade (placeholder)
    execute_trade(decision)

    # Mock PnL: If we decide "BUY", assume profit=5, else -10
    # (just a placeholder)
    if "BUY" in decision:
        profit_loss = 5.0
    else:
        profit_loss = -10.0

    # Log outcome
    sol_price = market_data.get("sol_price", 0.0)
    log_trade_outcome(decision, sol_price, profit_loss)

    # Reflection check
    should_patch = analyze_history_and_trigger_patch()
    if should_patch:
        request_autopatch()

    # Now we do a kill switch check
    if check_kill_switch_conditions(trade_history):
        print("[Main] KILL_SWITCH TRIGGERED! Freezing further operations.")
        return  # or raise an exception, or set a global freeze flag

    print("[Main] Phase 4 execution finished without kill-switch trigger.")

if __name__ == "__main__":
    main()
