"""
notifier.py – Phase 7-4 b
Sends plain text to the webhook defined in config/secrets.json.
• Prints the server’s response body on non-2xx codes.
• Silently disables itself if the config file is missing / malformed.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Final

import requests

# --------------------------------------------------------------------------- #
# Load once
# --------------------------------------------------------------------------- #

def _load_webhook() -> str | None:
    cfg_path: Final = (
        Path(__file__).resolve().parent.parent / "config" / "secrets.json"
    )
    try:
        with cfg_path.open(encoding="utf-8") as fh:
            data = json.load(fh)
        url: str | None = data.get("webhook_url")
        if not url:
            raise ValueError("key 'webhook_url' missing or empty")
        return url.strip()
    except Exception as exc:  # noqa: BLE001
        print(f"[Notifier] Disabled – cannot load webhook → {exc}")
        return None


_WEBHOOK_URL: Final = _load_webhook()


# --------------------------------------------------------------------------- #
# Public helper
# --------------------------------------------------------------------------- #

def notify(msg: str) -> None:
    """
    Fire-and-forget notification.
    If webhook is not configured, quietly returns.
    """
    if _WEBHOOK_URL is None:
        return

    try:
        r = requests.post(
            _WEBHOOK_URL,
            json={"content": msg},
            timeout=7,
        )
        if r.status_code not in (200, 204):
            print(f"[Notifier] HTTP {r.status_code}. Body → {r.text[:200]!r}")
    except Exception as exc:  # noqa: BLE001
        print(f"[Notifier] Error → {exc}")
