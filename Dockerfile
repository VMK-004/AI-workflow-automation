# Multi-stage build: Frontend + Backend
# Stage 1: Build frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /build
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
# Build with production API URL (relative path)
ARG VITE_API_URL=/api
ENV VITE_API_URL=${VITE_API_URL}
RUN npm run build

# Stage 2: Python backend
FROM python:3.12-slim

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

# Install Python dependencies (suppress root user warning)
RUN pip install --no-cache-dir --root-user-action=ignore -r requirements.txt

# Copy entire backend directory to preserve structure
COPY backend/ /app/

# Copy built frontend from previous stage
COPY --from=frontend-builder /build/dist /app/static

# Create directory for FAISS data
RUN mkdir -p /app/data/faiss

# Make startup script executable
RUN chmod +x /app/start_server.py

# Expose port (Render will set PORT env var)
EXPOSE 8000

# Start server using Python script (migrations run in Pre-Deploy Command on Render)
# This avoids shell variable expansion issues
CMD ["python", "/app/start_server.py"]


