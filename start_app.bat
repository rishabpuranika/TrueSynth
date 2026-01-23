@echo off
TITLE TrueSynth Launcher
cd /d "%~dp0"

echo ==========================================
echo    Starting TrueSynth Application
echo ==========================================

echo [1/2] Launching Backend Server...
start "TrueSynth Backend" cmd /k "cd backend && uvicorn app:app --reload --port 8000"

echo.
echo Waiting 5 seconds for backend to initialize...
timeout /t 5 /nobreak >nul

echo.
echo [2/2] Launching Frontend Application...
cd frontend
npm start
