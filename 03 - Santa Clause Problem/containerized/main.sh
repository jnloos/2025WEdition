#!/usr/bin/env bash
set -e

cleanup() {
  echo "Stopping containers..."
  docker compose down
}

trap cleanup EXIT INT TERM

docker compose build --no-cache
docker compose up --scale elf=18 --scale reindeer=9
