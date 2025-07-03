from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import uvicorn
import os
from dotenv import load_dotenv

from app.database import engine, get_db
from app.models import Base
from app.routers import invoice, menu, auth, carbon
from app.core.config import settings

load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Fork+ API",
    description="AI-Powered Sustainability Assistant for Restaurants",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directory
os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)

# Mount static files
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_FOLDER), name="uploads")

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(invoice.router, prefix="/api/invoices", tags=["invoices"])
app.include_router(menu.router, prefix="/api/menus", tags=["menus"])
app.include_router(carbon.router, prefix="/api/carbon", tags=["carbon"])

@app.get("/")
async def root():
    return {"message": "Welcome to Fork+ API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
