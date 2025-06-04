"""
data_pipeline.py
────────────────────────────────────────────────────────────────────────────
Phase-8-C – live SOL price via Birdeye “simple price” endpoint.
Falls back to last known price on API error.
"""

from __future__ import annotations

import time
import json
from typing import Final

from pathlib import Path

import requests

# ─── secrets ──────────────────────────────────────────────────────────────
_REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[1]   # ← fixed
_SECRETS   : Final[Path] = _REPO_ROOT / "config" / "secrets.json"

_BIRDEYE_KEY: str | None = None
_LAST_PRICE  = 150.0   # sane default if first call fails


def _load_key() -> None:
    global _BIRDEYE_KEY
    try:
        _BIRDEYE_KEY = json.loads(_SECRETS.read_text()).get("birdeye_api_key")
    except Exception:
        _BIRDEYE_KEY = None


def data_pipeline_init() -> None:
    """Called once from main.py."""
    _load_key()
    print("[DataPipeline] Initialized.")


# ─── helpers ──────────────────────────────────────────────────────────────
def _birdeye_sol_price() -> float:
    """Query Birdeye for SOL/USD and return the float price."""
    if not _BIRDEYE_KEY:
        raise RuntimeError("birdeye_api_key missing in secrets.json")

    url = (
        "https://public-api.birdeye.so/public/simple/price"
        "?address=solana"
    )
    headers = {"X-API-KEY": _BIRDEYE_KEY}
    resp = requests.get(url, headers=headers, timeout=4)
    resp.raise_for_status()

    data = resp.json()          # {"data":{"value":155.97},"success":true}
    return float(data["data"]["value"])


# ─── public API -----------------------------------------------------------
def fetch_sol_price() -> dict[str, float]:
    """
    Return dict with keys sol_price and timestamp.
    Falls back to the last good price if Birdeye errors out.
    """
    global _LAST_PRICE
    ts = time.time()

    try:
        price = _birdeye_sol_price()
        _LAST_PRICE = price
        print(f"[DataPipeline] SOL price fetched from Birdeye: {price:.2f}")
    except Exception as err:
        print(f"[DataPipeline] Birdeye error: {err!r} → using last price.")
        price = _LAST_PRICE

    return {"sol_price": price, "timestamp": ts}
