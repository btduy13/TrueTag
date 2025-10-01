# TRUETAG v4.0 - Standalone Executable

## Overview
This is a standalone version of TRUETAG v4.0 that can run on any Windows machine without requiring Python or any dependencies to be installed.

## Building the Standalone Executable

### Method 1: Auto Build (Recommended)
1. Double-click `build_auto.bat`
2. The script will automatically install PyInstaller if needed
3. Wait for the build process to complete
4. The executable will be created in the `dist` folder

### Method 2: Simple Build
1. Double-click `build_simple.bat`
2. Wait for the build process to complete
3. The executable will be created in the `dist` folder

### Method 3: Advanced Build
1. Double-click `build_standalone.bat`
2. Wait for the build process to complete
3. The executable will be created in the `dist` folder

### Method 4: Test Build Environment
1. Double-click `test_build.bat`
2. This will verify all requirements are met
3. Then run one of the build methods above

## Requirements for Building
- Python 3.8+ installed
- PyInstaller installed (`pip install pyinstaller`)
- All dependencies from `requirements.txt`

## What's Included in the Standalone
- **TRUETAG-v4.exe** - The main executable
- **All Python dependencies** - Embedded in the executable
- **Configuration files** - config.json, runtime_settings.json
- **Script folders** - Scripts folder with all AutoLISP scripts
- **Logo and icons** - logo.ico
- **Supporting modules** - usage_reporting.py, config_manager.py

## Distribution
The standalone executable can be:
- Copied to any Windows machine
- Run without installation
- Shared via USB, network, or cloud storage
- No Python or dependencies required on target machine

## File Size
The executable is typically 50-80 MB due to embedded Python runtime and all dependencies.

## System Requirements
- Windows 7/8/10/11 (64-bit recommended)
- BricsCAD installed (for AutoLISP script execution)
- Internet connection (for email reporting feature)

## Features Included
- ✅ Modern UI with responsive design
- ✅ AutoLISP script execution
- ✅ CSV file support
- ✅ Usage reporting and email notifications
- ✅ Theme switching
- ✅ Configuration persistence
- ✅ Error handling and logging

## Troubleshooting
If the build fails:
1. Ensure all dependencies are installed
2. Check that all files are present
3. Try the simple build method first
4. Check Python and PyInstaller versions

## Support
For issues or questions, contact the development team.
