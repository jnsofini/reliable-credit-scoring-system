import json

import requests
from deepdiff import DeepDiff

with open('event.json', 'rt', encoding='utf-8') as f_in:
    event = json.load(f_in)


# # Test contenerized lambda

url = 'http://localhost:8080/2015-03-31/functions/function/invocations'
response = requests.post(url, json=event, timeout=30)
print('Actual response:')
actual_response = response.json()
print(json.dumps(actual_response, indent=4))

expected_response = {
    "predictions": [
        {
            'model': 'risk_score_model',
            'version': 'Test123',  # "1dfce710dc824ecab012f7d910b190f6",
            'prediction': {
                'cust_score': 665,
                'cust_id': 6,
            },
        }
    ]
}

diff = DeepDiff(actual_response, expected_response, significant_digits=1)
assert 'values_changed' not in diff
assert 'values_change' not in diff
print("Difference is: ", diff)
