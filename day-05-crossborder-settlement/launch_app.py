#!/usr/bin/env python3
"""
Cross-Border Settlement Platform Launcher
Properly sets up Python path and launches the Streamlit app
"""

import sys
import os
import subprocess

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Change to the project directory
os.chdir(current_dir)

# Launch Streamlit with proper environment
if __name__ == "__main__":
    print("🚀 Starting Cross-Border Settlement Platform...")
    print(f"📁 Working directory: {current_dir}")
    print(f"🐍 Python path includes: {current_dir}")
    print("🌐 Access the app at: http://localhost:8505")
    print("=" * 50)

    try:
        # Run streamlit with the correct working directory
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            "ui/app.py", "--server.port", "8505"
        ], cwd=current_dir)
    except KeyboardInterrupt:
        print("\n👋 Shutting down platform...")
    except Exception as e:
        print(f"❌ Error starting platform: {e}")
