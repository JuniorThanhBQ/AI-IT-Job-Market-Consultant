import asyncio
import hashlib
import logging
import os
import re
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any

try:
    import fcntl as _fcntl

    fcntl: Any = _fcntl
except ImportError:
    fcntl = None

from app.core.config import settings

logger = logging.getLogger(__name__)

DEFAULT_CMD_TIMEOUT = getattr(settings.backup, "COMMAND_TIMEOUT_SECONDS", 3600)
LOCK_FILE_PATH = Path(
    getattr(
        settings.backup,
        "LOCK_FILE_PATH",
        os.path.join(tempfile.gettempdir(), "db_backup_restore.lock"),
    )
)
_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _safe_identifier(name: str, what: str) -> str:
    if not name or not _IDENTIFIER_RE.match(name):
        raise ValueError(
            f"Refusing to use unsafe {what} identifier: {name!r}. "
            f"Must match {_IDENTIFIER_RE.pattern}"
        )
    return f'"{name}"'


@contextmanager
def pipeline_lock(operation: str):
    if fcntl is None:
        logger.warning(
            "fcntl is not available on this platform. Running without locking."
        )
        yield
        return

    LOCK_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    lock_file = open(LOCK_FILE_PATH, "w")
    try:
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        lock_file.close()
        raise RuntimeError(
            f"Another backup/restore operation appears to be running; refusing "
            f"to start '{operation}'. If this is unexpected (stale lock), check "
            f"{LOCK_FILE_PATH}."
        )
    try:
        logger.info(f"Acquired pipeline lock for '{operation}'")
        yield
    finally:
        fcntl.flock(lock_file, fcntl.LOCK_UN)
        lock_file.close()


def calculate_sha256(file_path: Path) -> str:
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


async def run_cmd(
    cmd: list[str], env: dict | None = None, timeout: float | None = DEFAULT_CMD_TIMEOUT
) -> tuple[int, str, str]:
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=env,
    )
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except TimeoutError:
        logger.error(f"Command timed out after {timeout}s, killing: {' '.join(cmd)}")
        proc.kill()
        await proc.wait()
        return -1, "", f"Command timed out after {timeout}s"
    return (
        proc.returncode if proc.returncode is not None else -1,
        stdout.decode().strip(),
        stderr.decode().strip(),
    )
