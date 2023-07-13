from datetime import datetime
from typing import Optional

import fire
import hopsworks

from feature_pipeline import utils
from feature_pipeline import settings
import hsfs


logger = utils.get_logger(__name__)

FEATURE_GROUP = "credit_score"
data_views = "credit_score_view"

def create(
    feature_group_version: Optional[int] = None,
    start_datetime: Optional[datetime] = None,
    end_datetime: Optional[datetime] = None,
) -> dict:
    """Create a new feature view version and training dataset
    based on the given feature group version and start and end datetimes.

    Args:
        feature_group_version (Optional[int]): The version of the
            feature group. If None is provided, it will try to load it
            from the cached feature_pipeline_metadata.json file.
        start_datetime (Optional[datetime]): The start
            datetime of the training dataset that will be created.
            If None is provided, it will try to load it
            from the cached feature_pipeline_metadata.json file.
        end_datetime (Optional[datetime]): The end
            datetime of the training dataset that will be created.
              If None is provided, it will try to load it
            from the cached feature_pipeline_metadata.json file.

    Returns:
        dict: The feature group version.

    """

    
    project = hopsworks.login(
        api_key_value=settings.SETTINGS["FS_API_KEY"], project=settings.SETTINGS["FS_PROJECT_NAME"]
    )
    fs = project.get_feature_store()

    # Delete old feature views as the free tier only allows 100 feature views.
    # NOTE: Normally you would not want to delete feature views. We do it here just to stay in the free tier.
    _remove_unused_views(fs)

    # Create feature view in the given feature group version.
    store_fg = fs.get_feature_group(
        FEATURE_GROUP, version=feature_group_version
    )
    ds_query = store_fg.select_all()

    # ## Added this but not tested
    # train_test_period = ds_query.filter(ds_query.operation_date != "2023-08-01")
    # oot_query = ds_query.filter(ds_query.operation_date == "2023-08-01")
    # oot_feature_view = fs.create_feature_view(
    #     name=f"{FEATURE_GROUP}_oot_view",
    #     description="Out of time data to use for model validation",
    #     labels=[TARGET],
    #     query=oot_query,
    #     labels=[],
    # )
    # # Train test split
    # train_test_feature_view = fs.create_feature_view(
    #     name=f"{FEATURE_GROUP}_train_test_view",
    #     description="Data for the period to be used for model train and test",
    #     labels=[TARGET],
    #     query=train_test_period,
    #     labels=[],
    # )
    #     # create a training dataset 
    # X_train, y_train, X_test, y_test = train_test_feature_view.train_test_split(test_size=0.2, strategy=)

    # # materialise a training dataset
    # version, job = feature_view.create_train_test_split(
    #     test_size = 0.2,
    #     description = 'transactions_dataset_jan_feb',
    #     data_format = 'csv'
    # )


    feature_view = fs.create_feature_view(
        name=f"{FEATURE_GROUP}_view",
        description="Credit score data for risk scoring model.",
        query=ds_query,
        labels=[],
    )

    # Create training dataset.
    logger.info(
        f"Creating training dataset between {start_datetime} and {end_datetime}."
    )
    feature_view.create_training_data(
        description="Risk Scoring training dataset",
        data_format="csv",
        start_time=start_datetime,
        end_time=end_datetime,
        write_options={"wait_for_job": True},
        coalesce=False,
    )

    # Save metadata.
    metadata = {
        "feature_view_version": feature_view.version,
        "training_dataset_version": 1,
    }
    utils.save_json(
        metadata,
        file_name="feature_view_metadata.json",
    )

    return metadata

def _remove_unused_views(fs):
    try:
        feature_views = fs.get_feature_views(name=data_views)
    except hsfs.client.exceptions.RestAPIError:
        logger.info(f"No feature views found for {data_views}.")

        feature_views = []

    for feature_view in feature_views:
        try:
            feature_view.delete_all_training_datasets()
        except hsfs.client.exceptions.RestAPIError:
            logger.error(
                f"Failed to delete training datasets for feature view {feature_view.name} with version {feature_view.version}."
            )

        try:
            feature_view.delete()
        except hsfs.client.exceptions.RestAPIError:
            logger.error(
                f"Failed to delete feature view {feature_view.name} with version {feature_view.version}."
            )



if __name__ == "__main__":
    fire.Fire(create)
