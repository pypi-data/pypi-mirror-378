from retryxlib import retry

counter = {"count": 0}

@retry(attempts=3, backoff="fixed", delay=0.1, exceptions=(ValueError,))
def fail_twice_then_succeed():
    if counter["count"] < 2:
        counter["count"] += 1
        raise ValueError("Failing")
    return True

print(fail_twice_then_succeed())  # This will work!
