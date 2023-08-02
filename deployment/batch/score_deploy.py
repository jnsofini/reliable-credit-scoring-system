"""Deployment setup for batch deploy.

Here we use the batch scoring script in score.py to deploy in prefect server.
The job is set to run every 1st of the month.
"""
from prefect.deployments import Deployment
from prefect.server.schemas.schedules import CronSchedule
from score import credit_score_prediction

deployment = Deployment.build_from_flow(
    flow=credit_score_prediction,
    name="credit-score-prediction",
    version=1,
    parameters={"model_id": "dev"},
    schedule=(CronSchedule(cron="0 3 1 * *", timezone="America/Chicago")),
    work_queue_name="ml",
)

deployment.apply()
