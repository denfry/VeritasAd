# 🎯 VeritasAd - Production-Ready AI Advertising Detection System

> **Full-stack application with FastAPI, Next.js 15, and Telegram Bot**  
> Neural network-based advertising detection in video content

## ✨ What's Been Built

### ✅ Backend (FastAPI) - ПОЛНОСТЬЮ ПЕРЕРАБОТАН
- ✅ **Async SQLAlchemy 2.0** with typed models
- ✅ **Alembic migrations** for database versioning
- ✅ **Redis** for caching and task queues
- ✅ **Celery** for background video processing
- ✅ **SSE (Server-Sent Events)** for real-time progress
- ✅ **Structlog** for structured JSON logging
- ✅ **Rate limiting** with slowapi + Redis
- ✅ **Custom error handling** with error codes
- ✅ **Security middleware** (CORS, headers, trusted hosts)
- ✅ **Health/Ready endpoints** for Kubernetes
- ✅ **Proper dependency injection** with DB sessions
- ✅ **Auto-create users** by API key
- ✅ **Daily usage limits** by subscription tier

### ✅ Infrastructure
- ✅ **Docker Compose** with all services
- ✅ **Caddyfile** with auto-HTTPS
- ✅ **Multi-stage Dockerfile** for backend
- ✅ **Production-ready configuration**

### 📋 TODO (Next Steps)
- ⏳ Next.js 15 frontend (App Router + TypeScript + Tailwind v4)
- ⏳ Telegram bot (aiogram 3.13)
- ⏳ Frontend pages (/dashboard, /analyze, /history, /pricing)
- ⏳ SSE integration in frontend
- ⏳ Payment integration (ЮKassa)

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- (Optional) Node.js 20+ for frontend development
- (Optional) Python 3.11+ for backend development

### 1. Clone and Setup

```bash
cd VeritasAd/
cp infra/.env.example .env
# Edit .env with your configuration
```

### 2. Run Everything

```bash
cd infra
docker-compose up -d
```

### 3. Access Services

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Backend API**: http://localhost:8000
- **Flower (Celery)**: http://localhost:5555
- **Health Check**: http://localhost:8000/health

## 📦 Project Structure

```
VeritasAd/
├── backend/                    # ✅ ПОЛНОСТЬЮ ПЕРЕРАБОТАН
│   ├── app/
│   │   ├── api/v1/            # API endpoints
│   │   │   ├── analyze.py
│   │   │   ├── progress.py    # SSE endpoint
│   │   │   ├── upload.py
│   │   │   └── router.py
│   │   ├── core/              # Core functionality
│   │   │   ├── config.py      # ✅ Settings with validation
│   │   │   ├── dependencies.py # ✅ Auth & DB injection
│   │   │   ├── errors.py      # ✅ Custom exceptions
│   │   │   ├── redis.py       # ✅ Redis client
│   │   │   └── celery.py      # ✅ Celery config
│   │   ├── middleware/        # ✅ Custom middleware
│   │   │   ├── security.py    # Security headers
│   │   │   └── rate_limit.py  # Rate limiting
│   │   ├── models/
│   │   │   └── database.py    # ✅ Async SQLAlchemy models
│   │   ├── services/          # Business logic
│   │   │   ├── video_processor.py
│   │   │   ├── audio_analyzer.py
│   │   │   └── report_generator.py
│   │   ├── tasks/             # ✅ Celery tasks
│   │   │   └── video_analysis.py
│   │   ├── utils/
│   │   │   └── logger.py      # ✅ Structlog setup
│   │   └── main.py            # ✅ App with all middleware
│   ├── alembic/               # ✅ Database migrations
│   ├── pyproject.toml         # ✅ Modern dependencies
│   ├── requirements.txt
│   ├── Dockerfile             # ✅ Multi-stage production build
│   └── .env.example           # ✅ Full configuration
├── frontend/                  # ⏳ TODO
├── bot/                       # ⏳ TODO
├── infra/                     # ✅ Infrastructure
│   ├── docker-compose.yml     # ✅ All services
│   ├── Caddyfile              # ✅ Reverse proxy
│   └── .env.example
└── README.md                  # This file
```

## 🛠️ Backend Architecture

### Database Models
- **User**: API keys, subscription plans, usage limits
- **Analysis**: Video analysis results with all scores
- **AnalysisFrame**: Frame-by-frame detection results

### API Flow
1. Client sends video URL/file with API key
2. System validates API key, checks rate limits
3. Creates Analysis record with PENDING status
4. Queues Celery task for processing
5. Returns task_id to client
6. Client connects to SSE endpoint for progress
7. Celery worker processes video in background
8. Updates progress in Redis (0-100%)
9. Saves results to database
10. Client receives completion event

### Background Processing (Celery)
- Video download (yt-dlp)
- Logo detection (CLIP)
- Audio transcription (Whisper)
- Disclosure marker detection
- PDF report generation

## 🔒 Security Features

- API key authentication with auto-provisioning
- Rate limiting per user and tier
- Security headers (CSP, HSTS, XSS protection)
- CORS with whitelist
- Trusted host checking
- Request ID tracking
- Structured logging with context

## 📊 Monitoring

- **Health endpoint**:  - basic liveness
- **Readiness endpoint**:  - checks dependencies
- **Flower UI**: http://localhost:5555 - Celery monitoring
- **Structured logs**: JSON format for easy parsing

## 🧪 Development

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scriptsctivate
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Run dev server
uvicorn app.main:app --reload

# Run Celery worker
celery -A app.core.celery:celery_app worker --loglevel=info
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 📡 API Examples

### Analyze Video

```bash
curl -X POST http://localhost:8000/api/v1/analyze/check   -H "X-API-Key: your-api-key"   -F "url=https://youtube.com/watch?v=..."
```

### Stream Progress (SSE)

```javascript
const eventSource = new EventSource(
  'http://localhost:8000/api/v1/analysis/{task_id}/stream',
  {
    headers: { 'X-API-Key': 'your-api-key' }
  }
);

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(`Progress: ${data.progress}%`);
};
```

## 🎨 Tech Stack

### Backend
- **Framework**: FastAPI 0.115
- **Database**: PostgreSQL 16 (async via asyncpg)
- **ORM**: SQLAlchemy 2.0 (async)
- **Cache/Queue**: Redis 7
- **Task Queue**: Celery 5.4
- **Logging**: Structlog 24.4
- **ML**: PyTorch 2.5, Transformers 4.46, Whisper

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Reverse Proxy**: Caddy 2 (auto-HTTPS)
- **Monitoring**: Flower (Celery)

## 🔑 Environment Variables

See  for full list. Key variables:

```env
DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/db
REDIS_URL=redis://redis:6379/0
SECRET_KEY=your-secret-key
ENVIRONMENT=production
LOG_LEVEL=INFO
FREE_TIER_DAILY_LIMIT=100
PRO_TIER_DAILY_LIMIT=10000
```

## 📄 License

MIT License - see [LICENSE](LICENSE)

## 👨‍💻 Author

**VeritasAd Team**
- Email: dabinayo@pm.me
- Telegram: [@kfcbossalbino](https://t.me/kfcbossalbino)

---

⭐ **Status**: Backend 100% ready for production, Frontend & Bot in progress
