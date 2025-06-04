# intel/meme_scanner.py
"""
intel/meme_scanner.py
────────────────────────────────────────────────────────────────────────────
Phase-8 • real-data version

Uses Birdeye’s “trending” endpoint to derive a 0-100 meme-hype score.
"""

from __future__ import annotations

import json
import random
import time
from pathlib import Path
from typing import Any, Dict, Optional

import requests

from core.notifier.notifier import notify

# ───────────────────────────────────────────────────────────────────────────
_REPO_ROOT    = Path(__file__).resolve().parents[1]
_SECRETS_FILE = _REPO_ROOT / "config" / "secrets.json"

_API_KEY: Optional[str] = None
_INIT_DONE = False

_ENDPOINT = (
    "https://public-api.birdeye.so/defi/trending/trade"
    "?sort_by=trade_24h&time=1h&limit=50&offset=0"
)


# ───────────────────────────────────────────────────────────────────────────
def _lazy_init() -> None:
    """Load API key once; accept both legacy and new property names."""
    global _API_KEY, _INIT_DONE
    if _INIT_DONE:
        return

    try:
        data: Dict[str, Any] = json.loads(_SECRETS_FILE.read_text("utf-8"))
        # NEW ⇣  (accept either property)
        _API_KEY = data.get("birdeye_key") or data.get("birdeye_api_key")
        if _API_KEY:
            print("[MemeScanner] Birdeye key loaded ✓")
        else:
            print("[MemeScanner] No Birdeye key – fallback to random hype")
    except FileNotFoundError:
        print("[MemeScanner] secrets.json missing – using random hype")
    except json.JSONDecodeError as err:
        print(f"[MemeScanner] Malformed secrets.json – {err}")
    finally:
        _INIT_DONE = True


# ───────────────────────────────────────────────────────────────────────────
def meme_scanner_init() -> None:
    _lazy_init()
    status = "Birdeye feed" if _API_KEY else "random fallback"
    print(f"[MemeScanner] Online – {status}")


def _fetch_hype_score() -> float:
    """Call Birdeye and turn top-trending token into 0-100 hype score."""
    headers = {"X-API-KEY": _API_KEY}
    resp = requests.get(_ENDPOINT, headers=headers, timeout=4)
    resp.raise_for_status()

    data = resp.json().get("data", [])
    if not data:
        raise RuntimeError("empty response")

    top = data[0]
    volume_rank = 1                      # we already grabbed rank-1
    tweet_rank  = top.get("twitter_rank", 50)

    vol_score   = max(0, 100 - volume_rank * 2)
    tweet_score = max(0, 100 - tweet_rank * 2)
    return float(min(vol_score + tweet_score, 100))


# ---------------------------------------------------------------------------
def scan_feeds() -> Dict[str, float]:
    """
    Public helper imported by main.py.
    Returns {"meme_hype": <float>} always.
    """
    _lazy_init()

    if not _API_KEY:
        return {"meme_hype": round(random.random() * 100, 2)}

    try:
        score = _fetch_hype_score()
        return {"meme_hype": round(score, 2)}
    except Exception as exc:  # noqa: BLE001
        notify(f"⚠️ MemeScanner error → {exc!r}")
        return {"meme_hype": round(random.random() * 100, 2)}
