import os
import logging as logging

import pandas as pd
from optbinning import Scorecard

log = logging.getLogger(__name__)
# Makes sure the data is preprocess in way to conform to what
# the app expects
def load_model():
    print("Loading Model=================================")
    model_location = os.getenv("MODEL_LOCATION", "model")
    # model = Scorecard.load(f"{model_location}/model.pkl")
    model = Scorecard.load(f"{model_location}/model.pkl")
    return model


class ModelService:
    def __init__(self, model, model_version=None, callbacks=None):
        self.model = model
        self.model_version = model_version
        self.callbacks = callbacks or []

    def prepare_features(self, record):
        return pd.DataFrame([record])

    def predict(self, features):
        score = self.model.score(features)
        return int(score[0])

    def score_events(self, payload):
        # print("--------------*********************--------------------")
        # log.debug(payload)
        # print("-------------********************---------------------")

        predictions_events = []
        for record in payload["records"]:
            cust = record["cust"]
            cust_id = record["cust_id"]
            features = self.prepare_features(cust)
            prediction = self.predict(features)

            prediction_event = {
                "model": "risk_score_model",
                "version": self.model_version,
                "prediction": {"cust_score": prediction, "cust_id": cust_id},
            }
            for callback in self.callbacks:
                callback(prediction_event)

            predictions_events.append(prediction_event)
        # return {"predictions": predictions_events}

        return {"predictions": predictions_events}
