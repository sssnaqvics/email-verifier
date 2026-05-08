@echo off
echo ============================================
echo    MZ Verifier - First Time Setup
echo ============================================
echo.

echo [1/4] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    echo Please install Python from https://www.python.org/downloads/
    echo IMPORTANT: Check "Add Python to PATH" during installation
    pause
    exit
)
echo Python found!

echo.
echo [2/4] Creating virtual environment...
python -m venv venv
echo Virtual environment created!

echo.
echo [3/4] Installing packages...
call venv\Scripts\activate
pip install -r requirements.txt
echo Packages installed!

echo.
echo [4/4] Setup complete!
echo ============================================
echo    Setup finished successfully!
echo    Now double-click 'run.bat' to start
echo ============================================
pause