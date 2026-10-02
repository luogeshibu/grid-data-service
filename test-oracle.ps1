[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    throw "Environment not found. Run .\setup.ps1 first."
}

& $python scripts\test_oracle.py
exit $LASTEXITCODE
