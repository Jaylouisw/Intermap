Write-Host "Waiting for Docker to be ready..." -ForegroundColor Yellow

$maxAttempts = 30
$attempt = 0

while ($attempt -lt $maxAttempts) {
    $attempt++
    try {
        $result = docker info 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "`nDocker is ready!" -ForegroundColor Green
            break
        }
    } catch {}
    
    Write-Host "." -NoNewline
    Start-Sleep -Seconds 2
}

if ($attempt -eq $maxAttempts) {
    Write-Host "`nDocker failed to start. Please start Docker Desktop manually." -ForegroundColor Red
    exit 1
}

Write-Host "`n`nBuilding Intermap Docker image..." -ForegroundColor Cyan
docker build -t intermap:latest .

if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "`nStarting Intermap container..." -ForegroundColor Cyan
docker-compose up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "Intermap is running!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "`nAccess points:"
    Write-Host "  Web UI:   http://localhost:8000" -ForegroundColor Cyan
    Write-Host "  API:      http://localhost:5000" -ForegroundColor Cyan
    Write-Host "  IPFS API: http://localhost:5001" -ForegroundColor Cyan
    Write-Host "`nView logs:"
    Write-Host "  docker-compose logs -f" -ForegroundColor Yellow
    Write-Host "`nStop:"
    Write-Host "  docker-compose down" -ForegroundColor Yellow
} else {
    Write-Host "`nFailed to start container!" -ForegroundColor Red
    exit 1
}
