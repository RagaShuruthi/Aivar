#!/bin/bash
# ====================================================================
# AWS EC2 Automated Production Deployment Script
# Enterprise CRM Security Portal
# ====================================================================

set -e

echo "--------------------------------------------------------"
echo "Starting AWS Production Deployment"
echo "--------------------------------------------------------"

# 1. Update package manager & install Docker + Docker Compose
echo "[1/5] Updating packages and installing Docker..."
sudo apt-get update -y
sudo apt-get install -y docker.io docker-compose curl git

# 2. Enable & start Docker service
echo "[2/5] Starting Docker daemon..."
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER || true

# 3. Create .env file if missing
if [ ! -f .env ]; then
    echo "[3/5] Creating production .env file..."
    echo "GEMINI_API_KEY=${GEMINI_API_KEY}" > .env
fi

# 4. Build and launch production Docker containers
echo "[4/5] Building and starting Docker containers..."
sudo docker-compose down || true
sudo docker-compose build --no-cache
sudo docker-compose up -d

# 5. Verify deployment health check
echo "[5/5] Verifying backend API health check on port 8000..."
sleep 5
HEALTH_STATUS=$(curl -s http://localhost:8000/health | grep "healthy" || true)

if [ -n "$HEALTH_STATUS" ]; then
    PUBLIC_IP=$(curl -s ifconfig.me || echo "server-ip")
    echo "--------------------------------------------------------"
    echo "PRODUCTION DEPLOYMENT SUCCESSFUL"
    echo " FastAPI Backend:  http://${PUBLIC_IP}:8000/docs"
    echo " Streamlit Web UI: http://${PUBLIC_IP}:8501"
    echo "--------------------------------------------------------"
else
    echo "Health check failed. Inspecting logs:"
    sudo docker-compose logs --tail=50
    exit 1
fi
