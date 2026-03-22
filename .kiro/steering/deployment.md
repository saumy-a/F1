---
title: Deployment Configuration
inclusion: auto
---

# Deployment Configuration for F1 Dashboard

## Backend Multi-Stage Dockerfile

```dockerfile
# backend/Dockerfile
# Stage 1: Build stage
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY ./app ./app

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health')" || exit 1

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Frontend Multi-Stage Dockerfile

```dockerfile
# frontend/Dockerfile
# Stage 1: Build stage
FROM node:20-alpine as builder

WORKDIR /build

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build application
RUN npm run build

# Stage 2: Runtime stage with nginx
FROM nginx:1.25-alpine

# Copy built assets from builder
COPY --from=builder /build/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/health || exit 1

# Run nginx
CMD ["nginx", "-g", "daemon off;"]
```

## Docker Compose with Named Volumes and Profiles

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: f1-api
    ports:
      - "8000:8000"
    environment:
      - JOLPICA_BASE_URL=${JOLPICA_BASE_URL:-https://api.jolpi.ca/ergast/f1}
      - OPENF1_BASE_URL=${OPENF1_BASE_URL:-https://api.openf1.org/v1}
      - REDIS_URL=redis://redis:6379/0
      - CORS_ORIGINS=${CORS_ORIGINS:-http://localhost:3000}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
    depends_on:
      redis:
        condition: service_healthy
    networks:
      - f1-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import httpx; httpx.get('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    profiles:
      - dev
      - prod
    # Development-only volume mount
    volumes:
      - ./backend:/app:${DEV_MOUNT:-}

  web:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: f1-web
    ports:
      - "3000:80"
    environment:
      - VITE_API_BASE_URL=${VITE_API_BASE_URL:-http://localhost:8000}
      - VITE_WS_BASE_URL=${VITE_WS_BASE_URL:-ws://localhost:8000}
    networks:
      - f1-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    profiles:
      - dev
      - prod

  redis:
    image: redis:7-alpine
    container_name: f1-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - f1-network
    restart: unless-stopped
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    profiles:
      - dev
      - prod

  nginx:
    image: nginx:1.25-alpine
    container_name: f1-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - api
      - web
    networks:
      - f1-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    profiles:
      - prod

networks:
  f1-network:
    driver: bridge

volumes:
  redis-data:
    name: f1-redis-data
```

## Environment Files

```bash
# .env (backend)
JOLPICA_BASE_URL=https://api.jolpi.ca/ergast/f1
OPENF1_BASE_URL=https://api.openf1.org/v1
OPENF1_API_KEY=
REDIS_URL=redis://redis:6379/0
REDIS_TTL_SHORT=30
REDIS_TTL_LONG=3600
CORS_ORIGINS=http://localhost:3000,http://localhost
WS_PING_INTERVAL=20
LOG_LEVEL=INFO

# .env.frontend
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000

# .env.production
JOLPICA_BASE_URL=https://api.jolpi.ca/ergast/f1
OPENF1_BASE_URL=https://api.openf1.org/v1
REDIS_URL=redis://redis:6379/0
CORS_ORIGINS=https://yourdomain.com
LOG_LEVEL=WARNING
```

## Nginx Configuration with Optimizations

```nginx
# nginx/nginx.conf
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging format with request ID
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for" '
                    'request_id=$request_id request_time=$request_time';

    access_log /var/log/nginx/access.log main;

    # Performance optimizations
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 10M;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/rss+xml
        font/truetype
        font/opentype
        application/vnd.ms-fontobject
        image/svg+xml;
    gzip_disable "msie6";

    # Rate limiting zones
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=general_limit:10m rate=100r/s;
    limit_req_status 429;

    # Connection limiting
    limit_conn_zone $binary_remote_addr zone=conn_limit:10m;
    limit_conn conn_limit 10;

    # Upstream servers
    upstream api_backend {
        server api:8000 max_fails=3 fail_timeout=30s;
        keepalive 32;
    }

    upstream web_backend {
        server web:80 max_fails=3 fail_timeout=30s;
        keepalive 32;
    }

    server {
        listen 80;
        server_name _;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "no-referrer-when-downgrade" always;

        # Health check endpoint
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }

        # API routes with rate limiting
        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;
            
            proxy_pass http://api_backend;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header X-Request-ID $request_id;
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
            
            # Buffering
            proxy_buffering on;
            proxy_buffer_size 4k;
            proxy_buffers 8 4k;
            
            # No caching for API responses
            add_header Cache-Control "no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0";
        }

        # WebSocket routes
        location /ws/ {
            limit_req zone=general_limit burst=50 nodelay;
            
            proxy_pass http://api_backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket timeouts
            proxy_connect_timeout 7d;
            proxy_send_timeout 7d;
            proxy_read_timeout 7d;
            
            # Disable buffering for WebSocket
            proxy_buffering off;
        }

        # Static assets with aggressive caching
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            proxy_pass http://web_backend;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            
            # Cache static assets for 1 year
            expires 1y;
            add_header Cache-Control "public, immutable";
            access_log off;
        }

        # Frontend SPA routes
        location / {
            limit_req zone=general_limit burst=50 nodelay;
            
            proxy_pass http://web_backend;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # SPA fallback
            proxy_intercept_errors on;
            error_page 404 = /index.html;
            
            # Cache HTML for 5 minutes
            add_header Cache-Control "public, max-age=300";
        }
    }
}
```

## Running the Application

```bash
# Development mode (with hot reload)
DEV_MOUNT=rw docker-compose --profile dev up

# Production mode
docker-compose --profile prod up -d

# View logs
docker-compose logs -f api
docker-compose logs -f web

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Rebuild containers
docker-compose build --no-cache
docker-compose up -d
```

## Production Deployment Checklist

1. Set production environment variables in `.env.production`
2. Generate SSL certificates and place in `nginx/ssl/`
3. Update `CORS_ORIGINS` to production domain
4. Set `LOG_LEVEL=WARNING` or `ERROR` in production
5. Configure Redis persistence and memory limits
6. Set up monitoring and alerting
7. Configure backup strategy for Redis data
8. Test health checks for all services
9. Verify rate limiting is working
10. Test WebSocket connections under load
