# Sets up a centralized uv virtual environment for the EU5Miner uv workspace.
# Run once per machine, or after deleting the central venv.
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path "$PSScriptRoot/..").Path
$venvDir  = Join-Path $env:USERPROFILE ".venvs\EU5Miner"

Write-Host "Using venv: $venvDir"
Write-Host "Repo root: $repoRoot"

# Tell uv to put the venv outside the workspace (avoids OneDrive sync collisions).
$env:UV_PROJECT_ENVIRONMENT = $venvDir
# Force copy-mode linking so OneDrive does not choke on symlinks.
$env:UV_LINK_MODE = "copy"

Push-Location $repoRoot
try {
    uv sync --all-packages --extra=dev
    if ($LASTEXITCODE -ne 0) { throw "uv sync failed" }
    Write-Host "OK. Activate the venv with: & '$venvDir\Scripts\Activate.ps1'"
}
finally {
    Pop-Location
}
