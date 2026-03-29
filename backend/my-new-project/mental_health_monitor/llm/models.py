"""Pydantic models for structured agent outputs."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class CharacterSketch(BaseModel):
    """Character sketch generated from questionnaire."""
    personality_summary: str
    coping_style: str
    stress_sensitivity: str  # low, moderate, high
    social_dependency: str  # low, moderate, high
    motivational_style: str


class MetricAnalysis(BaseModel):
    """Analysis of a single metric."""
    metric_name: str
    value: float
    baseline: float
    pct_change: Optional[float] = None
    state: str  # normal, watchful, elevated
    reasoning: str


class BehavioralAgentOutput(BaseModel):
    """Output from behavioral signal agent."""
    overall_state: str  # normal, watchful, elevated
    metric_summary: Dict[str, str]
    implications: str
    recommendations: Optional[str] = None
    reasoning: str
    processed_at: datetime = Field(default_factory=datetime.utcnow)


class PhysiologicalAgentOutput(BaseModel):
    """Output from physiological/energy agent."""
    overall_state: str  # normal, watchful, elevated
    energy_assessment: str
    sleep_quality: str
    implications: str
    recommendations: Optional[str] = None
    reasoning: str
    processed_at: datetime = Field(default_factory=datetime.utcnow)


class ContextAgentOutput(BaseModel):
    """Output from context & environment agent."""
    overall_state: str  # normal, watchful, elevated
    mobility_assessment: str
    location_assessment: str
    environmental_implications: str
    recommendations: Optional[str] = None
    reasoning: str
    processed_at: datetime = Field(default_factory=datetime.utcnow)


class LanguageAgentOutput(BaseModel):
    """Output from language & expression agent."""
    state: str  # normal, watchful, elevated
    sentiment_score: float = Field(ge=-1.0, le=1.0)
    emotional_shift_summary: str
    tone_observations: str
    reasoning: str
    processed_at: datetime = Field(default_factory=datetime.utcnow)


class OrchestratorOutput(BaseModel):
    """Output from central orchestrator agent."""
    overall_state: str  # normal, watchful, elevated
    integrated_analysis: str
    primary_concerns: List[str]
    support_level: str  # minimal, moderate, active
    reasoning: str
    processed_at: datetime = Field(default_factory=datetime.utcnow)


class ConversationalAgentOutput(BaseModel):
    """Output from conversational support agent."""
    message: str
    tone: str
    includes_support_system_reference: bool = False
    processed_at: datetime = Field(default_factory=datetime.utcnow)
