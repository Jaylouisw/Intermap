# Quick start script for running Intermap in Docker
# This ensures proper port mappings and capabilities

Write-Host "🗺️  Starting Intermap Docker Container..." -ForegroundColor Cyan

# Stop and remove existing container if running
$existing = docker ps -a --filter "name=intermap" --format "{{.Names}}"
if ($existing -eq "intermap") {
    Write-Host "Stopping existing container..." -ForegroundColor Yellow
    docker stop intermap | Out-Null
    docker rm intermap | Out-Null
}

# Pull latest image
Write-Host "Pulling latest image from Docker Hub..." -ForegroundColor Cyan
docker pull jaylouisw/intermap:latest

# Run container with proper configuration
Write-Host "Starting container with port mappings..." -ForegroundColor Cyan
docker run -d `
    --name intermap `
    --cap-add=NET_ADMIN `
    --cap-add=NET_RAW `
    -p 5000:5000 `
    -p 4001:4001 `
    -p 5201:5201 `
    -v intermap-ipfs:/home/intermap/.ipfs `
    -v intermap-output:/app/output `
    jaylouisw/intermap:latest

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Intermap is starting!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 Web UI: http://localhost:5000" -ForegroundColor Cyan
    Write-Host "🔌 IPFS:   Port 4001" -ForegroundColor Cyan
    Write-Host "📡 iperf3: Port 5201" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📋 View logs:   docker logs -f intermap" -ForegroundColor Yellow
    Write-Host "⏹️  Stop:        docker stop intermap" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "⏳ Give it 10-15 seconds to start, then open http://localhost:5000" -ForegroundColor Magenta
} else {
    Write-Host ""
    Write-Host "❌ Failed to start container!" -ForegroundColor Red
    Write-Host "Check Docker is running: docker ps" -ForegroundColor Yellow
}
