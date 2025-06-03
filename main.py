"""
main.py

Phase 6 ➜ Phase 7-0
- Runs spot-trading loop (Phase 6).
- Adds placeholders for derivatives_engine & position_manager (Phase 7 scaffolds).
"""

print("[Debug] Top-level code in main.py is running!")

import time

# ─── Data & execution modules ──────────────────────────────────────────────
from pipelines.data_pipeline import data_pipeline_init, fetch_sol_price
from pipelines.execution_engine import (
    execution_engine_init,
    execute_trade
)

# ─── Phase-6 core modules ──────────────────────────────────────────────────
from agents.synergy_conductor import (
    synergy_conductor_init,
    synergy_conductor_run
)
from core.reflection_engine.reflection_engine import (
    reflection_engine_init,
    log_trade_outcome,
    analyze_history_and_trigger_patch,
    trade_history
)
from core.patch_core.patch_core import patch_core_init, request_autopatch
from core.ego_core.ego_core import ego_core_init
from security.kill_switch import kill_switch_init, check_kill_switch_conditions

from core.concurrency_manager.concurrency_manager import (
    concurrency_manager_init,
    start_god_awareness_thread,
    latest_whale_alert
)
from core.god_awareness.god_awareness import god_awareness_init

# ─── Phase-7 scaffolds (NEW) ───────────────────────────────────────────────
from core.derivatives_engine.derivatives_engine import derivatives_engine_init
from pipelines.position_manager import position_manager_init


# ───────────────────────────────────────────────────────────────────────────
def main():
    print("[Main] Entered main() function. Starting Phase 6 / 7-0 initialization…")

    # Phase-6 initializers
    data_pipeline_init()
    execution_engine_init()
    synergy_conductor_init()
    reflection_engine_init()
    patch_core_init()
    ego_core_init()
    kill_switch_init()
    god_awareness_init()
    concurrency_manager_init()

    # Phase-7-0 initializers (scaffolds)
    derivatives_engine_init()
    position_manager_init()

    # Start background God-Awareness thread
    start_god_awareness_thread()

    emotional_state = "neutral"
    print("[Main] Starting demo trading loop…")

    for i in range(3):
        print(f"\n[Main] Trade cycle #{i + 1}")

        market_data = fetch_sol_price()
        print(f"[Main] Market data fetched: {market_data}")

        # Example whale alert check
        if latest_whale_alert["whale_alert"]:
            emotional_state = "fear"

        decision = synergy_conductor_run(market_data, emotional_state)
        print(f"[Main] Synergy Conductor Decision: {decision}")

        execute_trade(decision)

        # Mock PnL calculation
        profit_loss = 5.0 if "BUY" in decision else -10.0
        sol_price = market_data.get("sol_price", 0.0)
        log_trade_outcome(decision, sol_price, profit_loss)

        if analyze_history_and_trigger_patch():
            request_autopatch()

        if check_kill_switch_conditions(trade_history):
            print("[Main] KILL_SWITCH TRIGGERED! Exiting loop.")
            break

        time.sleep(3)

    print("[Main] Phase 7-0 loop complete.")


# ───────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
