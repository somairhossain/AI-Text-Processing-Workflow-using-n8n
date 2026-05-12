# AI Text Processing Workflow

A simple AI-powered workflow system where a frontend application sends user input to a FastAPI backend, and the backend forwards the payload to an n8n automation workflow.

## Project structure

- `frontend/` — simple HTML/JavaScript UI
- `backend/` — FastAPI service that generates `session_id` and sends requests to n8n
- `workflow.json` — exported n8n workflow template
- `demo-video-link.txt` — placeholder for the demo video URL

## Features

- Collects user email and text input
- Optional website URL scraping for article summarization
- Generates a unique `session_id` per request
- Sends data to an n8n webhook
- n8n workflow performs AI summarization, key points extraction, Google Sheets storage, and email notification

## Setup

1. Copy the example environment file:

   ```bash
   cp backend/.env.example backend/.env
   ```

2. Update `backend/.env` with your n8n webhook URL:

   ```text
   N8N_WEBHOOK_URL=http://localhost:5678/webhook/process-text
   ```

3. Install backend dependencies:

   ```bash
   cd backend
   pip install -r requirements.txt
   ```

## Run the backend

From the `backend` directory:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

## Run the frontend

Open `frontend/index.html` in a browser, or serve it locally:

```bash
cd frontend
python -m http.server 8080
```

Then visit `http://localhost:8080`.

## Endpoints

- `POST /process` — send `email` and `text`
- `POST /process-url` — send `email` and `url` to scrape page content and forward it to n8n

## n8n workflow

Import `workflow.json` into n8n and configure credentials for:

- OpenAI (or another LLM provider)
- Google Sheets
- Email / SMTP

Workflow steps:

1. Webhook trigger receives `email`, `text`, `session_id`, and optionally `source_url`
2. AI Summary node generates a short 2–4 sentence summary
3. Key Points node extracts 3 key points
4. Google Sheets node appends a row with session data
5. Send Email node delivers summary and key points to the user

## Notes

- If you submit a URL, the backend scrapes `<p>` tags and sends the extracted text to n8n.
- The backend does not store data locally; it only forwards the request to n8n.
- Configure n8n node credentials after importing `workflow.json`.
