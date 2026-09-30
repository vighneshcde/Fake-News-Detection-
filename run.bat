@echo off
title TruthGuard AI - Fake News Detection Platform
echo ========================================================
echo   TruthGuard AI - Fake News & Misinformation Detector
echo ========================================================
echo.
echo Checking Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not found in PATH! Please install Python 3.10+
    pause
    exit /b
)

echo Starting TruthGuard AI server and launching dashboard...
echo.
python run.py
pause
