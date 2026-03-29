"""Database models for mental health monitoring system."""

from datetime import datetime
from typing import Optional
import json
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class UserProfile(Base):
    """User profile with character sketch."""
    __tablename__ = "user_profile"
    
    id = Column(Integer, primary_key=True)
    character_sketch_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<UserProfile(id={self.id}, created_at={self.created_at})>"


class BaselineMetrics(Base):
    """Baseline metrics computed from 28-03-2013 to 03-04-2013."""
    __tablename__ = "baseline_metrics"
    
    id = Column(Integer, primary_key=True)
    metric_name = Column(String(255), nullable=False, unique=True)
    baseline_value = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<BaselineMetrics(metric_name={self.metric_name}, value={self.baseline_value})>"


class WeeklyMetrics(Base):
    """Weekly aggregated metrics."""
    __tablename__ = "weekly_metrics"
    
    id = Column(Integer, primary_key=True)
    week_number = Column(Integer, nullable=False)
    metric_name = Column(String(255), nullable=False)
    avg_value = Column(Float, nullable=False)
    pct_change = Column(Float)  # Percentage change vs baseline
    duration_consecutive_days = Column(Integer, default=0)  # For state tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<WeeklyMetrics(week={self.week_number}, metric={self.metric_name}, value={self.avg_value})>"


class AgentOutput(Base):
    """Output from behavioral, physiological, and context agents."""
    __tablename__ = "agent_outputs"
    
    id = Column(Integer, primary_key=True)
    week_number = Column(Integer, nullable=False)
    agent_name = Column(String(255), nullable=False)  # behavioral, physiological, context
    agent_state = Column(String(50), nullable=False)  # normal, watchful, elevated
    metric_states = Column(JSON)  # Individual metric states
    reasoning_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<AgentOutput(week={self.week_number}, agent={self.agent_name}, state={self.agent_state})>"


class LanguageAgentOutput(Base):
    """Output from language & expression agent."""
    __tablename__ = "language_agent_outputs"
    
    id = Column(Integer, primary_key=True)
    week_number = Column(Integer, nullable=False)
    linguistic_state = Column(String(50), nullable=False)  # normal, watchful, elevated
    sentiment_score = Column(Float)  # -1 to 1
    emotional_shift_summary = Column(Text)
    reasoning = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<LanguageAgentOutput(week={self.week_number}, state={self.linguistic_state})>"


class OverallState(Base):
    """Overall system state after orchestrator synthesis."""
    __tablename__ = "overall_state"
    
    id = Column(Integer, primary_key=True)
    week_number = Column(Integer, nullable=False)
    final_state = Column(String(50), nullable=False)  # normal, watchful, elevated
    behavioural_state = Column(String(50))
    physiological_state = Column(String(50))
    context_state = Column(String(50))
    language_state = Column(String(50))
    support_message = Column(Text)
    orchestrator_reasoning = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<OverallState(week={self.week_number}, state={self.final_state})>"


class AppUser(Base):
    """Application user for patient/clinician login."""
    __tablename__ = "app_users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # patient | clinician
    display_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AppUser(id={self.id}, role={self.role}, email={self.email})>"


class PatientAccount(Base):
    """Patient account profile for app onboarding and clinician view."""
    __tablename__ = "patient_accounts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("app_users.id"), nullable=False, unique=True)
    full_name = Column(String(255), nullable=False)
    age = Column(Integer)
    consent_given = Column(Boolean, default=False)
    onboarding_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<PatientAccount(id={self.id}, user_id={self.user_id}, name={self.full_name})>"


class ConsentRecord(Base):
    """Consent records for privacy/data usage agreement."""
    __tablename__ = "consent_records"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patient_accounts.id"), nullable=False)
    policy_version = Column(String(50), nullable=False)
    accepted = Column(Boolean, nullable=False)
    accepted_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ConsentRecord(patient_id={self.patient_id}, accepted={self.accepted})>"


class QuestionnaireResponse(Base):
    """Stored questionnaire responses submitted during onboarding."""
    __tablename__ = "questionnaire_responses"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patient_accounts.id"), nullable=False)
    responses_json = Column(JSON, nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<QuestionnaireResponse(patient_id={self.patient_id}, id={self.id})>"


class JournalEntry(Base):
    """Patient in-app journaling entries."""
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patient_accounts.id"), nullable=False)
    content = Column(Text, nullable=False)
    mood = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<JournalEntry(id={self.id}, patient_id={self.patient_id})>"


class TrackingEvent(Base):
    """Tracking state events for patient journey (active/paused)."""
    __tablename__ = "tracking_events"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patient_accounts.id"), nullable=False)
    status = Column(String(50), nullable=False)  # active | paused
    reason = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<TrackingEvent(patient_id={self.patient_id}, status={self.status})>"
