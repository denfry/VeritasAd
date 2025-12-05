from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db
from .routers import jobs

# **Initialize FastAPI app with descriptive title**
app = FastAPI(title="VeritasAD API")


@app.on_event("startup")
def on_startup():
    # Stage 1: create tables if missing (replace with Alembic later)
    init_db()


# **Configure CORS to allow frontend access from any origin**
# ! In production: Replace ["*"] with specific domains (e.g., ["https://veritasad.app"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # Allows all origins (dev only)
    allow_credentials=True,       # Supports cookies & auth headers
    allow_methods=["*"],          # Allows all HTTP methods
    allow_headers=["*"],          # Allows all headers
)

# **Mount routers under their prefixes**
# Legacy routers (upload, train, analyze) are kept for backward compatibility but not mounted
# Main API is through /jobs endpoint
app.include_router(jobs.router)


# **Root endpoint — health check & docs redirect**
@app.get("/")
def home():
    """
    Welcome endpoint.
    Returns a friendly message and points to interactive Swagger UI.
    """
    return {"message": "VeritasAD API запущен. Перейдите на /docs"}


@app.get("/health")
def health():
    return {"status": "ok"}
