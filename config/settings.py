"""Central configuration. Override any value with an environment variable."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Leave LMS_BASE_URL unset to auto-start the bundled mock LMS on a free port.
# Set it (e.g. https://lms.example.com) to run the suite against a real LMS.
BASE_URL = os.getenv("LMS_BASE_URL") or None

HEADLESS = os.getenv("HEADLESS", "true").lower() != "false"
BROWSER = os.getenv("BROWSER", "chromium")          # chromium | firefox | webkit
SLOW_MO = int(os.getenv("SLOW_MO", "0"))            # ms between actions (debugging)
DEFAULT_TIMEOUT_MS = int(os.getenv("DEFAULT_TIMEOUT_MS", "7000"))

DATA_FILE = ROOT / "data" / "test_data.json"
REPORT_DIR = ROOT / "reports"
SCREENSHOT_DIR = ROOT / "screenshots"
