#!/bin/bash
# MitoAI Deployment Script
# © 2025 Daniel Guzman - All Rights Reserved
# Contact: guzman.daniel@outlook.com

echo "🚀 Deploying MitoAI Platform by Daniel Guzman"

# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install Python and pip
sudo apt install python3 python3-pip python3-venv nginx -y

# 3. Create project directory
mkdir -p /home/mitoai
cd /home/mitoai

# 4. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 5. Install dependencies
pip install -r requirements.txt

# 6. Set environment variables
echo "Setting up environment variables..."
echo "export OPENAI_API_KEY='your-openai-key-here'" >> ~/.bashrc
echo "export FLASK_ENV='production'" >> ~/.bashrc
source ~/.bashrc

# 7. Create systemd service for auto-start
sudo tee /etc/systemd/system/mitoai.service > /dev/null <<EOF
[Unit]
Description=MitoAI Platform by Daniel Guzman
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/mitoai
Environment=PATH=/home/mitoai/venv/bin
Environment=OPENAI_API_KEY=your-openai-key-here
Environment=FLASK_ENV=production
ExecStart=/home/mitoai/venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 2 app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 8. Configure Nginx reverse proxy
sudo tee /etc/nginx/sites-available/mitoai > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# 9. Enable Nginx configuration
sudo ln -s /etc/nginx/sites-available/mitoai /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# 10. Start MitoAI service
sudo systemctl daemon-reload
sudo systemctl enable mitoai
sudo systemctl start mitoai

# 11. Configure firewall
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable

echo "✅ MitoAI Platform deployed successfully!"
echo "🌐 Access your platform at: http://YOUR-VM-EXTERNAL-IP"
echo "📧 Contact Daniel Guzman: guzman.daniel@outlook.com"
echo ""
echo "To check status: sudo systemctl status mitoai"
echo "To view logs: sudo journalctl -u mitoai -f"