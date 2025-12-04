# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set PYTHONPATH to include the app directory so Python can find modules
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ /app/

# Create directory for FAISS data
RUN mkdir -p /app/data/faiss

# Expose port (Render will set PORT env var, default to 8000)
EXPOSE 8000

# Start server (migrations run in Pre-Deploy Command on Render)
# Use PORT env var from Render, fallback to 8000 for local development
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]


