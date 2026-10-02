[CmdletBinding()]
param(
    [switch]$Dev,
    [int]$Port = 8899
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$fastapi = Join-Path $PSScriptRoot ".venv\Scripts\fastapi.exe"
if (-not (Test-Path $fastapi)) {
    throw "Environment not found. Run .\setup.ps1 first."
}

if ($Dev) {
    & $fastapi dev --port $Port
} else {
    & $fastapi run --host 0.0.0.0 --port $Port
}
