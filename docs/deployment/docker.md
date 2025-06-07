# 🐳 Docker Deployment

<div align="center">

![Deployment Guide](https://img.shields.io/badge/guide-deployment-red)
![Difficulty](https://img.shields.io/badge/difficulty-intermediate-yellow)
![Time](https://img.shields.io/badge/time-30%20min-orange)

**🚀 Complete guide to containerized RadioX deployment**

[🏠 Documentation](../) • [🚀 Deployment Guides](../README.md#-deployment-guides) • [🏭 Production](production.md) • [📊 Monitoring](monitoring.md)

</div>

---

## 🎯 Overview

This guide covers **containerized deployment** of RadioX using Docker and Docker Compose for scalable, portable, and maintainable deployments.

### ✨ **Docker Benefits**
- 🚀 **Portable** - Run anywhere Docker is supported
- 🔄 **Scalable** - Easy horizontal scaling
- 🛡️ **Isolated** - Clean environment separation
- 📦 **Reproducible** - Consistent deployments

---

## 🐳 Docker Setup

### **📋 Prerequisites**

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

### **🔧 Project Structure**

```
RadioX/
├── 🐳 Dockerfile              # Main application container
├── 🔧 docker-compose.yml      # Multi-service orchestration
├── 🔧 docker-compose.prod.yml # Production overrides
├── 📁 docker/
│   ├── nginx.conf             # Nginx configuration
│   └── entrypoint.sh          # Container startup script
└── 📻 backend/                # Application code
```

---

## 📦 Dockerfile

### **🐳 Main Application Container**

Create `Dockerfile` in project root:

```dockerfile
# RadioX AI Radio Station Generator
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONOPTIMIZE=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd --create-home --shell /bin/bash radiox

# Set work directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ .
COPY setup_env.py /app/
COPY .env.example /app/

# Create necessary directories
RUN mkdir -p output logs && \
    chown -R radiox:radiox /app

# Copy entrypoint script
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Switch to app user
USER radiox

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python production/radiox_master.py --action system_status || exit 1

# Default command
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "production/radiox_master.py", "--action", "generate_broadcast", "--generate-audio"]
```

### **🚀 Entrypoint Script**

Create `docker/entrypoint.sh`:

```bash
#!/bin/bash
set -e

# Wait for environment setup
echo "🔧 Setting up RadioX environment..."

# Check if .env exists, if not create from template
if [ ! -f .env ]; then
    echo "📋 Creating .env from template..."
    cp .env.example .env
fi

# Run environment setup
python setup_env.py

# Validate system status
echo "🧪 Testing system status..."
python production/radiox_master.py --action system_status

echo "🚀 RadioX container ready!"

# Execute the main command
exec "$@"
```

---

## 🔧 Docker Compose

### **🎛️ Development Configuration**

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  radiox:
    build: .
    container_name: radiox-app
    restart: unless-stopped
    environment:
      - ENVIRONMENT=development
      - LOG_LEVEL=DEBUG
    env_file:
      - .env
    volumes:
      - ./backend/output:/app/output
      - ./backend/logs:/app/logs
      - ./backend/.env:/app/.env
    ports:
      - "8000:8000"
    networks:
      - radiox-network
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    container_name: radiox-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - radiox-network

  nginx:
    image: nginx:alpine
    container_name: radiox-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx.conf:/etc/nginx/nginx.conf
      - ./backend/output:/var/www/output:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - radiox
    networks:
      - radiox-network

volumes:
  redis-data:

networks:
  radiox-network:
    driver: bridge
```

### **🏭 Production Configuration**

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  radiox:
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
      - DEBUG=false
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
      restart_policy:
        condition: on-failure
        delay: 30s
        max_attempts: 3

  scheduler:
    build: .
    container_name: radiox-scheduler
    restart: unless-stopped
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
    env_file:
      - .env
    volumes:
      - ./backend/output:/app/output
      - ./backend/logs:/app/logs
    command: >
      sh -c "
        # Morning show (6:00 AM)
        echo '0 6 * * * python production/radiox_master.py --action generate_broadcast --time 06:00 --generate-audio' | crontab -
        # Noon show (12:00 PM)
        echo '0 12 * * * python production/radiox_master.py --action generate_broadcast --time 12:00 --generate-audio' | crontab -
        # Evening show (6:00 PM)
        echo '0 18 * * * python production/radiox_master.py --action generate_broadcast --time 18:00 --generate-audio' | crontab -
        # Night show (10:00 PM)
        echo '0 22 * * * python production/radiox_master.py --action generate_broadcast --time 22:00 --language de --generate-audio' | crontab -
        # Cleanup (2:00 AM daily)
        echo '0 2 * * * python production/radiox_master.py --action cleanup --cleanup-days 7' | crontab -
        crond -f
      "
    networks:
      - radiox-network

  nginx:
    volumes:
      - ./docker/nginx.prod.conf:/etc/nginx/nginx.conf
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
```

---

## 🌐 Nginx Configuration

### **🔧 Development Nginx**

Create `docker/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    upstream radiox_backend {
        server radiox:8000;
    }

    server {
        listen 80;
        server_name localhost;

        # Serve static files
        location /output/ {
            alias /var/www/output/;
            expires 1d;
            add_header Cache-Control "public, immutable";
        }

        # API proxy
        location /api/ {
            proxy_pass http://radiox_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health check
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }

        # Default location
        location / {
            proxy_pass http://radiox_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

### **🏭 Production Nginx**

Create `docker/nginx.prod.conf`:

```nginx
events {
    worker_connections 2048;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=static:10m rate=30r/s;

    upstream radiox_backend {
        least_conn;
        server radiox:8000 max_fails=3 fail_timeout=30s;
    }

    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        # SSL Configuration
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        # Serve static files with rate limiting
        location /output/ {
            limit_req zone=static burst=20 nodelay;
            alias /var/www/output/;
            expires 1d;
            add_header Cache-Control "public, immutable";
        }

        # API with rate limiting
        location /api/ {
            limit_req zone=api burst=5 nodelay;
            proxy_pass http://radiox_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health check
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
```

---

## 🚀 Deployment Commands

### **🔧 Development Deployment**

```bash
# Build and start services
docker-compose up --build -d

# View logs
docker-compose logs -f radiox

# Check status
docker-compose ps

# Stop services
docker-compose down
```

### **🏭 Production Deployment**

```bash
# Build and start production services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d

# Scale RadioX service
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --scale radiox=3 -d

# Update services (zero-downtime)
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build --no-deps -d radiox

# View production logs
docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f
```

### **🧪 Testing & Validation**

```bash
# Test container health
docker exec radiox-app python production/radiox_master.py --action system_status

# Generate test show
docker exec radiox-app python production/radiox_master.py --action generate_broadcast --news-count 1

# Check container resources
docker stats radiox-app

# Inspect container
docker inspect radiox-app
```

---

## 📊 Monitoring & Logging

### **📝 Container Logging**

```bash
# View all logs
docker-compose logs

# Follow specific service logs
docker-compose logs -f radiox

# View logs with timestamps
docker-compose logs -t radiox

# Limit log output
docker-compose logs --tail=100 radiox
```

### **🔍 Health Monitoring**

```bash
# Check container health
docker-compose ps

# Health check details
docker inspect --format='{{json .State.Health}}' radiox-app

# Container resource usage
docker stats --no-stream
```

### **📈 Log Aggregation**

Add to `docker-compose.yml` for centralized logging:

```yaml
services:
  radiox:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
        labels: "service=radiox"

  # Optional: Add ELK stack for log aggregation
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.8.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    volumes:
      - elasticsearch-data:/usr/share/elasticsearch/data

  logstash:
    image: docker.elastic.co/logstash/logstash:8.8.0
    volumes:
      - ./docker/logstash.conf:/usr/share/logstash/pipeline/logstash.conf

  kibana:
    image: docker.elastic.co/kibana/kibana:8.8.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
```

---

## 🔒 Security Best Practices

### **🛡️ Container Security**

```dockerfile
# Use non-root user
USER radiox

# Minimize attack surface
RUN rm -rf /var/lib/apt/lists/*

# Set security options
LABEL security.no-new-privileges=true
```

### **🔑 Secrets Management**

```yaml
# Use Docker secrets for production
services:
  radiox:
    secrets:
      - openai_api_key
      - elevenlabs_api_key
    environment:
      - OPENAI_API_KEY_FILE=/run/secrets/openai_api_key
      - ELEVENLABS_API_KEY_FILE=/run/secrets/elevenlabs_api_key

secrets:
  openai_api_key:
    file: ./secrets/openai_api_key.txt
  elevenlabs_api_key:
    file: ./secrets/elevenlabs_api_key.txt
```

### **🌐 Network Security**

```yaml
networks:
  radiox-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

---

## 🚨 Troubleshooting

### **Common Docker Issues**

| 🚨 Issue | 🔍 Diagnosis | ✅ Solution |
|----------|-------------|-------------|
| Container won't start | Check logs: `docker logs radiox-app` | Fix .env or dependencies |
| Out of memory | Check: `docker stats` | Increase memory limits |
| Port conflicts | Check: `netstat -tulpn` | Change port mappings |
| Volume permissions | Check: `ls -la backend/output` | Fix file permissions |

### **🔧 Debug Commands**

```bash
# Enter container shell
docker exec -it radiox-app bash

# Check container processes
docker exec radiox-app ps aux

# Test network connectivity
docker exec radiox-app ping google.com

# Check environment variables
docker exec radiox-app env | grep RADIOX
```

---

## 🔗 Related Guides

- **🏭 [Production Deployment](production.md)** - VPS deployment guide
- **📊 [Monitoring](monitoring.md)** - Advanced monitoring setup
- **🏗️ [Architecture](../developer-guide/architecture.md)** - System design
- **🧪 [Testing](../developer-guide/testing.md)** - Container testing

---

<div align="center">

**🐳 Your containerized RadioX is ready to sail!**

[🏠 Documentation](../) • [🏭 Production](production.md) • [💬 Get Help](../README.md#-support)

</div> 