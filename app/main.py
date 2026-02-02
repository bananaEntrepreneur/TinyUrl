from contextlib import asynccontextmanager
from fastapi import FastAPI
from .database import Base
from .core.config import get_engine
from .api.v1.urls import router
from .utils.logging import configure_logging
from datetime import datetime


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()

    engine = get_engine()
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
    except Exception as e:
        print(f"Warning: Could not create database tables: {e}")
        print("Make sure your database is running and credentials are correct")
    yield


app = FastAPI(title="TinyURL API", version="1.0.0", lifespan=lifespan)


app.include_router(router, prefix="/api/v1")


@app.get("/")
async def read_root():
    return {"message": "Welcome to the TinyURL API"}


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "service": "tinyurl-api"
    }