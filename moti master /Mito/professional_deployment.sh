#!/bin/bash

# MitoAI Platform - Professional Deployment Script
# Creator: Daniel Guzman
# Contact: guzman.daniel@outlook.com
# Copyright: 2025 Daniel Guzman - All Rights Reserved
# 
# NO ONE IS AUTHORIZED TO ALTER THIS DEPLOYMENT SCRIPT 
# UNLESS AUTHORIZED BY DANIEL GUZMAN

set -e

echo "=========================================="
echo "MitoAI Platform Professional Deployment"
echo "Creator: Daniel Guzman"
echo "Contact: guzman.daniel@outlook.com"
echo "=========================================="

# Deployment Configuration
PROJECT_NAME="mitoai-platform"
PROJECT_DIR="/opt/mitoai"
SERVICE_USER="mitoai"
PYTHON_VERSION="3.9"

# System Update
echo "Step 1: System Update"
sudo apt update && sudo apt upgrade -y

# Install System Dependencies
echo "Step 2: Installing System Dependencies"
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    nginx \
    supervisor \
    git \
    curl \
    wget \
    unzip \
    build-essential \
    libpq-dev \
    redis-server

# Create Service User
echo "Step 3: Creating Service User"
if ! id "$SERVICE_USER" &>/dev/null; then
    sudo useradd --system --shell /bin/bash --home-dir $PROJECT_DIR --create-home $SERVICE_USER
fi

# Create Project Directory Structure
echo "Step 4: Setting Up Project Directory"
sudo mkdir -p $PROJECT_DIR/{app,logs,backups,static,templates}
sudo chown -R $SERVICE_USER:$SERVICE_USER $PROJECT_DIR

# Python Virtual Environment Setup
echo "Step 5: Creating Python Virtual Environment"
sudo -u $SERVICE_USER python3 -m venv $PROJECT_DIR/venv
sudo -u $SERVICE_USER $PROJECT_DIR/venv/bin/pip install --upgrade pip setuptools wheel

# Install Python Dependencies
echo "Step 6: Installing Python Dependencies"
sudo -u $SERVICE_USER $PROJECT_DIR/venv/bin/pip install -r requirements.txt

# Environment Configuration
echo "Step 7: Setting Up Environment Configuration"
sudo tee $PROJECT_DIR/.env > /dev/null <<EOF
# MitoAI Platform Environment Configuration
# Creator: Daniel Guzman - guzman.daniel@outlook.com

# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=mitoai-daniel-guzman-secure-key-2025

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Database Configuration (if needed)
DATABASE_URL=postgresql://username:password@localhost/mitoai

# Redis Configuration
REDIS_URL=redis://localhost:6379

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=$PROJECT_DIR/logs/mitoai.log

# Security Configuration
CORS_ORIGINS=*
RATE_LIMIT_STORAGE_URL=redis://localhost:6379
EOF

sudo chown $SERVICE_USER:$SERVICE_USER $PROJECT_DIR/.env
sudo chmod 600 $PROJECT_DIR/.env

# Gunicorn Configuration
echo "Step 8: Configuring Gunicorn"
sudo tee $PROJECT_DIR/gunicorn.conf.py > /dev/null <<EOF
# Gunicorn Configuration for MitoAI Platform
# Creator: Daniel Guzman

import multiprocessing

# Socket
bind = "127.0.0.1:8000"

# Worker Configuration
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2

# Logging
accesslog = "$PROJECT_DIR/logs/access.log"
errorlog = "$PROJECT_DIR/logs/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process Naming
proc_name = "mitoai-platform"

# Server Mechanics
daemon = False
pidfile = "$PROJECT_DIR/mitoai.pid"
user = "$SERVICE_USER"
group = "$SERVICE_USER"
tmp_upload_dir = None

# SSL (if needed)
# keyfile = "/path/to/ssl/key"
# certfile = "/path/to/ssl/cert"
EOF

# Supervisor Configuration
echo "Step 9: Configuring Supervisor"
sudo tee /etc/supervisor/conf.d/mitoai.conf > /dev/null <<EOF
[program:mitoai]
command=$PROJECT_DIR/venv/bin/gunicorn -c $PROJECT_DIR/gunicorn.conf.py app:app
directory=$PROJECT_DIR
user=$SERVICE_USER
group=$SERVICE_USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=$PROJECT_DIR/logs/supervisor.log
stdout_logfile_maxbytes=10MB
stdout_logfile_backups=5
environment=PATH="$PROJECT_DIR/venv/bin"
EOF

