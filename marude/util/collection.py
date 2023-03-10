from functools import wraps


def as_tuple(func):
    @wraps(func)
    def _as_tuple(*args, **kwargs):
        return tuple(func(*args, **kwargs))

    return _as_tuple
