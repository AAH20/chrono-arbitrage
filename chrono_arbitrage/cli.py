"""
Unified Command-Line Interface for Project ChronoArbitrage.

Demonstrates real-time attention radar scanning, GRC truth filtering,
Kelly-sized prediction market execution, and compounding flywheel metrics.
"""

from __future__ import annotations
import argparse
import sys
import time

from chrono_arbitrage.radar import (
    AttentionSignal,
    StreamMonitor,
    MarketWatcher,
)
from chrono_arbitrage.truth_filter import (
    EvidenceProfile,
    EvidenceScorer,
    BotDetector,
)
from chrono_arbitrage.execution import (
    PredictionMarketRouter,
    B2BDemandRouter,
)
from chrono_arbitrage.flywheel import (
    CapitalCompounder,
    EpistemicLearner,
)


def cmd_scan(args):
    print("=== [Subsystem 1 & 2] Attention Radar & GRC Truth Filter ===")
    monitor = StreamMonitor(window_seconds=10.0, surge_acceleration_threshold=1.5)

    topic = "SEC_AI_SAFETY_STANDARD"
    print(f"[1] Ingesting stream signals for '{topic}'...")

    t0 = time.time()
    for i in range(5):
        monitor.ingest_signal(
            AttentionSignal(
                source="SEC_EDGAR_WIRE",
                topic=topic,
                text="SEC announces mandatory compliance framework for autonomous agents",
                timestamp=t0 + i * 0.5,
            )
        )

    surge = monitor.evaluate_topic_surge(topic, as_of_time=t0 + 3.0)
    print(f"    Signals Observed: {surge.total_signals_observed}, Velocity: {surge.current_velocity:.2f} sig/s")
    print(f"    Surge Detected: {surge.is_surging} (Acceleration Gradient: +{surge.acceleration_gradient:.1f}x)")

    # Evaluate Evidence Truth
    print("[2] Evaluating Claim Veracity through Gate/Prove Standard...")
    scorer = EvidenceScorer()
    profile = EvidenceProfile(
        has_primary_source_docket=True,
        has_cryptographic_attestation=True,
        independent_outlets_count=4,
        is_circular_citation=False,
        source_reputation_score=0.95,
    )
    veracity = scorer.evaluate_claim(profile)
    print(f"    Calibrated Probability: {veracity.calibrated_probability:.2f} ({veracity.calibrated_probability * 100:.0f}%)")
    print(f"    Epistemic Confidence: {veracity.confidence:.2f}")
    print(f"    Disinformation Risk: {veracity.disinformation_risk:.2f}")
    print(f"    Verdict: {veracity.rationale}")
    return veracity.calibrated_probability


def cmd_trade(args, verified_p=0.94):
    print("=== [Subsystem 3] Liquidity & Prediction Market Arbitrage ===")
    market = MarketWatcher()
    contract = market.register_contract(
        contract_id="poly_sec_ai_01",
        platform="POLYMARKET",
        title="Will SEC issue AI agent safety rule before Q4?",
        topic_tag="SEC_AI_SAFETY_STANDARD",
        best_bid=0.38,
        best_ask=0.42,  # Market only pricing in 42% probability!
    )
    print(f"[1] Found Active Contract '{contract.contract_id}':")
    print(f"    Title: {contract.title}")
    print(f"    Market Ask Price: ${contract.order_book.best_ask_yes:.2f} (Implied Prob: {contract.implied_probability * 100:.0f}%)")
    print(f"    Our Verified Probability: {verified_p * 100:.0f}%")

    router = PredictionMarketRouter(bankroll_usd=10000.0)
    opp = router.evaluate_contract(contract, verified_p_true=verified_p)

    if opp:
        print(f"[2] Arbitrage Opportunity Identified:")
        print(f"    Edge: +{opp.edge_percent:.1f}%")
        print(f"    Kelly Sizing: {opp.kelly_fraction * 100:.1f}% of treasury")
        print(f"    Recommended Stake: ${opp.recommended_stake_usd:.2f}")

        order = router.execute_order(opp)
        print(f"[3] Order Executed on {order.platform}:")
        print(f"    Order ID: {order.order_id}")
        print(f"    Bought {order.shares_filled:.1f} shares of YES at ${order.average_price:.2f}")
        print(f"    Deployed Capital: ${order.total_capital_deployed_usd:.2f}")
        print(f"    Expected Payout on Settlement: ${order.expected_payout_usd:.2f}")
        return order
    else:
        print("No edge found.")
        return None


def cmd_flywheel(args, order=None):
    print("=== [Subsystem 4] Self-Compounding Capital & Epistemic Flywheel ===")
    compounder = CapitalCompounder(initial_capital_usd=10000.0)
    learner = EpistemicLearner()

    # Simulate trade settlement: contract resolves YES (wins $1.00 payout)
    deployed = order.total_capital_deployed_usd if order else 1500.0
    payout = order.expected_payout_usd if order else 3571.43

    print("[1] Settling Arbitrage Position...")
    snap = compounder.record_settled_trade(deployed_capital=deployed, payout_received=payout)
    print(f"    Realized Net Profit: +${snap.realized_profit_usd:.2f}")
    print(f"    Compounded Treasury: ${snap.current_equity_usd:.2f} (Multiplier: {snap.compounding_multiplier:.3f}x)")
    print(f"    Peak Drawdown: {snap.drawdown_percent:.1f}%")

    print("[2] Calibrating Epistemic Forecast Edge (Brier Loss)...")
    learner.record_resolution(
        contract_id="poly_sec_ai_01",
        topic="SEC_AI_SAFETY_STANDARD",
        forecast_p=0.94,
        market_price=0.42,
        actual_outcome=True,
    )
    scorecard = learner.compute_scorecard()
    print(f"    Our Model Brier Score: {scorecard.mean_brier_score:.4f} (Superforecaster tier: < 0.15)")
    print(f"    Market Baseline Brier Score: {scorecard.market_mean_brier_score:.4f}")
    print(f"    Epistemic Edge Ratio: {scorecard.epistemic_edge_ratio:.1f}x superior accuracy")
    print(f"    Historical Win Rate: {scorecard.win_rate_percent:.1f}%")

    print("[3] High-Intent B2B Demand Capture:")
    b2b = B2BDemandRouter()
    lead = b2b.route_surge_to_demand("REGULATORY_FINE", "SEC_AI_SAFETY_SURGE")
    print(f"    Captured Intent: {lead.target_service}")
    print(f"    Target CTA: {lead.service_cta_url}")
    print(f"    Estimated Contract Value: ${lead.estimated_contract_value_usd:.2f}")


def main():
    parser = argparse.ArgumentParser(description="Project ChronoArbitrage CLI")
    subparsers = parser.add_subparsers(dest="command", help="Subcommands")

    subparsers.add_parser("scan", help="Scan attention radar and evaluate truth")
    subparsers.add_parser("trade", help="Execute prediction market arbitrage")
    subparsers.add_parser("flywheel", help="Show capital compounding and epistemic calibration")
    subparsers.add_parser("all", help="Run end-to-end arbitrage cycle")

    args = parser.parse_args()

    if args.command == "scan":
        cmd_scan(args)
    elif args.command == "trade":
        cmd_trade(args)
    elif args.command == "flywheel":
        cmd_flywheel(args)
    elif args.command == "all" or args.command is None:
        p_true = cmd_scan(args)
        print()
        order = cmd_trade(args, verified_p=p_true)
        print()
        cmd_flywheel(args, order=order)


if __name__ == "__main__":
    main()
