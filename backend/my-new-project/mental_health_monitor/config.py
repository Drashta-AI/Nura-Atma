"""Configuration module for mental health monitoring system."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT.parent / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
BEHAVIOUR_SIGNAL_DATA = PROJECT_ROOT.parent / "behaviour_signal_data"
WEARABLE_DATA = PROJECT_ROOT.parent / "wearble_data"
WIFI_DATA = PROJECT_ROOT.parent / "wifi_data"
CONVERSATION_DATA = PROJECT_ROOT.parent / "conversation_data"

# Database
DB_PATH = os.getenv("DB_PATH", "mental_health_monitor.db")

# LLM
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))

# Simulation
SIMULATION_START_DATE = "2013-04-20"
BASELINE_START_DATE = "2013-03-28"
BASELINE_END_DATE = "2013-04-03"
TOTAL_WEEKS = 3

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "mental_health_monitor.log")

def validate_configuration():
    """Validate required configuration.
    
    Raises:
        ValueError: If required configuration is missing
    """
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY environment variable not set")
    
    # Check data directories exist
    for data_dir in [BEHAVIOUR_SIGNAL_DATA, WEARABLE_DATA, WIFI_DATA, CONVERSATION_DATA]:
        if not data_dir.exists():
            print(f"Warning: Data directory not found: {data_dir}")
