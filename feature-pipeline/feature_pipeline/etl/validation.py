from great_expectations.core import ExpectationSuite, ExpectationConfiguration

MODELLING_COLUMNS = ['pulocationid', 'dolocationid', 'duration']

def build_expectation_suite() -> ExpectationSuite:
    """
    Builder used to retrieve an instance of the validation expectation suite.
    """

    expectation_suite_taxi_fare = ExpectationSuite(
        expectation_suite_name="taxi_fare_suite"
    )

    # Columns.
    expectation_suite_taxi_fare.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_table_columns_to_match_ordered_list",
            kwargs={
                "column_list": MODELLING_COLUMNS
            },
        )
    )
    expectation_suite_taxi_fare.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_table_column_count_to_equal", kwargs={"value": 3}
        )
    )

    # Duration values
    expectation_suite_taxi_fare.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_column_values_to_not_be_null",
            kwargs={"column": "duration"},
        )
    )

    expectation_suite_taxi_fare.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_column_values_to_be_of_type",
            kwargs={"column": "pulocationid", "type_": "str"},
        )
    )

    expectation_suite_taxi_fare.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_column_values_to_be_of_type",
            kwargs={"column": "dolocationid", "type_": "str"},
        )
    )

    

    # Energy consumption
    expectation_suite_taxi_fare.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_column_min_to_be_between",
            kwargs={
                "column": "duration",
                "min_value": 1,
                "strict_min": False,
                "max_value": 60,
                "strict_max": False,
            },
        )
    )
    expectation_suite_taxi_fare.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_column_values_to_be_of_type",
            kwargs={"column": "duration", "type_": "float64"},
        )
    )

    return expectation_suite_taxi_fare