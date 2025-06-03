"""
derivatives_engine.py
───────────────────────────────────────────────────────────────────────────────
Phase-7 engine with three automatic code paths:

  • driftpy  ≥ 0.9.x  → `DriftClient(cluster=…)`
  • driftpy  ≤ 0.8.x  → `DriftClient(connection, wallet, …)`
  • no driftpy        → lightweight stub (prints only)

Public factory
    derivatives_engine_init()  → engine  (real | stub)
"""

from __future__ import annotations

from typing import Any, Optional

# --------------------------------------------------------------------------- #
#  Library detection
# --------------------------------------------------------------------------- #
try:
    from driftpy.drift_client import DriftClient  # type: ignore
    DRIFT_AVAILABLE = True
    DRIFT_IMPORT_ERR: Optional[Exception] = None
except Exception as _err:                         # pragma: no cover
    DRIFT_AVAILABLE = False
    DriftClient = None                            # type: ignore
    DRIFT_IMPORT_ERR = _err

# Local helper to build connection + wallet for driftpy 0.8.x
if DRIFT_AVAILABLE:
    try:
        from solders.keypair import Keypair
        from solana.rpc.api import Client as SolanaClient
        from security.secure_wallet import load_keypair
    except Exception as _e:                       # pragma: no cover
        # These imports are only needed for the 0.8-style fallback
        Keypair = None                            # type: ignore
        SolanaClient = None                      # type: ignore
        _SEC_HELPER_ERR = _e
else:
    Keypair = None                                # type: ignore
    SolanaClient = None                           # type: ignore


# --------------------------------------------------------------------------- #
#  Common interface
# --------------------------------------------------------------------------- #
class DerivativesEngineBase:
    cluster: str

    def __init__(self, cluster: str = "devnet") -> None:
        self.cluster = cluster

    # ---- actions ---------------------------------------------------------- #
    def open_short(self, symbol: str, size: float) -> None:
        raise NotImplementedError

    def close_short(self, symbol: str) -> None:
        raise NotImplementedError

    def health(self) -> str:              # “real” | “stub”
        raise NotImplementedError


# =========================================================================== #
#  Real engine
# =========================================================================== #
if DRIFT_AVAILABLE:

    class _RealDerivativesEngine(DerivativesEngineBase):
        """Works with either driftpy 0.9-series or 0.8-series."""

        def __init__(self, cluster: str = "devnet") -> None:         # noqa: D401
            super().__init__(cluster)
            self.client = self._boot_client(cluster)
            print(f"[DerivativesEngine] Online – cluster: {self.cluster}")

        # ------------------------------------------------------------------ #
        #  0.9-style ➜ 0.8-style ➜ raise
        # ------------------------------------------------------------------ #
        @staticmethod
        def _boot_client(cluster: str) -> Any:
            # ① try ≥ 0.9.x signature
            try:
                return DriftClient(cluster=cluster)                   # type: ignore[arg-type]
            except TypeError:
                pass

            # ② fallback to ≤ 0.8.x signature
            try:
                # Build a quick connection + wallet
                rpc_url = (
                    "https://api.devnet.solana.com"
                    if cluster == "devnet"
                    else "https://api.mainnet-beta.solana.com"
                )
                connection = SolanaClient(rpc_url)                   # type: ignore[operator]
                kp = load_keypair()
                wallet = kp                                          # Keypair acts as wallet
                return DriftClient(connection, wallet)               # type: ignore[arg-type]
            except Exception as inner:
                # Give up – caller will drop to stub
                raise RuntimeError(inner) from inner

        # ---- demo methods (real trades later) --------------------------- #
        def open_short(self, symbol: str, size: float) -> None:
            print(f"[DerivativesEngine] (REAL) open SHORT {size} {symbol}")

        def close_short(self, symbol: str) -> None:
            print(f"[DerivativesEngine] (REAL) close SHORT {symbol}")

        def health(self) -> str:                                      # noqa: D401
            return "real"

# =========================================================================== #
#  Stub fallback
# =========================================================================== #
class _StubDerivativesEngine(DerivativesEngineBase):
    def __init__(self, cluster: str = "devnet") -> None:
        super().__init__(cluster)
        reason = f"{DRIFT_IMPORT_ERR}" if DRIFT_IMPORT_ERR else "driftpy unavailable"
        print("[DerivativesEngine] Stub mode –", reason)
        print(f"[DerivativesEngine] Stub Online – cluster: {self.cluster}")

    def open_short(self, symbol: str, size: float) -> None:
        print(f"[DerivativesEngine] (STUB) open SHORT {size} {symbol}")

    def close_short(self, symbol: str) -> None:
        print(f"[DerivativesEngine] (STUB) close SHORT {symbol}")

    def health(self) -> str:                                          # noqa: D401
        return "stub"


# --------------------------------------------------------------------------- #
#  Factory
# --------------------------------------------------------------------------- #
def derivatives_engine_init(cluster: str = "devnet") -> DerivativesEngineBase:
    """Return the appropriate engine instance (real or stub)."""
    if DRIFT_AVAILABLE:
        try:
            return _RealDerivativesEngine(cluster)
        except Exception as e:
            print("[DerivativesEngine] Fallback to stub –", e)
    return _StubDerivativesEngine(cluster)
