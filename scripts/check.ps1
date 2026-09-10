$ErrorActionPreference = "Stop"

Write-Host "[1/2] Ruff statikus elemzés" -ForegroundColor Cyan
python -m ruff check .

Write-Host "[2/2] Pytest és coverage" -ForegroundColor Cyan
python -m pytest

Write-Host "Minden minőségkapu sikeres." -ForegroundColor Green
