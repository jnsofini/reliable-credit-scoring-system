# Process Flow

In the feature-pipeline component of the project, the task is to get the development data to the feature store. The process is split into multiple steps as follows in etl:

1. Extract the data with _extract.py_
2. Transform the data with _cleaning.py_ by
    - Renaming columns
    - Casting to proper types
3. Validate the data with _validate.py_ by checking
    - Data types
    - Expected number of columns
    - Limits or set of values
4. Load the data to Hopswork Feature Store with _load.py_.

The other part is to create feature views. This are just like views in database, or losely equivilently, filters when you filter data in pandas it simply create a view on the data.

Because of limitattion in the number of views, views can be cleaned to reduce the number and also keep the views to those that are used.

