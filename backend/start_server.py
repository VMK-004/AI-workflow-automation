#!/usr/bin/env python3
"""Startup script for Render deployment"""
import os
import sys
import re
import subprocess

def run_migrations():
    """Run database migrations using Alembic"""
    try:
        print("Running database migrations...", file=sys.stderr)
        # Run alembic upgrade head
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            print("Migrations completed successfully", file=sys.stderr)
            if result.stdout:
                print(result.stdout, file=sys.stderr)
        else:
            print(f"WARNING: Migration failed with exit code {result.returncode}", file=sys.stderr)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            if result.stdout:
                print(result.stdout, file=sys.stderr)
            # Continue anyway - might be a non-critical error
    except Exception as e:
        print(f"WARNING: Failed to run migrations: {str(e)}", file=sys.stderr)
        print("Continuing with server startup...", file=sys.stderr)
        # Continue anyway - migrations might already be applied

def main():
    # Run migrations before starting server (for free tier, no Pre-Deploy Command)
    run_migrations()
    
    # Get PORT from environment, default to 8000
    port_str = os.environ.get("PORT", "8000")
    
    # Robustly extract numeric port value
    # Handle cases like "10000:-8000}", "${PORT:-8000}", etc.
    # Extract first sequence of digits
    match = re.search(r'\d+', str(port_str).strip())
    if match:
        port_str = match.group(0)
    else:
        port_str = "8000"  # Default if no digits found
    
    try:
        port = int(port_str)
        # Ensure port is in valid range
        if port < 1 or port > 65535:
            raise ValueError(f"Port {port} out of range")
    except (ValueError, AttributeError) as e:
        print(f"ERROR: Invalid PORT value '{os.environ.get('PORT', 'not set')}' -> extracted '{port_str}', defaulting to 8000", file=sys.stderr)
        port = 8000
    
    host = "0.0.0.0"
    
    print(f"Starting server on {host}:{port}", file=sys.stderr)
    
    # Import uvicorn and run
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        log_level="info"
    )

if __name__ == "__main__":
    main()

