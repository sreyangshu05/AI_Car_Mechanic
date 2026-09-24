# AI Car Mechanic

A focused full-stack vehicle troubleshooting assistant. It collects symptoms, asks context-dependent follow-up questions, accepts optional media, produces a clearly qualified preliminary assessment, and lets the user explicitly book a mechanic.

## Project status

Core local application and backend APIs are implemented. Production deployment is not included: no live URLs or production credentials are committed. The backend supports Neon PostgreSQL and Neon Object Storage; follow [the deployment runbook](docs/DEPLOYMENT.md) to provision and connect them.

## Architecture

`frontend/` is a Next.js app. `backend/` is Django + Django REST Framework with SQLite. Conversation, message, media, diagnosis, and booking data are persisted relationally. Deterministic validation handles uploads, domain filtering, dates, booking, and CRUD. AI reasoning is isolated in `backend/services/`; no provider call is made for validation, uploads, or booking.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
Copy-Item .env.example backend/.env
python backend/manage.py migrate
python backend/manage.py runserver
```

In another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Set `NEXT_PUBLIC_API_URL` to `http://localhost:8000/api` and configure `CORS_ALLOWED_ORIGINS`. `OPENROUTER_API_KEY` is optional; the deterministic fallback keeps the application usable when it is absent or unavailable. `OPENROUTER_MODEL` defaults to `nvidia/nemotron-3-ultra-550b-a55b:free`.

## API

- `POST /api/chat/` — `{message, conversation_id?}`; returns a follow-up response.
- `POST /api/upload/` — multipart `file` and optional `conversation_id`; accepts validated image/audio/video up to 50MB.
- `POST /api/diagnosis/` — `{conversation_id}`; returns probable issue, possible causes, severity, action, and confidence.
- `POST /api/booking/` — requires explicit booking form fields and a valid conversation/diagnosis.
- `GET /api/booking/{id}/` — retrieves a confirmed booking.
- `GET /api/conversations/{id}/` — retrieves conversation history.

Errors use `{success:false,error:{code,message}}`. AI output is never presented as a guaranteed mechanical diagnosis.

## API reference (request and response examples)

All endpoints are rooted at `/api`. JSON endpoints use `Content-Type: application/json`; uploads use `multipart/form-data`. Errors use `{success:false,error:{code,message}}`.

`POST /api/chat/` accepts `{message, conversation_id?, media_ids?}`. Example: `{"conversation_id":null,"message":"My car clicks but will not start","media_ids":[12]}`. The response contains `conversation_id`, `reply`, `status`, and `diagnosis_ready`.

`POST /api/upload/` accepts multipart `file` and optional `conversation_id`. It validates image/audio/video MIME types, extensions, and a 50 MB limit. The `201` response contains `media_id`, `conversation_id`, `file_type`, `url`, and `status`. Pass the returned `media_id` to `/api/chat/` or `/api/diagnosis/`.

`POST /api/diagnosis/` accepts `{conversation_id, media_ids?}` and requires at least four words of symptom detail. It returns `diagnosis_id`, `probable_issue`, `possible_causes`, `severity`, `recommended_action`, `confidence`, and `booking_available`. Results are preliminary, never guaranteed.

`POST /api/booking/` requires `conversation_id`, `diagnosis_id`, `customer_name`, `phone`, `email`, `vehicle_make`, `vehicle_model`, `vehicle_year`, `preferred_date`, `preferred_time`, and `problem_summary`. It returns `201` with the booking ID; conflicts return `409`.

`GET /api/booking/{id}/` returns the confirmed booking record. `GET /api/conversations/{id}/` returns conversation metadata and ordered messages, including message type, timestamp, and attached media URL.

See [API request examples](docs/API-EXAMPLES.md) for complete curl and JSON examples. See [operations and troubleshooting](docs/OPERATIONS.md) for CORS, styling, OpenRouter, storage, and security notes.

## Deployment

Follow [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md). The backend supports Neon PostgreSQL through `DATABASE_URL` and Neon Object Storage through `USE_NEON_OBJECT_STORAGE=True`; local defaults remain SQLite and local files. Provision the Neon bucket, transfer its branch credentials into Render's secret settings, and run migrations before launch. Existing media is not migrated automatically when switching storage.

The assignment requests Gemini, while the current implementation uses OpenRouter with an optional deterministic fallback. Update this provider integration if strict Gemini-only compliance is required.

## Verification

```powershell
python -m compileall -q backend
python backend/manage.py check
cd frontend; npm run build
```

The last two commands require installed dependencies. No live deployment or external service credentials are included in this repository.
