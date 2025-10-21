# AI API + Email Dashboard (test-ai)

Purpose
- Provide a backend API that integrates with an AI text-generation service and an email service (SMTP/IMAP).
- Serve as the backend for a dashboard that helps users generate email drafts with AI, send emails, and preview inbox messages.

Quickstart (local)
1. Create a virtualenv and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Create a `.env` file with these variables:

```
AI_API_KEY=your_ai_api_key
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=you@example.com
SMTP_PASS=supersecret
IMAP_HOST=imap.example.com
IMAP_USER=you@example.com
IMAP_PASS=supersecret
API_KEY=some-internal-api-key
```

3. Run the app:

```bash
uvicorn app.main:app --reload
```

Endpoints
- GET /health
  - Returns: {"status": "ok"}

- POST /generate
  - Body: { "prompt": "Write a short follow-up email about X" }
  - Returns: { "text": "..." }
  - Uses: Calls an AI provider endpoint (replace the placeholder URL in code with your provider).

- POST /send-email
  - Body: { "to": "recipient@example.com", "subject": "...", "body": "..." }
  - Returns: { "status": "sent" }
  - Uses: SMTP to send email via configured SMTP server.

- GET /fetch-emails?limit=10
  - Returns: list of recent messages (uid, from, subject, snippet, date)
  - Uses: IMAP to fetch recent messages.

Security
- Simple API key auth via the X-API-KEY header. Set `API_KEY` in the `.env` file.

Notes and next steps
- Replace the AI provider placeholder URL with your provider (OpenAI, Anthropic, etc.) and adjust the request/response parsing accordingly.
- Consider adding rate limits, error handling improvements, persistent storage, user accounts, and a frontend dashboard.
