# FastAPI Streaming Backend

Backend project for Bootcamp Devscale, AI Enabled Python Batch IV.

This service exposes a FastAPI endpoint that streams AI responses as server-sent events. It uses the OpenAI Agents SDK with an OpenRouter-compatible model provider.

## Tech Stack

- Python 3.13+
- FastAPI
- Uvicorn
- uv
- OpenAI Agents SDK
- OpenRouter

## Getting Started

Clone the repository and enter the backend directory:

```bash
git clone git@github.com:Devscale-Indonesia/fastapi-streaming-backend.git
cd fastapi-streaming-backend
```

Install dependencies:

```bash
uv sync
```

Create your local environment file:

```bash
cp .env.example .env
```

Update `.env` with your OpenRouter API key:

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

Run the development server:

```bash
uv run uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

## API

### POST `/`

Streams an AI response using server-sent events.

Example request:

```bash
curl -N http://127.0.0.1:8000/ \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "parts": [
          {
            "text": "Explain FastAPI streaming in simple terms."
          }
        ]
      }
    ]
  }'
```

## Environment Variables

| Name | Description |
| --- | --- |
| `OPENROUTER_API_KEY` | API key used to access OpenRouter. |

## Notes

- `.env` is ignored by Git and should not be committed.
- `.env.example` is safe to commit and documents required environment variables.
- The current model is configured in `app/main.py`.
