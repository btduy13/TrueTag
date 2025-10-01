@echo off
echo Building TRUETAG v4.0 Standalone Executable...
echo.

REM Clean previous builds
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "__pycache__" rmdir /s /q "__pycache__"

echo Cleaning previous builds... Done.
echo.

REM Build the executable
echo Building executable with PyInstaller...
python -m PyInstaller --clean TrueTag-ver4.spec

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo Executable created: dist\TRUETAG-v4.exe
    echo.
    echo The standalone application is ready to run on any Windows machine
    echo without requiring Python or any dependencies to be installed.
    echo.
    echo File size:
    dir "dist\TRUETAG-v4.exe" | find "TRUETAG-v4.exe"
    echo.
    pause
) else (
    echo.
    echo ========================================
    echo BUILD FAILED!
    echo ========================================
    echo.
    echo Please check the error messages above.
    echo.
    pause
)
