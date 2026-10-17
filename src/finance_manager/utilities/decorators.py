from functools import wraps
from time import sleep


def retry_until_transaction_ready(func):
    @wraps(func)
    def _wrapper(*args, **kwargs):
        max_attempts = kwargs.pop("max_attempts", 20)
        delay = kwargs.pop("delay", 3)

        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1.")
        if delay < 0:
            raise ValueError("delay must be non-negative.")

        for attempt in range(1, max_attempts + 1):
            if attempt > 1:
                sleep(delay)
            response = func(*args, **kwargs)
            if response["transactions_update_status"].value != "NOT_READY":
                return response

        raise TimeoutError(
            f"Transactions remained NOT_READY after {max_attempts} attempts."
        )

    return _wrapper
