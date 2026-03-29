"""Deterministic threshold engines for computing metric states in Python only."""

from typing import Dict, Tuple, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class MetricState:
    """State of a single metric."""
    metric_name: str
    value: float
    baseline: float
    pct_change: float
    state: str  # normal, watchful, elevated
    reasoning: str


class BehavioralSignalThresholdEngine:
    """Compute behavioral metric states (call count, conversation, screen time, phone interactions).
    
    ALL THRESHOLDS IN PYTHON ONLY - NO LLM COMPUTATION.
    """
    
    def __init__(self):
        self.metric_states: Dict[str, MetricState] = {}
    
    def analyze_call_count(self, value: float, baseline: float, consecutive_days: int = 7) -> MetricState:
        """Analyze call count metric.
        
        Rules:
            - Normal: < 25% drop
            - Watchful: 25-40% drop for ≥ 7 days
            - Elevated: ≥ 50% drop for ≥ 14 days
        
        Args:
            value: Current average call count
            baseline: Baseline call count
            consecutive_days: Number of consecutive days in current state
        
        Returns:
            MetricState object
        """
        if baseline == 0:
            return MetricState("call_count", value, baseline, 0, "normal", "No baseline data")
        
        pct_change = ((value - baseline) / baseline) * 100
        
        if pct_change >= -25:
            state = "normal"
            reasoning = f"Call count drop {pct_change:.1f}% is within normal range (<25%)"
        elif pct_change >= -40 and consecutive_days >= 7:
            state = "watchful"
            reasoning = f"Call count drop {pct_change:.1f}% is watchful (25-40%) for {consecutive_days} days"
        elif pct_change <= -50 and consecutive_days >= 14:
            state = "elevated"
            reasoning = f"Call count drop {pct_change:.1f}% is elevated (≥50%) for {consecutive_days} days"
        elif pct_change < -25:
            state = "watchful"
            reasoning = f"Call count drop {pct_change:.1f}% exceeds normal threshold but not yet elevated"
        else:
            state = "normal"
            reasoning = f"Call count change {pct_change:.1f}% is normal"
        
        return MetricState("call_count", value, baseline, pct_change, state, reasoning)
    
    def analyze_conversation_duration(self, value: float, baseline: float, consecutive_days: int = 7) -> MetricState:
        """Analyze conversation duration metric.
        
        Rules:
            - Normal: < 30% drop
            - Watchful: 30-45% drop for ≥ 7 days
            - Elevated: ≥ 50% drop for ≥ 14 days
        
        Args:
            value: Current average conversation duration
            baseline: Baseline conversation duration
            consecutive_days: Number of consecutive days in current state
        
        Returns:
            MetricState object
        """
        if baseline == 0:
            return MetricState("conversation_duration", value, baseline, 0, "normal", "No baseline data")
        
        pct_change = ((value - baseline) / baseline) * 100
        
        if pct_change >= -30:
            state = "normal"
            reasoning = f"Conversation duration drop {pct_change:.1f}% is within normal range (<30%)"
        elif pct_change >= -45 and consecutive_days >= 7:
            state = "watchful"
            reasoning = f"Conversation duration drop {pct_change:.1f}% is watchful (30-45%) for {consecutive_days} days"
        elif pct_change <= -50 and consecutive_days >= 14:
            state = "elevated"
            reasoning = f"Conversation duration drop {pct_change:.1f}% is elevated (≥50%) for {consecutive_days} days"
        elif pct_change < -30:
            state = "watchful"
            reasoning = f"Conversation duration drop {pct_change:.1f}% exceeds normal threshold"
        else:
            state = "normal"
            reasoning = f"Conversation duration change {pct_change:.1f}% is normal"
        
        return MetricState("conversation_duration", value, baseline, pct_change, state, reasoning)
    
    def analyze_phone_interactions(self, value: float, baseline: float, consecutive_days: int = 7) -> MetricState:
        """Analyze phone interaction events (proxy: screen time variance).
        
        Rules:
            - Normal: ± 20%
            - Watchful: ≥ 30% reduction for ≥ 7 days
            - Elevated: ≥ 50% reduction for ≥ 14 days
        
        Args:
            value: Current average interaction events
            baseline: Baseline interaction events
            consecutive_days: Number of consecutive days in current state
        
        Returns:
            MetricState object
        """
        if baseline == 0:
            return MetricState("phone_interactions", value, baseline, 0, "normal", "No baseline data")
        
        pct_change = ((value - baseline) / baseline) * 100
        
        if -20 <= pct_change <= 20:
            state = "normal"
            reasoning = f"Phone interactions within normal range (±20%): {pct_change:.1f}%"
        elif pct_change <= -30 and consecutive_days >= 7:
            if pct_change <= -50 and consecutive_days >= 14:
                state = "elevated"
                reasoning = f"Phone interactions drop {pct_change:.1f}% is elevated (≥50%) for {consecutive_days} days"
            else:
                state = "watchful"
                reasoning = f"Phone interactions drop {pct_change:.1f}% is watchful (≥30%) for {consecutive_days} days"
        else:
            state = "normal"
            reasoning = f"Phone interactions change {pct_change:.1f}% is acceptable"
        
        return MetricState("phone_interactions", value, baseline, pct_change, state, reasoning)
    
    def analyze_screen_time(self, value: float, baseline: float, consecutive_days: int = 7) -> MetricState:
        """Analyze screen time metric.
        
        Rules:
            - Normal: ± 20% of baseline
            - Watchful: ≥ 30% increase for ≥ 7 consecutive days
            - Elevated: ≥ 50% increase for ≥ 14 consecutive days
        
        Args:
            value: Current average screen time
            baseline: Baseline screen time
            consecutive_days: Number of consecutive days in current state
        
        Returns:
            MetricState object
        """
        if baseline == 0:
            return MetricState("screen_time", value, baseline, 0, "normal", "No baseline data")
        
        pct_change = ((value - baseline) / baseline) * 100
        
        if -20 <= pct_change <= 20:
            state = "normal"
            reasoning = f"Screen time within normal range (±20%): {pct_change:.1f}%"
        elif pct_change >= 30 and consecutive_days >= 7:
            if pct_change >= 50 and consecutive_days >= 14:
                state = "elevated"
                reasoning = f"Screen time increase {pct_change:.1f}% is elevated (≥50%) for {consecutive_days} days"
            else:
                state = "watchful"
                reasoning = f"Screen time increase {pct_change:.1f}% is watchful (≥30%) for {consecutive_days} days"
        else:
            state = "normal"
            reasoning = f"Screen time change {pct_change:.1f}% is acceptable"
        
        return MetricState("screen_time", value, baseline, pct_change, state, reasoning)
    
    def synthesize(self, metric_states: Dict[str, MetricState]) -> Tuple[str, str]:
        """Synthesize overall behavioral state from metric states.
        
        Rules:
            - Watchful: 1 Elevated metric OR many Watchful metrics
            - Elevated: ≥ 2 Elevated metrics
            - Normal: Otherwise
        
        Args:
            metric_states: Dictionary of metric names to MetricState objects
        
        Returns:
            Tuple of (overall_state, reasoning)
        """
        elevated_count = sum(1 for s in metric_states.values() if s.state == "elevated")
        watchful_count = sum(1 for s in metric_states.values() if s.state == "watchful")
        
        if elevated_count >= 2:
            overall_state = "elevated"
            reasoning = f"Behavioral: {elevated_count} metrics elevated"
        elif elevated_count == 1:
            overall_state = "watchful"
            reasoning = f"Behavioral: 1 elevated metric detected"
        elif watchful_count >= 2:
            overall_state = "watchful"
            reasoning = f"Behavioral: {watchful_count} watchful metrics"
        else:
            overall_state = "normal"
            reasoning = "Behavioral: all metrics normal"
        
        return overall_state, reasoning


