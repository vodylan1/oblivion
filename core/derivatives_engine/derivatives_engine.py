"""
core/derivatives_engine/derivatives_engine.py
─────────────────────────────────────────────
Phase 7   – “real-but-safe” implementation

* Tries to spin-up an on-chain Drift client (devnet by default).
* If Drift (or any compiled dependency) is missing / breaks,
  falls back to an **in-process stub** so the rest of the bot
  continues to run.

Public surface
──────────────
• derivatives_engine_init(cluster="devnet") → DerivativesEngineLike

  The returned object – real or stub – exposes the following
  no-risk methods you can already call elsewhere without crashing:

      .open_short(product_symbol, size)
      .close_short(position_id)

  Real implementation is obviously not finished; the stub just logs.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

# ---------------------------------------------------------------------
# 1.  Utility - STUB implementation
# ---------------------------------------------------------------------


@dataclass
class _StubPosition:
    """Represents a dummy derivatives position we keep in-memory only."""
    position_id: int
    product: str
    size: float
    opened_ts: float


class _StubDerivativesEngine:
    """
    “Fake” engine used when Drift cannot be imported (e.g. Windows
    boxes without Rust tool-chain).  It prints what it *would* do and
    stores positions in a tiny in-memory list so that later phases can
    read / iterate over them if needed.
    """

    def __init__(self, cluster: str = "devnet") -> None:
        self.cluster = cluster
        self._positions: list[_StubPosition] = []
        self._next_id = 1
        print(f"[DerivativesEngine] Stub Online – cluster: {cluster}")

    # ── public API ────────────────────────────────────────────────────
    def open_short(self, product: str, size: float) -> int:
        pos = _StubPosition(
            position_id=self._next_id,
            product=product,
            size=size,
            opened_ts=time.time(),
        )
        self._positions.append(pos)
        self._next_id += 1
        print(
            f"[DerivativesEngine-STUB] OPEN SHORT  id={pos.position_id} "
            f"product={product} size={size}"
        )
        return pos.position_id

    def close_short(self, position_id: int) -> None:
        pos = next((p for p in self._positions if p.position_id == position_id), None)
        if not pos:
            print(f"[DerivativesEngine-STUB] CLOSE SHORT  id={position_id} NOT-FOUND")
            return
        self._positions.remove(pos)
        pnl = round((0.5 - 0.5) * pos.size, 4)  # always 0 for now
        print(
            f"[DerivativesEngine-STUB] CLOSE SHORT  id={position_id} "
            f"product={pos.product} pnl≈{pnl}"
        )

    # ──────────────────────────────────────────────────────────────────
    def list_open_positions(self) -> list[_StubPosition]:
        """Helper for debugging or later UI work."""
        return list(self._positions)


# ---------------------------------------------------------------------
# 2.  Attempt a real Drift-py initialisation
# ---------------------------------------------------------------------


def _try_init_drift(cluster: str):
    """
    If driftpy + solana stack are present *and* compile correctly,
    build a minimal client object and return it.  We do not execute
    real trades in this phase – just prove the library loads.

    Returns a tuple: (success: bool, obj_or_exc)
    """
    try:
        from driftpy.drift_client import DriftClient  # type: ignore
        from solders.keypair import Keypair           # type: ignore
        from solana.rpc.api import Client             # type: ignore

        # Very slim client set-up – devnet only for now
        endpoint = "https://api.devnet.solana.com" if cluster == "devnet" else \
                   "https://api.mainnet-beta.solana.com"
        sol_client = Client(endpoint)
        kp = Keypair()  # temporary throw-away keypair

        drift = DriftClient(
            connection=sol_client,
            wallet=kp,
            cluster=cluster,
        )

        print(f"[DerivativesEngine] Online – cluster: {cluster}")
        return True, drift

    except Exception as exc:  # noqa: BLE001
        return False, exc


# ---------------------------------------------------------------------
# 3.  Public factory
# ---------------------------------------------------------------------


def derivatives_engine_init(cluster: str = "devnet"):
    """
    This is what `main.py` (or any other orchestrator) should call.

        derivatives_engine = derivatives_engine_init()

    The caller gets back **something** that has .open_short() /
    .close_short() methods, regardless of the environment.
    """
    ok, obj = _try_init_drift(cluster)

    if ok:
        # Thin compatibility wrapper so both real and stub share
        # method names the rest of the app expects.
        class _DriftWrapper:
            def __init__(self, client):
                self._client = client

            # NOTE: real trade wiring TBD in Phase 7-2
            def open_short(self, product: str, size: float) -> int:
                print(
                    "[DerivativesEngine-REAL] (placeholder) "
                    f"Would open short on {product} size={size}"
                )
                return int(time.time())  # fake id for now

            def close_short(self, position_id: int) -> None:
                print(
                    "[DerivativesEngine-REAL] (placeholder) "
                    f"Would close short position id={position_id}"
                )

        return _DriftWrapper(obj)

    # Fallback  → return stub
    print(
        "[DerivativesEngine] Drift not available, running in stub mode –",
        obj,
    )
    return _StubDerivativesEngine(cluster)
