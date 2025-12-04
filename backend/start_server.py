#!/usr/bin/env python3
"""Startup script for Render deployment"""
import os
import sys

def main():
    port = int(os.environ.get("PORT", "8000"))
    host = "0.0.0.0"
    
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

