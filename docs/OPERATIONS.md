# Operations, Troubleshooting, and Security

## Common symptoms

### Chat API responds with `405 Method Not Allowed`

`/api/chat/` accepts POST. Open the frontend or send JSON with POST; visiting the endpoint in a browser address bar sends GET.

### Browser reports CORS or failed fetch

Check that `NEXT_PUBLIC_API_URL` points to the backend API root (`.../api`) and that the exact frontend origin appears in backend `CORS_ALLOWED_ORIGINS`. Restart/redeploy after changing either value. Check browser Network details and backend logs for the actual response.

### Styling is missing or Next.js chunks fail

Confirm `frontend/app/layout.tsx` imports `./styles.css`, ensure only one Next.js dev server is using the project, stop it cleanly, restart from `frontend`, and hard-refresh. A `NET::ERR_NETWORK_CHANGED` indicates the browser connection to the dev server was interrupted.

### OpenRouter diagnosis falls back

The API intentionally falls back to deterministic rules when the key is unset, a request fails, a provider is overloaded, the response has no `choices`, or the model returns invalid diagnosis JSON. A provider `503`/`provider_overloaded` is upstream capacity; retry or select a currently available model in `OPENROUTER_MODEL`. Never expose the provider key in frontend configuration or logs.

### Uploaded media URL fails in production

For Neon set `USE_NEON_OBJECT_STORAGE=True`, the bucket name, and Neon branch endpoint/access credentials on the backend. Keep the bucket private and use signed URLs (`AWS_QUERYSTRING_AUTH=True`). For AWS S3 use `USE_S3_MEDIA=True`. Development-only local media serving runs only under `DEBUG=True`.

### Database contents disappear after deployment

SQLite is used when `DATABASE_URL` is unset and lives on local disk. Set `DATABASE_URL` for Neon PostgreSQL, run migrations, and configure database backups. Neon Object Storage is enabled with `USE_NEON_OBJECT_STORAGE=True`. Do not treat ephemeral service filesystems as durable.

### Next build reports a locked `.next` trace file

Stop all Next.js processes for the project, then rerun the build. Do not delete `.next` while a Next.js process is using it.

## Operational checks

- Backend: `python backend/manage.py check`.
- Database migration status: `python backend/manage.py showmigrations`.
- Apply migrations: `python backend/manage.py migrate`.
- Frontend: `cd frontend; npm run build`.
- Confirm production `DEBUG=False`, valid `ALLOWED_HOSTS`, exact CORS origins, HTTPS, durable storage, and a non-default Django secret.
- Monitor application logs for HTTP status, provider status/model, and storage errors. Avoid logging API keys, customer contact fields, full VINs, or uploaded contents.

## Data and safety

- Conversation identifiers are UUIDs and are stored by the browser for history convenience. They are not authentication or authorization tokens; the current API does not provide user accounts or private conversation access control. Do not use this configuration for sensitive customer records without adding authentication and ownership checks.
- Booking records contain customer contact details. Limit database/log access and use TLS.
- Diagnosis output is preliminary. Safety-critical symptoms and collision damage require an in-person inspection; do not direct users to drive an unsafe vehicle.
- Uploads have a 50 MB server limit and MIME/extension checks. For public deployment, add malware scanning, rate limiting, storage quotas, retention/deletion rules, and stricter file-content validation.
- Rotate any API key that has ever been committed, pasted into logs, or exposed in a client bundle.
- If a Neon Postgres connection string/password is shared outside a secret manager, reset the Neon role password and update Render's `DATABASE_URL` before launch.
