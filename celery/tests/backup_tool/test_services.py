import pytest
from unittest.mock import patch, AsyncMock, mock_open, call
from pathlib import Path
import json

from tools.backup_tool.service import (
    backup_db,
    upload_to_gdrive,
    enforce_retention_policy,
    list_remote_backups,
    check_rclone_login,
    _download_and_decompress_backup,
    _verify_latest_backup_impl,
    verify_latest_backup,
    restore_override,
    run_backup_pipeline,
)


@pytest.mark.asyncio
class TestBackupDB:
    @patch("tools.backup_tool.service.calculate_sha256", return_value="fake_sha_256")
    @patch("tools.backup_tool.service.run_cmd", new_callable=AsyncMock)
    @patch("tools.backup_tool.service.shutil.copyfileobj")
    @patch("tools.backup_tool.service.gzip.open")
    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.unlink")
    async def test_backup_db_success(
        self,
        mock_unlink,
        mock_exists,
        mock_open_file,
        mock_gzip,
        mock_copy,
        mock_run_cmd,
        mock_sha,
    ):
        mock_run_cmd.return_value = (0, "", "")
        temp_dir = Path("/tmp/fake_dir")

        gzip_path, sha_path = await backup_db(temp_dir)

        assert gzip_path.name.endswith(".gz")
        assert sha_path.name.endswith(".sha256")
        mock_run_cmd.assert_called_once()
        mock_unlink.assert_called_once()

    @patch("tools.backup_tool.service.run_cmd", new_callable=AsyncMock)
    async def test_backup_db_cmd_failure(self, mock_run_cmd):
        mock_run_cmd.return_value = (1, "", "pg_dump error")
        temp_dir = Path("/tmp/fake_dir")

        with pytest.raises(RuntimeError) as exc:
            await backup_db(temp_dir)
        assert "pg_dump failed" in str(exc.value)


@pytest.mark.asyncio
class TestUploadToGdrive:
    @patch("tools.backup_tool.service.run_cmd", new_callable=AsyncMock)
    async def test_upload_success(self, mock_run_cmd):
        mock_run_cmd.return_value = (0, "", "")
        await upload_to_gdrive(Path("dump.gz"), Path("dump.gz.sha256"))
        assert mock_run_cmd.call_count == 2

    @patch("tools.backup_tool.service.run_cmd", new_callable=AsyncMock)
    async def test_upload_dump_failure(self, mock_run_cmd):
        mock_run_cmd.return_value = (1, "", "error")
        with pytest.raises(RuntimeError):
            await upload_to_gdrive(Path("dump.gz"), Path("dump.gz.sha256"))

    @patch("tools.backup_tool.service.run_cmd", new_callable=AsyncMock)
    async def test_upload_sha_failure(self, mock_run_cmd):
        mock_run_cmd.side_effect = [(0, "", ""), (1, "", "error")]
        with pytest.raises(RuntimeError):
            await upload_to_gdrive(Path("dump.gz"), Path("dump.gz.sha256"))


@pytest.mark.asyncio
class TestEnforceRetentionPolicy:
    @patch("tools.backup_tool.service.settings")
    @patch("tools.backup_tool.service.run_cmd", new_callable=AsyncMock)
    async def test_enforce_no_deletion_needed(self, mock_run_cmd, mock_settings):
        mock_settings.backup.BACKUP_MAX_STACKS = 3
        fake_files = [{"Name": f"file{i}.dump.gz", "ModTime": str(i)} for i in range(3)]
        mock_run_cmd.return_value = (0, json.dumps(fake_files), "")

        await enforce_retention_policy()
        assert mock_run_cmd.call_count == 1

    @patch("tools.backup_tool.service.settings")
    @patch("tools.backup_tool.service.run_cmd", new_callable=AsyncMock)
    async def test_enforce_deletion_triggered(self, mock_run_cmd, mock_settings):
        mock_settings.backup.BACKUP_MAX_STACKS = 1
        fake_files = [
            {"Name": "old.dump.gz", "ModTime": "1"},
            {"Name": "new.dump.gz", "ModTime": "2"},
        ]
        mock_run_cmd.side_effect = [
            (0, json.dumps(fake_files), ""),
            (0, "", ""),
            (0, "", ""),
        ]

        await enforce_retention_policy()
        assert mock_run_cmd.call_count == 3
        mock_run_cmd.assert_has_calls(
            [
                call(
                    [
                        "rclone",
                        "deletefile",
                        f"{mock_settings.backup.RCLONE_REMOTE_PATH}/old.dump.gz",
                    ]
                ),
                call(
                    [
                        "rclone",
                        "deletefile",
                        f"{mock_settings.backup.RCLONE_REMOTE_PATH}/old.dump.gz.sha256",
                    ]
                ),
            ],
            any_order=False,
        )


