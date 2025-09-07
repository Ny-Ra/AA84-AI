import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from routes import image_router

load_dotenv()

logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = FastAPI()

app.include_router(image_router)

@app.get("/")
async def root() -> str:
    return "Hello, world!"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)