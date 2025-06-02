"""
secure_wallet.py

For solana>=0.36.x, we use solders.keypair/keypub directly.
"""

import os
import json
from solders.keypair import Keypair
from solana.rpc.api import Client

def secure_wallet_init():
    """Initialize secure wallet (placeholder)."""
    print("[SecureWallet] Initialized.")

def load_keypair(keyfile_path="~/.config/solana/id.json") -> Keypair:
    """
    Load a solders-based Keypair from a JSON file (typical Solana CLI).
    If file not found or error occurs, return a random ephemeral Keypair.
    """
    expanded_path = os.path.expanduser(keyfile_path)
    if not os.path.exists(expanded_path):
        print(f"[SecureWallet] Key file not found at {expanded_path}. Using random devnet key.")
        return Keypair()  # ephemeral

    try:
        with open(expanded_path, "r", encoding="utf-8") as f:
            byte_list = json.loads(f.read())  # typical 64-byte array
            secret_bytes = bytes(byte_list)
            kp = Keypair.from_bytes(secret_bytes)
            return kp
    except Exception as e:
        print(f"[SecureWallet] Error loading keypair: {e}")
        return Keypair()

def get_solana_client(network="devnet") -> Client:
    """
    Return a solana.rpc.api Client pointing to devnet or mainnet-beta.
    """
    if network == "devnet":
        url = "https://api.devnet.solana.com"
    else:
        url = "https://api.mainnet-beta.solana.com"
    return Client(url)
