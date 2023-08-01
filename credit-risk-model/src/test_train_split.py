import os

import pandas as pd
from sklearn.model_selection import train_test_split

SEED = 42

RAW_DATA_PATH = (
    "/home/fini/github-projects/mlops/capstone/data/heloc_dataset_v1.parquet"
)
TARGET = "RiskPerformance"

# TODO: Add comments and logging to this code


def get_data_splits(X, y, train_size=0.7, val_split=False):
    """Generate balanced data splits."""
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, train_size=train_size, stratify=y
    )
    # If we need validation split then split the test again. Now we con't need it
    if val_split:
        X_val, X_test, y_val, y_test = train_test_split(
            X_test, y_test, train_size=0.5, stratify=y_test
        )
        # Return dict instead?
    return X_train, X_test, y_train, y_test


def load_data(path, drop_cols=None):
    "Loads data and return dataframe without some columns."
    df = pd.read_parquet(path)
    if drop_cols:
        columns_to_drop = list(set(drop_cols).intersection(set(df.columns.values)))
        return df.drop(columns=columns_to_drop)
    return df


def save_parquet(path, frames: dict):
    """Saves dict of dataframes to files with name by key."""
    for name, frame in frames.items():
        frame.to_parquet(os.path.join(path, f"{name}.parquet"))


def main():
    """Main file to run the process."""
    raw_data = load_data(path=RAW_DATA_PATH)

    X_train, X_test, y_train, y_test = get_data_splits(
        X=raw_data.drop(columns=[TARGET]),
        y=raw_data[TARGET].astype("int8"),
        train_size=0.7,
        val_split=False,
    )

    # Save the data
    save_parquet(
        path="data",
        frames={
            "X_train": X_train,
            "X_val": X_test,
            "y_train": y_train.to_frame(),
            "y_val": y_test.to_frame(),
        },
    )


if __name__ == "__main__":
    main()
