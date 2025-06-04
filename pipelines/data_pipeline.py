# pipelines/data_pipeline.py
"""
Data-Pipeline  · Phase 9-C
────────────────────────────────────────────────────────────────────────────
• Loads a watch-list from  config/watchlist.json  (array of SPL mint addrs)
• Fetches prices per-token with Birdeye  /defi/price?address=<mint>
• Per-mint local cache (5 s TTL).  429 responses trigger a 60 s cool-off.
• Exposes helper:

      snapshot = fetch_market_snapshot()
      # {
      #   'sol_price'   : 157.4,
      #   'token_prices': {mint: price, …},
      #   'timestamp'   : 1.749e9
      # }

Compatible with the rest of the stack (main.py still calls
`fetch_sol_price` alias).
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, List

import requests

# ─── repo paths ───────────────────────────────────────────────────────────
_REPO_ROOT  = Path(__file__).resolve().parents[1]
_SECRETS_F  = _REPO_ROOT / "config" / "secrets.json"
_WATCHLIST_F = _REPO_ROOT / "config" / "watchlist.json"

# ─── constants ────────────────────────────────────────────────────────────
_SOL_MINT     = "So11111111111111111111111111111111111111112"
_BIRDEYE_URL  = "https://public-api.birdeye.so/defi/price"
_CACHE_TTL    = 5          # seconds for a normal OK fetch
_COOL_OFF_429 = 60         # seconds to wait after a rate-limit

# ─── globals (populated lazily) ───────────────────────────────────────────
_API_KEY: str | None = None
_CACHE  : Dict[str, Dict[str, float]] = {}    # mint ➞ {"price": .., "ts": .., "error_until": ..}


# ─── helpers ──────────────────────────────────────────────────────────────
def _load_api_key() -> None:
    global _API_KEY
    if _API_KEY is not None:
        return
    try:
        data = json.loads(_SECRETS_F.read_text())
        _API_KEY = data.get("birdeye_api_key") or data.get("birdeye_key")
    except FileNotFoundError:
        pass


def _load_watchlist() -> List[str]:
    if not _WATCHLIST_F.exists():
        return [_SOL_MINT]

    try:
        arr = json.loads(_WATCHLIST_F.read_text())
        return arr if isinstance(arr, list) and arr else [_SOL_MINT]
    except json.JSONDecodeError as err:
        print(f"[DataPipeline] watchlist.json malformed → {err}")
        return [_SOL_MINT]


def _need_fetch(mint: str) -> bool:
    """True if we should hit Birdeye for *mint* now."""
    rec = _CACHE.get(mint)
    now = time.time()
    if rec is None:
        return True
    if rec.get("error_until", 0) > now:       # still cooling off
        return False
    return now - rec["ts"] > _CACHE_TTL       # stale


def _fetch_single(mint: str) -> None:
    _load_api_key()

    if _API_KEY is None:
        return                               # leave price missing (== 0)

    headers = {"X-API-KEY": _API_KEY}
    try:
        resp = requests.get(_BIRDEYE_URL, params={"address": mint},
                            headers=headers, timeout=4)
        if resp.status_code == 429:
            raise requests.HTTPError("429 Too Many Requests", response=resp)
        resp.raise_for_status()

        price = float(resp.json()["data"]["value"])
        _CACHE[mint] = {"price": price,
                        "ts": time.time(),
                        "error_until": 0.0}

        if mint == _SOL_MINT:
            print(f"[DataPipeline] Live SOL price: {price:.2f}")

    except (KeyError, ValueError) as exc:          # malformed JSON
        print(f"[DataPipeline] Birdeye {mint[:4]}… err → {exc!r}")
        _CACHE[mint] = {"price": 0.0,
                        "ts": time.time(),
                        "error_until": time.time() + _CACHE_TTL}

    except requests.HTTPError as exc:
        if exc.response is not None and exc.response.status_code == 429:
            print(f"[DataPipeline] Birdeye 429 for {mint[:4]}… – cooling { _COOL_OFF_429 } s")
            _CACHE[mint] = {"price": _CACHE.get(mint, {}).get("price", 0.0),
                            "ts": time.time(),
                            "error_until": time.time() + _COOL_OFF_429}
        else:
            print(f"[DataPipeline] Birdeye {mint[:4]}… HTTP err → {exc!r}")
            _CACHE[mint] = {"price": 0.0,
                            "ts": time.time(),
                            "error_until": time.time() + _CACHE_TTL}

    except requests.RequestException as exc:
        print(f"[DataPipeline] Birdeye net err {mint[:4]}… → {exc!r}")
        _CACHE[mint] = {"price": 0.0,
                        "ts": time.time(),
                        "error_until": time.time() + _CACHE_TTL}


# ─── public API ───────────────────────────────────────────────────────────
def fetch_prices() -> Dict[str, float]:
    """
    Return {mint: price}.  All mints in watch-list are guaranteed to appear
    (price==0.0 if unavailable).
    """
    mints = _load_watchlist()
    for m in mints:
        if _need_fetch(m):
            _fetch_single(m)

    # expose only the numeric price
    return {m: _CACHE.get(m, {}).get("price", 0.0) for m in mints}


def fetch_market_snapshot() -> Dict:
    """Wrapper used by main.py."""
    prices = fetch_prices()
    return {
        "sol_price": prices.get(_SOL_MINT, 0.0),
        "token_prices": prices,
        "timestamp": time.time(),
    }


# Back-compat alias for older imports
fetch_sol_price = fetch_market_snapshot


def data_pipeline_init() -> None:
    print("[DataPipeline] Initialized.")
