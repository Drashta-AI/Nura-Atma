"""FastAPI backend for patient and clinician app flow (excluding settings endpoints)."""

from datetime import datetime, timedelta
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from mental_health_monitor.config import DB_PATH
from mental_health_monitor.ingestion import QuestionnaireLoader
from mental_health_monitor.database import (
    AgentOutput,
    AppUser,
    ConsentRecord,
    JournalEntry,
    LanguageAgentOutput,
    OverallState,
    PatientAccount,
    QuestionnaireResponse,
    TrackingEvent,
    UserProfile,
    get_session,
    init_database,
)


API_PREFIX = "/v1"
TOKEN_TTL_HOURS = 8
HASH_SALT = "demo-salt-v1"
ANALYTICAL_AGENTS = {"behavioral", "physiological", "context"}
SPECIAL_AGENTS = {"language", "orchestrator"}
SUPPORTED_AGENTS = ANALYTICAL_AGENTS | SPECIAL_AGENTS


app = FastAPI(
    title="Mental Health Monitor Backend",
    version="1.0.0",
    description="Backend API for patient and clinician app flow.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LoginRequest(BaseModel):
    email: str
    password: str
    role: str = Field(pattern="^(patient|clinician)$")


class ConsentRequest(BaseModel):
    accepted: bool
    policy_version: str = "v1"


class ProfileRequest(BaseModel):
    full_name: str
    age: Optional[int] = None


class QuestionnaireRequest(BaseModel):
    responses: Dict[str, Any]


class JournalCreateRequest(BaseModel):
    content: str
    mood: Optional[str] = None


class TrackingStatusRequest(BaseModel):
    status: str = Field(pattern="^(active|paused)$")
    reason: Optional[str] = None


class ChatRequest(BaseModel):
    message: str


class AuthContext(BaseModel):
    token: str
    user_id: int
    role: str


_TOKEN_STORE: Dict[str, Dict[str, Any]] = {}
_CHAT_BY_USER: Dict[int, Any] = {}


def _get_system_questionnaire() -> Dict[str, Any]:
    """Load questionnaire data already present in the system."""
    loader = QuestionnaireLoader()
    return loader.load_questionnaire_data()


def _get_system_questionnaire_questions() -> List[str]:
    """Get only questionnaire questions from system data."""
    questionnaire_data = _get_system_questionnaire()
    return list(questionnaire_data.keys())


def _hash_password(password: str) -> str:
    return sha256((password + HASH_SALT).encode("utf-8")).hexdigest()


def _issue_token(user_id: int, role: str) -> str:
    token = uuid4().hex
    _TOKEN_STORE[token] = {
        "user_id": user_id,
        "role": role,
        "expires_at": datetime.utcnow() + timedelta(hours=TOKEN_TTL_HOURS),
    }
    return token


def _extract_token(authorization: Optional[str]) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid Authorization format")
    return parts[1].strip()


def get_auth_context(authorization: Optional[str] = Header(default=None)) -> AuthContext:
    token = _extract_token(authorization)
    data = _TOKEN_STORE.get(token)
    if not data:
        raise HTTPException(status_code=401, detail="Invalid token")
    if data["expires_at"] < datetime.utcnow():
        _TOKEN_STORE.pop(token, None)
        raise HTTPException(status_code=401, detail="Token expired")

    return AuthContext(token=token, user_id=data["user_id"], role=data["role"])


def require_role(expected_role: str):
    def _checker(ctx: AuthContext = Depends(get_auth_context)) -> AuthContext:
        if ctx.role != expected_role:
            raise HTTPException(status_code=403, detail=f"{expected_role} role required")
        return ctx

    return _checker


def _serialize_analytical_agent(record: AgentOutput) -> Dict[str, Any]:
    return {
        "agent": record.agent_name,
        "week_number": record.week_number,
        "state": record.agent_state,
        "created_at": record.created_at,
        "payload": {
            "metric_states": record.metric_states or {},
            "reasoning": record.reasoning_json or {},
        },
    }


def _serialize_language_agent(record: LanguageAgentOutput) -> Dict[str, Any]:
    return {
        "agent": "language",
        "week_number": record.week_number,
        "state": record.linguistic_state,
        "created_at": record.created_at,
        "payload": {
            "sentiment_score": record.sentiment_score,
            "emotional_shift_summary": record.emotional_shift_summary,
            "reasoning": record.reasoning or {},
        },
    }


def _serialize_orchestrator(record: OverallState) -> Dict[str, Any]:
    return {
        "agent": "orchestrator",
        "week_number": record.week_number,
        "state": record.final_state,
        "created_at": record.created_at,
        "payload": {
            "behavioural_state": record.behavioural_state,
            "physiological_state": record.physiological_state,
            "context_state": record.context_state,
            "language_state": record.language_state,
            "support_message": record.support_message,
            "reasoning": record.orchestrator_reasoning or {},
        },
    }


def _latest_agent_output(session, agent: str) -> Optional[Dict[str, Any]]:
    if agent in ANALYTICAL_AGENTS:
        row = (
            session.query(AgentOutput)
            .filter(AgentOutput.agent_name == agent)
            .order_by(AgentOutput.week_number.desc(), AgentOutput.created_at.desc())
            .first()
        )
        return _serialize_analytical_agent(row) if row else None

    if agent == "language":
        row = (
            session.query(LanguageAgentOutput)
            .order_by(LanguageAgentOutput.week_number.desc(), LanguageAgentOutput.created_at.desc())
            .first()
        )
        return _serialize_language_agent(row) if row else None

    if agent == "orchestrator":
        row = (
            session.query(OverallState)
            .order_by(OverallState.week_number.desc(), OverallState.created_at.desc())
            .first()
        )
        return _serialize_orchestrator(row) if row else None

    return None


def _agent_history(session, agent: str) -> List[Dict[str, Any]]:
    if agent in ANALYTICAL_AGENTS:
        rows = (
            session.query(AgentOutput)
            .filter(AgentOutput.agent_name == agent)
            .order_by(AgentOutput.week_number.asc(), AgentOutput.created_at.asc())
            .all()
        )
        return [_serialize_analytical_agent(row) for row in rows]

    if agent == "language":
        rows = (
            session.query(LanguageAgentOutput)
            .order_by(LanguageAgentOutput.week_number.asc(), LanguageAgentOutput.created_at.asc())
            .all()
        )
        return [_serialize_language_agent(row) for row in rows]

    if agent == "orchestrator":
        rows = (
            session.query(OverallState)
            .order_by(OverallState.week_number.asc(), OverallState.created_at.asc())
            .all()
        )
        return [_serialize_orchestrator(row) for row in rows]

    return []


def _weekly_summary(session) -> List[Dict[str, Any]]:
    states = session.query(OverallState).order_by(OverallState.week_number.asc()).all()
    return [
        {
            "week_number": row.week_number,
            "state": row.final_state,
            "support_message": row.support_message,
            "created_at": row.created_at,
        }
        for row in states
    ]


def _compute_patient_indication(session, patient_id: int) -> str:
    latest = session.query(OverallState).order_by(OverallState.week_number.desc()).first()
    if latest:
        return latest.final_state

    # Fallback so clinician list still renders for demo accounts
    fallback = {0: "normal", 1: "watchful", 2: "elevated"}
    return fallback[patient_id % 3]


def _get_patient_account(session, user_id: int) -> Optional[PatientAccount]:
    return session.query(PatientAccount).filter(PatientAccount.user_id == user_id).first()


def _seed_demo_data() -> None:
    session = get_session()
    try:
        if session.query(AppUser).count() > 0:
            return

        users = [
            AppUser(
                email="patient@example.com",
                password_hash=_hash_password("patient123"),
                role="patient",
                display_name="Kanishk",
            ),
            AppUser(
                email="rahul@example.com",
                password_hash=_hash_password("patient123"),
                role="patient",
                display_name="Rahul",
            ),
            AppUser(
                email="bhargav@example.com",
                password_hash=_hash_password("patient123"),
                role="patient",
                display_name="Bhargav",
            ),
            AppUser(
                email="clinician@example.com",
                password_hash=_hash_password("clinician123"),
                role="clinician",
                display_name="Dr. Meera",
            ),
        ]
        session.add_all(users)
        session.flush()

        patient_accounts = [
            PatientAccount(user_id=users[0].id, full_name="Kanishk", age=22, consent_given=True, onboarding_completed=True),
            PatientAccount(user_id=users[1].id, full_name="Rahul", age=24, consent_given=True, onboarding_completed=True),
            PatientAccount(user_id=users[2].id, full_name="Bhargav", age=23, consent_given=True, onboarding_completed=True),
        ]
        session.add_all(patient_accounts)
        session.flush()

        tracking_events = [
            TrackingEvent(patient_id=patient_accounts[0].id, status="active", reason="Initial setup"),
            TrackingEvent(patient_id=patient_accounts[1].id, status="active", reason="Initial setup"),
            TrackingEvent(patient_id=patient_accounts[2].id, status="active", reason="Initial setup"),
        ]
        session.add_all(tracking_events)
        session.commit()
    finally:
        session.close()


@app.on_event("startup")
def startup_event() -> None:
    init_database(DB_PATH)
    _seed_demo_data()


@app.get("/health")
def health() -> Dict[str, Any]:
    return {"status": "ok", "time": datetime.utcnow()}


@app.post(f"{API_PREFIX}/auth/login")
def login(payload: LoginRequest) -> Dict[str, Any]:
    session = get_session()
    try:
        user = (
            session.query(AppUser)
            .filter(AppUser.email == payload.email, AppUser.role == payload.role)
            .first()
        )
        if not user or user.password_hash != _hash_password(payload.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = _issue_token(user.id, user.role)
        patient = _get_patient_account(session, user.id) if user.role == "patient" else None
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "role": user.role,
                "display_name": user.display_name,
                "patient_id": patient.id if patient else None,
            },
        }
    finally:
        session.close()


