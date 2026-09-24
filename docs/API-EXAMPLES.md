# API Examples

Base URL examples use `http://localhost:8000`. Replace with the deployed backend origin. Endpoints are rooted at `/api`.

## Chat

```http
POST /api/chat/
Content-Type: application/json
```

New conversation:

```json
{"message":"My car clicks when I try to start it"}
```

Continue and attach a previously uploaded file:

```json
{"conversation_id":"df3d7b1d-85b2-47cb-998b-c822694c8e13","message":"It only clicks and the lights are dim","media_ids":[12]}
```

Typical response:

```json
{"conversation_id":"df3d7b1d-85b2-47cb-998b-c822694c8e13","reply":"When you try to start it, does the engine crank, do you only hear clicking, or is there no sound? Do the dashboard lights come on?","status":"follow_up","diagnosis_ready":false}
```

## Upload media

```bash
curl -X POST http://localhost:8000/api/upload/ \
  -F 'file=@dashboard.jpg' \
  -F 'conversation_id=df3d7b1d-85b2-47cb-998b-c822694c8e13'
```

For a new conversation, omit `conversation_id`. Response `201` returns `media_id`, `conversation_id`, `file_type`, `url`, and `status`. Pass `media_id` in the chat `media_ids` array or diagnosis `media_ids` array.

## Diagnosis

```http
POST /api/diagnosis/
Content-Type: application/json
```

```json
{"conversation_id":"df3d7b1d-85b2-47cb-998b-c822694c8e13","media_ids":[12]}
```

Successful response fields: `diagnosis_id`, `summary`, `probable_issue`, `possible_causes`, `severity`, `recommended_action`, `confidence`, `booking_available`.

## Booking

```http
POST /api/booking/
Content-Type: application/json
```

```json
{
  "conversation_id":"df3d7b1d-85b2-47cb-998b-c822694c8e13",
  "diagnosis_id":4,
  "customer_name":"Asha Rao",
  "phone":"+919999999999",
  "email":"asha@example.com",
  "vehicle_make":"Honda",
  "vehicle_model":"Civic",
  "vehicle_year":2018,
  "problem_summary":"Clicking while starting",
  "preferred_date":"2026-10-01",
  "preferred_time":"10:30"
}
```

Response `201` returns booking ID, status, customer name, vehicle, problem summary, requested date and time.

```http
GET /api/booking/4/
GET /api/conversations/df3d7b1d-85b2-47cb-998b-c822694c8e13/
```

History response contains conversation ID, status, vehicle information, timestamps, and ordered messages with role, content, message type, timestamp, and media URL.

## Error example

```json
{"success":false,"error":{"code":"VALIDATION_ERROR","message":"Enter a valid email address."}}
```

Common statuses: `200` successful read/chat/diagnosis; `201` upload or booking created; `400` invalid input or insufficient details; `404` unknown conversation/booking; `409` duplicate booking; `405` unsupported HTTP method.
