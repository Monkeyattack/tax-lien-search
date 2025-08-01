#!/bin/bash
# Deployment script for Tax Lien Search to VPS Server
# Run this script on your VPS server (172.93.51.42)

set -e

echo "🚀 Deploying Tax Lien Search to VPS..."

# Configuration variables
APP_DIR="/var/www/tax-lien-search"
NGINX_SITE="tax-profithits"
DOMAIN="tax.profithits.app"
USER="www-data"

# Create application directory
echo "📁 Creating application directory..."
sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR

# Install Node.js if not present (for building React app)
if ! command -v node &> /dev/null; then
    echo "📦 Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

# Install Python if not present
if ! command -v python3 &> /dev/null; then
    echo "🐍 Installing Python..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-venv
fi

# Install PM2 for process management
if ! command -v pm2 &> /dev/null; then
    echo "⚙️ Installing PM2..."
    sudo npm install -g pm2
fi

# Clone or update repository
if [ -d "$APP_DIR/.git" ]; then
    echo "🔄 Updating existing repository..."
    cd $APP_DIR
    sudo -u $USER git pull origin main
else
    echo "📥 Cloning repository..."
    # You'll need to replace this with your actual repository URL
    # sudo -u $USER git clone <your-repo-url> $APP_DIR
    echo "❗ Please manually copy your project files to $APP_DIR"
fi

# Setup backend
echo "🔧 Setting up backend..."
cd $APP_DIR/backend
sudo -u $USER python3 -m venv venv
sudo -u $USER ./venv/bin/pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f "$APP_DIR/.env" ]; then
    echo "📝 Creating environment file..."
    sudo -u $USER cp $APP_DIR/.env.template $APP_DIR/.env
    echo "❗ Please edit $APP_DIR/.env with your configuration"
fi

# Initialize database
echo "🗄️ Initializing database..."
cd $APP_DIR
sudo -u $USER python3 -c "
import sys
sys.path.append('./backend')
from database import engine, Base
Base.metadata.create_all(bind=engine)
print('Database initialized successfully')
"

# Build frontend
echo "🏗️ Building frontend..."
cd $APP_DIR/frontend
sudo -u $USER npm install
sudo -u $USER npm run build

# Setup nginx
echo "🌐 Configuring nginx..."

# Create nginx site configuration
sudo tee /etc/nginx/sites-available/$NGINX_SITE > /dev/null << EOL
server {
    listen 80;
    server_name $DOMAIN;
    
    # Enable gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # Root directory for React build files
    root $APP_DIR/frontend/build;
    index index.html index.htm;
    
    # Handle client-side routing (React Router)
    location / {
        try_files \$uri \$uri/ /index.html;
    }
    
    # API proxy to backend
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        
        # CORS headers for API
        add_header 'Access-Control-Allow-Origin' 'https://$DOMAIN' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Accept,Authorization,Cache-Control,Content-Type,DNT,If-Modified-Since,Keep-Alive,Origin,User-Agent,X-Requested-With' always;
        
        # Handle preflight requests
        if (\$request_method = 'OPTIONS') {
            add_header 'Access-Control-Allow-Origin' 'https://$DOMAIN';
            add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS';
            add_header 'Access-Control-Allow-Headers' 'Accept,Authorization,Cache-Control,Content-Type,DNT,If-Modified-Since,Keep-Alive,Origin,User-Agent,X-Requested-With';
            add_header 'Access-Control-Max-Age' 1728000;
            add_header 'Content-Type' 'text/plain; charset=utf-8';
            add_header 'Content-Length' 0;
            return 204;
        }
    }
    
    # Static assets caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Manifest and service worker files
    location ~* \.(json|webmanifest)$ {
        expires 1d;
        add_header Cache-Control "public, must-revalidate";
    }
    
    # Security - deny access to hidden files
    location ~ /\. {
        deny all;
    }
    
    # Logging
    access_log /var/log/nginx/${NGINX_SITE}-access.log;
    error_log /var/log/nginx/${NGINX_SITE}-error.log;
}
EOL

# Enable the site
sudo ln -sf /etc/nginx/sites-available/$NGINX_SITE /etc/nginx/sites-enabled/

# Test nginx configuration
echo "🧪 Testing nginx configuration..."
sudo nginx -t

# Reload nginx
echo "🔄 Reloading nginx..."
sudo systemctl reload nginx

# Setup PM2 for backend process management
echo "🔧 Setting up PM2 for backend..."
cd $APP_DIR

# Create PM2 ecosystem file
sudo -u $USER tee ecosystem.config.js > /dev/null << EOL
module.exports = {
  apps: [{
    name: 'tax-lien-backend',
    script: './backend/venv/bin/python',
    args: './backend/main.py',
    cwd: '$APP_DIR',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production'
    }
  }]
};
EOL

# Start the backend with PM2
echo "🚀 Starting backend with PM2..."
sudo -u $USER pm2 start ecosystem.config.js
sudo -u $USER pm2 save
sudo -u $USER pm2 startup

echo "✅ Deployment completed!"
echo ""
echo "🌐 Your application should now be available at:"
echo "   Frontend: https://$DOMAIN"
echo "   Backend API: https://$DOMAIN/api"
echo ""
echo "📋 Next steps:"
echo "1. Edit $APP_DIR/.env with your configuration (SendGrid API key, etc.)"
echo "2. Restart the backend: sudo -u $USER pm2 restart tax-lien-backend"
echo "3. Check logs: sudo -u $USER pm2 logs tax-lien-backend"
echo "4. Monitor processes: sudo -u $USER pm2 monit"
echo ""
echo "📊 Useful commands:"
echo "   pm2 status              - Check process status"
echo "   pm2 logs tax-lien-backend - View backend logs"
echo "   pm2 restart tax-lien-backend - Restart backend"
echo "   sudo systemctl status nginx - Check nginx status"
echo "   sudo nginx -t           - Test nginx configuration"