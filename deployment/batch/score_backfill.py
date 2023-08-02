"""Deployment setup for batch deploy.

Runs the batch prediction to fill the data in the database.
"""

from datetime import datetime
from dateutil.relativedelta import relativedelta

from prefect import flow

import score


@flow
def credit_score_prediction_backfill():
    """Runs the scoring script to back fill."""
    start_date = datetime(year=2021, month=3, day=1)
    end_date = datetime(year=2022, month=4, day=1)

    _date = start_date

    while _date <= end_date:
        score.credit_score_prediction(data_id='2023-aug', run_id='dev')

        _date = _date + relativedelta(months=1)


if __name__ == '__main__':
    credit_score_prediction_backfill()
