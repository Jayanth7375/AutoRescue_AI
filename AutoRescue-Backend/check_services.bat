@echo off
REM AutoRescue AI - Service Status Checker (Wrapper)
REM Delegates to PowerShell for reliable status checking

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0check_services.ps1"
pause
