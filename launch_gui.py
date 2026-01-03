#!/usr/bin/env python3
"""
Launcher script for RAG Application GUI.

This script launches the Streamlit web interface with proper process management.
"""

import atexit
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

# Global process reference for cleanup
streamlit_process = None


def cleanup():
    """Clean up the Streamlit process and all children."""
    global streamlit_process

    if streamlit_process is None:
        return

    print("\nShutting down RAG Application...")

    try:
        # Get the process group to kill all children
        if hasattr(os, "killpg"):
            # Unix-like systems: kill process group
            try:
                os.killpg(os.getpgid(streamlit_process.pid), signal.SIGTERM)
                # Wait a bit for graceful shutdown
                time.sleep(1)
                # Force kill if still running
                try:
                    os.killpg(os.getpgid(streamlit_process.pid), signal.SIGKILL)
                except ProcessLookupError:
                    pass  # Already terminated
            except ProcessLookupError:
                pass  # Process already gone
        else:
            # Windows: terminate the process tree
            streamlit_process.terminate()
            try:
                streamlit_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                streamlit_process.kill()

    except Exception as e:
        print(f"Error during cleanup: {e}")
    finally:
        streamlit_process = None


def signal_handler(signum, frame):  # noqa: ARG001
    """Handle shutdown signals."""
    cleanup()
    sys.exit(0)


def main():
    """Launch the Streamlit web interface."""
    global streamlit_process

    # Register cleanup handlers
    atexit.register(cleanup)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Get the directory containing this script
    app_dir = Path(__file__).parent

    # Path to streamlit_app.py
    streamlit_app = app_dir / "streamlit_app.py"

    if not streamlit_app.exists():
        print(f"Error: Could not find {streamlit_app}")
        sys.exit(1)

    # Launch Streamlit with proper process management
    try:
        print("Starting RAG Application...")

        # Create new process group on Unix-like systems
        kwargs = {"cwd": str(app_dir)}
        if hasattr(os, "setpgrp"):
            kwargs["preexec_fn"] = os.setpgrp

        streamlit_process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", str(streamlit_app),
             "--server.headless", "true",
             "--browser.gatherUsageStats", "false"],
            **kwargs,
        )

        print(f"Streamlit server started (PID: {streamlit_process.pid})")
        print("Opening browser to http://localhost:8501")
        print("Press Ctrl+C to stop the server\n")

        # Wait for process to complete
        streamlit_process.wait()

    except KeyboardInterrupt:
        cleanup()
        sys.exit(0)
    except Exception as e:
        print(f"Error launching application: {e}")
        cleanup()
        sys.exit(1)


if __name__ == "__main__":
    main()
