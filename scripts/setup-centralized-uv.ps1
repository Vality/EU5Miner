$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$env:UV_PROJECT_ENVIRONMENT = Join-Path $env:USERPROFILE ".venvs\EU5Miner"
$env:UV_LINK_MODE = "copy"

Write-Host "Using UV_PROJECT_ENVIRONMENT=$env:UV_PROJECT_ENVIRONMENT"
Write-Host "Using UV_LINK_MODE=$env:UV_LINK_MODE"
Write-Host "Project root: $projectRoot"

Push-Location $projectRoot
try {
    uv sync --extra dev
    $pythonPath = Join-Path $env:UV_PROJECT_ENVIRONMENT "Scripts\python.exe"
    Write-Host "Centralized environment is ready."
    Write-Host "Interpreter: $pythonPath"
}
finally {
    Pop-Location
}
