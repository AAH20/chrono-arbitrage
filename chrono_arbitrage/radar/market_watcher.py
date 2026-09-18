"""
Prediction Market Surveillance Watcher.

Surveys prediction markets (Polymarket, Kalshi) for binary event contracts,
order-book liquidity depth, and implied probability pricing.
"""

from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class OrderBookSnapshot:
    """Current top-of-book and liquidity depth for a binary contract."""
    contract_id: str
    best_bid_yes: float     # Highest price buyers will pay for YES (0.00 to 1.00)
    best_ask_yes: float     # Lowest price sellers will accept for YES (0.00 to 1.00)
    bid_depth_usd: float
    ask_depth_usd: float
    timestamp: float = field(default_factory=time.time)

    @property
    def mid_market_price(self) -> float:
        return (self.best_bid_yes + self.best_ask_yes) / 2.0

    @property
    def spread(self) -> float:
        return round(max(0.0, self.best_ask_yes - self.best_bid_yes), 4)


@dataclass
class EventContract:
    """An event contract listed on Polymarket or Kalshi."""
    contract_id: str
    platform: str          # "POLYMARKET" or "KALSHI"
    title: str
    topic_tag: str
    order_book: OrderBookSnapshot
    volume_usd: float
    resolution_rules: str
    active: bool = True

    @property
    def implied_probability(self) -> float:
        """The probability priced in by the current market ask price."""
        return self.order_book.best_ask_yes


class MarketWatcher:
    """
    Maintains live state of tradable event contracts.
    """

    def __init__(self):
        self.contracts: Dict[str, EventContract] = {}

    def register_contract(
        self,
        contract_id: str,
        platform: str,
        title: str,
        topic_tag: str,
        best_bid: float,
        best_ask: float,
        bid_depth: float = 10000.0,
        ask_depth: float = 10000.0,
        resolution_rules: str = "Resolves according to primary source confirmation",
    ) -> EventContract:
        """Register or update an event contract."""
        ob = OrderBookSnapshot(
            contract_id=contract_id,
            best_bid_yes=best_bid,
            best_ask_yes=best_ask,
            bid_depth_usd=bid_depth,
            ask_depth_usd=ask_depth,
        )
        contract = EventContract(
            contract_id=contract_id,
            platform=platform,
            title=title,
            topic_tag=topic_tag,
            order_book=ob,
            volume_usd=50000.0,
            resolution_rules=resolution_rules,
        )
        self.contracts[contract_id] = contract
        return contract

    def get_contracts_for_topic(self, topic: str) -> List[EventContract]:
        """Find active contracts relevant to an attention topic."""
        return [c for c in self.contracts.values() if c.topic_tag.lower() == topic.lower() and c.active]