# Nginx Configuration
echo "Step 10: Configuring Nginx"
sudo tee /etc/nginx/sites-available/mitoai > /dev/null <<EOF
# MitoAI Platform Nginx Configuration
# Creator: Daniel Guzman - guzman.daniel@outlook.com

upstream mitoai_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name _;
    
    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # Rate Limiting
    limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone \$binary_remote_addr zone=static:10m rate=30r/s;
    
    # Static Files
    location /static/ {
        alias $PROJECT_DIR/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        limit_req zone=static burst=20 nodelay;
    }
    
    # API Endpoints
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        
        proxy_pass http://mitoai_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffer Settings
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }
    
    # Main Application
    location / {
        proxy_pass http://mitoai_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Health Check
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

# Enable Nginx Site
sudo ln -sf /etc/nginx/sites-available/mitoai /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx Configuration
sudo nginx -t

# Log Rotation Configuration
echo "Step 11: Setting Up Log Rotation"
sudo tee /etc/logrotate.d/mitoai > /dev/null <<EOF
$PROJECT_DIR/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 $SERVICE_USER $SERVICE_USER
    postrotate
        supervisorctl restart mitoai
    endscript
}
EOF

# Firewall Configuration
echo "Step 12: Configuring Firewall"
sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

# SSL Certificate Setup (Let's Encrypt)
echo "Step 13: SSL Certificate Setup"
sudo apt install -y certbot python3-certbot-nginx

# Create Backup Script
echo "Step 14: Creating Backup Script"
sudo tee $PROJECT_DIR/backup.sh > /dev/null <<EOF
#!/bin/bash
# MitoAI Platform Backup Script
# Creator: Daniel Guzman

BACKUP_DIR="$PROJECT_DIR/backups"
DATE=\$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p \$BACKUP_DIR

# Backup application files
tar -czf \$BACKUP_DIR/mitoai_app_\$DATE.tar.gz -C $PROJECT_DIR app static templates .env

# Backup logs
tar -czf \$BACKUP_DIR/mitoai_logs_\$DATE.tar.gz -C $PROJECT_DIR logs

# Remove backups older than 30 days
find \$BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: \$DATE"
EOF

sudo chmod +x $PROJECT_DIR/backup.sh
sudo chown $SERVICE_USER:$SERVICE_USER $PROJECT_DIR/backup.sh

# Setup Cron Jobs
echo "Step 15: Setting Up Cron Jobs"
sudo tee /tmp/mitoai_cron > /dev/null <<EOF
# MitoAI Platform Cron Jobs
# Daily backup at 2 AM
0 2 * * * $PROJECT_DIR/backup.sh >> $PROJECT_DIR/logs/backup.log 2>&1

# Weekly log cleanup
0 3 * * 0 find $PROJECT_DIR/logs -name "*.log.*" -mtime +7 -delete
EOF

sudo crontab -u $SERVICE_USER /tmp/mitoai_cron
sudo rm /tmp/mitoai_cron

# Service Management Scripts
echo "Step 16: Creating Service Management Scripts"

# Start Script
sudo tee $PROJECT_DIR/start.sh > /dev/null <<EOF
#!/bin/bash
echo "Starting MitoAI Platform..."
sudo supervisorctl start mitoai
sudo systemctl start nginx
echo "MitoAI Platform started successfully"
EOF

# Stop Script
sudo tee $PROJECT_DIR/stop.sh > /dev/null <<EOF
#!/bin/bash
echo "Stopping MitoAI Platform..."
sudo supervisorctl stop mitoai
echo "MitoAI Platform stopped successfully"
EOF

# Restart Script
sudo tee $PROJECT_DIR/restart.sh > /dev/null <<EOF
#!/bin/bash
echo "Restarting MitoAI Platform..."
sudo supervisorctl restart mitoai
sudo systemctl reload nginx
echo "MitoAI Platform restarted successfully"
EOF

# Status Script
sudo tee $PROJECT_DIR/status.sh > /dev/null <<EOF
#!/bin/bash
echo "MitoAI Platform Status:"
echo "======================="
sudo supervisorctl status mitoai
echo ""
echo "Nginx Status:"
sudo systemctl status nginx --no-pager -l
echo ""
echo "Recent Logs:"
tail -n 20 $PROJECT_DIR/logs/error.log
EOF

