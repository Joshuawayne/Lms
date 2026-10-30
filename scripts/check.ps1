[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path $PSScriptRoot -Parent
$NpmCommand = if ($env:OS -eq 'Windows_NT') { 'npm.cmd' } else { 'npm' }

function Invoke-Checked {
    param([string]$Command, [string[]]$Arguments)
    & $Command @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Check failed: $Command $($Arguments -join ' ')" }
}

Push-Location $ProjectRoot
try {
    $env:LMS_REQUIRE_DATABASE_TESTS = '1'
    Invoke-Checked -Command 'uv' -Arguments @('run', '--project', 'backend', '--frozen', 'ruff', 'check', 'backend', 'scripts')
    Invoke-Checked -Command 'uv' -Arguments @('run', '--project', 'backend', '--frozen', 'ruff', 'format', '--check', 'backend', 'scripts')
    Invoke-Checked -Command 'uv' -Arguments @('run', '--project', 'backend', '--frozen', 'pytest', 'backend/tests')
    Push-Location 'backend'
    try {
        Invoke-Checked -Command 'uv' -Arguments @('run', '--frozen', 'mypy', 'app')
        Invoke-Checked -Command 'uv' -Arguments @('run', '--frozen', 'lint-imports')
    } finally {
        Pop-Location
    }
    Invoke-Checked -Command $NpmCommand -Arguments @('run', 'contracts:check')
    Invoke-Checked -Command $NpmCommand -Arguments @('run', 'frontend:check')
    Invoke-Checked -Command $NpmCommand -Arguments @('run', 'frontend:build')
} finally {
    Pop-Location
}
