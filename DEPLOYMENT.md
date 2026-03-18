# Deployment Guide

Production deployment guide for the Metadata Service.

## Pre-Deployment Checklist

- [ ] All tests passing (`pytest tests/ -v`)
- [ ] Code quality checks pass (`make quality`)
- [ ] Dependencies updated (`poetry lock`)
- [ ] Environment variables configured
- [ ] Database backups created
- [ ] Rollback plan documented
- [ ] Monitoring setup completed
- [ ] Documentation updated

## Docker Deployment

### Production docker-compose.yml

```yaml
version: "3.9"

services:
  mysql:
    image: mysql:8.0
    container_name: metadata_mysql_prod
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_USER: ${DB_USER}
      MYSQL_PASSWORD: ${DB_PASSWORD}
      MYSQL_DATABASE: ${DB_NAME}
    volumes:
      - mysql_data_prod:/var/lib/mysql
      - ./backups:/backups
    ports:
      - "3306:3306"
    networks:
      - metadata_network
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    build:
      context: .
      dockerfile: Dockerfile.prod
    container_name: metadata_api_prod
    restart: always
    depends_on:
      mysql:
        condition: service_healthy
    ports:
      - "8000:8000"
    environment:
      ENVIRONMENT: production
      DB_HOST: mysql
      DB_PORT: 3306
      DB_USER: ${DB_USER}
      DB_PASSWORD: ${DB_PASSWORD}
      DB_NAME: ${DB_NAME}
      LOG_LEVEL: INFO
    volumes:
      - ./logs:/app/logs
    networks:
      - metadata_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    container_name: metadata_nginx
    restart: always
    depends_on:
      - api
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
      - ./logs/nginx:/var/log/nginx
    networks:
      - metadata_network

volumes:
  mysql_data_prod:

networks:
  metadata_network:
    driver: bridge
```

### Production Dockerfile

```dockerfile
FROM python:3.10-slim as builder

WORKDIR /app
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*
RUN pip install poetry

COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && poetry install --no-dev

FROM python:3.10-slim

WORKDIR /app
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

EXPOSE 8000

CMD ["gunicorn", "app.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

Add to pyproject.toml:
```toml
gunicorn = "^21.0.0"
```

## Cloud Deployment

### AWS ECS

1. **Create ECR Repository**
```bash
aws ecr create-repository --repository-name metadata-service
```

2. **Build and Push Image**
```bash
docker tag metadata-service:latest <aws-account>.dkr.ecr.<region>.amazonaws.com/metadata-service:latest
docker push <aws-account>.dkr.ecr.<region>.amazonaws.com/metadata-service:latest
```

3. **ECS Task Definition**
```json
{
  "family": "metadata-service",
  "containerDefinitions": [
    {
      "name": "metadata-api",
      "image": "<aws-account>.dkr.ecr.<region>.amazonaws.com/metadata-service:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "hostPort": 8000
        }
      ],
      "environment": [
        {"name": "ENVIRONMENT", "value": "production"},
        {"name": "DB_HOST", "value": "metadata-db.c123456.rds.amazonaws.com"}
      ],
      "secrets": [
        {"name": "DB_USER", "valueFrom": "arn:aws:secretsmanager:..."}
      ]
    }
  ]
}
```

### GCP Cloud Run

```bash
gcloud run deploy metadata-service \
  --image gcr.io/PROJECT_ID/metadata-service \
  --platform managed \
  --region us-central1 \
  --set-env-vars DB_HOST=cloudsql-proxy,ENVIRONMENT=production \
  --memory 1Gi \
  --cpu 1 \
  --timeout 3600
```

### Kubernetes

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: metadata-config
data:
  ENVIRONMENT: production
  LOG_LEVEL: INFO

---
apiVersion: v1
kind: Secret
metadata:
  name: metadata-secret
type: Opaque
stringData:
  DB_USER: metadata_user
  DB_PASSWORD: <secure-password>

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: metadata-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: metadata-service
  template:
    metadata:
      labels:
        app: metadata-service
    spec:
      containers:
      - name: api
        image: gcr.io/project/metadata-service:v1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          valueFrom:
            configMapKeyRef:
              name: metadata-config
              key: ENVIRONMENT
        - name: DB_USER
          valueFrom:
            secretKeyRef:
              name: metadata-secret
              key: DB_USER
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            cpu: 250m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi

---
apiVersion: v1
kind: Service
metadata:
  name: metadata-service
spec:
  selector:
    app: metadata-service
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

## Database Migration

### Pre-deployment

```bash
# Create backup
docker-compose exec mysql mysqldump -u root -p metadata_db > backup_$(date +%Y%m%d).sql

