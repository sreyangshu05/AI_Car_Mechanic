# Deployment Runbook

This document records a deployment path for the current code. The project is not deployed by these instructions; create the services and verify their URLs after following them.

## Production persistence configuration

The code supports PostgreSQL via `DATABASE_URL` and Neon Object Storage (S3-compatible) for media. Local development still defaults to SQLite and local media files.

### PostgreSQL / RDS

1. Create a PostgreSQL database (for example, Amazon RDS) reachable from the backend service. Restrict its network/security group to the backend only and require TLS.
2. Set `DATABASE_URL` in the backend's secret/environment configuration, e.g. `postgresql://USER:PASSWORD@HOST:5432/DBNAME`. URL-encode special characters in username/password. The production parser enables SSL.
3. Run `python backend/manage.py migrate` as a release step. Back up the database and test restoring a backup.
4. SQLite remains selected when `DATABASE_URL` is unset. SQLite is suitable for local development or a single instance with a persistent disk; avoid it for horizontally scaled or ephemeral services.

### Neon Object Storage media delivery

1. `neon.ts` declares the private `car-mechanic-uploads` bucket. Install the Neon CLI, authenticate, link this repository root to project `bold-bread-90006981` and branch `production`, then run `neon deploy` to provision it. The root `package.json` includes the Neon config packages needed to load `neon.ts`.
2. Neon Object Storage implements the S3 protocol. `neon deploy` / `neon env pull` exposes branch-scoped `AWS_ENDPOINT_URL_S3`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_REGION`. Transfer the generated values through Render's secret environment settings; don't rely on Render reading a local `.env.local`.
3. Set `USE_NEON_OBJECT_STORAGE=True`, `AWS_STORAGE_BUCKET_NAME=car-mechanic-uploads`, and `AWS_QUERYSTRING_AUTH=True` in Render. Copy the four generated `AWS_*` values to Render as secrets. The backend uses path-style S3 requests and S3 Signature V4.
4. Keep the bucket private. The Django API emits signed media URLs; don't add public-read access for customer uploads. Keep all storage credentials on Render, never in Vercel variables or the repository.
5. `USE_S3_MEDIA=True` is the alternative mode for AWS S3 or another S3-compatible service. Do not enable both storage mode flags together.
6. In production `DEBUG=False`, Django does not serve local media. Neon Object Storage serves stored objects through signed URLs.

Existing local files are not copied automatically; migrate them to the bucket before switching an existing installation. Neon CLI-generated local environment files are ignored and must not be committed.

If CLI browser authentication fails, create a project-scoped Neon API key in the Neon Console, copy it, then pipe it from the clipboard so it is not included in shell history:

```powershell
Get-Clipboard -Raw | neon profile create render-setup --api-key -
neon link --project-id bold-bread-90006981 --branch production -y --profile render-setup
neon deploy --profile render-setup
```

Do not paste the API key into chat or commit it. The `production` branch must exist; check the project branch list and use its actual branch name if different.
- The frontend expects `NEXT_PUBLIC_API_URL` at build time. Set it to the deployed backend API root ending in `/api` and rebuild/redeploy after changing it.
- The current `.env.example` describes OpenRouter, not Gemini. OpenRouter is optional and the deterministic diagnosis fallback remains active if it is unavailable.

## Frontend deployment (Vercel)

1. Push the repository to the Git provider and import it into Vercel.
2. Set the project root to `frontend` (or configure the monorepo root explicitly).
3. Use `npm run build` as the build command. The framework is Next.js.
4. Add `NEXT_PUBLIC_API_URL=https://<backend-host>/api` to Production and Preview environments as appropriate.
5. Deploy, open the resulting URL, and verify the page, stylesheet, chat, upload, history restore, diagnosis, and booking flow.
6. Add the final Vercel origin to the backend `CORS_ALLOWED_ORIGINS` and redeploy the backend.

## Backend deployment (Render + Neon)

1. Create a Render Web Service from the repository. Set Root Directory to `backend`, Build Command to `pip install -r requirements.txt`, and Start Command to `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`.
2. Create/link the Neon project and production branch. Add the private bucket from root `neon.ts` with `neon deploy` after authenticating and linking. The repository's Neon CLI skill/MCP setup can be initialized with `neon skills -y` and `neon mcp -y --oauth`.
3. In Render, set `SECRET_KEY` to a new random value, `DEBUG=False`, `ALLOWED_HOSTS=<your-service>.onrender.com`, and `CORS_ALLOWED_ORIGINS=https://<your-frontend>.vercel.app`.
4. Set `DATABASE_URL` to Neon’s pooled PostgreSQL URL. Keep it in Render's secret environment settings. Require SSL; preserve any query parameters supplied by Neon.
5. Set `USE_NEON_OBJECT_STORAGE=True`, `AWS_STORAGE_BUCKET_NAME=car-mechanic-uploads`, and `AWS_QUERYSTRING_AUTH=True`. Copy the branch-specific `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_ENDPOINT_URL_S3`, and `AWS_REGION` values into Render secret settings. Do not put these in Vercel or source control.
6. Set `OPENROUTER_API_KEY` and `OPENROUTER_MODEL` only if provider-backed diagnosis is wanted. Store the key in Render secrets.
7. Configure Render Pre-Deploy Command as `python manage.py migrate` (with service root `backend`), or run migrations once from the Render Shell.
8. Configure HTTPS, health monitoring, logs, and database backups. Confirm the API is reachable, then set Vercel's `NEXT_PUBLIC_API_URL` to `https://<your-service>.onrender.com/api` and deploy the frontend.
9. Check CORS, uploads to the private Neon bucket, private signed media URLs, diagnosis, and booking with the smoke checks below.

## Smoke checks after deployment

- `GET /api/chat/` should return method-not-allowed, confirming the route exists; use POST for chat.
- `POST /api/chat/` with a simple car symptom returns a conversation ID and follow-up.
- `GET /api/conversations/{uuid}/` returns that conversation.
- Upload a small allowed image and confirm `media_id` and a reachable media URL; attach it with a subsequent chat request.
- Generate a preliminary diagnosis and verify the response indicates the fallback or provider-derived assessment.
- Create a booking with a future date, then fetch `GET /api/booking/{id}/`.
- Refresh the frontend and check that history can be reopened and CSS/assets load.

## Rollback

Keep the prior frontend deployment and backend release available until the smoke checks pass. Roll back application versions together if API compatibility changes. Restore the database and media from backups if a migration or storage operation damages persisted data.
