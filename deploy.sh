#!/bin/bash

# Dala Deployment Script for Digital Ocean Droplet

set -e

echo "🚀 Starting Dala deployment..."

# Update system
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker
echo "🐳 Installing Docker..."
sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add current user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
echo "🔧 Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Git
echo "📝 Installing Git..."
sudo apt-get install -y git

# Clone repository
echo "📥 Cloning repository..."
cd /opt
sudo git clone https://github.com/takudzwachitsungo/dala.git
sudo chown -R $USER:$USER dala
cd dala

# Create .env file
echo "⚙️  Creating environment file..."
cat > .env << 'EOF'
# Database
POSTGRES_USER=dala_user
POSTGRES_PASSWORD=CHANGE_THIS_PASSWORD
POSTGRES_DB=dala_db

# JWT
JWT_SECRET_KEY=CHANGE_THIS_SECRET

# AI
ANTHROPIC_API_KEY=CHANGE_THIS_KEY

# Domain (optional)
DOMAIN=your-domain.com
EOF

echo "✏️  Please edit /opt/dala/.env with your actual credentials"
echo "   Run: nano /opt/dala/.env"
echo ""
echo "🔐 Generate JWT secret with: openssl rand -hex 32"
echo ""
read -p "Press Enter after editing .env file..."

# Build and start containers
echo "🏗️  Building and starting containers..."
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

echo "✅ Deployment complete!"
echo ""
echo "📍 Your app is running at: http://$(curl -s ifconfig.me)"
echo ""
echo "🔍 Check logs with: docker-compose -f docker-compose.prod.yml logs -f"
echo "🛑 Stop with: docker-compose -f docker-compose.prod.yml down"
echo ""
echo "🌐 To set up SSL, run: sudo certbot --nginx -d your-domain.com"
