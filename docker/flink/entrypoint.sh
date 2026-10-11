#!/usr/bin/env bash
set -euo pipefail

export HADOOP_CLASSPATH="$(hadoop classpath)"

if [[ -z "${FLINK_HDFS_BASE:-}" ]]; then
  echo "[entrypoint] FLINK_HDFS_BASE is not set. Please set it to the desired HDFS base path."
  exit 1
fi

upload_to_hdfs() {
  echo "[entrypoint] Preparing HDFS folders: ${FLINK_HDFS_BASE}"
  hdfs dfs -mkdir -p "${FLINK_HDFS_BASE}/lib" "${FLINK_HDFS_BASE}/plugins" "${FLINK_HDFS_BASE}/jars" "${FLINK_HDFS_BASE}/checkpoints" "${FLINK_HDFS_BASE}/savepoints"

  hdfs dfs -put -f /opt/flink/lib/*     "${FLINK_HDFS_BASE}/lib/"
  hdfs dfs -put -f /opt/flink/plugins/* "${FLINK_HDFS_BASE}/plugins/"
  hdfs dfs -put -f /opt/jars/*.jar      "${FLINK_HDFS_BASE}/jars/"

  hdfs dfs -chmod -R 755 "${FLINK_HDFS_BASE}"
  echo "[entrypoint] Upload finished."
}

if [[ "${UPLOAD_JARS:-false}" == "true" ]] || ! hdfs dfs -test -d "${FLINK_HDFS_BASE}/lib"; then
  upload_to_hdfs
fi

exec "$@"