"""Module to run test of scripts."""

import os

# import mlflow
import pickle

import boto3


# New code using boto3
def load_model(run_id):
    """Loading model with boto3 package only

    Args:
        run_id (str): The path to the model, or so called key without the
        file name.

    Returns:
        Scorecard: Scoring model
    """
    # model_path = get_model_location(run_id=run_id)
    # if not model_path.startswith("s3://"):
    #     return load_with_scorecard(f"{model_path}/model.pkl")

    s3client = boto3.client('s3')
    response = s3client.get_object(
        Bucket=os.getenv('MODEL_BUCKET'),
        Key=f'scorecards/{run_id}/model.pkl',
    )

    body = response['Body'].read()
    model_ = pickle.loads(body)

    return model_


RUN_ID = "dev"

model = load_model(run_id=RUN_ID)
