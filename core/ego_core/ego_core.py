"""
ego_core.py

Phase 3: Minimal demonstration of EGO_CORE.
Incorporates an 'emotional' factor that might alter final synergy decisions.
"""

def ego_core_init():
    """Initialize EGO_CORE (placeholder)."""
    print("[EGO_CORE] Initialized.")

def apply_emotional_overlay(decision: str, emotional_state: str):
    """
    If EGO is in a certain emotional state, we might alter the final decision.
    For example, if 'rage', we double down on a BUY decision.
    If 'fear', we might downgrade a BUY to HOLD.
    """
    if emotional_state == "rage" and decision == "BUY":
        print("[EGO_CORE] RAGE state: Amplifying BUY decision (placeholder).")
        # A real scenario might increase buy size or reduce hold thresholds.
        return "BUY_MORE"  # A custom signal
    elif emotional_state == "fear" and decision == "BUY":
        print("[EGO_CORE] FEAR state: Changing BUY to HOLD.")
        return "HOLD"
    else:
        return decision
