#!/usr/bin/env python3
"""
Launcher script for RAG Application GUI.

This script launches the Streamlit web interface.
"""

import sys
import subprocess
from pathlib import Path


def main():
    """Launch the Streamlit web interface."""
    # Get the directory containing this script
    app_dir = Path(__file__).parent

    # Path to streamlit_app.py
    streamlit_app = app_dir / "streamlit_app.py"

    if not streamlit_app.exists():
        print(f"Error: Could not find {streamlit_app}")
        sys.exit(1)

    # Launch Streamlit
    try:
        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", str(streamlit_app)],
            cwd=str(app_dir),
        )
    except KeyboardInterrupt:
        print("\nShutting down RAG Application...")
        sys.exit(0)
    except Exception as e:
        print(f"Error launching application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
