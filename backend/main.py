from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from decouple import config
import os

from database import engine, SessionLocal, Base
from routers import auth, properties, investments, alerts, counties, data_import
from models import User

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Tax Lien Search API",
    description="Texas Tax Deed Investment Tracking System",
    version="1.0.0"
)

# CORS middleware
origins = config('CORS_ORIGINS', default='').split(',')
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(properties.router, prefix="/api/properties", tags=["properties"])
app.include_router(investments.router, prefix="/api/investments", tags=["investments"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
app.include_router(counties.router, prefix="/api/counties", tags=["counties"])
app.include_router(data_import.router, prefix="/api", tags=["data-import"])

@app.get("/")
async def root():
    return {
        "message": "Tax Lien Search API",
        "version": "1.0.0",
        "description": "Texas Tax Deed Investment Tracking System"
    }

@app.get("/api/health")
async def health_check(db: Session = Depends(get_db)):
    return {
        "status": "healthy",
        "database": "connected",
        "environment": config('APP_ENV', default='development')
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=config('DEBUG', default=True, cast=bool)
    )