[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path $PSScriptRoot -Parent

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    throw 'Install uv first: https://docs.astral.sh/uv/getting-started/installation/'
}

Push-Location $ProjectRoot
try {
    if (-not (Test-Path 'backend/.env')) {
        Copy-Item 'backend/.env.example' 'backend/.env'
    }
    & uv sync --project backend --frozen
    if ($LASTEXITCODE -ne 0) { throw 'Backend dependency installation failed.' }
    Write-Host 'Backend ready. Start it with: npm run backend:dev'
} finally {
    Pop-Location
}
