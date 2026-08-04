@echo off
set VERSION=4.1.2
set APP_NAME=TrueTag_v%VERSION%_Setup

echo ========================================
echo Building Single-File Installer EXE
echo ========================================

:: Clean previous builds
if exist build_installer rmdir /s /q build_installer
if exist dist_installer rmdir /s /q dist_installer

:: Build the single-file setup
python -m PyInstaller --noconfirm --onefile --windowed --name "%APP_NAME%" --icon "logo.ico" --add-data "TrueTag_Setup;TrueTag_Setup" --workpath "build_installer" --distpath "dist_installer" "single_file_installer.py"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ========================================
    echo BUILD FAILED!
    echo ========================================
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ========================================
echo BUILD SUCCESSFUL!
echo Output: dist_installer\%APP_NAME%.exe
echo ========================================
pause
