FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

# Changed from app.py to app_fixed.py to use the fixed version of the application
CMD ["streamlit", "run", "app_fixed.py", "--server.address", "0.0.0.0"]
