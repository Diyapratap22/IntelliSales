"""Launcher for the legacy Streamlit dashboard.

Run with:
    python -m app.streamlit_runner
or:
    streamlit run app/streamlit_dashboard.py
"""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_FILE = Path(__file__).resolve().parent / "streamlit_dashboard.py"


def main() -> None:
    """Start the preserved Streamlit dashboard."""

    command = [sys.executable, "-m", "streamlit", "run", str(DASHBOARD_FILE)]

    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


if __name__ == "__main__":
    main()