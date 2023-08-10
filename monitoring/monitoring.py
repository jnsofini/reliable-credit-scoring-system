import datetime
import time
import logging 
import pandas as pd
import storage
import psycopg
from pathlib import Path

from prefect import task, flow
import os

from optbinning import Scorecard
from optbinning.scorecard import ScorecardMonitoring

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")

SEND_TIMEOUT = 10

BASE_PATH = Path(__file__).parent
PROJECT_ROOT = BASE_PATH.parent

DATA_BASE_PATH = BASE_PATH.parent/"data"

metrics_table = "risk_score_metrics"

create_table_statement = f"""
drop table if exists {metrics_table};
create table {metrics_table}(
	index integer,
	psi float,
	bin VARCHAR
)
"""

def get_data():
    x_train = pd.read_parquet(f"{DATA_BASE_PATH}/X_train.parquet")
    y_train = pd.read_parquet(f"{DATA_BASE_PATH}/y_train.parquet")
    x_val = pd.read_parquet(f"{DATA_BASE_PATH}/X_val.parquet")
    y_val = pd.read_parquet(f"{DATA_BASE_PATH}/y_val.parquet")
    # train = x_train.assign(RiskPerformance=y_train.values)
    # val = x_val.assign(RiskPerformance=y_val.values)

    return x_train, x_val, y_train, y_val

    

POSTGRES_HOST = "localhost"
POSTGRES_PORT = 5432
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "password"
DATA_BASE="test_prepare"

sync_engine = f"""postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{DATA_BASE}"""

def prepare_database(postgres_conn_str:str | None = None, dbname="test"):
    postgres_conn_str = postgres_conn_str or f"""host={POSTGRES_HOST} port={POSTGRES_PORT} user={POSTGRES_USER} password={POSTGRES_PASSWORD}"""

    """Create database if it doesn't exist."""
    with psycopg.connect(postgres_conn_str, autocommit=True) as conn:
        res = conn.execute(f"SELECT 1 FROM pg_database WHERE datname='{dbname}'")
        if len(res.fetchall()) == 0:
            conn.execute(f"create database {dbname};")
        with psycopg.connect(f"{postgres_conn_str} dbname={dbname}") as conn:
            conn.execute(create_table_statement)


def calculate_metrics_psi(model, x_actual, y_actual, x_expected, y_expected): 
    monitoring = ScorecardMonitoring(scorecard=model, psi_method="cart", psi_n_bins=10, verbose=True)
    monitoring.fit(X_actual=x_actual, y_actual=y_actual, X_expected=x_expected, y_expected=y_expected)
    psi_table = monitoring.psi_table()
    # psi_table = _format_psi_table(psi_table)
    psi_feature_table = monitoring.psi_variable_table()
    
    return psi_table, psi_feature_table.rename(columns=str.lower) #.to_dict(orient="records")

def get_model_location():
     """Gets the location of the model"""
     return os.getenv("MODEL_LOCATION", DATA_BASE_PATH / "model/model.pkl")

def monitoring_psi():
    # dbname="test-prepare"
    prepare_database(dbname=DATA_BASE)
    x_expected, x_actual, y_expected, y_actual = get_data()
    model_location = get_model_location()
    score_card_model = Scorecard.load(model_location)
    score_psi, feature_psi = calculate_metrics_psi(
         model=score_card_model, 
         x_actual=x_actual, 
         y_actual=y_actual.values, 
         x_expected=x_expected, 
         y_expected=y_expected.values
         )
    storage.insert_dataframe(
        table_name="score_psi", 
        table_data=score_psi, 
        conn_str=sync_engine,
        )
    storage.insert_dataframe(
        table_name="feature_psi", 
        table_data=feature_psi, 
        conn_str=sync_engine,
        )
    logging.info("data sent")
    time.sleep(2)

if __name__ == '__main__':
	monitoring_psi()
    


