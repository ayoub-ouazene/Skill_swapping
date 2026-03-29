@echo off
REM From repo root, with venv activated: run-api.bat
cd /d "%~dp0"
set PYTHONPATH=%~dp0backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
