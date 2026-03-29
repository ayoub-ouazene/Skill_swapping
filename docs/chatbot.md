# Personal chatbot (SkillSwap Assistant)

**What it is:** Each logged-in user gets a **private assistant** that can **remember the current thread** (stored in the database) and **tailor answers** using a live snapshot of **their** SkillSwap data (credits, skills, session counts, profile).

**Not the same as:** `POST /matching/Search_skills` (intent + skill search, no `chat_*` tables). See end of this file.

---

## Flow

1. **Get a JWT** — `POST /auth/login` or `POST /auth/register`.
2. **Optional:** `POST /chat/conversations` to open a named thread, **or** skip and send messages without `conversation_id` (backend uses the latest thread or creates **“Main chat”**).
3. **Send:** `POST /chat/messages` with `{ "message": "..." }` (and optional `conversation_id`).
4. **Load UI history:** `GET /chat/conversations` → `GET /chat/conversations/{id}/messages`.

Every successful reply **saves** the user line and the assistant line in Postgres. If the model call fails, **nothing** from that turn is stored.

---

## How one reply is built (short)

1. **System** instructions for SkillSwap + safety (no inventing other people’s data).
2. **Your context block** (refreshed each request): name, email, bio, credits, rating, skills you offer, session counts (teacher / student / completed).
3. **Thread memory:** up to **40** earlier messages in **this** conversation only, then your new message.
4. **Model:** Groq **`llama-3.1-8b-instant`**. If **`GROQ_API_KEY`** is missing, the send endpoint returns **503**.

---

## What you need

| Need | Why |
|------|-----|
| `GROQ_API_KEY` | LLM replies |
| `DATABASE_URL` | Conversations, messages, and user rows for context |
| JWT on `/chat/*` | Same pattern as `/users/me` — `Authorization: Bearer <token>` (in Swagger: **Authorize** → paste token only) |

**New database:** tables may appear via app startup. **Existing Neon DB:** run `backend/migrations/002_chat_tables.sql` or `python backend/scripts/apply_chat_tables.py`.

---

## API (base path `/chat`)

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/messages` | Send text; optional `conversation_id`; returns `reply` + ids |
| POST | `/conversations` | New thread; optional `title` (max 200, default `"Chat"`) |
| GET | `/conversations` | Your threads, newest activity first |
| GET | `/conversations/{id}/messages` | History; query `skip`, `limit` (default limit 100, max 200) |

Typical errors: **401** (auth), **404** (wrong conversation for this user), **502** (upstream), **503** (no Groq key).

---

## Personalization (what the model sees about you)

Refreshed from the DB each time: name, email, bio, **Time credits**, **rating**, **skills you teach**, counts of sessions as teacher / as student / **completed** (any role). Used to personalize tone and facts; it must not leak other users’ private details.

---

## Memory rules

- **Per thread:** only the last **40** messages in that thread are sent to the model; older messages stay in the DB for your UI but are not in context.
- **Across threads:** no shared memory between `conversation_id`s.

---

## Related

- **CRUD / auth / users / skills / sessions:** `docs/crud-api.md`
- **Blueprint & product TODO:** `crud-guide.md`
- **Code:** `backend/app/routers/chat.py`, `backend/app/services/chat_user_context.py`, models `ChatConversation` / `ChatMessage`, router wired in `backend/app/main.py`
