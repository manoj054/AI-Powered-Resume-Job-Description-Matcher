@echo off
echo Starting AI-Resume-Matcher FastAPI Backend via uv...
cd backend
uv run python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
pause

