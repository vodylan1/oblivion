"""
main.py

Phase 6  ➜  Phase 7-0 / 7-1
------------------------------------
* Regular spot-trading demo loop (Phase 6)
* Phase 7 scaffolds promoted to “real” stubs
  – DerivativesEngine now returns an object
  – PositionManager placeholder still prints
"""

print("[Debug] Top-level code in main.py is running!")

import time

# ─── Data & Execution modules ──────────────────────────────────────────────
from pipelines.data_pipeline import data_pipeline_init, fetch_sol_price
from pipelines.execution_engine import (
    execution_engine_init,
    execute_trade,
)

# ─── Phase-6 core modules ─────────────────────────────────────────────────
from agents.synergy_conductor import (
    synergy_conductor_init,
    synergy_conductor_run,
)
from core.reflection_engine.reflection_engine import (
    reflection_engine_init,
    log_trade_outcome,
    analyze_history_and_trigger_patch,
    trade_history,
)
from core.patch_core.patch_core import patch_core_init, request_autopatch
from core.ego_core.ego_core import ego_core_init
from security.kill_switch import kill_switch_init, check_kill_switch_conditions

from core.concurrency_manager.concurrency_manager import (
    concurrency_manager_init,
    start_god_awareness_thread,
    latest_whale_alert,
)
from core.god_awareness.god_awareness import god_awareness_init

# ─── Phase-7 modules (now “real” stubs) ────────────────────────────────────
from core.derivatives_engine.derivatives_engine import derivatives_engine_init
from pipelines.position_manager import position_manager_init


# ───────────────────────────────────────────────────────────────────────────
def main() -> None:
    print("[Main] Entered main() function. Starting Phase 6 / 7 initialization…")

    # Phase-6 initialisers
    data_pipeline_init()
    execution_engine_init()
    synergy_conductor_init()
    reflection_engine_init()
    patch_core_init()
    ego_core_init()
    kill_switch_init()
    god_awareness_init()
    concurrency_manager_init()

    # Phase-7 initialisers (scaffolds → working stubs)
    derivatives_engine = derivatives_engine_init()   # keep the object
    position_manager_init()

    # Background God-Awareness thread
    start_god_awareness_thread()

    print("[Main] Starting demo trading loop…")
    emotional_state = "neutral"

    for cycle in range(3):
        print(f"\n[Main] Trade cycle #{cycle + 1}")

        # 1 ─ Fetch market data
        market_data = fetch_sol_price()
        print(f"[Main] Market data fetched: {market_data}")

        # 2 ─ If whale alert → FEAR overlay
        if latest_whale_alert["whale_alert"]:
            emotional_state = "fear"

        # 3 ─ Decide via Synergy Conductor
        decision = synergy_conductor_run(market_data, emotional_state)
        print(f"[Main] Synergy Conductor Decision: {decision}")

        # 4 ─ Execute
        execute_trade(decision)

        # 5 ─ Mock PnL & logging
        profit_loss = 5.0 if "BUY" in decision else -10.0
        log_trade_outcome(decision, market_data["sol_price"], profit_loss)

        # 6 ─ Reflection & autopatch
        if analyze_history_and_trigger_patch():
            request_autopatch()

        # 7 ─ Kill-switch check
        if check_kill_switch_conditions(trade_history):
            print("[Main] KILL_SWITCH TRIGGERED! Exiting loop.")
            break

        time.sleep(3)

    print("[Main] Phase 7 loop complete.")


# ───────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
