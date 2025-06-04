"""
position_manager.py  – Phase-7-5  (fixed)

Keeps a ledger of open / closed positions.
The JSON ledger lives in  storage/positions.json
so we survive restarts.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List

# ────────────────────────────────────────────────────────────────
_STORAGE = Path(__file__).parent.parent / "storage"
_STORAGE.mkdir(exist_ok=True)
_FILE = _STORAGE / "positions.json"          # ← no stray space!

# ----------------------------------------------------------------
class _PositionManager:
    def __init__(self) -> None:
        self._open: List[Dict[str, Any]] = []
        self._hist: List[Dict[str, Any]] = []
        self._load()

    # ----- persistence ------------------------------------------
    def _load(self) -> None:
        if not _FILE.exists():
            return
        try:
            data: Dict[str, Any] = json.loads(_FILE.read_text())
            self._open = data.get("open", [])
            self._hist = data.get("history", [])
            print(f"[PositionManager] Restored {len(self._open)} open positions.")
        except Exception as err:  # noqa: BLE001
            print(f"[PositionManager] Corrupt ledger, starting fresh – {err}")

    def _flush(self) -> None:
        payload = {"open": self._open, "history": self._hist}
        _FILE.write_text(json.dumps(payload, indent=2))

    # ----- public helpers ---------------------------------------
    def open_long(self, size: float, price: float, sig: str) -> None:
        rec = {
            "ts": time.time(),
            "side": "LONG",
            "size": size,
            "entry": price,
            "sig": sig,
        }
        self._open.append(rec)
        self._flush()

    def close_long(self, price: float, sig: str) -> None:
        if not self._open:
            return
        pos = self._open.pop()
        pnl = (price - pos["entry"]) * pos["size"]
        rec = {**pos, "exit": price, "pnl": pnl, "close_sig": sig}
        self._hist.append(rec)
        self._flush()

    # ----- introspection ----------------------------------------
    def list_open(self) -> List[Dict[str, Any]]:
        return self._open

    def list_history(self, n: int = 5) -> List[Dict[str, Any]]:
        return self._hist[-n:]


# exported singleton
PM = _PositionManager()


def position_manager_init() -> None:
    print("[PositionManager] Online – Phase 7-5")
