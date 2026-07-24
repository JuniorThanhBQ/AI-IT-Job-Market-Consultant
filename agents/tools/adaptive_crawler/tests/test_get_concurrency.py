import os
from unittest.mock import mock_open, patch

from agents.tools.adaptive_crawler.scripts.get_concurrency import (
    get_suitable_concurrency,
)


def test_get_suitable_concurrency_default():
    concurrency = get_suitable_concurrency()
    assert isinstance(concurrency, int)
    assert concurrency >= 1


def test_get_suitable_concurrency_env_override(monkeypatch):
    monkeypatch.setenv("CELERY_WORKER_CONCURRENCY", "4")
    assert get_suitable_concurrency() == 4


def test_get_suitable_concurrency_celery_concurrency_env(monkeypatch):
    monkeypatch.delenv("CELERY_WORKER_CONCURRENCY", raising=False)
    monkeypatch.setenv("CELERY_CONCURRENCY", "3")
    assert get_suitable_concurrency() == 3


def test_get_suitable_concurrency_invalid_env(monkeypatch):
    monkeypatch.setenv("CELERY_WORKER_CONCURRENCY", "invalid")
    concurrency = get_suitable_concurrency()
    assert isinstance(concurrency, int)
    assert concurrency >= 1


def test_get_suitable_concurrency_negative_env(monkeypatch):
    monkeypatch.setenv("CELERY_WORKER_CONCURRENCY", "-5")
    concurrency = get_suitable_concurrency()
    assert isinstance(concurrency, int)
    assert concurrency >= 1


def test_cgroup_v2_memory_max(monkeypatch):
    monkeypatch.delenv("CELERY_WORKER_CONCURRENCY", raising=False)
    monkeypatch.delenv("CELERY_CONCURRENCY", raising=False)

    def mock_exists(path):
        return path == "/sys/fs/cgroup/memory.max"

    m_open = mock_open(read_data="2097152000\n")  # ~2000 MB -> 4 concurrency max

    with patch("os.path.exists", side_effect=mock_exists):
        with patch("builtins.open", m_open):
            with patch("os.cpu_count", return_value=8):
                assert get_suitable_concurrency() == 4


def test_cgroup_v2_memory_max_is_max(monkeypatch):
    monkeypatch.delenv("CELERY_WORKER_CONCURRENCY", raising=False)
    monkeypatch.delenv("CELERY_CONCURRENCY", raising=False)

    def mock_exists(path):
        return path == "/sys/fs/cgroup/memory.max"

    m_open = mock_open(read_data="max\n")

    with patch("os.path.exists", side_effect=mock_exists):
        with patch("builtins.open", m_open):
            with patch("os.cpu_count", return_value=4):
                assert get_suitable_concurrency() == 4


def test_cgroup_v2_exception(monkeypatch):
    monkeypatch.delenv("CELERY_WORKER_CONCURRENCY", raising=False)
    monkeypatch.delenv("CELERY_CONCURRENCY", raising=False)

    def mock_exists(path):
        return path == "/sys/fs/cgroup/memory.max"

    with patch("os.path.exists", side_effect=mock_exists):
        with patch("builtins.open", side_effect=PermissionError("Denied")):
            with patch("os.cpu_count", return_value=2):
                assert get_suitable_concurrency() == 2


def test_cgroup_v1_memory_limit(monkeypatch):
    monkeypatch.delenv("CELERY_WORKER_CONCURRENCY", raising=False)
    monkeypatch.delenv("CELERY_CONCURRENCY", raising=False)

    def mock_exists(path):
        return path == "/sys/fs/cgroup/memory/memory.limit_in_bytes"

    m_open = mock_open(read_data="1048576000\n")  # ~1000 MB -> 2 concurrency max

    with patch("os.path.exists", side_effect=mock_exists):
        with patch("builtins.open", m_open):
            with patch("os.cpu_count", return_value=8):
                assert get_suitable_concurrency() == 2


def test_cgroup_v1_exception(monkeypatch):
    monkeypatch.delenv("CELERY_WORKER_CONCURRENCY", raising=False)
    monkeypatch.delenv("CELERY_CONCURRENCY", raising=False)

    def mock_exists(path):
        return path == "/sys/fs/cgroup/memory/memory.limit_in_bytes"

    with patch("os.path.exists", side_effect=mock_exists):
        with patch("builtins.open", side_effect=OSError("Read error")):
            with patch("os.cpu_count", return_value=2):
                assert get_suitable_concurrency() == 2


def test_sysconf_memory_fallback(monkeypatch):
    monkeypatch.delenv("CELERY_WORKER_CONCURRENCY", raising=False)
    monkeypatch.delenv("CELERY_CONCURRENCY", raising=False)

    def mock_sysconf(name):
        if name == "SC_PHYS_PAGES":
            return 512000
        if name == "SC_PAGE_SIZE":
            return 4096
        raise ValueError("Unknown sysconf")

    with patch("os.path.exists", return_value=False):
        with patch.object(os, "sysconf", side_effect=mock_sysconf, create=True):
            with patch("os.cpu_count", return_value=4):
                assert get_suitable_concurrency() == 4


def test_sysconf_exception(monkeypatch):
    monkeypatch.delenv("CELERY_WORKER_CONCURRENCY", raising=False)
    monkeypatch.delenv("CELERY_CONCURRENCY", raising=False)

    with patch("os.path.exists", return_value=False):
        with patch.object(
            os, "sysconf", side_effect=ValueError("Sysconf error"), create=True
        ):
            with patch("os.cpu_count", return_value=3):
                assert get_suitable_concurrency() == 3


def test_no_cpu_count_fallback(monkeypatch):
    monkeypatch.delenv("CELERY_WORKER_CONCURRENCY", raising=False)
    monkeypatch.delenv("CELERY_CONCURRENCY", raising=False)

    with patch("os.path.exists", return_value=False):
        with patch("os.cpu_count", return_value=None):
            assert get_suitable_concurrency() == 1
