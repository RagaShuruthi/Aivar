#!/bin/bash
# ====================================================================
# AWS EC2 / ECS Automated Production Deployment Script
# Agentic AI CRM Assistant with Permission Proxy (PS-2.2)
# ====================================================================

set -e

echo "--------------------------------------------------------"
echo "🚀 Starting AWS Production Deployment for Agentic AI CRM"
echo "--------------------------------------------------------"

# 1. Update package manager & install Docker + Docker Compose
echo "📦 Updating packages and installing Docker..."
sudo apt-get update -y
sudo apt-get install -y docker.io docker-compose curl git

# 2. Enable & start Docker service
echo "⚡ Starting Docker daemon..."
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER

# 3. Create .env file if missing
if [ ! -f .env ]; then
    echo "🔑 Creating production .env file..."
    echo "GEMINI_API_KEY=${GEMINI_API_KEY}" > .env
fi

# 4. Build and launch production Docker containers
echo "🛠️ Building and starting Docker containers..."
sudo docker-compose down || true
sudo docker-compose build --no-cache
sudo docker-compose up -d

# 5. Verify deployment health check
echo "⏳ Verifying backend API health check on port 8000..."
sleep 5
HEALTH_STATUS=$(curl -s http://localhost:8000/health | grep "healthy" || true)

if [ -n "$HEALTH_STATUS" ]; then
    echo "--------------------------------------------------------"
    echo "✅ PRODUCTION DEPLOYMENT SUCCESSFUL!"
    echo " Fast API Backend:  http://$(curl -s ifconfig.me):8000/docs"
    echo " Streamlit Web UI: http://$(curl -s ifconfig.me):8501"
    echo "--------------------------------------------------------"
else
    echo "❌ Health check failed. Inspecting logs:"
    sudo docker-compose logs --tail=50
    exit 1
fi
