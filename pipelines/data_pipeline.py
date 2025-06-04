# pipelines/data_pipeline.py
"""
Data-Pipeline · Phase 9-B
────────────────────────────────────────────────────────────────────────────
• Loads an (optional) watch-list from  `config/watchlist.json`
• If ONLY one mint is requested → uses Birdeye **/defi/price**
  (single-asset endpoint – works on every plan, avoids 404)
• If >1 mints are requested      → uses Birdeye **/defi/prices**
• Caches results for 5 s to respect Birdeye rate limits
• Always returns: {
      "sol_price":   float,            # SOL/USD
      "token_prices": {mint: price},   # all requested mints
      "timestamp":   unix_ts
  }
Existing callers (`fetch_sol_price`) remain backward-compatible.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, List

import requests

# ────────────────────────────────────────────────────────────────
_REPO_ROOT   = Path(__file__).resolve().parents[1]
_SECRETS     = _REPO_ROOT / "config" / "secrets.json"
_WATCHLIST   = _REPO_ROOT / "config" / "watchlist.json"

_SOL_MINT    = "So11111111111111111111111111111111111111112"
_URL_SINGLE  = "https://public-api.birdeye.so/defi/price"
_URL_MULTI   = "https://public-api.birdeye.so/defi/prices"

_API_KEY: str | None = None
_CACHE   : Dict[str, float] = {}
_CACHE_TS: float = 0.0


# ────────────────────────────────────────────────────────────────
def _load_api_key() -> None:
    """Populate _API_KEY once; accept either key property name."""
    global _API_KEY
    if _API_KEY is not None:
        return
    try:
        with open(_SECRETS, "r", encoding="utf-8") as fh:
            data = json.load(fh)
            _API_KEY = data.get("birdeye_key") or data.get("birdeye_api_key")
    except FileNotFoundError:
        pass  # run offline if secrets.json absent


def _load_watchlist() -> List[str]:
    """Return list of mint addresses to query (defaults to SOL only)."""
    if _WATCHLIST.exists():
        try:
            mints: List[str] = json.loads(_WATCHLIST.read_text())
            return mints or [_SOL_MINT]
        except json.JSONDecodeError as err:
            print(f"[DataPipeline] Malformed watchlist.json → {err}")
    return [_SOL_MINT]


def _refresh_prices() -> None:
    """Refresh _CACHE if 5 s elapsed since last fetch."""
    global _CACHE, _CACHE_TS
    _load_api_key()
    mints = _load_watchlist()

    if _API_KEY is None:
        print("[DataPipeline] No Birdeye key → using cached prices.")
        return
    if time.time() - _CACHE_TS < 5:  # throttle
        return

    try:
        headers = {"X-API-KEY": _API_KEY}

        # ── SINGLE-token fast-path ───────────────────────────────────────
        if len(mints) == 1:
            params = {"address": mints[0]}
            resp   = requests.get(_URL_SINGLE, params=params,
                                  headers=headers, timeout=4)
            resp.raise_for_status()
            value = float(resp.json()["data"]["value"])
            _CACHE = {mints[0]: value}

        # ── MULTI-token query ───────────────────────────────────────────
        else:
            joined = ",".join(mints)
            resp   = requests.get(_URL_MULTI,
                                  params={"addresses": joined},
                                  headers=headers, timeout=4)
            resp.raise_for_status()
            data = resp.json().get("data", [])
            _CACHE = {row["address"]: float(row["value"]) for row in data}

        _CACHE_TS = time.time()

        sol = _CACHE.get(_SOL_MINT)
        if sol is not None:
            print(f"[DataPipeline] Live SOL price: {sol:.2f}")

    except Exception as exc:  # noqa: BLE001
        print(f"[DataPipeline] Birdeye error: {exc!r} → using cache.")


# ────────────────────────────────────────────────────────────────
def fetch_prices() -> Dict[str, float]:
    """External API – returns {mint: price} (may be partially cached)."""
    _refresh_prices()
    return _CACHE.copy()


def fetch_market_snapshot() -> Dict:
    """Convenience helper used by main.py."""
    prices   = fetch_prices()
    sol_price = prices.get(_SOL_MINT, 0.0)
    return {
        "sol_price":   sol_price,
        "token_prices": prices,
        "timestamp":   time.time(),
    }


# Back-compat alias (older phases call this)
fetch_sol_price = fetch_market_snapshot


def data_pipeline_init() -> None:
    print("[DataPipeline] Initialized.")
