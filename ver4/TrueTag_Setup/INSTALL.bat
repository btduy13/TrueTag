@echo off
echo.
echo ========================================================
echo        TrueTag v4 - BricsCAD Plugin Installer
echo ========================================================
echo.
echo Starting PowerShell installer...
echo.

PowerShell.exe -ExecutionPolicy Bypass -File "%~dp0install_plugin.ps1"

pause
