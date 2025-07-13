#!/bin/bash

# Cross-Border Settlement Platform Startup Script
# This script activates the virtual environment and runs the Streamlit app

echo "🚀 Starting Cross-Border Settlement Platform..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please create one first:"
    echo "python -m venv .venv"
    echo "source .venv/bin/activate"
    echo "pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Check if requirements are installed
if ! python -c "import streamlit" 2>/dev/null; then
    echo "📦 Installing requirements..."
    pip install -r requirements.txt
fi

# Set PYTHONPATH to include the current directory
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run the Streamlit app
echo "🌐 Starting Streamlit app on port 8505..."
echo "📱 Open your browser to: http://localhost:8505"
echo "🛑 Press Ctrl+C to stop the application"

streamlit run ui/app.py --server.port 8505 