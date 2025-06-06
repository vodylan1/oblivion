import asyncio
import pytest

from agents.base import Agent, AgentMeta, TradeSignal
from core.synergy_conductor.conductor import SynergyConductor


class HoldAgent(Agent):  # always HOLD, confidence 1.0
    meta = AgentMeta(
        name="HoldAgent",
        version="0.1",
        risk_profile="neutral",
        description="Baseline no‑op agent",
    )

    async def logic(self, market_data):
        return TradeSignal(action="HOLD", confidence=1.0, meta={"agent": self.meta.name})


@pytest.mark.asyncio
async def test_live_cycle():
    conductor = SynergyConductor([HoldAgent()], decay=1.0)
    md = {}  # empty mock market data
    sig = await conductor.vote(md)
    assert sig.action == "HOLD"
    assert 0.99 < sig.confidence <= 1.0
