#!/usr/bin/env bash

set -Eeuo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
export PROJECT_DIR="${PROJECT_DIR:-$ROOT_DIR}"

if ! docker compose version >/dev/null 2>&1; then
    echo "Error: Docker Compose v2 is required." >&2
    exit 1
fi

if [[ ! -f "$PROJECT_DIR/.env" ]]; then
    echo "Error: missing environment file: $PROJECT_DIR/.env" >&2
    exit 1
fi

if ! docker network inspect hadoop_net >/dev/null 2>&1; then
    echo "Creating external Docker network: hadoop_net"
    docker network create hadoop_net >/dev/null
fi

start_compose_stack() {
    local name="$1"
    local compose_file="$2"

    echo "Starting $name..."
    docker compose \
        --project-directory "$PROJECT_DIR" \
        --file "$PROJECT_DIR/$compose_file" \
        up -d

    sleep 5
}

start_compose_stack "Hadoop" "docker/hadoop/docker-compose.hadoop.yaml"
start_compose_stack "Hive" "docker/hive/docker-compose.hive.yaml"
start_compose_stack "Kafka" "docker/kafka/docker-compose.kafka.yaml"
start_compose_stack "PostgreSQL" "docker/postgres/docker-compose.postgres.yaml"
start_compose_stack "Flink" "docker/flink/docker-compose.flink.yaml"

echo "All Docker Compose stacks started successfully."
