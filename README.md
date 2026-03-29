# SkillSwap Backend 🚀

The backend API for SkillSwap, a time-credit-based skill exchange platform. Built with FastAPI, PostgreSQL (via Neon), and powered by Google Gemini for AI-driven semantic search and automated certificate processing.

## Prerequisites
* Python 3.9+
* A [Neon.tech](https://neon.tech/) account (for Serverless PostgreSQL)
* A [Google Gemini API Key](https://aistudio.google.com/) (for AI Vision and Vector Embeddings)

## 🛠️ Local Setup & Installation

Create a venv at the **repo root**, activate it, then install backend deps from `backend/`:

```bash
# Windows
python -m venv venv
venv\Scripts\activate
pip install -r backend/requirements.txt
```

```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

Put `.env` at the **repo root** (or ensure `DATABASE_URL` etc. are visible to the process). Example variables:

- `DATABASE_URL` — Neon connection string  
- `GEMINI_API_KEY`, `GROQ_API_KEY`, … as needed  

## Running the API

The Python package is **`backend/app`**. You must either **change into `backend`** or set **`PYTHONPATH`** to include `backend`.

**Option A — from `backend` (recommended):**

```bash
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Option B — from repo root (Windows):** with venv activated, run `.\run-api.ps1` or `run-api.bat`. They set `PYTHONPATH` to `backend` then start uvicorn.

If you run `uvicorn app.main:app` from the repo root **without** `PYTHONPATH` or `cd backend`, you get `ModuleNotFoundError: No module named 'app'`.

## API documentation (Swagger)

http://127.0.0.1:8000/docs

