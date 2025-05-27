"""
scoring_engine.py

Phase 4: Introduce a basic SCORING_ENGINE that computes a simple
risk–reward score for the given market data.
"""

def scoring_engine_init():
    """Initialize SCORING_ENGINE (placeholder)."""
    print("[ScoringEngine] Initialized.")

def compute_score(market_data: dict) -> float:
    """
    Compute a basic risk–reward score based on the current market data.
    For demonstration, we'll do something naive:
      - If sol_price is low, reward is high,
      - If sol_price is high, risk is high.
    Returns a float 0-100, where higher = more attractive to buy.
    """
    sol_price = market_data.get("sol_price", 0.0)

    # Example logic (totally naive):
    # Let's define a reference "sweet spot" as 20
    # Score decreases as price moves away from 20
    ideal_price = 20.0

    difference = abs(sol_price - ideal_price)
    # The further from 20, the lower the score
    base_score = max(0, 100 - difference * 4)  # each point away from 20 costs 4 points

    # We might add more factors in the future (volume, sentiment, etc.)
    return base_score
