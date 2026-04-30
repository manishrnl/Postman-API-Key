@echo off
title Postman to GitHub Sync
echo ---------------------------------------------------
echo Starting Postman Workspace Sync to GitHub...
echo ---------------------------------------------------

:: Check if the file exists before running
if exist Export_To_Github.py (
    python Export_To_Github.py
) else (
    echo [ERROR] Could not find Export_To_Github.py in this folder.
    echo Current folder is: %cd%
)

echo ---------------------------------------------------
echo Process Finished.
echo ---------------------------------------------------
pause