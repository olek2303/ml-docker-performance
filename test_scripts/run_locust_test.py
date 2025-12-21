# ========================================
# ==    locust -f run_locust_test.py    ==
# ========================================

import pandas as pd
import random
import os
from locust import HttpUser, task, between


CSV_PATH = "../text_classification_analysis/data/mental_health_data.csv"

data_samples = []

try:
    df = pd.read_csv(CSV_PATH)
    data_samples = df['statement'].dropna().tolist()
except Exception as e:
    print(f"No data file found.")

print(f"Loaded {len(data_samples)} samples for testing.")

class MLUser(HttpUser):
    wait_time = between(0.5, 2)

    @task
    def predict_endpoint(self):
        input_text = random.choice(data_samples)
        model = random.choice(['SVC', 'NB'])

        payload = {
            "text": input_text,
            "model": model
        }

        with self.client.post("/predict", json=payload, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status: {response.status_code} | Error: {response.text[:100]}")
