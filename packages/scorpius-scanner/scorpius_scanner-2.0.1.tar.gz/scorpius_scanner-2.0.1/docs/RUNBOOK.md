# Scorpius SaaS Platform - Runbook

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.9+
- Node.js 18+
- PostgreSQL 15+ (or use Docker)
- Redis 7+ (or use Docker)
- MinIO or S3-compatible storage

### Local Development Setup

1. **Clone the repository**
```bash
git clone https://github.com/scorpius/ultra-smart-contract-scanner-v2.git
cd ultra-smart-contract-scanner-v2
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start services with Docker Compose**
```bash
docker-compose up -d
```

This will start:
- PostgreSQL (port 5432)
- Redis (port 6379)
- MinIO (ports 9000, 9001)
- Backend API (port 8000)
- Celery Worker
- Celery Flower (port 5555)
- Simulation Service (port 8001)
- Web Dashboard (port 3000)

4. **Run database migrations**
```bash
docker-compose exec backend alembic upgrade head
```

5. **Access the application**
- Web Dashboard: http://localhost:3000
- API Documentation: http://localhost:8000/v1/docs
- MinIO Console: http://localhost:9001 (minioadmin/minioadmin)
- Celery Flower: http://localhost:5555

## Manual Setup (Without Docker)

### Backend Setup

1. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

2. **Set up PostgreSQL**
```bash
createdb scorpius
createuser scorpius -P  # Set password
```

3. **Run migrations**
```bash
alembic upgrade head
```

4. **Start the API server**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

5. **Start Celery worker**
```bash
celery -A app.workers.celery_app worker --loglevel=info
```

6. **Start Celery Flower (optional)**
```bash
celery -A app.workers.celery_app flower
```

### Frontend Setup

1. **Install Node dependencies**
```bash
cd web
npm install
```

2. **Start development server**
```bash
npm run dev
```

3. **Build for production**
```bash
npm run build
npm start
```

## API Usage

### Authentication

1. **Register a new user**
```bash
curl -X POST http://localhost:8000/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "SecurePass123!"}'
```

2. **Login**
```bash
curl -X POST http://localhost:8000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "SecurePass123!"}'
```

### Create and Run a Scan

1. **Create a project**
```bash
curl -X POST http://localhost:8000/v1/projects?org_id=YOUR_ORG_ID \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "My DeFi Protocol", "default_chain": "ethereum"}'
```

2. **Upload and scan**
```bash
curl -X POST http://localhost:8000/v1/scans \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "project_id=YOUR_PROJECT_ID" \
  -F "fast=true" \
  -F "with_sim=true" \
  -F "file=@contracts.zip"
```

3. **Check scan status**
```bash
curl http://localhost:8000/v1/scans/SCAN_ID \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## CLI Usage

### Install CLI
```bash
pip install -e .
```

### Run a scan
```bash
scorpius scan ./contracts --fast --json results.json
```

### Generate report
```bash
scorpius report results.json --summary
```

## Production Deployment

### Using Docker

1. **Build images**
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build
```

2. **Deploy with environment variables**
```bash
export JWT_SECRET_KEY=$(openssl rand -hex 32)
export DATABASE_URL=postgresql://user:pass@db:5432/scorpius
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Kubernetes Deployment

See `/k8s` directory for Kubernetes manifests (if available).

### Environment Variables

Critical environment variables for production:

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `JWT_SECRET_KEY`: Secret key for JWT tokens (generate with `openssl rand -hex 32`)
- `S3_ENDPOINT_URL`: S3/MinIO endpoint
- `S3_ACCESS_KEY_ID`: S3 access key
- `S3_SECRET_ACCESS_KEY`: S3 secret key
- `STRIPE_SECRET_KEY`: Stripe API key (if billing enabled)
- `ENABLE_BILLING`: Enable billing features (true/false)
- `ENABLE_SIMULATION`: Enable simulation features (true/false)

## Monitoring

### Health Checks

- API Health: `GET /v1/health`
- API Readiness: `GET /v1/health/ready`
- Metrics: `GET /metrics` (Prometheus format)

### Logs

- API logs: `docker-compose logs backend`
- Worker logs: `docker-compose logs worker`
- All logs: `docker-compose logs -f`

### Performance Metrics

Monitor these KPIs:
- Time-to-First-High (TTF-High): Target < 60s
- API response time: p95 < 200ms
- Scan success rate: > 95%
- Simulation budget usage: < 180s per scan

## Troubleshooting

### Common Issues

1. **Database connection errors**
   - Check PostgreSQL is running: `docker-compose ps postgres`
   - Verify DATABASE_URL is correct
   - Check network connectivity

2. **Scan failures**
   - Check worker logs: `docker-compose logs worker`
   - Verify scanner dependencies are installed
   - Check disk space for temp files

3. **S3/MinIO issues**
   - Verify MinIO is running: `docker-compose ps minio`
   - Check bucket exists: Access MinIO console
   - Verify credentials are correct

4. **Authentication errors**
   - Verify JWT_SECRET_KEY is set
   - Check token expiration
   - Ensure CORS origins are configured

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
export DEBUG=true
```

### Database Migrations

Roll back migration:
```bash
alembic downgrade -1
```

Create new migration:
```bash
alembic revision --autogenerate -m "Description"
```

## Backup and Recovery

### Database Backup

```bash
docker-compose exec postgres pg_dump -U scorpius scorpius > backup.sql
```

### Database Restore

```bash
docker-compose exec -T postgres psql -U scorpius scorpius < backup.sql
```

### S3 Backup

```bash
# Using MinIO client
mc mirror minio/scorpius /backup/scorpius
```

## Security

### Best Practices

1. **Secrets Management**
   - Use environment variables or secret management service
   - Never commit secrets to version control
   - Rotate JWT secret keys regularly

2. **Network Security**
   - Use HTTPS in production
   - Configure firewall rules
   - Limit database access to application servers

3. **API Security**
   - Implement rate limiting
   - Use API tokens for automation
   - Enable CORS only for trusted origins

### Security Headers

Nginx configuration for production:
```nginx
add_header X-Frame-Options "DENY";
add_header X-Content-Type-Options "nosniff";
add_header X-XSS-Protection "1; mode=block";
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
```

## Support

- Documentation: https://docs.scorpius.io
- Issues: https://github.com/scorpius/scanner-v2/issues
- Email: support@scorpius.io