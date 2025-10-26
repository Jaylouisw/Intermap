# Build and push to Docker Hub

# Configuration
$IMAGE_NAME = "yourusername/intermap"
$VERSION = "2.0.0"

Write-Host "Building Intermap Docker image..." -ForegroundColor Cyan

# Build the image
docker build -t ${IMAGE_NAME}:${VERSION} -t ${IMAGE_NAME}:latest .

if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "`nImage built successfully!" -ForegroundColor Green
Write-Host "`nTo push to Docker Hub:" -ForegroundColor Yellow
Write-Host "1. Login: docker login"
Write-Host "2. Push: docker push ${IMAGE_NAME}:${VERSION}"
Write-Host "        docker push ${IMAGE_NAME}:latest"
Write-Host "`nOthers can then run:" -ForegroundColor Cyan
Write-Host "  docker run -d -p 8000:8000 -p 5000:5000 -p 5001:5001 ${IMAGE_NAME}:latest"
