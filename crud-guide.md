# SkillSwap API Blueprint

High-level map of the SkillSwap backend: who can do what, in what order, and what is still planned.  
For request bodies, auth headers, and status codes, see **`docs/crud-api.md`** (and **`docs/chatbot.md`** for personal chat).

---

## At a glance

**Idea:** Peer-to-peer teaching and learning with **Time Credits** as the internal balance. Users register, get a wallet, list skills, run sessions, and use a **JWT** for private routes.

**Typical flow**

1. **Register or log in** → receive a **JWT**.
2. **Profile:** read/update **your** account (`/users/me`); view **someone else’s public card** before booking (`/users/{userId}`).
3. **Marketplace:** browse **skills** (paginated list + skill detail with teacher info).
4. **Sessions:** list **your past** completed sessions; open **one session’s** detail if you were teacher or student.

Other features (certificates, matching chatbot, economy, **personal assistant chat**) live on separate route groups—see repo docs.

---

## 1. Authentication & Users (`/auth`, `/users`)

**Role:** Accounts, passwords, JWTs, and profiles (private vs public).

| Endpoint | What it does |
|----------|----------------|
| `POST /auth/register` | New user, **hashed password**, **2** Time Credits to start |
| `POST /auth/login` | Check credentials → **JWT** |
| `GET /users/me` | **Private:** credits, rating, email, name, bio (needs JWT) |
| `PUT /users/me` | **Update** name, bio (needs JWT) |
| `GET /users/{userId}` | **Public** profile of another user (e.g. before a session)—no email |

---

## 2. Skills (`/skills`)

**Role:** Marketplace of skills people teach (ties to teachers in the DB).

| Endpoint | What it does |
|----------|----------------|
| `GET /skills` | **Paginated** list of skills + teacher summary |
| `GET /skills/{skillId}` | **One skill** + teacher-facing fields |

Vector search / AI matching for discovery is handled elsewhere (e.g. `/matching`).

---

## 3. Sessions (`/sessions`)

**Role:** Read **your** learning sessions once they exist in the system (creation/booking is still TODO below).

| Endpoint | What it does |
|----------|----------------|
| `GET /sessions` | **Past completed** sessions where you are teacher or student |
| `GET /sessions/{sessionId}` | **One session** if you participate; otherwise forbidden / not found |

---

## Principles (unchanged)

- **Auth:** JWT on protected routes.
- **Economy:** Time Credits are the internal unit for booking/settlement (see economy routes for flows that move credits).
- **Product:** Built for peer teaching and learning, not a generic store.

---

## TODO / Missing

- [ ] **Create** session (`POST /sessions`) — booking
- [ ] Session **cancel** / **update**
- [ ] **Payment / credit deduction** (product-wide; partial logic may exist under `/economy`)
- [ ] **Rating & review** system (beyond fields on sessions/users)
- [x] **Personal chat** (per-user threads + history + assistant) — see **`docs/chatbot.md`**
- [ ] **Real-time** transport (WebSockets / SSE) if you need live typing or push—optional on top of REST chat

---
