# PowerShell script to run the Advanced Multi-Agent System Demo
# Usage: .\run_demo.ps1

Write-Host "🚀 Starting Advanced Multi-Agent System Demo..." -ForegroundColor Green
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.9+" -ForegroundColor Red
    exit 1
}

# Check if required packages are installed
Write-Host "Checking dependencies..." -ForegroundColor Yellow

$pydanticInstalled = python -c "import pydantic; print('OK')" 2>&1
if ($pydanticInstalled -ne "OK") {
    Write-Host "Installing required packages..." -ForegroundColor Yellow
    pip install pydantic requests
}

Write-Host "✓ All dependencies installed" -ForegroundColor Green
Write-Host ""

# Set environment variables if .env file exists
if (Test-Path ".env") {
    Write-Host "Loading environment variables from .env..." -ForegroundColor Yellow
    Get-Content .env | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
        }
    }
}

# Run the demo
Write-Host "Starting demo..." -ForegroundColor Green
Write-Host ""
python examples/advanced_multi_agent_demo.py

Write-Host ""
Write-Host "Demo completed!" -ForegroundColor Green

# Made with Bob
