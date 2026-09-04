from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from tools.backup_tool.db_transactions import (
    _get_pg_env,
    restore_override,
    verify_backup,
)


class TestHelpers:
    @patch("tools.backup_tool.db_transactions.settings")
    @patch("os.environ.copy", return_value={"EXISTING": "1"})
    def test_get_pg_env_with_pwd(self, mock_env_copy, mock_settings):
        mock_settings.database.POSTGRES_PASSWORD = "test_pwd"
        env = _get_pg_env()
        assert env["PGPASSWORD"] == "test_pwd"
        assert env["EXISTING"] == "1"


@pytest.mark.asyncio
class TestVerifyBackup:
    @patch(
        "tools.backup_tool.db_transactions._drop_db_if_exists", new_callable=AsyncMock
    )
    @patch("tools.backup_tool.db_transactions._create_db", new_callable=AsyncMock)
    @patch("tools.backup_tool.db_transactions._restore_dump", new_callable=AsyncMock)
    async def test_verify_backup_success(self, mock_restore, mock_create, mock_drop):
        mock_drop.return_value = (0, "", "")
        mock_create.return_value = (0, "", "")
        mock_restore.return_value = (0, "", "")

        res = await verify_backup(Path("dump"))
        assert res is True
        assert mock_drop.call_count == 2
        mock_create.assert_called_once()
        mock_restore.assert_called_once()

    @patch(
        "tools.backup_tool.db_transactions._drop_db_if_exists", new_callable=AsyncMock
    )
    @patch("tools.backup_tool.db_transactions._create_db", new_callable=AsyncMock)
    async def test_verify_backup_create_fail(self, mock_create, mock_drop):
        mock_drop.return_value = (0, "", "")
        mock_create.return_value = (1, "", "error")

        res = await verify_backup(Path("dump"))
        assert res is False

    @patch(
        "tools.backup_tool.db_transactions._drop_db_if_exists", new_callable=AsyncMock
    )
    @patch("tools.backup_tool.db_transactions._create_db", new_callable=AsyncMock)
    @patch("tools.backup_tool.db_transactions._restore_dump", new_callable=AsyncMock)
    async def test_verify_backup_restore_fail(
        self, mock_restore, mock_create, mock_drop
    ):
        mock_drop.return_value = (0, "", "")
        mock_create.return_value = (0, "", "")
        mock_restore.return_value = (1, "", "error")

        res = await verify_backup(Path("dump"))
        assert res is False


@pytest.mark.asyncio
class TestRestoreOverride:
    @patch("tools.backup_tool.db_transactions._check_db_exists", new_callable=AsyncMock)
    @patch("tools.backup_tool.db_transactions._create_db", new_callable=AsyncMock)
    @patch("tools.backup_tool.db_transactions._restore_dump", new_callable=AsyncMock)
    async def test_restore_no_existing_db_success(
        self, mock_restore, mock_create, mock_check
    ):
        mock_check.return_value = False
        mock_create.return_value = (0, "", "")
        mock_restore.return_value = (0, "", "")

        res = await restore_override(Path("dump"))
        assert res is True

    @patch("tools.backup_tool.db_transactions._check_db_exists", new_callable=AsyncMock)
    @patch(
        "tools.backup_tool.db_transactions._disallow_connections",
        new_callable=AsyncMock,
    )
    @patch(
        "tools.backup_tool.db_transactions._terminate_connections",
        new_callable=AsyncMock,
    )
    @patch(
        "tools.backup_tool.db_transactions._drop_db_if_exists", new_callable=AsyncMock
    )
    @patch("tools.backup_tool.db_transactions._rename_db", new_callable=AsyncMock)
    @patch(
        "tools.backup_tool.db_transactions._allow_connections", new_callable=AsyncMock
    )
    async def test_restore_rename_fails_rollback(
        self, mock_allow, mock_rename, mock_drop, mock_term, mock_disallow, mock_check
    ):
        mock_check.return_value = True
        mock_drop.return_value = (0, "", "")
        mock_rename.return_value = (1, "", "rename error")

        res = await restore_override(Path("dump"))
        assert res is False
        mock_allow.assert_called_once()

    @patch("tools.backup_tool.db_transactions._check_db_exists", new_callable=AsyncMock)
    @patch(
        "tools.backup_tool.db_transactions._disallow_connections",
        new_callable=AsyncMock,
    )
    @patch(
        "tools.backup_tool.db_transactions._terminate_connections",
        new_callable=AsyncMock,
    )
    @patch(
        "tools.backup_tool.db_transactions._drop_db_if_exists", new_callable=AsyncMock
    )
    @patch("tools.backup_tool.db_transactions._rename_db", new_callable=AsyncMock)
    @patch("tools.backup_tool.db_transactions._create_db", new_callable=AsyncMock)
    @patch("tools.backup_tool.db_transactions._restore_dump", new_callable=AsyncMock)
    @patch(
        "tools.backup_tool.db_transactions._allow_connections", new_callable=AsyncMock
    )
    async def test_restore_pg_restore_fails_rollback(
        self,
        mock_allow,
        mock_restore,
        mock_create,
        mock_rename,
        mock_drop,
        mock_term,
        mock_disallow,
        mock_check,
    ):
        mock_check.return_value = True
        mock_drop.return_value = (0, "", "")
        mock_rename.return_value = (0, "", "")
        mock_create.return_value = (0, "", "")
        mock_restore.return_value = (1, "", "restore error")
        mock_allow.return_value = (0, "", "")

        res = await restore_override(Path("dump"))
        assert res is False
        assert mock_term.call_count == 3
        assert mock_rename.call_count == 2
        mock_allow.assert_called_once()

    @patch("tools.backup_tool.db_transactions._check_db_exists", new_callable=AsyncMock)
    @patch(
        "tools.backup_tool.db_transactions._disallow_connections",
        new_callable=AsyncMock,
    )
    @patch(
        "tools.backup_tool.db_transactions._terminate_connections",
        new_callable=AsyncMock,
    )
    @patch(
        "tools.backup_tool.db_transactions._drop_db_if_exists", new_callable=AsyncMock
    )
    @patch("tools.backup_tool.db_transactions._rename_db", new_callable=AsyncMock)
    @patch("tools.backup_tool.db_transactions._create_db", new_callable=AsyncMock)
    @patch("tools.backup_tool.db_transactions._restore_dump", new_callable=AsyncMock)
    @patch(
        "tools.backup_tool.db_transactions._allow_connections", new_callable=AsyncMock
    )
    async def test_restore_full_success(
        self,
        mock_allow,
        mock_restore,
        mock_create,
        mock_rename,
        mock_drop,
        mock_term,
        mock_disallow,
        mock_check,
    ):
        mock_check.return_value = True
        mock_drop.return_value = (0, "", "")
        mock_rename.return_value = (0, "", "")
        mock_create.return_value = (0, "", "")
        mock_restore.return_value = (0, "", "")
        mock_allow.return_value = (0, "", "")

        res = await restore_override(Path("dump"))
        assert res is True
        assert mock_drop.call_count == 2
