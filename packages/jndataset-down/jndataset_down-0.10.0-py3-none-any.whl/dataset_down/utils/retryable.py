import time
import requests
from http.client import IncompleteRead
from dataset_down.exception.IncompleteReadException import IncompleteReadException
def retry_with_backoff(max_retries=3, base_delay=1, max_delay=5):
    def decorator(func):
        def wrapper(*args, **kwargs):
            retry_count = 0
            delay = base_delay
            while retry_count < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    time.sleep(delay)
                    retry_count += 1
                    delay = min(delay * 1.5, max_delay)
                    if isinstance(e, IncompleteRead):
                        print("IncompleteRead retry... ")
                    elif isinstance(e, requests.exceptions.ConnectionError):
                        print("ConnectionError retry... ")
                    elif isinstance(e, requests.exceptions.ReadTimeout):
                        print("ReadTimeout retry... ")
                    elif isinstance(e, requests.exceptions.ChunkedEncodingError):
                        print("ChunkedEncodingError retry... ")
                    elif isinstance(e, IncompleteReadException):
                        print("IncompleteReadException retry... ")
                    else:
                        print(f"error happend in function {func.__name__} ,msg: {e}")
            raise Exception(
                f"function {func.__name__} failed after {max_retries} retries."
            )
        return wrapper
    return decorator