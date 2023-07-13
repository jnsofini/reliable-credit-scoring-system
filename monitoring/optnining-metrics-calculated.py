import datetime
import time
import random
import logging 
import pandas as pd
import numpy as np
import io
import psycopg

from prefect import task, flow

from evidently.report import Report
from evidently import ColumnMapping
from evidently.metrics import ColumnDriftMetric, DatasetDriftMetric, DatasetMissingValuesMetric

from optbinning import Scorecard
from optbinning.scorecard import ScorecardMonitoring

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")

SEND_TIMEOUT = 10
rand = random.Random()
DATA_BASE_PATH = "/home/fini/Learning/CreditRisk/crm-simple-scorecard/mlops-model/data"

metrics_table = "risk_score_metrics"

create_table_statement = f"""
drop table if exists {metrics_table};
create table {metrics_table}(
	index integer,
	psi float,
	bin VARCHAR
)
"""
num_features = [
            "AverageMInFile",
            "MSinceMostRecentInqexcl7days",
            "PercentTradesNeverDelq",
            "ExternalRiskEstimate",
            "NetFractionRevolvingBurden",
            "NumSatisfactoryTrades",
            "PercentInstallTrades"
      ]

def get_data():
    x_train = pd.read_parquet(f"{DATA_BASE_PATH}/X_train.parquet")
    y_train = pd.read_parquet(f"{DATA_BASE_PATH}/y_train.parquet")
    x_val = pd.read_parquet(f"{DATA_BASE_PATH}/X_val.parquet")
    y_val = pd.read_parquet(f"{DATA_BASE_PATH}/y_val.parquet")
    # train = x_train.assign(RiskPerformance=y_train.values)
    # val = x_val.assign(RiskPerformance=y_val.values)

    return x_train[num_features], x_val[num_features], y_train, y_val

    

POSTGRES_HOST = "localhost"
POSTGRES_PORT = 5432
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "password"
DB_CONNECTION = f"host={POSTGRES_HOST} port={POSTGRES_PORT} user={POSTGRES_USER} password={POSTGRES_PASSWORD}"


def prep_db(dbname="test"):
    with psycopg.connect(f"host={POSTGRES_HOST} port={POSTGRES_PORT} user={POSTGRES_USER} password={POSTGRES_PASSWORD}", autocommit=True) as conn:
        res = conn.execute(f"SELECT 1 FROM pg_database WHERE datname='{dbname}'")
        if len(res.fetchall()) == 0:
            conn.execute("create database test;")
        with psycopg.connect(f"host={POSTGRES_HOST} port={POSTGRES_PORT} dbname={dbname} user={POSTGRES_USER} password={POSTGRES_PASSWORD}") as conn:
            conn.execute(create_table_statement)


def _format_psi_table(psi_table):
    dict_data = (
        psi_table.iloc[:-1, :]
        .reset_index()
        .rename(columns=str.lower)
        [["index", "bin", "psi"]]
        .to_dict(orient="records")
        )
    return dict_data

# def _generate_psi_dom():
#     dom = """
#         index integer,
#         psi float,
#         bin VARCHAR
#         """
#     return dom

# def create_psi_monitor_table(table_name: str="credit_risk_metrics"):

#     create_table_statement = f"""
#     drop table if exists {table_name};
#     create table {table_name}(
#         {_generate_psi_dom()}
#     )
#     """

#     return create_table_statement

def _insert_psi_posgres(values: dict, cursor, table=None):
    cursor.execute(
		"insert into risk_score_metrics(index, psi, bin) values (%s, %s, %s)",
		(values["index"], values["psi"], values["bin"])
	)

def calculate_metrics_psi(model, X_actual, y_actual, X_expected, y_expected): 
    monitoring = ScorecardMonitoring(scorecard=model, psi_method="cart", psi_n_bins=10, verbose=True)
    monitoring.fit(X_actual=X_actual, y_actual=y_actual, X_expected=X_expected, y_expected=y_expected)
    result_table = monitoring.psi_table()
    psi_table = _format_psi_table(result_table)
    psi_feature_table = monitoring.psi_variable_table()
    
    return psi_table, psi_feature_table.rename(columns=str.lower).to_dict(orient="records")

# def insert_psi_records_to_postgres(psi_records, curr):
#     for record in psi_records:
#         _insert_psi_posgres(record, curr)

def monitoring_psi():
    dbname="test"
    prep_db()
    x_expected, x_actual, y_expected, y_actual = get_data()
    score_card_model = Scorecard.load("/home/fini/github-projects/mlops/05-monitoring/models/scorecard-model.pkl")
    score_psi, feature_psi = calculate_metrics_psi(score_card_model, x_actual, y_actual.values, x_expected, y_expected.values)
    with psycopg.connect(f"host={POSTGRES_HOST} port={POSTGRES_PORT} dbname={dbname} user={POSTGRES_USER} password={POSTGRES_PASSWORD}", autocommit=True) as conn:
        for record in score_psi:
            with conn.cursor() as curr:
                    _insert_psi_posgres(record, curr)
                    logging.info("data sent")
                    time.sleep(2)

if __name__ == '__main__':
	monitoring_psi()
    


