@echo off
title Postman to GitHub Auto-Sync
echo ---------------------------------------------------
echo Starting Postman Workspace Sync to GitHub...
echo ---------------------------------------------------

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    pause
    exit /b
)

:: Run the script (using quotes to handle spaces if necessary)
:: Adjust the name below if you renamed it to sync_postman.py
python "Sync Postman.py"

echo ---------------------------------------------------
echo Sync Process Completed.
echo ---------------------------------------------------
pause