# Make scripts executable
sudo chmod +x $PROJECT_DIR/{start,stop,restart,status}.sh
sudo chown $SERVICE_USER:$SERVICE_USER $PROJECT_DIR/{start,stop,restart,status}.sh

# Final Service Startup
echo "Step 17: Starting Services"
sudo systemctl enable supervisor
sudo systemctl start supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start mitoai

sudo systemctl enable nginx
sudo systemctl start nginx

# Health Check
echo "Step 18: Health Check"
sleep 5

if curl -f http://localhost/api/platform-status > /dev/null 2>&1; then
    echo "SUCCESS: MitoAI Platform is running successfully"
    echo ""
    echo "Platform Information:"
    echo "===================="
    echo "Creator: Daniel Guzman"
    echo "Contact: guzman.daniel@outlook.com"
    echo "Platform URL: http://$(curl -s ifconfig.me)"
    echo "Local URL: http://localhost"
    echo "API Status: http://localhost/api/platform-status"
    echo ""
    echo "Management Commands:"
    echo "Start: $PROJECT_DIR/start.sh"
    echo "Stop: $PROJECT_DIR/stop.sh"
    echo "Restart: $PROJECT_DIR/restart.sh"
    echo "Status: $PROJECT_DIR/status.sh"
    echo ""
    echo "Log Files:"
    echo "Application: $PROJECT_DIR/logs/error.log"
    echo "Access: $PROJECT_DIR/logs/access.log"
    echo "Supervisor: $PROJECT_DIR/logs/supervisor.log"
    echo ""
    echo "Configuration Files:"
    echo "Environment: $PROJECT_DIR/.env"
    echo "Gunicorn: $PROJECT_DIR/gunicorn.conf.py"
    echo "Nginx: /etc/nginx/sites-available/mitoai"
    echo "Supervisor: /etc/supervisor/conf.d/mitoai.conf"
else
    echo "ERROR: Platform health check failed"
    echo "Check logs: $PROJECT_DIR/logs/error.log"
    exit 1
fi

# Security Hardening
echo "Step 19: Security Hardening"

# Set proper file permissions
sudo chown -R $SERVICE_USER:$SERVICE_USER $PROJECT_DIR
sudo chmod -R 755 $PROJECT_DIR
sudo chmod 600 $PROJECT_DIR/.env
sudo chmod 644 $PROJECT_DIR/logs/*.log 2>/dev/null || true

# Disable unnecessary services
sudo systemctl disable apache2 2>/dev/null || true
sudo systemctl stop apache2 2>/dev/null || true

# Configure fail2ban for additional security
sudo apt install -y fail2ban
sudo tee /etc/fail2ban/jail.local > /dev/null <<EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[nginx-http-auth]
enabled = true

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
logpath = $PROJECT_DIR/logs/error.log
maxretry = 10

[nginx-botsearch]
enabled = true
filter = nginx-botsearch
logpath = $PROJECT_DIR/logs/access.log
maxretry = 2
EOF

sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Final Security Check
echo "Step 20: Final Security Check"
echo "Checking file permissions..."
ls -la $PROJECT_DIR/
echo ""
echo "Checking service status..."
sudo supervisorctl status
echo ""
echo "Checking nginx status..."
sudo systemctl status nginx --no-pager
echo ""

# SSL Certificate Installation Reminder
echo "=========================================="
echo "DEPLOYMENT COMPLETED SUCCESSFULLY"
echo "=========================================="
echo ""
echo "IMPORTANT NEXT STEPS:"
echo "1. Update OpenAI API key in $PROJECT_DIR/.env"
echo "2. Configure domain name if needed"
echo "3. Install SSL certificate: sudo certbot --nginx -d yourdomain.com"
echo "4. Update firewall rules for your specific needs"
echo "5. Configure monitoring and alerting"
echo ""
echo "SECURITY REMINDERS:"
echo "- Change default secret keys in .env file"
echo "- Configure proper CORS origins"
echo "- Set up regular backups"
echo "- Monitor logs regularly"
echo "- Keep system updated"
echo ""
echo "SUPPORT:"
echo "Creator: Daniel Guzman"
echo "Contact: guzman.daniel@outlook.com"
echo ""
echo "Copyright: 2025 Daniel Guzman - All Rights Reserved"
echo "NO ONE IS AUTHORIZED TO ALTER THIS SOFTWARE"
echo "UNLESS AUTHORIZED BY DANIEL GUZMAN"
echo "=========================================="