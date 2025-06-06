# Oblivion – SynergyConductor v1.1 (skeleton)
import asyncio
from typing import Dict, List, Any
from agents import Agent, TradeSignal


class SynergyConductor:
    def __init__(self, agents: List[Agent], decay: float = 0.97):
        self.agents = [a for a in agents if a.meta.enabled]
        self.weights: Dict[str, float] = {a.meta.name: 1.0 for a in self.agents}
        self.decay = decay  # confidence‑decay per cycle

    async def vote(self, market_data: Dict[str, Any]) -> TradeSignal:
        # gather signals concurrently
        signals = await asyncio.gather(
            *[agent.logic(market_data) for agent in self.agents]
        )
        # weighted score aggregation
        score: Dict[str, float] = {}
        for sig in signals:
            w = self.weights.get(sig.meta.get("agent", ""), 1.0)
            score[sig.action] = score.get(sig.action, 0.0) + sig.confidence * w
        best = max(score, key=score.get)
        return TradeSignal(action=best, confidence=score[best] / len(self.agents))
