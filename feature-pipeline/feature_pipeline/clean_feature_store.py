import fire
import hopsworks

from feature_pipeline import settings

groups_to_delete = "deveopment-data"
views_to_delete = "credit_score_view"

def clean():
    """
    Utiliy function used during development to clean all the data from the feature store.
    """

    project = hopsworks.login(
        api_key_value=settings.SETTINGS["FS_API_KEY"], project=settings.SETTINGS["FS_PROJECT_NAME"]
    )
    fs = project.get_feature_store()

    print("Deleting feature views and training datasets...")
    try:
        feature_views = fs.get_feature_views(name=views_to_delete)
        print("Deleting the views: ", feature_views)

        for feature_view in feature_views:
            try:
                feature_view.delete()
            except Exception as e:
                print(e)
    except Exception as e:
        print("---------------------")
        print(e)

    print("Deleting feature groups...")
    try:
        feature_groups = fs.get_feature_groups(name=groups_to_delete)
        print("Deleting the groups: ", feature_groups)
        for feature_group in feature_groups:
            try:
                feature_group.delete()
            except Exception as e:
                print(e)
    except Exception as e:
        print("---------------------")
        print(e)


if __name__ == "__main__":
    fire.Fire(clean)
