"""Create chat_conversations + chat_messages if missing (uses DATABASE_URL from .env)."""
import os
import sys

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
load_dotenv(os.path.join(_repo_root, ".env"))
load_dotenv()

url = os.getenv("DATABASE_URL")
if not url:
    print("DATABASE_URL not set.", file=sys.stderr)
    sys.exit(1)

sql_path = os.path.join(_repo_root, "backend", "migrations", "002_chat_tables.sql")
with open(sql_path, encoding="utf-8") as f:
    ddl = f.read()

engine = create_engine(url, pool_pre_ping=True)
with engine.begin() as conn:
    for part in ddl.split(";"):
        stmt = part.strip()
        if stmt:
            conn.execute(text(stmt))
print("OK: chat tables applied.")
