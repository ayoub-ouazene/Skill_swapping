# SkillSwap CRUD API (implemented)

This document describes the **SkillSwap** REST endpoints implemented in `backend/app/main.py` (routers under `backend/app/routers/`). They follow the blueprint in `crud-guide.md`.

**Base URL (local):** `http://127.0.0.1:8000`  
**Interactive docs:** `GET /docs` (Swagger UI), `GET /redoc`

---

## Authentication

All protected routes expect an **HTTP Bearer token** (JWT).

| Header | Value |
|--------|--------|
| `Authorization` | `Bearer <access_token>` |

Obtain `<access_token>` from:

- `POST /auth/register`, or  
- `POST /auth/login`

The JWT payload includes the subject `sub` (user UUID). Tokens are signed with `JWT_SECRET_KEY` from the environment (a dev default exists if unset—set a strong secret in production).

**Swagger UI:** use **Authorize** and paste **only** the token string (not the word `Bearer`).

---

## 1. Authentication & users

### `POST /auth/register`

Creates a user, hashes the password (bcrypt), sets initial **Time Credits** to **2.0**, normalizes **email** to lowercase, and returns a JWT.

**Auth:** none  

**Request body (JSON):**

| Field | Type | Rules |
|-------|------|--------|
| `email` | string | Valid email |
| `password` | string | Min length **8** |
| `first_name` | string | Max 100 chars |
| `last_name` | string | Max 100 chars |

**Response:** `201 Created`

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```

**Errors:** `400` if email already registered.

---

### `POST /auth/login`

Verifies email/password and returns a JWT.

**Auth:** none  

**Request body (JSON):**

| Field | Type |
|-------|------|
| `email` | string |
| `password` | string |

**Response:** `200 OK` — same shape as register (`access_token`, `token_type`).

**Errors:** `401` if credentials are wrong.

---

### `GET /users/me`

Returns the **logged-in** user’s private profile.

**Auth:** Bearer  

**Response:** `200 OK`

| Field | Description |
|-------|-------------|
| `id` | User UUID |
| `email` | Email |
| `first_name`, `last_name` | Name |
| `bio` | Optional bio |
| `credit` | Time Credit balance |
| `rating` | Average rating (stored on user) |

---

### `PUT /users/me`

Updates the current user’s profile. Only fields sent in the body are updated (**partial update**).

**Auth:** Bearer  

**Request body (JSON):** all optional  

| Field | Type | Max length |
|-------|------|------------|
| `first_name` | string | 100 |
| `last_name` | string | 100 |
| `bio` | string | 2000 |

**Response:** `200 OK` — same shape as `GET /users/me`.

---

### `GET /users/{user_id}`

Returns a **public** profile for another user (e.g. before booking).

**Auth:** none  

**Path:** `user_id` — UUID  

**Response:** `200 OK`

| Field | Description |
|-------|-------------|
| `id` | User UUID |
| `first_name`, `last_name` | Name |
| `bio` | Optional |
| `rating` | Public rating |
| `skills` | List of `{ id, skill_name }` |

**Errors:** `404` if user does not exist.

**Note:** Email is **not** exposed on public profiles.

---

## 2. Skills (read-only marketplace)

These endpoints list skills stored in the database (often created via other flows, e.g. certificate upload).

### `GET /skills`

Paginated list of skills with teacher summary.

**Auth:** none  

**Query parameters:**

| Name | Default | Notes |
|------|---------|--------|
| `skip` | `0` | Offset |
| `limit` | `20` | Clamped between **1** and **100** |

**Response:** `200 OK`

```json
{
  "items": [
    {
      "id": "<uuid>",
      "skill_name": "...",
      "teacher_id": "<uuid>",
      "teacher_first_name": "...",
      "teacher_last_name": "...",
      "teacher_rating": 0.0
    }
  ],
  "total": 0,
  "skip": 0,
  "limit": 20
}
```

---

### `GET /skills/{skill_id}`

Detail for one skill, including teacher public fields.

**Auth:** none  

**Path:** `skill_id` — UUID  

**Response:** `200 OK` — includes `teacher_bio` among teacher fields.

**Errors:** `404` if skill not found.

---

## 3. Sessions (past sessions only)

Session rows are created elsewhere (e.g. economy flows). These routes only **read** data.

### `GET /sessions`

Lists **past** sessions for the current user: `status == "COMPLETED"`, where the user is **teacher** or **student**.

**Auth:** Bearer  

**Response:** `200 OK`

```json
{
  "items": [
    {
      "id": "<uuid>",
      "teacher_id": "<uuid>",
      "student_id": "<uuid>",
      "skill_id": "<uuid>",
      "skill_name": "... or null",
      "status": "COMPLETED",
      "duration_hours": null,
      "rating": null
    }
  ]
}
```

If there are no completed sessions, `items` is `[]`.

---

### `GET /sessions/{session_id}`

Returns one session if the current user is the **teacher** or **student**.

**Auth:** Bearer  

**Path:** `session_id` — UUID  

**Response:** `200 OK` — same fields as each item above (single object, not wrapped in `items`).

**Errors:**

| Code | When |
|------|------|
| `404` | Session not found |
| `403` | User is not teacher or student on this session |

---

## Summary table

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| POST | `/auth/register` | No | Register + JWT |
| POST | `/auth/login` | No | Login + JWT |
| GET | `/users/me` | Bearer | Current user (private) |
| PUT | `/users/me` | Bearer | Update profile |
| GET | `/users/{user_id}` | No | Public profile + skills |
| GET | `/skills` | No | List skills (paginated) |
| GET | `/skills/{skill_id}` | No | Skill detail |
| GET | `/sessions` | Bearer | My completed sessions |
| GET | `/sessions/{session_id}` | Bearer | Session detail (participant only) |

---

## Not covered here (see `crud-guide.md` TODO)

- `POST /sessions` (create booking)
- Session cancel/update
- Payment / credit deduction (partially elsewhere under `/economy`)
- Ratings/reviews beyond stored fields
- Other routers: `/certificates`, `/matching`, `/economy` (separate features)

---

## Database note

If `users` was created before the `bio` column existed, apply the migration in `backend/migrations/001_add_users_bio.sql` or run `backend/scripts/apply_bio_column.py` once.
