""" 
Calculate metrics using evidently.
"""
import datetime
import io
import logging
import random
import time

# import storage
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
from evidently import ColumnMapping
from evidently.metrics import (
    ColumnDriftMetric,
    DatasetDriftMetric,
    DatasetMissingValuesMetric,
)
from evidently.report import Report
from optbinning import Scorecard
from prefect import flow, task
import os
from src.db import prepare_table, prepare_database  # pylint: disable=import-error

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s"
)

SEND_TIMEOUT = 10
rand = random.Random()
# FILE_DIR = Path(__file__).parent
# DATA_PATH = FILE_DIR / "data"
DATABASE = "TEST_DB_1"
BASE_PATH = Path(__file__).parent
PROJECT_ROOT = BASE_PATH.parent

DATA_BASE_PATH = BASE_PATH.parent / "data"

CREATE_TABLE_STATEMENT = """
drop table if exists risk_score_metrics;
create table risk_score_metrics(
	timestamp timestamp,
	prediction_drift float,
	num_drifted_columns integer,
	share_missing_values float
)
"""
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_USER = os.getenv("POSTGRES_USER", "monitoring")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "monitoring")
DATA_BASE = os.getenv("DATA_BASE", "monitoring")
postgres_conn = (
    f"host={POSTGRES_HOST} port={POSTGRES_PORT} "
    f"user={POSTGRES_USER} password={POSTGRES_PASSWORD}"
)


def get_data(path):
    """Reads train and test fata from path."""
    x_train = pd.read_parquet(f"{path}/X_train.parquet")
    y_train = pd.read_parquet(f"{path}/y_train.parquet")
    x_val = pd.read_parquet(f"{path}/X_val.parquet")
    y_val = pd.read_parquet(f"{path}/y_val.parquet")
    train = x_train.assign(RiskPerformance=y_train.values)
    val = x_val.assign(RiskPerformance=y_val.values)

    return train, val


reference_data, raw_data = get_data(path=DATA_BASE_PATH)
# print(reference_data.head())
# print(raw_data.head())
TARGET = "RiskPerformance"
# reference_data = pd.read_parquet('data/reference.parquet')
model = Scorecard.load("models/scorecard-model.pkl")
# Score the reference data
reference_data['prediction'] = model.score(reference_data)
# raw_data = pd.read_parquet('data/raw.parquet')

# We don'y have that to batch on. So what we do is simulate data by adding days in Feb 2023
#  to the data we have so that we can get daily events.
raw_data["operation_date"] = [
    datetime.datetime(2023, 2, day, 0, 0)
    for day in np.random.randint(1, 13, size=raw_data.shape[0])
]  # datetime.datetime(2023, 2, 1, 0, 0)#pd.to_datetime(raw_data["operation_date"])

begin = datetime.datetime(2023, 2, 1, 0, 0)

# cat_features = []
num_features = [
    "AverageMInFile",
    "MSinceMostRecentInqexcl7days",
    "PercentTradesNeverDelq",
    "ExternalRiskEstimate",
    "NetFractionRevolvingBurden",
    "NumSatisfactoryTrades",
    "PercentInstallTrades",
]
column_mapping = ColumnMapping(
    target=None,
    prediction='prediction',
    numerical_features=num_features,
    # categorical_features=cat_features
)

report = Report(
    metrics=[
        ColumnDriftMetric(column_name='prediction'),
        DatasetDriftMetric(),
        DatasetMissingValuesMetric(),
    ]
)


@task
def calculate_metrics_postgresql(i):  # i is aggregate period
    """Calculate evidently metrics and insert in data base."""
    current_data = raw_data[
        (raw_data.operation_date >= (begin + datetime.timedelta(days=i)))
        & (raw_data.operation_date < (begin + datetime.timedelta(days=i + 1)))
    ]

    # current_data.fillna(0, inplace=True)
    current_data['prediction'] = model.score(current_data)

    report.run(
        reference_data=reference_data,
        current_data=current_data,
        column_mapping=column_mapping,
    )

    result = report.as_dict()

    prediction_drift = result['metrics'][0]['result']['drift_score']
    num_drifted_columns = result['metrics'][1]['result']['number_of_drifted_columns']
    share_missing_values = result['metrics'][2]['result']['current'][
        'share_of_missing_values'
    ]
    return prediction_drift, num_drifted_columns, share_missing_values
    # insert_cols = "timestamp, prediction_drift, num_drifted_columns, share_missing_values"
    # curr.execute(
    #     f"insert into risk_score_metrics({insert_cols}) values (%s, %s, %s, %s)",
    #     (
    #         begin + datetime.timedelta(i),
    #         prediction_drift,
    #         num_drifted_columns,
    #         share_missing_values,
    #     ),
    # )


@flow
def batch_monitoring_backfill():
    """Backfil the data by adding the prediction to the develoment data"""
    prepare_database(conn_string=postgres_conn, dbname=DATA_BASE)
    table_name = prepare_table(
        db_conn=postgres_conn, create_table_=CREATE_TABLE_STATEMENT
    )
    # sync_connection = storage.db_connection_string(data_base=DATABASE)
    last_send = datetime.datetime.now() - datetime.timedelta(seconds=10)
    with psycopg.connect(
        f"{postgres_conn} dbname={DATA_BASE}",
        autocommit=True,
    ) as conn:
        for i in range(0, 27):
            with conn.cursor() as curr:
                (
                    prediction_drift,
                    num_drifted_columns,
                    share_missing_values,
                ) = calculate_metrics_postgresql(i)

                # Send the data to database

                insert_cols = "timestamp, prediction_drift, num_drifted_columns, share_missing_values"
                curr.execute(
                    f"insert into risk_score_metrics({insert_cols}) values (%s, %s, %s, %s)",
                    (
                        begin + datetime.timedelta(i),
                        prediction_drift,
                        num_drifted_columns,
                        share_missing_values,
                    ),
                )

            new_send = datetime.datetime.now()
            seconds_elapsed = (new_send - last_send).total_seconds()
            if seconds_elapsed < SEND_TIMEOUT:
                time.sleep(SEND_TIMEOUT - seconds_elapsed)
            while last_send < new_send:
                last_send = last_send + datetime.timedelta(seconds=10)
            logging.info("data sent")


if __name__ == '__main__':
    batch_monitoring_backfill()
