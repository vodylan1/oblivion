"""
kill_switch.py

Phase 4: Minimal KILL_SWITCH logic.
We'll define a function that checks certain conditions (fake or real)
and can return True if the system needs to freeze.
"""

def kill_switch_init():
    """Initialize kill switch (placeholder)."""
    print("[KillSwitch] Initialized.")

def check_kill_switch_conditions(trade_history):
    """
    Check for conditions that require a kill switch.
    Example: if sum of last N trades' profit_loss < -50, or any other meltdown logic.
    Return True if we need to halt, False otherwise.
    """
    if len(trade_history) == 0:
        return False

    # Example: If total PnL in last 5 trades < -50, we kill it
    recent_trades = trade_history[-5:] if len(trade_history) >= 5 else trade_history
    total_pnl = sum(t["profit_loss"] for t in recent_trades)

    if total_pnl < -50:
        print("[KillSwitch] Condition met! Total PnL in last 5 trades below -50.")
        return True

    return False
