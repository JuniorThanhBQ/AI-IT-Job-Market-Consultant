#!/bin/bash
set -e

echo "Waiting for stack startup..."
sleep 15

docker compose ps

backend_status=$(docker inspect --format='{{json .State.Health.Status}}' $(docker compose ps -q backend))
echo "Backend health status: $backend_status"
if [ "$backend_status" != "\"healthy\"" ]; then
  echo "Error: Backend container is unhealthy!"
  docker compose logs backend
  exit 1
fi

frontend_status=$(docker inspect --format='{{json .State.Health.Status}}' $(docker compose ps -q frontend))
echo "Frontend health status: $frontend_status"
if [ "$frontend_status" != "\"healthy\"" ]; then
  echo "Error: Frontend container is unhealthy!"
  docker compose logs frontend
  exit 1
fi

echo "All containers are healthy!"
