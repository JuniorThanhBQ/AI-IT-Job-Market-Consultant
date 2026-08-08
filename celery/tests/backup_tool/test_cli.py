import os
import pytest
from unittest.mock import patch, AsyncMock, call

from tools.backup_tool.cli import (
    _non_interactive,
    _confirm,
    list_backups_cli,
    run_backup_cli,
    verify_restore_cli,
    run_restore_override_cli,
    main,
)


class TestCLIHelpers:
    @patch("sys.stdin.isatty")
    def test_non_interactive_true(self, mock_isatty):
        mock_isatty.return_value = False
        assert _non_interactive() is True

    @patch("sys.stdin.isatty")
    def test_non_interactive_false(self, mock_isatty):
        mock_isatty.return_value = True
        assert _non_interactive() is False

    @patch("sys.stdin.isatty")
    def test_non_interactive_exception(self, mock_isatty):
        mock_isatty.side_effect = Exception("error")
        assert _non_interactive() is True

    @patch("tools.backup_tool.cli._non_interactive", return_value=True)
    def test_confirm_non_interactive(self, mock_non_interactive):
        assert _confirm("Proceed?") is False

    @patch("tools.backup_tool.cli._non_interactive", return_value=False)
    @patch("builtins.input", return_value="y")
    def test_confirm_interactive_yes(self, mock_input, mock_non_interactive):
        assert _confirm("Proceed?") is True

    @patch("tools.backup_tool.cli._non_interactive", return_value=False)
    @patch("builtins.input", return_value="N")
    def test_confirm_interactive_no(self, mock_input, mock_non_interactive):
        assert _confirm("Proceed?") is False


@pytest.mark.asyncio
class TestListBackupsCLI:
    @patch("tools.backup_tool.cli.list_remote_backups", new_callable=AsyncMock)
    @patch("builtins.print")
    async def test_list_backups_empty(self, mock_print, mock_list_remote):
        mock_list_remote.return_value = []
        await list_backups_cli()
        mock_print.assert_not_called()

    @patch("tools.backup_tool.cli.list_remote_backups", new_callable=AsyncMock)
    @patch("builtins.print")
    @patch(
        "tools.backup_tool.cli.format_utc_modtime", return_value="2023-01-01 12:00:00"
    )
    async def test_list_backups_with_data(
        self, mock_format, mock_print, mock_list_remote
    ):
        mock_list_remote.return_value = [
            {"Name": "backup1.zip", "Size": 1048576, "ModTime": "raw_time_1"},
            {"Name": "backup2.zip", "Size": 0, "ModTime": "raw_time_2"},
        ]
        await list_backups_cli()
        assert mock_print.call_count == 4
        mock_format.assert_has_calls([call("raw_time_1"), call("raw_time_2")])

    @patch("tools.backup_tool.cli.list_remote_backups", new_callable=AsyncMock)
    async def test_list_backups_exception(self, mock_list_remote):
        mock_list_remote.side_effect = Exception("Connection Error")
        with pytest.raises(SystemExit) as exc:
            await list_backups_cli()
        assert exc.value.code == 1


@pytest.mark.asyncio
class TestRunBackupCLI:
    @patch("tools.backup_tool.cli.run_backup_pipeline", new_callable=AsyncMock)
    async def test_run_backup_success(self, mock_pipeline):
        mock_pipeline.return_value = True
        await run_backup_cli()

    @patch("tools.backup_tool.cli.run_backup_pipeline", new_callable=AsyncMock)
    async def test_run_backup_failure(self, mock_pipeline):
        mock_pipeline.return_value = False
        with pytest.raises(SystemExit) as exc:
            await run_backup_cli()
        assert exc.value.code == 1

    @patch("tools.backup_tool.cli.run_backup_pipeline", new_callable=AsyncMock)
    async def test_run_backup_exception(self, mock_pipeline):
        mock_pipeline.side_effect = RuntimeError("Process failed")
        with pytest.raises(SystemExit) as exc:
            await run_backup_cli()
        assert exc.value.code == 1


@pytest.mark.asyncio
class TestVerifyRestoreCLI:
    @patch("tools.backup_tool.cli.verify_latest_backup", new_callable=AsyncMock)
    async def test_verify_restore_success(self, mock_verify):
        mock_verify.return_value = True
        await verify_restore_cli()

    @patch("tools.backup_tool.cli.verify_latest_backup", new_callable=AsyncMock)
    async def test_verify_restore_failure(self, mock_verify):
        mock_verify.return_value = False
        with pytest.raises(SystemExit) as exc:
            await verify_restore_cli()
        assert exc.value.code == 1

    @patch("tools.backup_tool.cli.verify_latest_backup", new_callable=AsyncMock)
    async def test_verify_restore_exception(self, mock_verify):
        mock_verify.side_effect = RuntimeError("Process failed")
        with pytest.raises(SystemExit) as exc:
            await verify_restore_cli()
        assert exc.value.code == 1


