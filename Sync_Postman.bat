@echo off
title Postman to GitHub Sync
echo ---------------------------------------------------
echo Starting Postman Workspace Sync to GitHub...
echo ---------------------------------------------------

:: Check if the file exists before running
if exist Sync_Postman.py (
    python Sync_Postman.py
) else (
    echo [ERROR] Could not find Sync_Postman.py in this folder.
    echo Current folder is: %cd%
)

echo ---------------------------------------------------
echo Process Finished.
echo ---------------------------------------------------
pause