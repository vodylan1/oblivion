"""
main.py

Phase 5: 
- We start a background thread for GodAwareness scanning (but in debug mode, it only does one scan).
- We incorporate concurrency logic so we can do synergy logic in parallel.
- If a whale alert is detected, we might alter EGO_CORE or kill switch logic in real time.

NOTE: Make sure concurrency_manager.py is in "debug" mode 
(i.e., the while True loop is commented out).
"""

print("[Debug] Top-level code in main.py is running!")  # Immediate test

import time

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
from security.kill_switch import kill_switch_init, check_kill_switch_conditions

# Concurrency manager (debug version) - see concurrency_manager.py
from core.concurrency_manager.concurrency_manager import (
    concurrency_manager_init,
    start_god_awareness_thread,
    latest_whale_alert
)

# God Awareness
from core.god_awareness.god_awareness import god_awareness_init

def main():
    print("[Main] Entered main() function. Starting Phase 5 initialization...")

    # Initialize everything
    data_pipeline_init()
    execution_engine_init()
    synergy_conductor_init()
    reflection_engine_init()
    patch_core_init()
    ego_core_init()
    kill_switch_init()
    god_awareness_init()
    concurrency_manager_init()

    # Start the background GodAwareness thread (which in debug mode runs once)
    start_god_awareness_thread()

    # Example emotional state
    emotional_state = "neutral"

    print("[Main] Starting a small loop of trades with concurrency debug mode active.")

    # We'll do a small loop of 3 trades here, just to demonstrate concurrency
    for i in range(3):
        print(f"\n[Main] Trade cycle #{i+1}")

        market_data = fetch_sol_price()
        print(f"[Main] Market data fetched: {market_data}")

        # Check if there's a whale alert from concurrency_manager
        if latest_whale_alert["whale_alert"]:
            print("[Main] Whale alert is active! Possibly adjust synergy or EGO...")
            # If we want to trigger fear, we do:
            emotional_state = "fear"

        # Run synergy with the (possibly updated) emotional state
        decision = synergy_conductor_run(market_data, emotional_state)
        print(f"[Main] Synergy Conductor Decision: {decision}")

        # Execute trade (placeholder)
        execute_trade(decision)

        # Mock PnL
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

        # Kill switch check
        if check_kill_switch_conditions(trade_history):
            print("[Main] KILL_SWITCH TRIGGERED! Freezing further operations.")
            break

        # Sleep a bit before next trade cycle
        time.sleep(3)

    print("[Main] Phase 5 loop complete. Concurrency + GodAwareness (debug) active.")


# --------------------------
# Make sure we call main()
# --------------------------
if __name__ == "__main__":
    main()
