import re

from sqlalchemy import String, func
from sqlalchemy.orm import Session

from app.models import User


def build_user_handle(user: User) -> str:
    """Stable pseudo-username: slug from name + first 8 hex chars of UUID (no DB column)."""
    parts = f"{user.first_name or ''}{user.last_name or ''}"
    base = re.sub(r"[^a-z0-9]+", "", parts.lower())[:24]
    suf = str(user.id).replace("-", "")[:8]
    if base:
        return f"{base}_{suf}"
    return f"user_{suf}"


def user_for_handle(db: Session, handle: str) -> User | None:
    """Resolve handle to User (verifies full handle string)."""
    handle = (handle or "").strip().lower().lstrip("@")
    if not handle or "_" not in handle:
        return None
    suffix = handle.rsplit("_", 1)[-1]
    if len(suffix) != 8 or not re.fullmatch(r"[a-f0-9]{8}", suffix):
        return None
    candidates = (
        db.query(User)
        .filter(
            func.replace(func.cast(User.id, String), "-", "").like(f"{suffix}%"),
        )
        .all()
    )
    for u in candidates:
        if build_user_handle(u).lower() == handle:
            return u
    return None
