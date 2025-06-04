"""
core/scoring_engine/neural_score.py
────────────────────────────────────────────────────────────────────────────
Phase-8 stub – “neural” composite score.

For now we keep it deterministic and *very* light-weight:

    score =
        0.60 × price_score +
        0.25 × meme_hype_score +
        0.15 × whale_risk_penalty

• price_score replicates the legacy linear curve from scoring_engine.py
• meme_hype_score is simply the meme_hype % already in market_data
• whale_risk_penalty is 0 unless market_data["whale_alert"] is True
  (then we subtract 25 points)

The function signature matches the old compute_score so callers can
switch over without changes.
"""

from __future__ import annotations

# --- reuse the constants from the legacy engine ---------------------------
from core.scoring_engine.scoring_engine import (
    IDEAL_PRICE,
    POINTS_PER_USD,
    MIN_SCORE,
    MAX_SCORE,
)


def _price_component(price: float) -> float:
    dist = abs(price - IDEAL_PRICE)
    raw  = MAX_SCORE - dist * POINTS_PER_USD
    return max(MIN_SCORE, min(MAX_SCORE, raw))


def compute_score(market_data: dict) -> float:        # noqa: D401
    """
    Return a float ∈ [0, 100] – higher ⇒ more attractive to BUY.
    The weighting can be tuned / evolved later.
    """
    price       = float(market_data.get("sol_price", 0.0))
    meme_hype   = float(market_data.get("meme_hype", 0.0))        # already 0-100
    whale_panic = 25.0 if market_data.get("whale_alert") else 0.0

    price_score = _price_component(price)
    meme_score  = meme_hype                       # simple 1-for-1 mapping
    risk_penalty = whale_panic

    combined = (
        0.60 * price_score +
        0.25 * meme_score  -
        0.15 * risk_penalty
    )

    return max(MIN_SCORE, min(MAX_SCORE, round(combined, 2)))
