@echo off
echo ========================================
echo Blog Editor - Starting...
echo ========================================
echo.

cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt -q

echo.
echo ========================================
echo Starting Blog Editor...
echo Open http://localhost:5000 in your browser
echo Press Ctrl+C to stop
echo ========================================
echo.

python app.py
