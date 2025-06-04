"""
pipelines/execution_engine.py · Phase 7-5 (patched v2)

• MODE = "mock"         → print only
• MODE = "real_devnet"  → dev-net airdrop (1 SOL) as on-chain ping

All actions are mirrored to Discord via core.notifier.
"""
from __future__ import annotations

import time
from typing import Literal

from solders.rpc.responses import GetBalanceResp  # type: ignore

from core.notifier.notifier import notify
from security.secure_wallet import load_keypair, get_solana_client

MODE: Literal["mock", "real_devnet"] = "real_devnet"


# ────────────────────────────────────────────────────────────────────────────
def execution_engine_init() -> None:
    print(f"[ExecutionEngine] Initialised – mode = {MODE}")


def _discord_echo(decision: str, lamports: int | None = None) -> None:
    txt = f"🤖 **{decision}**"
    if lamports is not None:
        txt += f" – balance: {lamports / 1e9:,.4f} SOL"
    notify(txt)


def execute_trade(decision: str, price: float | None = None) -> None:
    """
    Single entry-point for main.py and tests.

    • HOLD → noop
    • Others → mock or real dev-net
    """
    # ─── HOLD ──────────────────────────────────────────────────────────────
    if decision == "HOLD":
        print("[ExecutionEngine] (REAL) Decision HOLD → noop.")
        return

    # ─── MOCK ──────────────────────────────────────────────────────────────
    if MODE == "mock":
        print(f"[ExecutionEngine] (MOCK) {decision} at ${price}")
        _discord_echo(f"{decision} (mock) @ ${price}")
        return

    # ─── REAL DEV-NET ──────────────────────────────────────────────────────
    try:
        kp     = load_keypair()
        client = get_solana_client("devnet")

        print(f"[ExecutionEngine] Requesting 1 SOL airdrop … ({decision})")
        _discord_echo(f"{decision} – requesting dev-net airdrop")

        sig_resp = client.request_airdrop(kp.pubkey(), int(1e9))
        sig      = sig_resp.value      # str

        # wait for confirmation once, then read balance
        client.confirm_transaction(sig, commitment="confirmed")
        time.sleep(1.5)                # dev-net propagation buffer

        bal_resp: GetBalanceResp = client.get_balance(kp.pubkey())  # type: ignore
        lamports = bal_resp.value       # ← solders 0.26+ field
        print(f"[ExecutionEngine] Post-drop balance {lamports} lamports")

        _discord_echo(decision, lamports=lamports)

    except Exception as exc:  # noqa: BLE001
        print(f"[ExecutionEngine] ERROR during dev-net tx: {exc!r}")
        notify(f"⚠️ ExecutionEngine error: `{exc!r}`")
