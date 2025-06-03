"""
position_manager.py  · Phase 7-4

In-memory store for open-/closed positions.
Will be swapped for an on-chain / DB version later.
"""

from __future__ import annotations

from typing import Dict, List, TypedDict

# Basic typed record
class Position(TypedDict):
    side: str           # LONG | SHORT
    size: float         # notional in USD for demo
    entry: float        # entry price
    exit: float | None  # set on close
    pnl: float | None   # set on close


class _PM:
    def __init__(self) -> None:
        self._open: Dict[str, Position] = {}
        self._history: List[Position] = []
        print("[PositionManager] Online – Phase 7-4")

    # ───── public helpers ───────────────────────────────
    def open(self, side: str, size: float, price: float) -> None:
        if side in self._open:
            print(f"[PositionManager] WARN: {side} already open → skipping")
            return
        self._open[side] = Position(side=side, size=size, entry=price,
                                    exit=None, pnl=None)

    def close(self, side: str, price: float) -> Position | None:
        pos = self._open.pop(side, None)
        if not pos:
            print(f"[PositionManager] WARN: no {side} to close")
            return None

        # PnL:  (price - entry) × size   (sign depends on side)
        raw = (price - pos["entry"]) * pos["size"]
        pos["exit"] = price
        pos["pnl"] = raw if pos["side"] == "LONG" else -raw
        self._history.append(pos)
        return pos

    # Stats / CLI
    def list_open(self) -> Dict[str, Position]:
        return self._open

    def list_history(self, n: int = 5) -> List[Position]:
        return self._history[-n:]


# singleton
PM = _PM()
