"""
Compute and log monitoring metrics.
"""
# pylint: disable=logging-fstring-interpolation
# import datetime
import logging
import os
import time
from pathlib import Path

import pandas as pd
from optbinning import Scorecard
from optbinning.scorecard import ScorecardMonitoring
# from prefect import flow, task
from src.db import insert_dataframe, prepare_database # pylint: disable=import-error
from src.metrics import formatted_metrics # pylint: disable=import-error

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s"
)

SEND_TIMEOUT = 10

BASE_PATH = Path(__file__).parent
PROJECT_ROOT = BASE_PATH.parent

DATA_BASE_PATH = BASE_PATH.parent / "data"

METRICS_TABLE = "risk_score_metrics"

create_table_statement = f"""
drop table if exists {METRICS_TABLE};
create table {METRICS_TABLE}(
	index integer,
	psi float,
	bin VARCHAR
)
"""


def get_data():
    """Loads train and test data."""
    x_train = pd.read_parquet(f"{DATA_BASE_PATH}/X_train.parquet")
    y_train = pd.read_parquet(f"{DATA_BASE_PATH}/y_train.parquet").values.reshape(-1)
    x_val = pd.read_parquet(f"{DATA_BASE_PATH}/X_val.parquet")
    y_val = pd.read_parquet(f"{DATA_BASE_PATH}/y_val.parquet").values.reshape(-1)
    # train = x_train.assign(RiskPerformance=y_train.values)
    # val = x_val.assign(RiskPerformance=y_val.values)

    return x_train, x_val, y_train, y_val


POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_USER = os.getenv("POSTGRES_USER", "monitoring")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "monitoring")
DATA_BASE = os.getenv("DATA_BASE", "monitoring")

sync_engine = (
    f"postgresql+psycopg://{POSTGRES_USER}"
    f":{POSTGRES_PASSWORD}@{POSTGRES_HOST}"
    f":{POSTGRES_PORT}/{DATA_BASE}"
    )
postgres_conn = (
    f"host={POSTGRES_HOST} port={POSTGRES_PORT} "
    f"user={POSTGRES_USER} password={POSTGRES_PASSWORD}"
    )

# def prepare_database(postgres_conn_str:str | None = None, dbname="test"):
#     postgres_conn_str = postgres_conn_str or (
# f"host={POSTGRES_HOST} port={POSTGRES_PORT} "
# f"user={POSTGRES_USER} password={POSTGRES_PASSWORD}"
# )

#     """Create database if it doesn't exist."""
#     with psycopg.connect(postgres_conn_str, autocommit=True) as conn:
#         res = conn.execute(f"SELECT 1 FROM pg_database WHERE datname='{dbname}'")
#         if len(res.fetchall()) == 0:
#             conn.execute(f"create database {dbname};")
#         with psycopg.connect(f"{postgres_conn_str} dbname={dbname}") as conn:
#             conn.execute(create_table_statement)


def calculate_metrics_psi(model, x_actual, y_actual, x_expected, y_expected):
    """Calculates PSI metris using optbinning"""
    monitoring = ScorecardMonitoring(
        scorecard=model, psi_method="cart", psi_n_bins=10, show_digits=3, verbose=True
    )
    monitoring.fit(
        X_actual=x_actual,
        y_actual=y_actual,
        X_expected=x_expected,
        y_expected=y_expected,
    )
    psi_table = monitoring.psi_table()
    # psi_table = _format_psi_table(psi_table)
    psi_feature_table = monitoring.psi_variable_table()

    return format_data(psi_table), format_data(
        psi_feature_table
    )  # .rename(columns=str.lower) #.to_dict(orient="records")


def get_model_location():
    """Gets the location of the model"""
    return os.getenv("MODEL_LOCATION", DATA_BASE_PATH / "model/model.pkl")


def monitoring_psi(db_conn_string: str):
    """Computing metrics, writing to database."""
    # dbname="test-prepare"
    dbname, _ = prepare_database(
        dbname=DATA_BASE, conn_string=db_conn_string
    )

    x_expected, x_actual, y_expected, y_actual = get_data()
    model_location = get_model_location()
    score_card_model = Scorecard.load(str(model_location))
    reference_metrics_data = get_stats(
        model=score_card_model, x_data=x_expected, y_data=y_expected
    )

    insert_dataframe(
        table_name="reference_model_stats",
        table_data=reference_metrics_data,
        sync_engine=sync_engine,
    )

    metrics_data = get_stats(model=score_card_model, x_data=x_actual, y_data=y_actual)
    insert_dataframe(
        table_name="model_stats",
        table_data=metrics_data,
        sync_engine=sync_engine,
    )
    score_psi, feature_psi = calculate_metrics_psi(
        model=score_card_model,
        x_actual=x_actual,
        y_actual=y_actual,
        x_expected=x_expected,
        y_expected=y_expected,
    )

    logging.info("writing to database: {dbname}")

    insert_dataframe(
        table_name="score_psi",
        table_data=format_data(score_psi),
        sync_engine=sync_engine,
    )
    insert_dataframe(
        table_name="feature_psi",
        table_data=format_data(feature_psi),
        sync_engine=sync_engine,
    )

    logging.info(f"Data sent to database: {dbname}")
    time.sleep(2)

    # return None


def validate_data_to_write(left_frame, right_frame):
    """Dataframe results validation."""
    if left_frame is None:
        if right_frame is None:
            return 'both'
        return "left"
    if right_frame is None:
        return 'right'
    return None


def format_data(data: pd.DataFrame, columns=None, sig_fig=3, order_by="PSI"):
    """Formating script for PSI metrics."""
    logging.info(data)
    if columns is None:
        columns = {
            col: float
            for col in data.columns
            if (col.endswith("%") or col.endswith("PSI"))
        }

    return data.astype(columns).round(sig_fig).sort_values(by=[order_by])


def get_stats(model, x_data, y_data):
    """Gets metrics that are formatted."""
    y_pred = model.predict_proba(x_data)[:, 1]
    data = formatted_metrics(y_data, y_pred)
    return pd.DataFrame(
        {"Metrics": list(data.keys()), "Values": list(data.values())}
    ).sort_values(by=["Values"])


if __name__ == '__main__':
    monitoring_psi(db_conn_string=postgres_conn)
