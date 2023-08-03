Activate the environment in capstone from the capstone root

```sh
capstone$ pipenv shell & credit-risk-model/

```

## Logging model

With MLflow, we can log a model locally as well as in the server. For local saving we can use the usual `scorecard.save` and then load it with `Scorecard.load` or use `pickle.load` in a `with open(..., 'rb')` context as follows

```py
with open('path-to-model.pkl) as f:
    model = pickle.load(f)
```

Another great option to save locally is via `mlflow` with

```py
scorecard.fit(x, y)
mlflow.sklearn.save_model(
    path="model", 
    sk_model=scorecard,
    serialization_format="pickle",
    )
```

 with the model saved in directory `model`. The directory contains other files including

- conda.yaml
- MLmodel
- model.pkl
- python_env
- requirements.txt

This file can also be loaded with either `Scorecard.load` or use `picle.load`.

Remote server storage is the one we are very intesrested in. For example, storing model artifacts in an S3 bucket. This is where we want to use `mlflow.sklearn.log_model` method. The following segment helps us achieve this.

```py
scorecard.fit(x, y)
mlflow.sklearn.log_model(
    artifact_path="model", 
    sk_model=scorecard,
    serialization_format="pickle"
    )
```

The path the model will be identified with mlflow with the usual `f's3://{model_bucket}/{experiment_id}/{run_id}/artifacts/model'` which follow how mlflow stores model. Here is an examle `/mlruns/1/eadf66f1dc894e4dad2f0d74835056bd/artifacts/model/model.pkl`. The associated files mentioned above are also stored in the same path. This model can be loaded and used as follows

```py
with open("mlruns/1/eadf66f1dc894e4dad2f0d74835056bd/artifacts/model/model.pkl", "rb") as f:
    model = pickle.load(f)

model.score(val_data)
```

## Tests

Test provided. You need to open the project such that the test is in the root dir and then click on the pytest icon to set test. Run with `pytest` or `pytest --durations=5` to see the top five slowest tests completed.
