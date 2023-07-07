# Feature Pipeline

The work here is inspired by the inspiring work done Paul Iusztin. You can find his seven-lecture full stack ML blog course in [Towards Data Science](https://medium.com/towards-data-science/a-framework-for-building-a-production-ready-feature-engineering-pipeline-f0b29609b20f).
Here we pull the data, process it and sent it to Hopswork feature store. This is achieved by first setting an account and get an feature store api key. The environment is set and scripts ran.

Now it works.


## Install for Development

Note that the activation is done in the original repository of energy consuption and then we navigate to mlops dir.
Create virtual environment:

```shell
cd feature-pipeline
poetry shell
poetry install
```

Check the [Set Up Additional Tools](https://github.com/iusztinpaul/energy-forecasting#-set-up-additional-tools-) and [Usage](https://github.com/iusztinpaul/energy-forecasting#usage) sections to see **how to set up** the **additional tools** and **credentials** you need to run this project.

Check out this [Medium article](https://medium.com/towards-data-science/a-framework-for-building-a-production-ready-feature-engineering-pipeline-f0b29609b20f) for more details about this module.


## Usage for Development

To start the ETL pipeline navigate to the `feature-pipeline` and run:
```shell
python -m feature_pipeline.pipeline
```

To create a new feature view run:
```shell
python -m feature_pipeline.feature_view
```

**NOTE:** Be careful to set the `ML_PIPELINE_ROOT_DIR` variable as explained in this [section](https://github.com/iusztinpaul/energy-forecasting#set-up-the-ml_pipeline_root_dir-variable).


## Issues Encountered

Initially, I tried to activate the environment created under the original repo and then navigate to use this code. There was a problem because that code installed other a folder `feature_pipeline`. As a result the env was reading the path properly. Alternatives is to setup another environment or change the root.

## Features

We didn't consult the data dictionary and just inferred the names using chatGPT. Here are the columns ans their descriotions

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

```json
{
  "RiskPerformance": "Risk performance indicator",
  "ExternalRiskEstimate": "Estimated external risk level",
  "MSinceOldestTradeOpen": "Months since the oldest trade account was opened",
  "MSinceMostRecentTradeOpen": "Months since the most recent trade account was opened",
  "AverageMInFile": "Average months reported since the file was created",
  "NumSatisfactoryTrades": "Number of satisfactory trades",
  "NumTrades60Ever2DerogPubRec": "Number of trades with 60+ days past due or derogatory public records ever",
  "NumTrades90Ever2DerogPubRec": "Number of trades with 90+ days past due or derogatory public records ever",
  "PercentTradesNeverDelq": "Percentage of trades never delinquent",
  "MSinceMostRecentDelq": "Months since the most recent delinquency",
  "MaxDelq2PublicRecLast12M": "Maximum delinquency reported in the last 12 months",
  "MaxDelqEver": "Maximum delinquency ever reported",
  "NumTotalTrades": "Total number of trades",
  "NumTradesOpeninLast12M": "Number of trades opened in the last 12 months",
  "PercentInstallTrades": "Percentage of installment trades",
  "MSinceMostRecentInqexcl7days": "Months since the most recent inquiry excluding the last 7 days",
  "NumInqLast6M": "Number of inquiries in the last 6 months",
  "NumInqLast6Mexcl7days": "Number of inquiries in the last 6 months excluding the last 7 days",
  "NetFractionRevolvingBurden": "Net fraction revolving burden",
  "NetFractionInstallBurden": "Net fraction installment burden",
  "NumRevolvingTradesWBalance": "Number of revolving trades with balance",
  "NumInstallTradesWBalance": "Number of installment trades with balance",
  "NumBank2NatlTradesWHighUtilization": "Number of bank/national trades with high utilization",
  "PercentTradesWBalance": "Percentage of trades with balance"
}
```

Please note that the inferred descriptions are based solely on the column names and may not accurately represent the actual data or its context.