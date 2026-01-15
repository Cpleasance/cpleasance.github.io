@echo off
echo ========================================
echo Site Preview - Starting...
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
echo Starting Site Preview...
echo Open http://localhost:5001 in your browser
echo.
echo Changes to your site files will auto-reload
echo Press Ctrl+C to stop
echo ========================================
echo.

python app.py
