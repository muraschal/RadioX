# 📊 Monitoring Guide

<div align="center">

![Deployment Guide](https://img.shields.io/badge/guide-deployment-red)
![Difficulty](https://img.shields.io/badge/difficulty-intermediate-yellow)
![Time](https://img.shields.io/badge/time-25%20min-orange)

**📈 Complete guide to monitoring RadioX in production**

[🏠 Documentation](../) • [🚀 Deployment Guides](../README.md#-deployment-guides) • [🏭 Production](production.md) • [🐳 Docker](docker.md)

</div>

---

## 🎯 Overview

This guide covers **comprehensive monitoring** of RadioX, from basic health checks to advanced metrics collection and alerting.

### ✨ **Monitoring Features**
- 📊 **System Metrics** - CPU, memory, disk usage
- 🔍 **Application Health** - Service status and performance
- 📝 **Log Aggregation** - Centralized logging and analysis
- 🚨 **Alerting** - Proactive issue notification
- 📈 **Performance Tracking** - Generation times and success rates

---

## 🔍 Built-in Monitoring

### **📊 System Status Checks**

RadioX includes built-in monitoring capabilities:

```bash
# Complete system status
python production/radiox_master.py --action system_status

# Individual service tests
python cli/cli_master.py test
python cli/cli_audio.py test
python cli/cli_crypto.py test
python cli/cli_rss.py test
```

### **📈 Health Check Output**

```bash
📊 RadioX System Status Report
==============================

🔑 API Keys Status:
   ✅ OpenAI: Valid (GPT-4 & DALL-E access)
   ✅ ElevenLabs: Valid (12,450 characters remaining)
   ✅ CoinMarketCap: Valid (Pro plan)
   ✅ Weather API: Valid (1,000 calls/day)

🗄️ Database Status:
   ✅ Supabase: Connected (eu-central-1)
   ✅ Tables: 5/5 accessible
   ✅ Recent Activity: 23 broadcasts in last 7 days

📊 Performance Metrics:
   ⏱️ Avg Generation Time: 45 seconds
   🎵 Avg Audio Duration: 12 minutes
   📁 Storage Used: 2.3 GB
   🔄 Success Rate: 98.7%

🎉 SYSTEM HEALTHY! Ready for production use.
```

---

## 📝 Log Management

### **🗂️ Log Structure**

RadioX generates structured logs in multiple locations:

```
backend/logs/
├── radiox_master_20240101.log      # Main application logs
├── audio_generation_20240101.log   # Audio service logs
├── broadcast_generation_20240101.log # Broadcast logs
├── system_monitoring_20240101.log  # System health logs
└── error_20240101.log              # Error logs
```

### **📊 Log Rotation Configuration**

```bash
# Create logrotate configuration
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

### **🔍 Log Analysis Commands**

```bash
# View recent errors
tail -f backend/logs/error_$(date +%Y%m%d).log

# Search for specific issues
grep -i "error\|failed\|exception" backend/logs/radiox_master_*.log

# Monitor real-time logs
tail -f backend/logs/radiox_master_$(date +%Y%m%d).log

# Analyze performance
grep "Generation completed" backend/logs/radiox_master_*.log | tail -20
```

---

## 📈 Prometheus & Grafana Setup

### **🔧 Prometheus Configuration**

Create `monitoring/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "radiox_rules.yml"

scrape_configs:
  - job_name: 'radiox'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']

  - job_name: 'nginx'
    static_configs:
      - targets: ['localhost:9113']

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

### **📊 Grafana Dashboard**

Create `monitoring/grafana-dashboard.json`:

```json
{
  "dashboard": {
    "title": "RadioX Monitoring Dashboard",
    "panels": [
      {
        "title": "System Health",
        "type": "stat",
        "targets": [
          {
            "expr": "radiox_system_health",
            "legendFormat": "System Status"
          }
        ]
      },
      {
        "title": "Generation Success Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(radiox_broadcasts_total[5m])",
            "legendFormat": "Successful Generations"
          },
          {
            "expr": "rate(radiox_broadcasts_failed_total[5m])",
            "legendFormat": "Failed Generations"
          }
        ]
      },
      {
        "title": "Average Generation Time",
        "type": "graph",
        "targets": [
          {
            "expr": "radiox_generation_duration_seconds",
            "legendFormat": "Generation Time"
          }
        ]
      },
      {
        "title": "API Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "radiox_api_calls_total",
            "legendFormat": "{{service}}"
          }
        ]
      }
    ]
  }
}
```

### **🐳 Docker Compose Monitoring Stack**

Create `monitoring/docker-compose.monitoring.yml`:

```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: radiox-prometheus
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - ./radiox_rules.yml:/etc/prometheus/radiox_rules.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'

  grafana:
    image: grafana/grafana:latest
    container_name: radiox-grafana
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=radiox_admin
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana-dashboard.json:/var/lib/grafana/dashboards/radiox.json

  node-exporter:
    image: prom/node-exporter:latest
    container_name: radiox-node-exporter
    restart: unless-stopped
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.rootfs=/rootfs'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'

  alertmanager:
    image: prom/alertmanager:latest
    container_name: radiox-alertmanager
    restart: unless-stopped
    ports:
      - "9093:9093"
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml

volumes:
  prometheus-data:
  grafana-data:
```

---

## 🚨 Alerting Configuration

### **⚠️ Prometheus Alert Rules**

Create `monitoring/radiox_rules.yml`:

```yaml
groups:
  - name: radiox_alerts
    rules:
      - alert: RadioXServiceDown
        expr: up{job="radiox"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "RadioX service is down"
          description: "RadioX service has been down for more than 1 minute"

      - alert: HighGenerationFailureRate
        expr: rate(radiox_broadcasts_failed_total[5m]) > 0.1
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High broadcast generation failure rate"
          description: "Broadcast generation failure rate is {{ $value }} per second"

      - alert: LongGenerationTime
        expr: radiox_generation_duration_seconds > 300
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "Broadcast generation taking too long"
          description: "Generation time is {{ $value }} seconds"

      - alert: APIQuotaLow
        expr: radiox_api_quota_remaining < 1000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "API quota running low"
          description: "{{ $labels.service }} quota remaining: {{ $value }}"

      - alert: DiskSpaceHigh
        expr: (node_filesystem_avail_bytes / node_filesystem_size_bytes) * 100 < 10
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Disk space critically low"
          description: "Disk space is {{ $value }}% full"
```

### **📧 Alertmanager Configuration**

Create `monitoring/alertmanager.yml`:

```yaml
global:
  smtp_smarthost: 'localhost:587'
  smtp_from: 'alerts@radiox.ai'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
  - name: 'web.hook'
    email_configs:
      - to: 'admin@radiox.ai'
        subject: 'RadioX Alert: {{ .GroupLabels.alertname }}'
        body: |
          {{ range .Alerts }}
          Alert: {{ .Annotations.summary }}
          Description: {{ .Annotations.description }}
          {{ end }}
    
    slack_configs:
      - api_url: 'YOUR_SLACK_WEBHOOK_URL'
        channel: '#radiox-alerts'
        title: 'RadioX Alert'
        text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'

inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'dev', 'instance']
```

---

## 📱 Health Check Scripts

### **🔍 Comprehensive Health Monitor**

Create `monitoring/health_monitor.sh`:

```bash
#!/bin/bash

# RadioX Health Monitor Script
RADIOX_DIR="/home/radiox/RadioX/backend"
LOG_FILE="/home/radiox/RadioX/logs/health_monitor.log"
ALERT_WEBHOOK="YOUR_WEBHOOK_URL"

cd $RADIOX_DIR

# Function to send alert
send_alert() {
    local message="$1"
    local severity="$2"
    
    echo "$(date): $severity - $message" >> $LOG_FILE
    
    # Send to webhook (Slack, Discord, etc.)
    curl -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\"🚨 RadioX Alert: $message\"}" \
        $ALERT_WEBHOOK
}

# Check system status
echo "$(date): Running health check..." >> $LOG_FILE

if ! python production/radiox_master.py --action system_status > /tmp/radiox_health.txt 2>&1; then
    send_alert "System health check failed" "CRITICAL"
    cat /tmp/radiox_health.txt >> $LOG_FILE
    exit 1
fi

# Check disk space
DISK_USAGE=$(df /home/radiox/RadioX | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 85 ]; then
    send_alert "Disk usage high: ${DISK_USAGE}%" "WARNING"
fi

# Check memory usage
MEMORY_USAGE=$(free | grep Mem | awk '{printf("%.0f", $3/$2 * 100.0)}')
if [ $MEMORY_USAGE -gt 90 ]; then
    send_alert "Memory usage high: ${MEMORY_USAGE}%" "WARNING"
fi

# Check recent generation success
RECENT_FAILURES=$(grep -c "Generation failed" logs/radiox_master_$(date +%Y%m%d).log 2>/dev/null || echo 0)
if [ $RECENT_FAILURES -gt 3 ]; then
    send_alert "Multiple generation failures: $RECENT_FAILURES in last day" "WARNING"
fi

# Check API quotas
python -c "
import os
import requests
import sys

# Check ElevenLabs quota
try:
    response = requests.get(
        'https://api.elevenlabs.io/v1/user/subscription',
        headers={'xi-api-key': os.getenv('ELEVENLABS_API_KEY')}
    )
    if response.status_code == 200:
        data = response.json()
        remaining = data.get('character_limit', 0) - data.get('character_count', 0)
        if remaining < 5000:
            print(f'ElevenLabs quota low: {remaining} characters remaining')
            sys.exit(1)
except Exception as e:
    print(f'Failed to check ElevenLabs quota: {e}')
    sys.exit(1)
" 2>/dev/null || send_alert "API quota check failed or quota low" "WARNING"

echo "$(date): Health check completed successfully" >> $LOG_FILE
```

### **📊 Performance Monitor**

Create `monitoring/performance_monitor.py`:

```python
#!/usr/bin/env python3
"""
RadioX Performance Monitor
Tracks generation times, success rates, and system metrics
"""

import os
import json
import time
import psutil
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

class RadioXMonitor:
    def __init__(self):
        self.db_path = "/home/radiox/RadioX/monitoring/metrics.db"
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for metrics"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                timestamp DATETIME,
                metric_name TEXT,
                metric_value REAL,
                tags TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def record_metric(self, name, value, tags=None):
        """Record a metric to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO metrics (timestamp, metric_name, metric_value, tags) VALUES (?, ?, ?, ?)',
            (datetime.now(), name, value, json.dumps(tags or {}))
        )
        
        conn.commit()
        conn.close()
    
    def collect_system_metrics(self):
        """Collect system performance metrics"""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        self.record_metric('system.cpu_percent', cpu_percent)
        
        # Memory usage
        memory = psutil.virtual_memory()
        self.record_metric('system.memory_percent', memory.percent)
        self.record_metric('system.memory_available_gb', memory.available / (1024**3))
        
        # Disk usage
        disk = psutil.disk_usage('/home/radiox/RadioX')
        disk_percent = (disk.used / disk.total) * 100
        self.record_metric('system.disk_percent', disk_percent)
        self.record_metric('system.disk_free_gb', disk.free / (1024**3))
        
        # Load average
        load_avg = os.getloadavg()
        self.record_metric('system.load_1min', load_avg[0])
        self.record_metric('system.load_5min', load_avg[1])
        self.record_metric('system.load_15min', load_avg[2])
    
    def analyze_generation_performance(self):
        """Analyze broadcast generation performance from logs"""
        log_dir = Path("/home/radiox/RadioX/backend/logs")
        today = datetime.now().strftime("%Y%m%d")
        log_file = log_dir / f"radiox_master_{today}.log"
        
        if not log_file.exists():
            return
        
        generation_times = []
        success_count = 0
        failure_count = 0
        
        with open(log_file, 'r') as f:
            for line in f:
                if "Generation completed" in line:
                    success_count += 1
                    # Extract generation time if logged
                    if "in" in line and "seconds" in line:
                        try:
                            time_str = line.split("in")[1].split("seconds")[0].strip()
                            generation_times.append(float(time_str))
                        except:
                            pass
                elif "Generation failed" in line:
                    failure_count += 1
        
        # Record metrics
        total_generations = success_count + failure_count
        if total_generations > 0:
            success_rate = (success_count / total_generations) * 100
            self.record_metric('radiox.success_rate_percent', success_rate)
        
        self.record_metric('radiox.successful_generations', success_count)
        self.record_metric('radiox.failed_generations', failure_count)
        
        if generation_times:
            avg_time = sum(generation_times) / len(generation_times)
            self.record_metric('radiox.avg_generation_time_seconds', avg_time)
            self.record_metric('radiox.max_generation_time_seconds', max(generation_times))
    
    def check_output_directory(self):
        """Monitor output directory size and file count"""
        output_dir = Path("/home/radiox/RadioX/backend/output")
        
        if not output_dir.exists():
            return
        
        total_size = 0
        file_count = 0
        
        for file_path in output_dir.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
                file_count += 1
        
        self.record_metric('radiox.output_size_gb', total_size / (1024**3))
        self.record_metric('radiox.output_file_count', file_count)
    
    def generate_report(self):
        """Generate performance report"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get metrics from last 24 hours
        yesterday = datetime.now() - timedelta(days=1)
        
        cursor.execute('''
            SELECT metric_name, AVG(metric_value), MAX(metric_value), MIN(metric_value)
            FROM metrics 
            WHERE timestamp > ? 
            GROUP BY metric_name
        ''', (yesterday,))
        
        metrics = cursor.fetchall()
        
        print("📊 RadioX Performance Report (Last 24h)")
        print("=" * 50)
        
        for metric_name, avg_val, max_val, min_val in metrics:
            print(f"{metric_name}:")
            print(f"  Average: {avg_val:.2f}")
            print(f"  Maximum: {max_val:.2f}")
            print(f"  Minimum: {min_val:.2f}")
            print()
        
        conn.close()

if __name__ == "__main__":
    monitor = RadioXMonitor()
    
    # Collect all metrics
    monitor.collect_system_metrics()
    monitor.analyze_generation_performance()
    monitor.check_output_directory()
    
    # Generate report if requested
    if len(os.sys.argv) > 1 and os.sys.argv[1] == "--report":
        monitor.generate_report()
```

---

## 🔄 Automated Monitoring Setup

### **⏰ Cron Jobs for Monitoring**

```bash
# Add to radiox user crontab
sudo crontab -u radiox -e

# Health check every 5 minutes
*/5 * * * * /home/radiox/RadioX/monitoring/health_monitor.sh

# Performance metrics every minute
* * * * * /home/radiox/RadioX/venv/bin/python /home/radiox/RadioX/monitoring/performance_monitor.py

# Daily performance report
0 8 * * * /home/radiox/RadioX/venv/bin/python /home/radiox/RadioX/monitoring/performance_monitor.py --report | mail -s "RadioX Daily Report" admin@radiox.ai

# Weekly log cleanup
0 2 * * 0 find /home/radiox/RadioX/backend/logs -name "*.log" -mtime +30 -delete
```

### **🐳 Docker Monitoring**

For Docker deployments, add monitoring to `docker-compose.yml`:

```yaml
services:
  radiox-monitor:
    build: .
    container_name: radiox-monitor
    restart: unless-stopped
    volumes:
      - ./backend/logs:/app/logs:ro
      - ./monitoring:/app/monitoring
    command: >
      sh -c "
        while true; do
          python /app/monitoring/performance_monitor.py
          sleep 60
        done
      "
    networks:
      - radiox-network
```

---

## 📱 Mobile Alerts

### **📲 Slack Integration**

```python
# monitoring/slack_alerts.py
import requests
import json

def send_slack_alert(message, severity="INFO"):
    webhook_url = "YOUR_SLACK_WEBHOOK_URL"
    
    color_map = {
        "INFO": "#36a64f",
        "WARNING": "#ff9500", 
        "CRITICAL": "#ff0000"
    }
    
    payload = {
        "attachments": [
            {
                "color": color_map.get(severity, "#36a64f"),
                "fields": [
                    {
                        "title": f"RadioX Alert ({severity})",
                        "value": message,
                        "short": False
                    }
                ]
            }
        ]
    }
    
    response = requests.post(webhook_url, json=payload)
    return response.status_code == 200
```

### **📧 Email Alerts**

```python
# monitoring/email_alerts.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_alert(subject, message, to_email):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    from_email = "alerts@radiox.ai"
    password = "your_app_password"
    
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    
    msg.attach(MIMEText(message, 'plain'))
    
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(from_email, password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
```

---

## 🔗 Related Guides

- **🏭 [Production Deployment](production.md)** - Production setup and configuration
- **🐳 [Docker Deployment](docker.md)** - Containerized monitoring
- **🏗️ [Architecture](../developer-guide/architecture.md)** - System design
- **🧪 [Testing](../developer-guide/testing.md)** - Testing and validation

---

<div align="center">

**📊 Your RadioX monitoring is now enterprise-ready!**

[🏠 Documentation](../) • [🏭 Production](production.md) • [💬 Get Help](../README.md#-support)

</div> 