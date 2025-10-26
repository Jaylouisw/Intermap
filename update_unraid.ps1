# Update Intermap on Unraid Server
# Run this script to deploy the latest version with ICMP + TCP fallback

$UNRAID_IP = "10.0.0.10"
$CONTAINER_NAME = "intermap"

Write-Host "🚀 Updating Intermap on Unraid ($UNRAID_IP)..." -ForegroundColor Cyan
Write-Host ""

Write-Host "📦 Pulling latest image from Docker Hub..." -ForegroundColor Yellow
ssh root@$UNRAID_IP "docker pull jaylouisw/intermap:latest"

Write-Host ""
Write-Host "🛑 Stopping and removing old container..." -ForegroundColor Yellow  
ssh root@$UNRAID_IP "docker stop $CONTAINER_NAME 2>nul; docker rm $CONTAINER_NAME 2>nul"

Write-Host ""
Write-Host "🚀 Starting new container..." -ForegroundColor Yellow
ssh root@$UNRAID_IP "docker run -d --name $CONTAINER_NAME --cap-add=NET_ADMIN --cap-add=NET_RAW --net=host -v /mnt/user/appdata/intermap/ipfs:/home/intermap/.ipfs -v /mnt/user/appdata/intermap/output:/app/output jaylouisw/intermap:latest"

Write-Host ""
Write-Host "⏳ Waiting 15 seconds for startup..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

Write-Host ""
Write-Host "📋 Recent logs:" -ForegroundColor Cyan
ssh root@$UNRAID_IP "docker logs $CONTAINER_NAME --tail 20"

Write-Host ""
Write-Host "✅ Update complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Web UI: http://$UNRAID_IP:5000" -ForegroundColor Cyan
Write-Host "📋 View logs: ssh root@$UNRAID_IP 'docker logs -f $CONTAINER_NAME'" -ForegroundColor Cyan
Write-Host ""
Write-Host "🎯 New Feature: Topology updates after EVERY traceroute!" -ForegroundColor Green
Write-Host "   Watch the network graph grow in real-time!" -ForegroundColor Green
