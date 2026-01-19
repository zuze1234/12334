@echo off
echo =======================================
echo  Clap Detection Setup Script (Windows)
echo =======================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

echo [OK] Python found
python --version
echo.

REM Create virtual environment
echo [INFO] Creating virtual environment...
python -m venv venv

if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)

echo [OK] Virtual environment created
echo.

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)

echo [OK] Virtual environment activated
echo.

REM Upgrade pip
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo [INFO] Installing dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo [OK] Dependencies installed
echo.

REM Create .env file if it doesn't exist
if not exist .env (
    echo [INFO] Creating .env file...
    copy .env.example .env
    echo [OK] .env file created from .env.example
    echo.
    echo [WARNING] IMPORTANT: Edit the .env file and add your Yandex OAuth token!
    echo           You can edit it with: notepad .env
    echo.
) else (
    echo [OK] .env file already exists
    echo.
)

echo =======================================
echo  Setup complete!
echo =======================================
echo.
echo Next steps:
echo 1. Edit .env file and add your Yandex OAuth token:
echo    notepad .env
echo.
echo 2. Activate the virtual environment:
echo    venv\Scripts\activate
echo.
echo 3. Run the application:
echo    python main.py
echo.
echo 4. Open your browser and navigate to:
echo    http://localhost:5000
echo.
echo =======================================
pause
