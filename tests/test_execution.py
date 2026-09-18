"""Unit tests for Prediction Market Router and B2B Demand Router."""

import unittest
from chrono_arbitrage.radar import MarketWatcher
from chrono_arbitrage.execution import (
    PredictionMarketRouter,
    B2BDemandRouter,
)


class TestExecution(unittest.TestCase):

    def test_kelly_arbitrage_sizing(self):
        watcher = MarketWatcher()
        contract = watcher.register_contract(
            contract_id="c_test",
            platform="POLYMARKET",
            title="Will FDA approve drug Y?",
            topic_tag="FDA_DRUG_Y",
            best_bid=0.30,
            best_ask=0.35,
        )

        router = PredictionMarketRouter(bankroll_usd=10000.0, max_allocation_per_trade=0.15)

        # Model verified probability is 0.80 (huge edge over 0.35 ask)
        opp = router.evaluate_contract(contract, verified_p_true=0.80)

        self.assertIsNotNone(opp)
        self.assertEqual(opp.target_side, "YES")
        self.assertAlmostEqual(opp.edge_percent, 45.0, places=1)
        self.assertLessEqual(opp.recommended_stake_usd, 1500.0)  # Capped at 15%

        order = router.execute_order(opp)
        self.assertEqual(order.status, "FILLED")
        self.assertGreater(order.expected_payout_usd, order.total_capital_deployed_usd)

    def test_b2b_demand_router(self):
        router = B2BDemandRouter()
        lead = router.route_surge_to_demand("CYBER_EXPLOIT", "Zero-day CVE surge")

        self.assertEqual(lead.estimated_contract_value_usd, 7500.0)
        self.assertIn("a2zsoc.com", lead.service_cta_url)


if __name__ == "__main__":
    unittest.main()
