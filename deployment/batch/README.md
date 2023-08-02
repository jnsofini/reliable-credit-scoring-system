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

## Prefect Server


The deployment are set in Prefect server with a workpool _ml_. We need to start the work pool locally via.
Check and/set profile with the following

```sh
prefect profile ls # List the profiles
prefect profile use dev # Select dev profile
prefect agent start --pool default-agent-pool --work-queue ml # Start workpool
```

With that set, you can trigger the job from the server UI or from the terminal. Here I just used the UI.

Next is to try and is to set some automation where I created an even to sent an email when task completes. There are multiple options to take from including flow entering _pending, failed_ etc.