"""
wick_agent.py

Agent Archetype: Wick.
Aggressive sniper approach.
Phase 2: Minimal signal logic, just for demonstration.
"""

def wick_agent_logic(market_data: dict):
    """
    If sol_price < 25, let's say Wick is still in for a BUY.
    Otherwise, Wick might SELL (or for now, just 'HOLD').
    """
    sol_price = market_data.get("sol_price", 0)
    if sol_price < 25:
        return "BUY"
    else:
        return "HOLD"
