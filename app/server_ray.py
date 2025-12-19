# ==============================================
# uzycie:   serve run app.server_ray:server_ray
# ==============================================

import traceback
import time
from typing import Annotated

from fastapi import FastAPI, Request, Response, status
from pydantic import BaseModel, AfterValidator
from ray import serve

from app.config import load_ml_model, predict, logger


def validate_model_name(model: str) -> str:
    allowed_models = ['SVC', 'NB']
    if model not in allowed_models:
        raise ValueError(f"Model must be one of: {allowed_models}")
    return model


class Message(BaseModel):
    text: str
    model: Annotated[str, AfterValidator(validate_model_name)]


app = FastAPI()


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


@serve.deployment(num_replicas=1, ray_actor_options={"num_cpus": 1})
@serve.ingress(app)
class MLService:
    def __init__(self):
        logger.info("[Ray] Initializing service... Loading models...")
        try:
            self.model_nb, self.model_svc, self.tokenizer = load_ml_model()
            logger.info("[Ray] Models loaded successfully.")
        except Exception as e:
            logger.critical(f"Failed to load ML models: {e}")
            raise e


    @app.get('/')
    def index(self):
        return {"message": "ML Models API is running on Ray Serve."}

    @app.get('/status', status_code=status.HTTP_200_OK)
    def health_check(self):
        ready = hasattr(self, 'model_nb') and hasattr(self, 'model_svc')
        return {'status': 'running', 'models_loaded': ready}

    @app.post('/predict')
    async def predict_endpoint(self, request: Message):
        try:
            text = request.text
            if not text:
                return {"error": "No text provided for prediction."}

            model_choice = request.model

            model_choice = request.model
            model = self.model_nb if model_choice == 'NB' else self.model_svc

            prediction = predict(text, model, self.tokenizer)
            # logger.info(f"Received text: {text} | Prediction: {prediction}")
            return {"text": text, "prediction": prediction, "model_used": type(model).__name__}

        except Exception as e:
            logger.error(f"Error in /predict endpoint: {e}")
            traceback.print_exc()
            return {"error": "An error occurred during prediction."}


server_ray = MLService.bind()
