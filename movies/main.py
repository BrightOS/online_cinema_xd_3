from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import run
from routes import list_of_routes
from prometheus_fastapi_instrumentator import Instrumentator
from logger import logger, setup_logging
from tracing import setup_tracing
from starlette.requests import Request
import time

setup_logging()

app = FastAPI()
setup_tracing(app, "cinema_api")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(f"Method: {request.method} Path: {request.url.path} Status: {response.status_code} Duration: {duration:.2f}s")
    return response

Instrumentator().instrument(app).expose(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for route in list_of_routes:
    app.include_router(route)

if __name__ == "__main__":
    run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_level="debug",
        timeout_keep_alive=60
    )
