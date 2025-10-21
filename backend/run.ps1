param(
    [ValidateSet("dev", "prod", "migrate", "test")]
    [string]$Mode = "dev",
    [switch]$Help
)

function Show-Help {
    Write-Host "History AI Backend - PowerShell Runner" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\run.ps1 [Mode] [Options]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Modes:" -ForegroundColor Green
    Write-Host "  dev       - Run development server with auto-reload (default)"
    Write-Host "  prod      - Run production server"
    Write-Host "  migrate   - Run database migrations"
    Write-Host "  test      - Run pytest test suite"
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Green
    Write-Host "  -Help     - Show this help message"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Magenta
    Write-Host "  .\run.ps1 dev"
    Write-Host "  .\run.ps1 migrate"
    Write-Host "  .\run.ps1 test"
    Write-Host ""
}

function Check-VenvActive {
    if ($null -eq $env:VIRTUAL_ENV) {
        Write-Host "Virtual environment is not active. Activating..." -ForegroundColor Yellow
        & ".\.venv\Scripts\Activate.ps1"
    }
}

function Run-Dev {
    Write-Host "Starting development server..." -ForegroundColor Green
    Write-Host "API will be available at http://localhost:8000" -ForegroundColor Cyan
    Write-Host "Docs available at http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host ""
    uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
}

function Run-Prod {
    Write-Host "Starting production server..." -ForegroundColor Green
    Write-Host "API will be available at http://0.0.0.0:8000" -ForegroundColor Cyan
    Write-Host ""
    uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
}

function Run-Migrate {
    Write-Host "Running database migrations..." -ForegroundColor Green
    Write-Host ""
    uv run alembic upgrade head
    Write-Host ""
    Write-Host "Migrations completed." -ForegroundColor Green
}

function Run-Test {
    Write-Host "Running test suite..." -ForegroundColor Green
    Write-Host ""
    uv run pytest -v --tb=short
    Write-Host ""
    Write-Host "Tests completed." -ForegroundColor Green
}

function Check-Environment {
    Write-Host "Checking environment..." -ForegroundColor Yellow
    
    $missingVars = @()
    
    if (-not (Test-Path ".env")) {
        $missingVars += ".env file"
    }
    
    if ($env:GEMINI_API_KEY -eq $null -and -not (Test-Path ".env")) {
        $missingVars += "GEMINI_API_KEY"
    }
    
    if ($env:DATABASE_URL -eq $null -and -not (Test-Path ".env")) {
        $missingVars += "DATABASE_URL"
    }
    
    if ($missingVars.Count -gt 0) {
        Write-Host "Warning: Missing environment configuration:" -ForegroundColor Yellow
        foreach ($var in $missingVars) {
            Write-Host "  - $var" -ForegroundColor Yellow
        }
        Write-Host ""
        Write-Host "Please create a .env file with GEMINI_API_KEY and DATABASE_URL" -ForegroundColor Yellow
        Write-Host ""
    } else {
        Write-Host "Environment check passed." -ForegroundColor Green
    }
}

# Main execution
if ($Help) {
    Show-Help
    exit 0
}

Write-Host ""
Write-Host "History AI Backend" -ForegroundColor Cyan
Write-Host "==================" -ForegroundColor Cyan
Write-Host ""

Check-VenvActive
Check-Environment

switch ($Mode) {
    "dev" {
        Run-Dev
    }
    "prod" {
        Run-Prod
    }
    "migrate" {
        Run-Migrate
    }
    "test" {
        Run-Test
    }
    default {
        Write-Host "Unknown mode: $Mode" -ForegroundColor Red
        Show-Help
        exit 1
    }
}
