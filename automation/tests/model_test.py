from pathlib import Path

import pandas as pd
from deepdiff import DeepDiff

import model

customer = {
    "cust": {
        "riskperformance": 0,
        "externalriskestimate": 79,
        "msinceoldesttradeopen": 133,
        "msincemostrecenttradeopen": 2,
        "averageminfile": 68,
        "numsatisfactorytrades": 27,
        "numtrades60ever2derogpubrec": 0,
        "numtrades90ever2derogpubrec": 0,
        "percenttradesneverdelq": 100,
        "msincemostrecentdelq": -7,
        "maxdelq2publicreclast12m": 7,
        "maxdelqever": 8,
        "numtotaltrades": 30,
        "numtradesopeninlast12m": 3,
        "percentinstalltrades": 36,
        "msincemostrecentinqexcl7days": 0,
        "numinqlast6m": 4,
        "numinqlast6mexcl7days": 4,
        "netfractionrevolvingburden": 1,
        "netfractioninstallburden": 93,
        "numrevolvingtradeswbalance": 4,
        "numinstalltradeswbalance": 2,
        "numbank2natltradeswhighutilization": 0,
        "percenttradeswbalance": 60,
    },
    "cust_id": 6,
}


class MockModel:
    def __init__(self, value=10):
        self.value = value

    def score(self, X):
        n = len(X)
        return [self.value] * n


def read_text(file):
    test_directory = Path(__file__).parent

    with open(test_directory / file, 'rt', encoding='utf-8') as f_in:
        return f_in.read().strip()


def test_predict():
    model_mock = MockModel(10)
    model_service = model.ModelService(model_mock)
    customer_data = pd.DataFrame([customer["cust"]])
    actual_score = model_service.predict(customer_data)
    expected_score = 10

    assert actual_score == expected_score


def test_lambda_handler():
    model_mock = MockModel(10)
    model_version = "test123"
    model_service = model.ModelService(model=model_mock, model_version=model_version)

    base64_input = read_text('data.b64')
    event = {
        "Records": [
            {
                "kinesis": {
                    "data": base64_input,
                },
            }
        ]
    }
    actual_scores = model_service.lambda_handler(event)
    expected_scores = {
        "predictions": [
            {
                'model': 'risk_score_model',
                'version': model_version,
                'prediction': {
                    'cust_score': 10,
                    'cust_id': 6,
                },
            },
        ]
    }

    assert actual_scores == expected_scores


def test_base64_decode():
    base64_input = read_text('data.b64')
    actual_result = model.base64_decode(base64_input)
    expected_result = customer

    assert actual_result == expected_result


def test_prepare_features():
    model_service = model.ModelService(None)

    actual_features = model_service.prepare_features(customer)
    expected_features = pd.DataFrame([customer["cust"]])
    print(actual_features)
    print(expected_features)

    diff = DeepDiff(
        actual_features.to_dict(orient="records"),
        expected_features.to_dict(orient="records"),
        significant_digits=1,
    )
    assert 'values_changed' not in diff
    assert 'values_change' not in diff
    print("Difference is: ", diff)


# test_prepare_features()
