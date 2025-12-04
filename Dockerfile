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

# Make startup script executable
RUN chmod +x /app/start_server.py

# Expose port (Render will set PORT env var)
EXPOSE 8000

# Start server using Python script (migrations run in Pre-Deploy Command on Render)
# This avoids shell variable expansion issues
CMD ["python", "/app/start_server.py"]


