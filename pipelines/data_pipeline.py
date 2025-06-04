"""
pipelines/data_pipeline.py
──────────────────────────────────────────────────────────────────────────────
Phase 8-C

* Live SOL ↔ USD spot-price via Birdeye “simple/price” endpoint
* Fallback to last-known price if the call fails
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Final, Mapping

import requests


# ─── constants ──────────────────────────────────────────────────────────────
_REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[1]
_SECRETS   : Final[Path] = _REPO_ROOT / "config" / "secrets.json"

# Correct SPL-mint address for SOL (wrapped SOL)
_SOL_MINT: Final[str] = "So11111111111111111111111111111111111111112"

_BIRDEYE_URL: Final[str] = (
    "https://public-api.birdeye.so/public/simple/price"
    f"?address={_SOL_MINT}"
)

_LAST_PRICE: float = 150.0          # seed fallback


# ─── helpers ────────────────────────────────────────────────────────────────
def data_pipeline_init() -> None:
    print("[DataPipeline] Initialized.")


def _load_birdeye_key() -> str | None:
    """
    Return the `birdeye_api_key` from config/secrets.json
    or None if not present / malformed.
    """
    try:
        cfg: Mapping[str, Any] = json.loads(_SECRETS.read_text("utf-8"))
        return cfg.get("birdeye_api_key")
    except Exception:          # FileNotFound, JSONDecodeError, …
        return None


def _birdeye_sol_price() -> float:
    """
    Query Birdeye’s free ‘simple/price’ endpoint.

    Raises
    ------
    RuntimeError   if the API key is missing
    requests.HTTPError   if Birdeye returns non-200
    """
    api_key = _load_birdeye_key()
    if not api_key:
        raise RuntimeError("birdeye_api_key missing in secrets.json")

    headers = {"X-API-KEY": api_key}
    resp = requests.get(_BIRDEYE_URL, headers=headers, timeout=4)
    resp.raise_for_status()

    price = float(resp.json()["data"]["value"])
    print(f"[DataPipeline] SOL price fetched from Birdeye: {price:.2f}")
    return price


# ─── public façade ─────────────────────────────────────────────────────────
def fetch_sol_price() -> dict[str, Any]:
    """
    Universal price fetch used by `main.py`.

    Returns
    -------
    dict
        {
            "sol_price": 156.04,
            "timestamp": 1_749_044_808.123
        }
    """
    global _LAST_PRICE
    try:
        _LAST_PRICE = _birdeye_sol_price()
    except Exception as err:      # noqa: BLE001  (catch - log - carry on)
        print(f"[DataPipeline] Birdeye error: {err!r} → using last price.")
    return {"sol_price": _LAST_PRICE, "timestamp": time.time()}
