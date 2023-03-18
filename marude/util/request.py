from time import sleep
from functools import wraps
from requests.exceptions import ConnectionError, ChunkedEncodingError, ReadTimeout


def retry(after: float = None, multiplier: float = None):

    def _retry(run: callable):

        @wraps(run)
        def __retry(*args, **kwargs):
            attempts_count = None if after is None else 0

            while True:
                try:
                    return run(*args, **kwargs)
                except (ValueError, ConnectionError, ChunkedEncodingError, ReadTimeout) as error:
                    if after is not None:
                        if multiplier is None:
                            delay = after
                        else:
                            delay = after * (multiplier ^ attempts_count)
                            attempts_count += 1
                        print(f'Error executing query: {error}, repeat after {delay} seconds')
                        sleep(delay)
                    print(f'Error executing query: {error}, repeat immediately')
        return __retry
    return _retry
