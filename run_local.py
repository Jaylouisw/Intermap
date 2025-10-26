"""
Run Intermap locally without Docker
Quick launcher for development/testing
"""
import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

print("Starting Intermap locally...")
print("=" * 60)

# Check Python dependencies
try:
    import aiohttp
    import yaml
    print("✓ Python dependencies installed")
except ImportError:
    print("Installing Python dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

# Check if IPFS is running
try:
    import aiohttp
    import asyncio
    
    async def check_ipfs():
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post('http://127.0.0.1:5001/api/v0/version') as resp:
                    if resp.status == 200:
                        return True
        except:
            return False
        return False
    
    if asyncio.run(check_ipfs()):
        print("✓ IPFS daemon is running")
    else:
        print("⚠ IPFS daemon not running!")
        print("  Please start IPFS:")
        print("  - Install from: https://dist.ipfs.tech/#kubo")
        print("  - Then run: ipfs daemon")
        sys.exit(1)
except Exception as e:
    print(f"⚠ Could not check IPFS: {e}")

# Start the application
print("\nStarting Intermap node...")
print("=" * 60)

# Start API server in background
api_process = subprocess.Popen(
    [sys.executable, "-m", "src.main"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

time.sleep(2)

# Check if frontend is built
frontend_build = Path("frontend/build")
if not frontend_build.exists():
    print("\nBuilding frontend...")
    subprocess.run(["npm", "install"], cwd="frontend", shell=True)
    subprocess.run(["npm", "run", "build"], cwd="frontend", shell=True)

# Start simple HTTP server for frontend
print("\nStarting web interface...")
ui_process = subprocess.Popen(
    [sys.executable, "-m", "http.server", "8000", "--directory", "frontend/build"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT
)

time.sleep(1)

print("\n" + "=" * 60)
print("✅ Intermap is running!")
print("=" * 60)
print("\n📍 Access points:")
print("  Web UI:   http://localhost:8000")
print("  API:      http://localhost:5000")
print("  IPFS API: http://localhost:5001")
print("\n Press Ctrl+C to stop\n")

# Open browser
time.sleep(1)
webbrowser.open("http://localhost:8000")

try:
    # Keep running
    api_process.wait()
except KeyboardInterrupt:
    print("\n\nStopping Intermap...")
    api_process.terminate()
    ui_process.terminate()
    print("Stopped.")
