"""
Ozymandias – long-term empire builder.
Adds on dips, rarely sells.
"""

from core.scoring_engine.scoring_engine import compute_score, IDEAL_PRICE


def ozymandias_agent_logic(market_data: dict) -> str:
    score     = compute_score(market_data)
    sol_price = market_data.get("sol_price", 0)

    if sol_price < IDEAL_PRICE * 0.90 and score >= 55:
        return "BUY"
    return "HOLD"
