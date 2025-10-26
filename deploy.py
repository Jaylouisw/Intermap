"""
Intermap Docker Deployment Script
Waits for Docker, builds image, and deploys container
"""
import subprocess
import sys
import time
import shutil

def check_docker():
    """Check if Docker is available."""
    return shutil.which("docker") is not None

def wait_for_docker():
    """Wait for Docker to be ready."""
    print("Checking for Docker...")
    while not check_docker():
        print("⏳ Waiting for Docker to be available...")
        print("   (Make sure Docker Desktop is running)")
        time.sleep(5)
    
    print("✓ Docker found!")
    
    # Wait for Docker daemon to be ready
    max_attempts = 12
    for i in range(max_attempts):
        try:
            result = subprocess.run(
                ["docker", "info"],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                print("✓ Docker daemon is ready!")
                return True
        except:
            pass
        
        print(f"⏳ Waiting for Docker daemon... ({i+1}/{max_attempts})")
        time.sleep(5)
    
    print("❌ Docker daemon not responding")
    return False

def build_image():
    """Build Docker image."""
    print("\n" + "="*60)
    print("Building Intermap Docker image...")
    print("="*60 + "\n")
    
    result = subprocess.run(["docker", "build", "-t", "intermap:latest", "."])
    
    if result.returncode != 0:
        print("\n❌ Build failed!")
        return False
    
    print("\n✅ Image built successfully!")
    return True

def deploy_container():
    """Deploy container using docker-compose."""
    print("\n" + "="*60)
    print("Deploying Intermap container...")
    print("="*60 + "\n")
    
    result = subprocess.run(["docker-compose", "up", "-d"])
    
    if result.returncode != 0:
        print("\n❌ Deployment failed!")
        return False
    
    print("\n✅ Container deployed successfully!")
    return True

def show_status():
    """Show container status and access info."""
    print("\n" + "="*60)
    print("Intermap is running!")
    print("="*60)
    print("\n📍 Access points:")
    print("   Web UI:    http://localhost:8000")
    print("   API:       http://localhost:5000")
    print("   IPFS API:  http://localhost:5001/webui")
    print("\n📊 Useful commands:")
    print("   View logs:     docker-compose logs -f")
    print("   Stop:          docker-compose down")
    print("   Restart:       docker-compose restart")
    print("   Status:        docker-compose ps")
    print("\n")

def main():
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║                                                               ║")
    print("║   🗺️  INTERMAP - Docker Deployment                          ║")
    print("║                                                               ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print()
    
    # Wait for Docker
    if not wait_for_docker():
        sys.exit(1)
    
    # Build image
    if not build_image():
        sys.exit(1)
    
    # Deploy container
    if not deploy_container():
        sys.exit(1)
    
    # Show status
    show_status()

if __name__ == "__main__":
    main()
