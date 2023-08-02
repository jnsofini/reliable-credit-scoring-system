# Batch deployment

Notes from RCSS deployment.

## Batch Scoring

Here we use prefect cloud. The first step is to run `prefect login` and hit enter when it asked for API key. This allows you to authenticate via the browser, if have no API key like in our case.

To run, start from the root directory and  activate environment. Here I use `pipenv shell` and then run the scripte via

```python
cd deployment
python batch/score.py
```

We have set a deployment script so that this can be triggered from the Prefect server. Ths job is set to run every 1st day of the month at 3 am. The deployment is achieved via the deployment script through

```python
python batch/score_deploy.py
```

## Code Quality

Code quality is ensured via `black, isort & pylint`. These are bundled into the make file alongside other commands which can be executed as follows

```shell
make quality_checks  # quality checks
make batch-deploy    # quality checks
```

There are other commands bundled in the make file, summerized as follows
``
