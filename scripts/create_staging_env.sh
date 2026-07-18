#!/bin/bash
set -e

cp .env.example .env

sed -i 's/DOCKER_IMAGE_BACKEND=not_available/DOCKER_IMAGE_BACKEND=ai-it-job-market-consultant-backend/g' .env
sed -i 's/DOCKER_IMAGE_FRONTEND=not_available/DOCKER_IMAGE_FRONTEND=ai-it-job-market-consultant-frontend/g' .env
