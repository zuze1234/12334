@echo off
echo =======================================
echo  Clap Detection Application (Windows)
echo =======================================
echo.

REM Check if virtual environment exists
if not exist venv (
    echo [ERROR] Virtual environment not found!
    echo Please run setup.bat first
    pause
    exit /b 1
)

REM Check if .env exists
if not exist .env (
    echo [ERROR] .env file not found!
    echo Please copy .env.example to .env and add your Yandex token
    pause
    exit /b 1
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)

REM Check if YANDEX_TOKEN is set
findstr /C:"YANDEX_TOKEN=your_yandex_oauth_token_here" .env >nul
if not errorlevel 1 (
    echo [WARNING] YANDEX_TOKEN may not be set in .env file
    echo The application will run but Yandex integration will not work
    echo.
)

REM Run the application
echo [INFO] Starting server...
echo [INFO] Open http://localhost:5000 in your browser
echo.
python main.py
