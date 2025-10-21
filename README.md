# AI Workflow Orchestrator

A unified automation layer that connects ChatGPT, Notion, Gmail, and GitHub through API hooks. Create, monitor, and trigger AI-powered workflows to automate business processes.

## Features

- **Task Orchestration**: Create multi-step workflows that chain API calls (email → GPT → Notion → GitHub)
- **Prompt Templates**: Reusable AI prompt templates stored as JSON files
- **Dashboard UI**: Interactive Streamlit dashboard to manage jobs and workflows
- **API Integrations**: Gmail, Notion, GitHub, and OpenAI
- **Authentication**: Token-based authentication system
- **Logging**: Automatic workflow execution logs with detailed results
- **FastAPI Backend**: RESTful API for programmatic access

## Architecture

```
src/test_ai/
├── api.py                  # FastAPI backend
├── auth/                   # Authentication module
├── api_clients/            # API client wrappers (OpenAI, GitHub, Notion, Gmail)
├── orchestrator/           # Workflow execution engine
├── prompts/                # Prompt template management
├── dashboard/              # Streamlit UI
├── config/                 # Configuration management
├── workflows/              # Example workflow definitions
└── logs/                   # Workflow execution logs
```

## Quick Start

### 1. Installation

```bash
# Install dependencies with Poetry
poetry install

# Or with pip
pip install -r requirements.txt
```

### 2. Configuration

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:
- **OPENAI_API_KEY** (Required): Your OpenAI API key
- **GITHUB_TOKEN** (Optional): GitHub personal access token
- **NOTION_TOKEN** (Optional): Notion integration token
- **GMAIL_CREDENTIALS_PATH** (Optional): Path to Gmail OAuth credentials

### 3. Run the Dashboard

```bash
# Run the Streamlit dashboard
poetry run streamlit run src/test_ai/dashboard/app.py

# Or directly with Python
python -m streamlit run src/test_ai/dashboard/app.py
```

The dashboard will open at http://localhost:8501

### 4. Run the API Server

```bash
# Run the FastAPI server
poetry run python src/test_ai/api.py

# Or with uvicorn
poetry run uvicorn test_ai.api:app --reload
```

The API will be available at http://localhost:8000

API Documentation: http://localhost:8000/docs

## Usage

### Using the Dashboard

1. **Create Prompt Templates**: Go to the Prompts tab and create reusable AI prompts
2. **Create Workflows**: Define multi-step workflows in the Workflows tab
3. **Execute Workflows**: Run workflows with custom parameters in the Execute tab
4. **View Logs**: Check execution results in the Logs tab

### Using the API

#### Authenticate

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"user_id": "demo", "password": "demo"}'
```

#### List Workflows

```bash
curl http://localhost:8000/workflows \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Execute a Workflow

```bash
curl -X POST http://localhost:8000/workflows/execute \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_id": "simple_ai_completion",
    "variables": {"prompt": "Write a haiku about coding"}
  }'
```

## Example Workflows

### 1. Simple AI Completion

Generate text using OpenAI:

```json
{
  "id": "simple_ai_completion",
  "name": "Simple AI Completion",
  "description": "Generate a simple AI completion",
  "steps": [
    {
      "id": "generate",
      "type": "openai",
      "action": "generate_completion",
      "params": {
        "prompt": "{{prompt}}",
        "model": "gpt-4o-mini"
      }
    }
  ],
  "variables": {
    "prompt": "Write a short poem about AI"
  }
}
```

### 2. Email to Notion Summary

Fetch email, summarize with GPT, save to Notion:

```json
{
  "id": "email_to_notion",
  "name": "Email to Notion Summary",
  "steps": [
    {
      "id": "fetch_email",
      "type": "gmail",
      "action": "list_messages",
      "params": {"max_results": 1},
      "next_step": "summarize"
    },
    {
      "id": "summarize",
      "type": "openai",
      "action": "summarize",
      "params": {"text": "{{fetch_email_output}}"},
      "next_step": "save_to_notion"
    },
    {
      "id": "save_to_notion",
      "type": "notion",
      "action": "create_page",
      "params": {
        "parent_id": "{{notion_database_id}}",
        "title": "Email Summary",
        "content": "{{summarize_output}}"
      }
    }
  ]
}
```

### 3. Generate SOP and Commit to GitHub

Create an SOP with AI and commit to GitHub:

```json
{
  "id": "generate_sop_to_github",
  "name": "Generate SOP and Commit to GitHub",
  "steps": [
    {
      "id": "generate_sop",
      "type": "openai",
      "action": "generate_sop",
      "params": {"task_description": "{{task_description}}"},
      "next_step": "commit_to_github"
    },
    {
      "id": "commit_to_github",
      "type": "github",
      "action": "commit_file",
      "params": {
        "repo_name": "{{repo_name}}",
        "file_path": "{{file_path}}",
        "content": "{{generate_sop_output}}",
        "message": "Add SOP: {{task_description}}"
      }
    }
  ]
}
```

## Supported Integrations

### OpenAI
- `generate_completion`: Generate text completions
- `summarize`: Summarize text
- `generate_sop`: Generate Standard Operating Procedures

### GitHub
- `create_issue`: Create GitHub issues
- `commit_file`: Commit files to repositories
- `list_repositories`: List user repositories

### Notion
- `create_page`: Create Notion pages
- `append_to_page`: Append content to pages
- `search_pages`: Search for pages

### Gmail
- `list_messages`: List Gmail messages
- `get_message`: Get specific message
- `extract_email_body`: Extract email content

## Development

### Project Structure

```
test-ai/
├── src/test_ai/           # Source code
│   ├── api.py             # FastAPI application
│   ├── main.py            # Original demo file
│   ├── auth/              # Authentication
│   ├── api_clients/       # API integrations
│   ├── orchestrator/      # Workflow engine
│   ├── prompts/           # Template management
│   ├── dashboard/         # Streamlit UI
│   ├── config/            # Configuration
│   ├── workflows/         # Workflow definitions
│   └── logs/              # Execution logs
├── pyproject.toml         # Poetry configuration
├── .env.example           # Environment template
└── README.md              # This file
```

### Adding New Workflow Steps

1. Add action methods to the appropriate API client in `src/test_ai/api_clients/`
2. Update the workflow engine in `src/test_ai/orchestrator/workflow_engine.py`
3. Create example workflows in `src/test_ai/workflows/`

### Testing

Run the simple demo:

```bash
poetry run python src/test_ai/main.py
```

## Use Cases

- **Email Automation**: Summarize emails and push to Notion
- **Documentation Generation**: Generate SOPs and commit to GitHub
- **Content Processing**: Extract, transform, and distribute content
- **Report Generation**: Combine data from multiple sources
- **Task Automation**: Chain multiple API calls for complex workflows

## Contributing

This is a portfolio project demonstrating:
- API integration and orchestration
- AI-powered automation
- Modern Python application architecture
- FastAPI and Streamlit development

## License

MIT License - Feel free to use this project for your own portfolio or consulting work!
