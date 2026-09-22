# AIJMC Environment Variables Reference

This document provides a comprehensive reference for configuration variables defined in [.env.example](../../.env.example). These environment variables configure the FastAPI, Next.js, database, Celery, RabbitMQ, Redis.

## 1. General Environment

| Name | Format | Context |
|---|---|---|
| `PROJECT_NAME` | `string` | Display name of the project. |
| `ENVIRONMENT` | `local` \| `development` \| `staging` \| `production` | System runtime mode. |
| `DOMAIN` | `string` (hostname) | Base domain or host IP where the system is deployed. |
| `FRONTEND_HOST` | `string` (URL) | URL of the frontend user interface. |
| `BACKEND_CORS_ORIGINS` | `JSON array of URLs` | Cross-Origin Resource Sharing example: `["http://localhost:3000","http://localhost:5173"]`. |
| `BACKEND_TRUSTED_HOSTS` | `JSON array of hostnames` | Allowed host headers validated by FastAPI's `TrustedHostMiddleware` to prevent HTTP Host Header poisoning attacks. |

## 2. Authentication and Security

| Name | Format | Context |
|---|---|---|
| `SECRET_KEY` | `string` (cryptographic hex/base64) | Cryptographic secret key used to sign and verify JWT and encrypted sessions. Must be generated securely using `make generate-secret`. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `integer` | Lifespan of JWT authentication access tokens in minutes. |
| `EMAIL_RESET_TOKEN_EXPIRE_HOURS` | `integer` | Validity period in hours for password-reset verification tokens sent to user email addresses. |
| `FIRST_SUPERUSER` | `string` (Email) | Email address for the initial root administrator account. |
| `FIRST_SUPERUSER_PASSWORD` | `string` | Password assigned to the initial superuser. |
| `EMAIL_TEST_USER` | `string` (Email) | Dummy email recipient for testing. |

## 3. AI Agent and Embedding

| Name | Format | Context |
|---|---|---|
| `GEMINI_API_KEY` | `JSON array of strings` | Google Gemini API keys used by backend agents and Celery workers. |


## 4. Database Configuration
| Name | Format | Context |
|---|---|---|
| `POSTGRES_SERVER` | `string` (hostname/IP) | Network hostname or Docker service name for the PostgreSQL instance. |
| `POSTGRES_PORT` | `integer` | Port on which the PostgreSQL database server listens. |
| `POSTGRES_USER` | `string` | Database user account credentials used by SQLAlchemy and Alembic migrations. |
| `POSTGRES_PASSWORD` | `string` | Password authenticating the database user. |
| `POSTGRES_DB` | `string` | Target PostgreSQL database name where tables, pgvector extensions, and migrations are applied. |

## 5. In-Memory Cache and Message Broker

| Name | Format | Context |
|---|---|---|
| `REDIS_SERVER` | `string` (hostname/IP) | Hostname or Docker service name for the Redis server. |
| `REDIS_PORT` | `integer` | Port on which Redis accepts connections. Used for caching, rate limiting, and temporary state storage. |
| `CUSTOM_REDIS_URL` | `string` | Explicit Redis connection URL |
| `RABBITMQ_SERVER` | `string` (hostname/IP) | Hostname or Docker service name for the RabbitMQ AMQP broker. |
| `RABBITMQ_PORT` | `integer` | Port for RabbitMQ AMQP protocol communication. |
| `RABBITMQ_USER` | `string` | AMQP authentication user for Celery task queuing. |
| `RABBITMQ_PASSWORD` | `string` | AMQP authentication password for Celery task queuing. |
| `CUSTOM_RABBITMQ_URL` | `string` | Explicit AMQP connection URL. |

## 6. Celery Asynchronous Workers