@app.get(f"{API_PREFIX}/me")
def me(ctx: AuthContext = Depends(get_auth_context)) -> Dict[str, Any]:
    session = get_session()
    try:
        user = session.query(AppUser).filter(AppUser.id == ctx.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        patient = _get_patient_account(session, user.id) if user.role == "patient" else None
        return {
            "id": user.id,
            "role": user.role,
            "display_name": user.display_name,
            "patient_id": patient.id if patient else None,
        }
    finally:
        session.close()


@app.post(f"{API_PREFIX}/patient/consent")
def set_consent(payload: ConsentRequest, ctx: AuthContext = Depends(require_role("patient"))) -> Dict[str, Any]:
    session = get_session()
    try:
        patient = _get_patient_account(session, ctx.user_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient profile not found")

        record = ConsentRecord(
            patient_id=patient.id,
            policy_version=payload.policy_version,
            accepted=payload.accepted,
        )
        patient.consent_given = payload.accepted
        session.add(record)
        session.commit()
        return {"patient_id": patient.id, "consent_given": patient.consent_given}
    finally:
        session.close()


@app.post(f"{API_PREFIX}/patient/profile")
def upsert_profile(payload: ProfileRequest, ctx: AuthContext = Depends(require_role("patient"))) -> Dict[str, Any]:
    session = get_session()
    try:
        patient = _get_patient_account(session, ctx.user_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient profile not found")

        patient.full_name = payload.full_name
        patient.age = payload.age
        session.commit()
        return {"patient_id": patient.id, "full_name": patient.full_name, "age": patient.age}
    finally:
        session.close()


@app.post(f"{API_PREFIX}/patient/questionnaire")
def submit_questionnaire(payload: QuestionnaireRequest, ctx: AuthContext = Depends(require_role("patient"))) -> Dict[str, Any]:
    session = get_session()
    try:
        patient = _get_patient_account(session, ctx.user_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient profile not found")

        system_questions = set(_get_system_questionnaire_questions())
        invalid_questions = [q for q in payload.responses.keys() if q not in system_questions]
        if invalid_questions:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Some submitted questions are not part of the system questionnaire",
                    "invalid_questions": invalid_questions,
                },
            )

        response = QuestionnaireResponse(patient_id=patient.id, responses_json=payload.responses)
        patient.onboarding_completed = True
        session.add(response)
        session.commit()
        return {
            "patient_id": patient.id,
            "questionnaire_id": response.id,
            "submitted_at": response.submitted_at,
            "onboarding_completed": patient.onboarding_completed,
        }
    finally:
        session.close()


@app.get(f"{API_PREFIX}/patient/questionnaire")
def get_patient_questionnaire(ctx: AuthContext = Depends(require_role("patient"))) -> Dict[str, Any]:
    """Return questionnaire questions already present in the system."""
    session = get_session()
    try:
        patient = _get_patient_account(session, ctx.user_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient profile not found")

        questionnaire_data = _get_system_questionnaire()
        latest_submission = (
            session.query(QuestionnaireResponse)
            .filter(QuestionnaireResponse.patient_id == patient.id)
            .order_by(QuestionnaireResponse.submitted_at.desc())
            .first()
        )

        questions = [
            {
                "id": str(index + 1),
                "question": question,
                "suggested_answer": suggested_answer,
            }
            for index, (question, suggested_answer) in enumerate(questionnaire_data.items())
        ]

        return {
            "patient_id": patient.id,
            "questions": questions,
            "latest_responses": latest_submission.responses_json if latest_submission else {},
        }
    finally:
        session.close()


@app.get(f"{API_PREFIX}/patient/onboarding-status")
def onboarding_status(ctx: AuthContext = Depends(require_role("patient"))) -> Dict[str, Any]:
    session = get_session()
    try:
        patient = _get_patient_account(session, ctx.user_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient profile not found")

        has_questionnaire = (
            session.query(QuestionnaireResponse)
            .filter(QuestionnaireResponse.patient_id == patient.id)
            .count()
            > 0
        )

        return {
            "patient_id": patient.id,
            "consent_given": patient.consent_given,
            "questionnaire_submitted": has_questionnaire,
            "onboarding_completed": False,
        }
    finally:
        session.close()


@app.get(f"{API_PREFIX}/patient/home")
def patient_home(ctx: AuthContext = Depends(require_role("patient"))) -> Dict[str, Any]:
    session = get_session()
    try:
        patient = _get_patient_account(session, ctx.user_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient profile not found")

        latest_overall = _latest_agent_output(session, "orchestrator")
        latest_agents = {agent: _latest_agent_output(session, agent) for agent in sorted(SUPPORTED_AGENTS)}
        weekly = _weekly_summary(session)
        track = (
            session.query(TrackingEvent)
            .filter(TrackingEvent.patient_id == patient.id)
            .order_by(TrackingEvent.created_at.desc())
            .first()
        )

        key_insights = {
            "contextual": latest_agents.get("context"),
            "behavioral": latest_agents.get("behavioral"),
            "wearable": latest_agents.get("physiological"),
            "language": latest_agents.get("language"),
        }

        return {
            "patient": {"id": patient.id, "full_name": patient.full_name, "age": patient.age},
            "indication_level": (latest_overall or {}).get("state", _compute_patient_indication(session, patient.id)),
            "weekly_summary": weekly,
            "key_insights": key_insights,
            "gentle_check_in": (latest_overall or {}).get("payload", {}).get("support_message"),
            "tracking_status": track.status if track else "active",
        }
    finally:
        session.close()


@app.get(f"{API_PREFIX}/patient/weekly-summary")
def patient_weekly_summary(ctx: AuthContext = Depends(require_role("patient"))) -> Dict[str, Any]:
    session = get_session()
    try:
        return {"weeks": _weekly_summary(session)}
    finally:
        session.close()


@app.post(f"{API_PREFIX}/patient/chat")
def patient_chat(payload: ChatRequest, ctx: AuthContext = Depends(require_role("patient"))) -> Dict[str, Any]:
    message = payload.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        from mental_health_monitor.chat import InteractiveChat
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Chat dependencies unavailable: {exc}")

    chat = _CHAT_BY_USER.get(ctx.user_id)
    if chat is None:
        chat = InteractiveChat()
        _CHAT_BY_USER[ctx.user_id] = chat

    reply = chat.chat(message)
    return {
        "reply": reply,
        "latest_state": chat.latest_orchestrator_state,
        "history": chat.get_conversation_history(),
    }


@app.post(f"{API_PREFIX}/patient/journal")
def create_journal(payload: JournalCreateRequest, ctx: AuthContext = Depends(require_role("patient"))) -> Dict[str, Any]:
    if not payload.content.strip():
        raise HTTPException(status_code=400, detail="Journal content cannot be empty")

    session = get_session()
    try:
        patient = _get_patient_account(session, ctx.user_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient profile not found")

        entry = JournalEntry(patient_id=patient.id, content=payload.content.strip(), mood=payload.mood)
        session.add(entry)
        session.commit()
        return {
            "journal_id": entry.id,
            "patient_id": patient.id,
            "content": entry.content,
            "mood": entry.mood,
            "created_at": entry.created_at,
        }
    finally:
        session.close()


@app.get(f"{API_PREFIX}/patient/journal")
def list_journal(ctx: AuthContext = Depends(require_role("patient"))) -> Dict[str, Any]:
    session = get_session()
    try:
        patient = _get_patient_account(session, ctx.user_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient profile not found")

        rows = (
            session.query(JournalEntry)
            .filter(JournalEntry.patient_id == patient.id)
            .order_by(JournalEntry.created_at.desc())
            .all()
        )

        return {
            "entries": [
                {
                    "id": row.id,
                    "content": row.content,
                    "mood": row.mood,
                    "created_at": row.created_at,
                }
                for row in rows
            ]
        }
    finally:
        session.close()


@app.patch(f"{API_PREFIX}/patient/tracking-status")
def update_tracking_status(payload: TrackingStatusRequest, ctx: AuthContext = Depends(require_role("patient"))) -> Dict[str, Any]:
    session = get_session()
    try:
        patient = _get_patient_account(session, ctx.user_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient profile not found")

        event = TrackingEvent(patient_id=patient.id, status=payload.status, reason=payload.reason)
        session.add(event)
        session.commit()
        return {
            "patient_id": patient.id,
            "status": payload.status,
            "reason": payload.reason,
            "updated_at": event.created_at,
        }
    finally:
        session.close()


@app.get(f"{API_PREFIX}/patient/agents/latest")
def patient_agents_latest(ctx: AuthContext = Depends(require_role("patient"))) -> Dict[str, Any]:
    session = get_session()
    try:
        return {agent: _latest_agent_output(session, agent) for agent in sorted(SUPPORTED_AGENTS)}
    finally:
        session.close()


@app.get(f"{API_PREFIX}/patient/agents/{{agent}}/latest")
def patient_agent_latest(agent: str, ctx: AuthContext = Depends(require_role("patient"))) -> Dict[str, Any]:
    normalized = agent.strip().lower()
    if normalized not in SUPPORTED_AGENTS:
        raise HTTPException(status_code=404, detail=f"Unsupported agent '{agent}'")

    session = get_session()
    try:
        out = _latest_agent_output(session, normalized)
        if out is None:
            raise HTTPException(status_code=404, detail=f"No output for agent '{agent}'")
        return out
    finally:
        session.close()


@app.get(f"{API_PREFIX}/patient/agents/{{agent}}/history")
def patient_agent_history(agent: str, ctx: AuthContext = Depends(require_role("patient"))) -> Dict[str, Any]:
    normalized = agent.strip().lower()
    if normalized not in SUPPORTED_AGENTS:
        raise HTTPException(status_code=404, detail=f"Unsupported agent '{agent}'")

    session = get_session()
    try:
        return {"agent": normalized, "history": _agent_history(session, normalized)}
    finally:
        session.close()


@app.get(f"{API_PREFIX}/clinician/patients")
def clinician_patients(ctx: AuthContext = Depends(require_role("clinician"))) -> Dict[str, Any]:
    session = get_session()
    try:
        patients = session.query(PatientAccount).order_by(PatientAccount.id.asc()).all()
        return {
            "patients": [
                {
                    "patient_id": row.id,
                    "full_name": row.full_name,
                    "age": row.age,
                    "indication_level": _compute_patient_indication(session, row.id),
                }
                for row in patients
            ]
        }
    finally:
        session.close()


@app.get(f"{API_PREFIX}/clinician/patients/{{patient_id}}/overview")
def clinician_patient_overview(patient_id: int, ctx: AuthContext = Depends(require_role("clinician"))) -> Dict[str, Any]:
    session = get_session()
    try:
        patient = session.query(PatientAccount).filter(PatientAccount.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        latest_overall = _latest_agent_output(session, "orchestrator")
        return {
            "patient": {"id": patient.id, "full_name": patient.full_name, "age": patient.age},
            "indication_level": _compute_patient_indication(session, patient.id),
            "weekly_summary": _weekly_summary(session),
            "profile": {
                "consent_given": patient.consent_given,
                "onboarding_completed": patient.onboarding_completed,
            },
            "orchestrator": latest_overall,
        }
    finally:
        session.close()


@app.get(f"{API_PREFIX}/clinician/patients/{{patient_id}}/agents/latest")
def clinician_agents_latest(patient_id: int, ctx: AuthContext = Depends(require_role("clinician"))) -> Dict[str, Any]:
    session = get_session()
    try:
        patient = session.query(PatientAccount).filter(PatientAccount.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        return {
            "patient_id": patient_id,
            "agents": {agent: _latest_agent_output(session, agent) for agent in sorted(SUPPORTED_AGENTS)},
        }
    finally:
        session.close()


@app.get(f"{API_PREFIX}/clinician/patients/{{patient_id}}/agents/{{agent}}/history")
def clinician_agent_history(patient_id: int, agent: str, ctx: AuthContext = Depends(require_role("clinician"))) -> Dict[str, Any]:
    normalized = agent.strip().lower()
    if normalized not in SUPPORTED_AGENTS:
        raise HTTPException(status_code=404, detail=f"Unsupported agent '{agent}'")

    session = get_session()
    try:
        patient = session.query(PatientAccount).filter(PatientAccount.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        return {
            "patient_id": patient_id,
            "agent": normalized,
            "history": _agent_history(session, normalized),
        }
    finally:
        session.close()


@app.get(f"{API_PREFIX}/reports")
def list_reports(ctx: AuthContext = Depends(get_auth_context)) -> Dict[str, Any]:
    report_dir = Path("weekly_reports")
    if not report_dir.exists():
        return {"reports": []}

    reports = sorted(report_dir.glob("week_*_report.md"))
    return {
        "reports": [
            {
                "name": report.name,
                "path": str(report.as_posix()),
                "modified_at": datetime.fromtimestamp(report.stat().st_mtime),
            }
            for report in reports
        ]
    }


@app.get(f"{API_PREFIX}/reports/{{week_number}}")
def get_report(week_number: int, ctx: AuthContext = Depends(get_auth_context)) -> Dict[str, Any]:
    report_path = Path("weekly_reports") / f"week_{week_number}_report.md"
    if not report_path.exists():
        raise HTTPException(status_code=404, detail=f"Report not found for week {week_number}")

    return {
        "week_number": week_number,
        "name": report_path.name,
        "content": report_path.read_text(encoding="utf-8"),
    }


@app.post(f"{API_PREFIX}/auth/logout")
def logout(ctx: AuthContext = Depends(get_auth_context)) -> Dict[str, Any]:
    _TOKEN_STORE.pop(ctx.token, None)
    return {"ok": True}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)
