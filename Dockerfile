# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install gcc for cryptography/bcrypt wheel compilation on some platforms
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend and frontend code
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Set working directory to backend
WORKDIR /app/backend

# Create uploads and exports directories
RUN mkdir -p uploads exports

# Expose port
EXPOSE 8000

# Start the server (Railway injects $PORT automatically)
CMD uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}
