#!/usr/bin/env python3
"""Startup script for Render deployment"""
import os
import sys

def main():
    # Get PORT from environment, default to 8000
    port_str = os.environ.get("PORT", "8000")
    
    # Clean the port string (remove any shell expansion artifacts)
    port_str = port_str.strip().split(":")[0].split("}")[0]
    
    try:
        port = int(port_str)
    except ValueError:
        print(f"ERROR: Invalid PORT value '{port_str}', defaulting to 8000", file=sys.stderr)
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

