"""Weekly simulator for running the 3-week monitoring simulation."""

from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Dict, List, Optional
import json
import time

from ..ingestion import ExcelDataLoader, BaselineEngine, WeeklyWindowEngine
from ..ingestion import BehavioralSignalThresholdEngine, PhysiologicalThresholdEngine, ContextThresholdEngine
from ..graph import GraphState, get_compiled_graph
from ..database import get_session, WeeklyMetrics, UserProfile, AgentOutput, LanguageAgentOutput, OverallState
from ..llm import LLMFactory
from ..reports import ReportGenerator

logger = logging.getLogger(__name__)


class WeeklySimulator:
    """Run weekly simulation for 3 weeks starting 20-04-2013."""
    
    SIMULATION_START = datetime(2013, 4, 20)
    TOTAL_WEEKS = 3
    
    def __init__(self):
        """Initialize weekly simulator."""
        self.loader = ExcelDataLoader()
        self.baseline_engine = BaselineEngine(self.loader)
        self.weekly_engine = WeeklyWindowEngine(self.loader)
        self.behavioral_threshold = BehavioralSignalThresholdEngine()
        self.physiological_threshold = PhysiologicalThresholdEngine()
        self.context_threshold = ContextThresholdEngine()
        self.graph = get_compiled_graph()
    
    def get_character_sketch(self) -> Dict:
        """Get character sketch from database or generate from questionnaire.
        
        Returns:
            Character sketch dictionary
        """
        session = get_session()
        try:
            profile = session.query(UserProfile).order_by(UserProfile.id.desc()).first()
            if profile and profile.character_sketch_json:
                return profile.character_sketch_json
        except Exception as e:
            logger.error(f"Error retrieving character sketch: {e}")
        finally:
            session.close()
        
        # Return default if not found
        return {
            "personality_summary": "Unknown",
            "coping_style": "Unknown",
            "stress_sensitivity": "moderate",
            "social_dependency": "moderate",
            "motivational_style": "Unknown"
        }
    
    def get_baseline_metrics(self) -> Dict[str, float]:
        """Get baseline metrics from database.
        
        Returns:
            Dictionary of baseline metrics
        """
        session = get_session()
        try:
            baseline = self.weekly_engine.get_baseline()
            return baseline
        finally:
            session.close()
    
    def get_weekly_metrics(self, week_number: int) -> Dict[str, tuple]:
        """Get weekly metrics for a specific week.
        
        Args:
            week_number: Week number (1, 2, 3)
        
        Returns:
            Dictionary of metric_name -> (value, pct_change)
        """
        return self.weekly_engine.compute_week_metrics(week_number)
    
    def compute_metric_states(self, week_number: int, baseline: Dict[str, float]) -> tuple:
        """Compute behavioral, physiological, and context metric states.
        
        Args:
            week_number: Week number
            baseline: Baseline metrics
        
        Returns:
            Tuple of (behavioral_states, physiological_states, context_states)
        """
        weekly_metrics = self.get_weekly_metrics(week_number)
        
        # Behavioral states
        behavioral_states = {}
        
        # Call count
        call_count_state = self.behavioral_threshold.analyze_call_count(
            weekly_metrics.get("call_count", (0, 0))[0],
            baseline.get("call_count", 1),
            7
        )
        behavioral_states["call_count"] = call_count_state
        
        # Conversation duration
        conv_dur_state = self.behavioral_threshold.analyze_conversation_duration(
            weekly_metrics.get("conversation_duration", (0, 0))[0],
            baseline.get("conversation_duration", 1),
            7
        )
        behavioral_states["conversation_duration"] = conv_dur_state
        
        # Phone interactions
        phone_int_state = self.behavioral_threshold.analyze_phone_interactions(
            weekly_metrics.get("phone_interactions", (0, 0))[0],
            baseline.get("phone_interactions", 1),
            7
        )
        behavioral_states["phone_interactions"] = phone_int_state
        
        # Screen time
        screen_state = self.behavioral_threshold.analyze_screen_time(
            weekly_metrics.get("screen_time", (0, 0))[0],
            baseline.get("screen_time", 1),
            7
        )
        behavioral_states["screen_time"] = screen_state
        
        # Physiological states
        physiological_states = {}
        
        # Activity (steps)
        activity_state = self.physiological_threshold.analyze_activity(
            weekly_metrics.get("steps", (0, 0))[0],
            baseline.get("steps", 1),
            7
        )
        physiological_states["activity"] = activity_state
        
        # App balance
        app_balance_state = self.physiological_threshold.analyze_app_balance(
            weekly_metrics.get("app_balance_index", (0, 0))[0],
            baseline.get("app_balance_index", 0.5)
        )
        physiological_states["app_balance"] = app_balance_state
        
        # Sleep
        sleep_state = self.physiological_threshold.analyze_sleep(
            weekly_metrics.get("sleep", (0, 0))[0],
            baseline.get("sleep", 7.5),
            7
        )
        physiological_states["sleep"] = sleep_state
        
        # Context states
        context_states = {}
        
        # DUWC
        duwc_state = self.context_threshold.analyze_daily_unique_wifi_count(
            weekly_metrics.get("duwc", (0, 0))[0],
            baseline.get("duwc", 1),
            7
        )
        context_states["duwc"] = duwc_state
        
        # Location dominance
        location_state = self.context_threshold.analyze_wifi_location_dominance(
            weekly_metrics.get("wifi_location_dominance", (0, 0))[0],
            baseline.get("wifi_location_dominance", 60),
            7
        )
        context_states["location_dominance"] = location_state
        
        return behavioral_states, physiological_states, context_states
    
    def get_weekly_messages(self, week_number: int) -> str:
        """Get aggregated chat messages for a week.
        
        Args:
            week_number: Week number
        
        Returns:
            Aggregated messages string
        """
        df = self.loader.load_chat_messages()
        if df.empty:
            return "No messages available for this week."
        
        # Try to filter by date
        week_start = self.SIMULATION_START + timedelta(days=(week_number - 1) * 7)
        week_end = week_start + timedelta(days=7)
        
        # Find date column
        date_col = None
        for col in df.columns:
            if col.lower() in ['date', 'timestamp', 'created_at']:
                date_col = col
                break
        
        if date_col and 'Date' in df.columns and df[date_col].dtype == 'datetime64[ns]':
            filtered = df[(df[date_col] >= week_start) & (df[date_col] <= week_end)]
        else:
            # Return all messages with week indicator
            filtered = df.head(50)  # Limit to first 50 for demo
        
        # Find message column
        message_col = None
        for col in df.columns:
            if col.lower() in ['message', 'text', 'content', 'chat', 'body']:
                message_col = col
                break
        
        if message_col:
            messages_list = filtered[message_col].dropna().astype(str).tolist()
            return "\n".join(messages_list[:50])  # First 50 messages
        
        return "Messages: " + str(filtered.to_dict('records')[:10])
    
    def run_week(self, week_number: int) -> Dict:
        """Run analysis for a single week.
        
        Args:
            week_number: Week number (1, 2, 3)
        
        Returns:
            Dictionary with complete week analysis results
        """
        logger.info(f"Starting week {week_number} analysis...")
        
        try:
            # Get data
            character_sketch = self.get_character_sketch()
            baseline = self.get_baseline_metrics()
            
            # Compute metric states
            behavioral_states, physiological_states, context_states = self.compute_metric_states(
                week_number, baseline
            )
            
            # Get weekly messages
            weekly_messages = self.get_weekly_messages(week_number)
            
            # Prepare graph input
            graph_input = GraphState(
                week_number=week_number,
                start_date=self.SIMULATION_START + timedelta(days=(week_number - 1) * 7),
                character_sketch=character_sketch,
                baseline_metrics=baseline,
                behavioral_metric_states={k: v.__dict__ for k, v in behavioral_states.items()},
                physiological_metric_states={k: v.__dict__ for k, v in physiological_states.items()},
                context_metric_states={k: v.__dict__ for k, v in context_states.items()},
                weekly_messages=weekly_messages
            )
            
            # Run graph
            logger.info(f"Running orchestration graph for week {week_number}...")
            result = self.graph.invoke(graph_input)
            
            # Save weekly metrics to DB
            weekly_metrics = self.get_weekly_metrics(week_number)
            self.weekly_engine.save_weekly_metrics_to_db(week_number, weekly_metrics)
            
            logger.info(f"Week {week_number} analysis complete. State: {result.get('overall_state', 'unknown')}")
            
            # Wait 5 minutes per week for simulation pacing
            logger.info(f"Waiting 5 minutes before next week...")
            time.sleep(300)
            
            return {
                "week_number": week_number,
                "success": True,
                "overall_state": result.get("overall_state", "normal"),
                "support_message": result.get("conversational_message", ""),
                "errors": result.get("errors", [])
            }
        
        except Exception as e:
            logger.error(f"Error processing week {week_number}: {e}", exc_info=True)
            return {
                "week_number": week_number,
                "success": False,
                "overall_state": "unknown",
                "error": str(e)
            }

    def reset_previous_outputs(self) -> None:
        """Clear previous reports and LLM outputs before a new simulation run."""
        session = get_session()
        try:
            deleted_agent_rows = session.query(AgentOutput).delete()
            deleted_language_rows = session.query(LanguageAgentOutput).delete()
            deleted_overall_rows = session.query(OverallState).delete()
            session.commit()
            logger.info(
                "Cleared previous LLM outputs: %s agent rows, %s language rows, %s overall rows",
                deleted_agent_rows,
                deleted_language_rows,
                deleted_overall_rows,
            )
        except Exception:
            session.rollback()
            logger.exception("Failed to clear previous LLM outputs")
            raise
        finally:
            session.close()

        report_dir = ReportGenerator.REPORT_DIR
        if not report_dir.exists():
            return

        removed_files = 0
        for report_file in report_dir.glob("week_*_report.md"):
            try:
                report_file.unlink()
                removed_files += 1
            except OSError:
                logger.exception("Failed to delete report file: %s", report_file)
                raise

        logger.info("Cleared %s previous weekly report files", removed_files)
    
    def run_simulation(self) -> List[Dict]:
        """Run the complete 3-week simulation.
        
        Returns:
            List of results for each week
        """
        logger.info(f"Starting 3-week simulation from {self.SIMULATION_START}")
        self.reset_previous_outputs()
        
        results = []
        for week in range(1, self.TOTAL_WEEKS + 1):
            result = self.run_week(week)
            results.append(result)
        
        logger.info("Simulation complete!")
        return results
