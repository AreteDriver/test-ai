#!/usr/bin/env bash
# Start the FastAPI server

cd "$(dirname "$0")"

echo "🚀 Starting AI Workflow Orchestrator API Server..."
echo "📍 API will be available at: http://localhost:8000"
echo "📖 API Documentation at: http://localhost:8000/docs"
echo ""

PYTHONPATH=src poetry run uvicorn test_ai.api:app --reload --host 0.0.0.0 --port 8000
