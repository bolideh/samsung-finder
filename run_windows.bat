@echo off
title Samsung Device Finder
color 0B

echo.
echo  Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] Python not found!
    echo  Please install Python from https://python.org/downloads
    echo  Make sure to check "Add Python to PATH" during install.
    pause
    exit /b 1
)

echo  Python found. Starting scanner...
echo.

:: Run as admin for best ARP results
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo  Requesting admin privileges for full network access...
    powershell -Command "Start-Process cmd -ArgumentList '/c cd /d %~dp0 && python src\scanner_windows.py && pause' -Verb RunAs"
) else (
    python src\scanner_windows.py
)