@pytest.mark.asyncio
class TestListRemoteBackups:
    @patch("tools.backup_tool.service.run_cmd", new_callable=AsyncMock)
    async def test_list_success(self, mock_run_cmd):
        fake_files = [
            {"Name": "f1.dump.gz", "ModTime": "1"},
            {"Name": "f2.txt", "ModTime": "2"},
        ]
        mock_run_cmd.return_value = (0, json.dumps(fake_files), "")

        res = await list_remote_backups()
        assert len(res) == 1
        assert res[0]["Name"] == "f1.dump.gz"

    @patch("tools.backup_tool.service.run_cmd", new_callable=AsyncMock)
    async def test_list_directory_not_found(self, mock_run_cmd):
        mock_run_cmd.return_value = (1, "", "directory not found")
        res = await list_remote_backups()
        assert res == []

    @patch("tools.backup_tool.service.run_cmd", new_callable=AsyncMock)
    async def test_list_runtime_error(self, mock_run_cmd):
        mock_run_cmd.return_value = (1, "", "generic error")
        with pytest.raises(RuntimeError):
            await list_remote_backups()


@pytest.mark.asyncio
class TestCheckRcloneLogin:
    @patch("tools.backup_tool.service.shutil.which", return_value=None)
    async def test_no_rclone(self, mock_which):
        logged_in, msg = await check_rclone_login()
        assert not logged_in

    @patch("tools.backup_tool.service.shutil.which", return_value="/usr/bin/rclone")
    @patch("tools.backup_tool.service.run_cmd", new_callable=AsyncMock)
    async def test_rclone_success(self, mock_run_cmd, mock_which):
        mock_run_cmd.return_value = (0, "", "")
        logged_in, msg = await check_rclone_login()
        assert logged_in

    @patch("tools.backup_tool.service.shutil.which", return_value="/usr/bin/rclone")
    @patch("tools.backup_tool.service.run_cmd", new_callable=AsyncMock)
    async def test_rclone_failure(self, mock_run_cmd, mock_which):
        mock_run_cmd.return_value = (1, "", "error")
        logged_in, msg = await check_rclone_login()
        assert not logged_in


@pytest.mark.asyncio
class TestDownloadAndDecompress:
    @patch("tools.backup_tool.service.list_remote_backups", new_callable=AsyncMock)
    async def test_no_backups(self, mock_list):
        mock_list.return_value = []
        res = await _download_and_decompress_backup(Path("/tmp"))
        assert res is None

    @patch("tools.backup_tool.service.list_remote_backups", new_callable=AsyncMock)
    @patch("tools.backup_tool.service.run_cmd", new_callable=AsyncMock)
    async def test_download_dump_fails(self, mock_run_cmd, mock_list):
        mock_list.return_value = [{"Name": "f1.dump.gz"}]
        mock_run_cmd.return_value = (1, "", "error")
        res = await _download_and_decompress_backup(Path("/tmp"))
        assert res is None

    @patch("tools.backup_tool.service.list_remote_backups", new_callable=AsyncMock)
    @patch("tools.backup_tool.service.run_cmd", new_callable=AsyncMock)
    async def test_download_sha_fails(self, mock_run_cmd, mock_list):
        mock_list.return_value = [{"Name": "f1.dump.gz"}]
        mock_run_cmd.side_effect = [(0, "", ""), (1, "", "error")]
        res = await _download_and_decompress_backup(Path("/tmp"))
        assert res is None

    @patch("tools.backup_tool.service.list_remote_backups", new_callable=AsyncMock)
    @patch("tools.backup_tool.service.run_cmd", new_callable=AsyncMock)
    @patch("tools.backup_tool.service.calculate_sha256", return_value="actual_sha")
    @patch("builtins.open", new_callable=mock_open, read_data="expected_sha filename")
    async def test_sha_mismatch(self, mock_open_f, mock_sha, mock_run_cmd, mock_list):
        mock_list.return_value = [{"Name": "f1.dump.gz"}]
        mock_run_cmd.return_value = (0, "", "")
        res = await _download_and_decompress_backup(Path("/tmp"))
        assert res is None

    @patch("tools.backup_tool.service.list_remote_backups", new_callable=AsyncMock)
    @patch("tools.backup_tool.service.run_cmd", new_callable=AsyncMock)
    @patch("tools.backup_tool.service.calculate_sha256", return_value="match_sha")
    @patch("builtins.open", new_callable=mock_open, read_data="match_sha filename")
    @patch("tools.backup_tool.service.gzip.open")
    @patch("tools.backup_tool.service.shutil.copyfileobj")
    async def test_success(
        self, mock_copy, mock_gzip, mock_open_f, mock_sha, mock_run_cmd, mock_list
    ):
        mock_list.return_value = [{"Name": "f1.dump.gz"}]
        mock_run_cmd.return_value = (0, "", "")
        res = await _download_and_decompress_backup(Path("/tmp"))
        assert res == Path("/tmp/f1.dump")


