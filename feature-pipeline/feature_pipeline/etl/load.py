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
    nyc_taxi_feature_group = feature_store.get_or_create_feature_group(
        name="nyc_green_taxi",
        version=feature_group_version,
        description="New York Green taxi data for the time period in file.",
        primary_key=["index"],
        # event_time="datetime_utc",
        online_enabled=False,
        expectation_suite=validation_expectation_suite,
    )
    # Upload data.
    nyc_taxi_feature_group.insert(
        features=data,
        overwrite=False,
        write_options={
            "wait_for_job": True,
        },
    )

    # Add feature descriptions.
    feature_descriptions = [
        {
            "name": "pulocationid",
            "description": """
                            Describe the pick-up location of the passenger.
                            """,
            "validation_rules": "Always have a code",
        },
        {
            "name": "dolocationid",
            "description": """
                            Describe the drop-off location of the passenger
                            """,
            "validation_rules": "It is a valid code",
        },
        {
            "name": "duration",
            "description": """
                            The ride duration in minutes.
                            """,
            "validation_rules": ">1 (float) < 60",
        },
    ]
    
    for description in feature_descriptions:
        nyc_taxi_feature_group.update_feature_description(
            description["name"], description["description"]
        )

    # Update statistics.
    nyc_taxi_feature_group.statistics_config = {
        "enabled": True,
        "histograms": True,
        "correlations": True,
    }
    nyc_taxi_feature_group.update_statistics_config()
    nyc_taxi_feature_group.compute_statistics()

    return nyc_taxi_feature_group
