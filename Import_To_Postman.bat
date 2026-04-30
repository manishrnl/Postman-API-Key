@echo off
title Github to Postman Sync
echo ---------------------------------------------------
echo Starting Postman Workspace Sync from GitHub...
echo ---------------------------------------------------

:: Check if the file exists before running
if exist Import_To_Postman.py (
    python Import_To_Postman.py
) else (
    echo [ERROR] Could not find Import_To_Postman.py in this folder.
    echo Current folder is: %cd%
)

echo ---------------------------------------------------
echo Process Finished.
echo ---------------------------------------------------
pause