import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from tools.backup_tool.backup_services import (
    check_rclone_login,
    list_remote_backups,
    restore_override,
    run_backup_pipeline,
    verify_latest_backup,
)


@pytest.mark.asyncio
@patch(
    "tools.backup_tool.backup_services.run_cmd",
    new_callable=AsyncMock,
    return_value=(0, "Total: 100GB", ""),
)
@patch("shutil.which", return_value="/usr/bin/rclone")
async def test_check_rclone_login_success(
    mock_which: MagicMock, mock_run_cmd: AsyncMock
):
    success, message = await check_rclone_login()
    assert success is True
    assert message == ""


@pytest.mark.asyncio
@patch("shutil.which", return_value=None)
async def test_check_rclone_login_missing_binary(mock_which: MagicMock):
    success, message = await check_rclone_login()
    assert success is False
    assert "rclone executable not found" in message


@pytest.mark.asyncio
@patch(
    "tools.backup_tool.backup_services.run_cmd",
    new_callable=AsyncMock,
    return_value=(1, "", "Unauthorized"),
)
@patch("shutil.which", return_value="/usr/bin/rclone")
async def test_check_rclone_login_command_failure(
    mock_which: MagicMock, mock_run_cmd: AsyncMock
):
    success, message = await check_rclone_login()
    assert success is False
    assert message == "Unauthorized"


@pytest.mark.asyncio
@patch("tools.backup_tool.backup_services.run_cmd", new_callable=AsyncMock)
async def test_list_remote_backups_success(mock_run_cmd: AsyncMock):
    sample_files = [
        {"Name": "db_backup_20260101.dump.gz", "ModTime": "2026-01-01T10:00:00Z"},
        {"Name": "db_backup_20260102.dump.gz", "ModTime": "2026-01-02T10:00:00Z"},
        {"Name": "other_file.txt", "ModTime": "2026-01-03T10:00:00Z"},
    ]
    mock_run_cmd.return_value = (0, json.dumps(sample_files), "")
    backups = await list_remote_backups()
    assert len(backups) == 2
    assert backups[0]["Name"] == "db_backup_20260102.dump.gz"
    assert backups[1]["Name"] == "db_backup_20260101.dump.gz"


@pytest.mark.asyncio
@patch(
    "tools.backup_tool.backup_services.run_cmd",
    new_callable=AsyncMock,
    return_value=(1, "", "directory not found error"),
)
async def test_list_remote_backups_directory_not_found(mock_run_cmd: AsyncMock):
    backups = await list_remote_backups()
    assert backups == []


@pytest.mark.asyncio
@patch(
    "tools.backup_tool.backup_services.run_cmd",
    new_callable=AsyncMock,
    return_value=(1, "", "network timeout"),
)
async def test_list_remote_backups_failure(mock_run_cmd: AsyncMock):
    with pytest.raises(RuntimeError) as exc_info:
        await list_remote_backups()
    assert "Failed to list remote backups" in str(exc_info.value)


@pytest.mark.asyncio
@patch(
    "tools.backup_tool.backup_services.run_cmd",
    new_callable=AsyncMock,
    return_value=(0, "invalid-json", ""),
)
async def test_list_remote_backups_json_parse_failure(mock_run_cmd: AsyncMock):
    with pytest.raises(RuntimeError) as exc_info:
        await list_remote_backups()
    assert "Failed to parse rclone JSON output" in str(exc_info.value)


@pytest.mark.asyncio
@patch(
    "tools.backup_tool.backup_services.verify_latest_backup_impl",
    new_callable=AsyncMock,
    return_value=True,
)
@patch(
    "tools.backup_tool.backup_services.list_remote_backups",
    new_callable=AsyncMock,
    return_value=[{"Name": "db.dump.gz"}],
)
@patch(
    "tools.backup_tool.backup_services.enforce_retention_policy", new_callable=AsyncMock
)
@patch("tools.backup_tool.backup_services.upload_to_gdrive", new_callable=AsyncMock)
@patch("tools.backup_tool.backup_services.backup_db", new_callable=AsyncMock)
@patch("tools.backup_tool.backup_services.pipeline_lock", return_value=MagicMock())
async def test_run_backup_pipeline_success(
    mock_lock: MagicMock,
    mock_backup_db: AsyncMock,
    mock_upload: AsyncMock,
    mock_retention: AsyncMock,
    mock_list: AsyncMock,
    mock_verify: AsyncMock,
    tmp_path: Path,
):
    mock_backup_db.return_value = (tmp_path / "db.gz", tmp_path / "db.gz.sha256")
    result = await run_backup_pipeline()
    assert result is True


@pytest.mark.asyncio
@patch(
    "tools.backup_tool.backup_services.verify_latest_backup_impl",
    new_callable=AsyncMock,
    return_value=False,
)
@patch(
    "tools.backup_tool.backup_services.list_remote_backups",
    new_callable=AsyncMock,
    return_value=[{"Name": "db.dump.gz"}],
)
@patch(
    "tools.backup_tool.backup_services.enforce_retention_policy", new_callable=AsyncMock
)
@patch("tools.backup_tool.backup_services.upload_to_gdrive", new_callable=AsyncMock)
@patch("tools.backup_tool.backup_services.backup_db", new_callable=AsyncMock)
@patch("tools.backup_tool.backup_services.pipeline_lock", return_value=MagicMock())
async def test_run_backup_pipeline_verification_failure(
    mock_lock: MagicMock,
    mock_backup_db: AsyncMock,
    mock_upload: AsyncMock,
    mock_retention: AsyncMock,
    mock_list: AsyncMock,
    mock_verify: AsyncMock,
    tmp_path: Path,
):
    mock_backup_db.return_value = (tmp_path / "db.gz", tmp_path / "db.gz.sha256")
    result = await run_backup_pipeline()
    assert result is False


