#!/bin/bash

# Check for syntax errors before building Docker image
echo "Checking for Python syntax errors..."
find . -name "*.py" -exec python -m py_compile {} \; 2>/dev/null

if [ $? -ne 0 ]; then
    echo "❌ Syntax errors detected. Please fix them before running Docker."
    echo "Run python -m py_compile *.py to identify the specific errors."
    exit 1
else
    echo "✅ No Python syntax errors detected."
fi

# Build the Docker image
echo "Building Docker image..."
docker build -t algorithmic-trading-platform .

# Run the Docker container
echo "Running Docker container..."
docker run -p 8501:8501 algorithmic-trading-platform

# Instructions
echo ""
echo "Access the application at http://localhost:8501"
echo "Press Ctrl+C to stop the container"
