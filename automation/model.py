import base64
import json
import os
import pickle

import boto3
import mlflow
import pandas as pd
from s3fs.core import S3FileSystem
from optbinning import Scorecard
from config import col_map


def get_model_mlflow_location(run_id):
    model_location = os.getenv('MODEL_LOCATION')

    if model_location is not None:
        return model_location

    model_bucket = os.getenv('MODEL_BUCKET', 'moose-solutions-mlops-registry')
    experiment_id = os.getenv('MLFLOW_EXPERIMENT_ID', '1')

    model_location = f's3://{model_bucket}/{experiment_id}/{run_id}/artifacts/model'
    return model_location


def get_model_location(run_id):
    model_location = os.getenv('MODEL_LOCATION')

    if model_location is not None:
        return model_location

    model_bucket = os.getenv('MODEL_BUCKET', 'moose-solutions-mlops-registry')

    model_location = f's3://{model_bucket}/scorecards/{run_id}'
    return model_location


def load_model_mlflow(run_id):
    model_path = get_model_mlflow_location(run_id)
    model = mlflow.pyfunc.load_model(model_path)
    return model


# def load_model(run_id):
#     print("Loading Model=================================")
#     model_path = get_model_location(run_id)
#     model = Scorecard.load(f"{model_path}/model.pkl")
#     return model

def load_with_scorecard(path):
    return Scorecard.load(path)


def load_model(run_id):
    model_path = get_model_location(run_id=run_id)
    if not model_path.startswith("s3://"):
        return load_with_scorecard(f"{model_path}/model.pkl")
    s3_file = S3FileSystem(
        anon=False,
        secret=os.getenv("AWS_SECRET_ACCESS_KEY"),
        key=os.getenv("AWS_ACCESS_KEY_ID"),
    )
    model = pickle.load(s3_file.open(f"{model_path}/model.pkl"))
    return model


def base64_decode(encoded_data):
    decoded_data = base64.b64decode(encoded_data).decode('utf-8')
    cust_event = json.loads(decoded_data)
    return cust_event


class ModelService:
    def __init__(self, model, model_version=None, callbacks=None):
        self.model = model
        self.model_version = model_version
        self.callbacks = callbacks or []

    def prepare_features(self, record):
        return pd.DataFrame([record]).rename(columns=col_map)

    def predict(self, features):
        score = self.model.score(features)
        return int(score[0])

    def lambda_handler(self, event):
        # print(json.dumps(event))

        predictions_events = []

        for record in event['Records']:
            encoded_data = record['kinesis']['data']
            cust_event = base64_decode(encoded_data)

            print(cust_event)
            cust = cust_event['cust']
            cust_id = cust_event['cust_id']

            print("Preparing Features=================================")
            features = self.prepare_features(cust)
            print("Scoring =================================")
            prediction = self.predict(features)
            print("--------------------made it here-----------------")
            prediction_event = {
                'model': 'risk_score_model',
                'version': self.model_version,
                'prediction': {'cust_score': prediction, 'cust_id': cust_id},
            }
            for callback in self.callbacks:
                callback(prediction_event)

            predictions_events.append(prediction_event)

        return {'predictions': predictions_events}


class KinesisCallback:
    def __init__(self, kinesis_client, prediction_stream_name):
        self.kinesis_client = kinesis_client
        self.prediction_stream_name = prediction_stream_name

    def put_record(self, prediction_event):
        cust_id = prediction_event['prediction']['cust_id']

        self.kinesis_client.put_record(
            StreamName=self.prediction_stream_name,
            Data=json.dumps(prediction_event),
            PartitionKey=str(cust_id),
        )


def create_kinesis_client():
    endpoint_url = os.getenv('KINESIS_ENDPOINT_URL')

    if endpoint_url is None:
        return boto3.client('kinesis')

    return boto3.client('kinesis', endpoint_url=endpoint_url)


def init(prediction_stream_name: str, run_id: str, test_run: bool):
    model = load_model(run_id)

    callbacks = []

    if not test_run:
        kinesis_client = create_kinesis_client()
        kinesis_callback = KinesisCallback(kinesis_client, prediction_stream_name)
        callbacks.append(kinesis_callback.put_record)

    model_service = ModelService(model=model, model_version=run_id, callbacks=callbacks)

    return model_service
