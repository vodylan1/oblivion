# pipelines/data_pipeline.py
"""
Data-Pipeline  · Phase 9-C
────────────────────────────────────────────────────────────────────────────
Birdeye dev-tier friendly:
•   per-mint cache with 30 s TTL
•   60 s cool-off after HTTP 429
•   graceful fallback on malformed JSON
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, List, Tuple

import requests

# ───────────────────────── paths ──────────────────────────────────────────
_REPO     = Path(__file__).resolve().parents[1]
_SECRETS  = _REPO / "config" / "secrets.json"
_WATCH    = _REPO / "config" / "watchlist.json"

_SOL_MINT = "So11111111111111111111111111111111111111112"
_ENDPOINT = "https://public-api.birdeye.so/defi/price"

_API_KEY: str | None = None

# per-mint cache:  mint → (price, ts_fetched, ts_last_429)
_CACHE: Dict[str, Tuple[float, float, float]] = {}


# ───────────────────────── helpers ────────────────────────────────────────
def _load_key() -> None:
    global _API_KEY
    if _API_KEY is not None:
        return
    try:
        with open(_SECRETS, "r", encoding="utf-8") as fh:
            _API_KEY = json.load(fh).get("birdeye_api_key")
    except FileNotFoundError:
        pass


def _watchlist() -> List[str]:
    if _WATCH.exists():
        try:
            return json.loads(_WATCH.read_text())
        except json.JSONDecodeError as exc:
            print(f"[DataPipeline] malformed watchlist → {exc}")
    return [_SOL_MINT]


def _query_birdeye(mint: str) -> float | None:
    """Return price or None on hard failure."""
    headers = {"X-API-KEY": _API_KEY} if _API_KEY else {}
    try:
        r = requests.get(_ENDPOINT,
                         params={"address": mint},
                         headers=headers,
                         timeout=4)
        if r.status_code == 429:
            # register cool-off
            _CACHE[mint] = (_CACHE.get(mint, (0.0, 0.0, 0.0))[0],
                            time.time(),         # keep ts_fetched
                            time.time())         # last_429
            return None
        r.raise_for_status()
        value = r.json()["data"]["value"]          # KeyError if missing
        return float(value)
    except (requests.RequestException, KeyError) as exc:
        print(f"[DataPipeline] Birdeye {mint[:4]}… err → {exc!r}")
        return None


def _maybe_update(mint: str) -> None:
    """
    Fetch fresh quote for *mint* if:
        • older than 30 s  AND
        • we’re not inside the 60 s cool-off after a 429
    """
    price, ts_last, ts_429 = _CACHE.get(mint, (0.0, 0.0, 0.0))
    now = time.time()

    if now - ts_last < 30:             # still fresh
        return
    if now - ts_429 < 60:              # cool-off window
        return

    new_price = _query_birdeye(mint)
    if new_price is not None:
        _CACHE[mint] = (new_price, now, ts_429)


# ───────────────────────── public surface ─────────────────────────────────
def fetch_market_snapshot() -> Dict:
    """
    Return consistent market view consumed by main.py.
    """
    _load_key()
    for m in _watchlist():
        _maybe_update(m)

    sol_price = _CACHE.get(_SOL_MINT, (0.0, 0.0, 0.0))[0]
    if sol_price:
        print(f"[DataPipeline] Live SOL price: {sol_price:.2f}")

    return {
        "sol_price": sol_price,
        "token_prices": {m: _CACHE[m][0] for m in _CACHE},
        "timestamp": time.time(),
    }


# keep legacy alias
fetch_sol_price = fetch_market_snapshot


def data_pipeline_init() -> None:
    print("[DataPipeline] Initialized.")
