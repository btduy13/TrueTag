# TrueTag v4 - BricsCAD Plugin Installer
# This script creates a complete installation package that integrates TrueTag directly into BricsCAD

import os
import shutil
import subprocess

def create_installer():
    print("=" * 60)
    print(" Creating TrueTag v4.1.1 BricsCAD Plugin Installer...")
    print("=" * 60)
    
    # Define paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(base_dir, "dist")
    exe_name = "TRUETAG-v4.1.1.exe"
    exe_path = os.path.join(dist_dir, exe_name)
    
    output_dir = os.path.join(base_dir, "TrueTag_Setup")
    
    # 1. Verify build exists
    if not os.path.exists(exe_path):
        print("❌ ERROR: Executable not found in dist/")
        print(f"   Expected: {exe_path}")
        print("\n⚠️  Please build the application first:")
        print("   Run: build_auto.bat")
        return False
    
    print(f"✓ Found executable: {exe_name}")
    
    # 2. Create Setup directory
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"✓ Created setup directory: {output_dir}")
    else:
        print(f"✓ Using existing setup directory: {output_dir}")
        
    # Clean subdirectory "Scripts" specifically if possible, to avoid stale files
    scripts_dst_clean = os.path.join(output_dir, "Scripts")
    if os.path.exists(scripts_dst_clean):
        try:
            shutil.rmtree(scripts_dst_clean)
        except:
            pass # Ignore if we can't delete, we'll overwrite anyway
    
    # 3. Copy Application Files
    print("\n📦 Copying application files...")
    shutil.copy2(exe_path, os.path.join(output_dir, exe_name))
    print(f"  ✓ {exe_name}")
    
    if os.path.exists(os.path.join(base_dir, "logo.ico")):
        shutil.copy2(os.path.join(base_dir, "logo.ico"), os.path.join(output_dir, "logo.ico"))
        print(f"  ✓ logo.ico")
    
    # Copy Scripts folder REMOVED (Bundled in EXE)
    
    # 4. Create Menu Definition File (.mnu)
    # This is critical - we need an actual menu definition file for BricsCAD to load
    print("\n📝 Creating Menu Definition file...")
    
    mnu_content = """***MENUGROUP=TRUETAG

***POP1
**TRUETAG
[TrueTag v4.1.1]
[&Launch TrueTag]^C^C(c:TRUETAG) 
[&Quick Launch (TT)]^C^C(c:TT) 
[--]
[Launch with &PID Scripts]^C^C(c:TRUETAG_PID) 
[Launch with &TML Scripts]^C^C(c:TRUETAG_TML) 
[Launch with Po&sition Scripts]^C^C(c:TRUETAG_POS) 
[--]
[License &Info]^C^C(c:TRUETAG_LICENSE) 
[&Help]^C^C(c:TRUETAG_HELP) 

[&Help]^C^C(c:TRUETAG_HELP) 
"""
    with open(os.path.join(output_dir, "truetag_menu.mnu"), "w", encoding="utf-8") as f:
        f.write(mnu_content)
    print(f"  ✓ truetag_menu.mnu")

    # 5. Create LISP Startup File (injected into on_doc_load.lsp)
    print("\n📝 Creating LISP integration files...")
    
    startup_lisp = ''';;; TrueTag v4.1.1 Startup Integration
;;; This file is automatically added to BricsCAD's on_doc_load.lsp

;; Load TrueTag plugin
(defun truetag-load-plugin (/ install-path)
  (setq install-path "REPLACE_WITH_INSTALL_DIR")
  
  ;; Only load once per session
  (if (not (boundp 'TRUETAG-LOADED))
    (progn
      (setq TRUETAG-LOADED T)
      (load (strcat install-path "/truetag_loader.lsp"))
      (princ "\\nTrueTag v4 plugin loaded successfully!")
    )
  )
  (princ)
)

;; Auto-load TrueTag
(truetag-load-plugin)
'''
    
    with open(os.path.join(output_dir, "truetag_startup.lsp"), "w", encoding="utf-8") as f:
        f.write(startup_lisp)
    print(f"  ✓ truetag_startup.lsp")
    
    # 6. Create MAIN Loader (Modified to load the .mnu file)
    loader_lisp = ''';; TrueTag v4 BricsCAD Integration Loader
;; Auto-generated - Do not manually edit paths

(setq *truetag-path* nil)
(setq *truetag-scripts-path* nil)

(defun truetag-init-paths ()
  (setq base-path "REPLACE_WITH_INSTALL_DIR")
  
  (setq *truetag-path* (strcat base-path "/REPLACE_WITH_EXE_NAME"))
  (setq *truetag-scripts-path* (strcat base-path "/Scripts"))
  
  (if (findfile *truetag-path*)
    (princ (strcat "\\nTrueTag v4 initialized: " *truetag-path*))
    (princ "\\nWarning: TrueTag v4 executable not found at expected path!")
  )
  
  ;; Force MenuBar to show
  (setvar "MENUBAR" 1)
  
  ;; Load the Menu File
  (truetag-load-menu base-path)
  
  (princ "\\n=======================================================")
  (princ "\\n     TRUETAG v4 INSTALLED SUCCESSFULLY ")
  (princ "\\n=======================================================")
  (princ "\\n Look for 'TrueTag v4' in the Menu Bar")
  (princ "\\n=======================================================")
  (princ)
)

;; Function to load the menu group
;; Function to load the menu group
;; Function to load the menu group
(defun truetag-load-menu (base-path / menu-file-cui menu-file-mnu i)
  ;; 1. Load the Menu if not present
  (if (not (menugroup "TRUETAG"))
    (progn
      (setq menu-file-cui (strcat base-path "/truetag_menu.cui"))
      (setq menu-file-mnu (strcat base-path "/truetag_menu.mnu"))
      
      (cond
        ;; Prefer compiled CUI
        ((findfile menu-file-cui)
           (setvar "FILEDIA" 0)
           (command "_.MENULOAD" menu-file-cui)
           (setvar "FILEDIA" 1)
        )
        ;; Fallback to MNU (will compile to CUI)
        ((findfile menu-file-mnu)
           (setvar "FILEDIA" 0)
           (command "_.MENULOAD" menu-file-mnu)
           (setvar "FILEDIA" 1)
        )
        (t (princ "\\nError: TrueTag menu file not found."))
      )
    )
  )
  
  ;; 2. Ensure Visibility (Force insert at end of bar)
  (if (menugroup "TRUETAG")
    (progn
       ;; Check if ALREADY visible?
       ;; We iterate to see if TRUETAG.POP1 is displayed.
       ;; But simpler is just to re-insert it if we want to be sure, 
       ;; or just assume valid if group is loaded. 
       ;; However, to fix "invisible menu" issues, we try to insert.
       ;; BUT inserting duplicate menus is bad.
       
       ;; Let's only insert if we can't find "TrueTag v4" in the menu bar names?
       ;; Hard to check names easily in LISP without complex iteration.
       
       ;; Safest Strategy for Startup:
       ;; Just append to P20 (safe high number) if not sure.
       ;; But wait, duplicates?
       ;; menucmd "P...=+..." DOES allow duplicates.
       
       ;; BETTER: Only force insert if we JUST loaded it.
       ;; If it was already loaded (previous session), BricsCAD remembers position!
       ;; So we strictly only need to simple check.
       
       ;; For now, I will keep the loop logic but only run it if needed?
       ;; No, let's just make it robust. BricsCAD remembers menubar state.
       ;; So we implicitly trust BricsCAD if Menugroup exists.
       ;; We only force insert on the very first load or if completely missing.
       
       (princ "\\nTrueTag Menu Loaded.")
       
       ;; Force display in Menubar (Try to append to the end)
       (if (not (menucmd "P20=?"))
         (menucmd "P20=+TRUETAG.POP1")
         (menucmd "P19=+TRUETAG.POP1")
       )
    )
  )
)

;; Main launch command
(defun c:TRUETAG ()
  "Launch TrueTag v4"
  (truetag-init-paths)
  (truetag-launch-app "")
)

;; Quick launch shortcut
(defun c:TT ()
  "Quick launch TrueTag v4"
  (truetag-init-paths)
  (truetag-launch-app "")
)

;; Launch application
(defun truetag-launch-app (category / launch-cmd)
  "Launch TrueTag v4 application"
  (if *truetag-path*
    (progn
      (princ (strcat "\\nLaunching TrueTag v4..."))
      
      (if (/= category "")
        (setq launch-cmd (strcat *truetag-path* " --category " category))
        (setq launch-cmd *truetag-path*)
      )
      
      (startapp launch-cmd "")
      (princ "\\nTrueTag v4 launched successfully!")
      
      (if (/= category "")
        (princ (strcat "\\nCategory: " (strcase category)))
      )
    )
    (progn
      (princ "\\nError: TrueTag v4 executable not found!")
      (princ "\\nPlease ensure TrueTag v4 is properly installed.")
    )
  )
  (princ)
)

;; Category-specific launch commands
(defun c:TRUETAG_PID ()
  "Launch TrueTag v4 with PID scripts"
  (truetag-init-paths)
  (truetag-launch-app "PID")
)

(defun c:TRUETAG_TML ()
  "Launch TrueTag v4 with TML scripts"
  (truetag-init-paths)
  (truetag-launch-app "TML")
)

(defun c:TRUETAG_POS ()
  "Launch TrueTag v4 with Position scripts"
  (truetag-init-paths)
  (truetag-launch-app "POS")
)

;; License info command
(defun c:TRUETAG_LICENSE ()
  "Display TrueTag v4 license information"
  (princ "\\n=== TrueTag v4 License Information ===")
  (princ "\\nFor detailed license information, please run TrueTag v4 application.")
  (princ "\\nUse TRUETAG command to launch the application.")
  (princ)
)

;; Help command
(defun c:TRUETAG_HELP ()
  "Display TrueTag v4 help"
  (princ "\\n=== TrueTag v4 Help ===")
  (princ "\\n")
  (princ "\\nAvailable Commands:")
  (princ "\\n  TRUETAG       - Launch TrueTag v4 application")
  (princ "\\n  TT            - Quick launch TrueTag v4")
  (princ "\\n  TRUETAG_PID   - Launch with PID scripts category")
  (princ "\\n  TRUETAG_TML   - Launch with TML scripts category")
  (princ "\\n  TRUETAG_POS   - Launch with Position scripts category")
  (princ "\\n  TRUETAG_LICENSE - Show license information")
  (princ "\\n  TRUETAG_HELP  - Show this help")
  (princ "\\n")
  (princ "\\nFeatures:")
  (princ "\\n  - Smart tag generation for CAD drawings")
  (princ "\\n  - Multiple script categories (PID, TML, Position)")
  (princ "\\n  - CSV file support for batch processing")
  (princ "\\n  - Professional UI with modern design")
  (princ)
)

;; Initialize on load
(truetag-init-paths)
'''
    
    loader_lisp = loader_lisp.replace("REPLACE_WITH_EXE_NAME", exe_name)
    with open(os.path.join(output_dir, "truetag_loader.lsp"), "w", encoding="utf-8") as f:
        f.write(loader_lisp)
    print(f"  ✓ truetag_loader.lsp")
    
    # 7. Create PowerShell Installer
    # (Updated to include safe ASCII markers and copy the .mnu file)
    print("\n🔧 Creating PowerShell installer...")
    
    ps_installer = r'''# TrueTag v4 BricsCAD Plugin Installer
# PowerShell Script for Automatic Installation

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "       TrueTag v4 - BricsCAD Plugin Installer" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Define Installation Directory
$defaultDir = "$env:APPDATA\TrueTag"
$installDir = Read-Host "Installation directory [Press Enter for: $defaultDir]"
if ([string]::IsNullOrWhiteSpace($installDir)) {
    $installDir = $defaultDir
}

Write-Host ""
Write-Host "[OK] Installation Directory: $installDir" -ForegroundColor Green

# 2. Create installation directory
if (Test-Path $installDir) {
    Write-Host "[OK] Directory exists. Updating installation..." -ForegroundColor Yellow
} else {
    Write-Host "[OK] Creating directory..." -ForegroundColor Green
    New-Item -ItemType Directory -Path $installDir -Force | Out-Null
}

# 3. Copy files
Write-Host ""
Write-Host "[COPY] Copying files..." -ForegroundColor Green

Copy-Item "REPLACE_WITH_EXE_NAME" "$installDir\" -Force
Write-Host "  [OK] REPLACE_WITH_EXE_NAME"

if (Test-Path "logo.ico") {
    Copy-Item "logo.ico" "$installDir\" -Force
    Write-Host "  [OK] logo.ico"
}

# Scripts folder copy removed (bundled)

Copy-Item "truetag_loader.lsp" "$installDir\" -Force
Write-Host "  [OK] truetag_loader.lsp"

Copy-Item "truetag_startup.lsp" "$installDir\" -Force
Write-Host "  [OK] truetag_startup.lsp"

if (Test-Path "truetag_menu.mnu") {
    Copy-Item "truetag_menu.mnu" "$installDir\" -Force
    Write-Host "  [OK] truetag_menu.mnu"
}

# 4. Update paths in LISP files
Write-Host ""
Write-Host "[CONFIG] Configuring LISP files..." -ForegroundColor Green

$lispPath = $installDir -replace '\\', '/'

# Update truetag_loader.lsp
$loaderContent = Get-Content "$installDir\truetag_loader.lsp" -Raw
$loaderContent = $loaderContent -replace 'REPLACE_WITH_INSTALL_DIR', $lispPath
Set-Content "$installDir\truetag_loader.lsp" -Value $loaderContent -Encoding UTF8
Write-Host "  [OK] Updated truetag_loader.lsp"

# Update truetag_startup.lsp
$startupContent = Get-Content "$installDir\truetag_startup.lsp" -Raw
$startupContent = $startupContent -replace 'REPLACE_WITH_INSTALL_DIR', $lispPath
Set-Content "$installDir\truetag_startup.lsp" -Value $startupContent -Encoding UTF8
Write-Host "  [OK] Updated truetag_startup.lsp"

# 5. Find BricsCAD installations
Write-Host ""
Write-Host "[SEARCH] Searching for BricsCAD installations..." -ForegroundColor Green

$bricscadPaths = @()
$versions = @("V24", "V23", "V25")
$langs = @("en_US", "en_GB", "en_AU")

foreach ($ver in $versions) {
    foreach ($lang in $langs) {
        $supportPath = "$env:APPDATA\Bricsys\BricsCAD\${ver}x64\$lang\Support"
        if (Test-Path $supportPath) {
            $bricscadPaths += $supportPath
            Write-Host "  [FOUND] BricsCAD $ver ($lang)" -ForegroundColor Green
        }
    }
}

if ($bricscadPaths.Count -eq 0) {
    Write-Host ""
    Write-Host "[WARNING] No BricsCAD installations found automatically." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "MANUAL INSTALLATION REQUIRED:" -ForegroundColor Yellow
    Write-Host "1. Open BricsCAD"
    Write-Host "2. Type: (load `"$installDir\truetag_loader.lsp`")"
    Write-Host "3. Or add to your Support File Search Path:"
    Write-Host "   Tools > Settings > Files > Support File Search Path"
    Write-Host "   Then add: $installDir"
    Write-Host ""
    Write-Host "Or specify BricsCAD Support path manually:"
    $manualPath = Read-Host "Enter BricsCAD Support folder path (or press Enter to skip)"
    
    if (![string]::IsNullOrWhiteSpace($manualPath) -and (Test-Path $manualPath)) {
        $bricscadPaths += $manualPath
    }
}

# 6. Install to BricsCAD
if ($bricscadPaths.Count -gt 0) {
    Write-Host ""
    Write-Host "[INSTALL] Installing to BricsCAD..." -ForegroundColor Green
    
    foreach ($supportPath in $bricscadPaths) {
        Write-Host ""
        Write-Host "  Installing to: $supportPath" -ForegroundColor Cyan
        
        # Check/create on_doc_load.lsp
        $onDocLoadPath = "$supportPath\on_doc_load.lsp"
        
        if (Test-Path $onDocLoadPath) {
            # Append to existing file
            $content = Get-Content $onDocLoadPath -Raw
            
            # Check if TrueTag is already in the file
            if ($content -notmatch "TrueTag v4") {
                Write-Host "    [OK] Adding TrueTag to existing on_doc_load.lsp"
                Add-Content $onDocLoadPath "`n`n;; TrueTag v4 Auto-Load`n(load `"$lispPath/truetag_loader.lsp`")`n" -Encoding UTF8
            } else {
                Write-Host "    [OK] TrueTag already in on_doc_load.lsp (skipping)"
            }
        } else {
            Write-Host "    [OK] Creating on_doc_load.lsp"
            $newContent = @"
;;; BricsCAD on_doc_load.lsp
;;; This file is automatically loaded when a document is opened

;; TrueTag v4 Auto-Load
(load "$lispPath/truetag_loader.lsp")
"@
            Set-Content $onDocLoadPath -Value $newContent -Encoding UTF8
        }
        
        Write-Host "    [OK] Integration complete!" -ForegroundColor Green
    }
}

# 7. Success message
Write-Host ""
Write-Host "========================================================" -ForegroundColor Green
Write-Host "          INSTALLATION SUCCESSFUL!" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Installation Location:" -ForegroundColor Cyan
Write-Host "  $installDir"
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Open or restart BricsCAD"
Write-Host "  2. Look for 'TrueTag v4' in the Menu Bar"
Write-Host "  3. Or type 'TRUETAG' or 'TT' to launch"
Write-Host ""
Write-Host "Commands Available:" -ForegroundColor Cyan
Write-Host "  TRUETAG       - Launch TrueTag"
Write-Host "  TT            - Quick launch"
Write-Host "  TRUETAG_HELP  - Show help"
Write-Host ""

Read-Host "Press Enter to exit"
'''
    
    ps_installer = ps_installer.replace("REPLACE_WITH_EXE_NAME", exe_name)
    with open(os.path.join(output_dir, "install_plugin.ps1"), "w", encoding="utf-8") as f:
        f.write(ps_installer)
    print(f"  ✓ install_plugin.ps1")
    
    # 7. Create batch launcher
    batch_installer = r'''@echo off
echo.
echo ========================================================
echo        TrueTag v4 - BricsCAD Plugin Installer
echo ========================================================
echo.
echo Starting PowerShell installer...
echo.

PowerShell.exe -ExecutionPolicy Bypass -File "%~dp0install_plugin.ps1"

pause
'''
    
    with open(os.path.join(output_dir, "INSTALL.bat"), "w", encoding="utf-8") as f:
        f.write(batch_installer)
    print(f"  ✓ INSTALL.bat")
    
    # 8. Create README
    print("\n📄 Creating documentation...")
    
    readme = r'''# TrueTag v4 - BricsCAD Plugin Installation

## Quick Start

### For Windows Users:
**Double-click `INSTALL.bat`** and follow the prompts.

### For Advanced Users:
Right-click `install_plugin.ps1` → Run with PowerShell

---

## What This Installer Does

1. **Copies TrueTag files** to `%APPDATA%\TrueTag` (or your chosen location)
2. **Detects BricsCAD installations** automatically
3. **Integrates with BricsCAD** by updating `on_doc_load.lsp`
4. **Loads TrueTag Menu automatically** via `truetag_menu.mnu`

---

## After Installation

1. **Open or restart BricsCAD**
2. Look for **"TrueTag v4"** in the menu bar (top of window)
3. Or type `TRUETAG` or `TT` in the command line

---

## Available Commands

| Command | Description |
|---------|-------------|
| `TRUETAG` | Launch TrueTag v4 |
| `TT` | Quick launch (shortcut) |
| `TRUETAG_PID` | Launch with PID scripts |
| `TRUETAG_TML` | Launch with TML scripts |
| `TRUETAG_POS` | Launch with Position scripts |
| `TRUETAG_HELP` | Show help |
| `TRUETAG_LICENSE` | Show license info |

---

## Troubleshooting

### Menu doesn't appear in BricsCAD

**Option 1:** Manually load the plugin:
```
Command: (load "C:/Users/YourName/AppData/Roaming/TrueTag/truetag_loader.lsp")
```

**Option 2:** Check MenuBar is visible:
```
Command: MENUBAR
New value: 1
```

**Option 3:** Manually load the menu file:
```
Command: MENULOAD
Select: %APPDATA%/TrueTag/truetag_menu.mnu
```

### BricsCAD not detected during installation

Manually specify the Support folder when prompted, typically:
```
C:\Users\YourName\AppData\Roaming\Bricsys\BricsCAD\V24x64\en_US\Support
```

---

## Uninstallation

1. Delete the TrueTag installation folder (default: `%APPDATA%\TrueTag`)
2. Remove the TrueTag line from BricsCAD's `on_doc_load.lsp`:
   - Location: `%APPDATA%\Bricsys\BricsCAD\V**x64\en_US\Support\on_doc_load.lsp`
   - Remove line: `(load "path/to/truetag_loader.lsp")`
3. Unload menu: `(command "_MENUNLOAD" "TRUETAG")`

---

**TrueTag v4 © 2025**
'''
    
    with open(os.path.join(output_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme)
    print(f"  ✓ README.md")
    
    # Final success message
    print("\n" + "=" * 60)
    print("✓ Installation package created successfully!")
    print("=" * 60)
    print(f"\n📦 Package Location: {output_dir}")
    print(f"\n🚀 To Install:")
    print(f"   1. Navigate to: {output_dir}")
    print(f"   2. Double-click: INSTALL.bat")
    print(f"   3. User will see the menu immediately!")
    print("")
    
    return True

if __name__ == "__main__":
    success = create_installer()
    if success:
        print("✓ Done!")
    else:
        print("✗ Failed to create installer package.")
        exit(1)
