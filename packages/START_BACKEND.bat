@echo off
echo.
echo ===========================================
echo   PackVote 2.0 - Starting Backend API
echo ===========================================
echo.

cd api

REM Check if venv exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate venv
call venv\Scripts\activate

REM Install/update dependencies
echo Installing dependencies...
pip install -r requirements.txt --quiet

echo.
echo ✅ Starting FastAPI server on http://localhost:8000
echo ✅ API Documentation: http://localhost:8000/docs
echo.
echo Press CTRL+C to stop the server
echo.

python -m uvicorn main:app --reload --port 8000
