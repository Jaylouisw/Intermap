<!--
Intermap - GitHub Setup & Automated Docker Builds
Copyright (c) 2025 Jay Wenden
Licensed under CC-BY-NC-SA 4.0
-->

# GitHub Setup & Automated Docker Builds

*Created by Jay Wenden*

---

## Step 1: Initialize Git Repository

Run this script to set up git locally:
```powershell
.\setup_github.ps1
```

Or manually:
```bash
git init
git add .
git commit -m "Initial commit: Intermap distributed network topology mapper"
```

## Step 2: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: **intermap**
3. Description: **Distributed P2P Internet Topology Mapper using IPFS**
4. Public or Private (your choice)
5. **Don't** initialize with README (we already have one)
6. Click "Create repository"

## Step 3: Push to GitHub

Replace `jaylouisw` with your GitHub username:

```bash
git remote add origin https://github.com/jaylouisw/intermap.git
git branch -M main
git push -u origin main
```

## Step 4: Set Up Docker Hub

1. Go to https://hub.docker.com/settings/security
2. Click **"New Access Token"**
3. Description: **GitHub Actions**
4. Copy the token (you won't see it again!)

## Step 5: Add Secrets to GitHub

1. Go to your GitHub repo: `https://github.com/jaylouisw/intermap`
2. Click **Settings** > **Secrets and variables** > **Actions**
3. Click **"New repository secret"**
4. Add these two secrets:

   **Secret 1:**
   - Name: `DOCKERHUB_USERNAME`
   - Value: Your Docker Hub username
   
   **Secret 2:**
   - Name: `DOCKERHUB_TOKEN`
   - Value: The access token from Step 4

## Step 6: Automatic Builds

That's it! Now every time you:
- Push to `main` branch → Builds and pushes `latest` tag
- Create a tag like `v2.0.0` → Builds and pushes version-specific tag

The workflow file is already in `.github/workflows/docker-build.yml`

## Testing the Workflow

Trigger a build:
```bash
git tag v1.0.0
git push origin v1.0.0
```

Watch the build:
- Go to your repo > **Actions** tab
- You'll see the build running
- Takes ~10-15 minutes first time
- Docker image will appear at: `docker.io/jaylouisw/intermap:latest`

## Users Can Now Deploy With:

```bash
docker run -d -p 8000:8000 jaylouisw/intermap:latest
```

Or:
```bash
docker pull jaylouisw/intermap:latest
docker-compose up -d
```

## Multi-Platform Support

The workflow builds for:
- `linux/amd64` (Intel/AMD x86_64)
- `linux/arm64` (ARM like Raspberry Pi, Mac M1/M2)

So it works on almost any platform!

## Updating

To release a new version:
```bash
# Make your changes
git add .
git commit -m "Added new feature"
git push

# Create version tag
git tag v2.0.1
git push origin v2.0.1
```

GitHub Actions will automatically build and push the new version!

