@echo off
setlocal enabledelayedexpansion

REM Set default port if not provided
if "%PORT%"=="" set PORT=8000

echo --- Startup Script Initiated ---
echo Starting Uvicorn server on 0.0.0.0:%PORT%...

REM Change to the project root directory (not the API directory)
cd /d "%~dp0.."

echo Current working directory: %cd%

REM Start Uvicorn with proper binding for Render
uvicorn packages.api.main:app --host 0.0.0.0 --port %PORT%