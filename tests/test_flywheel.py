"""Unit tests for Capital Compounder and Epistemic Learner."""

import unittest
from chrono_arbitrage.flywheel import (
    CapitalCompounder,
    EpistemicLearner,
)


class TestFlywheel(unittest.TestCase):

    def test_capital_compounding_growth(self):
        compounder = CapitalCompounder(initial_capital_usd=10000.0, reinvestment_rate=1.0)

        # Trade 1: Deploy 1000, payout 2000 (+1000 profit)
        s1 = compounder.record_settled_trade(deployed_capital=1000.0, payout_received=2000.0)
        self.assertEqual(s1.current_equity_usd, 11000.0)
        self.assertEqual(s1.compounding_multiplier, 1.1)

        # Trade 2: Deploy 1500, payout 3000 (+1500 profit)
        s2 = compounder.record_settled_trade(deployed_capital=1500.0, payout_received=3000.0)
        self.assertEqual(s2.current_equity_usd, 12500.0)
        self.assertEqual(s2.compounding_multiplier, 1.25)
        self.assertEqual(s2.drawdown_percent, 0.0)

    def test_epistemic_learner_brier_score_calibration(self):
        learner = EpistemicLearner()

        # Two sharp, well-calibrated predictions:
        # Event 1: Forecast 0.90, actual YES (Loss = 0.01)
        learner.record_resolution("c1", "TopicA", forecast_p=0.90, market_price=0.50, actual_outcome=True)
        # Event 2: Forecast 0.10, actual NO (Loss = 0.01)
        learner.record_resolution("c2", "TopicB", forecast_p=0.10, market_price=0.45, actual_outcome=False)

        scorecard = learner.compute_scorecard()
        self.assertEqual(scorecard.total_resolutions, 2)
        self.assertAlmostEqual(scorecard.mean_brier_score, 0.01, places=3)
        self.assertGreater(scorecard.market_mean_brier_score, 0.20)
        self.assertGreater(scorecard.epistemic_edge_ratio, 10.0)
        self.assertEqual(scorecard.win_rate_percent, 100.0)


if __name__ == "__main__":
    unittest.main()
