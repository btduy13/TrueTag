#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Build script for License Manager UI
Builds the License Manager UI into a standalone executable using PyInstaller
"""

import os
import sys
import subprocess
import shutil

def check_dependencies():
    """Check if required dependencies are installed"""
    print("Checking dependencies...")
    
    required_packages = ['PyInstaller', 'ttkbootstrap']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.lower().replace('-', '_'))
            print(f"  ✓ {package} is installed")
        except ImportError:
            print(f"  ✗ {package} is not installed")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nInstalling missing packages: {', '.join(missing_packages)}")
        for package in missing_packages:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        print("Dependencies installed successfully!")
    
    return True

def clean_build():
    """Clean previous build files"""
    print("\nCleaning previous build...")
    
    dirs_to_remove = ['build', 'dist']
    files_to_remove = []
    
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"  Removed {dir_name}/")
            except Exception as e:
                print(f"  Warning: Could not remove {dir_name}/: {e}")
    
    for file_name in files_to_remove:
        if os.path.exists(file_name):
            try:
                os.remove(file_name)
                print(f"  Removed {file_name}")
            except Exception as e:
                print(f"  Warning: Could not remove {file_name}: {e}")

def build_application():
    """Build the application using PyInstaller"""
    print("\nBuilding application...")
    
    spec_file = 'license_manager_ui.spec'
    
    if not os.path.exists(spec_file):
        print(f"Error: Spec file not found: {spec_file}")
        return False
    
    try:
        # Run PyInstaller
        cmd = [sys.executable, '-m', 'PyInstaller', spec_file, '--clean', '--noconfirm']
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        print("Build completed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error:")
        print(e.stdout)
        print(e.stderr)
        return False
    except Exception as e:
        print(f"Build failed with error: {e}")
        return False

def verify_build():
    """Verify that the build was successful"""
    print("\nVerifying build...")
    
    exe_path = os.path.join('dist', 'LicenseManager.exe')
    
    if os.path.exists(exe_path):
        file_size = os.path.getsize(exe_path)
        print(f"  ✓ Executable found: {exe_path}")
        print(f"  ✓ File size: {file_size / 1024 / 1024:.2f} MB")
        return True
    else:
        print(f"  ✗ Executable not found: {exe_path}")
        return False

def main():
    """Main build function"""
    print("=" * 50)
    print("License Manager UI - Build Script")
    print("=" * 50)
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"\nWorking directory: {script_dir}")
    
    # Check dependencies
    if not check_dependencies():
        print("Error: Failed to install dependencies")
        return 1
    
    # Clean previous build
    clean_build()
    
    # Build application
    if not build_application():
        print("\nBuild failed!")
        return 1
    
    # Verify build
    if not verify_build():
        print("\nBuild verification failed!")
        return 1
    
    print("\n" + "=" * 50)
    print("Build completed successfully!")
    print("=" * 50)
    print(f"\nExecutable: {os.path.join('dist', 'LicenseManager.exe')}")
    print("\nYou can now run the application from the dist folder.")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())








