"""
One-off: add users.bio if missing. Uses DATABASE_URL from .env (project root or backend).

Run from repo root (with venv active):
  python backend/scripts/apply_bio_column.py

Or from backend:
  python scripts/apply_bio_column.py
"""
import os
import sys

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Prefer Skill_swapping/.env next to backend/
_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
load_dotenv(os.path.join(_repo_root, ".env"))
load_dotenv()  # fallback: cwd

url = os.getenv("DATABASE_URL")
if not url:
    print("DATABASE_URL not set. Put .env in project root or export DATABASE_URL.", file=sys.stderr)
    sys.exit(1)

sql = "ALTER TABLE users ADD COLUMN IF NOT EXISTS bio VARCHAR(2000);"

engine = create_engine(url, pool_pre_ping=True)
with engine.begin() as conn:
    conn.execute(text(sql))
print("OK: users.bio column ensured.")
