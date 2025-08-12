# Deployment Guide

## Overview

VoltForge can be deployed in multiple ways depending on your requirements:
- Local development setup
- Docker containerized deployment
- Cloud deployment (AWS, GCP, Azure)
- Kubernetes deployment

## Docker Deployment

### Prerequisites
- Docker
- Docker Compose

### Quick Start
```bash
# Clone the repository
git clone https://github.com/your-org/voltforge.git
cd voltforge

# Copy environment configuration
cp .env.example .env

# Edit .env with your production settings
nano .env

# Start services
docker-compose up -d
```

### Docker Compose Configuration
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - API_HOST=0.0.0.0
      - API_PORT=8000
      - CHROMA_PERSIST_DIRECTORY=/app/data
    volumes:
      - ./data:/app/data
      - ./backend/src:/app/src
    depends_on:
      - nginx

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./infra/nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
```

## Production Environment Setup

### Environment Variables
```env
# Production API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_KEY=your-secure-production-api-key

# Database Configuration
CHROMA_PERSIST_DIRECTORY=/app/data/chroma_db

# AI Services
OPENAI_API_KEY=your-openai-api-key
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Production Settings
DEBUG=false
LOG_LEVEL=INFO
CORS_ORIGINS=https://your-frontend-domain.com

# Security
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Performance
WORKERS=4
MAX_CONNECTIONS=1000
TIMEOUT=30
```

### SSL Configuration
```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    location / {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Cloud Deployment

### AWS Deployment

#### Using AWS ECS
```bash
# Build and push Docker image
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin your-account.dkr.ecr.us-west-2.amazonaws.com

docker build -t voltforge-backend ./backend
docker tag voltforge-backend:latest your-account.dkr.ecr.us-west-2.amazonaws.com/voltforge-backend:latest
docker push your-account.dkr.ecr.us-west-2.amazonaws.com/voltforge-backend:latest

# Deploy using ECS task definition
aws ecs update-service --cluster voltforge-cluster --service voltforge-backend --task-definition voltforge-backend:latest
```

#### ECS Task Definition
```json
{
  "family": "voltforge-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "voltforge-backend",
      "image": "your-account.dkr.ecr.us-west-2.amazonaws.com/voltforge-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "API_HOST",
          "value": "0.0.0.0"
        },
        {
          "name": "API_PORT",
          "value": "8000"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/voltforge-backend",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### Google Cloud Platform

#### Using Cloud Run
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/your-project/voltforge-backend ./backend
gcloud run deploy voltforge-backend --image gcr.io/your-project/voltforge-backend --platform managed --region us-central1
```

### Azure Container Instances
```bash
# Create resource group
az group create --name voltforge-rg --location eastus

# Deploy container
az container create \
  --resource-group voltforge-rg \
  --name voltforge-backend \
  --image your-registry.azurecr.io/voltforge-backend:latest \
  --cpu 1 \
  --memory 2 \
  --ports 8000 \
  --environment-variables API_HOST=0.0.0.0 API_PORT=8000
```

## Kubernetes Deployment

### Deployment Manifest
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: voltforge-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: voltforge-backend
  template:
    metadata:
      labels:
        app: voltforge-backend
    spec:
      containers:
      - name: backend
        image: voltforge-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: API_HOST
          value: "0.0.0.0"
        - name: API_PORT
          value: "8000"
        - name: CHROMA_PERSIST_DIRECTORY
          value: "/app/data"
        volumeMounts:
        - name: data-volume
          mountPath: /app/data
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
      volumes:
      - name: data-volume
        persistentVolumeClaim:
          claimName: voltforge-data-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: voltforge-backend-service
spec:
  selector:
    app: voltforge-backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

### Persistent Volume Claim
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: voltforge-data-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

## Monitoring and Logging

### Health Checks
```bash
# Check application health
curl http://your-domain.com/health

# Expected response
{
  "status": "healthy",
  "timestamp": "2025-01-08T12:00:00Z",
  "version": "1.0.0"
}
```

### Logging Configuration
```python
# In production settings
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/app/logs/voltforge.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}
```

### Monitoring with Prometheus
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'voltforge-backend'
    static_configs:
      - targets: ['voltforge-backend:8000']
    metrics_path: '/metrics'
```

## Backup and Recovery

### Database Backup
```bash
# Backup ChromaDB data
tar -czf voltforge-backup-$(date +%Y%m%d).tar.gz ./data/chroma_db

# Upload to cloud storage
aws s3 cp voltforge-backup-$(date +%Y%m%d).tar.gz s3://your-backup-bucket/
```

### Automated Backup Script
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="voltforge_backup_$DATE.tar.gz"

# Create backup
tar -czf "$BACKUP_DIR/$BACKUP_FILE" ./data

# Upload to cloud (example: AWS S3)
aws s3 cp "$BACKUP_DIR/$BACKUP_FILE" s3://your-backup-bucket/

# Clean up old backups (keep last 7 days)
find $BACKUP_DIR -name "voltforge_backup_*.tar.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE"
```

## Performance Optimization

### Production Optimizations
1. **Use multiple workers**: Set `WORKERS=4` or more
2. **Enable caching**: Configure Redis for caching
3. **Database optimization**: Regular maintenance and indexing
4. **CDN**: Use CDN for static assets
5. **Load balancing**: Distribute traffic across multiple instances

### Scaling Considerations
- **Horizontal scaling**: Add more application instances
- **Database scaling**: Consider database clustering
- **Caching layer**: Implement Redis/Memcached
- **Queue system**: Use Celery for background tasks

## Security Checklist

- [ ] Use HTTPS in production
- [ ] Set strong API keys and secrets
- [ ] Configure CORS properly
- [ ] Enable rate limiting
- [ ] Regular security updates
- [ ] Monitor for vulnerabilities
- [ ] Backup encryption
- [ ] Access logging
- [ ] Network security groups
- [ ] Regular penetration testing

## Troubleshooting

### Common Issues

#### High Memory Usage
```bash
# Monitor memory usage
docker stats voltforge-backend

# Optimize memory settings
export PYTHONMALLOC=malloc
export MALLOC_ARENA_MAX=2
```

#### Slow Response Times
```bash
# Check database performance
# Monitor query execution times
# Consider adding indexes
# Implement caching
```

#### Connection Issues
```bash
# Check network connectivity
curl -I http://your-domain.com/health

# Check logs
docker logs voltforge-backend
```

## Rollback Procedures

### Quick Rollback
```bash
# Rollback to previous version
docker-compose down
docker-compose up -d --scale backend=0
docker tag voltforge-backend:previous voltforge-backend:latest
docker-compose up -d
```

### Database Rollback
```bash
# Restore from backup
tar -xzf voltforge-backup-20250108.tar.gz
cp -r data/chroma_db ./data/
docker-compose restart backend
```