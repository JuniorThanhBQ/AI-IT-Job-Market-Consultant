import os


def get_suitable_concurrency() -> int:
    env_concurrency = os.getenv("CELERY_WORKER_CONCURRENCY") or os.getenv(
        "CELERY_CONCURRENCY"
    )
    if env_concurrency:
        try:
            val = int(env_concurrency)
            if val > 0:
                return val
        except ValueError:
            pass

    return os.cpu_count() or 1


if __name__ == "__main__":
    print(get_suitable_concurrency())
