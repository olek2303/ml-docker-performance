from fastapi import FastAPI, Request, Response
from contextlib import asynccontextmanager

import uvicorn
import logging
import sys
import time

# ----- Helper Functions -----


# ----- Logging Configuration -----

logger = logging.getLogger("API_LOGGER")
logger.setLevel(logging.INFO)

LOG_FORMAT = "[%(asctime)s] [%(levelname)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


# ----- API Configuration -----

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("[Lifespan] Server is starting up...")
    yield
    logger.info("[Lifespan] Server is shutting down...")

app = FastAPI(lifespan=lifespan)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    path = request.url.path
    method = request.method

    response: Response = await call_next(request)

    process_time = (time.time() - start_time) * 1000
    formatted_process_time = f"{process_time:.2f}ms"

    logger.info(
        f"REQ: {method} {path} - Status: {response.status_code} - Czas: {formatted_process_time}"
    )

    return response

@app.get('/')
def index():
    return {"message": "ML Models API is running."}


# ----- Application Start -----

uvicorn_log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": LOG_FORMAT,
            "datefmt": DATE_FORMAT,
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "uvicorn": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False
        },
        "uvicorn.error": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False
        },
        "uvicorn.access": {
            "handlers": [],
            "level": "CRITICAL",
            "propagate": False
        },
    },
}

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_config=uvicorn_log_config
    )