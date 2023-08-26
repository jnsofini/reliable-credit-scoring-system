# Feature Pipeline

The work here is inspired by the inspiring work done Paul Iusztin. You can find his seven-lecture full stack ML blog course in [Towards Data Science](https://medium.com/towards-data-science/a-framework-for-building-a-production-ready-feature-engineering-pipeline-f0b29609b20f).

## Introduction

I this part of the project we demonstrate the process of pulling data from various sources, prepropocessing it and then storing it in a feature store. The pre processing includes treating for outliers, missing, special codes. As a results, an exploratory analysis should be done to determine the strategy for treatment and then incorporate into this pipeline.

To run the code we need to set the python environment as [explained below](#Development-environment-setup).


## Development environment setup

The files to set this environment are `pyproject.toml` and `poetry.lock`. Navigate to the `feature-pipeline` directory and then setup the virtual environment via:

```shell
cd feature-pipeline
poetry shell
poetry install
```

Check the [Set Up Additional Tools](https://github.com/iusztinpaul/energy-forecasting#-set-up-additional-tools-) and [Usage](https://github.com/iusztinpaul/energy-forecasting#usage) sections to see **how to set up** the **additional tools** and **credentials** you need to run this project.

## Data

The data used in this project is the FICO explainable machine learning data. A detailed description of the data can be found in the FICO XAI Challenge page. We also provided some more details in the problem statement see?
Down load the data and store in the data folder. The feature store loaders expect the data directory to be set.

Check out this [Medium article](https://medium.com/towards-data-science/a-framework-for-building-a-production-ready-feature-engineering-pipeline-f0b29609b20f) for more details about this module.


## Usage for Development

To start the ETL pipeline navigate to the `feature-pipeline` and run:
```shell
python -m feature_pipeline.pipeline
```

Open Hopswork and navigate to the project to confirm that the data is pushed. Different approaches can be used to create a test train split. We could use the indices and get a test-train split and then store the indices as another table in the store which can be joined to the original data. Alternatively we could used the indices to create a view of the trainin and test data. 

To create a new feature view, put the necessary table name and run:

```shell
python -m feature_pipeline.feature_view
```

In the case of this project we avoided regular API calls to the feature store by simply storing the test and train data locally. This doesn't jeopardize the MLOPS best practices as we add them at the end to the feature store for feature usage.

**NOTE:** Be careful to set the `ML_PIPELINE_ROOT_DIR` variable .


## Issues Encountered

Initially, I tried to activate the environment created under the original repo and then navigate to use this code. There was a problem because that code installed additional folders including `feature_pipeline` (See `pyproject.toml` file). Solution was to create an environment specifically for this repository.

## Features

We didn't consult the data dictionary and just inferred the names using chatGPT. Here are the columns ans their descriptions

Based on the given list of column names, here are the descriptions inferred for each feature:

| Feature Name                       | Description                                                |
|------------------------------------|------------------------------------------------------------|
| RiskPerformance                    | Risk performance indicator                                 |
| ExternalRiskEstimate               | Estimated external risk level                              |
| MSinceOldestTradeOpen              | Months since the oldest trade account was opened           |
| MSinceMostRecentTradeOpen          | Months since the most recent trade account was opened       |
| AverageMInFile                     | Average months reported since the file was created         |
| NumSatisfactoryTrades              | Number of satisfactory trades                              |
| NumTrades60Ever2DerogPubRec        | Number of trades with 60+ days past due or derogatory public records ever                      |
| NumTrades90Ever2DerogPubRec        | Number of trades with 90+ days past due or derogatory public records ever                      |
| PercentTradesNeverDelq             | Percentage of trades never delinquent                      |
| MSinceMostRecentDelq               | Months since the most recent delinquency                    |
| MaxDelq2PublicRecLast12M           | Maximum delinquency reported in the last 12 months         |
| MaxDelqEver                        | Maximum delinquency ever reported                           |
| NumTotalTrades                     | Total number of trades                                      |
| NumTradesOpeninLast12M             | Number of trades opened in the last 12 months              |
| PercentInstallTrades               | Percentage of installment trades                           |
| MSinceMostRecentInqexcl7days       | Months since the most recent inquiry excluding the last 7 days |
| NumInqLast6M                       | Number of inquiries in the last 6 months                   |
| NumInqLast6Mexcl7days              | Number of inquiries in the last 6 months excluding the last 7 days |
| NetFractionRevolvingBurden         | Net fraction revolving burden                              |
| NetFractionInstallBurden           | Net fraction installment burden                            |
| NumRevolvingTradesWBalance         | Number of revolving trades with balance                     |
| NumInstallTradesWBalance           | Number of installment trades with balance                  |
| NumBank2NatlTradesWHighUtilization | Number of bank/national trades with high utilization       |
| PercentTradesWBalance              | Percentage of trades with balance                          |

Here is the JSON format with feature names as keys and descriptions as values:

## Data Prep and Loading

The data is prepared and loaded to a feature store. The store is set as explained below. The code is designed to follow process flows that are familiar, namely, ETL. 

1. Extract the data with _extract.py_. This extracts the data from a dump.
2. Transform the data with _cleaning.py_ by
    - Renaming columns
    - Casting to proper types
3. Great Expectations was used to validate the data with _validate.py_ by checking
    - Data types
    - Expected number of columns
    - Limits or set of values
4. Load the data to Hopswork Feature Store with _load.py_.

The script os orchestrated with `prefect`.

The other part is to create feature views. This are just like views in database, or losely equivilently, filters when you filter data in pandas it simply create a view on the data.

Because of limitation in the number of views, views can be cleaned to reduce the number and also keep the views to those that are used.

## Feature Store

We use [HopsWork](https://c.app.hopsworks.ai/p/45287/fs/45140/fg) for feature store. The login is via Google outh so no account was created. A free account is used with only one project permitted. It is named as _energyconsuption_ because that was the original project where I started. Every dataset is stored under that project. The data for  this project isn called _credit_score_.

### Setting up HopsWork

A HopsWork account is needed. The configuration file was used to send data to HopsWork. Add this as _.env_ file in the root of the `feature-pipeline` project directory with the following data, replacing the values with the appropriate values.

```txt
FS_API_KEY = "YOUR-HOPSWORK-API-KEY"
FS_PROJECT_NAME = "YOUR-PROJECT-NAME"
```


Please note that the inferred descriptions are based solely on the column names and may not accurately represent the actual data or its context.