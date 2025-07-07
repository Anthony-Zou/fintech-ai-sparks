# MCP Financial Intelligence Platform Dockerfile
# Multi-stage build for optimized production deployment

# Stage 1: Base Python environment
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    MCP_SERVER_NAME=financial-intelligence \
    LOG_LEVEL=INFO

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory and user
RUN groupadd -r mcpuser && useradd -r -g mcpuser mcpuser
WORKDIR /app

# Stage 2: Dependencies installation
FROM base as dependencies

# Copy dependency files
COPY requirements.txt pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 3: Application build
FROM dependencies as application

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs data && \
    chown -R mcpuser:mcpuser /app

# Stage 4: Production image
FROM application as production

# Switch to non-root user
USER mcpuser

# Expose ports
EXPOSE 8000 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command (can be overridden)
CMD ["python", "-m", "mcp_server.main"]

# Stage 5: Development image
FROM application as development

# Install development dependencies
USER root
RUN pip install --no-cache-dir \
    pytest \
    pytest-asyncio \
    black \
    isort \
    flake8 \
    mypy \
    jupyter

# Switch back to mcpuser
USER mcpuser

# Default command for development
CMD ["python", "-m", "mcp_server.main", "--reload"] 