"""
derivatives_engine.py   – Phase 7 starter
• Wires Drift Client if available.
• Falls back to dummy implementation when offline or config missing.
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass

# ────────────────────────────────────────────────────────────────────────────
@dataclass
class DerivativesEngine:
    endpoint: str = "https://api.devnet.solana.com"

    def __post_init__(self) -> None:
        try:
            driftpy = importlib.import_module("driftpy")
            self.drift_client = driftpy.DriftClient(endpoint=self.endpoint)  # type: ignore
            print("[DerivativesEngine] Online – cluster:", self.endpoint.split("//")[1].split(".")[0])
        except Exception as e:
            self.drift_client = None
            print("[DerivativesEngine] Drift not available, running in stub mode –", e)

    # ------------------------------------------------------------------ #
    def open_short(self, amount: float) -> None:
        if self.drift_client is None:
            print(f"[DerivativesEngine] (STUB) open_short {amount}")
            return
        # TODO: implement real call
        print("[DerivativesEngine] open_short not yet implemented")

    def close_short(self) -> None:
        if self.drift_client is None:
            print("[DerivativesEngine] (STUB) close_short")
            return
        # TODO: implement real call
        print("[DerivativesEngine] close_short not yet implemented")


# simple helper for existing imports
def derivatives_engine_init() -> None:
    global _ENGINE
    _ENGINE = DerivativesEngine()
