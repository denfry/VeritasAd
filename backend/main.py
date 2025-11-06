from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import upload, train

app = FastAPI(title="VeritasAD API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)

@app.get("/")
def home():
    return {"message": "VeritasAD API запущен. Перейдите на /docs"}
