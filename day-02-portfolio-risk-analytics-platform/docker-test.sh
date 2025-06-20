#!/bin/bash

# Build the Docker image
echo "Building Docker image..."
docker build -t portfolio-risk-analytics .

# Run the Docker container
echo "Running Docker container..."
docker run -p 8501:8501 portfolio-risk-analytics

# Instructions
echo ""
echo "Access the application at http://localhost:8501"
echo "Press Ctrl+C to stop the container"
