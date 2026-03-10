# TrueTag v4 BricsCAD Plugin Installer
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

Copy-Item "TRUETAG-v4.1.1.exe" "$installDir\" -Force
Write-Host "  [OK] TRUETAG-v4.1.1.exe"

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
