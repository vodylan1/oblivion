"""
execution_engine.py
────────────────────────────────────────────────────────────────────────────
• MODE is now chosen at runtime from CLI:
      main.py  --env mock|devnet|mainnet

• mock            – print-only
• real_devnet     – 1 SOL airdrop on dev-net
• real_mainnet    – NO on-chain write yet (placeholder)
"""

from __future__ import annotations

import time
from typing import Literal, Optional

from solders.rpc.responses import GetBalanceResp  # type: ignore
from solana.rpc.api import Client
from solana.rpc.types import TxOpts

from core.notifier.notifier import notify
from security.secure_wallet import load_keypair, get_solana_client

# will be overwritten by initialise()
MODE: Literal["mock", "real_devnet", "real_mainnet"] = "mock"


# ───────────────────────────────────────────────────────────────────────────
def execution_engine_init(env: str = "mock") -> None:
    global MODE
    MODE = (
        "mock"
        if env == "mock"
        else "real_devnet"
        if env == "devnet"
        else "real_mainnet"
    )
    print(f"[ExecutionEngine] Initialised – mode = {MODE}")


def _discord_echo(decision: str, lamports: Optional[int] = None) -> None:
    txt = f"🤖 **{decision}**"
    if lamports is not None:
        txt += f" – balance: {lamports/1e9:,.4f} SOL"
    notify(txt)


# --------------------------------------------------------------------------- #
def execute_trade(decision: str, price: float | None = None) -> None:
    """
    * BUY / SELL on dev-net → 1 SOL airdrop (keep-alive)
    * BUY / SELL on main-net → placeholder until Drift route is wired
    * HOLD                → no-op
    """
    if decision == "HOLD":
        print("[ExecutionEngine] Decision HOLD → noop.")
        return

    if MODE == "mock":
        print(f"[ExecutionEngine] (MOCK) {decision} at ${price}")
        _discord_echo(f"{decision} (mock) @ ${price}")
        return

    if MODE == "real_devnet":
        _airdrop_one_sol(decision)
        return

    if MODE == "real_mainnet":
        print("[ExecutionEngine] (MAIN-NET) placeholder – no tx sent.")
        notify(f"⚠️ MAIN-NET mode: {decision} (no live route yet)")
        return


# --------------------------------------------------------------------------- #
def _airdrop_one_sol(decision: str) -> None:
    """Request 1 SOL on dev-net and report final balance."""
    try:
        kp = load_keypair()
        client: Client = get_solana_client("devnet")

        print(f"[ExecutionEngine] Requesting 1 SOL airdrop … ({decision})")
        sig = client.request_airdrop(kp.pubkey(), int(1e9))["result"]
        client.confirm_transaction(sig, commitment="confirmed")

        bal_resp: GetBalanceResp = client.get_balance(kp.pubkey())  # type: ignore
        lamports = bal_resp.value  # solders 0.26 attr

        print(f"[ExecutionEngine] Post-drop balance {lamports} lamports")
        _discord_echo(decision, lamports=lamports)

    except Exception as exc:      # noqa: BLE001
        print(f"[ExecutionEngine] ERROR during dev-net tx: {exc}")
        notify(f"⚠️ ExecutionEngine error: `{exc!r}`")
