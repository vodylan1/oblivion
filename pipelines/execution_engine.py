"""
execution_engine.py  – Phase 7  
Supports two modes:
  • mock         : just prints
  • real_devnet  : submits a dev-net airdrop tx (proof-of-life)
"""

from typing import Literal, Optional
from security.secure_wallet import load_keypair, get_solana_client

MODE: Literal["mock", "real_devnet"] = "mock"   # default


# ────────────────────────────────────────────────────────────────────────────
def execution_engine_init(mode: Optional[str] = None) -> None:
    global MODE
    MODE = mode or MODE
    print(f"[ExecutionEngine] Initialised – mode = {MODE}")


def execute_trade(decision: str) -> None:
    """Route BUY/SELL/HOLD depending on MODE."""
    if MODE == "mock":
        print(f"[ExecutionEngine] (MOCK) {decision}")
        return

    # ------- real dev-net scaffold -------
    if MODE == "real_devnet" and decision in {"BUY", "SELL"}:
        perform_devnet_transaction(decision)
    else:
        print("[ExecutionEngine] (REAL) HOLD")


def perform_devnet_transaction(decision: str) -> None:
    """
    **Not** an on-chain trade – just requests an airdrop so you
    can see a signed transaction hit dev-net.
    """
    try:
        kp      = load_keypair()
        client  = get_solana_client("devnet")

        print(f"[ExecutionEngine] Dev-net {decision} – requesting 0.2 SOL airdrop")
        sig = client.request_airdrop(kp.pubkey(), int(0.2 * 1e9))  # lamports
        print("   tx sig:", sig)

        # Simple confirm-sleep
        import time
        time.sleep(2)
        bal = client.get_balance(kp.pubkey())["result"]["value"] / 1e9
        print(f"   new balance ≈ {bal:.4f} SOL")

    except Exception as exc:
        print("[ExecutionEngine] ERROR", exc)
