"""
ozymandias_agent.py

Agent Archetype: Ozymandias.
Long-term empire building.
Phase 2: Minimal signal logic.
"""

def ozymandias_agent_logic(market_data: dict):
    """
    Let's pretend Ozymandias always invests 10% of capital,
    but for simplicity, we just return 'BUY' if sol_price < 30.
    """
    sol_price = market_data.get("sol_price", 0)
    if sol_price < 30:
        return "BUY"
    else:
        return "HOLD"
