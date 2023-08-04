# pylint: disable=[missing-module-docstring,invalid-name,
# broad-exception-caught, logging-fstring-interpolation]

from great_expectations.core import ExpectationConfiguration, ExpectationSuite

MODELLING_COLUMNS = [
    "riskperformance",
    "externalriskestimate",
    "msinceoldesttradeopen",
    "msincemostrecenttradeopen",
    "averageminfile",
    "numsatisfactorytrades",
    "numtrades60ever2derogpubrec",
    "numtrades90ever2derogpubrec",
    "percenttradesneverdelq",
    "msincemostrecentdelq",
    "maxdelq2publicreclast12m",
    "maxdelqever",
    "numtotaltrades",
    "numtradesopeninlast12m",
    "percentinstalltrades",
    "msincemostrecentinqexcl7days",
    "numinqlast6m",
    "numinqlast6mexcl7days",
    "netfractionrevolvingburden",
    "netfractioninstallburden",
    "numrevolvingtradeswbalance",
    "numinstalltradeswbalance",
    "numbank2natltradeswhighutilization",
    "percenttradeswbalance",
    "operation_date",
    "id",
]


def build_expectation_suite() -> ExpectationSuite:
    """
    Builder used to retrieve an instance of the validation expectation suite.
    """

    expectation_suite_credit_score = ExpectationSuite(
        expectation_suite_name="credit_score_suite"
    )

    # Columns.
    expectation_suite_credit_score.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_table_columns_to_match_ordered_list",
            kwargs={"column_list": MODELLING_COLUMNS},
        )
    )
    expectation_suite_credit_score.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_table_column_count_to_equal", kwargs={"value": 26}
        )
    )

    # Duration values
    expectation_suite_credit_score.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_column_values_to_not_be_null",
            kwargs={"column": "riskperformance"},
        )
    )

    expectation_suite_credit_score.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_column_values_to_be_of_type",
            kwargs={"column": "riskperformance", "type_": "bool"},
        )
    )

    expectation_suite_credit_score.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_column_values_to_be_of_type",
            kwargs={"column": "id", "type_": "str"},
        )
    )

    for col in MODELLING_COLUMNS[:-2]:
        expectation_suite_credit_score.add_expectation(
            ExpectationConfiguration(
                expectation_type="expect_column_values_to_be_of_type",
                kwargs={"column": col, "type_": "int"},
            )
        )

    # RiskPerformance
    expectation_suite_credit_score.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_column_min_to_be_between",
            kwargs={
                "column": "riskperformance",
                "min_value": 0,
                "strict_min": False,
                "max_value": 1,
                "strict_max": False,
            },
        )
    )

    return expectation_suite_credit_score
