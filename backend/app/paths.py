"""Writable paths for uploads (Docker runs as non-root; CWD under /app is not writable)."""
import os
import tempfile

_cached: str | None = None


def get_upload_temp_dir() -> str:
    global _cached
    if _cached is not None:
        return _cached
    override = os.environ.get("SKILL_SWAP_UPLOAD_DIR")
    if override:
        _cached = os.path.abspath(override)
    else:
        _cached = os.path.join(tempfile.gettempdir(), "skillswap_uploads")
    os.makedirs(_cached, exist_ok=True)
    return _cached
