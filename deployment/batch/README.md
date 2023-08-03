# Batch deployment

Notes from RCSS deployment.

## Batch Scoring

Here we use prefect cloud. The first step is to run `prefect login` and hit enter when it asked for API key. This allows you to authenticate via the browser, if have no API key like in our case.

### Score new data

To run, start from the root directory and  activate environment. Here I use `pipenv shell` and then run the scripte via

```python
cd deployment
python batch/score.py
```

We have set a deployment script so that this can be triggered from the Prefect server. Ths job is set to run every 1st day of the month at 3 am. The deployment is achieved via the deployment script through

```python
python batch/score_deploy.py
```

After confirming the deployment in the Prefect UI, a worker pool can be started in a separate terminal with

```sh
prefect agent start --pool default-agent-pool --work-queue ml #cloud prefect
prefect worker start --pool 'ml' #Local Prefect
```

The work can triggered from the Prefect UI or from the terminal. On the UI go to deployment and run the work. It will run in our local server. To run via the terminal, get the name of the deployment from Prefect server and run via

```sh
prefect deployment run 'credit-score-prediction/batch-deployment'
```

### Backfill score

After developing the model, we retrouspectively apply it to data stored in our system. In this case, we use the script called backfill. Backfill can be deployed via deployment script as we did for the scoring of fresh data, however, we want to use the CLI and achieve with the following steps:

```sh
prefect deploy score_backfill.py : credit_score_prediction_backfill --name backfill-batch-deployment --description "Bach deployment for credit score model" --pool ml
```

We get a similar output as before. Check the deployment in Prefect UI and do a quick run. This time it will not ask for parameters as it can run with the default params.

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

## Deployment via Prefect Deployment

Consider the case of a local prefect server. By first starting a server locally via `prefect server start` and then running `python score.py dev` we see that the work progresses without an error. We want try to see if we can build a deployment in a subdirectory. At the end it didn't work when it is pulling code from GitHub so I changed it to pull code from local. This is because I am able to add the subdir which is something I am still struggling to figure out when pulling code from GitHub. When you run the next step, don't forget to replace

```yaml
prefect.projects.steps.git_clone_project:
     repository: github/path/to/project.git
```

with

```yaml
- prefect.projects.steps.set_working_directory:
    directory: /home/fini/github-projects/reliable-credit-scoring-system/deployment/batch
```

. We run `prefect project init` in the _batch_ folder. Let's see how to register the success run via CLI command. Run by deploying by configuring it and noting the format `scriptname:flow`.

```sh
prefect deploy score.py:ride_duration_prediction --name batch-deployment --description "Bach deployment for prediction model" --pool ml
```

The following is my output

```txt
╭────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Deployment 'credit-score-prediction/batch-deployment' successfully created with id '6810d942-fbf2-4a71-85f0-2eccd623b87e'.                │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
View Deployment in UI: http://127.0.0.1:4200/deployments/deployment/6810d942-fbf2-4a71-85f0-2eccd623b87e

To execute flow runs from this deployment, start a worker in a separate terminal that pulls work from the 'ml' work pool:

        $ prefect worker start --pool 'ml'

To schedule a run for this deployment, use the following command:

        $ prefect deployment run 'ride-duration-prediction/batch-deployment'
```

Start the worker as specified above in command `prefect worker start --pool 'ml'` so that it can wait for processes to that are schedulled or those that are run adhoc. Let's do this from the UI. Open the prefect server in the browser, go to deployments and select `batch-deployment/credit-score-prediction`.

Click on the run button located at the top right. A parge will open asking for params. Populated the parameters with the same data as was done in the CLI run. Watch what happens in the termininal where you ran the worker.
