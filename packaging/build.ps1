$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Push-Location $ProjectRoot
try {
    Remove-Item (Join-Path $ProjectRoot "build") -Recurse -Force -ErrorAction SilentlyContinue
    $DistRoot = Join-Path $ProjectRoot "dist"
    Remove-Item $DistRoot -Recurse -Force -ErrorAction SilentlyContinue
    New-Item -ItemType Directory -Path $DistRoot -Force | Out-Null

    $CandidatePythons = @(
        (Join-Path $ProjectRoot ".venv\Scripts\python.exe"),
        (Join-Path (Split-Path -Parent $ProjectRoot) ".venv\Scripts\python.exe"),
        "python"
    )
    $Python = $CandidatePythons | Where-Object { $_ -eq "python" -or (Test-Path $_) } | Select-Object -First 1
    if (-not $Python) {
        throw "No Python executable was found. Create a virtual environment or add Python to PATH."
    }

    & $Python -m pip install --upgrade pip
    if ($LASTEXITCODE -ne 0) { throw "pip upgrade failed." }

    & $Python -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) { throw "Dependency installation failed." }

    & $Python -m PyInstaller `
        --clean `
        --noconfirm `
        --onefile `
        --windowed `
        --name VisualScreensaver `
        --distpath $DistRoot `
        --add-data "config;config" `
        --collect-all PySide6 `
        run_screensaver.py
    if ($LASTEXITCODE -ne 0) { throw "PyInstaller build failed." }

    $IntermediateExe = Join-Path $ProjectRoot "build\VisualScreensaver\VisualScreensaver.exe"
    Remove-Item $IntermediateExe -Force -ErrorAction SilentlyContinue

    $BuiltExe = Join-Path $DistRoot "VisualScreensaver.exe"
    if (-not (Test-Path $BuiltExe)) {
        throw "Build completed, but the expected executable was not found: $BuiltExe"
    }

    $FinalExe = Join-Path $ProjectRoot "VisualScreensaver.exe"
    Copy-Item $BuiltExe $FinalExe -Force

    Remove-Item (Join-Path $ProjectRoot "build") -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item $DistRoot -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item (Join-Path $ProjectRoot "VisualScreensaver.spec") -Force -ErrorAction SilentlyContinue
    Get-ChildItem $ProjectRoot -Directory -Recurse -Force -Filter "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

    Write-Host "Build complete. Run this executable:" -ForegroundColor Green
    Write-Host $FinalExe -ForegroundColor Cyan
    Write-Host "Generated build artifacts were cleaned after the final EXE was copied." -ForegroundColor Green
}
finally {
    Pop-Location
}