@pytest.mark.asyncio
@patch(
    "tools.backup_tool.backup_services.backup_db",
    new_callable=AsyncMock,
    side_effect=RuntimeError("pg_dump error"),
)
@patch("tools.backup_tool.backup_services.pipeline_lock", return_value=MagicMock())
async def test_run_backup_pipeline_exception_handling(
    mock_lock: MagicMock, mock_backup_db: AsyncMock
):
    result = await run_backup_pipeline()
    assert result is False


@pytest.mark.asyncio
@patch(
    "tools.backup_tool.backup_services.verify_latest_backup_impl",
    new_callable=AsyncMock,
    return_value=True,
)
@patch(
    "tools.backup_tool.backup_services.list_remote_backups",
    new_callable=AsyncMock,
    return_value=[{"Name": "db.dump.gz"}],
)
@patch("tools.backup_tool.backup_services.pipeline_lock", return_value=MagicMock())
async def test_verify_latest_backup_success(
    mock_lock: MagicMock,
    mock_list: AsyncMock,
    mock_verify: AsyncMock,
    tmp_path: Path,
):
    result = await verify_latest_backup(tmp_path)
    assert result is True


@pytest.mark.asyncio
@patch(
    "tools.backup_tool.backup_services.verify_latest_backup_impl",
    new_callable=AsyncMock,
    return_value=False,
)
@patch(
    "tools.backup_tool.backup_services.list_remote_backups",
    new_callable=AsyncMock,
    return_value=[{"Name": "db.dump.gz"}],
)
@patch("tools.backup_tool.backup_services.pipeline_lock", return_value=MagicMock())
async def test_verify_latest_backup_failure(
    mock_lock: MagicMock,
    mock_list: AsyncMock,
    mock_verify: AsyncMock,
    tmp_path: Path,
):
    result = await verify_latest_backup(tmp_path)
    assert result is False


@pytest.mark.asyncio
@patch(
    "tools.backup_tool.backup_services.db_restore_override",
    new_callable=AsyncMock,
    return_value=True,
)
@patch(
    "tools.backup_tool.backup_services.db_verify_backup",
    new_callable=AsyncMock,
    return_value=True,
)
@patch(
    "tools.backup_tool.backup_services.download_and_decompress_backup",
    new_callable=AsyncMock,
)
@patch(
    "tools.backup_tool.backup_services.list_remote_backups",
    new_callable=AsyncMock,
    return_value=[{"Name": "db.dump.gz"}],
)
async def test_restore_override_success(
    mock_list: AsyncMock,
    mock_download: AsyncMock,
    mock_verify: AsyncMock,
    mock_restore: AsyncMock,
    tmp_path: Path,
):
    fake_dump = tmp_path / "decompressed.dump"
    mock_download.return_value = fake_dump
    result = await restore_override(tmp_path)
    assert result is True
    mock_restore.assert_awaited_once_with(fake_dump)


@pytest.mark.asyncio
@patch(
    "tools.backup_tool.backup_services.download_and_decompress_backup",
    new_callable=AsyncMock,
    return_value=None,
)
@patch(
    "tools.backup_tool.backup_services.list_remote_backups",
    new_callable=AsyncMock,
    return_value=[{"Name": "db.dump.gz"}],
)
async def test_restore_override_download_failed(
    mock_list: AsyncMock,
    mock_download: AsyncMock,
    tmp_path: Path,
):
    result = await restore_override(tmp_path)
    assert result is False


@pytest.mark.asyncio
@patch("tools.backup_tool.backup_services.db_restore_override", new_callable=AsyncMock)
@patch(
    "tools.backup_tool.backup_services.db_verify_backup",
    new_callable=AsyncMock,
    return_value=False,
)
@patch(
    "tools.backup_tool.backup_services.download_and_decompress_backup",
    new_callable=AsyncMock,
)
@patch(
    "tools.backup_tool.backup_services.list_remote_backups",
    new_callable=AsyncMock,
    return_value=[{"Name": "db.dump.gz"}],
)
async def test_restore_override_pre_verification_failed(
    mock_list: AsyncMock,
    mock_download: AsyncMock,
    mock_verify: AsyncMock,
    mock_restore: AsyncMock,
    tmp_path: Path,
):
    fake_dump = tmp_path / "decompressed.dump"
    mock_download.return_value = fake_dump
    result = await restore_override(tmp_path)
    assert result is False
    mock_restore.assert_not_called()


@pytest.mark.asyncio
@patch(
    "tools.backup_tool.backup_services.db_restore_override",
    new_callable=AsyncMock,
    return_value=False,
)
@patch(
    "tools.backup_tool.backup_services.db_verify_backup",
    new_callable=AsyncMock,
    return_value=True,
)
@patch(
    "tools.backup_tool.backup_services.download_and_decompress_backup",
    new_callable=AsyncMock,
)
@patch(
    "tools.backup_tool.backup_services.list_remote_backups",
    new_callable=AsyncMock,
    return_value=[{"Name": "db.dump.gz"}],
)
async def test_restore_override_db_override_failed(
    mock_list: AsyncMock,
    mock_download: AsyncMock,
    mock_verify: AsyncMock,
    mock_restore: AsyncMock,
    tmp_path: Path,
):
    fake_dump = tmp_path / "decompressed.dump"
    mock_download.return_value = fake_dump
    result = await restore_override(tmp_path)
    assert result is False
