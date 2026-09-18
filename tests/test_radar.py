"""Unit tests for Stream Monitor and Market Watcher."""

import unittest
from chrono_arbitrage.radar import (
    AttentionSignal,
    StreamMonitor,
    MarketWatcher,
)


class TestRadar(unittest.TestCase):

    def test_stream_monitor_velocity_surge(self):
        monitor = StreamMonitor(window_seconds=10.0, surge_acceleration_threshold=1.0)
        topic = "TESLA_CYBERCAB"

        # Ingest 5 rapid signals
        for i in range(5):
            monitor.ingest_signal(
                AttentionSignal(
                    source="TWITTER",
                    topic=topic,
                    text="FSD approval announced",
                    timestamp=100.0 + i * 0.2,
                )
            )

        report = monitor.evaluate_topic_surge(topic, as_of_time=102.0)
        self.assertTrue(report.is_surging)
        self.assertEqual(report.total_signals_observed, 5)
        self.assertGreater(report.acceleration_gradient, 1.0)

    def test_market_watcher_registration_and_implied_prob(self):
        watcher = MarketWatcher()
        contract = watcher.register_contract(
            contract_id="c_01",
            platform="POLYMARKET",
            title="Fed rate cut in September?",
            topic_tag="FED_RATES",
            best_bid=0.68,
            best_ask=0.72,
        )

        self.assertEqual(contract.implied_probability, 0.72)
        self.assertAlmostEqual(contract.order_book.spread, 0.04, places=3)

        matching = watcher.get_contracts_for_topic("FED_RATES")
        self.assertEqual(len(matching), 1)
        self.assertEqual(matching[0].contract_id, "c_01")


if __name__ == "__main__":
    unittest.main()
