"""
Centralized Configuration for the Test Automation Framework.
Allows overrides via environment variables for CI/CD and local environments.
"""

import os
from pathlib import Path

# Workspace root
WORKSPACE_DIR = Path(__file__).resolve().parent.parent.parent

# Application URL
BASE_URL = os.environ.get("APP_BASE_URL", "http://127.0.0.1:5000")

# Database Path
DB_PATH = WORKSPACE_DIR / "database" / "social_dashboard.db"

# Browser & Test Settings
HEADLESS = os.environ.get("HEADLESS", "true").lower() in ("true", "1", "yes")
BROWSER_TYPE = os.environ.get("BROWSER_TYPE", "chromium")
SLOW_MO = int(os.environ.get("SLOW_MO", "0"))
DEFAULT_TIMEOUT = int(os.environ.get("DEFAULT_TIMEOUT", "10000"))  # ms

# Artifacts & Reporting
REPORTS_DIR = WORKSPACE_DIR / "reports"
SCREENSHOTS_DIR = REPORTS_DIR / "screenshots"

# Ensure output directories exist
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
