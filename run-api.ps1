# Start FastAPI from repo root (sets PYTHONPATH so `app` resolves to backend/app).
# Usage: activate venv first, then:  .\run-api.ps1
$root = $PSScriptRoot
$env:PYTHONPATH = Join-Path $root "backend"
Set-Location $root
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
