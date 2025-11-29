# VeritasAd - Production Deployment Guide

## Quick Start (Local Development)

```bash
# 1. Clone repository
cd VeritasAd/

# 2. Start all services with Docker Compose
cd infra
docker-compose up -d

# 3. Check services
docker-compose ps

# 4. Access services
# API: http://localhost:8000/docs
# Frontend: http://localhost:3000
# Flower: http://localhost:5555
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| backend | 8000 | FastAPI backend |
| frontend | 3000 | Next.js frontend |
| postgres | 5432 | PostgreSQL database |
| redis | 6379 | Redis cache |
| celery-worker | - | Background tasks |
| flower | 5555 | Celery monitoring |
| bot | - | Telegram bot |
| caddy | 80/443 | Reverse proxy |

## Environment Configuration

### Backend (.env)
```env
DATABASE_URL=postgresql+asyncpg://veritasad:veritasad123@postgres:5432/veritasad
REDIS_URL=redis://redis:6379/0
SECRET_KEY=your-secret-key-here
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### Bot (.env)
```env
TELEGRAM_BOT_TOKEN=your-bot-token
API_URL=http://backend:8000
REDIS_URL=redis://redis:6379/2
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Database Migrations

```bash
# Run migrations
cd backend
docker-compose exec backend alembic upgrade head

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "description"
```

## Monitoring

### Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f celery-worker
```

### Celery Monitoring
Access Flower at http://localhost:5555

### Health Checks
- Backend: http://localhost:8000/health
- Backend Ready: http://localhost:8000/ready

## Production Deployment

### Prerequisites
- Ubuntu 20.04+ server
- Docker & Docker Compose
- Domain name with DNS configured

### Steps

1. **Clone repository**
```bash
git clone https://github.com/youruser/VeritasAd.git
cd VeritasAd/
```

2. **Configure environment**
```bash
cp infra/.env.example .env
# Edit .env with production values
nano .env
```

3. **Configure Caddy**
Edit `infra/Caddyfile` with your domain:
```
your-domain.com {
  # ... (configuration already present)
}
```

4. **Start services**
```bash
cd infra
docker-compose up -d
```

5. **Run migrations**
```bash
docker-compose exec backend alembic upgrade head
```

6. **Check services**
```bash
docker-compose ps
docker-compose logs
```

### SSL/HTTPS

Caddy automatically handles SSL certificates via Let's Encrypt.
Just configure your domain in Caddyfile.

## Scaling

### Horizontal Scaling

Add more Celery workers:
```yaml
# docker-compose.yml
celery-worker-2:
  <<: *celery-worker
  container_name: veritasad-celery-worker-2
```

### Vertical Scaling

Adjust resources in docker-compose.yml:
```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 4G
```

## Backup

### Database
```bash
docker-compose exec postgres pg_dump -U veritasad veritasad > backup.sql
```

### Restore
```bash
cat backup.sql | docker-compose exec -T postgres psql -U veritasad veritasad
```

## Troubleshooting

### Backend not starting
```bash
docker-compose logs backend
# Check database connection
docker-compose exec backend alembic current
```

### Celery tasks not processing
```bash
docker-compose logs celery-worker
# Check Redis connection
docker-compose exec redis redis-cli ping
```

### Frontend build errors
```bash
cd frontend
npm install
npm run build
```

## Security Checklist

- [ ] Change SECRET_KEY in production
- [ ] Use strong database password
- [ ] Configure CORS_ORIGINS whitelist
- [ ] Enable HTTPS (Caddy handles this)
- [ ] Set up firewall (UFW)
- [ ] Regular security updates
- [ ] Monitor logs for suspicious activity

## Performance Tuning

### PostgreSQL
```sql
-- Adjust max connections
ALTER SYSTEM SET max_connections = 200;

-- Tune memory
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
```

### Redis
```bash
# Increase max memory
docker-compose exec redis redis-cli CONFIG SET maxmemory 1gb
```

### Celery
Adjust concurrency in docker-compose.yml:
```yaml
command: celery -A app.core.celery:celery_app worker --concurrency=4
```

## Support

For issues, check:
- Logs: `docker-compose logs`
- Health: http://your-domain/health
- Flower: http://your-domain/flower
