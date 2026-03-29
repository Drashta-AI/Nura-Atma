"""LangGraph state models for the orchestration pipeline."""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List, Annotated
from datetime import datetime
from operator import add


class GraphState(BaseModel):
    """Complete state for the LangGraph pipeline."""
    
    # Week tracking
    week_number: int
    start_date: datetime
    
    # Character and baseline
    character_sketch: Optional[Dict[str, Any]] = None
    baseline_metrics: Optional[Dict[str, float]] = None
    
    # Weekly data
    weekly_metrics: Optional[Dict[str, tuple]] = None  # metric_name -> (value, pct_change)
    
    # Metric states from threshold engines
    behavioral_metric_states: Optional[Dict[str, Any]] = None
    physiological_metric_states: Optional[Dict[str, Any]] = None
    context_metric_states: Optional[Dict[str, Any]] = None
    
    # Aggregated chat messages for language analysis
    weekly_messages: Optional[str] = None
    
    # Agent outputs
    behavioral_agent_output: Optional[Dict[str, Any]] = None
    physiological_agent_output: Optional[Dict[str, Any]] = None
    context_agent_output: Optional[Dict[str, Any]] = None
    language_agent_output: Optional[Dict[str, Any]] = None
    
    # Orchestration
    orchestrator_output: Optional[Dict[str, Any]] = None
    overall_state: Optional[str] = None  # normal, watchful, elevated
    
    # Conversational support
    conversational_message: Optional[str] = None
    
    # Metadata - use Annotated with list reducer for concurrent updates
    processed_agents: Annotated[List[str], add] = Field(default_factory=list)
    errors: Annotated[List[str], add] = Field(default_factory=list)


class AgentInput(BaseModel):
    """Input for analytical agents."""
    week_number: int
    character_sketch: Dict[str, Any]
    baseline_metrics: Dict[str, float]
    metric_states: Dict[str, Any]
    weekly_metrics: Optional[Dict[str, tuple]] = None
    messages: Optional[str] = None
