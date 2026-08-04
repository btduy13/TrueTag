param(
    [switch]$SkipTests
)

$ErrorActionPreference = 'Stop'
$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $projectDir

$version = (& python -c "from version import APP_VERSION; print(APP_VERSION)").Trim()
if (!$version) {
    throw 'Unable to determine APP_VERSION.'
}

$releaseDir = Join-Path $projectDir "release\v$version"
$workDir = Join-Path $projectDir ".release-build\v$version"
New-Item -ItemType Directory -Force -Path $releaseDir, $workDir | Out-Null

if (!$SkipTests) {
    & python -m unittest discover -s tests -v
    if ($LASTEXITCODE -ne 0) { throw 'Regression tests failed.' }
    & python test_build.py
    if ($LASTEXITCODE -ne 0) { throw 'Build readiness checks failed.' }
}

& python -m PyInstaller TRUETAG-v4.1.1.spec --clean --noconfirm `
    --distpath $releaseDir --workpath (Join-Path $workDir 'main')
if ($LASTEXITCODE -ne 0) { throw 'TrueTag build failed.' }

& python -m PyInstaller license_manager_ui.spec --clean --noconfirm `
    --distpath $releaseDir --workpath (Join-Path $workDir 'manager')
if ($LASTEXITCODE -ne 0) { throw 'License Manager build failed.' }

$mainExe = Join-Path $releaseDir "TRUETAG-v$version.exe"
$setupMainExe = Join-Path $projectDir "TrueTag_Setup\TRUETAG-v$version.exe"
Copy-Item -LiteralPath $mainExe -Destination $setupMainExe -Force

& python -m PyInstaller TrueTag_v4.1.1_Setup.spec --clean --noconfirm `
    --distpath $releaseDir --workpath (Join-Path $workDir 'installer')
if ($LASTEXITCODE -ne 0) { throw 'Installer build failed.' }

$assets = @(
    $mainExe,
    (Join-Path $releaseDir "LicenseManager-v$version.exe"),
    (Join-Path $releaseDir "TrueTag_v${version}_Setup.exe")
)

foreach ($asset in $assets) {
    if (!(Test-Path -LiteralPath $asset)) {
        throw "Expected release asset is missing: $asset"
    }
    $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $asset).Hash.ToLowerInvariant()
    $checksumPath = "$asset.sha256"
    Set-Content -LiteralPath $checksumPath -Value "$hash  $([IO.Path]::GetFileName($asset))" -Encoding ascii
}

Write-Host "Release build complete: $releaseDir"
Get-ChildItem -LiteralPath $releaseDir -File | Select-Object Name, Length
