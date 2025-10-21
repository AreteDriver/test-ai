#!/usr/bin/env bash
# Start the Streamlit Dashboard

cd "$(dirname "$0")"

echo "🎨 Starting AI Workflow Orchestrator Dashboard..."
echo "📍 Dashboard will be available at: http://localhost:8501"
echo ""

PYTHONPATH=src poetry run streamlit run src/test_ai/dashboard/app.py
