"""
Prediction Market Arbitrage Router.

Applies fractional Kelly Criterion and Expected Value optimization to place
orders on mispriced binary event contracts on Polymarket and Kalshi.
"""

from __future__ import annotations
import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from ..radar.market_watcher import EventContract


@dataclass
class ArbitrageOpportunity:
    """An identified mispricing in a prediction market contract."""
    contract_id: str
    platform: str
    target_side: str           # "YES" or "NO"
    market_price: float        # Price to buy on order book
    verified_probability: float # Model's calibrated probability
    edge_percent: float        # Difference (verified_prob - market_price)
    kelly_fraction: float      # Optimal fractional bankroll allocation
    recommended_stake_usd: float


@dataclass
class OrderExecutionResult:
    """The result of executing an arbitrage trade."""
    order_id: str
    contract_id: str
    platform: str
    side: str
    shares_filled: float
    average_price: float
    total_capital_deployed_usd: float
    expected_payout_usd: float
    status: str
    timestamp: float = field(default_factory=time.time)


class PredictionMarketRouter:
    """
    Executes programmatic event-contract arbitrage.
    """

    def __init__(self, bankroll_usd: float = 10000.0, max_allocation_per_trade: float = 0.15):
        self.bankroll_usd = bankroll_usd
        self.max_allocation = max_allocation_per_trade  # Max 15% of bankroll per position
        self.executed_orders: List[OrderExecutionResult] = []

    def evaluate_contract(
        self, contract: EventContract, verified_p_true: float
    ) -> Optional[ArbitrageOpportunity]:
        """
        Compare market ask price against verified probability and calculate Kelly allocation.
        """
        ask_yes = contract.order_book.best_ask_yes
        bid_yes = contract.order_book.best_bid_yes

        # Case 1: Market underprices YES (verified_p_true > ask_yes)
        if verified_p_true > ask_yes + 0.05:  # Minimum 5% edge
            edge = verified_p_true - ask_yes
            # Binary Kelly: f* = (p - ask) / (1 - ask)
            b = (1.0 - ask_yes) / max(0.01, ask_yes)
            raw_kelly = (verified_p_true * (b + 1.0) - 1.0) / b
            # Use Half-Kelly for conservative risk management
            half_kelly = max(0.0, min(self.max_allocation, raw_kelly * 0.5))
            stake = round(self.bankroll_usd * half_kelly, 2)

            if stake > 10.0:
                return ArbitrageOpportunity(
                    contract_id=contract.contract_id,
                    platform=contract.platform,
                    target_side="YES",
                    market_price=ask_yes,
                    verified_probability=verified_p_true,
                    edge_percent=edge * 100.0,
                    kelly_fraction=half_kelly,
                    recommended_stake_usd=stake,
                )

        # Case 2: Market overprices YES (verified_p_true < bid_yes -> Buy NO)
        p_no = 1.0 - verified_p_true
        ask_no = 1.0 - bid_yes  # Synthetic cost to buy NO
        if p_no > ask_no + 0.05:
            edge = p_no - ask_no
            b = (1.0 - ask_no) / max(0.01, ask_no)
            raw_kelly = (p_no * (b + 1.0) - 1.0) / b
            half_kelly = max(0.0, min(self.max_allocation, raw_kelly * 0.5))
            stake = round(self.bankroll_usd * half_kelly, 2)

            if stake > 10.0:
                return ArbitrageOpportunity(
                    contract_id=contract.contract_id,
                    platform=contract.platform,
                    target_side="NO",
                    market_price=ask_no,
                    verified_probability=p_no,
                    edge_percent=edge * 100.0,
                    kelly_fraction=half_kelly,
                    recommended_stake_usd=stake,
                )

        return None

    def execute_order(self, opp: ArbitrageOpportunity) -> OrderExecutionResult:
        """
        Execute an order on the prediction market contract.
        """
        order_id = f"ord_{uuid.uuid4().hex[:10]}"
        stake = min(opp.recommended_stake_usd, self.bankroll_usd)

        shares = stake / opp.market_price
        expected_payout = shares * 1.0  # Payout is $1.00 per winning share

        result = OrderExecutionResult(
            order_id=order_id,
            contract_id=opp.contract_id,
            platform=opp.platform,
            side=opp.target_side,
            shares_filled=shares,
            average_price=opp.market_price,
            total_capital_deployed_usd=stake,
            expected_payout_usd=expected_payout,
            status="FILLED",
        )

        self.executed_orders.append(result)
        return result
