# PowerShell script to create and run Alembic migration for FCM token

Write-Host "Creating Alembic migration for FCM token..." -ForegroundColor Green

# Generate migration
Write-Host "`nGenerating migration..." -ForegroundColor Yellow
docker-compose exec api alembic revision --autogenerate -m "add_fcm_token_to_users"

if ($LASTEXITCODE -eq 0) {
    Write-Host "Migration file created successfully!" -ForegroundColor Green
    
    # Run migration
    Write-Host "`nApplying migration..." -ForegroundColor Yellow
    docker-compose exec api alembic upgrade head
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`nMigration completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "`nError applying migration!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "`nError creating migration file!" -ForegroundColor Red
    exit 1
}
