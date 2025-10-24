@echo off
setlocal enabledelayedexpansion

REM Set default port if not provided
if "%PORT%"=="" set PORT=8000

echo --- Startup Script Initiated ---
echo Starting Uvicorn server on 0.0.0.0:%PORT%...

REM Change to the project directory
cd /d "%~dp0..\packages\api"

echo Current working directory: %cd%

REM Start Uvicorn with proper binding for Render
python -m uvicorn main:app --host 0.0.0.0 --port %PORT%