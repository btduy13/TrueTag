@echo off
REM TrueTag v4 BricsCAD Integration Uninstaller
REM Script gỡ cài đặt tích hợp TrueTag v4 khỏi BricsCAD

echo ========================================
echo TrueTag v4 BricsCAD Integration Uninstaller
echo ========================================
echo.

REM Thiết lập đường dẫn
set "BRICSCAD_SUPPORT_DIR=%APPDATA%\Bricsys\BricsCAD\V24\en_US\Support"
set "DESKTOP=%USERPROFILE%\Desktop"
set "SHORTCUT_PATH=%DESKTOP%\TrueTag v4.lnk"

echo BricsCAD Support Directory: %BRICSCAD_SUPPORT_DIR%
echo.

REM Xác nhận gỡ cài đặt
set /p confirm="Are you sure you want to uninstall TrueTag v4 integration? (Y/N): "
if /i not "%confirm%"=="Y" (
    echo Uninstall cancelled.
    pause
    exit /b 0
)

echo.
echo Uninstalling TrueTag v4 integration...

REM Xóa files
echo Removing integration files...
if exist "%BRICSCAD_SUPPORT_DIR%\bricscad_launcher.lsp" (
    del "%BRICSCAD_SUPPORT_DIR%\bricscad_launcher.lsp"
    echo ✓ Removed bricscad_launcher.lsp
)

if exist "%BRICSCAD_SUPPORT_DIR%\bricscad_integration.lsp" (
    del "%BRICSCAD_SUPPORT_DIR%\bricscad_integration.lsp"
    echo ✓ Removed bricscad_integration.lsp
)

if exist "%BRICSCAD_SUPPORT_DIR%\TrueTag_BricsCAD.cui" (
    del "%BRICSCAD_SUPPORT_DIR%\TrueTag_BricsCAD.cui"
    echo ✓ Removed TrueTag_BricsCAD.cui
)

if exist "%BRICSCAD_SUPPORT_DIR%\truetag_autoload.lsp" (
    del "%BRICSCAD_SUPPORT_DIR%\truetag_autoload.lsp"
    echo ✓ Removed truetag_autoload.lsp
)

REM Xóa desktop shortcut
echo Removing desktop shortcut...
if exist "%SHORTCUT_PATH%" (
    del "%SHORTCUT_PATH%"
    echo ✓ Removed desktop shortcut
)

REM Khôi phục registry
echo Restoring BricsCAD configuration...
reg delete "HKEY_CURRENT_USER\Software\Bricsys\BricsCAD\V24\Profiles\Default" /v "MENUNAME" /f >nul 2>&1

echo Registry restored!
echo.

REM Xóa user guide
if exist "INTEGRATION_GUIDE.txt" (
    del "INTEGRATION_GUIDE.txt"
    echo ✓ Removed integration guide
)

echo.
echo ========================================
echo Uninstall Summary
echo ========================================
echo.
echo Files removed from: %BRICSCAD_SUPPORT_DIR%
echo Desktop shortcut removed
echo BricsCAD configuration restored
echo.
echo TrueTag v4 integration has been uninstalled.
echo.
echo Note: The main TrueTag v4 application files remain intact.
echo You can still run TrueTag v4 directly from its installation folder.
echo.

pause
