#!/bin/bash
set -e

cp .env.example .env

sed -i 's/DOCKER_IMAGE_BACKEND=.*/DOCKER_IMAGE_BACKEND=ai-it-job-market-consultant-backend/g' .env
sed -i 's/DOCKER_IMAGE_FRONTEND=.*/DOCKER_IMAGE_FRONTEND=ai-it-job-market-consultant-frontend/g' .env
sed -i 's/DOCKER_IMAGE_CELERY=.*/DOCKER_IMAGE_CELERY=ai-it-job-market-consultant-celery/g' .env
