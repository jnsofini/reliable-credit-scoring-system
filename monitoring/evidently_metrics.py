import datetime
import time
import random
import logging 
import pandas as pd
import numpy as np
import io
import psycopg
import db
import storage
from pathlib import Path

from prefect import task, flow

from evidently.report import Report
from evidently import ColumnMapping
from evidently.metrics import (
    ColumnDriftMetric, 
    DatasetDriftMetric, 
    DatasetMissingValuesMetric,
)

from optbinning import Scorecard

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")

SEND_TIMEOUT = 10
rand = random.Random()
FILE_DIR = Path(__file__).parent
DATA_PATH = FILE_DIR/"data"
DATABASE = "TEST_DB_1"

create_table_statement = """
drop table if exists risk_score_metrics;
create table risk_score_metrics(
	timestamp timestamp,
	prediction_drift float,
	num_drifted_columns integer,
	share_missing_values float
)
"""

def get_data(path):
    x_train = pd.read_parquet(f"{path}/X_train.parquet")
    y_train = pd.read_parquet(f"{path}/y_train.parquet")
    x_val = pd.read_parquet(f"{path}/X_val.parquet")
    y_val = pd.read_parquet(f"{path}/y_val.parquet")
    train = x_train.assign(RiskPerformance=y_train.values)
    val = x_val.assign(RiskPerformance=y_val.values)

    return train, val

    
reference_data, raw_data = get_data(path=DATA_PATH)
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
raw_data["operation_date"] = [datetime.datetime(2023, 2, day, 0, 0) for day in np.random.randint(1, 13, size=raw_data.shape[0])]#datetime.datetime(2023, 2, 1, 0, 0)#pd.to_datetime(raw_data["operation_date"])

begin = datetime.datetime(2023, 2, 1, 0, 0)

# cat_features = []
num_features = [
            "AverageMInFile",
            "MSinceMostRecentInqexcl7days",
            "PercentTradesNeverDelq",
            "ExternalRiskEstimate",
            "NetFractionRevolvingBurden",
            "NumSatisfactoryTrades",
            "PercentInstallTrades"
      ]
column_mapping = ColumnMapping(
    target=None,
    prediction='prediction',
    numerical_features=num_features,
    # categorical_features=cat_features
)

report = Report(metrics=[
    ColumnDriftMetric(column_name='prediction'),
    DatasetDriftMetric(),
    DatasetMissingValuesMetric()
]
)


@task
def calculate_metrics_postgresql(curr, i): #i is aggregate period
	current_data = raw_data[(raw_data.operation_date >= (begin + datetime.timedelta(days=i))) &
		(raw_data.operation_date < (begin + datetime.timedelta(days=i + 1)))]

	#current_data.fillna(0, inplace=True)
	current_data['prediction'] = model.score(current_data)

	report.run(reference_data = reference_data, current_data = current_data,
		column_mapping=column_mapping)

	result = report.as_dict()

	prediction_drift = result['metrics'][0]['result']['drift_score']
	num_drifted_columns = result['metrics'][1]['result']['number_of_drifted_columns']
	share_missing_values = result['metrics'][2]['result']['current']['share_of_missing_values']

	curr.execute(
		"insert into risk_score_metrics(timestamp, prediction_drift, num_drifted_columns, share_missing_values) values (%s, %s, %s, %s)",
		(begin + datetime.timedelta(i), prediction_drift, num_drifted_columns, share_missing_values)
	)

@flow
def batch_monitoring_backfill():

	db.prepare_database(create_table_=create_table_statement)
	sync_connecttion = storage.db_connection_string(data_base=DATABASE)
	last_send = datetime.datetime.now() - datetime.timedelta(seconds=10)
	with psycopg.connect("host=localhost port=5432 dbname=test user=postgres password=password", autocommit=True) as conn:
		for i in range(0, 27):
			with conn.cursor() as curr:
				calculate_metrics_postgresql(curr, i)

			new_send = datetime.datetime.now()
			seconds_elapsed = (new_send - last_send).total_seconds()
			if seconds_elapsed < SEND_TIMEOUT:
				time.sleep(SEND_TIMEOUT - seconds_elapsed)
			while last_send < new_send:
				last_send = last_send + datetime.timedelta(seconds=10)
			logging.info("data sent")

if __name__ == '__main__':
	batch_monitoring_backfill()
