"""
tywin_agent.py

Agent Archetype: Tywin.
Focus on defensive, conservative strategy.
Phase 2: Minimal signal logic.
"""

def tywin_agent_logic(market_data: dict):
    """
    If sol_price is too high, Tywin might stay out (HOLD).
    If sol_price is relatively low, Tywin might do a small 'BUY'.
    """
    sol_price = market_data.get("sol_price", 0)
    if sol_price < 15:
        return "BUY"
    else:
        return "HOLD"
