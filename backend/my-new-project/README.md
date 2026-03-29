# Mental Health Behavioral Monitoring System

This project is a multi-agent mental health monitoring demo built with Python, LangChain, LangGraph, FastAPI, and SQLite. It combines behavioral, wearable, Wi-Fi context, questionnaire, and conversational signals to produce weekly risk-state assessments and supportive responses.

## What This Codebase Does

- Loads multi-modal data from Excel/CSV files.
- Computes baseline metrics and weekly metric changes.
- Applies deterministic threshold logic in Python to derive per-domain states.
- Uses LLM-backed agents for reasoning over precomputed signals.
- Synthesizes domain outputs into an orchestrated weekly overall state.
- Persists all outputs to SQLite and generates markdown reports.
- Exposes an API backend for patient/clinician flows.

## Verified Runtime Requirements

These requirements are verified from `pyproject.toml`, `requirements.txt`, and runtime imports.

- Python 3.11 or newer.
- pip and virtual environment support.
- A valid `GROQ_API_KEY` environment variable for LLM-backed paths.
- Dependencies (from `requirements.txt`):
  - langchain
  - langgraph
  - langchain-groq
  - pydantic
  - pandas
  - openpyxl
  - python-dotenv
  - sqlalchemy
  - fastapi
  - uvicorn

## Required Data Inputs

The project expects these top-level folders (relative to the project root):

- `behaviour_signal_data/`
- `wearble_data/`
- `wifi_data/`
- `conversation_data/`

Expected files:

- `behaviour_signal_data/Call_Count_Context_Agent.xlsx`
- `behaviour_signal_data/conversation_duration_progressive.xlsx`
- `behaviour_signal_data/screen_time_progressive.xlsx`
- `behaviour_signal_data/app_balance_index_2013-03-28_to_2013-05-26.xlsx`
- `wearble_data/exercise_steps_inference.xlsx`
- `wearble_data/date_and_sleep_hours.xlsx`
- `wifi_data/DUWC_Context_Environment_Agent.xlsx`
- `wifi_data/wifi_location_dominance.xlsx`
- `conversation_data/mental_health_chat_data.csv`

Note: The directory name is `wearble_data` in code and workspace (spelling is intentional for compatibility).

## Project Layout

```
my-new-project/
  main.py                    # Full simulation orchestrator entrypoint
  simulator.py               # Simulation-only runner
  interactive_mode.py        # Terminal chat UI (uses same DB)
  api_server.py              # FastAPI backend entrypoint
  requirements.txt
  pyproject.toml
  mental_health_monitor/
    main.py                  # Core orchestration logic
    config.py                # Env and path config + validation
    database/                # SQLAlchemy models and sessions
    ingestion/               # Data loading, baseline, weekly windows, thresholds
    graph/                   # LangGraph state and nodes
    llm/                     # LLM factory, prompts, response models
    scheduler/               # Weekly simulation loop
    chat/                    # Interactive conversational support
    reports.py               # Weekly markdown report generation
```

## Configuration

Create a `.env` file in `my-new-project/`:

```env
GROQ_API_KEY=your_groq_api_key
LLM_MODEL=llama-3.3-70b-versatile
LLM_TEMPERATURE=0.7
DB_PATH=mental_health_monitor.db
LOG_LEVEL=INFO
LOG_FILE=mental_health_monitor.log
```

Notes:

- `GROQ_API_KEY` is required by `validate_configuration()` for simulation/chat flows.
- API startup itself initializes the database and demo users even before simulation is run.

## Setup

From `my-new-project/`:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## How To Start The Simulation

Runs character sketch generation, baseline setup, 3-week simulation, and result export.

```bash
python main.py
```

Outputs:

- `mental_health_monitor.db`
- `mental_health_monitor.log`
- `simulation_results.json`
- `weekly_reports/week_*_report.md`

Alternative simulation-only runner:

```bash
python simulator.py
```

## How To Start The Backend API

From `my-new-project/`:

```bash
python api_server.py
```

Alternative:

```bash
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

API basics:

- Health check: `GET /health`
- API prefix: `/v1`
- Auth endpoint: `POST /v1/auth/login`

Demo users seeded on startup:

- Patient: `patient@example.com` / `patient123`
- Patient: `rahul@example.com` / `patient123`
- Patient: `bhargav@example.com` / `patient123`
- Clinician: `clinician@example.com` / `clinician123`

## Recommended Startup Order

If you want realistic API data for dashboards/history:

1. Start simulation (`python main.py` or `python simulator.py`).
2. Start backend API (`python api_server.py`).

If you start backend first, it still works with seeded demo accounts but has limited monitoring history until simulation runs.

## Agent Flow (High Level)

1. Ingestion loads behavioral, wearable, Wi-Fi, and conversation sources.
2. Baseline engine computes 7-day baseline.
3. Weekly window engine computes weekly aggregates and deltas.
4. Threshold engines assign deterministic states per domain.
5. Parallel analytical agents reason over the computed signals.
6. Orchestrator fuses outputs into final weekly state.
7. Support layer generates human-facing, non-diagnostic guidance.
8. Database and weekly markdown reports are updated.

## Development Notes

- Deterministic metric-state assignment lives in `mental_health_monitor/ingestion/threshold_engines.py`.
- Simulation scheduling logic lives in `mental_health_monitor/scheduler/weekly_simulator.py`.
- FastAPI endpoints are in `api_server.py`.
- Database models and session lifecycle are in `mental_health_monitor/database/`.

## Troubleshooting

- Error: `GROQ_API_KEY environment variable not set`
  - Add `GROQ_API_KEY` to `.env` and restart the process.
- Missing Excel/CSV data errors
  - Ensure required files exist in the folders listed above.
- `Database not initialized. Call init_database() first.`
  - Run through the provided entrypoints (`main.py`, `simulator.py`, `interactive_mode.py`, `api_server.py`) rather than importing internal modules directly.

## Disclaimer

This is a research/demo system and not a medical diagnostic tool.
