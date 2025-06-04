"""
main.py
────────────────────────────────────────────────────────────────────────────
Phase-7-5  →  Phase-8 scaffold + CLI tweak for main-net runs
"""

from __future__ import annotations

import time

print("[Debug] Top-level code in main.py is running!")

# ─── Imports (unchanged) ───────────────────────────────────────────────────
from pipelines.data_pipeline import data_pipeline_init, fetch_sol_price
from pipelines.execution_engine import execution_engine_init, execute_trade

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

from core.derivatives_engine.derivatives_engine import derivatives_engine_init
from pipelines.position_manager import position_manager_init, PM

from core.mutation_engine import mutation_engine_init, propose_patch
from intel.meme_scanner import meme_scanner_init, scan_feeds

# ───────────────────────────────────────────────────────────────────────────
def main(env: str = "mock", continuous: bool = False) -> None:
    """
    Entry-point.

    • env = mock | devnet | mainnet
    • --continuous  ⇒ loop forever
    """
    print("[Main] Starting Phase-7-5 / 8 initialisation…")

    # Initialisers … (unchanged – trimmed for brevity)
    data_pipeline_init()
    execution_engine_init(env)         # pass CLI flag through
    synergy_conductor_init()
    reflection_engine_init()
    patch_core_init()
    ego_core_init()
    kill_switch_init()
    god_awareness_init()
    concurrency_manager_init()

    derivatives_engine_init()
    position_manager_init()

    mutation_engine_init()
    meme_scanner_init()

    start_god_awareness_thread()

    emotional_state = "neutral"
    loop_count      = 0
    max_cycles      = float("inf") if continuous else 3

    print("[Main] Entering trading loop…")
    while loop_count < max_cycles:
        loop_count += 1
        print(f"\n[Main] Trade cycle #{loop_count}")

        market_data = fetch_sol_price()
        market_data.update(scan_feeds())

        if latest_whale_alert["whale_alert"]:
            emotional_state = "fear"

        decision = synergy_conductor_run(market_data, emotional_state)
        price    = market_data.get("sol_price", 0.0)

        print(f"[Main] Market data: {market_data}")
        print(f"[Main] Decision: {decision}")

        execute_trade(decision, price)
        log_trade_outcome(decision, price, 0.0)

        if analyze_history_and_trigger_patch():
            request_autopatch()

        check_kill_switch_conditions(trade_history)

        time.sleep(3)

    print("[Main] Loop complete.")


# ───────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["mock", "devnet", "mainnet"], default="mock")
    parser.add_argument(
        "--continuous", action="store_true", help="run indefinitely instead of 3 demo cycles"
    )
    args = parser.parse_args()

    main(env=args.env, continuous=args.continuous)
