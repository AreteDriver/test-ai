## Quick Start

# 1) Configure environment
cp config/settings.example.yaml config/settings.yaml
cp config/prompts.example.json config/prompts.json
# Create .env with any secrets you prefer not to keep in settings.yaml

# 2) Install
pip install -r requirements.txt

# 3) Run API
uvicorn src.main:app --reload

# 4) Run Streamlit dashboard
streamlit run streamlit_app.py

## OAuth notes (Gmail)
Place Google OAuth client as credentials.json in repo root. First run creates token.json.

## Safety
Never commit .env, credentials.json, or token.json.