# Test migration locally
docker-compose exec api alembic upgrade head
```

### Production Migration

```bash
# Connect to production
ssh prodserver

# Run migrations
docker-compose exec api alembic upgrade head

# Verify migration
docker-compose exec api alembic current
```

### Rollback

```bash
# Identify previous version
docker-compose exec api alembic history

# Rollback one version
docker-compose exec api alembic downgrade -1

# Specific version
docker-compose exec api alembic downgrade 001_initial_tables
```

## Monitoring & Logging

### Application Metrics

```python
# In app/main.py
from prometheus_client import Counter, Histogram

request_count = Counter('requests_total', 'Total requests')
request_duration = Histogram('request_duration_seconds', 'Request duration')

@app.middleware("http")
async def add_metrics(request: Request, call_next):
    request_count.inc()
    with request_duration.time():
        response = await call_next(request)
    return response
```

### Logging Configuration

```yaml
# logging.yml
version: 1
disable_existing_loggers: false

formatters:
  standard:
    format: "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
  json:
    class: pythonjsonlogger.jsonlogger.JsonFormatter

handlers:
  console:
    class: logging.StreamHandler
    formatter: standard
    level: INFO
  file:
    class: logging.handlers.RotatingFileHandler
    filename: logs/app.log
    maxBytes: 10485760  # 10MB
    backupCount: 5
    formatter: json

root:
  level: INFO
  handlers: [console, file]
```

### Health Checks

Regular monitoring with:
```bash
# Database connection
SELECT 1

# API response time
curl -w "%{time_total}s" http://localhost:8000/health

# Lineage graph integrity
SELECT COUNT(*) FROM lineage
WHERE upstream_dataset_id = downstream_dataset_id

# Search performance
SELECT COUNT(*) FROM datasets WHERE table_name LIKE '%test%'
```

## Performance Tuning

### Database Optimization

```sql
-- Analyze tables
ANALYZE TABLE datasets;
ANALYZE TABLE columns;
ANALYZE TABLE lineage;

-- Check index usage
SELECT object_name, count_read, count_write 
FROM performance_schema.table_io_waits_summary 
WHERE object_schema = 'metadata_db';
```

### API Optimization

```python
# Connection pooling
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40
)

# Caching
from functools import lru_cache

@lru_cache(maxsize=100)
def get_dataset_lineage(dataset_id: int):
    # Cached results
    pass
```

### Load Testing

```bash
# Using Apache Bench
ab -n 10000 -c 100 http://localhost:8000/api/v1/datasets/

# Using Locust
locust -f locustfile.py --host=http://localhost:8000
```

## Security Hardening

### SSL/TLS Setup

```bash
# Generate self-signed certificate for testing
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# Use Let's Encrypt for production
certbot certonly --standalone -d metadata.example.com
```

### Nginx Configuration

```nginx
upstream api {
    server api:8000;
}

server {
    listen 80;
    server_name _;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name metadata.example.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    location / {
        proxy_pass http://api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Database Security

```sql
-- Limit user permissions
CREATE USER 'metadata_app'@'%' IDENTIFIED BY 'strong_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON metadata_db.* TO 'metadata_app'@'%';
FLUSH PRIVILEGES;
```

## Disaster Recovery

### Backup Strategy

```bash
#!/bin/bash
# Daily backup
docker-compose exec mysql mysqldump -u root -p metadata_db | gzip > /backups/metadata_$(date +%Y%m%d).sql.gz

# Upload to S3
aws s3 cp /backups/metadata_*.sql.gz s3://backup-bucket/
```

### Restore Procedure

```bash
# Download backup from S3
aws s3 cp s3://backup-bucket/metadata_20240101.sql.gz .

# Restore
gunzip -c metadata_20240101.sql.gz | docker-compose exec -T mysql mysql -u root -p metadata_db
```

## Deployment Checklist

Before going live:

- [ ] SSL certificates installed
- [ ] Database backups configured
- [ ] Monitoring alerts set up
- [ ] Logging configured
- [ ] Rate limiting enabled
- [ ] API documentation updated
- [ ] Team trained on operations
- [ ] Rollback plan documented
- [ ] DNS configured
- [ ] Load balancer tested
- [ ] Failover tested
- [ ] Performance baseline established

## Post-Deployment

1. **Monitor closely for 24 hours**
   - Check error rates
   - Monitor database performance
   - Watch memory/CPU usage

2. **Notify stakeholders**
   - Send deployment notification
   - Provide status page link
   - Document any changes

3. **Document lessons learned**
   - What went well
   - What could improve
   - Update runbooks

---

For questions or issues, contact the DevOps team.
