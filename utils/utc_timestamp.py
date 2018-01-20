import time


def utc_timestamp() -> int:
    return int(time.time() * 1000)
