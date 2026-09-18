"""Unit tests for Evidence Scorer and Bot Detector."""

import unittest
from chrono_arbitrage.truth_filter import (
    EvidenceProfile,
    EvidenceScorer,
    BotDetector,
)


class TestTruthFilter(unittest.TestCase):

    def test_evidence_scorer_primary_docket_pass(self):
        scorer = EvidenceScorer(min_confidence_to_trade=0.75)

        verified_profile = EvidenceProfile(
            has_primary_source_docket=True,
            has_cryptographic_attestation=True,
            independent_outlets_count=3,
            is_circular_citation=False,
            source_reputation_score=0.9,
        )
        score = scorer.evaluate_claim(verified_profile)

        self.assertTrue(score.passes_trade_gate)
        self.assertGreaterEqual(score.calibrated_probability, 0.85)
        self.assertLess(score.disinformation_risk, 0.2)

    def test_evidence_scorer_rejects_circular_rumor(self):
        scorer = EvidenceScorer(min_confidence_to_trade=0.75)

        rumor_profile = EvidenceProfile(
            has_primary_source_docket=False,
            has_cryptographic_attestation=False,
            independent_outlets_count=1,
            is_circular_citation=True,  # Disinformation hallmark
            source_reputation_score=0.2,
        )
        score = scorer.evaluate_claim(rumor_profile)

        self.assertFalse(score.passes_trade_gate)
        self.assertGreater(score.disinformation_risk, 0.7)

    def test_bot_detector_copypasta_amplification(self):
        detector = BotDetector(max_duplicate_ratio=0.4)

        # Swarm of identical tweets
        identical_msgs = [
            "BREAKING: Company X files for bankruptcy!!",
            "BREAKING: Company X files for bankruptcy!!",
            "BREAKING: Company X files for bankruptcy!!",
            "BREAKING: Company X files for bankruptcy!!",
            "Legitimate organic comment here.",
        ]
        report = detector.analyze_messages("COMPANY_X", identical_msgs)

        self.assertTrue(report.is_manipulated)
        self.assertGreaterEqual(report.duplicate_text_ratio, 0.8)


if __name__ == "__main__":
    unittest.main()
