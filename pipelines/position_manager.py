"""
pipelines/position_manager.py
────────────────────────────────────────────────────────────────────────────
Very light position registry until the full ledger arrives in Phase 8.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List


# ─── internal data ────────────────────────────────────────────────────────
@dataclass
class _Position:
    side: str          # LONG | SHORT
    open_px: float
    size: float        # contracts, placeholder
    pnl: float = 0.0
    closed: bool = False


class PM:
    """
    Singleton-ish helper; acts as crude in-memory database.
    Usage:
        from pipelines.position_manager import PM
        PM.open("LONG", 160.0)
        PM.close("LONG", 162.0)
        PM.list_open()
    """

    _open:  List[_Position] = []
    _hist:  List[_Position] = []

    # -------- operations --------------------------------------------------
    @classmethod
    def open(cls, side: str, px: float, size: float = 1.0) -> None:
        cls._open.append(_Position(side, px, size))

    @classmethod
    def close(cls, side: str, px: float) -> None:
        for pos in cls._open:
            if pos.side == side and not pos.closed:
                pos.pnl = (px - pos.open_px) * pos.size * (1 if side == "LONG" else -1)
                pos.closed = True
                cls._hist.append(pos)
        cls._open = [p for p in cls._open if not p.closed]

    # -------- queries -----------------------------------------------------
    @classmethod
    def list_open(cls):      return cls._open
    @classmethod
    def list_history(cls):   return cls._hist[-5:]

# ─── legacy wrapper expected by main.py ───────────────────────────────────
def position_manager_init():
    """
    Maintain backward-compat with earlier phases.
    Called once from main.py; returns the PM class so callers can do:

        pm = position_manager_init()
        pm.open(...)
    """
    print("[PositionManager] Online – Phase 7-4")
    return PM
