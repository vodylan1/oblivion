"""
execution_engine.py   · Phase 7-5
───────────────────────────────────────────────────────────────────────────────
Two run-modes:

    MODE = "mock"         → print only
    MODE = "real_devnet"  → request 1 SOL airdrop for every BUY/SELL
                             (acts as “on-chain ping” while we are still
                              scaffolding proper Drift DEX calls)

All BUY/SELL/CLOSE events are reported to Discord via core.notifier.
"""
from __future__ import annotations

import time
from typing import Literal

import requests
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
        txt += f" – balance: {lamports/1e9:,.4f} SOL"
    notify(txt)


def execute_trade(decision: str, price: float | None = None) -> None:
    """
    Unified entry-point used by main.py and by unit tests / REPL snippets.
    Only BUY, SELL, CLOSE_LONG, CLOSE_SHORT touch the chain; HOLD is noop.
    """
    if decision == "HOLD":
        print("[ExecutionEngine] (REAL) Decision HOLD → noop.")
        return

    if MODE == "mock":
        print(f"[ExecutionEngine] (MOCK) {decision} at ${price}")
        _discord_echo(f"{decision} (mock) @ ${price}")
        return

    # real_devnet
    try:
        kp = load_keypair()
        client = get_solana_client("devnet")

        print(f"[ExecutionEngine] Requesting 1 SOL airdrop … ({decision})")
        _discord_echo(f"{decision} – requesting devnet airdrop")

        sig = client.request_airdrop(kp.pubkey(), int(1e9))
        time.sleep(2)

        bal_resp: GetBalanceResp = client.get_balance(kp.pubkey())  # type: ignore
        lamports = bal_resp.result.value  # .value for solders-types
        print(f"[ExecutionEngine] Post-drop balance {lamports} lamports")

        _discord_echo(decision, lamports=lamports)

    except Exception as exc:
        print(f"[ExecutionEngine] ERROR during devnet tx: {exc}")
        notify(f"⚠️ ExecutionEngine error: `{exc!r}`")
