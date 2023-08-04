import requests
import json
from pathlib import Path
import os
from deepdiff import DeepDiff

FILE_DIR = Path(__file__).parent

def read_json(path):
    """Reads json data to a python dict."""
    with open(file=path, mode="r", encoding="utf-8") as fhandle:
        data = json.load(fhandle)
    return data

customers = read_json(FILE_DIR/"data.json")

def get_endpount():
   """Gets url endpoint."""
   port = os.getenv("PORT", 8002)
   url_data = {
       "local": f"http://localhost:{port}/predict",
       "fly": "https://credit-scoring.fly.dev/predict",
   }
   deployment_env = os.getenv("DEPLOY_ENV", "local")
   api_endpoint = os.getenv(deployment_env, url_data[deployment_env])

   return api_endpoint

url = get_endpount()
response = requests.post(url, json=customers)

# print('Actual response:')
actual_response = response.json()
# print(json.dumps(actual_response, indent=6))
expected_response = read_json(FILE_DIR/"expected.json")
# print(json.dumps(actual_response, indent=6))

diff = DeepDiff(actual_response, expected_response, significant_digits=1)
assert 'type_changes' not in diff
assert 'values_changed' not in diff
print(f"Difference is:  {diff}")
