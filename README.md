
# NURA WELLNESS APP

This project is a **multi-agent mental health monitoring system** that combines behavioral, wearable, Wi-Fi context, questionnaire, and conversational signals to produce **weekly risk-state assessments and supportive responses**.

It is built using:

* **Backend:** Python, FastAPI, LangChain, LangGraph, SQLite
* **Frontend:** Modern web UI (Vite-based development server)

The system:

* Loads multi-modal data from Excel/CSV files
* Computes baseline metrics and weekly changes
* Applies deterministic threshold logic
* Uses LLM-backed agents for reasoning
* Synthesizes outputs into an overall mental state
* Stores results and generates reports
* Exposes APIs for frontend interaction

---

# 📁 Project Structure

```
NURA_WELLNESS_APP/
│── frontend/   # Frontend application (UI)
│── backend/    # Backend API + multi-agent system
```

---

# 🧠 Backend Overview

The backend is a **multi-agent mental health monitoring system** built with:

* FastAPI
* LangChain + LangGraph
* SQLite
* LLM-based reasoning (via Groq)

It processes behavioral, wearable, Wi-Fi, and conversational data to generate **weekly mental health risk assessments and insights**.

---

## ⚙️ Backend Setup

Navigate to backend:

```bash
cd backend
```

### 1. Create virtual environment

```bash
python -m venv .venv
```

Activate:

**Windows (PowerShell):**

```powershell
.\.venv\Scripts\Activate.ps1
```

---

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 3. Configure environment

Create a `.env` file inside `backend/`:

```env
GROQ_API_KEY=your_groq_api_key
LLM_MODEL=llama-3.3-70b-versatile
LLM_TEMPERATURE=0.7
DB_PATH=mental_health_monitor.db
LOG_LEVEL=INFO
LOG_FILE=mental_health_monitor.log
```

---

## ▶️ Running Backend

### Run simulation (recommended first)

```bash
python main.py
```

### Start API server

```bash
python api_server.py
```

Or:

```bash
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🔌 API Details

* Base URL: `http://localhost:8000`
* Health Check: `/health`
* API Prefix: `/v1`
* Login: `/v1/auth/login`

### Demo Users

* Patient: `patient@example.com / patient123`
* Patient: `rahul@example.com / patient123`
* Patient: `bhargav@example.com / patient123`
* Clinician: `clinician@example.com / clinician123`

---

## 📊 Backend Features

* Multi-modal data ingestion (Excel/CSV)
* Baseline + weekly behavioral analysis
* Deterministic threshold engines
* LLM-powered agent reasoning
* Weekly risk state generation
* SQLite persistence
* Markdown report generation
* Interactive chat support

---

## 📂 Required Data (Backend)

Ensure these folders exist inside `backend/`:

* `behaviour_signal_data/`
* `wearble_data/`
* `wifi_data/`
* `conversation_data/`

---

# 🎨 Frontend Overview

The frontend is a development server-based UI that connects to the backend API.

---

## ⚙️ Frontend Setup

Navigate to frontend:

```bash
cd frontend
```

### Install dependencies

```bash
npm install
```

---

## ▶️ Running Frontend

```bash
npm run dev
```

Open browser:

```
http://localhost:5173
```

---

# 🔄 Recommended Startup Order

For full functionality:

1. Start backend simulation:

   ```bash
   cd backend
   python main.py
   ```

2. Start backend API:

   ```bash
   python api_server.py
   ```

3. Start frontend:

   ```bash
   cd ../frontend
   npm run dev
   ```

---

# 🔗 Full System Flow

1. Backend ingests multi-modal data
2. Computes baseline + weekly changes
3. Applies threshold-based state detection
4. LLM agents analyze signals
5. Orchestrator generates final mental state
6. API exposes results
7. Frontend visualizes insights

---

# ⚠️ Troubleshooting

### Missing API key

```
GROQ_API_KEY environment variable not set
```

➡️ Add it to `.env`

---

### Missing data files

➡️ Ensure required Excel/CSV files exist

---

### Database errors

```
Database not initialized
```

➡️ Run:

```bash
python main.py
```

---

# ⚠️ Disclaimer

This is a **research/demo system** and not a medical diagnostic tool.
