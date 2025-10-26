# Initialize git repository (if not already done)
git init

# Create .gitignore if needed
if (!(Test-Path .gitignore)) {
    @"
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
*.egg-info/
.venv/
venv/
env/

# Node
node_modules/
npm-debug.log*

# Build
build/
dist/
*.egg

# IDE
.vscode/
.idea/
*.swp

# Logs
*.log
intermap.log

# Output
output/*.gexf
output/*.json

# OS
.DS_Store
Thumbs.db

# Testing
.pytest_cache/
.coverage
"@ | Out-File -FilePath .gitignore -Encoding utf8
}

# Stage all files
git add .

# Initial commit
git commit -m "Initial commit: Intermap distributed network topology mapper"

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Git repository initialized!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Create a new repository on GitHub: https://github.com/new" -ForegroundColor Yellow
Write-Host "   Repository name: intermap" -ForegroundColor Yellow
Write-Host "   Description: Distributed P2P Internet Topology Mapper using IPFS" -ForegroundColor Yellow
Write-Host "   Make it public (or private)" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. Add the remote and push:" -ForegroundColor Yellow
Write-Host "   git remote add origin https://github.com/YOUR_USERNAME/intermap.git" -ForegroundColor White
Write-Host "   git branch -M main" -ForegroundColor White
Write-Host "   git push -u origin main" -ForegroundColor White
Write-Host ""
Write-Host "3. Set up Docker Hub secrets on GitHub:" -ForegroundColor Yellow
Write-Host "   Go to: Settings > Secrets and variables > Actions" -ForegroundColor White
Write-Host "   Add two secrets:" -ForegroundColor White
Write-Host "     - DOCKERHUB_USERNAME: your Docker Hub username" -ForegroundColor White
Write-Host "     - DOCKERHUB_TOKEN: Docker Hub access token" -ForegroundColor White
Write-Host ""
Write-Host "4. Create Docker Hub access token:" -ForegroundColor Yellow
Write-Host "   https://hub.docker.com/settings/security" -ForegroundColor White
Write-Host "   Click 'New Access Token'" -ForegroundColor White
Write-Host ""
Write-Host "After setup, every push to 'main' will automatically build and push Docker image!" -ForegroundColor Green
