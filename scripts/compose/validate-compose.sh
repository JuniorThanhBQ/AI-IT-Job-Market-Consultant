#!/bin/bash
set -euo pipefail

echo "Validating Docker Compose syntax..."

CLEANUP_ENV=false
if [ ! -f .env ] && [ -f .env.example ]; then
  echo "Creating temporary .env from .env.example for validation..."
  cp .env.example .env
  CLEANUP_ENV=true
fi

cleanup() {
  if [ "$CLEANUP_ENV" = true ]; then
    echo "Cleaning up temporary .env file..."
    rm -f .env
  fi
}
trap cleanup EXIT

for file in $COMPOSE_FILES; do
  echo "Checking syntax for $file..."
  if ! docker compose -f "$file" config --quiet; then
    echo "::error file=$file::Syntax error in file $file"
    exit 1
  fi
  echo "$file syntax is valid."
done
