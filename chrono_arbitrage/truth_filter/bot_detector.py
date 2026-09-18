"""
Coordinated Bot Syndicate & Pump-and-Dump Detector.

Scans social message distributions for artificial syndication, copy-paste
amplification, and coordinated market spoofing attacks.
"""

from __future__ import annotations
import hashlib
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class BotSyndicateReport:
    """Analysis of message syndication and inauthentic behavior."""
    topic: str
    is_manipulated: bool
    duplicate_text_ratio: float
    bot_probability: float
    verdict: str


class BotDetector:
    """
    Detects inauthentic volume amplification.
    """

    def __init__(self, max_duplicate_ratio: float = 0.40):
        self.max_duplicate_ratio = max_duplicate_ratio

    def analyze_messages(self, topic: str, messages: List[str]) -> BotSyndicateReport:
        """
        Scan a batch of messages discussing a topic for copy-paste bot signatures.
        """
        if not messages:
            return BotSyndicateReport(
                topic=topic,
                is_manipulated=False,
                duplicate_text_ratio=0.0,
                bot_probability=0.0,
                verdict="NO_DATA",
            )

        # Hash normalized messages to detect duplicate copypasta
        hashes = [hashlib.md5(m.strip().lower().encode()).hexdigest() for m in messages]
        counts = Counter(hashes)
        total = len(messages)

        # Count messages that appear more than once
        duplicates = sum(count for h, count in counts.items() if count > 1)
        duplicate_ratio = duplicates / total

        # High duplicate ratio indicates bot swarm copypasta
        bot_prob = min(1.0, duplicate_ratio * 1.8)
        is_manipulated = (duplicate_ratio > self.max_duplicate_ratio) and (total >= 5)

        verdict = (
            "COORDINATED_BOT_MANIPULATION_DETECTED"
            if is_manipulated
            else "ORGANIC_INFORMATION_FLOW"
        )

        return BotSyndicateReport(
            topic=topic,
            is_manipulated=is_manipulated,
            duplicate_text_ratio=duplicate_ratio,
            bot_probability=bot_prob,
            verdict=verdict,
        )
