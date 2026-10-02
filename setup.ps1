[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
Set-Location $PSScriptRoot

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " Grid Data Service v0.3.0 - Setup" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

function Find-Python {
    $candidates = @(
        @{ Cmd = "py"; Args = @("-3.12") },
        @{ Cmd = "py"; Args = @("-3.13") },
        @{ Cmd = "py"; Args = @("-3.11") },
        @{ Cmd = "py"; Args = @("-3.10") },
        @{ Cmd = "python"; Args = @() }
    )

    foreach ($candidate in $candidates) {
        try {
            $null = Get-Command $candidate.Cmd -ErrorAction Stop
            $version = & $candidate.Cmd @($candidate.Args) -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
            if ($LASTEXITCODE -ne 0) { continue }

            $parts = $version.Trim().Split(".")
            if ([int]$parts[0] -eq 3 -and [int]$parts[1] -ge 10) {
                return $candidate
            }
        } catch {}
    }

    return $null
}

$python = Find-Python
if (-not $python) {
    throw "Python 3.10+ was not found."
}

Write-Host "[1/5] Python" -ForegroundColor Cyan
& $python.Cmd @($python.Args) --version

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "[2/5] Creating .venv" -ForegroundColor Cyan
    & $python.Cmd @($python.Args) -m venv .venv
} else {
    Write-Host "[2/5] Reusing existing .venv" -ForegroundColor Green
}

$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

Write-Host "[3/5] Upgrading packaging tools" -ForegroundColor Cyan
& $venvPython -m pip install --upgrade pip setuptools wheel

Write-Host "[4/5] Installing project + development tools" -ForegroundColor Cyan
& $venvPython -m pip install -e ".[dev]"

Write-Host "[5/5] Validating configuration and source" -ForegroundColor Cyan
& $venvPython scripts\validate_config.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& $venvPython -m compileall -q app
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "Setup complete." -ForegroundColor Green
Write-Host ""
Write-Host "Customer configuration:" -ForegroundColor Yellow
Write-Host "  Application : config\application.yaml"
Write-Host "  Jeddah model: config\profiles\jeddah.yaml"
Write-Host "  Oracle local: config\local\jeddah.yaml"
Write-Host ""
Write-Host "Test Oracle:"
Write-Host "  .\test-oracle.ps1"
Write-Host ""
Write-Host "Official FastAPI development command:"
Write-Host "  .\.venv\Scripts\fastapi.exe dev"
Write-Host ""
Write-Host "Official FastAPI production command:"
Write-Host "  .\.venv\Scripts\fastapi.exe run --host 0.0.0.0 --port 8899"
Write-Host ""
