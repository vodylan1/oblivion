"""
tests/test_scoring_neural.py
Verifies that the neural scorer obeys the weight file and clamps 0-100.
"""

# ---------------------------------------------------------------------- #
def test_neural_score_range():
    # late import ensures we pick up the current config on every run
    from core.scoring_engine.neural_score import compute_score

    data = {"sol_price": 0.0, "meme_hype": 150.0}
    score = compute_score(data)
    assert 0.0 <= score <= 100.0


def test_neural_weight_bias(tmp_path, monkeypatch):
    """
    Create a temporary weight file with extreme +99 bias.
    The scorer should return exactly 99 regardless of inputs.
    """
    cfg = tmp_path / "w.json"
    cfg.write_text('{"w_price": 0, "w_meme": 0, "bias": 99}')

    import importlib
    from core.scoring_engine import neural_score as ns

    monkeypatch.setattr(ns, "_CFG_PATH", cfg)
    monkeypatch.setattr(ns, "_WEIGHTS", None)   # clear cached weights
    ns = importlib.reload(ns)                   # reload with temp config

    assert ns.compute_score({"sol_price": 200, "meme_hype": 0}) == 99.0
