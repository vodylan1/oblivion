# pipelines/data_pipeline.py
"""
Data-Pipeline  · Phase 9-B
────────────────────────────────────────────────────────────────────────────
• Loads `config/watchlist.json`
• Fetches prices **per token** via  /defi/price?address=<mint>
• Always returns:
      {
        'sol_price'   : <float>,
        'token_prices': {mint: price, ...},
        'timestamp'   : <unix-ts>
      }
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, List

import requests

# ───────────────────── repo paths ─────────────────────────────────────────
_REPO   = Path(__file__).resolve().parents[1]
_SECRETS = _REPO / "config" / "secrets.json"
_WATCH   = _REPO / "config" / "watchlist.json"

_SOL_MINT = "So11111111111111111111111111111111111111112"
_ENDPOINT = "https://public-api.birdeye.so/defi/price"

_API_KEY: str | None = None
_CACHE  : Dict[str, float] = {}
_CACHE_TS = 0.0


# ───────────────────── helpers ────────────────────────────────────────────
def _load_key() -> None:
    global _API_KEY
    if _API_KEY is not None:
        return
    try:
        with open(_SECRETS, "r", encoding="utf-8") as fh:
            _API_KEY = json.load(fh).get("birdeye_api_key")  # ← correct key
    except FileNotFoundError:
        pass


def _load_watchlist() -> List[str]:
    if _WATCH.exists():
        try:
            lst: List[str] = json.loads(_WATCH.read_text())
            if lst:
                return lst
        except json.JSONDecodeError as exc:
            print(f"[DataPipeline] Malformed watchlist.json → {exc}")
    return [_SOL_MINT]                     # default = SOL only


def _fetch_price(mint: str) -> float:
    """Single call to Birdeye; raises on non-200 so caller can handle."""
    headers = {"X-API-KEY": _API_KEY} if _API_KEY else {}
    r = requests.get(_ENDPOINT, params={"address": mint}, headers=headers, timeout=4)
    r.raise_for_status()
    return float(r.json()["data"]["value"])


def _refresh_prices() -> None:
    """Refill the in-memory cache – throttled to once every 5 s."""
    global _CACHE, _CACHE_TS
    if time.time() - _CACHE_TS < 5:
        return                                     # keep last values

    _load_key()
    mints = _load_watchlist()
    prices: Dict[str, float] = {}

    for mint in mints:
        try:
            prices[mint] = _fetch_price(mint)
        except Exception as exc:                   # noqa: BLE001
            print(f"[DataPipeline] Birdeye fetch {mint[:4]}… failed → {exc!r}")
            prices[mint] = _CACHE.get(mint, 0.0)   # fallback to old value

    _CACHE, _CACHE_TS = prices, time.time()
    if _CACHE.get(_SOL_MINT):
        print(f"[DataPipeline] Live SOL price: {_CACHE[_SOL_MINT]:.2f}")


# ───────────────────── public API ─────────────────────────────────────────
def fetch_market_snapshot() -> Dict:
    """
    Called by main.py to obtain the latest market view.
    """
    _refresh_prices()
    sol = _CACHE.get(_SOL_MINT, 0.0)
    return {
        "sol_price": sol,
        "token_prices": _CACHE.copy(),
        "timestamp": time.time(),
    }


# Legacy alias so older code keeps working
fetch_sol_price = fetch_market_snapshot


def data_pipeline_init() -> None:
    print("[DataPipeline] Initialized.")
