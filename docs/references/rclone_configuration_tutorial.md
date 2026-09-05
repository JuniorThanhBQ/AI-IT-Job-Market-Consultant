# Rclone Configuration & Token Renewal Tutorial

This document guides you on how to set up, authenticate, and renew Google Drive authorization for database backups in AIJMC.

## 1. Why `invalid_grant` Happens

When listing, uploading, or restoring backups, you might encounter:

```text
Failed to create file system for "gdrive:": couldn't find root directory ID: ... oauth2: cannot fetch token: 400 Bad Request
Response: {
  "error": "invalid_grant",
  "error_description": "Bad Request"
}
```

### Root Causes
1. **Google Cloud OAuth Consent Screen in Testing Mode**:
   By default, Google Cloud projects created in Testing status issue OAuth refresh tokens that expire strictly after **7 days**.
2. **Revoked Credentials**:
   If user permissions or passwords change on the Google account, or the app credential is regenerated in Google Cloud Console, previous tokens are invalidated.
3. **Unused Tokens**:
   Google automatically expires OAuth refresh tokens if unused for 6 continuous months.

### How to Prevent Weekly Expiration
- In [Google Cloud Console](https://console.cloud.google.com/):
  1. Navigate to **APIs & Services** > **OAuth consent screen**.
  2. Under **Publishing status**, click **PUBLISH APP** to switch from "Testing" to "In production".
  3. While unverified production apps will show a one-time "Google hasn't verified this app" warning when authorizing in your browser, their OAuth refresh tokens **do not expire after 7 days**.

## 2. Installing Rclone on Your Host Computer

To configure Google Drive OAuth with your web browser, install `rclone` on your host operating system:

### Windows
Using WinGet:
```powershell
winget install Rclone.Rclone
```
Or download the pre-compiled zip from [rclone.org/downloads](https://rclone.org/downloads/) and add `rclone.exe` to your `PATH`.

### macOS
Using Homebrew:
```bash
brew install rclone
```

### Linux (Ubuntu / Debian)
```bash
sudo apt update && sudo apt install -y rclone
```
Or via official install script:
```bash
sudo -v ; curl https://rclone.org/install.sh | sudo bash
```

Verify installation:
```bash
rclone version
```

## 3. Configuring Google Drive with Rclone

### Step 1: Create Google Cloud OAuth Credentials
1. Open [Google Cloud Console](https://console.cloud.google.com/).
2. Enable the **Google Drive API**.
3. Go to **APIs & Services** > **Credentials**.
4. Click **Create Credentials** > **OAuth client ID**.
5. Select **Application type**: **Desktop app**.
6. Note down your **Client ID** and **Client Secret**.

### Step 2: Run `rclone config`
Run the interactive setup wizard:
```bash
rclone config
```

Follow the prompts:
1. `n) New remote`
2. `name> gdrive` *(Important: The project uses remote name `gdrive`)*
3. `Storage> drive` *(Choose Google Drive, usually number 18 or by name `drive`)*
4. `client_id>` *(Paste your Client ID)*
5. `client_secret>` *(Paste your Client Secret)*
6. `scope> 1` *(Full access all files, or `drive`)*
7. `root_folder_id>` *(Leave blank for root, or specify target backup folder ID)*
8. `service_account_file>` *(Leave blank)*
9. `Edit advanced config? (y/n)> n`
10. `Use web browser to automatically authenticate with remote? (y/n)> y`
    - A browser tab will open automatically.
    - Log in to your Google account and click **Allow** (or **Advanced > Proceed** if in testing/unverified mode).
11. `Configure this as a Shared Drive (Team Drive)? (y/n)> n`
12. `y) Yes this is OK`
13. `q) Quit config`

### Step 3: Verify the Connection
Test your remote access:
```bash
rclone lsd gdrive:
```
If your folders appear, your authentication is active and working.

Once authorized locally, you need the configuration placed inside the project so Celery workers and backup runners can use it.

### Fast Token Renewal
If you already configured Rclone previously on your machine and only need to refresh an expired token:
1. Reconnect directly from your terminal:
   ```bash
   rclone config reconnect gdrive:
   ```
2. Press `y` to authenticate in the opened browser tab.
3. Sync the new token into the project:
   ```bash
   make remake-rclone-config
   ```

### Automated Setup
Simply run:
```bash
make remake-rclone-config
```

What this command does:
1. Automatically detects the system Rclone configuration path:
   - Windows: `%APPDATA%\rclone\rclone.conf`
   - Linux/macOS: `~/.config/rclone/rclone.conf`
2. Validates the `[gdrive]` section and OAuth tokens.
3. Automatically syncs and copies the configuration to:
   - `celery_app/rclone.conf`
   - `deployment/rclone.conf`

### Interactive Fallback
If you are working on a remote machine or container without host `rclone` installed, you can run:
```bash
uv run python scripts/remake_rclone_config.py --interactive
```
The script will prompt you for `client_id`, `client_secret`, and `token` JSON directly and write the files cleanly.

---

## 5. Verifying in AIJMC

After updating the config, verify that the backup pipeline can list backups:

### Locally
```bash
make backup-restore CMD=list
```

### In Docker Container
```bash
make backup-restore-docker CMD=list
```

When successful, you will see the formatted backup table:
```text
Filename                                           | Size (MB)    | Modified Time
---------------------------------------------------------------------------------------------
db_backup_20260812_133057.dump.gz                  | 14.01        | 2026-08-12 13:31:15 UTC
db_backup_20260812_114416.dump.gz                  | 14.00        | 2026-08-12 11:44:31 UTC
db_backup_20260811_101358.dump.gz                  | 13.00        | 2026-08-11 10:14:15 UTC
db_backup_20260811_090954.dump.gz                  | 13.14        | 2026-08-11 09:10:01 UTC
db_backup_20260811_090653.dump.gz                  | 13.14        | 2026-08-11 09:06:59 UTC
============================================================
ACTION: LIST
STATUS: SUCCESS
DETAILS: Operation 'list' finished.
============================================================
```
