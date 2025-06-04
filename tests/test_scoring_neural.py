"""
test_scoring_neural.py
Assures composite scorer respects weight file and clamping.
"""

from core.scoring_engine.neural_score import compute_score


def test_neural_score_range():
    data = {"sol_price": 0.0, "meme_hype": 150.0}   # insane hype
    score = compute_score(data)
    assert 0.0 <= score <= 100.0


def test_neural_weight_bias(tmp_path, monkeypatch):
    # create temp weight file with extreme bias
    cfg = tmp_path / "w.json"
    cfg.write_text('{"w_price": 0, "w_meme": 0, "bias": 99}')

    # monkey-patch module attr so compute_score reads our file
    import importlib
    from core.scoring_engine import neural_score as ns

    monkeypatch.setattr(ns, "_CFG_PATH", cfg)
    importlib.reload(ns)

    score = ns.compute_score({"sol_price": 200, "meme_hype": 0})
    assert score == 99.0
