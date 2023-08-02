"""Module for formatting logging and printing."""


def stage_info(stage, symbol="=", length=100):
    """Helps with formatting data for logging."""
    msg = f"\n{symbol*length}\n{stage.center(length, symbol)}\n{symbol*length}"
    return msg
