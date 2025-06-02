"""
execution_engine.py

Phase 6 (latest solana>=0.36.x).
Two modes:
 - 'mock': placeholder prints
 - 'real_devnet': a minimal devnet transaction (we'll do an airdrop example).
"""

from security.secure_wallet import load_keypair, get_solana_client

MODE = "real_devnet"  # or "mock"

def execution_engine_init():
    print("[ExecutionEngine] Initialized.")

def execute_trade(decision: str):
    """
    If MODE == 'mock', do placeholder prints.
    If MODE == 'real_devnet', sign & send a devnet transaction (airdrop).
    """
    if MODE == "mock":
        if decision == "BUY":
            print("[ExecutionEngine] (MOCK) Executing BUY order.")
        elif decision == "SELL":
            print("[ExecutionEngine] (MOCK) Executing SELL order.")
        else:
            print("[ExecutionEngine] (MOCK) Decision is HOLD. No action taken.")
    elif MODE == "real_devnet":
        if decision in ["BUY", "SELL"]:
            perform_devnet_transaction(decision)
        else:
            print("[ExecutionEngine] (REAL) Decision is HOLD. No action taken.")

def perform_devnet_transaction(decision: str):
    """
    Example devnet transaction - simply request an airdrop to show on-chain calls.
    Not an actual DEX trade, just a scaffold for demonstration.
    """
    print(f"[ExecutionEngine] (REAL) Attempting a devnet {decision} transaction...")

    try:
        kp = load_keypair()  # solders.keypair.Keypair
        client = get_solana_client(network="devnet")

        print("[ExecutionEngine] Requesting 1 SOL airdrop (devnet)...")
        airdrop_sig = client.request_airdrop(kp.pubkey(), int(1e9))  # 1 SOL in lamports
        print(f"[ExecutionEngine] Airdrop signature: {airdrop_sig}")

        # Wait/confirm the transaction
        import time
        time.sleep(2)

        balance_resp = client.get_balance(kp.pubkey())
        lamports = balance_resp["result"]["value"]
        print(f"[ExecutionEngine] Post-airdrop balance: {lamports} lamports")

    except Exception as e:
        print(f"[ExecutionEngine] Error in perform_devnet_transaction: {e}")
