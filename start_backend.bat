@echo off
echo Starting AI-Resume-Matcher FastAPI Backend...
cd /d "%~dp0\backend"
uv run --python 3.15 python main.py
pause
