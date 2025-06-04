"""
tests/test_scoring_neural.py
Verifies that the neural scorer obeys the weight file and clamps 0-100.
"""

# --------------------------------------------------------------------------- #
def test_neural_score_range():
    from core.scoring_engine.neural_score import compute_score

    score = compute_score({"sol_price": 0.0, "meme_hype": 150.0})
    assert 0.0 <= score <= 100.0


def test_neural_weight_bias(tmp_path, monkeypatch):
    """
    Point the scorer at a temporary weight file with extreme +99 bias.
    The score must be exactly 99 regardless of inputs.
    """
    cfg = tmp_path / "w.json"
    cfg.write_text('{"w_price": 0, "w_meme": 0, "bias": 99}')

    # Patch module constants, *then* reload the module so the new file is read
    import importlib
    from core.scoring_engine import neural_score as ns

    monkeypatch.setattr(ns, "_CFG_PATH", cfg)
    monkeypatch.setattr(ns, "_WEIGHTS", None)
    ns = importlib.reload(ns)                      # <<< refresh with temp cfg

    assert ns.compute_score({"sol_price": 200, "meme_hype": 0}) == 99.0