| Name | Format | Context |
|---|---|---|
| `CELERY_WORKER_MAX_TASKS_PER_CHILD` | `integer` | Maximum tasks a Celery worker child process executes before being terminated and replaced with a fresh process. |
| `CRAWLER_MAX_CONCURRENCY` | `integer` | Maximum concurrent browser pages or scraping sessions processed simultaneously by the crawler worker. |
| `SITE_CRAWL_TIMEOUT_SECONDS` | `integer` | Global timeout in seconds allocated for a single job board scraping run before the task is aborted. |
| `CRAWLER_MAX_REQUESTS_PER_CRAWL` | `integer` | Safety cap on the total count of web requests or pages fetched during an individual crawl execution. |
| `CRAWLER_MAX_REQUEST_RETRIES` | `integer` | Maximum number of retry attempts for failed network requests, page load timeouts, or transient HTTP errors. |
| `CRAWLER_REQUEST_HANDLER_TIMEOUT_SECONDS` | `integer` | Maximum seconds allowed for an individual HTTP request or page handler execution before timing out. |
| `CRAWLER_UPDATE_BATCH_SIZE` | `integer` | Number of open jobs retrieved and evaluated in parallel per batch during the scheduled job status update workflow. |
| `CRAWLER_UPDATE_MIN_DELAY_SECONDS` | `float` | Minimum random jitter delay between consecutive job URL status verification checks. |
| `CRAWLER_UPDATE_MAX_DELAY_SECONDS` | `float` | Maximum random jitter delay between consecutive job URL status verification checks. |
| `CRAWLER_MIN_DELAY_SECONDS` | `float` | Minimum random jitter delay between consecutive scraping requests to avoid triggering anti-bot rate limits. |
| `CRAWLER_MAX_DELAY_SECONDS` | `float` | Maximum random jitter delay between consecutive scraping requests. |
| `CRAWLER_BROWSER_TYPE` | `chromium` \| `firefox` \| `webkit` | Underlying browser engine launched by Playwright and Crawl4AI. |
| `CRAWLER_HEADLESS` | `boolean` | When `true`, runs the browser in headless mode without a graphical user interface. Set to `false` during local development to visually debug scraping scripts. |

## 7. SMTP

| Name | Format | Context |
|---|---|---|
| `SMTP_TLS` | `boolean` | Enables STARTTLS encryption when connecting to the SMTP server. |
| `SMTP_SSL` | `boolean` | Enables direct SSL/TLS encryption. Mutually exclusive with STARTTLS. |
| `SMTP_PORT` | `integer` | Port number used to connect to the outbound mail relay. |
| `SMTP_HOST` | `string` | Fully qualified domain name or IP of the outbound SMTP relay (e.g., `smtp.gmail.com`). |
| `SMTP_USER` | `string` | Username or account email for authenticating with the SMTP server. |
| `SMTP_PASSWORD` | `string` | Password or application-specific token for SMTP authentication. |
| `EMAILS_FROM_EMAIL` | `string` | Sender address placed in the `From:` header of outgoing emails. |
| `EMAILS_FROM_NAME` | `string` | Display name attached to outgoing system emails (defaults to `PROJECT_NAME` if omitted). |

## 8. Automated Backup

| Name | Format | Context |
|---|---|---|
| `BACKUP_RESTORE_ADMIN_PASSWORD` | `string` | Security passphrase required to execute database backup and restoration routines. |
| `RCLONE_REMOTE_PATH` | `string` | Rclone remote destination identifier and folder path for synchronizing snapshot archives. |
| `BACKUP_MAX_STACKS` | `integer` | Maximum number of retained backup snapshot archives before older archives are automatically pruned. |

## 9. Docker Container Images

| Name | Format | Context |
|---|---|---|
| `DOCKER_IMAGE_BACKEND` | `string` | Image repository tag for building and running the FastAPI backend service. |
| `DOCKER_IMAGE_FRONTEND` | `string` | Image repository tag for building and running the Next.js frontend service. |
| `DOCKER_IMAGE_CELERY` | `string` | Image repository tag for building and running the Celery asynchronous worker containers. |
| `GITHUB_TOKEN` | `string`| GitHub Personal Access Token used for automated workflows, release tagging, and automated issue creation (`test_case_report.py`). |
| `NGROK_AUTHTOKEN` | `string` | Ngrok authentication token used when exposing local development endpoints to public webhooks and mobile device testing. |