@pytest.mark.asyncio
class TestPipelinesAndWrappers:
    @patch(
        "tools.backup_tool.service._download_and_decompress_backup",
        new_callable=AsyncMock,
    )
    @patch("tools.backup_tool.service.db_verify_backup", new_callable=AsyncMock)
    async def test_verify_latest_backup_impl_success(self, mock_db_verify, mock_dl):
        mock_dl.return_value = Path("dump")
        mock_db_verify.return_value = True
        assert await _verify_latest_backup_impl(Path("/tmp")) is True

    @patch(
        "tools.backup_tool.service._download_and_decompress_backup",
        new_callable=AsyncMock,
    )
    async def test_verify_latest_backup_impl_fail_dl(self, mock_dl):
        mock_dl.return_value = None
        assert await _verify_latest_backup_impl(Path("/tmp")) is False

    @patch(
        "tools.backup_tool.service._verify_latest_backup_impl", new_callable=AsyncMock
    )
    async def test_verify_latest_backup(self, mock_impl):
        mock_impl.return_value = True
        assert await verify_latest_backup(Path("/tmp")) is True

    @patch(
        "tools.backup_tool.service._download_and_decompress_backup",
        new_callable=AsyncMock,
    )
    async def test_restore_override_fail_dl(self, mock_dl):
        mock_dl.return_value = None
        assert await restore_override(Path("/tmp")) is False

    @patch(
        "tools.backup_tool.service._download_and_decompress_backup",
        new_callable=AsyncMock,
    )
    @patch("tools.backup_tool.service.db_verify_backup", new_callable=AsyncMock)
    async def test_restore_override_fail_verify(self, mock_db_verify, mock_dl):
        mock_dl.return_value = Path("dump")
        mock_db_verify.return_value = False
        assert await restore_override(Path("/tmp")) is False

    @patch(
        "tools.backup_tool.service._download_and_decompress_backup",
        new_callable=AsyncMock,
    )
    @patch("tools.backup_tool.service.db_verify_backup", new_callable=AsyncMock)
    @patch("tools.backup_tool.service.db_restore_override", new_callable=AsyncMock)
    async def test_restore_override_success(
        self, mock_db_restore, mock_db_verify, mock_dl
    ):
        mock_dl.return_value = Path("dump")
        mock_db_verify.return_value = True
        mock_db_restore.return_value = True
        assert await restore_override(Path("/tmp")) is True

    @patch("tools.backup_tool.service.backup_db", new_callable=AsyncMock)
    @patch("tools.backup_tool.service.upload_to_gdrive", new_callable=AsyncMock)
    @patch("tools.backup_tool.service.enforce_retention_policy", new_callable=AsyncMock)
    @patch(
        "tools.backup_tool.service._verify_latest_backup_impl", new_callable=AsyncMock
    )
    async def test_run_backup_pipeline_success(
        self, mock_verify, mock_enforce, mock_upload, mock_backup
    ):
        mock_backup.return_value = (Path("a"), Path("b"))
        mock_verify.return_value = True
        assert await run_backup_pipeline() is True

    @patch("tools.backup_tool.service.backup_db", new_callable=AsyncMock)
    @patch("tools.backup_tool.service.upload_to_gdrive", new_callable=AsyncMock)
    @patch("tools.backup_tool.service.enforce_retention_policy", new_callable=AsyncMock)
    @patch(
        "tools.backup_tool.service._verify_latest_backup_impl", new_callable=AsyncMock
    )
    async def test_run_backup_pipeline_verify_fail(
        self, mock_verify, mock_enforce, mock_upload, mock_backup
    ):
        mock_backup.return_value = (Path("a"), Path("b"))
        mock_verify.return_value = False
        assert await run_backup_pipeline() is False

    @patch("tools.backup_tool.service.backup_db", new_callable=AsyncMock)
    async def test_run_backup_pipeline_exception(self, mock_backup):
        mock_backup.side_effect = Exception("Crash")
        assert await run_backup_pipeline() is False
