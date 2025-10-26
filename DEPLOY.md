# 🚀 Deployment Guide

This guide covers deploying Intermap to various platforms, from local development to production cloud hosting.

---

## 📋 Prerequisites

Before deploying, ensure you have:

- ✅ GitHub account with repository set up
- ✅ Docker Hub account (for automated builds)
- ✅ Docker installed locally (for testing)
- ✅ Git configured with SSH keys

---

## 🐳 Docker Hub Setup

### 1. Add GitHub Secrets for Automated Builds

Intermap uses GitHub Actions to automatically build and push Docker images to Docker Hub.

**Step-by-step:**

1. **Get Docker Hub Access Token**
   - Go to https://hub.docker.com/settings/security
   - Click **"New Access Token"**
   - Description: `GitHub Actions - Intermap`
   - Permissions: **Read, Write, Delete**
   - Click **Generate** and **copy the token** (you won't see it again!)

2. **Add Secrets to GitHub Repository**
   - Go to your GitHub repo: `https://github.com/jaylouisw/intermap`
   - Click **Settings** → **Secrets and variables** → **Actions**
   - Click **New repository secret**
   
   Add two secrets:
   
   **Secret 1:**
   - Name: `DOCKERHUB_USERNAME`
   - Value: Your Docker Hub username (e.g., `jaywendendev`)
   
   **Secret 2:**
   - Name: `DOCKERHUB_TOKEN`
   - Value: The access token you copied from step 1

3. **Verify GitHub Actions Workflow**
   
   The workflow file `.github/workflows/docker-build.yml` should exist. If not, create it:

   ```yaml
   name: Docker Build and Push

   on:
     push:
       branches: [ master, main ]
       tags: [ 'v*' ]
     pull_request:
       branches: [ master, main ]

   jobs:
     build:
       runs-on: ubuntu-latest
       steps:
         - name: Checkout code
           uses: actions/checkout@v3

         - name: Set up Docker Buildx
           uses: docker/setup-buildx-action@v2

         - name: Log in to Docker Hub
           uses: docker/login-action@v2
           with:
             username: ${{ secrets.DOCKERHUB_USERNAME }}
             password: ${{ secrets.DOCKERHUB_TOKEN }}

         - name: Extract metadata
           id: meta
           uses: docker/metadata-action@v4
           with:
             images: ${{ secrets.DOCKERHUB_USERNAME }}/intermap
             tags: |
               type=ref,event=branch
               type=ref,event=pr
               type=semver,pattern={{version}}
               type=semver,pattern={{major}}.{{minor}}
               type=raw,value=latest,enable={{is_default_branch}}

         - name: Build and push
           uses: docker/build-push-action@v4
           with:
             context: .
             push: ${{ github.event_name != 'pull_request' }}
             tags: ${{ steps.meta.outputs.tags }}
             labels: ${{ steps.meta.outputs.labels }}
             cache-from: type=gha
             cache-to: type=gha,mode=max
   ```

4. **Test the Workflow**
   ```bash
   git add .
   git commit -m "chore: setup GitHub Actions for Docker Hub"
   git push origin master
   ```
   
   - Go to **Actions** tab in GitHub
   - Watch the build complete
   - Check Docker Hub for your image: `https://hub.docker.com/r/jaylouisw/intermap`

5. **Create a Release (Optional)**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
   
   This creates a versioned image: `jaylouisw/intermap:v1.0.0` and `jaylouisw/intermap:1.0`

---

## 🏠 Local Development

### Docker Compose

```bash
git clone https://github.com/jaylouisw/intermap.git
cd intermap
docker-compose up -d
```

Access at http://localhost:8000

### From Source

```bash
# Install dependencies
pip install -r requirements.txt
cd frontend && npm install && npm run build && cd ..

# Start IPFS daemon (separate terminal)
ipfs daemon

# Run application
python src/main.py
```

---

## ☁️ Cloud Platform Deployment

### 🚂 Railway

**Railway** is one of the easiest platforms for deploying Docker containers with generous free tier.

**Free Tier:**
- $5/month in credits
- ~500 hours runtime
- Automatic HTTPS
- Simple deployment

**Deployment Steps:**

1. **Create Railway Account**
   - Go to https://railway.app/
   - Sign up with GitHub

2. **Deploy from GitHub**
   - Click **New Project**
   - Select **Deploy from GitHub repo**
   - Choose `intermap` repository
   - Railway auto-detects Dockerfile

3. **Configure Environment**
   - Click on your service
   - Go to **Variables** tab
   - Add:
     ```
     PORT=8000
     WEB_PORT=8000
     LOG_LEVEL=INFO
     ```

4. **Add Network Capabilities** (Important!)
   
   Railway doesn't support `NET_ADMIN` by default, but you can request it:
   
   - Go to **Settings** tab
   - Under **Deploy**, add:
     ```
     Docker Command: --cap-add NET_ADMIN --cap-add NET_RAW
     ```
   
   **Note**: If traceroute fails, Railway may not support raw sockets. Use ICMP echo mode instead.

5. **Generate Domain**
   - Go to **Settings** → **Networking**
   - Click **Generate Domain**
   - Your app will be at: `https://YOUR-APP.railway.app`

6. **Monitor Logs**
   - Click **Deployments** tab
   - View real-time logs

**Limitations:**
- May not support raw ICMP (depends on infrastructure)
- Limited to 500 hours/month on free tier
- Network capabilities restricted

### 🎨 Render

**Render** provides free Docker hosting with excellent support for web services.

**Free Tier:**
- 750 hours/month
- Automatic SSL
- Free for public repos

**Deployment Steps:**

1. **Create Render Account**
   - Go to https://render.com/
   - Sign up with GitHub

2. **Create New Web Service**
   - Click **New** → **Web Service**
   - Connect your GitHub repo
   - Select `intermap` repository

3. **Configure Service**
   ```
   Name: intermap
   Environment: Docker
   Region: Choose closest to you
   Branch: master
   ```

4. **Set Environment Variables**
   ```
   PORT=8000
   WEB_PORT=8000
   LOG_LEVEL=INFO
   PYTHONUNBUFFERED=1
   ```

5. **Advanced Settings**
   - Docker Command: Leave empty (uses Dockerfile CMD)
   - Health Check Path: `/`
   - Auto-Deploy: Yes

6. **Deploy**
   - Click **Create Web Service**
   - Wait for build (~5-10 minutes)
   - Your app will be at: `https://intermap.onrender.com`

**Limitations:**
- Free tier spins down after 15 min inactivity (cold starts)
- May not support raw ICMP packets
- Limited to 750 hours/month

### ✈️ Fly.io

**Fly.io** offers true global edge deployment with excellent Docker support.

**Free Tier:**
- 3 shared-cpu VMs with 256MB RAM
- 3GB persistent storage
- 160GB outbound transfer/month

**Deployment Steps:**

1. **Install flyctl**
   ```bash
   # Windows (PowerShell)
   iwr https://fly.io/install.ps1 -useb | iex
   
   # Mac/Linux
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login**
   ```bash
   flyctl auth login
   ```

3. **Initialize App**
   ```bash
   cd intermap
   flyctl launch
   ```
   
   Answer prompts:
   ```
   App name: intermap-YOUR-USERNAME
   Region: Choose closest to you
   Set up PostgreSQL: No
   Deploy now: No (configure first)
   ```

4. **Edit fly.toml**
   ```toml
   app = "intermap-YOUR-USERNAME"
   primary_region = "ord"

   [build]
     dockerfile = "Dockerfile"

   [env]
     PORT = "8000"
     WEB_PORT = "8000"
     LOG_LEVEL = "INFO"

   [[services]]
     internal_port = 8000
     protocol = "tcp"

     [[services.ports]]
       port = 80
       handlers = ["http"]
       force_https = true

     [[services.ports]]
       port = 443
       handlers = ["tls", "http"]

     [[services.http_checks]]
       interval = "30s"
       timeout = "5s"
       grace_period = "10s"
       method = "GET"
       path = "/"

   [mounts]
     source = "intermap_data"
     destination = "/data"
   ```

5. **Allocate IPv4 (Optional)**
   ```bash
   flyctl ips allocate-v4
   ```

6. **Deploy**
   ```bash
   flyctl deploy
   ```

7. **Open App**
   ```bash
   flyctl open
   ```

**Advantages:**
- Real global edge deployment
- Better network capabilities than other platforms
- Persistent storage with volumes
- Can allocate static IPs

**Limitations:**
- More complex setup
- Free tier has resource limits
- May still have ICMP restrictions

### 🌀 Heroku

**Heroku** classic PaaS platform with container support.

**Free Tier:** Deprecated (only paid plans)

**Deployment Steps:**

1. **Install Heroku CLI**
   ```bash
   # Mac
   brew tap heroku/brew && brew install heroku
   
   # Windows
   # Download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Login**
   ```bash
   heroku login
   heroku container:login
   ```

3. **Create App**
   ```bash
   heroku create intermap-YOUR-USERNAME
   ```

4. **Set Environment Variables**
   ```bash
   heroku config:set WEB_PORT=8000
   heroku config:set LOG_LEVEL=INFO
   heroku config:set PYTHONUNBUFFERED=1
   ```

5. **Deploy Container**
   ```bash
   heroku container:push web
   heroku container:release web
   ```

6. **Scale Dyno**
   ```bash
   heroku ps:scale web=1
   ```

7. **Open App**
   ```bash
   heroku open
   ```

**Note**: Heroku free tier ended November 2022. Minimum $5-7/month required.

---

## 🏢 Self-Hosted / VPS

### DigitalOcean Droplet

**Best for full control and production deployments.**

1. **Create Droplet**
   - Size: Basic - $6/month (1 vCPU, 1 GB RAM)
   - Image: Ubuntu 22.04 LTS
   - Enable: Monitoring, IPv6

2. **SSH into Droplet**
   ```bash
   ssh root@YOUR_DROPLET_IP
   ```

3. **Install Docker**
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   ```

4. **Run Intermap**
   ```bash
   docker run -d \
     --name intermap \
     --network host \
     --cap-add NET_ADMIN \
     --cap-add NET_RAW \
     --restart unless-stopped \
     jaylouisw/intermap:latest
   ```

5. **Set Up Firewall**
   ```bash
   ufw allow 22/tcp    # SSH
   ufw allow 80/tcp    # HTTP
   ufw allow 443/tcp   # HTTPS
   ufw allow 8000/tcp  # Intermap web UI
   ufw allow 4001/tcp  # IPFS
   ufw allow 5201/tcp  # iperf3
   ufw enable
   ```

6. **Set Up Reverse Proxy (Nginx)**
   ```bash
   apt install nginx certbot python3-certbot-nginx
   ```
   
   Create `/etc/nginx/sites-available/intermap`:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://localhost:8000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
       }
   }
   ```
   
   Enable site:
   ```bash
   ln -s /etc/nginx/sites-available/intermap /etc/nginx/sites-enabled/
   nginx -t
   systemctl reload nginx
   ```

7. **Enable HTTPS**
   ```bash
   certbot --nginx -d your-domain.com
   ```

8. **Monitor Logs**
   ```bash
   docker logs -f intermap
   ```

### AWS EC2 / Google Cloud / Azure

Similar to DigitalOcean - launch a VM, install Docker, run container. Each platform has specific networking configurations.

**EC2 Specifics:**
- Use Security Groups to allow ports
- Use Elastic IP for static address
- Consider ECS for container orchestration

**Google Cloud Specifics:**
- Use Compute Engine VM
- Configure firewall rules
- Consider Cloud Run for serverless

**Azure Specifics:**
- Use Azure Container Instances
- Configure Network Security Groups
- Consider Azure App Service

---

## 🔒 Production Considerations

### Security

- ✅ Use HTTPS (Certbot for Let's Encrypt)
- ✅ Configure firewall (UFW, Security Groups)
- ✅ Keep Docker images updated
- ✅ Use Docker secrets for sensitive data
- ✅ Enable Docker Content Trust
- ✅ Run as non-root user in container

### Monitoring

```bash
# Container stats
docker stats intermap

# View logs
docker logs -f --tail 100 intermap

# Check IPFS status
docker exec intermap ipfs swarm peers
```

### Backups

```bash
# Export IPFS data
docker exec intermap tar -czf /data/ipfs-backup.tar.gz /data/ipfs

# Copy from container
docker cp intermap:/data/ipfs-backup.tar.gz ./

# Export graphs
docker exec intermap python -m src.cli export --format gexf
```

### Updates

```bash
# Pull latest image
docker pull jaylouisw/intermap:latest

# Stop and remove old container
docker stop intermap
docker rm intermap

# Run new container
docker run -d \
  --name intermap \
  --network host \
  --cap-add NET_ADMIN \
  --cap-add NET_RAW \
  --restart unless-stopped \
  jaylouisw/intermap:latest
```

---

## 📊 Resource Requirements

### Minimum Specs

- **CPU**: 1 vCPU
- **RAM**: 512 MB
- **Storage**: 2 GB
- **Network**: 1 Gbps shared

**Good for**: Testing, small networks

### Recommended Specs

- **CPU**: 2 vCPU
- **RAM**: 2 GB
- **Storage**: 10 GB SSD
- **Network**: 1 Gbps dedicated

**Good for**: Production, 100+ nodes mapped

### Heavy Workload

- **CPU**: 4 vCPU
- **RAM**: 4 GB
- **Storage**: 25 GB SSD
- **Network**: 10 Gbps

**Good for**: Large networks, datacenter deployments

---

## ❓ Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs intermap

# Check IPFS
docker exec intermap ipfs id

# Restart container
docker restart intermap
```

### Traceroute Not Working

**Problem**: `Operation not permitted` errors

**Solution**: Ensure capabilities are set:
```bash
docker run --cap-add NET_ADMIN --cap-add NET_RAW ...
```

### Port Already in Use

```bash
# Find what's using port 8000
netstat -tulpn | grep 8000

# Kill process or change port
docker run -p 8001:8000 ...
```

### IPFS Can't Connect

```bash
# Check IPFS daemon
docker exec intermap ipfs daemon --version

# Check swarm
docker exec intermap ipfs swarm peers

# Restart IPFS
docker restart intermap
```

---

## 📚 Additional Resources

- **Docker Documentation**: https://docs.docker.com/
- **IPFS Deployment**: https://docs.ipfs.io/how-to/
- **Railway Docs**: https://docs.railway.app/
- **Render Docs**: https://render.com/docs
- **Fly.io Docs**: https://fly.io/docs/

---

## 🆘 Need Help?

- **GitHub Issues**: [Report deployment problems](https://github.com/jaylouisw/intermap/issues)
- **Discussions**: [Ask deployment questions](https://github.com/jaylouisw/intermap/discussions)
- **Wiki**: [Check deployment wiki](https://github.com/jaylouisw/intermap/wiki/Deployment)

---

**Happy deploying!** 🚀 Help map the internet from the cloud!

