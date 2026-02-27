#!/usr/bin/env python3
"""
Backend startup script for Project Niyati

This script allows you to start either Flask or FastAPI backend server.
Usage:
    python start_backend.py flask    # Start Flask on port 5000
    python start_backend.py fastapi  # Start FastAPI on port 8000
"""

import sys
import os

def start_flask():
    """Start Flask development server"""
    print("Starting Flask backend on http://127.0.0.1:5000")
    print("Make sure frontend .env.local has: NEXT_PUBLIC_API_URL=http://127.0.0.1:5000")
    from app import app
    app.run(debug=True, port=5000, host='0.0.0.0')

def start_fastapi():
    """Start FastAPI server with uvicorn"""
    print("Starting FastAPI backend on http://127.0.0.1:8000")
    print("Make sure frontend .env.local has: NEXT_PUBLIC_API_URL=http://127.0.0.1:8000")
    import uvicorn
    uvicorn.run("app_fastapi:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python start_backend.py [flask|fastapi]")
        print("\nExamples:")
        print("  python start_backend.py flask    # Start Flask on port 5000")
        print("  python start_backend.py fastapi  # Start FastAPI on port 8000")
        sys.exit(1)
    
    backend_type = sys.argv[1].lower()
    
    if backend_type == "flask":
        start_flask()
    elif backend_type == "fastapi":
        start_fastapi()
    else:
        print(f"Unknown backend type: {backend_type}")
        print("Use 'flask' or 'fastapi'")
        sys.exit(1)
