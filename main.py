"""
main.py

Phase-7-5 → Phase-8 scaffold
────────────────────────────
• Spot-trading demo loop (mock or dev-net)
• DerivativesEngine stub
• Phase-8 stubs wired:
    – mutation_engine (GPT patches, later)
    – meme_scanner     (real-time alpha feeds, later)
"""

from __future__ import annotations

import time

print("[Debug] Top-level code in main.py is running!")

# ─── Data & execution modules ──────────────────────────────────────────────
from pipelines.data_pipeline import data_pipeline_init, fetch_sol_price
from pipelines.execution_engine import (
    execution_engine_init,
    execute_trade,
)

# ─── Phase-6 core modules ──────────────────────────────────────────────────
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

# ─── Phase-7 scaffolds ─────────────────────────────────────────────────────
from core.derivatives_engine.derivatives_engine import derivatives_engine_init
from pipelines.position_manager import position_manager_init, PM

# ─── Phase-8 stubs ─────────────────────────────────────────────────────────
from core.mutation_engine import mutation_engine_init, propose_patch
from intel.meme_scanner import meme_scanner_init, scan_feeds

# ───────────────────────────────────────────────────────────────────────────
def main(env: str = "mock", continuous: bool = False) -> None:
    """
    Entry-point.  `env` can be “mock” (default) or “devnet”.

    • continuous=False → run 3 demo cycles then exit
    • continuous=True  → loop forever
    """
    print("[Main] Starting Phase-7-5 / 8 initialisation…")

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

    # Phase-7 scaffolds
    derivatives_engine_init()
    position_manager_init()

    # Phase-8 stubs
    mutation_engine_init()
    meme_scanner_init()

    # Background God-Awareness thread
    start_god_awareness_thread()

    emotional_state = "neutral"
    loop_count      = 0
    max_cycles      = float("inf") if continuous else 3

    print("[Main] Entering trading loop…")
    while loop_count < max_cycles:
        loop_count += 1
        print(f"\n[Main] Trade cycle #{loop_count}")

        # ── market data ─────────────────────────────
        market_data = fetch_sol_price()
        market_data.update(scan_feeds())          # Phase-8 feed
        print(f"[Main] Market data: {market_data}")

        # adjust emotion if whale alert
        if latest_whale_alert["whale_alert"]:
            emotional_state = "fear"

        decision = synergy_conductor_run(market_data, emotional_state)
        print(f"[Main] Decision: {decision}")

        price = market_data.get("sol_price", 0.0)
        execute_trade(decision, price)

        # simple PnL mock
        pnl = 5.0 if "BUY" in decision else -10.0
        log_trade_outcome(decision, price, pnl)

        if analyze_history_and_trigger_patch():
            request_autopatch()

        if check_kill_switch_conditions(trade_history):
            print("[Main] Kill-switch tripped – shutting down.")
            break

        time.sleep(3)

    print("[Main] Loop complete.")


# ───────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["mock", "devnet"], default="mock")
    parser.add_argument(
        "--continuous",
        action="store_true",
        help="run indefinitely instead of 3 demo cycles",
    )
    args = parser.parse_args()

    main(env=args.env, continuous=args.continuous)