class PhysiologicalThresholdEngine:
    """Compute physiological metric states (steps, app balance, sleep).
    
    ALL THRESHOLDS IN PYTHON ONLY - NO LLM COMPUTATION.
    """
    
    def analyze_activity(self, value: float, baseline: float, consecutive_days: int = 7) -> MetricState:
        """Analyze activity (steps) metric.
        
        Rules:
            - Normal: ≥ 70% of baseline
            - Watchful: 55-70% of baseline for ≥ 7 consecutive days
            - Elevated: ≤ 50% of baseline for ≥ 14 consecutive days
        
        Args:
            value: Current average steps
            baseline: Baseline steps
            consecutive_days: Number of consecutive days in current state
        
        Returns:
            MetricState object
        """
        if baseline == 0:
            return MetricState("activity", value, baseline, 0, "normal", "No baseline data")
        
        pct_of_baseline = (value / baseline) * 100
        
        if pct_of_baseline >= 70:
            state = "normal"
            reasoning = f"Activity at {pct_of_baseline:.1f}% of baseline (≥70%)"
        elif pct_of_baseline >= 55 and consecutive_days >= 7:
            state = "watchful"
            reasoning = f"Activity at {pct_of_baseline:.1f}% of baseline (55-70%) for {consecutive_days} days"
        elif pct_of_baseline <= 50 and consecutive_days >= 14:
            state = "elevated"
            reasoning = f"Activity at {pct_of_baseline:.1f}% of baseline (≤50%) for {consecutive_days} days"
        elif pct_of_baseline < 70:
            state = "watchful"
            reasoning = f"Activity decline to {pct_of_baseline:.1f}% of baseline"
        else:
            state = "normal"
            reasoning = f"Activity at {pct_of_baseline:.1f}% of baseline"
        
        return MetricState("activity", value, baseline, pct_of_baseline - 100, state, reasoning)
    
    def analyze_app_balance(self, value: float, baseline: float) -> MetricState:
        """Analyze app balance index metric.
        
        Rules:
            - Normal: ≥ 0.45
            - Watchful: 0.25 - < 0.45
            - Elevated: < 0.25
        
        Args:
            value: Current app balance index
            baseline: Baseline app balance (not used for thresholds, just reference)
        
        Returns:
            MetricState object
        """
        if value >= 0.45:
            state = "normal"
            reasoning = f"App balance index {value:.3f} is healthy (≥0.45)"
        elif value >= 0.25:
            state = "watchful"
            reasoning = f"App balance index {value:.3f} is imbalanced (0.25-0.45)"
        else:
            state = "elevated"
            reasoning = f"App balance index {value:.3f} is severely imbalanced (<0.25)"
        
        return MetricState("app_balance", value, baseline, value - baseline, state, reasoning)
    
    def analyze_sleep(self, value: float, baseline: float, consecutive_days: int = 7) -> MetricState:
        """Analyze sleep duration metric.
        
        Rules:
            - Normal: 6.5 - 9.0 hours
            - Watchful: ≤ 6.0 hrs OR ≥ 9.5 hrs for ≥ 7 consecutive days
            - Elevated: ≤ 6.0 hrs OR ≥ 9.5 hrs for ≥ 14 consecutive days
        
        Args:
            value: Current average sleep in hours
            baseline: Baseline sleep in hours
            consecutive_days: Number of consecutive days in current state
        
        Returns:
            MetricState object
        """
        if 6.5 <= value <= 9.0:
            state = "normal"
            reasoning = f"Sleep {value:.1f}h is healthy (6.5-9.0h)"
        elif (value <= 6.0 or value >= 9.5) and consecutive_days >= 7:
            if consecutive_days >= 14:
                state = "elevated"
                reasoning = f"Sleep {value:.1f}h is abnormal for {consecutive_days} days (elevated)"
            else:
                state = "watchful"
                reasoning = f"Sleep {value:.1f}h is abnormal for {consecutive_days} days (watchful)"
        else:
            state = "normal"
            reasoning = f"Sleep {value:.1f}h is acceptable"
        
        return MetricState("sleep", value, baseline, value - baseline, state, reasoning)
    
    def synthesize(self, metric_states: Dict[str, MetricState]) -> Tuple[str, str]:
        """Synthesize overall physiological state from metric states.
        
        Rules:
            - Elevated: More than one metric Elevated
            - Watchful: One or more metrics Watchful
            - Normal: All metrics Normal
        
        Args:
            metric_states: Dictionary of metric names to MetricState objects
        
        Returns:
            Tuple of (overall_state, reasoning)
        """
        elevated_count = sum(1 for s in metric_states.values() if s.state == "elevated")
        watchful_count = sum(1 for s in metric_states.values() if s.state == "watchful")
        
        if elevated_count > 1:
            overall_state = "elevated"
            reasoning = f"Physiological: {elevated_count} metrics elevated"
        elif elevated_count == 1 or watchful_count >= 1:
            overall_state = "watchful"
            reasoning = f"Physiological: elevated={elevated_count}, watchful={watchful_count}"
        else:
            overall_state = "normal"
            reasoning = "Physiological: all metrics normal"
        
        return overall_state, reasoning


