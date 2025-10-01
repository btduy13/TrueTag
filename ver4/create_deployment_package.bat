@echo off
echo Creating TRUETAG v4.0 Deployment Package...
echo.

REM Create deployment directory
if exist "TRUETAG-v4-Deployment" rmdir /s /q "TRUETAG-v4-Deployment"
mkdir "TRUETAG-v4-Deployment"

echo Created deployment directory.

REM Copy executable
if exist "dist\TRUETAG-v4.exe" (
    copy "dist\TRUETAG-v4.exe" "TRUETAG-v4-Deployment\"
    echo Copied executable.
) else (
    echo ERROR: Executable not found! Please build first.
    pause
    exit /b 1
)

REM Copy configuration files
copy "config.json" "TRUETAG-v4-Deployment\" 2>nul
copy "runtime_settings.json" "TRUETAG-v4-Deployment\" 2>nul
echo Copied configuration files.

REM Copy script folders
if exist "Scripts" (
    xcopy "Scripts" "TRUETAG-v4-Deployment\Scripts\" /E /I /Q
    echo Copied script folders.
) else (
    echo WARNING: Script folders not found!
)

REM Copy documentation
copy "README_STANDALONE.md" "TRUETAG-v4-Deployment\README.md" 2>nul
echo Copied documentation.

REM Create a simple launcher
echo @echo off > "TRUETAG-v4-Deployment\Run-TRUETAG.bat"
echo echo Starting TRUETAG v4.0... >> "TRUETAG-v4-Deployment\Run-TRUETAG.bat"
echo TRUETAG-v4.exe >> "TRUETAG-v4-Deployment\Run-TRUETAG.bat"
echo echo. >> "TRUETAG-v4-Deployment\Run-TRUETAG.bat"
echo echo TRUETAG v4.0 has closed. >> "TRUETAG-v4-Deployment\Run-TRUETAG.bat"
echo pause >> "TRUETAG-v4-Deployment\Run-TRUETAG.bat"
echo Created launcher script.

echo.
echo ========================================
echo DEPLOYMENT PACKAGE CREATED!
echo ========================================
echo.
echo Package location: TRUETAG-v4-Deployment\
echo.
echo Contents:
dir "TRUETAG-v4-Deployment" /B
echo.
echo Total size:
for /f "tokens=3" %%a in ('dir "TRUETAG-v4-Deployment" /-c ^| find "File(s)"') do echo %%a bytes
echo.
echo This package can be:
echo - Copied to any Windows machine
echo - Run without installation
echo - Shared via USB or network
echo.
echo To run: Double-click TRUETAG-v4.exe or Run-TRUETAG.bat
echo.
pause
