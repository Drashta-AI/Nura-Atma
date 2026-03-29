"""Excel data loader for behavioral, physiological, and contextual data."""

import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple
import logging
import os 


logger = logging.getLogger(__name__)


class ExcelDataLoader:
    """Load and parse Excel files with behavioral, physiological, and contextual data."""
    
    def __init__(self, data_dir: str = "behaviour_signal_data"):
        """Initialize loader with data directory.
        
        Args:
            data_dir: Root directory containing subdirectories for different data types
        """
        self.data_dir = Path(data_dir)
        self.behaviour_dir = self.data_dir / "behaviour_signal_data" if not data_dir.endswith("behaviour_signal_data") else self.data_dir
        self.wearable_dir = self.data_dir.parent / "wearble_data"
        self.wifi_dir = self.data_dir.parent / "wifi_data"
        self.conversation_dir = self.data_dir.parent / "conversation_data"
    
    def load_call_count(self) -> pd.DataFrame:
        """Load call count data.
        
        Returns:
            DataFrame with date and call count columns
        """
        file_path = self.behaviour_dir / "Call_Count_Context_Agent.xlsx"
        if not file_path.exists():
            logger.warning("Current working directory:", os.getcwd())
            logger.warning(f"Call count file not found at {file_path}")
            return pd.DataFrame()
        
        df = pd.read_excel(file_path)
        if 'Date' in df.columns:
            df['date'] = pd.to_datetime(df['Date'])
        return df
    
    def load_conversation_duration(self) -> pd.DataFrame:
        """Load conversation duration data.
        
        Returns:
            DataFrame with date and conversation duration columns
        """
        file_path = self.behaviour_dir / "conversation_duration_progressive.xlsx"
        if not file_path.exists():
            logger.warning(f"Conversation duration file not found at {file_path}")
            return pd.DataFrame()
        
        df = pd.read_excel(file_path)
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
        return df
    
    def load_screen_time(self) -> pd.DataFrame:
        """Load screen time data.
        
        Returns:
            DataFrame with date and screen time columns
        """
        file_path = self.behaviour_dir / "screen_time_progressive.xlsx"
        if not file_path.exists():
            logger.warning(f"Screen time file not found at {file_path}")
            return pd.DataFrame()
        
        df = pd.read_excel(file_path)
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        return df
    
    def load_app_balance_index(self) -> pd.DataFrame:
        """Load app balance index data.
        
        Returns:
            DataFrame with date and app balance index columns
        """
        file_path = self.behaviour_dir / "app_balance_index_2013-03-28_to_2013-05-26.xlsx"
        if not file_path.exists():
            logger.warning(f"App balance index file not found at {file_path}")
            return pd.DataFrame()
        
        df = pd.read_excel(file_path)
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        return df
    
    def load_steps(self) -> pd.DataFrame:
        """Load steps/activity data.
        
        Returns:
            DataFrame with date and steps columns
        """
        file_path = self.wearable_dir / "exercise_steps_inference.xlsx"
        if not file_path.exists():
            logger.warning(f"Steps file not found at {file_path}")
            return pd.DataFrame()
        
        df = pd.read_excel(file_path)
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        return df
    
    def load_sleep(self) -> pd.DataFrame:
        """Load sleep duration data.
        
        Returns:
            DataFrame with date and sleep hours columns
        """
        file_path = self.wearable_dir / "date_and_sleep_hours.xlsx"
        if not file_path.exists():
            logger.warning(f"Sleep file not found at {file_path}")
            return pd.DataFrame()
        
        df = pd.read_excel(file_path)
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        return df
    
    def load_duwc(self) -> pd.DataFrame:
        """Load Daily Unique WiFi Count (DUWC) data.
        
        Returns:
            DataFrame with date and DUWC columns
        """
        file_path = self.wifi_dir / "DUWC_Context_Environment_Agent.xlsx"
        if not file_path.exists():
            logger.warning(f"DUWC file not found at {file_path}")
            return pd.DataFrame()
        
        df = pd.read_excel(file_path)
        logger.info(f"DUWC data loaded with {len(df)} records")
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
        return df
    
    def load_wifi_location_dominance(self) -> pd.DataFrame:
        """Load WiFi location dominance data.
        
        Returns:
            DataFrame with date and location dominance columns
        """
        file_path = self.wifi_dir / "wifi_location_dominance.xlsx"
        if not file_path.exists():
            logger.warning(f"WiFi location dominance file not found at {file_path}")
            return pd.DataFrame()
        
        df = pd.read_excel(file_path)
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        return df
    
    def load_chat_messages(self) -> pd.DataFrame:
        """Load conversation/chat messages for language analysis.
        
        Returns:
            DataFrame with date, timestamp, and message columns
        """
        file_path = self.conversation_dir / "mental_health_chat_data.csv"
        
        if not file_path.exists():
            logger.warning(f"Chat data file not found at {file_path}")
            return pd.DataFrame()
        
        # ✅ FIX: specify encoding
        df = pd.read_csv(file_path, encoding="utf-8")

        # Normalize column names
        df.columns = df.columns.str.strip().str.lower()

        # Parse date columns safely
        for col in ['date', 'timestamp']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=False)

        return df

    
    def get_baseline_window_data(self) -> Dict[str, pd.DataFrame]:
        """Get all data for baseline window (28-03-2013 to 03-04-2013).
        
        Returns:
            Dictionary mapping metric names to DataFrames filtered for baseline period
        """
        baseline_start = datetime(2013, 3, 28)
        baseline_end = datetime(2013, 4, 3, 23, 59, 59)
        
        data = {}
        for metric_name, loader_func in [
            ("call_count", self.load_call_count),
            ("conversation_duration_minutes", self.load_conversation_duration),
            ("screen_time", self.load_screen_time),
            ("app_balance_index", self.load_app_balance_index),
            ("steps", self.load_steps),
            ("sleep_hours", self.load_sleep),
            ("duwc", self.load_duwc),
            ("wifi_location_dominance", self.load_wifi_location_dominance),
        ]:
            df = loader_func()
            if not df.empty and 'date' in df.columns:
                # Filter for baseline period
                filtered = df[(df['date'] >= baseline_start) & (df['date'] <= baseline_end)]
                data[metric_name] = filtered
            else:
                data[metric_name] = pd.DataFrame()
        
        return data
    
    def get_weekly_window_data(self, week_start: datetime) -> Dict[str, pd.DataFrame]:
        """Get all data for a specific week.
        
        Args:
            week_start: Start date of the week
        
        Returns:
            Dictionary mapping metric names to DataFrames filtered for the week
        """
        week_end = week_start + timedelta(days=7, seconds=-1)
        
        data = {}
        for metric_name, loader_func in [
            ("call_count", self.load_call_count),
            ("conversation_duration_minutes", self.load_conversation_duration),
            ("screen_time", self.load_screen_time),
            ("app_balance_index", self.load_app_balance_index),
            ("steps", self.load_steps),
            ("sleep_hours", self.load_sleep),
            ("duwc", self.load_duwc),
            ("wifi_location_dominance", self.load_wifi_location_dominance),
        ]:
            df = loader_func()
            if not df.empty and 'date' in df.columns:
                # Filter for week
                filtered = df[(df['date'] >= week_start) & (df['date'] <= week_end)]
                data[metric_name] = filtered
            else:
                data[metric_name] = pd.DataFrame()
        
        return data
