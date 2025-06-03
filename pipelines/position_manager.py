"""
position_manager.py – Phase 7-4
(unchanged PM class code …)
"""

# existing imports + PM class stay here
# …

# ─── thin wrapper expected by main.py ─────────────────────────────────────
def position_manager_init():
    """
    Back-compat helper so legacy code can still do
        from pipelines.position_manager import position_manager_init
    """
    print("[PositionManager] Online – Phase 7-4")
    return PM
