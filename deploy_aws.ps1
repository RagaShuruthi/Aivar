# PowerShell AWS Deployment Script for Agentic AI CRM Assistant
Write-Host "--------------------------------------------------------" -ForegroundColor Cyan
Write-Host "🚀 Starting AWS Production Deployment for Agentic AI CRM" -ForegroundColor Cyan
Write-Host "--------------------------------------------------------" -ForegroundColor Cyan

# Check if Docker is installed
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker is not installed or not running in PATH." -ForegroundColor Red
    Exit 1
}

# Build and start containers
Write-Host "🛠️ Building and launching Docker containers via docker-compose..." -ForegroundColor Yellow
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Verify Health
Write-Host "⏳ Verifying backend health check..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

try {
    $res = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
    if ($res.status -eq "healthy") {
        Write-Host "--------------------------------------------------------" -ForegroundColor Green
        Write-Host "✅ PRODUCTION DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
        Write-Host " FastAPI Docs: http://localhost:8000/docs" -ForegroundColor Green
        Write-Host " Streamlit UI: http://localhost:8501" -ForegroundColor Green
        Write-Host "--------------------------------------------------------" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Health probe error: $_" -ForegroundColor Red
    docker-compose logs
}
