"""
secure_wallet.py
────────────────────────────────────────────────────────────────────────────
Single source of truth for:

* loading a Keypair (solders)
* returning an Anchor-compatible `Wallet`
* creating a solana-py `Client`
* utility `wallet_and_client()` used by execution / derivatives engines
"""

from __future__ import annotations

import json
import os
from typing import Tuple

from solders.keypair import Keypair
from solana.rpc.api import Client
from anchorpy import Wallet


# ------------------------------------------------------------------ #
def _default_keyfile() -> str:
    return os.path.expanduser("~/.config/solana/id.json")


def load_keypair(path: str | None = None) -> Keypair:
    """
    Load a standard 64-byte Solana keypair file.
    Falls back to an **ephemeral** random keypair if the file is missing.
    """
    path = path or _default_keyfile()
    if not os.path.exists(path):
        print(f"[SecureWallet] Keyfile {path} not found – using random key.")
        return Keypair()
    try:
        with open(path, "r", encoding="utf-8") as f:
            secret = bytes(json.load(f))
        return Keypair.from_bytes(secret)
    except Exception as exc:
        print(f"[SecureWallet] Could not load keyfile – {exc}; using random.")
        return Keypair()


def get_solana_client(network: str = "devnet") -> Client:
    url = (
        "https://api.devnet.solana.com"
        if network == "devnet"
        else "https://api.mainnet-beta.solana.com"
    )
    return Client(url)


# ------------------------------------------------------------------ #
def wallet_and_client(network: str = "devnet") -> Tuple[Wallet, Client]:
    """
    Convenience helper imported by other modules:
        >>> wallet, client = wallet_and_client("devnet")
    """
    kp = load_keypair()
    return Wallet(kp), get_solana_client(network)
