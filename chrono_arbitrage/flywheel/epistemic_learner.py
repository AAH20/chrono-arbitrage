"""
Epistemic Learner & Brier Score Calibration.

Evaluates forecast accuracy, measures probability calibration over time,
and logs resolved outcomes into persistent memory to compound future predictive edge.
"""

from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PredictionResolution:
    """A resolved prediction contract and the verified real-world outcome."""
    contract_id: str
    topic: str
    forecast_probability: float  # Our model's initial prediction (0.0 to 1.0)
    market_price_at_entry: float # The market's price at entry
    actual_outcome: bool         # True if YES happened, False if NO happened
    resolved_at: float = field(default_factory=time.time)

    @property
    def brier_score(self) -> float:
        """Quadratic loss (forecast - actual)^2. 0.0 is perfect, 0.25 is random."""
        actual_val = 1.0 if self.actual_outcome else 0.0
        return (self.forecast_probability - actual_val) ** 2


@dataclass
class EpistemicScorecard:
    """Cumulative performance metrics of the truth filter."""
    total_resolutions: int
    mean_brier_score: float      # Lower is better (< 0.15 is superforecaster tier)
    market_mean_brier_score: float # Baseline market Brier score
    epistemic_edge_ratio: float  # How much more accurate our model is than market price
    win_rate_percent: float


class EpistemicLearner:
    """
    Calibrates forecasting confidence and updates memory with empirical outcomes.
    """

    def __init__(self):
        self.resolutions: List[PredictionResolution] = []

    def record_resolution(
        self,
        contract_id: str,
        topic: str,
        forecast_p: float,
        market_price: float,
        actual_outcome: bool,
    ) -> PredictionResolution:
        """Record the final settlement of an event."""
        res = PredictionResolution(
            contract_id=contract_id,
            topic=topic,
            forecast_probability=forecast_p,
            market_price_at_entry=market_price,
            actual_outcome=actual_outcome,
        )
        self.resolutions.append(res)
        return res

    def compute_scorecard(self) -> EpistemicScorecard:
        """Compute Brier calibration metrics across all settled predictions."""
        if not self.resolutions:
            return EpistemicScorecard(0, 0.25, 0.25, 1.0, 0.0)

        total = len(self.resolutions)
        our_losses = [r.brier_score for r in self.resolutions]
        market_losses = [
            (r.market_price_at_entry - (1.0 if r.actual_outcome else 0.0)) ** 2
            for r in self.resolutions
        ]

        mean_our_bs = sum(our_losses) / total
        mean_market_bs = sum(market_losses) / total

        # Wins: where we traded in direction of outcome
        wins = 0
        for r in self.resolutions:
            predicted_yes = r.forecast_probability >= 0.5
            if predicted_yes == r.actual_outcome:
                wins += 1

        win_rate = (wins / total * 100.0) if total > 0 else 0.0
        edge_ratio = mean_market_bs / max(0.001, mean_our_bs)

        return EpistemicScorecard(
            total_resolutions=total,
            mean_brier_score=round(mean_our_bs, 4),
            market_mean_brier_score=round(mean_market_bs, 4),
            epistemic_edge_ratio=round(edge_ratio, 2),
            win_rate_percent=round(win_rate, 1),
        )
