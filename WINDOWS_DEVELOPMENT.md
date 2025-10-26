# Windows Development Setup for Intermap

This guide covers different ways to run Intermap on Windows with full ICMP traceroute support.

## The Problem: Windows Docker Desktop ICMP Limitation

**Windows Docker Desktop blocks raw ICMP packets** due to Hyper-V virtualization layer, even with `NET_ADMIN` and `NET_RAW` capabilities. This prevents standard ICMP traceroute from discovering network hops.

**Solution implemented**: Intermap now uses **ICMP with automatic TCP SYN fallback**:
- ✅ ICMP traceroute attempted first (standard protocol, best results)
- ✅ TCP SYN traceroute automatically used if ICMP blocked
- ✅ Works on all platforms: Linux, WSL2, macOS, Windows Docker Desktop

## Recommended Setup: WSL2 with Native Docker

This gives you native Linux performance with full ICMP support, without Docker Desktop overhead.

### Prerequisites
- Windows 10/11 (build 19041 or higher)
- WSL2 enabled
- 8GB+ RAM recommended

### Step 1: Install WSL2 Ubuntu

```powershell
# Install WSL2 and Ubuntu
wsl --install -d Ubuntu

# Set WSL2 as default
wsl --set-default-version 2

# Verify installation
wsl -l -v
```

### Step 2: Install Docker in WSL2 (Native, NOT Docker Desktop)

Open WSL2 Ubuntu terminal:

```bash
# Update packages
sudo apt update
sudo apt upgrade -y

# Install Docker dependencies
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Set up stable repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Start Docker service
sudo service docker start

# Add your user to docker group
sudo usermod -aG docker $USER

# Restart WSL to apply group changes
exit  # Then: wsl --shutdown from PowerShell
```

### Step 3: Enable Docker Autostart (Optional)

Create `/etc/wsl.conf` in WSL2:

```bash
sudo nano /etc/wsl.conf
```

Add:

```ini
[boot]
command="service docker start"
```

Save and exit. Docker will now start automatically when WSL2 boots.

### Step 4: Clone and Run Intermap

```bash
# Clone repository
cd ~
git clone https://github.com/Jaylouisw/Intermap.git
cd Intermap

# Create Docker volumes
docker volume create intermap-ipfs
docker volume create intermap-output

# Run Intermap with full capabilities
docker run -d \
  --name intermap \
  --cap-add=NET_ADMIN \
  --cap-add=NET_RAW \
  -p 5000:5000 \
  -v intermap-ipfs:/root/.ipfs \
  -v intermap-output:/app/output \
  jaylouisw/intermap:latest

# View logs
docker logs -f intermap
```

### Step 5: Access Web UI

From Windows browser: `http://localhost:5000`

Or from WSL2 IP:
```bash
# Get WSL2 IP
hostname -I | awk '{print $1}'
```

Then access: `http://<WSL2_IP>:5000` from Windows

## Alternative: Native Windows Python (No Docker)

For development/testing, run Python directly on Windows with admin privileges.

### Prerequisites
- Python 3.9+ installed
- Administrator privileges
- Git

### Installation

```powershell
# Clone repository
cd $env:USERPROFILE\Documents\Dev
git clone https://github.com/Jaylouisw/Intermap.git
cd Intermap

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Install IPFS
# Download from: https://dist.ipfs.tech/#kubo
# Add ipfs.exe to PATH
```

### Running as Administrator

```powershell
# Start PowerShell as Administrator
Start-Process powershell -Verb RunAs

# Activate venv and run
cd $env:USERPROFILE\Documents\Dev\Intermap
.\venv\Scripts\Activate.ps1
python src/main.py
```

**Why admin required**: Raw ICMP socket access needs elevated privileges on Windows.

## Alternative: Linux VM/Unraid/Cloud

For production deployments, use native Linux:

### Unraid
```bash
docker run -d \
  --name=intermap \
  --net=host \
  --cap-add=NET_ADMIN \
  --cap-add=NET_RAW \
  -v /mnt/user/appdata/intermap/ipfs:/root/.ipfs \
  -v /mnt/user/appdata/intermap/output:/app/output \
  jaylouisw/intermap:latest
```

### Digital Ocean / AWS / GCP
Use Docker or Kubernetes deployment with `NET_ADMIN` + `NET_RAW` capabilities.

## Traceroute Methods Comparison

| Method | Platform | Requires Root | Firewall Bypass | Best Results |
|--------|----------|---------------|-----------------|--------------|
| **ICMP** | Native Linux, WSL2, macOS | Yes | No | ✅ Yes |
| **TCP SYN** | All platforms | No | Yes | ⚠️ Good |
| **System tracert/traceroute** | Windows/Linux | No | Varies | ⚠️ Limited |

**Intermap automatically uses the best available method** for your platform.

## Troubleshooting

### ICMP Traceroute Shows 0 Hops

**Symptom**: Logs show "ICMP traceroute failed (likely blocked), falling back to TCP SYN"

**Causes**:
1. Windows Docker Desktop (Hyper-V blocks ICMP) ✅ **TCP fallback enabled**
2. Container missing capabilities: Add `--cap-add=NET_ADMIN --cap-add=NET_RAW`
3. Firewall blocking ICMP: Check host/network firewall rules

**Solution**: Use WSL2 with native Docker (this guide) or accept TCP SYN fallback.

### TCP Traceroute Still Failing

**Symptom**: Both ICMP and TCP show 0 hops

**Causes**:
1. Scapy not installed: `pip install scapy` in container
2. Target IP unreachable: Verify with `ping <target>`
3. Strict firewall: Test from different network

### Permission Denied on Native Python

**Symptom**: "Operation not permitted" when running traceroute

**Solution**: Run PowerShell as Administrator (required for raw sockets on Windows)

### WSL2 Docker Not Starting

```bash
# Check Docker status
sudo service docker status

# Restart Docker
sudo service docker restart

# Check for errors
sudo journalctl -u docker
```

## Performance Notes

**WSL2 Native Docker vs Docker Desktop**:
- ✅ 20-30% faster network I/O
- ✅ Full ICMP support (no fallback needed)
- ✅ Lower memory overhead
- ✅ Better integration with Linux tools
- ❌ Requires manual Docker installation
- ❌ No Docker Desktop GUI

## Security Considerations

**Why raw socket capabilities are needed**:
- ICMP traceroute requires crafting packets with specific TTL values
- TCP SYN traceroute needs to send raw TCP packets
- Both require `CAP_NET_ADMIN` and `CAP_NET_RAW` on Linux

**Is this safe?**
- ✅ Containers are isolated from host network
- ✅ Only network scanning capabilities granted, not filesystem access
- ✅ Intermap filters all private IPs before sharing data
- ⚠️ Don't run untrusted code with these capabilities

## Next Steps

1. **Choose your platform**: WSL2 (recommended) or native Python
2. **Deploy Intermap**: Follow installation steps above
3. **Monitor logs**: Check for "ICMP" vs "TCP SYN" in traceroute messages
4. **View topology**: Access web UI at http://localhost:5000
5. **Check performance**: ICMP should show better hop discovery than TCP

## References

- [WSL2 Installation Guide](https://docs.microsoft.com/en-us/windows/wsl/install)
- [Docker on WSL2](https://docs.docker.com/desktop/wsl/)
- [Scapy Documentation](https://scapy.readthedocs.io/)
- [ICMP RFC 792](https://tools.ietf.org/html/rfc792)
- [Intermap GitHub](https://github.com/Jaylouisw/Intermap)
