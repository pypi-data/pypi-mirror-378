import logging
from functools import wraps
from collections.abc import Callable


def enable_debug_logging(level=logging.INFO):
    logger = logging.getLogger(__package__)
    logger.setLevel(level)

    # also handle info and debug
    logging.basicConfig(level=logging.INFO, format="info: %(message)s")
    logging.basicConfig(level=logging.DEBUG, format="debug: %(message)s")

    logger.info(f"This is {__package__}. Enabled more verbose logging.")


def expand_to_dim(dim: int, n: int = 0):
    """
    Expand the nth argument of the decorated function to have at least `dim` dimensions.
    This can for eample be used to modify functions taking a stack of arrays as their
    first argument to also work on single arrays.

    Paramters
    ---------
    dim: int
        Dimension to expand the nth argument to.
    n: int
        Number of the argument to be expanded.

    Example
    ------
    see definition of hotopy.image.to_polar2D
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # expand array
            array = args[n]
            added_dims = dim - array.ndim
            array = array[added_dims * (None,) + (...,)]
            args = args[:n] + (array,) + args[n + 1 :]

            # Call the original function
            result = func(*args, **kwargs)

            # remove extra dimensions
            return result[added_dims * (0,)]

        return wrapper

    return decorator
