.PHONY: help \
        docker-server-run docker-server-down \
        backup-restore-docker \
        run-crawlfourai-celery run-crawler-celery run-crawler-update \
        run-k6 run-load-test run-stress-test run-spike-test run-endurance-test

.DEFAULT_GOAL := help


help:
	@echo "Available commands:"
	@echo "  make docker-server-run       - Start Docker services"
	@echo "  make docker-server-down      - Stop Docker services and remove volumes"
	@echo "  make backup-restore-docker   - Run backup restore (CMD=list|backup|restore|restore-override)"
	@echo "  make run-crawlfourai-celery  - Run Crawl4AI Celery task"
	@echo "  make run-crawler-celery      - Run adaptive crawler Celery task"
	@echo "  make run-crawler-update      - Run jobs update Celery task"
	@echo "  make run-k6                  - Run k6 login test script"
	@echo "  make run-load-test           - Run k6 jobs search load test"
	@echo "  make run-stress-test         - Run k6 jobs search stress test"
	@echo "  make run-spike-test          - Run k6 jobs search spike test"
	@echo "  make run-endurance-test      - Run k6 jobs search endurance test"


docker-server-run:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d


docker-server-down:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml down -v


backup-restore-docker:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml exec celery-worker-default \
		python celery/scripts/backup_restore_runner.py "$(CMD)"


run-crawlfourai-celery:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml exec celery-worker-crawler \
		celery -A celery_app call celery_app.run_crawl4ai_task


run-crawler-celery:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml exec celery-worker-crawler \
		celery -A celery_app call celery_app.run_crawler_task


run-crawler-update:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml exec celery-worker-default \
		celery -A celery_app call celery_app.run_jobs_update_task


run-k6:
	k6 run k6_testing/login_test.js

run-load-test:
	k6 run k6_testing/load_test.js

run-stress-test:
	k6 run k6_testing/stress_test.js

run-spike-test:
	k6 run k6_testing/spike_test.js

run-endurance-test:
	k6 run k6_testing/endurance_test.js
