import logging
import time
from functools import wraps


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def a_named_timeit(name: str):
    """
    Async decorator to log execution time of a wrapped function
    """
    def inner(func):
        @wraps(func)
        async def wrapped(*args, **kwargs):
            t1 = time.perf_counter()
            res = await func(*args, **kwargs)
            logger.info(f'{name}: {time.perf_counter()-t1}; {func}')
            return res
        return wrapped
    return inner


def named_timeit(name: str):
    """
    Sync decorator to log execution time of a wrapped function
    """
    def inner(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            t1 = time.perf_counter()
            res = func(*args, **kwargs)
            logger.info(f'{name}: {time.perf_counter()-t1}; {func}')
            return res
        return wrapped
    return inner
