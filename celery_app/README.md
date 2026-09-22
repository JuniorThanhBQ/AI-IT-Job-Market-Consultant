# AIJMC Celery Distributed Task Queue

AIJMC's asynchronous background task system, featuring four primary tasks: data mining, recruitment news updates, periodic backups, and task notifications.

## Registered tasks

The app registers the following tasks:

- `run_crawler_task` - executes the adaptive crawler workflow once per day at 00:00
- `run_crawl4ai_task` - executes the crawl4ai crawler once per day at 02:30
- `run_jobs_update_task` - refreshes job data every 2 hours
- `run_database_backup_task` - runs the database backup pipeline every 3 hours

The email reporting tools are imported into the Celery app so their tasks are available to the worker.

## Runtime configuration

- Broker: RabbitMQ via `settings.rabbitmq.RABBITMQ_URL`
- Result backend: RPC
- Timezone: `Asia/Ho_Chi_Minh`
- Beat schedule file: temporary directory location managed by Docker volume
- Worker concurrency: derived from the startup helper and falls back to CPU count

## Makefile supports:

Run backup restore Docker (requires CMD=[list|backup|restore|restore-override])":
```bash
make backup-restore-docker
```

Regenerate or sync rclone.conf from local system to celery_app:
```bash
make remake-rclone-config
```
*(If your token expires or returns `invalid_grant`, reconnect first on your host machine via `rclone config reconnect gdrive:` then run `make remake-rclone-config`)*

Run Celery adaptive crawler task manually in Docker container:
```bash
make run-crawler-celery
```

Run Celery jobs update task manually in Docker container:
```bash
make run-crawler-update
```

Run Celery crawl4ai task manually in Docker container:
```bash
make run-crawlfourai-celery
```

## Celery folder structure

```text
celery_app/
├── Dockerfile
├── README.md
├── celery_app.py
├── pyproject.toml
├── rclone.conf
├── rclone.conf.example
├── scripts/
│   ├── backup_restore_runner.py
│   ├── get_concurrency.py
│   └── start_worker.sh
├── tests/
├── tools/
│   ├── adaptive_crawler/
│   │   ├── config_crawler.py
│   │   ├── crawler.py
│   │   ├── helpers.py
│   │   ├── crawler_adapter/
│   │   │   ├── base_adapter.py
│   │   │   ├── itjobs_adapter.py
│   │   │   ├── itviec_adapter.py
│   │   │   ├── topdev_adapter.py
│   │   │   └── vietnamworks_adapter.py
│   │   ├── crawler_factory/
│   │   │   ├── base_factory.py
│   │   │   ├── itjobs_factory/
│   │   │   ├── itviec_factory/
│   │   │   ├── topdev_factory/
│   │   │   └── vietnamworks_factory/
│   │   └── crawler_repository/
│   │       ├── company_repository.py
│   │       └── job_repository.py
│   ├── backup_tool/
│   │   ├── backup_helpers.py
│   │   ├── backup_services.py
│   │   └── db_transactions.py
│   ├── crawl4ai_crawler/
│   │   ├── adapter.py
│   │   ├── config_crawler.py
│   │   └── crawler.py
│   ├── crawler_update_tool/
│   │   ├── job_updater.py
│   │   └── updater_services.py
│   └── email_report_tool/
│       ├── email_templates.html
│       └── tasks.py
└── utils/
    ├── backup_utils.py
    ├── itviec_utils.py
    ├── text_parser.py
    └── topdev_utils.py
```
