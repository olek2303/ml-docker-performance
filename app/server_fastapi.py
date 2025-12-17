import traceback

from fastapi import FastAPI, Request, Response, status
from contextlib import asynccontextmanager

from pydantic import BaseModel
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfVectorizer

import uvicorn
import logging
import sys
import time
import joblib

NAIVE_BAYES_MODEL_PATH = "./models/naive_bayes_original.joblib"
TFIDF_TOKENIZER_PATH = "./models/tfidf_original.joblib"
SVC_MODEL_PATH = "./models/svc_original.joblib"


# ----- Logging Configuration -----
logger = logging.getLogger("API_LOGGER")
logger.setLevel(logging.INFO)

LOG_FORMAT = "[%(asctime)s] [%(levelname)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

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


# ----- API Configuration -----
class Message(BaseModel):
    text: str

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

@app.get('/status', status_code=status.HTTP_200_OK)
def index():
    return {'status': 'running'}

@app.post('/predict')
async def predict_endpoint(request: Message):
    try:
        text = request.text
        if not text:
            return {"error": "No text provided for prediction."}

        prediction = predict(text)
        # logger.info(f"Received text: {text} | Prediction: {prediction}")
        return {"text": text, "prediction": prediction}
    except Exception as e:
        logger.error(f"Error in /predict endpoint: {e}")
        traceback.print_exc()
        return {"error": "An error occurred during prediction."}


# ----- Helper Functions -----
def load_ml_model():
    try:
        model = joblib.load(NAIVE_BAYES_MODEL_PATH)
        tokenizer = joblib.load(TFIDF_TOKENIZER_PATH)
        logger.info("ML model and tokenizer loaded successfully.")
        return model, tokenizer
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        traceback.print_exc()
        raise e

def predict(text: str):
    try:
        X = tokenizer.transform([text])
        prediction = model.predict(X)
        return prediction[0]
    except Exception as e:
        logger.error(f"Error during prediction: {e}")
        traceback.print_exc()
        raise e


# ----- Application Start -----
if __name__ == "__main__":
    model, tokenizer = load_ml_model()
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_config=uvicorn_log_config
    )