class ContextThresholdEngine:
    """Compute context & environment metric states (WiFi diversity, location dominance).
    
    ALL THRESHOLDS IN PYTHON ONLY - NO LLM COMPUTATION.
    """
    
    def analyze_daily_unique_wifi_count(self, value: float, baseline: float, consecutive_days: int = 7) -> MetricState:
        """Analyze daily unique WiFi count (DUWC).
        
        Rules:
            - Normal: ≥ 70% of baseline
            - Watchful: 40-70% of baseline for ≥ 7 consecutive days
            - Elevated: ≤ 40% of baseline for ≥ 14 consecutive days
        
        Args:
            value: Current average DUWC
            baseline: Baseline DUWC
            consecutive_days: Number of consecutive days
        
        Returns:
            MetricState object
        """
        if baseline == 0:
            return MetricState("duwc", value, baseline, 0, "normal", "No baseline data")
        
        pct_of_baseline = (value / baseline) * 100
        
        if pct_of_baseline >= 70:
            state = "normal"
            reasoning = f"WiFi diversity at {pct_of_baseline:.1f}% of baseline (≥70%)"
        elif pct_of_baseline >= 40 and consecutive_days >= 7:
            state = "watchful"
            reasoning = f"WiFi diversity at {pct_of_baseline:.1f}% of baseline (40-70%) for {consecutive_days} days"
        elif pct_of_baseline <= 40 and consecutive_days >= 14:
            state = "elevated"
            reasoning = f"WiFi diversity at {pct_of_baseline:.1f}% of baseline (≤40%) for {consecutive_days} days"
        elif pct_of_baseline < 70:
            state = "watchful"
            reasoning = f"WiFi diversity decline to {pct_of_baseline:.1f}% of baseline"
        else:
            state = "normal"
            reasoning = f"WiFi diversity at {pct_of_baseline:.1f}% of baseline"
        
        return MetricState("duwc", value, baseline, pct_of_baseline - 100, state, reasoning)
    
    def analyze_wifi_location_dominance(self, value: float, baseline: float, consecutive_days: int = 7) -> MetricState:
        """Analyze WiFi location dominance (% time at primary location).
        
        Rules:
            - Normal: ≤ 65% of day
            - Watchful: 70-80% of day for ≥ 7 consecutive days
            - Elevated: ≥ 85% of day for ≥ 14 consecutive days
        
        Args:
            value: Current location dominance percentage (0-100)
            baseline: Baseline dominance percentage
            consecutive_days: Number of consecutive days
        
        Returns:
            MetricState object
        """
        if value <= 65:
            state = "normal"
            reasoning = f"Location dominance {value:.1f}% is healthy (≤65%)"
        elif 70 <= value <= 80 and consecutive_days >= 7:
            state = "watchful"
            reasoning = f"Location dominance {value:.1f}% is high (70-80%) for {consecutive_days} days"
        elif value >= 85 and consecutive_days >= 14:
            state = "elevated"
            reasoning = f"Location dominance {value:.1f}% is very high (≥85%) for {consecutive_days} days"
        elif value >= 70:
            state = "watchful"
            reasoning = f"Location dominance {value:.1f}% is elevated"
        else:
            state = "normal"
            reasoning = f"Location dominance {value:.1f}% is acceptable"
        
        return MetricState("location_dominance", value, baseline, value - baseline, state, reasoning)
    
    def synthesize(self, metric_states: Dict[str, MetricState]) -> Tuple[str, str]:
        """Synthesize overall context state.
        
        Rules:
            - Normal: Both Normal OR only one Watchful
            - Watchful: DUWC = Watchful OR Home dominance = Watchful, OR Either one Elevated alone
            - Elevated: DUWC = Elevated AND Home dominance = Elevated AND persistence ≥ 14 days
        
        Args:
            metric_states: Dictionary of metric names to MetricState objects
        
        Returns:
            Tuple of (overall_state, reasoning)
        """
        duwc_state = metric_states.get("duwc", MetricState("duwc", 0, 0, 0, "normal", "")).state
        location_state = metric_states.get("location_dominance", MetricState("location_dominance", 0, 0, 0, "normal", "")).state
        
        # Both elevated with long duration = elevated overall
        if duwc_state == "elevated" and location_state == "elevated":
            overall_state = "elevated"
            reasoning = "Context: Both WiFi diversity and location dominance elevated"
        # One elevated alone = watchful
        elif duwc_state == "elevated" or location_state == "elevated":
            overall_state = "watchful"
            reasoning = f"Context: One metric elevated (duwc={duwc_state}, location={location_state})"
        # Either metric watchful = watchful
        elif duwc_state == "watchful" or location_state == "watchful":
            overall_state = "watchful"
            reasoning = f"Context: One or more watchful metrics (duwc={duwc_state}, location={location_state})"
        # Both normal = normal
        else:
            overall_state = "normal"
            reasoning = "Context: all metrics normal"
        
        return overall_state, reasoning
