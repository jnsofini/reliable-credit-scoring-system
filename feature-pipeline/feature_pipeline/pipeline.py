import datetime
from typing import Optional
import fire
import pandas as pd

from prefect import flow, task

from feature_pipeline.etl import cleaning, load, extract, validation
from feature_pipeline import utils

logger = utils.get_logger(__name__)

DATA_PATH = "/home/fini/github-projects/mlops/capstone/data/raw_heloc_dataset_v3.parquet"
TARGET = "RiskPerformance"
MODELLING_COLUMNS = ['RiskPerformance', 'ExternalRiskEstimate', 'MSinceOldestTradeOpen',
       'MSinceMostRecentTradeOpen', 'AverageMInFile', 'NumSatisfactoryTrades',
       'NumTrades60Ever2DerogPubRec', 'NumTrades90Ever2DerogPubRec',
       'PercentTradesNeverDelq', 'MSinceMostRecentDelq',
       'MaxDelq2PublicRecLast12M', 'MaxDelqEver', 'NumTotalTrades',
       'NumTradesOpeninLast12M', 'PercentInstallTrades',
       'MSinceMostRecentInqexcl7days', 'NumInqLast6M', 'NumInqLast6Mexcl7days',
       'NetFractionRevolvingBurden', 'NetFractionInstallBurden',
       'NumRevolvingTradesWBalance', 'NumInstallTradesWBalance',
       'NumBank2NatlTradesWHighUtilization', 'PercentTradesWBalance',
       'operation_date', 'id']

FEATURE_GROUP_VERSION = 1

@flow
def run(
    source_path: str = DATA_PATH,
    feature_group_version: int = FEATURE_GROUP_VERSION,
) -> None:
    """
    Extract data from the API.

    Args:
        export_end_reference_datetime: The end reference datetime of the export window. If None, the current time is used.
            Because the data is always delayed with "days_delay" days, this date is used only as a reference point.
            The real extracted window will be computed as [export_end_reference_datetime - days_delay - days_export, export_end_reference_datetime - days_delay].
        days_delay: Data has a delay of N days. Thus, we have to shift our window with N days.
        days_export: The number of days to export.
        url: The URL of the API.
        feature_group_version: The version of the feature store feature group to save the data to.

    Returns:
          A dictionary containing metadata of the pipeline.
    """

    logger.info(f"Extracting data from API.")
    data = extract.get_data(path=source_path)
    # TODO: Add handling of empy data returned
    
    logger.info("Successfully extracted data from API.")
    # print(data_and_metadata)

    logger.info(f"Transforming data.")
    data = transform(data)
    logger.info("Successfully transformed data.")
    print(data.head())

    logger.info("Building validation expectation suite.")
    validation_expectation_suite = validation.build_expectation_suite()
    logger.info("Successfully built validation expectation suite.")

    logger.info(f"Validating data and loading it to the feature store.")
    load.to_feature_store(
        data,
        validation_expectation_suite=validation_expectation_suite,
        feature_group_version=feature_group_version,
    )
    # metadata["feature_group_version"] = feature_group_version
    logger.info("Successfully validated data and loaded it to the feature store.")

    # logger.info(f"Wrapping up the pipeline.")
    # # utils.save_json(metadata, file_name="feature_pipeline_metadata.json")
    # logger.info("Done!")

    # return metadata

@task
def transform(data: pd.DataFrame) -> pd.DataFrame:
    """
    Wrapper containing all the transformations from the ETL pipeline.
    """

    columns_types = cleaning.get_columns_types(data, exemption=["operation_date", "id", "RiskPerformance"])
    logger.info("Cleaning data: Casting columns")
    # print(columns_types)
    data = cleaning.cast_columns(df=data, columns_type=columns_types)
    data = cleaning.replace(df=data, replacement={TARGET: {"Bad":1, "Good": 0}})  
    logger.info("Cleaning data: Renaming columns")
    data = cleaning.rename_columns(data)
    print("--------------------", data.columns)  
    
    # data = cleaning.remove_outliers(
    #     data, 
    #     strategy={"duration": {"min": 1, "max": 60}}
    #         )

    return data


if __name__ == "__main__":
    fire.Fire(run)