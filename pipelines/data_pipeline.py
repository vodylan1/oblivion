"""
pipelines/data_pipeline.py
────────────────────────────────────────────────────────────────────────────
Phase 8-C  •  SOL/USD spot-price via Birdeye

▪ Fetches the live SOL price from Birdeye’s “simple/price” endpoint
▪ Uses the correct mint address for wrapped SOL
▪ Falls back to the last good price if the call fails
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Final, Mapping

import requests


# ──────────────────────────────────────────────────────────────────────────
_REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[1]
_SECRETS   : Final[Path] = _REPO_ROOT / "config" / "secrets.json"

# Correct SPL mint for SOL (wrapped SOL)
_SOL_MINT: Final[str] = "So11111111111111111111111111111111111111112"

_BIRDEYE_URL: Final[str] = (
    "https://public-api.birdeye.so/public/simple/price"
    f"?address={_SOL_MINT}"
)

_LAST_PRICE: float = 150.0     # seeded fallback


# ──────────────────────────────────────────────────────────────────────────
def data_pipeline_init() -> None:
    print("[DataPipeline] Initialized.")


def _load_birdeye_key() -> str | None:
    """Return the Birdeye API key from config/secrets.json or None."""
    try:
        cfg: Mapping[str, Any] = json.loads(_SECRETS.read_text("utf-8"))
        return cfg.get("birdeye_api_key")
    except Exception:        # File missing or malformed
        return None


def _birdeye_sol_price() -> float:
    """
    Query Birdeye and return the latest SOL/USD price.

    Raises
    ------
    RuntimeError         If the API key is missing.
    requests.HTTPError   If Birdeye responds with non-200.
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


# ──────────────────────────────────────────────────────────────────────────
def fetch_sol_price() -> dict[str, Any]:
    """
    Public helper imported by main.py.

    Returns a dict ⇒  {"sol_price": 156.74, "timestamp": 1_749_044_808.12}
    """
    global _LAST_PRICE
    try:
        _LAST_PRICE = _birdeye_sol_price()
    except Exception as err:        # noqa: BLE001
        print(f"[DataPipeline] Birdeye error: {err!r} → using last price.")
    return {"sol_price": _LAST_PRICE, "timestamp": time.time()}
