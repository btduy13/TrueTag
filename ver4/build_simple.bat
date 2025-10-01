@echo off
echo Building TRUETAG v4.0 Standalone Executable (Simple Method)...
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
    --name "TRUETAG-v4" ^
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
