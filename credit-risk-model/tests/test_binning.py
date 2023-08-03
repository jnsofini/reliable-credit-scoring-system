"""Module to holde tests."""

import pytest
from deepdiff import DeepDiff
from optbinning import BinningProcess
# from src.tools import read_json


@pytest.fixture
def get_binning_objects():
    """Loads artifacts that are needed for tests."""
    actual_response_binning = BinningProcess.load(
        "data/reference/auto-binning-process.pkl"
    )
    expected_response_binning = BinningProcess.load(
        "data/uat/preprocessing/binning-transformer.pkl"
    )
    return actual_response_binning, expected_response_binning


# @pytest.fixture
def test_compare_tables(
    # get_binning_objects,
):  # (actual_response, expected_response, significant_digits=2):
    """Compare results of any pipeline with expected results."""
    actual_binning, expected_binning = get_binning_objects()
    actual_response = actual_binning.summary().to_dict(orient="records")
    expected_response = expected_binning.summary().to_dict(orient="records")
    diff = DeepDiff(actual_response, expected_response, significant_digits=2)
    # print("Difference is: ", diff)
    assert 'values_changed' not in diff
    assert 'type_changes' not in diff


# compare_tables(
# actual_response=actual_response.summary(),
# expected_response=expected_response.summary()
# )
