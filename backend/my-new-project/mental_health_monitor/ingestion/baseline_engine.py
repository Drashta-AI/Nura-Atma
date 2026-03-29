"""Baseline metrics computation engine (28-03-2013 to 03-04-2013)."""

import pandas as pd
from datetime import datetime
from typing import Dict
import logging

from .excel_loader import ExcelDataLoader
from ..database import get_session, BaselineMetrics

logger = logging.getLogger(__name__)


class BaselineEngine:
    """Compute 7-day baseline metrics from 28-03-2013 to 03-04-2013."""
    
    BASELINE_START = datetime(2013, 3, 28)
    BASELINE_END = datetime(2013, 4, 3)
    
    def __init__(self, loader: ExcelDataLoader):
        """Initialize baseline engine.
        
        Args:
            loader: ExcelDataLoader instance
        """
        self.loader = loader
    
    def compute_baseline(self) -> Dict[str, float]:
        """Compute all baseline metrics.
        
        Returns:
            Dictionary mapping metric names to baseline values
        """
        data = self.loader.get_baseline_window_data()
        baseline = {}
        
        # Call count baseline (average calls per day)
        baseline["call_count"] = self._compute_call_count_baseline(data.get("call_count", pd.DataFrame()))
        
        # Conversation duration baseline (average minutes per day)
        baseline["conversation_duration"] = self._compute_conversation_duration_baseline(
            data.get("conversation_duration_minutes", pd.DataFrame())
        )
        
        # Screen time baseline (average minutes per day)
        baseline["screen_time"] = self._compute_screen_time_baseline(
            data.get("screen_time", pd.DataFrame())
        )
        
        # App balance index baseline (average of daily indices)
        baseline["app_balance_index"] = self._compute_app_balance_baseline(
            data.get("app_balance_index", pd.DataFrame())
        )
        
        # Steps baseline (average steps per day)
        baseline["steps"] = self._compute_steps_baseline(data.get("steps", pd.DataFrame()))
        
        # Sleep baseline (average hours per day)
        baseline["sleep"] = self._compute_sleep_baseline(data.get("sleep_hours", pd.DataFrame()))
        
        # DUWC baseline (average unique WiFi networks per day)
        baseline["duwc"] = self._compute_duwc_baseline(data.get("duwc", pd.DataFrame()))
        
        # WiFi location dominance baseline (average % time at home location)
        baseline["wifi_location_dominance"] = self._compute_location_dominance_baseline(
            data.get("wifi_location_dominance", pd.DataFrame())
        )
        
        return baseline
    
    def _compute_call_count_baseline(self, df: pd.DataFrame) -> float:
        """Compute average daily call count.
        
        Args:
            df: DataFrame with Date and call count columns
        
        Returns:
            Average daily call count
        """
        if df.empty:
            logger.warning("No call count data for baseline")
            return 0.0
        
        # Get call count column (name may vary)
        call_col = None
        for col in df.columns:
            if 'call' in col.lower() or col.lower() == 'count':
                call_col = col
                break
        
        if call_col:
            return df[call_col].mean()
        return 0.0
    
    def _compute_conversation_duration_baseline(self, df: pd.DataFrame) -> float:
        """Compute average daily conversation duration in minutes.
        
        Args:
            df: DataFrame with conversation duration data
        
        Returns:
            Average daily conversation duration
        """
        if df.empty:
            logger.warning("No conversation duration data for baseline")
            return 0.0
        
        duration_col = None
        for col in df.columns:
            if 'duration' in col.lower() or 'minutes' in col.lower():
                duration_col = col
                break
        
        if duration_col:
            return df[duration_col].mean()
        return 0.0
    
    def _compute_screen_time_baseline(self, df: pd.DataFrame) -> float:
        """Compute average daily screen time in minutes.
        
        Args:
            df: DataFrame with screen time data
        
        Returns:
            Average daily screen time
        """
        if df.empty:
            logger.warning("No screen time data for baseline")
            return 0.0
        
        screen_col = None
        for col in df.columns:
            if 'screen' in col.lower() or 'time' in col.lower():
                screen_col = col
                break
        
        if screen_col:
            return df[screen_col].mean()
        return 0.0
    
    def _compute_app_balance_baseline(self, df: pd.DataFrame) -> float:
        """Compute average daily app balance index.
        
        Args:
            df: DataFrame with app balance index data
        
        Returns:
            Average app balance index (0 to 1)
        """
        if df.empty:
            logger.warning("No app balance index data for baseline")
            return 0.5
        
        balance_col = None
        for col in df.columns:
            if 'balance' in col.lower() or 'index' in col.lower():
                balance_col = col
                break
        
        if balance_col:
            mean_val = df[balance_col].mean()
            # Ensure it's normalized to 0-1
            if mean_val > 1:
                mean_val = mean_val / 100
            return mean_val
        return 0.5
    
    def _compute_steps_baseline(self, df: pd.DataFrame) -> float:
        """Compute average daily steps.
        
        Args:
            df: DataFrame with steps data
        
        Returns:
            Average daily steps
        """
        if df.empty:
            logger.warning("No steps data for baseline")
            return 0.0
        
        steps_col = None
        for col in df.columns:
            if 'steps' in col.lower() or 'exercise' in col.lower():
                steps_col = col
                break
        
        if steps_col:
            return df[steps_col].mean()
        return 0.0
    
    def _compute_sleep_baseline(self, df: pd.DataFrame) -> float:
        """Compute average daily sleep duration in hours.
        
        Args:
            df: DataFrame with sleep data
        
        Returns:
            Average daily sleep in hours
        """
        if df.empty:
            logger.warning("No sleep data for baseline")
            return 7.5
        
        sleep_col = None
        for col in df.columns:
            if 'sleep' in col.lower() or 'hours' in col.lower():
                sleep_col = col
                break
        
        if sleep_col:
            value = df[sleep_col].mean()
            # If value looks like it's in minutes, convert to hours
            if value > 24:
                value = value / 60
            return value
        return 7.5
    
    def _compute_duwc_baseline(self, df: pd.DataFrame) -> float:
        """Compute average daily unique WiFi count (DUWC).
        
        Args:
            df: DataFrame with DUWC data
        
        Returns:
            Average daily unique WiFi count
        """
        if df.empty:
            logger.warning("No DUWC data for baseline")
            return 0.0
        
        duwc_col = None
        for col in df.columns:
            if 'duwc' in col.lower() or 'unique' in col.lower() or 'wifi' in col.lower():
                duwc_col = col
                break
        
        if duwc_col:
            return df[duwc_col].mean()
        return 0.0
    
    def _compute_location_dominance_baseline(self, df: pd.DataFrame) -> float:
        """Compute average WiFi location dominance (% time at primary location).
        
        Args:
            df: DataFrame with location dominance data
        
        Returns:
            Average dominance percentage (0-100)
        """
        if df.empty:
            logger.warning("No WiFi location dominance data for baseline")
            return 60.0
        
        dominance_col = None
        for col in df.columns:
            if 'dominance' in col.lower() or 'location' in col.lower() or 'percentage' in col.lower():
                dominance_col = col
                break
        
        if dominance_col:
            return df[dominance_col].mean()
        return 60.0
    
    def save_baseline_to_db(self, baseline: Dict[str, float]):
        """Save baseline metrics to database.
        
        Args:
            baseline: Dictionary of metric names to baseline values
        """
        session = get_session()
        try:
            # Clear existing baseline
            session.query(BaselineMetrics).delete()
            session.commit()
            
            # Insert new baseline
            for metric_name, value in baseline.items():
                db_metric = BaselineMetrics(
                    metric_name=metric_name,
                    baseline_value=value
                )
                session.add(db_metric)
            
            session.commit()
            logger.info(f"Saved {len(baseline)} baseline metrics to database")
        except Exception as e:
            logger.error(f"Error saving baseline metrics: {e}")
            session.rollback()
        finally:
            session.close()
