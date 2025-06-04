"""
pipelines/data_pipeline.py
────────────────────────────────────────────────────────────────────────────
Phase 8-C  •  SOL/USD spot-price via Birdeye

✔ Uses the correct “defi/price” endpoint
✔ Accepts either "birdeye_api_key" **or** "birdeye_key" in secrets.json
✔ Falls back to the previous good price on any error
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Final, Mapping

import requests

# ------------------------------------------------------------------------ #
_REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[1]
_SECRETS   : Final[Path] = _REPO_ROOT / "config" / "secrets.json"

_SOL_MINT  : Final[str] = "So11111111111111111111111111111111111111112"

# *** single-line patch:  public → defi  ***
_BIRDEYE_URL: Final[str] = (
    "https://public-api.birdeye.so/defi/price"
    f"?address={_SOL_MINT}"
)

_LAST_PRICE: float = 150.0          # seeded fallback


# ------------------------------------------------------------------------ #
def data_pipeline_init() -> None:
    print("[DataPipeline] Initialized.")


def _load_birdeye_key() -> str | None:
    """Return the key from secrets.json (either field name is accepted)."""
    try:
        cfg: Mapping[str, Any] = json.loads(_SECRETS.read_text("utf-8"))
        return cfg.get("birdeye_api_key") or cfg.get("birdeye_key")
    except Exception:
        return None


def _birdeye_sol_price() -> float:
    api_key = _load_birdeye_key()
    if not api_key:
        raise RuntimeError("birdeye_api_key missing in secrets.json")

    headers = {"X-API-KEY": api_key}
    resp = requests.get(_BIRDEYE_URL, headers=headers, timeout=4)
    resp.raise_for_status()

    price = float(resp.json()["data"]["value"])
    print(f"[DataPipeline] SOL price fetched from Birdeye: {price:.2f}")
    return price


# ------------------------------------------------------------------------ #
def fetch_sol_price() -> dict[str, Any]:
    """
    Return {"sol_price": <float>, "timestamp": <unix-ts>}.
    """
    global _LAST_PRICE
    try:
        _LAST_PRICE = _birdeye_sol_price()
    except Exception as err:               # noqa: BLE001
        print(f"[DataPipeline] Birdeye error: {err!r} → using last price.")
    return {"sol_price": _LAST_PRICE, "timestamp": time.time()}
