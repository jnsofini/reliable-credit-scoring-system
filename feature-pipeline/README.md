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