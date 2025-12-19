import asyncio
import aiohttp
import pandas as pd
import time

url = "http://localhost:8000/predict"
model = 'NB'    # albo 'SVC'
type_run = 'ray'  # albo 'fastapi'
output_filename = f"../results/docker_run_{model}_{type_run}_test_results.csv"

async def process_api_request(session, input_data):
    payload = {"text": input_data, "model": model}
    start_time = time.perf_counter()

    try:
        async with session.post(url, json=payload) as response:
            if response.status == 200:
                json_response = await response.json()
                end_time = time.perf_counter()
                duration = end_time - start_time

                return True, input_data, json_response, duration
            else:
                error_text = await response.text()
                end_time = time.perf_counter()
                duration = end_time - start_time
                return False, input_data, f"Status {response.status}", duration

    except Exception as e:
        end_time = time.perf_counter()
        return False, input_data, str(e), end_time - start_time


async def run_concurrent_requests(input_data_list):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for input_text in input_data_list:
            tasks.append(process_api_request(session, input_text))

        return await asyncio.gather(*tasks)


if __name__ == "__main__":

    df_test_data = pd.read_csv("../text_classification_analysis/data/mental_health_data.csv")
    test_inputs = df_test_data['statement'].sample(200, random_state=42).tolist()

    print(f"Sending {len(test_inputs)} test inputs")
    results = asyncio.run(run_concurrent_requests(test_inputs))

    saved_data = []

    for success, input_text, output, duration in results:
        record = {
            "input_text": input_text,
            "duration_seconds": round(duration, 4),
            "status": "success" if success else "error"
        }

        if success:
            if isinstance(output, dict):
                record.update(output)
            else:
                record["api_response"] = output
        else:
            record["error_details"] = output

        saved_data.append(record)

    df_results = pd.DataFrame(saved_data)
    df_results.to_csv(output_filename, index=False)

    print(f"Test completed, results saved to {output_filename}")

