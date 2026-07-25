Param()

# PowerShell script to run prod migrations
# Usage: $env:DATABASE_URL = 'postgres://user:pass@host:port/dbname'; .\.venv\Scripts\Activate.ps1; .\scripts\run_prod_migrate.ps1

if (-not $env:DATABASE_URL) {
    Write-Error "DATABASE_URL environment variable is not set. Set it and re-run."
    exit 1
}

Write-Host "Running migrations against: $($env:DATABASE_URL.Split('@')[0])..."
.\.venv\Scripts\python.exe manage.py migrate --noinput
Write-Host "Migrations completed successfully."
