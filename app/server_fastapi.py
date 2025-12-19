import traceback
from typing import Annotated

from fastapi import FastAPI, Request, Response, status
from contextlib import asynccontextmanager
from pydantic import BaseModel, field_validator, AfterValidator

import uvicorn
import time

from config import load_ml_model, uvicorn_log_config, predict, logger


def validate_model_name(model: str) -> str:
    allowed_models = ['SVC', 'NB']
    if model not in allowed_models:
        raise ValueError(f"Model must be one of: {allowed_models}")
    return model

# ----- API Configuration -----
class Message(BaseModel):
    text: str
    model: Annotated[str, AfterValidator(validate_model_name)]


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

        model_choice = request.model
        model = model_nb if model_choice == 'NB' else model_svc

        prediction = predict(text, model, tokenizer)
        # logger.info(f"Received text: {text} | Prediction: {prediction}")
        return {"text": text, "prediction": prediction, "model_used": type(model).__name__}
    except Exception as e:
        logger.error(f"Error in /predict endpoint: {e}")
        traceback.print_exc()
        return {"error": "An error occurred during prediction."}



# ----- Application Start -----
if __name__ == "__main__":

    try:
        model_nb, model_svc, tokenizer = load_ml_model()
    except Exception as e:
        logger.critical("Failed to load ML model and tokenizer. Exiting application.")
        exit(1)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_config=uvicorn_log_config
    )