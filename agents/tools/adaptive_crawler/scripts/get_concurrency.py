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

    cpu_count = os.cpu_count() or 1

    mem_bytes = None
    if os.path.exists("/sys/fs/cgroup/memory.max"):
        try:
            with open("/sys/fs/cgroup/memory.max", "r") as f:
                val = f.read().strip()
                if val != "max":
                    mem_bytes = int(val)
        except Exception:
            pass

    if mem_bytes is None and os.path.exists(
        "/sys/fs/cgroup/memory/memory.limit_in_bytes"
    ):
        try:
            with open("/sys/fs/cgroup/memory/memory.limit_in_bytes", "r") as f:
                mem_bytes = int(f.read().strip())
        except Exception:
            pass

    if mem_bytes is None and hasattr(os, "sysconf"):
        try:
            pages = os.sysconf("SC_PHYS_PAGES")
            page_size = os.sysconf("SC_PAGE_SIZE")
            if pages and page_size:
                mem_bytes = pages * page_size
        except Exception:
            pass

    if mem_bytes and mem_bytes > 0:
        mem_mb = mem_bytes / (1024 * 1024)
        max_by_mem = max(1, int(mem_mb // 500))
        concurrency = min(cpu_count, max_by_mem)
    else:
        concurrency = cpu_count

    return max(1, concurrency)


if __name__ == "__main__":
    print(get_suitable_concurrency())
