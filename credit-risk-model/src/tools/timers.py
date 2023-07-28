import time
from typing import Callable


def timeit(logger=None):
    def wrapper(func: Callable):
        def wrapper_function(*args, **kwargs):
            start = start_time = time.perf_counter()
            func(*args, **kwargs)
            end = time.perf_counter()
            msg = f"Time taken : {(end - start):.2} seconds"
            if logger:
                logger(msg)
            else:
                print(msg)

        return wrapper_function

    return wrapper
