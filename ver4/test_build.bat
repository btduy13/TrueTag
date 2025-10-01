@echo off
echo Testing TRUETAG v4.0 Build Process...
echo.

REM Check Python
python --version
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)

REM Check PyInstaller
python -m PyInstaller --version
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: PyInstaller not found!
    pause
    exit /b 1
)

REM Check required files
if not exist "TrueTag-ver4.py" (
    echo ERROR: TrueTag-ver4.py not found!
    pause
    exit /b 1
)

if not exist "logo.ico" (
    echo ERROR: logo.ico not found!
    pause
    exit /b 1
)

if not exist "config.json" (
    echo ERROR: config.json not found!
    pause
    exit /b 1
)

echo All checks passed! Build environment is ready.
echo.
echo To build the standalone executable, run:
echo   build_auto.bat
echo.
pause
