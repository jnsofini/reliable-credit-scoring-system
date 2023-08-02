#!/usr/bin/env python
# coding: utf-8
# pylint: disable=logging-fstring-interpolation

""" 
Batch deployment script.

This module is used to run the back deployment. It loads the model from
the registry and runs a prediction.
"""

import os
import pickle
import sys
import uuid
from datetime import datetime

import boto3
import pandas as pd
from prefect import flow, get_run_logger, task
from prefect.context import get_run_context

# import logging as logger
# logger.basicConfig(format='%(levelname)s:%(message)s', encoding='utf-8', level=logger.INFO)


# from dateutil.relativedelta import relativedelta


BUCKET = "moose-solutions-mlops-registry"
SCORE_BUCKET = os.getenv("SCORE_BUCKET", "moose-solutions")  # -mlops-learning")
SUB_DIR = "mlops-zoomcamp"
RUN_TYPE = "Test"


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
        Bucket=os.getenv('MODEL_BUCKET', 'moose-solutions-mlops-registry'),
        Key=f'scorecards/{run_id}/model.pkl',
    )

    body = response['Body'].read()
    model = pickle.loads(body)

    return model


def generate_uuids(num):
    """Generate n UUID"""
    return [str(uuid.uuid4()) for _ in range(num)]


def read_dataframe(filename: str, features: list[str] | None = None) -> pd.DataFrame:
    """Reads data and return a set of columns.

    Args:
        filename (str): path to the file to read
        features (list[str] | None, optional): List of features to retain. Defaults to None.

    Returns:
        pd.DataFrame: Data
    """

    data = pd.read_parquet(filename)
    if features:
        return data[features]
    return data


def prepare_data(data: pd.DataFrame) -> pd.DataFrame:
    """Adds column `id` to the data."""
    data["id"] = generate_uuids(data.shape[0])
    return data


def save_results(
    data: pd.DataFrame,
    score: list[int],
    output_file: str,
    run_date: str,
    model_meta_data: dict[str, str],
) -> None:
    """Adds information to the original data and saves results.

    Adds score, run_id and model version to the data.

    Args:
        data (pd.DataFrame): Data to score
        score (list[int]): Array of scores
        run_id (str): Run id gotten from model registy
        output_file (str): Path to store file
        run_date (str): Date when the model was run
        model_version (str, optional): Version of the model that is used. Defaults to "".
    """
    df_result = data.copy()
    df_result["score_date"] = run_date
    df_result['score'] = score
    df_result['run_id'] = model_meta_data.get("run_id")
    df_result['model_version'] = model_meta_data.get("model_version", None)

    if RUN_TYPE.lower() != "test":
        df_result.to_parquet(output_file, index=False)
    # print(df_result.head())


@task
def apply_model(
    input_file: str, run_id: str, output_file: str, run_date: datetime
) -> str:
    """Apply various steps to run the mode.

    Reads data, runs predic and saves results

    Args:
        input_file (str): File containing the data to score
        run_id (str): Model experiment run id
        output_file (str): File to save output
        run_date (datetime): Date when the experiment was run

    Returns:
        str: Location of the customer score.
    """
    logger = get_run_logger()

    logger.info(f'reading the data from {input_file}...')
    x_data = read_dataframe(input_file)

    logger.info(f'Loading the model with RUN_ID={run_id}...')
    model = load_model(run_id)

    logger.info('Applying the model...')
    predicted_score = model.score(x_data)

    logger.info(f'Saving the result to {output_file}...')

    save_results(
        data=x_data,
        score=predicted_score,
        output_file=output_file,
        run_date=run_date,
        model_meta_data={"run_id": run_id, "model_version": run_id},
    )

    return output_file


def get_paths(snapshot):
    """Gets the location of the source data and destination of scores."""
    input_file = f"s3://{SCORE_BUCKET}/data/{snapshot}/x_data.parquet"
    output_file = f"s3://{SCORE_BUCKET}/data/{snapshot}/scores.parquet"

    return input_file, output_file


@flow
def credit_score_prediction(data_id: str = '2023-aug', run_id: str = "dev"):
    """Gets the data, scores and saves.

    Args:
        data_id (str): The id of the data to use in form `year-month` ex. 2023-aug
        run_id (str, optional): The run id of the model used. Defaults to "dev".
    """
    # run_date = datetime.now().isoformat()#get_run_context().flow_run.expected_start_time
    prefect_context = get_run_context()
    run_date = prefect_context.flow_run.expected_start_time

    input_file, output_file = get_paths(data_id)

    logger = get_run_logger()
    logger.info(f"Data Source: {input_file}")
    logger.info(f"Data Destinitaion: {output_file}")

    apply_model(
        input_file=input_file, run_id=run_id, output_file=output_file, run_date=run_date
    )


# @flow
# def run():
#     """Runs credit score prediction"""
#     data_id = '2023-aug' or sys.argv[1]  # '2023-aug'
#     credit_score_prediction(data_id=data_id)


if __name__ == '__main__':
    DATA_ID = '2023-aug' or sys.argv[1]
    credit_score_prediction(data_id=DATA_ID)