@pytest.mark.asyncio
class TestRestoreOverrideCLI:
    @patch("tools.backup_tool.cli.settings")
    async def test_restore_override_invalid_env(self, mock_settings):
        mock_settings.ENVIRONMENT = "production"
        with pytest.raises(SystemExit) as exc:
            await run_restore_override_cli("test_pwd")
        assert exc.value.code == 1

    @patch("tools.backup_tool.cli.settings")
    @patch("tools.backup_tool.cli._non_interactive", return_value=True)
    async def test_restore_override_non_interactive(self, mock_non_int, mock_settings):
        mock_settings.ENVIRONMENT = "local"
        with pytest.raises(SystemExit) as exc:
            await run_restore_override_cli("test_pwd")
        assert exc.value.code == 1

    @patch("tools.backup_tool.cli.settings")
    @patch("tools.backup_tool.cli._non_interactive", return_value=False)
    @patch("builtins.input", return_value="wrong_pwd")
    @patch("tools.backup_tool.cli.verify_password", return_value=(False, ""))
    async def test_restore_override_invalid_password(
        self, mock_verify, mock_input, mock_non_int, mock_settings
    ):
        mock_settings.ENVIRONMENT = "local"
        with pytest.raises(SystemExit) as exc:
            await run_restore_override_cli("test_pwd")
        assert exc.value.code == 1

    @patch("tools.backup_tool.cli.settings")
    @patch("tools.backup_tool.cli._non_interactive", return_value=False)
    @patch("builtins.input", return_value="correct_pwd")
    @patch("tools.backup_tool.cli.verify_password", return_value=(True, ""))
    @patch("tools.backup_tool.cli.restore_override", new_callable=AsyncMock)
    async def test_restore_override_success(
        self, mock_restore, mock_verify, mock_input, mock_non_int, mock_settings
    ):
        mock_settings.ENVIRONMENT = "local"
        mock_restore.return_value = True
        await run_restore_override_cli("test_pwd")

    @patch("tools.backup_tool.cli.settings")
    @patch("tools.backup_tool.cli._non_interactive", return_value=False)
    @patch("builtins.input", return_value="correct_pwd")
    @patch("tools.backup_tool.cli.verify_password", return_value=(True, ""))
    @patch("tools.backup_tool.cli.restore_override", new_callable=AsyncMock)
    async def test_restore_override_failure(
        self, mock_restore, mock_verify, mock_input, mock_non_int, mock_settings
    ):
        mock_settings.ENVIRONMENT = "local"
        mock_restore.return_value = False
        with pytest.raises(SystemExit) as exc:
            await run_restore_override_cli("test_pwd")
        assert exc.value.code == 1

    @patch("tools.backup_tool.cli.settings")
    @patch("tools.backup_tool.cli._non_interactive", return_value=False)
    @patch("builtins.input", return_value="correct_pwd")
    @patch("tools.backup_tool.cli.verify_password", return_value=(True, ""))
    @patch("tools.backup_tool.cli.restore_override", new_callable=AsyncMock)
    async def test_restore_override_exception(
        self, mock_restore, mock_verify, mock_input, mock_non_int, mock_settings
    ):
        mock_settings.ENVIRONMENT = "local"
        mock_restore.side_effect = RuntimeError("Process failed")
        with pytest.raises(SystemExit) as exc:
            await run_restore_override_cli("test_pwd")
        assert exc.value.code == 1


class TestMainCLI:
    @patch("tools.backup_tool.cli.settings")
    @patch("sys.argv", ["cli.py", "list"])
    def test_main_no_configured_pwd(self, mock_settings):
        mock_settings.backup.BACKUP_RESTORE_ADMIN_PASSWORD = None
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 1

    @patch("tools.backup_tool.cli.settings")
    @patch("sys.argv", ["cli.py", "list"])
    @patch.dict(os.environ, {}, clear=True)
    def test_main_no_supplied_pwd(self, mock_settings):
        mock_settings.backup.BACKUP_RESTORE_ADMIN_PASSWORD = "config_pwd"
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 1

    @patch("tools.backup_tool.cli.settings")
    @patch("sys.argv", ["cli.py", "--password", "wrong_pwd", "list"])
    @patch("tools.backup_tool.cli.verify_password", return_value=(False, ""))
    def test_main_invalid_password(self, mock_verify_pw, mock_settings):
        mock_settings.backup.BACKUP_RESTORE_ADMIN_PASSWORD = "config_pwd"
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 1

    @patch("tools.backup_tool.cli.settings")
    @patch("sys.argv", ["cli.py", "--password", "correct_pwd", "list"])
    @patch("tools.backup_tool.cli.verify_password", return_value=(True, ""))
    @patch("tools.backup_tool.cli.check_rclone_login")
    def test_main_rclone_login_failed(self, mock_rclone, mock_verify_pw, mock_settings):
        mock_settings.backup.BACKUP_RESTORE_ADMIN_PASSWORD = "config_pwd"

        async def mock_rclone_func():
            return False, "Error message"

        mock_rclone.side_effect = mock_rclone_func
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 1

    @pytest.mark.parametrize(
        "command, target_func_name",
        [
            ("list", "list_backups_cli"),
            ("backup", "run_backup_cli"),
            ("restore", "verify_restore_cli"),
            ("restore-override", "run_restore_override_cli"),
        ],
    )
    @patch("tools.backup_tool.cli.settings")
    @patch("tools.backup_tool.cli.verify_password", return_value=(True, ""))
    @patch("tools.backup_tool.cli.check_rclone_login")
    @patch("tools.backup_tool.cli.asyncio.run")
    def test_main_command_routing(
        self,
        mock_asyncio_run,
        mock_rclone,
        mock_verify_pw,
        mock_settings,
        command,
        target_func_name,
    ):
        mock_settings.backup.BACKUP_RESTORE_ADMIN_PASSWORD = "config_pwd"
        mock_asyncio_run.side_effect = [(True, ""), None]

        with patch("sys.argv", ["cli.py", "--password", "correct_pwd", command]):
            with patch(f"tools.backup_tool.cli.{target_func_name}"):
                main()
                assert mock_asyncio_run.call_count == 2
