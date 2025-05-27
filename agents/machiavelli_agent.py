"""
machiavelli_agent.py

Agent Archetype: Machiavelli.
Focus on stealth, infiltration, alpha gathering for early entries.
Phase 2: We'll just produce a mock signal based on sol_price for demonstration.
"""

def machiavelli_agent_logic(market_data: dict):
    """
    Returns a basic 'buy' or 'hold' signal.
    E.g., if sol_price < 20, then 'buy', else 'hold'.
    """
    sol_price = market_data.get("sol_price", 0)
    if sol_price < 20:
        return "BUY"
    else:
        return "HOLD"
