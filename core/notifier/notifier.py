"""
notifier.py – send Discord webhook pings.

(unchanged docstring …)
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

import requests

# ─── locate repo-root/config/secrets.json ─────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parents[2]          # ← two levels up
CFG_PATH  = REPO_ROOT / "config" / "secrets.json"

_WEBHOOK: str | None = None
_INITIALISED = False


def _lazy_init() -> None:             # ― only the path logic changed
    global _WEBHOOK, _INITIALISED
    if _INITIALISED:
        return
    try:
        with CFG_PATH.open("r", encoding="utf-8") as fh:
            data: dict[str, Any] = json.load(fh)
            _WEBHOOK = data.get("webhook_url")
            if _WEBHOOK:
                print("[Notifier] Webhook loaded OK.")
            else:
                print("[Notifier] No 'webhook_url' key → disabled.")
    except FileNotFoundError:
        print(f"[Notifier] {CFG_PATH} missing → notifier disabled.")
    except json.JSONDecodeError as err:
        print(f"[Notifier] Malformed secrets.json → disabled.\n  ↳ {err}")
    finally:
        _INITIALISED = True
# … rest of file unchanged …
