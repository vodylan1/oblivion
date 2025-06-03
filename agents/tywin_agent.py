"""
Tywin – ultra-conservative guardian.
Buys only when price is deep discount; sells when overheated.
"""

from core.scoring_engine.scoring_engine import compute_score, IDEAL_PRICE


def tywin_agent_logic(market_data: dict) -> str:
    score     = compute_score(market_data)
    sol_price = market_data.get("sol_price", 0)

    if sol_price < IDEAL_PRICE * 0.85:
        return "BUY"
    if sol_price > IDEAL_PRICE * 1.20 and score < 40:
        return "SELL"
    return "HOLD"
