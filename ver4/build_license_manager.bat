@echo off
REM Build script for License Manager UI
REM This script builds the License Manager UI into a standalone executable

echo ========================================
echo Building License Manager UI
echo ========================================
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller is not installed. Installing...
    pip install pyinstaller
)

REM Check if ttkbootstrap is installed
python -c "import ttkbootstrap" 2>nul
if errorlevel 1 (
    echo ttkbootstrap is not installed. Installing...
    pip install ttkbootstrap
)

echo.
echo Cleaning previous build...
if exist "build" rmdir /s /q "build"
if exist "dist\LicenseManager.exe" del /q "dist\LicenseManager.exe"
if exist "dist\LicenseManager" rmdir /s /q "dist\LicenseManager"

echo.
echo Building application...
pyinstaller license_manager_ui.spec --clean --noconfirm

echo.
if exist "dist\LicenseManager.exe" (
    echo ========================================
    echo Build successful!
    echo Executable: dist\LicenseManager.exe
    echo ========================================
) else (
    echo ========================================
    echo Build failed!
    echo ========================================
    pause
    exit /b 1
)

echo.
pause








