#!/usr/bin/env bash

set -Eeuo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
export PROJECT_DIR="${PROJECT_DIR:-$ROOT_DIR}"

if ! docker compose version >/dev/null 2>&1; then
    echo "Error: Docker Compose v2 is required." >&2
    exit 1
fi

stop_compose_stack() {
    local name="$1"
    local compose_file="$2"

    echo "Stopping $name..."
    docker compose \
        --project-directory "$PROJECT_DIR" \
        --file "$PROJECT_DIR/$compose_file" \
        down -v
}

stop_compose_stack "Flink" "docker/flink/docker-compose.flink.yaml"
stop_compose_stack "PostgreSQL" "docker/postgres/docker-compose.postgres.yaml"
stop_compose_stack "Kafka" "docker/kafka/docker-compose.kafka.yaml"
stop_compose_stack "Hive" "docker/hive/docker-compose.hive.yaml"
stop_compose_stack "Hadoop" "docker/hadoop/docker-compose.hadoop.yaml"

echo "All Docker Compose stacks stopped successfully."
