# Process Flow

In the feature-pipeline component of the project, the task is to get the development data to the feature store. The process is split into multiple steps as follows in etl:

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

Because of limitattion in the number of views, views can be cleaned to reduce the number and also keep the views to those that are used.

## Feature Store

We use [HopsWork](https://c.app.hopsworks.ai/p/45287/fs/45140/fg) for feature store. The login is via Google outh so no account was created. A free account is used with only one project permitted. It is named as _energyconsuption_ because that was the original project where I started. Every dataset is stored under that project. The data for  this project isn called _credit_score_.

### Setting up HopsWork

A HopsWork account is needed. The configuration file was used to send data to HopsWork. Add this as _.env_ file in the root of the `feature-pipeline` project directory with the following data, replacing the values with the appropriate values.

```txt
FS_API_KEY = "YOUR-HOPSWORK-API-KEY"
FS_PROJECT_NAME = "YOUR-PROJECT-NAME"
```

## Explorations

There are some things I am yet to research on. These includes

- When I added prefect to the script, it removed all the logging I had added via the python standard logging

## Blog Explanation

Follow readme to understand about setting up and running the code. To run the code you will need a 

## ETL Code

In the feature_pipeline/pipeline.py file, we have the main entry point of the pipeline under the `run()` method.

As you can see below, the run method follows on a high level the exact steps of an ETL pipeline:

extract.from_api() — Extract the data from the energy consumption API.
    transform() — Transform the extracted data.
    validation.build_expectation_suite() — Build the data validation and integrity suite. Ignore this step, as we will insist on it in Lesson 6.
    load.to_feature_store() — Load the data in the feature store.

Please note how I used the logger to reflect the system's current state. When your program is deployed and running 24/7, having verbose logging is crucial to debugging the system. Also, always use the Python logger instead of the print method, as you can choose different logging levels and output streams.

On a higher level, it seems easy to understand. Let's dive into each component separately.
