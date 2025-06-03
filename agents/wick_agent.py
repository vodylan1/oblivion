"""
Wick – aggressive sniper, trades both directions quickly.
"""

from core.scoring_engine.scoring_engine import compute_score, IDEAL_PRICE


def wick_agent_logic(market_data: dict) -> str:
    score     = compute_score(market_data)
    sol_price = market_data.get("sol_price", 0)

    if score > 75:
        return "BUY"
    if score < 25 and sol_price > IDEAL_PRICE * 1.05:
        return "SELL"
    return "HOLD"
