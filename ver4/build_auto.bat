echo off
echo Building TrueTag v4.1.2 Standalone Executable (Auto Setup)...
echo.

REM Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.8+ and try again.
    pause
    exit /b 1
)

echo Python found. Checking PyInstaller...

REM Check if PyInstaller is available
python -m PyInstaller --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo PyInstaller not found. Installing...
    python -m pip install pyinstaller
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to install PyInstaller!
        pause
        exit /b 1
    )
    echo PyInstaller installed successfully.
) else (
    echo PyInstaller found.
)

echo.

REM Clean previous builds
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "__pycache__" rmdir /s /q "__pycache__"

echo Cleaning previous builds... Done.
echo.

REM Build the executable with all necessary options
echo Building executable with PyInstaller...
python -m PyInstaller --onefile ^
    --windowed ^
    --name "TRUETAG-v4.1.2" ^
    --icon "logo.ico" ^
    --add-data "logo.ico;." ^
    --add-data "config.json;." ^
    --add-data "runtime_settings.json;." ^
    --add-data "usage_reporting.py;." ^
    --add-data "config_manager.py;." ^
    --add-data "Scripts;Scripts" ^
    --hidden-import "win32com.client" ^
    --hidden-import "ttkbootstrap" ^
    --hidden-import "PIL" ^
    --hidden-import "PIL.Image" ^
    --hidden-import "PIL.ImageTk" ^
    --hidden-import "tkinter" ^
    --hidden-import "tkinter.ttk" ^
    --hidden-import "tkinter.messagebox" ^
    --hidden-import "tkinter.filedialog" ^
    --hidden-import "json" ^
    --hidden-import "os" ^
    --hidden-import "sys" ^
    --hidden-import "datetime" ^
    --hidden-import "time" ^
    --hidden-import "smtplib" ^
    --hidden-import "email.mime.text" ^
    --hidden-import "email.mime.multipart" ^
    --hidden-import "email.mime.base" ^
    --hidden-import "csv" ^
    --hidden-import "glob" ^
    --hidden-import "shutil" ^
    TrueTag-ver4.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo Executable created: dist\TRUETAG-v4.1.2.exe
    echo.
    echo The standalone application is ready to run on any Windows machine
    echo without requiring Python or any dependencies to be installed.
    echo.
    echo File size:
    dir "dist\TRUETAG-v4.1.2.exe" | find "TRUETAG-v4.1.2.exe"
    echo.
    echo.
    echo Non-interactive build: Skipping deployment package prompt.
    REM echo Would you like to create a deployment package? (Y/N)
    REM set /p choice=
    REM if /i "%choice%"=="Y" (
    REM     call create_deployment_package.bat
    REM )
    echo Done.
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
