import sys
import traceback

from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
import logging
from datetime import datetime

date = datetime.now()

NAIVE_BAYES_MODEL_PATH = "./models/naive_bayes_original.joblib"
SVC_MODEL_PATH = "./models/svc_original.joblib"
TFIDF_TOKENIZER_PATH = "./models/tfidf_original.joblib"
LOG_FILENAME = f"./results/logs/{date.month}{date.day}_{date.hour}{date.minute}{date.second}.log"

# ----- Helper Functions -----
def load_ml_model():
    try:
        model_nb = joblib.load(NAIVE_BAYES_MODEL_PATH)
        model_svc = joblib.load(SVC_MODEL_PATH)
        tokenizer = joblib.load(TFIDF_TOKENIZER_PATH)
        logger.info("ML model and tokenizer loaded successfully.")
        return model_nb, model_svc, tokenizer
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        traceback.print_exc()
        raise e

def predict(text: str, model, tokenizer):
    try:
        X = tokenizer.transform([text])
        prediction = model.predict(X)
        return prediction[0]
    except Exception as e:
        logger.error(f"Error during prediction: {e}")
        traceback.print_exc()
        raise e


# ----- Logging Configuration -----
logger = logging.getLogger("API_LOGGER")
logger.setLevel(logging.INFO)

LOG_FORMAT = "[%(asctime)s] [%(levelname)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

file_handler = logging.FileHandler(LOG_FILENAME, mode='a', encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

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
        # Dodajemy handler plikowy do konfiguracji Uvicorna
        "file": {
            "class": "logging.FileHandler",
            "formatter": "default",
            "filename": LOG_FILENAME,
            "mode": "a",
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "uvicorn": {
            # Dodajemy "file" do listy handlerów
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False
        },
        "uvicorn.error": {
            # Dodajemy "file" do listy handlerów
            "handlers": ["console", "file"],
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