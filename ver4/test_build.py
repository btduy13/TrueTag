#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quick test script to verify build setup
"""

import os
import sys
import subprocess

def check_files():
    """Check if all required files exist"""
    print("Checking required files...")
    
    required_files = [
        'license_manager_ui.py',
        'license_generator.py',
        'license_server.py',
        'license_manager_ui.spec',
        'logo.ico',
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"  [OK] {file}")
        else:
            print(f"  [MISSING] {file} - MISSING")
            missing_files.append(file)
    
    return len(missing_files) == 0

def check_dependencies():
    """Check if all dependencies are installed"""
    print("\nChecking dependencies...")
    
    dependencies = [
        'PyInstaller',
        'ttkbootstrap',
        'license_generator',
        'license_server',
        'Flask',
        'Flask-CORS',
        'requests',
    ]
    
    missing_deps = []
    for dep in dependencies:
        try:
            if dep == 'PyInstaller':
                # PyInstaller is a package, check differently
                import subprocess
                result = subprocess.run([sys.executable, '-m', 'PyInstaller', '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print(f"  [OK] {dep} (installed)")
                else:
                    raise ImportError()
            else:
                __import__(dep.lower().replace('-', '_'))
                print(f"  [OK] {dep}")
        except (ImportError, subprocess.TimeoutExpired, FileNotFoundError):
            print(f"  [NOT INSTALLED] {dep} - NOT INSTALLED")
            missing_deps.append(dep)
    
    return len(missing_deps) == 0

def main():
    """Main test function"""
    print("=" * 50)
    print("License Manager UI - Build Test")
    print("=" * 50)
    print()
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"Working directory: {script_dir}\n")
    
    # Check files
    files_ok = check_files()
    
    # Check dependencies
    deps_ok = check_dependencies()
    
    print("\n" + "=" * 50)
    if files_ok and deps_ok:
        print("[SUCCESS] All checks passed! Ready to build.")
        print("\nTo build the application, run:")
        print("  - build_license_manager.bat (Windows)")
        print("  - python build_license_manager.py (Cross-platform)")
        print("  - pyinstaller license_manager_ui.spec --clean --noconfirm")
        return 0
    else:
        print("[ERROR] Some checks failed. Please fix the issues above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())

