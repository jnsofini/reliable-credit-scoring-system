def stage_info(stage, symbol="=", length=100):
    msg = f"\n{symbol*length}\n{stage.center(length, symbol)}\n{symbol*length}"
    return msg
