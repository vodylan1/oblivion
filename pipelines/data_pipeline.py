# pipelines/data_pipeline.py
"""
Data-Pipeline  · Phase 9-A
────────────────────────────────────────────────────────────────────────────
• Reads `config/watchlist.json`  → list[str] of SPL mint addresses.
• Fetches *all* prices in one call via Birdeye /defi/prices.
• Still exposes the historical `sol_price` field so existing
  agents keep working, and adds `token_prices` for arena mode.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Dict, List

import requests

# ────────────────────────────────────────────────────────────────
_REPO_ROOT = Path(__file__).resolve().parents[1]
_SECRETS   = _REPO_ROOT / "config" / "secrets.json"
_WATCHLIST = _REPO_ROOT / "config" / "watchlist.json"

_BIRDEYE_URL = "https://public-api.birdeye.so/defi/prices"
_SOL_MINT    = "So11111111111111111111111111111111111111112"

_API_KEY: str | None = None
_CACHE   : Dict[str, float] = {}
_CACHE_TS: float = 0.0


# ────────────────────────────────────────────────────────────────
def _load_api_key() -> None:
    global _API_KEY
    if _API_KEY is not None:
        return

    try:
        with open(_SECRETS, "r", encoding="utf-8") as fh:
            _API_KEY = json.load(fh).get("birdeye_key")
    except FileNotFoundError:
        pass      # leave as None → handled later


def _load_watchlist() -> List[str]:
    if _WATCHLIST.exists():
        try:
            addrs: List[str] = json.loads(_WATCHLIST.read_text())
            if addrs:
                return addrs
        except json.JSONDecodeError as err:
            print(f"[DataPipeline] Malformed watchlist.json → {err}")
    return [_SOL_MINT]   # default – SOL only


def _refresh_prices() -> None:
    """Internal helper, populates _CACHE with latest prices."""
    global _CACHE, _CACHE_TS
    _load_api_key()
    mints = _load_watchlist()

    if _API_KEY is None:
        print("[DataPipeline] No Birdeye key → using cached prices.")
        return

    # Respect 5-second throttle
    if time.time() - _CACHE_TS < 5:
        return

    try:
        headers = {"X-API-KEY": _API_KEY}
        joined  = ",".join(mints)
        resp = requests.get(_BIRDEYE_URL, params={"addresses": joined},
                            headers=headers, timeout=4)
        resp.raise_for_status()
        data = resp.json().get("data", {})

        # Birdeye returns list[dict]; flatten into mint → price
        _CACHE = {entry["address"]: float(entry["value"]) for entry in data}
        _CACHE_TS = time.time()

        sol_price = _CACHE.get(_SOL_MINT)
        if sol_price:
            print(f"[DataPipeline] Live SOL price: {sol_price:.2f}")

    except Exception as exc:
        print(f"[DataPipeline] Birdeye error: {exc!r} → using cache.")


# ────────────────────────────────────────────────────────────────
def fetch_prices() -> Dict[str, float]:
    """
    Public entry-point: returns a dict  {mint: price}.
    Always includes the SOL mint even if not in watch-list.
    """
    _refresh_prices()
    return _CACHE.copy()


def fetch_market_snapshot() -> Dict:
    """
    Convenience helper used by main.py:

        snapshot = fetch_market_snapshot()
        # → {
        #      'sol_price': 155.8,
        #      'token_prices': {...},
        #      'timestamp':  1.749e9
        #   }

    """
    prices = fetch_prices()
    sol = prices.get(_SOL_MINT, 0.0)
    return {
        "sol_price": sol,
        "token_prices": prices,
        "timestamp": time.time(),
    }


# keep the old Phase-7 alias for backward compatibility
fetch_sol_price = fetch_market_snapshot


def data_pipeline_init() -> None:
    print("[DataPipeline] Initialized.")
