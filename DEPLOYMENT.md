# Docker Deployment & Container Management Guide

This document provides instructions for containerizing, deploying, managing, and scaling the **WorkPulse Job Market Analysis and Recommendation System** using Docker and Docker Compose.

---

## 1. Prerequisites
Ensure you have the following installed on your target host or cloud server:
- **Docker Engine:** `20.10+` or `24.0+`
- **Docker Compose:** `v2.0+`
- **Git** (for repository management)

Verify your installation:
```bash
docker --version
docker compose version
```

---

## 2. Multi-Container Architecture Overview

The multi-container setup configured in `docker-compose.yml` comprises:
1. **`web` Service (Application & Recommendation Server):**
   - High-concurrency production Python 3.12 container.
   - Runs Gunicorn WSGI server with 3 worker processes.
   - Serves the interactive Web UI, REST API endpoints, and real-time TF-IDF recommendation engine.
   - Exposes Port `5000:5000`.
   - Includes container health checks querying `/api/health`.
2. **`analytics_worker` Service (Background Analytics & Ingestion):**
   - Headless worker service sharing the persistent data and model volumes.
   - Executes scheduled model retraining, monthly dynamic pipeline updates, and database index sync.

---

## 3. Step-by-Step Instructions: Build, Run, and Deploy

### Step 3.1: Build Docker Images
Build the optimized multi-stage container image locally:
```bash
# Build using Docker Compose
docker compose build

# Alternatively, build standalone image
docker build -t workpulse-analytics:latest .
```

### Step 3.2: Launch the Multi-Container Cluster
Start the cluster in detached (background) mode:
```bash
docker compose up -d
```

### Step 3.3: Verify Running Services & Health Status
Inspect container status and health probes:
```bash
docker compose ps
```
Expected output:
```
NAME                         IMAGE               COMMAND                  SERVICE             STATUS                    PORTS
workpulse_web                workpulse_web       "gunicorn --bind 0.0…"   web                 Up (healthy)              0.0.0.0:5000->5000/tcp
workpulse_analytics_worker   workpulse_worker    "python3 -u -c '..."     analytics_worker    Up
```

### Step 3.4: Inspect Real-Time Container Logs
```bash
# Stream logs from all services
docker compose logs -f

# Stream logs specifically from the web server
docker compose logs -f web
```

### Step 3.5: Access the Web Application & REST API
Once running, navigate to:
- **Web Dashboard:** `http://localhost:5000/`
- **Job Recommendation Engine:** `http://localhost:5000/recommend`
- **Interactive REST API Docs:** `http://localhost:5000/api/docs`
- **Health Check Endpoint:** `http://localhost:5000/api/health`

---

## 4. Operational Commands & Maintenance

### Run Tests Inside Container
Execute the automated test suite directly inside the running container:
```bash
docker compose exec web python3 -m pytest tests/
```

### Re-Run Analytics & Model Training Inside Container
If you provide an updated dataset, run the end-to-end pipeline inside the container:
```bash
docker compose exec web python3 run_pipeline.py --force
```

### Trigger Monthly Dynamic Update Webhook
```bash
curl -X POST http://localhost:5000/api/monthly/update \
  -H "Content-Type: application/json" \
  -d '{"action": "refresh"}'
```

### Stopping and Teardown
```bash
# Gracefully stop containers
docker compose stop

# Stop and remove containers and networks
docker compose down

# Stop, remove containers, and purge volumes (fresh start)
docker compose down -v
```

---

## 5. Production Cloud Deployment (AWS, GCP, DigitalOcean, Kubernetes)

### Production Reverse Proxy (Nginx) Configuration
In enterprise deployments, place Nginx in front of the Gunicorn container for SSL/TLS termination and static asset caching:
```nginx
server {
    listen 80;
    server_name labor-pulse.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Resource Constraints (Docker Compose)
To configure CPU and memory limits for high-traffic environments, add the following to `docker-compose.yml`:
```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2048M
    reservations:
      cpus: '0.5'
      memory: 512M
```
