#!/bin/bash
# Start the FastAPI backend server on port 5000

echo "Starting Project Niyati Backend Server..."
echo "Server will be available at: http://127.0.0.1:5000"
echo "API Documentation: http://127.0.0.1:5000/docs"
echo ""

cd "$(dirname "$0")"
uvicorn main:app --reload --host 0.0.0.0 --port 5000
