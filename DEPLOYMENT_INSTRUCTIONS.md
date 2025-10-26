# 🚀 Complete Deployment Instructions

This guide provides step-by-step instructions for deploying Intermap from development to production.

---

## 📝 Summary of Changes

All documentation has been updated:
- ✅ **README.md**: Complete rewrite with compelling features, modern multi-gigabit support
- ✅ **CONTRIBUTING.md**: Detailed developer guidelines and contribution process
- ✅ **DEPLOY.md**: Comprehensive deployment guide for all platforms
- ✅ **QUICKSTART.md**: 60-second setup guide
- ✅ **GEXF Colors**: 12 bandwidth categories supporting up to 100 Gbps

---

## 🐳 Step 1: Setup Docker Hub Integration

### 1.1 Get Docker Hub Access Token

1. Go to **https://hub.docker.com/settings/security**
2. Click **"New Access Token"**
3. Set these values:
   - **Description**: `GitHub Actions - Intermap`
   - **Permissions**: ✅ Read, ✅ Write, ✅ Delete
4. Click **Generate**
5. **COPY THE TOKEN** (you won't see it again!)

### 1.2 Add GitHub Secrets

1. Go to your repo: **https://github.com/YOUR_USERNAME/intermap**
2. Click: **Settings** → **Secrets and variables** → **Actions**
3. Click: **New repository secret**

**Add Secret #1:**
```
Name:  DOCKERHUB_USERNAME
Value: your-dockerhub-username
```

**Add Secret #2:**
```
Name:  DOCKERHUB_TOKEN
Value: [paste the token from step 1.1]
```

### 1.3 Update Repository URLs

Replace `YOUR_USERNAME` in these files with your actual GitHub/Docker Hub username:

```bash
# Update README.md
sed -i 's/YOUR_USERNAME/jaywendendev/g' README.md

# Update all markdown files
find . -name "*.md" -type f -exec sed -i 's/YOUR_USERNAME/jaywendendev/g' {} +

# Windows PowerShell:
Get-ChildItem -Recurse -Include *.md | ForEach-Object {
    (Get-Content $_) -replace 'YOUR_USERNAME', 'jaywendendev' | Set-Content $_
}
```

### 1.4 Verify Workflow File

Check `.github/workflows/docker-build.yml` exists. It should look like this:

```yaml
name: Build and Push Docker Image

on:
  push:
    branches: [ main, master ]
    tags: [ 'v*' ]
  pull_request:
    branches: [ main, master ]

env:
  REGISTRY: docker.io
  IMAGE_NAME: ${{ secrets.DOCKERHUB_USERNAME }}/intermap

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    # ... rest of workflow
```

### 1.5 Test the Integration

```bash
# Commit and push
git add .
git commit -m "chore: update repository URLs and setup CI"
git push origin master

# Watch the build
# Go to: https://github.com/YOUR_USERNAME/intermap/actions
```

After ~5-10 minutes, check Docker Hub:
- Visit: **https://hub.docker.com/r/YOUR_USERNAME/intermap**
- You should see the `latest` tag

---

## 🏷️ Step 2: Create a Release

### 2.1 Tag a Version

```bash
# Create annotated tag
git tag -a v1.0.0 -m "Release v1.0.0 - Initial public release

Features:
- Multi-gigabit bandwidth mapping (up to 100 Gbps)
- Smart subnet scanning with ping sweep
- Comprehensive traceroute with verification
- iperf3 bandwidth testing
- Real-time IPFS-based P2P coordination
- Web-based visualization with vis.js
- GEXF export for Gephi analysis
"

# Push tag to GitHub
git push origin v1.0.0
```

### 2.2 Create GitHub Release

1. Go to: **https://github.com/YOUR_USERNAME/intermap/releases/new**
2. Select tag: **v1.0.0**
3. Release title: **Intermap v1.0.0 - Internet Topology Mapper**
4. Description:

```markdown
## 🌐 Intermap v1.0.0

The first stable release of Intermap - a distributed internet topology mapper!

### ✨ Highlights

- **Multi-Gigabit Support**: Bandwidth mapping up to 100 Gbps
- **Smart Mapping**: Automatic subnet detection with fast ping sweeps
- **Comprehensive Discovery**: Traceroute + bandwidth + verification
- **P2P Architecture**: Fully distributed via IPFS (no central server)
- **Privacy-First**: Only public IPs shared, private IPs filtered
- **Rich Visualization**: Color-coded edges showing bandwidth speeds

### 🚀 Quick Start

**Docker:**
```bash
docker run -d --name intermap --network host --cap-add NET_ADMIN --cap-add NET_RAW YOUR_USERNAME/intermap:v1.0.0
```

**Docker Compose:**
```bash
docker-compose up -d
```

Open: http://localhost:8000

### 📊 Bandwidth Colors

- 🔵 Cyan/Blue: 10-100 Gbps (datacenter)
- 🟢 Green: 1-10 Gbps (multi-gig fiber)
- 🟡 Yellow: 100 Mbps - 1 Gbps (fast broadband)
- 🟠 Orange: 10-100 Mbps (medium)
- 🔴 Red: <10 Mbps (slow)

### 📚 Documentation

- [README](README.md) - Full feature overview
- [Quick Start](QUICKSTART.md) - 60-second setup
- [Deployment](DEPLOY.md) - Cloud deployment guide
- [Contributing](CONTRIBUTING.md) - Developer guide

### 🙏 Contribute

Help map the internet! Run a node or contribute code.

**License**: CC BY-NC-SA 4.0
```

5. Check **Set as the latest release**
6. Click **Publish release**

---

## ☁️ Step 3: Deploy to Free Tier Platforms

### Option A: Railway (Recommended)

**Free Tier**: $5/month in credits (~500 hours)

```bash
# 1. Go to https://railway.app
# 2. Sign up with GitHub
# 3. Click "New Project" → "Deploy from GitHub repo"
# 4. Select your intermap repository
# 5. Railway auto-detects Dockerfile
# 6. Add environment variables:
PORT=8000
WEB_PORT=8000
LOG_LEVEL=INFO

# 7. Generate domain in Settings → Networking
# 8. Access at: https://YOUR-APP.railway.app
```

**Limitations**:
- May not support raw ICMP (traceroute limitations)
- 500 hours/month limit
- Network capabilities restricted

### Option B: Render

**Free Tier**: 750 hours/month with automatic SSL

```bash
# 1. Go to https://render.com
# 2. Sign up with GitHub
# 3. New → Web Service
# 4. Connect intermap repository
# 5. Configure:
Name: intermap
Environment: Docker
Region: [closest to you]

# 6. Environment variables:
PORT=8000
WEB_PORT=8000
LOG_LEVEL=INFO

# 7. Deploy and wait ~5-10 minutes
# 8. Access at: https://intermap.onrender.com
```

**Limitations**:
- Spins down after 15 min inactivity (cold starts)
- May not support raw ICMP
- 750 hours/month limit

### Option C: Fly.io

**Free Tier**: 3 VMs with 256MB RAM each

```powershell
# 1. Install flyctl
iwr https://fly.io/install.ps1 -useb | iex

# 2. Login
flyctl auth login

# 3. Initialize
cd intermap
flyctl launch
# App name: intermap-YOUR-USERNAME
# Region: [closest]
# PostgreSQL: No
# Deploy now: No

# 4. Deploy
flyctl deploy

# 5. Open
flyctl open
```

**Advantages**:
- Global edge deployment
- Better network capabilities
- Persistent storage
- Static IP available

### Option D: DigitalOcean (VPS - Best for Production)

**Cost**: $6/month for 1GB RAM droplet

```bash
# 1. Create account at https://www.digitalocean.com
# 2. Create Droplet:
#    - Ubuntu 22.04 LTS
#    - Basic - $6/mo (1 vCPU, 1 GB)
# 3. SSH into droplet
ssh root@YOUR_DROPLET_IP

# 4. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 5. Run Intermap
docker run -d \
  --name intermap \
  --network host \
  --cap-add NET_ADMIN \
  --cap-add NET_RAW \
  --restart unless-stopped \
  YOUR_USERNAME/intermap:latest

# 6. Setup firewall
ufw allow 22/tcp    # SSH
ufw allow 8000/tcp  # Intermap web UI
ufw allow 4001/tcp  # IPFS
ufw allow 5201/tcp  # iperf3
ufw enable

# 7. Access at: http://YOUR_DROPLET_IP:8000
```

**Setup HTTPS with Nginx** (optional):

```bash
# Install Nginx and Certbot
apt install nginx certbot python3-certbot-nginx

# Create config
cat > /etc/nginx/sites-available/intermap <<EOF
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

# Enable site
ln -s /etc/nginx/sites-available/intermap /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx

# Get SSL certificate
certbot --nginx -d your-domain.com

# Access at: https://your-domain.com
```

---

## 🔄 Step 4: Update and Maintain

### Pull Latest Updates

```bash
# Update your local repo
git pull origin master

# Rebuild and push Docker image (triggers automatically on push)
git push origin master

# Or manually:
docker build -t YOUR_USERNAME/intermap:latest .
docker push YOUR_USERNAME/intermap:latest
```

### Update Running Containers

**Docker:**
```bash
docker pull YOUR_USERNAME/intermap:latest
docker stop intermap
docker rm intermap
docker run -d --name intermap --network host --cap-add NET_ADMIN --cap-add NET_RAW YOUR_USERNAME/intermap:latest
```

**Railway/Render**: Auto-deploys on git push

**Fly.io**:
```bash
flyctl deploy
```

**DigitalOcean VPS**:
```bash
ssh root@YOUR_DROPLET_IP
docker pull YOUR_USERNAME/intermap:latest
docker restart intermap
```

---

## 📊 Step 5: Monitor and Verify

### Check Docker Hub

Visit: **https://hub.docker.com/r/YOUR_USERNAME/intermap**

Should see:
- ✅ `latest` tag (from master branch)
- ✅ `v1.0.0` tag (from release)
- ✅ Build timestamp
- ✅ Image size

### Check GitHub Actions

Visit: **https://github.com/YOUR_USERNAME/intermap/actions**

Should see:
- ✅ Green checkmarks for builds
- ✅ Automatic builds on push
- ✅ Tag builds for releases

### Test Deployment

```bash
# Pull and run your image
docker pull YOUR_USERNAME/intermap:latest
docker run -d --name test-intermap -p 8000:8000 YOUR_USERNAME/intermap:latest

# Check logs
docker logs -f test-intermap

# Access UI
# Open: http://localhost:8000

# Verify IPFS
docker exec test-intermap ipfs id

# Check for subnet scan
docker logs test-intermap | grep "subnet"

# Clean up
docker stop test-intermap
docker rm test-intermap
```

---

## 📚 Step 6: Update Repository Settings

### README Badges

Update these URLs in README.md:

```markdown
[![Docker Build](https://github.com/YOUR_USERNAME/intermap/actions/workflows/docker-build.yml/badge.svg)](https://github.com/YOUR_USERNAME/intermap/actions/workflows/docker-build.yml)
[![Docker Hub](https://img.shields.io/docker/pulls/YOUR_USERNAME/intermap)](https://hub.docker.com/r/YOUR_USERNAME/intermap)
```

### Repository Settings

1. Go to: **Settings** → **General**
2. Set description: "Distributed P2P internet topology mapper with multi-gigabit bandwidth testing"
3. Set website: Your deployment URL
4. Topics: `internet`, `topology`, `mapping`, `p2p`, `ipfs`, `traceroute`, `bandwidth`, `network-analysis`

### About Section

Enable:
- ✅ Releases
- ✅ Packages
- ✅ Discussions
- ✅ Wiki

---

## 🎉 You're Done!

### Checklist

- ✅ Docker Hub secrets configured
- ✅ GitHub Actions building successfully
- ✅ Release v1.0.0 created
- ✅ Docker images published
- ✅ Deployed to cloud platform
- ✅ Documentation updated
- ✅ Repository configured

### Share Your Node!

Tell people to run:
```bash
docker run -d --name intermap --network host --cap-add NET_ADMIN --cap-add NET_RAW YOUR_USERNAME/intermap:latest
```

### Next Steps

1. **Monitor**: Watch GitHub Actions and Docker Hub for build status
2. **Test**: Deploy to multiple platforms and verify functionality
3. **Promote**: Share on Reddit, Twitter, forums
4. **Maintain**: Respond to issues, merge PRs, release updates
5. **Scale**: Run nodes in multiple locations for better coverage

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/intermap/issues)
- **Discussions**: [GitHub Discussions](https://github.com/YOUR_USERNAME/intermap/discussions)
- **Wiki**: [Project Wiki](https://github.com/YOUR_USERNAME/intermap/wiki)

---

**Happy deploying!** 🚀 Your internet mapping project is now live!
