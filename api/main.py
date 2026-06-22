from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from api.routers import me, raffles
from core.config import settings

app = FastAPI(
    title="Rafflix API",
    description="Backend API for Rafflix Telegram Web App",
    version="1.0.0"
)

# CORS Configuration
# In production, specify the exact WEBAPP_URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(me.router, prefix="/api")
app.include_router(raffles.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Rafflix API is running"}
