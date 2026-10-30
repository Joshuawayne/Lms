[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path $PSScriptRoot -Parent
$NpmCommand = if ($env:OS -eq 'Windows_NT') { 'npm.cmd' } else { 'npm' }

if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    throw 'Install Node.js 24 LTS first: https://nodejs.org/'
}

Push-Location $ProjectRoot
try {
    if (-not (Test-Path 'frontend/.env')) {
        Copy-Item 'frontend/.env.example' 'frontend/.env'
    }
    & $NpmCommand ci --no-audit --no-fund
    if ($LASTEXITCODE -ne 0) { throw 'Shared tooling installation failed.' }
    & $NpmCommand ci --prefix frontend --no-audit --no-fund
    if ($LASTEXITCODE -ne 0) { throw 'Frontend dependency installation failed.' }
    & $NpmCommand run postinstall --prefix frontend
    if ($LASTEXITCODE -ne 0) { throw 'Nuxt type preparation failed.' }
    & $NpmCommand run contracts:check
    if ($LASTEXITCODE -ne 0) { throw 'API contract verification failed.' }
    Write-Host 'Frontend ready. Start it with: npm run frontend:dev'
} finally {
    Pop-Location
}
