"""Weekly window engine for computing aggregated metrics and percentage changes."""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Tuple
import logging

from .excel_loader import ExcelDataLoader
from ..database import get_session, BaselineMetrics, WeeklyMetrics

logger = logging.getLogger(__name__)


class WeeklyWindowEngine:
    """Compute weekly aggregated metrics and percentage changes vs baseline."""
    
    SIMULATION_START = datetime(2013, 4, 20)  # Week 1 starts 20-04-2013
    
    def __init__(self, loader: ExcelDataLoader):
        """Initialize weekly window engine.
        
        Args:
            loader: ExcelDataLoader instance
        """
        self.loader = loader
        self._baseline_cache = None
    
    def get_baseline(self) -> Dict[str, float]:
        """Get cached baseline metrics from database.
        
        Returns:
            Dictionary of baseline metrics
        """
        if self._baseline_cache is not None:
            return self._baseline_cache
        
        session = get_session()
        try:
            baseline = {}
            metrics = session.query(BaselineMetrics).all()
            for metric in metrics:
                baseline[metric.metric_name] = metric.baseline_value
            self._baseline_cache = baseline
            return baseline
        finally:
            session.close()
    
    def compute_week_metrics(self, week_number: int) -> Dict[str, Tuple[float, float]]:
        """Compute aggregated metrics for a given week.
        
        Args:
            week_number: Week number (1, 2, 3)
        
        Returns:
            Dictionary mapping metric names to tuples of (avg_value, pct_change)
        """
        # Calculate week start date
        week_start = self.SIMULATION_START + timedelta(days=(week_number - 1) * 7)
        
        # Get data for the week
        data = self.loader.get_weekly_window_data(week_start)
        baseline = self.get_baseline()
        
        metrics = {}
        
        # Call count
        call_count_avg = self._compute_call_count_avg(data.get("call_count", pd.DataFrame()))
        metrics["call_count"] = (
            call_count_avg,
            self._compute_pct_change(call_count_avg, baseline.get("call_count", 1))
        )
        
        # Conversation duration
        conv_dur_avg = self._compute_conversation_duration_avg(data.get("conversation_duration", pd.DataFrame()))
        metrics["conversation_duration"] = (
            conv_dur_avg,
            self._compute_pct_change(conv_dur_avg, baseline.get("conversation_duration", 1))
        )
        
        # Phone interaction events (proxy: screen time minutes)
        screen_time_avg = self._compute_screen_time_avg(data.get("screen_time", pd.DataFrame()))
        metrics["phone_interactions"] = (
            screen_time_avg,
            self._compute_pct_change(screen_time_avg, baseline.get("screen_time", 1))
        )
        
        # Screen time
        metrics["screen_time"] = (
            screen_time_avg,
            self._compute_pct_change(screen_time_avg, baseline.get("screen_time", 1))
        )
        
        # Activity (steps)
        steps_avg = self._compute_steps_avg(data.get("steps", pd.DataFrame()))
        metrics["steps"] = (
            steps_avg,
            self._compute_pct_change(steps_avg, baseline.get("steps", 1))
        )
        
        # App balance index
        app_balance_avg = self._compute_app_balance_avg(data.get("app_balance_index", pd.DataFrame()))
        metrics["app_balance_index"] = (
            app_balance_avg,
            abs(app_balance_avg - baseline.get("app_balance_index", 0.5))
        )
        
        # Sleep
        sleep_avg = self._compute_sleep_avg(data.get("sleep", pd.DataFrame()))
        metrics["sleep"] = (
            sleep_avg,
            self._compute_absolute_change(sleep_avg, baseline.get("sleep", 7.5))
        )
        
        # DUWC (Daily Unique WiFi Count)
        duwc_avg = self._compute_duwc_avg(data.get("duwc", pd.DataFrame()))
        metrics["duwc"] = (
            duwc_avg,
            self._compute_pct_change(duwc_avg, baseline.get("duwc", 1))
        )
        
        # WiFi location dominance
        location_dom_avg = self._compute_location_dominance_avg(data.get("wifi_location_dominance", pd.DataFrame()))
        metrics["wifi_location_dominance"] = (
            location_dom_avg,
            self._compute_absolute_change(location_dom_avg, baseline.get("wifi_location_dominance", 60))
        )
        
        return metrics
    
    def _compute_pct_change(self, current: float, baseline: float) -> float:
        """Compute percentage change from baseline.
        
        Args:
            current: Current value
            baseline: Baseline value
        
        Returns:
            Percentage change (-100 to +inf)
        """
        if baseline == 0:
            return 0.0
        return ((current - baseline) / baseline) * 100
    
    def _compute_absolute_change(self, current: float, baseline: float) -> float:
        """Compute absolute change from baseline.
        
        Args:
            current: Current value
            baseline: Baseline value
        
        Returns:
            Absolute difference
        """
        return current - baseline
    
    def _compute_call_count_avg(self, df: pd.DataFrame) -> float:
        """Compute average daily call count."""
        if df.empty:
            return 0.0
        
        call_col = None
        for col in df.columns:
            if 'call' in col.lower() or col.lower() == 'count':
                call_col = col
                break
        
        if call_col:
            return df[call_col].mean()
        return 0.0
    
    def _compute_conversation_duration_avg(self, df: pd.DataFrame) -> float:
        """Compute average daily conversation duration."""
        if df.empty:
            return 0.0
        
        duration_col = None
        for col in df.columns:
            if 'duration' in col.lower() or 'minutes' in col.lower():
                duration_col = col
                break
        
        if duration_col:
            return df[duration_col].mean()
        return 0.0
    
    def _compute_screen_time_avg(self, df: pd.DataFrame) -> float:
        """Compute average daily screen time."""
        if df.empty:
            return 0.0
        
        screen_col = None
        for col in df.columns:
            if 'screen' in col.lower() or 'time' in col.lower():
                screen_col = col
                break
        
        if screen_col:
            return df[screen_col].mean()
        return 0.0
    
    def _compute_steps_avg(self, df: pd.DataFrame) -> float:
        """Compute average daily steps."""
        if df.empty:
            return 0.0
        
        steps_col = None
        for col in df.columns:
            if 'steps' in col.lower() or 'exercise' in col.lower():
                steps_col = col
                break
        
        if steps_col:
            return df[steps_col].mean()
        return 0.0
    
    def _compute_app_balance_avg(self, df: pd.DataFrame) -> float:
        """Compute average daily app balance index."""
        if df.empty:
            return 0.5
        
        balance_col = None
        for col in df.columns:
            if 'balance' in col.lower() or 'index' in col.lower():
                balance_col = col
                break
        
        if balance_col:
            mean_val = df[balance_col].mean()
            if mean_val > 1:
                mean_val = mean_val / 100
            return mean_val
        return 0.5
    
    def _compute_sleep_avg(self, df: pd.DataFrame) -> float:
        """Compute average daily sleep."""
        if df.empty:
            return 7.5
        
        sleep_col = None
        for col in df.columns:
            if 'sleep' in col.lower() or 'hours' in col.lower():
                sleep_col = col
                break
        
        if sleep_col:
            value = df[sleep_col].mean()
            if value > 24:
                value = value / 60
            return value
        return 7.5
    
    def _compute_duwc_avg(self, df: pd.DataFrame) -> float:
        """Compute average daily unique WiFi count."""
        if df.empty:
            return 0.0
        
        duwc_col = None
        for col in df.columns:
            if 'duwc' in col.lower() or 'unique' in col.lower():
                duwc_col = col
                break
        
        if duwc_col:
            return df[duwc_col].mean()
        return 0.0
    
    def _compute_location_dominance_avg(self, df: pd.DataFrame) -> float:
        """Compute average WiFi location dominance."""
        if df.empty:
            return 60.0
        
        dominance_col = None
        for col in df.columns:
            if 'dominance' in col.lower() or 'location' in col.lower() or 'percentage' in col.lower():
                dominance_col = col
                break
        
        if dominance_col:
            return df[dominance_col].mean()
        return 60.0
    
    def save_weekly_metrics_to_db(self, week_number: int, metrics: Dict[str, Tuple[float, float]]):
        """Save weekly metrics to database.
        
        Args:
            week_number: Week number (1, 2, 3)
            metrics: Dictionary of metric names to (avg_value, pct_change) tuples
        """
        session = get_session()
        try:
            # Delete existing metrics for this week
            session.query(WeeklyMetrics).filter(WeeklyMetrics.week_number == week_number).delete()
            session.commit()
            
            # Insert new metrics
            for metric_name, (avg_value, pct_change) in metrics.items():
                db_metric = WeeklyMetrics(
                    week_number=week_number,
                    metric_name=metric_name,
                    avg_value=avg_value,
                    pct_change=pct_change,
                    duration_consecutive_days=7  # Full week
                )
                session.add(db_metric)
            
            session.commit()
            logger.info(f"Saved {len(metrics)} weekly metrics for week {week_number}")
        except Exception as e:
            logger.error(f"Error saving weekly metrics: {e}")
            session.rollback()
        finally:
            session.close()
