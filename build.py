"""
Intermap - Distributed P2P Internet Topology Mapper
Copyright (c) 2025 Jay Wenden
Licensed under CC-BY-NC-SA 4.0
"""

import sys
import subprocess
import shutil

if not shutil.which("docker"):
    print("Docker not found. Install Docker Desktop:")
    print("https://www.docker.com/products/docker-desktop/")
    sys.exit(1)

print("Building Intermap Docker image...")
subprocess.run(["docker", "build", "-t", "intermap:latest", "."])
