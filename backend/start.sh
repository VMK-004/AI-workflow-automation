#!/bin/sh
set -e

# Get PORT from environment, default to 8000 if not set
PORT=${PORT:-8000}

# Start uvicorn server
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"




