import json

import hopsworks
import pandas as pd
from great_expectations.core import ExpectationSuite
from hsfs.feature_group import FeatureGroup

from feature_pipeline.settings import SETTINGS


def to_feature_store(
    data: pd.DataFrame,
    validation_expectation_suite: ExpectationSuite,
    feature_group_version: int,
) -> FeatureGroup:
    """
    This function takes in a pandas DataFrame and a validation expectation suite,
    performs validation on the data using the suite, and then saves the data to a
    feature store in the feature store.
    """

    # Connect to feature store.
    project = hopsworks.login(
        api_key_value=SETTINGS["FS_API_KEY"], 
        project=SETTINGS["FS_PROJECT_NAME"]
    )
    feature_store = project.get_feature_store()

    # Create feature group.
    store_feature_group = feature_store.get_or_create_feature_group(
        name="credit_score",
        version=feature_group_version,
        description="Explainable Machine Learning Challenge credit risk data.",
        primary_key=["id"],
        # event_time="datetime_utc",
        online_enabled=False,
        expectation_suite=validation_expectation_suite,
    )
    # Upload data.
    store_feature_group.insert(
        features=data,
        overwrite=False,
        write_options={
            "wait_for_job": True,
        },
    )

    # Add feature descriptions.
    with open("metadata.json", "r") as f:
        meta_data = json.load(f)
        feature_descriptions = meta_data["feature_descriptions"]
    # feature_descriptions = [
    #     {
    #         "name": "riskperformance",
    #         "description": """
    #                         Describe the risk indicator of the customer. 
    #                         1 if they ran into financial difficulty and 0 otherwise.
    #                         """,
    #         "validation_rules": "Always have a code",
    #     },
    #     {
    #         "name": "numtrades60ever2derogpubrec",
    #         "description": """
    #                         Describes the number of trades that are 60 and older
    #                         """,
    #         "validation_rules": ">0 int",
    #     },
    #     {
    #         "name": "numtrades90ever2derogpubrec",
    #         "description": """
    #                         Describes the number of trades that are 60 and older
    #                         """,
    #         "validation_rules": ">0 (int)",
    #     },
    # ]
    
    for description in feature_descriptions:
        store_feature_group.update_feature_description(
            description["name"].lower(), description["description"]
        )

    # Update statistics.
    store_feature_group.statistics_config = {
        "enabled": True,
        "histograms": True,
        "correlations": True,
    }
    store_feature_group.update_statistics_config()
    store_feature_group.compute_statistics()

    return store_feature_group
