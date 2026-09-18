"""
Evidence-Based Narrative Truth Scorer.

Adapts the Gate/Prove rubric from fde-bounty-snr to evaluate claim veracity,
primary-source attribution, and evidence completeness before capital is risked.
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class EvidenceProfile:
    """The evidence backing a breaking narrative claim."""
    has_primary_source_docket: bool = False   # Link to SEC, court docket, government gazette
    has_cryptographic_attestation: bool = False  # Signed cryptographic receipt
    independent_outlets_count: int = 1
    is_circular_citation: bool = False        # Loop of news aggregators quoting each other
    source_reputation_score: float = 0.5      # 0.0 (anonymous troll) to 1.0 (regulatory wire)


@dataclass
class VeracityScore:
    """Mathematical assessment of claim truth probability."""
    calibrated_probability: float  # P(True) between 0.01 and 0.99
    confidence: float              # Epistemic certainty in evaluation
    disinformation_risk: float     # Estimated probability of intentional manipulation
    passes_trade_gate: bool        # Whether the signal is safe to commit capital
    rationale: str


class EvidenceScorer:
    """
    Computes rigorous Bayesian belief updates based on physical and documentary evidence.
    """

    def __init__(self, min_confidence_to_trade: float = 0.80):
        self.min_confidence = min_confidence_to_trade

    def evaluate_claim(self, profile: EvidenceProfile) -> VeracityScore:
        """
        Evaluate claim veracity using the Gate/Prove evidence standard.
        """
        # Base prior
        log_odds = 0.0  # prior 50%

        # 1. Primary source docket (huge positive weight)
        if profile.has_primary_source_docket:
            log_odds += 2.8  # ~16x likelihood ratio

        # 2. Cryptographic attestation
        if profile.has_cryptographic_attestation:
            log_odds += 2.2

        # 3. Source reputation
        log_odds += (profile.source_reputation_score - 0.5) * 2.0

        # 4. Independent corroboration (diminishing returns)
        corrob_boost = math.log(max(1, profile.independent_outlets_count)) * 0.5
        log_odds += corrob_boost

        # 5. Penalties for circular citations
        disinfo_risk = 0.1
        if profile.is_circular_citation:
            log_odds -= 2.5
            disinfo_risk = 0.85

        # Convert log odds back to probability
        p_true = 1.0 / (1.0 + math.exp(-log_odds))
        p_true = max(0.01, min(0.99, p_true))

        # Calculate confidence
        evidence_density = (
            (1.0 if profile.has_primary_source_docket else 0.0) * 0.4
            + (1.0 if profile.has_cryptographic_attestation else 0.0) * 0.3
            + min(1.0, profile.independent_outlets_count / 3.0) * 0.3
        )

        confidence = evidence_density * (1.0 - disinfo_risk)
        passes_gate = (confidence >= self.min_confidence) and (p_true >= 0.85 or p_true <= 0.15)

        if passes_gate:
            rationale = f"GATE CLEARED: Verified with primary evidence (P={p_true:.2f}, Conf={confidence:.2f})"
        else:
            rationale = f"GATE LOCKED: Insufficient evidence or high disinformation risk (P={p_true:.2f}, Conf={confidence:.2f})"

        return VeracityScore(
            calibrated_probability=p_true,
            confidence=confidence,
            disinformation_risk=disinfo_risk,
            passes_trade_gate=passes_gate,
            rationale=rationale,
        )
