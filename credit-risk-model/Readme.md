# Model Traininig Pipeline

In the model training pipeline, we carry out two main task; feature reduction and model development. The model we are developing is a scoring model which scores customers with a risk rating. It also demands a lot of explainablity so this inspires the choice models used.


## Development environment setup

The files to set this environment are `Pipfile` and `Pipfile.lock`. Navigate to the project root directory and then setup the virtual environment via `pipenv`:

```shell
pipenv install --dev
pipenv shell (to activate the enviroment)
```

The `--dev` flag is for development purpise. The packages needed to run in production are a small subset of the files needed in development.

## Data reduction

The data reduction steps includes the follwing

- [Separation](src/test_train_split.py): In this step, we strategically partitions the data to ensure that the model's performance can be evaluated on unseen data. By using separate training and testing sets, train_test_split helps to avoid overfitting.  The testing set allows us to estimate how well the model will perform on new, unseen data. This evaluation helps in selecting the best model, tuning hyperparameters, and making informed decisions about its deployment and usage in real-world scenarios.

- [Preprocessing](src/preprocess.py): This steps involves a few processes. It holds data transformation as well as dimensionality reduction to improve the efficiency of the learning process. In the feature reduction part we aim to remove the feature with negligeable variation using **VarianceThreshold**.

    In the second part of the step, we preprocess the data including transforming every feature to ordinal data using WOE. With `OptBinning's` `BinningProcess`, we efficiently transform continuous variables into categorical bins, improving the interpretability and predictive power of your models. Run this stage with the following command

    ```python
    python -m src.preprocess
    ```

- [Clustering](src/clustering.py): In this feature reduction stage, the features are clustered together based on their correlation using 'varclushi' library. The feature with the highest informational value and the one at the center of the cluster are selected. With Varclushi, you can identify and eliminate redundant or irrelevant features from your dataset, leading to more efficient and interpretable models. Run this stage with the following command

    ```python
    python -m src.clustering
    ```

- [Feature selection](src/featurization.py): In the feature selection stage, a further smaller number of feature are further selected (using `RFECV`, Recursive Feature Elimination with Cross-Validation) to provide a parsimonous model. There are other techniques which we tried but didn't use in the final pipeline, including sequetial feature selection. Run this stage with the following command

    ```python
    python -m src.featurization
    ```

Alternatively, all these sections can be ran via a make file via

```shell
make datareduction
```

## [Model](src/scorecard.py)

The model part involves three states. These stages are 

- Binnin stage to transform the data to WOE
- A estimatore stage where an algorithm is picked and optimized. The algorithms and packages will be scikit-learn `LogisticRegression` that is widely used for binary and multiclass classification problems.
- The scorecarding stage where the probabilities from the model prediction are used to create a range of scores which rank order risk. The `Scorecard` module in OptBinning allows you to develop scorecards by combining binning, logistic regression and scoring, facilitating credit risk modeling and scoring applications.

    Run this stage with the following command

    ```python
    python -m src.scorecard
    ```
