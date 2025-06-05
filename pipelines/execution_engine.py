"""
execution_engine.py
────────────────────────────────────────────────────────────────────────────
Phase-9-C

• MODE selected at runtime (mock | devnet | mainnet)
• Position sizing: risk_pct of wallet balance (config/parameters.json)
• BUY routes through Jupiter simulator in mock/devnet
• All entries recorded in PositionManager so PnL can be audited
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

import requests
from solders.rpc.responses import GetBalanceResp  # type: ignore
from solana.rpc.api import Client

from core.notifier.notifier import notify
from pipelines.swap_router import simulate_buy
from pipelines.position_manager import PM
from security.secure_wallet import load_keypair, get_solana_client

# ───────────────────────────────────────────────────────────────────────────
_MODE: Literal["mock", "real_devnet", "real_mainnet"] = "mock"

# runtime tunables ----------------------------------------------------------
_CFG = Path(__file__).resolve().parents[1] / "config" / "parameters.json"
try:
    _PARAMS: dict = json.loads(_CFG.read_text())
except Exception:
    _PARAMS = {}

_RISK_PCT: float = float(_PARAMS.get("risk_pct", 0.02))      # 2 % of wallet
_SLIPPAGE_BPS: int = int(_PARAMS.get("slippage_bps", 25))    # 0.25 %

_SOL_MINT = "So11111111111111111111111111111111111111112"


# ───────────────────────────────────────────────────────────────────────────
def execution_engine_init(env: str = "mock") -> None:
    """Initialise engine mode (mock / devnet / mainnet)."""
    global _MODE
    _MODE = (
        "mock"
        if env == "mock"
        else "real_devnet"
        if env == "devnet"
        else "real_mainnet"
    )
    print(f"[ExecutionEngine] Initialised – mode = {_MODE}")


def _echo(msg: str) -> None:
    notify(f"🤖 {msg}")


# --------------------------------------------------------------------------- #
def _wallet_balance_lamports() -> int:
    """
    Return lamport balance for the active keypair.
    In mock mode we fake 10 SOL so position sizing maths still work.
    """
    if _MODE == "mock":
        return int(10 * 1e9)

    kp = load_keypair()
    net = "devnet" if _MODE == "real_devnet" else "mainnet"
    client: Client = get_solana_client(net)
    bal_resp: GetBalanceResp = client.get_balance(kp.pubkey())  # type: ignore
    return bal_resp.value


def _calc_lamports(entry_price: float | None) -> int:
    """Risk-based position size ⇒ lamports."""
    price = entry_price or 1.0
    wal_lamports = _wallet_balance_lamports()
    usd_wallet   = wal_lamports / 1e9 * price
    usd_pos      = usd_wallet * _RISK_PCT
    sol_size     = usd_pos / price
    return max(int(sol_size * 1e9), int(0.0001 * 1e9))  # ≥ 0.0001 SOL


# --------------------------------------------------------------------------- #
def execute_trade(decision: str, price: float | None = None) -> None:
    """
    Main entry-point called from main.py.
    """

    if decision == "HOLD":
        print("[ExecutionEngine] Decision HOLD → noop.")
        return

    if decision.startswith("BUY"):
        _handle_buy(decision, price)
        return

    print(f"[ExecutionEngine] ⚠️ Un-handled decision: {decision!r}")


# --------------------------------------------------------------------------- #
def _handle_buy(decision: str, price: float | None) -> None:
    lamports = _calc_lamports(price)

    # ── MOCK ───────────────────────────────────────────────────────────────
    if _MODE == "mock":
        print(f"[ExecutionEngine] (MOCK) {decision} {lamports/1e9:.4f} SOL at ${price}")
        PM.open_long(lamports / 1e9, price or 0.0, "mock")
        return

    # ── DEVNET (sim swap) ─────────────────────────────────────────────────
    if _MODE == "real_devnet":
        simulate_buy(_SOL_MINT, lamports / 1e9, _SLIPPAGE_BPS)
        PM.open_long(lamports / 1e9, price or 0.0, "sim-devnet")
        _echo(f"BUY {lamports/1e9:.4f} SOL on devnet (simulated)")
        return

    # ── MAINNET (still simulation until Drift wired) ──────────────────────
    if _MODE == "real_mainnet":
        simulate_buy(_SOL_MINT, lamports / 1e9, _SLIPPAGE_BPS)
        PM.open_long(lamports / 1e9, price or 0.0, "sim-mainnet")
        _echo(f"BUY {lamports/1e9:.4f} SOL on mainnet - simulated")
        return
