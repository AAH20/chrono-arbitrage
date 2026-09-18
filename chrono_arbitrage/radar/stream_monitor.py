"""
Stream Attention Monitor.

Monitors real-time information feeds (news, social, regulatory dockets),
calculating signal velocity gradients and detecting narrative attention surges.
"""

from __future__ import annotations
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class AttentionSignal:
    """An individual signal or mention detected across monitored channels."""
    source: str          # e.g., "SEC_EDGAR", "X_STREAM", "NEWS_WIRE", "PACER"
    topic: str           # Target entity, company, or policy ticker
    text: str
    reach: int = 1000
    timestamp: float = field(default_factory=time.time)


@dataclass
class StreamSurgeReport:
    """Detection report for a narrative velocity surge."""
    topic: str
    is_surging: bool
    current_velocity: float    # Signals per second
    baseline_velocity: float   # Historical baseline signals per second
    acceleration_gradient: float  # (v_curr - v_base) / v_base
    total_signals_observed: int
    sentiment_divergence: float = 0.0


class StreamMonitor:
    """
    Sliding-window monitor computing signal velocity gradients.
    """

    def __init__(
        self,
        window_seconds: float = 60.0,
        surge_acceleration_threshold: float = 2.0,  # 200% acceleration
    ):
        self.window_seconds = window_seconds
        self.surge_threshold = surge_acceleration_threshold
        self._signal_history: Dict[str, deque[AttentionSignal]] = {}
        self._historical_baselines: Dict[str, float] = {}

    def ingest_signal(self, signal: AttentionSignal) -> None:
        """Ingest a new attention signal into the sliding window."""
        if signal.topic not in self._signal_history:
            self._signal_history[signal.topic] = deque()

        self._signal_history[signal.topic].append(signal)
        self._prune_expired(signal.topic, signal.timestamp)

    def _prune_expired(self, topic: str, current_time: float) -> None:
        """Discard signals older than the active evaluation window."""
        q = self._signal_history.get(topic)
        if not q:
            return
        cutoff = current_time - self.window_seconds
        while q and q[0].timestamp < cutoff:
            q.popleft()

    def evaluate_topic_surge(self, topic: str, as_of_time: Optional[float] = None) -> StreamSurgeReport:
        """
        Evaluate if a topic is experiencing an attention surge relative to baseline.
        """
        now = as_of_time or time.time()
        self._prune_expired(topic, now)

        q = self._signal_history.get(topic, deque())
        count = len(q)

        current_velocity = count / max(1.0, self.window_seconds)
        baseline = self._historical_baselines.get(topic, 0.05)  # Nominal baseline: 0.05 signals/sec

        gradient = (current_velocity - baseline) / max(0.01, baseline)
        is_surging = (gradient >= self.surge_threshold) and (count >= 3)

        # Update historical baseline exponentially
        self._historical_baselines[topic] = 0.9 * baseline + 0.1 * current_velocity

        return StreamSurgeReport(
            topic=topic,
            is_surging=is_surging,
            current_velocity=current_velocity,
            baseline_velocity=baseline,
            acceleration_gradient=gradient,
            total_signals_observed=count,
        )
