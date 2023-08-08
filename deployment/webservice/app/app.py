"""FastAPI webservice to run scores."""

from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from model import ModelService, load_model
from pydantic import BaseModel # pylint: disable=no-name-in-module

model = load_model()
model_service = ModelService(model=model, model_version="V1")

app = FastAPI()


# pydantic models


class CustomerInfo(BaseModel):
    ExternalRiskEstimate: int
    AverageMInFile: int
    NumSatisfactoryTrades: int
    PercentTradesNeverDelq: int
    PercentInstallTrades: int
    MSinceMostRecentInqexcl7days: int
    NetFractionRevolvingBurden: int


class Customer(BaseModel):
    cust: CustomerInfo
    cust_id: int


class Records(BaseModel):
    records: list[Customer]


class Prediction(BaseModel):
    cust_score: int
    cust_id: int


class PredictionInfo(BaseModel):
    model: str
    version: str
    prediction: Prediction


class PredictionRecords(BaseModel):
    predictions: list[PredictionInfo]


# routes


@app.get("/ping")
async def pong():
    return {"ping": "pong!"}


@app.post("/predict", status_code=200)  # response_model=Predictions,
def get_prediction(payload: Records):
    # print("----===================================--------------")
    # record = jsonable_encoder(payload)
    # print(record)
    # # print(payload)
    # print("--==================================--------------------")

    predictions = model_service.score_events(payload=jsonable_encoder(payload))

    if not predictions:
        raise HTTPException(status_code=400, detail="Model not found.")

    return predictions
