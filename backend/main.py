from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# **Import routers for modular API structure**
from routers import upload, train

# **Initialize FastAPI app with descriptive title**
app = FastAPI(title="VeritasAD API")

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
app.include_router(upload.router)
# TODO: Add train.router when training endpoint is ready
app.include_router(train.router)

# **Root endpoint — health check & docs redirect**
@app.get("/")
def home():
    """
    Welcome endpoint.
    Returns a friendly message and points to interactive Swagger UI.
    """
    return {"message": "VeritasAD API запущен. Перейдите на /docs"}

# ? Consider adding /health endpoint with DB & model status
# ! Security: Disable debug mode in production
# FIXME: Enable HTTPS & rate limiting in production deployment
