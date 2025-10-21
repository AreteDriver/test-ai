#!/usr/bin/env bash
# Initialize default templates and test setup

cd "$(dirname "$0")"

echo "🔧 Initializing AI Workflow Orchestrator..."
echo ""

# Create default prompt templates
cat > /tmp/init_templates.py << 'EOF'
import os
os.environ["OPENAI_API_KEY"] = "demo-key"

from test_ai.prompts import PromptTemplateManager

manager = PromptTemplateManager()
manager.create_default_templates()
print("✅ Default prompt templates created!")

templates = manager.list_templates()
print(f"\n📝 {len(templates)} templates available:")
for t in templates:
    print(f"  - {t['name']}: {t['description']}")
EOF

PYTHONPATH=src poetry run python /tmp/init_templates.py

echo ""
echo "✅ Initialization complete!"
echo ""
echo "Next steps:"
echo "  1. Update .env with your API keys"
echo "  2. Run ./run_dashboard.sh to start the dashboard"
echo "  3. Run ./run_api.sh to start the API server"
