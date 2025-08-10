import os
import logging
from fastapi import FastAPI

logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = FastAPI()

@app.get("/")
async def root() -> str:
    return "Hello, world!"

@app.get("/health")
async def health_check() -> dict:
    return {"status": "healthy"}