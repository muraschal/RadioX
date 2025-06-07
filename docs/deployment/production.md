# 🏭 Production Deployment

<div align="center">

![Deployment Guide](https://img.shields.io/badge/guide-deployment-red)
![Difficulty](https://img.shields.io/badge/difficulty-advanced-red)
![Time](https://img.shields.io/badge/time-45%20min-orange)

**🚀 Complete guide to deploying RadioX in production environments**

[🏠 Documentation](../) • [🚀 Deployment Guides](../README.md#-deployment-guides) • [🐳 Docker](docker.md) • [📊 Monitoring](monitoring.md)

</div>

---

## 🎯 Overview

This guide covers **production deployment** of RadioX, from server setup to automated scheduling and monitoring.

### ✨ **Production Features**
- 🚀 **Automated Scheduling** - Cron-based show generation
- 🔄 **Service Management** - Systemd service configuration
- 📊 **Monitoring** - Health checks and logging
- 🔒 **Security** - API key management and access control
- 📈 **Scalability** - Load balancing and resource optimization

---

## 🏗️ Production Architecture

### **🌐 Deployment Options**

| 🎯 Option | 📝 Description | 🔧 Complexity | 💰 Cost |
|-----------|----------------|---------------|---------|
| **VPS Deployment** | Single server setup | Medium | Low |
| **Docker Compose** | Containerized services | Medium | Low |
| **Kubernetes** | Orchestrated containers | High | Medium |
| **Cloud Functions** | Serverless execution | Low | Variable |

### **🏭 Recommended Production Stack**

```
🌐 Load Balancer (Nginx)
├── 📻 RadioX Master Service
├── 🗄️ Supabase Database
├── 📁 File Storage (S3/Local)
└── 📊 Monitoring (Prometheus/Grafana)
```

---

## 🚀 VPS Deployment

### **🖥️ Server Requirements**

| Resource | Minimum | Recommended | Notes |
|----------|---------|-------------|-------|
| **CPU** | 2 cores | 4 cores | For audio processing |
| **RAM** | 4 GB | 8 GB | GPT-4 & audio generation |
| **Storage** | 50 GB | 100 GB | Audio files & logs |
| **Network** | 100 Mbps | 1 Gbps | API calls & file uploads |

### **🔧 Server Setup**

```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install Python 3.11
sudo apt install python3.11 python3.11-venv python3.11-pip -y

# 3. Install system dependencies
sudo apt install git nginx supervisor redis-server -y

# 4. Create RadioX user
sudo useradd -m -s /bin/bash radiox
sudo usermod -aG sudo radiox
```

### **📻 RadioX Installation**

```bash
# 1. Switch to RadioX user
sudo su - radiox

# 2. Clone repository
git clone https://github.com/your-org/RadioX.git
cd RadioX

# 3. Setup environment
./setup.sh

# 4. Configure production environment
cp .env.example .env
nano .env  # Add production API keys

# 5. Test installation
cd backend && python production/radiox_master.py --action system_status
```

### **⚙️ Environment Configuration**

```bash
# Production .env configuration
ENVIRONMENT=production
LOG_LEVEL=INFO
DEBUG=false

# API Keys (Production)
OPENAI_API_KEY=sk-prod-your-openai-key
ELEVENLABS_API_KEY=your-production-elevenlabs-key
COINMARKETCAP_API_KEY=your-production-coinmarketcap-key
WEATHER_API_KEY=your-production-weather-key

# Database (Production)
SUPABASE_URL=https://your-prod-project.supabase.co
SUPABASE_ANON_KEY=your-production-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-production-service-key

# Voice Configuration (Production)
ELEVENLABS_MARCEL_VOICE_ID=your-production-marcel-id
ELEVENLABS_JARVIS_VOICE_ID=your-production-jarvis-id
```

---

## 🔄 Service Management

### **🎛️ Systemd Service**

Create `/etc/systemd/system/radiox.service`:

```ini
[Unit]
Description=RadioX AI Radio Station Generator
After=network.target

[Service]
Type=simple
User=radiox
Group=radiox
WorkingDirectory=/home/radiox/RadioX/backend
Environment=PATH=/home/radiox/RadioX/venv/bin
ExecStart=/home/radiox/RadioX/venv/bin/python production/radiox_master.py --action generate_broadcast --generate-audio
Restart=always
RestartSec=300

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=radiox

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/home/radiox/RadioX/backend/output
ReadWritePaths=/home/radiox/RadioX/backend/logs

[Install]
WantedBy=multi-user.target
```

### **🔧 Service Management Commands**

```bash
# Enable and start service
sudo systemctl enable radiox
sudo systemctl start radiox

# Check status
sudo systemctl status radiox

# View logs
sudo journalctl -u radiox -f

# Restart service
sudo systemctl restart radiox
```

---

## ⏰ Automated Scheduling

### **📅 Cron Configuration**

```bash
# Edit crontab for radiox user
sudo crontab -u radiox -e

# Add scheduled broadcasts
# Morning show (6:00 AM)
0 6 * * * cd /home/radiox/RadioX/backend && /home/radiox/RadioX/venv/bin/python production/radiox_master.py --action generate_broadcast --time 06:00 --generate-audio

# Noon show (12:00 PM)
0 12 * * * cd /home/radiox/RadioX/backend && /home/radiox/RadioX/venv/bin/python production/radiox_master.py --action generate_broadcast --time 12:00 --generate-audio

# Evening show (6:00 PM)
0 18 * * * cd /home/radiox/RadioX/backend && /home/radiox/RadioX/venv/bin/python production/radiox_master.py --action generate_broadcast --time 18:00 --generate-audio

# Night show (10:00 PM)
0 22 * * * cd /home/radiox/RadioX/backend && /home/radiox/RadioX/venv/bin/python production/radiox_master.py --action generate_broadcast --time 22:00 --language de --generate-audio

# Cleanup old files (daily at 2:00 AM)
0 2 * * * cd /home/radiox/RadioX/backend && /home/radiox/RadioX/venv/bin/python production/radiox_master.py --action cleanup --cleanup-days 7

# System health check (every hour)
0 * * * * cd /home/radiox/RadioX/backend && /home/radiox/RadioX/venv/bin/python production/radiox_master.py --action system_status >> /home/radiox/RadioX/logs/health_check.log 2>&1
```

### **🔄 Advanced Scheduling**

```bash
# Create scheduling script
cat > /home/radiox/RadioX/scripts/schedule_shows.sh << 'EOF'
#!/bin/bash

RADIOX_DIR="/home/radiox/RadioX/backend"
PYTHON_BIN="/home/radiox/RadioX/venv/bin/python"
LOG_DIR="/home/radiox/RadioX/logs"

cd $RADIOX_DIR

# Function to generate show with error handling
generate_show() {
    local time=$1
    local language=${2:-en}
    local log_file="$LOG_DIR/scheduled_$(date +%Y%m%d_%H%M%S).log"
    
    echo "$(date): Generating $time show in $language" >> $log_file
    
    if $PYTHON_BIN production/radiox_master.py \
        --action generate_broadcast \
        --time $time \
        --language $language \
        --generate-audio >> $log_file 2>&1; then
        echo "$(date): Show generation successful" >> $log_file
    else
        echo "$(date): Show generation failed" >> $log_file
        # Send alert (email, Slack, etc.)
    fi
}

# Generate show based on current time
current_hour=$(date +%H)

case $current_hour in
    06) generate_show "06:00" "en" ;;
    12) generate_show "12:00" "en" ;;
    18) generate_show "18:00" "en" ;;
    22) generate_show "22:00" "de" ;;
esac
EOF

chmod +x /home/radiox/RadioX/scripts/schedule_shows.sh
```

---

## 🌐 Web Server Configuration

### **🔧 Nginx Configuration**

Create `/etc/nginx/sites-available/radiox`:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    
    # Serve static files
    location /output/ {
        alias /home/radiox/RadioX/backend/output/;
        expires 1d;
        add_header Cache-Control "public, immutable";
    }
    
    # API proxy (if using FastAPI)
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

### **🔒 SSL Certificate**

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

---

## 📊 Monitoring & Logging

### **📝 Log Configuration**

```bash
# Create log rotation configuration
sudo cat > /etc/logrotate.d/radiox << 'EOF'
/home/radiox/RadioX/backend/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 radiox radiox
    postrotate
        systemctl reload radiox
    endscript
}
EOF
```

### **🔍 Health Monitoring Script**

```bash
# Create monitoring script
cat > /home/radiox/RadioX/scripts/monitor.sh << 'EOF'
#!/bin/bash

RADIOX_DIR="/home/radiox/RadioX/backend"
PYTHON_BIN="/home/radiox/RadioX/venv/bin/python"
LOG_FILE="/home/radiox/RadioX/logs/monitor.log"

cd $RADIOX_DIR

# Check system status
if $PYTHON_BIN production/radiox_master.py --action system_status > /tmp/radiox_status.txt 2>&1; then
    echo "$(date): System healthy" >> $LOG_FILE
else
    echo "$(date): System unhealthy - sending alert" >> $LOG_FILE
    # Send alert (implement your notification method)
    cat /tmp/radiox_status.txt >> $LOG_FILE
fi

# Check disk space
DISK_USAGE=$(df /home/radiox/RadioX | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "$(date): Disk usage high: ${DISK_USAGE}%" >> $LOG_FILE
    # Send disk space alert
fi

# Check service status
if ! systemctl is-active --quiet radiox; then
    echo "$(date): RadioX service is down - restarting" >> $LOG_FILE
    sudo systemctl restart radiox
fi
EOF

chmod +x /home/radiox/RadioX/scripts/monitor.sh

# Add to crontab (every 5 minutes)
echo "*/5 * * * * /home/radiox/RadioX/scripts/monitor.sh" | sudo crontab -u radiox -
```

---

## 🔒 Security Configuration

### **🛡️ Firewall Setup**

```bash
# Configure UFW firewall
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH, HTTP, HTTPS
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Check status
sudo ufw status
```

### **🔑 API Key Security**

```bash
# Secure .env file permissions
chmod 600 /home/radiox/RadioX/.env
chown radiox:radiox /home/radiox/RadioX/.env

# Create backup of API keys (encrypted)
gpg --symmetric --cipher-algo AES256 /home/radiox/RadioX/.env
mv /home/radiox/RadioX/.env.gpg /home/radiox/backups/
```

### **📊 Security Monitoring**

```bash
# Install fail2ban for SSH protection
sudo apt install fail2ban -y

# Configure fail2ban
sudo cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
EOF

sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## 📈 Performance Optimization

### **⚡ System Optimization**

```bash
# Optimize Python performance
export PYTHONOPTIMIZE=1
export PYTHONDONTWRITEBYTECODE=1

# Add to .bashrc for radiox user
echo 'export PYTHONOPTIMIZE=1' >> /home/radiox/.bashrc
echo 'export PYTHONDONTWRITEBYTECODE=1' >> /home/radiox/.bashrc
```

### **🗄️ Database Optimization**

```sql
-- Supabase database optimization
-- Add indexes for frequently queried columns
CREATE INDEX IF NOT EXISTS idx_news_articles_published_at ON news_articles(published_at);
CREATE INDEX IF NOT EXISTS idx_broadcast_scripts_created_at ON broadcast_scripts(created_at);
CREATE INDEX IF NOT EXISTS idx_broadcast_logs_timestamp ON broadcast_logs(timestamp);

-- Clean up old data (run monthly)
DELETE FROM news_articles WHERE published_at < NOW() - INTERVAL '30 days';
DELETE FROM broadcast_logs WHERE timestamp < NOW() - INTERVAL '90 days';
```

---

## 🚨 Troubleshooting

### **Common Production Issues**

| 🚨 Issue | 🔍 Diagnosis | ✅ Solution |
|----------|-------------|-------------|
| Service won't start | Check logs: `journalctl -u radiox` | Fix .env or permissions |
| Audio generation fails | ElevenLabs quota | Check API credits |
| High CPU usage | Multiple concurrent generations | Implement queue system |
| Disk space full | Large audio files | Increase cleanup frequency |

### **🔧 Debug Commands**

```bash
# Check service status
sudo systemctl status radiox

# View recent logs
sudo journalctl -u radiox -n 50

# Test system manually
sudo su - radiox
cd RadioX/backend
python production/radiox_master.py --action system_status

# Check resource usage
htop
df -h
free -h
```

---

## 🔗 Related Guides

- **🐳 [Docker Deployment](docker.md)** - Containerized deployment
- **📊 [Monitoring](monitoring.md)** - Advanced monitoring setup
- **🏗️ [Architecture](../developer-guide/architecture.md)** - System design
- **🧪 [Testing](../developer-guide/testing.md)** - Production testing

---

<div align="center">

**🏭 Your RadioX production deployment is ready!**

[🏠 Documentation](../) • [🐳 Docker Setup](docker.md) • [💬 Get Help](../README.md#-support)

</div> 