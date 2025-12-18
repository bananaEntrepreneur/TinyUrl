from fastapi import FastAPI
from .database import Base, engine
from .api.v1.urls import router as urls_router


app = FastAPI(title="TinyURL API", version="1.0.0")

Base.metadata.create_all(bind=engine)

app.include_router(urls_router, prefix="/api/v1", tags=["urls"])


@app.get("/")
async def read_root():
    return {"message": "Welcome to the TinyURL API"}