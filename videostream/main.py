from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.admin import api_router as admin_router
from routers.tasks import api_router as tasks_router
from routers.user import api_router as user_router
from uvicorn import run
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.requests import Request
import time
from utils.logger import logger
from tracing import setup_tracing

app = FastAPI()
setup_tracing(app, "cinema_videostream")

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

app.include_router(admin_router)
app.include_router(user_router)
app.include_router(tasks_router)

if __name__ == "__main__":
    run("main:app", host="0.0.0.0", port=8002, log_level="debug", timeout_keep_alive=60)
