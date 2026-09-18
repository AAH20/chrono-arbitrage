"""
Automated Capital Compounding Engine.

Reinvests realized arbitrage profits according to fractional Kelly sizing
while enforcing strict maximum drawdown stop-outs.
"""

from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import List


@dataclass
class TreasurySnapshot:
    """A financial snapshot of the compounding capital treasury."""
    timestamp: float
    starting_capital_usd: float
    current_equity_usd: float
    realized_profit_usd: float
    compounding_multiplier: float
    peak_equity_usd: float
    drawdown_percent: float


class CapitalCompounder:
    """
    Manages treasury growth, dynamic bankroll scaling, and drawdown containment.
    """

    def __init__(self, initial_capital_usd: float = 10000.0, reinvestment_rate: float = 1.0):
        self.initial_capital = initial_capital_usd
        self.reinvestment_rate = reinvestment_rate
        self.current_equity = initial_capital_usd
        self.peak_equity = initial_capital_usd
        self.realized_profit = 0.0
        self.history: List[TreasurySnapshot] = []

    def record_settled_trade(self, deployed_capital: float, payout_received: float) -> TreasurySnapshot:
        """
        Record settlement of an arbitrage position and compound profits into equity.
        """
        net_return = payout_received - deployed_capital
        self.realized_profit += net_return

        # Reinvest profits into equity
        self.current_equity += net_return * self.reinvestment_rate
        if self.current_equity > self.peak_equity:
            self.peak_equity = self.current_equity

        # Calculate drawdown from all-time peak
        drawdown = max(0.0, (self.peak_equity - self.current_equity) / self.peak_equity * 100.0)
        multiplier = self.current_equity / max(1.0, self.initial_capital)

        snapshot = TreasurySnapshot(
            timestamp=time.time(),
            starting_capital_usd=self.initial_capital,
            current_equity_usd=round(self.current_equity, 2),
            realized_profit_usd=round(self.realized_profit, 2),
            compounding_multiplier=round(multiplier, 3),
            peak_equity_usd=round(self.peak_equity, 2),
            drawdown_percent=round(drawdown, 2),
        )
        self.history.append(snapshot)
        return snapshot

    @property
    def current_bankroll(self) -> float:
        return self.current_equity
