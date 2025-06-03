"""
main.py   · Phase 7-5
───────────────────────────────────────────────────────────────────────────────
*   infinite / N-cycle trading loop with clean shutdown
*   Discord notifications everywhere (errors, kill-switch, normal flow)
"""
from __future__ import annotations

import argparse
import signal
import sys
import time
from typing import Optional

from agents.synergy_conductor import (  # noqa: E402  pylint: disable=C0413
    synergy_conductor_init,
    synergy_conductor_run,
)
from core.concurrency_manager.concurrency_manager import (  # noqa: E402
    concurrency_manager_init,
    start_god_awareness_thread,
    latest_whale_alert,
)
from core.derivatives_engine.derivatives_engine import (
    derivatives_engine_init,  # noqa: E402
)
from core.ego_core.ego_core import ego_core_init  # noqa: E402
from core.notifier.notifier import notify  # noqa: E402
from core.patch_core.patch_core import patch_core_init, request_autopatch  # noqa: E402
from core.reflection_engine.reflection_engine import (  # noqa: E402
    analyze_history_and_trigger_patch,
    log_trade_outcome,
    reflection_engine_init,
    trade_history,
)
from pipelines.data_pipeline import data_pipeline_init, fetch_sol_price  # noqa: E402
from pipelines.execution_engine import (  # noqa: E402
    execution_engine_init,
    execute_trade,
)
from pipelines.position_manager import position_manager_init  # noqa: E402
from security.kill_switch import (  # noqa: E402
    KillSwitchTripped,
    check_kill_switch_conditions,
    kill_switch_init,
)
from core.god_awareness.god_awareness import god_awareness_init  # noqa: E402


# ────────────────────────────────────────────────────────────────────────────
def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(prog="oblivion")
    ap.add_argument("--cycles", type=int, help="run exactly N cycles then exit")
    ap.add_argument(
        "--continuous",
        action="store_true",
        help="run forever (until Ctrl-C or kill switch)",
    )
    return ap.parse_args()


_SHUTDOWN = False


def _signal_handler(signum, frame):  # noqa: D401, N802  pylint: disable=W0613
    global _SHUTDOWN
    _SHUTDOWN = True
    notify("🛑 SIGINT received – graceful shutdown requested.")


# ────────────────────────────────────────────────────────────────────────────
def initialise_everything() -> None:
    print("[Main] Entered main() function. Starting Phase 7 initialisation…")

    data_pipeline_init()
    execution_engine_init()
    synergy_conductor_init()
    reflection_engine_init()
    patch_core_init()
    ego_core_init()
    kill_switch_init()
    god_awareness_init()
    concurrency_manager_init()
    derivatives_engine_init()        # online or stub
    position_manager_init()

    start_god_awareness_thread()
    notify("✅ **Oblivion** bot online (Phase 7-5)")


# ────────────────────────────────────────────────────────────────────────────
def main() -> None:
    args = parse_args()
    total_cycles: Optional[int] = args.cycles
    continuous = args.continuous or total_cycles is None

    # Ctrl-C handler
    signal.signal(signal.SIGINT, _signal_handler)

    initialise_everything()

    emotional_state = "neutral"
    cycle = 0

    try:
        while continuous or (total_cycles and cycle < total_cycles):
            if _SHUTDOWN:
                break
            cycle += 1
            print(f"\n[Main] Trade cycle #{cycle}")

            market_data = fetch_sol_price()
            print(f"[Main] Market data fetched: {market_data}")

            if latest_whale_alert["whale_alert"]:
                emotional_state = "fear"

            decision = synergy_conductor_run(market_data, emotional_state)
            print(f"[Main] Synergy Conductor Decision: {decision}")

            execute_trade(decision, market_data["sol_price"])

            # mock PnL placeholder
            pnl = 5.0 if "BUY" in decision else -10.0
            log_trade_outcome(decision, market_data["sol_price"], pnl)

            if analyze_history_and_trigger_patch():
                request_autopatch()

            check_kill_switch_conditions(trade_history)

            time.sleep(3)

    except KillSwitchTripped as ks:
        print(f"[Main] {ks}")
        notify("💀 Bot halted by kill-switch.")
    except Exception as exc:  # noqa: BLE001
        print(f"[Main] Top-level exception: {exc!r}")
        notify(f"⚠️ Unhandled exception: `{exc!r}`")
    finally:
        notify("🟡 Oblivion loop exited (clean).")
        print("[Main] Loop exited.")

# ────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
