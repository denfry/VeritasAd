# Railway Deployment Guide — VeritasAd

## Architecture

```
Railway Project: veritasad
├── Frontend (Next.js)      → your-project.up.railway.app
├── Backend (FastAPI)       → separate Railway URL
├── Bot (aiogram)           → no public URL (polling mode)
├── PostgreSQL              → Railway managed
└── Redis                   → Railway managed
```

## Quick Deploy

### 1. Push to GitHub

```bash
git add .
git commit -m "deploy to railway"
git push origin main
```

### 2. Create Railway Project

1. Go to https://railway.app
2. **New Project** → **Deploy from GitHub repo** → select VeritasAd
3. Railway auto-detects the monorepo

### 3. Add Services

Click **+ New** for each:

| Service | Root Directory | Dockerfile |
|---------|---------------|------------|
| Backend | `backend` | `Dockerfile` |
| Frontend | `frontend` | `Dockerfile` |
| Bot | `bot` | `Dockerfile` |
| PostgreSQL | — | Railway managed |
| Redis | — | Railway managed |

### 4. Set Environment Variables

#### Backend (copy-paste ready)

```
ENVIRONMENT=production
DEBUG=false
DISABLE_AUTH=false

SUPABASE_URL=https://zpfktkvgurpsyyecdibf.supabase.co
SUPABASE_ANON_KEY=<from Supabase Dashboard → Settings → API → anon public>
SUPABASE_JWT_SECRET=daOhiWLroRIoeIdqP9NzgA_JsScG9A5

TELEGRAM_BOT_TOKEN=8314731852:AAEq0UIE1kwMrNFPsjt6CZ12Cb7cIXcMiE4
BOT_SECRET_KEY=veritasad_prod_bot_secret_key_2026_secure

CORS_ORIGINS=["https://your-frontend-url.up.railway.app"]
TRUSTED_HOSTS=["*.up.railway.app","localhost"]

DOWNLOAD_CONCURRENT_FRAGMENTS=8
USE_ARIA2C=true
LOG_LEVEL=INFO
LOG_FORMAT=json
```

> **Note:** Railway auto-injects `DATABASE_URL` and `REDIS_URL` from the PostgreSQL/Redis services. No need to set them manually.

#### Frontend (copy-paste ready)

```
NODE_ENV=production
NEXT_PUBLIC_API_URL=<Railway backend URL, e.g. https://backend-production-xxx.up.railway.app>
NEXT_PUBLIC_SUPABASE_URL=https://zpfktkvgurpsyyecdibf.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<from Supabase Dashboard → Settings → API → anon public>
NEXT_PUBLIC_TELEGRAM_BOT_USERNAME=veritasadbot
NEXT_PUBLIC_DISABLE_AUTH=false
```

#### Bot (copy-paste ready)

```
TELEGRAM_BOT_TOKEN=8314731852:AAEq0UIE1kwMrNFPsjt6CZ12Cb7cIXcMiE4
API_URL=<Railway backend internal URL, e.g. http://backend.railway.internal:8000>
REDIS_URL=<from Railway Redis reference>/2
ENVIRONMENT=production
BOT_SECRET_KEY=veritasad_prod_bot_secret_key_2026_secure
BOT_USERNAME=veritasadbot
```

### 5. Link Services

In Railway dashboard:
1. Click each service → **Variables** → **Reference**
2. Reference `DATABASE_URL` from PostgreSQL
3. Reference `REDIS_URL` from Redis
4. For Bot `API_URL`: use the backend's **internal Railway URL** (found in backend service → Settings → Networking)

### 6. Supabase Configuration

In Supabase Dashboard → Authentication → URL Configuration:
- **Site URL**: your Railway frontend URL
- **Redirect URLs**:
  - `https://your-frontend.up.railway.app/auth/callback`
  - `https://your-frontend.up.railway.app/auth/login`

### 7. Telegram Bot Configuration

In @BotFather:
- Run `/setdomain` and set your frontend Railway URL (for Login Widget)

### 8. Deploy

Railway auto-deploys on push to `main`. Monitor logs in dashboard.

## Troubleshooting

### Frontend build fails
- Ensure all `NEXT_PUBLIC_*` vars are set in Railway
- Check `NEXT_PUBLIC_API_URL` points to backend Railway URL

### CORS errors
- Update `CORS_ORIGINS` in backend vars with your frontend Railway URL
- Format: `["https://frontend-url.up.railway.app"]`

### Bot not responding
- Check `TELEGRAM_BOT_TOKEN` is correct
- Verify `API_URL` uses backend's **internal** Railway URL (not public URL)
- Bot uses polling — no webhook needed

### Auth not working
- Verify `SUPABASE_JWT_SECRET` matches Supabase Dashboard → Settings → API → JWT Secret
- Check `DISABLE_AUTH=false` on backend
- Verify Supabase redirect URLs include your Railway frontend URL
