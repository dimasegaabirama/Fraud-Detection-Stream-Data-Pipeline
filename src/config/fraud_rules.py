KAFKA_TOPIC = "transactions"

HADOOP_CONF_DIR = "/etc/hadoop/conf"

HIVE_CONF_DIR = "/opt/hive/conf"
HIVE_WAREHOUSE_DIR = "/opt/hive/warehouse"

PIPELINE_CATALOG="hive_catalog"
PIPELINE_DEFAULT_DATABASE="fraud_detection"
PIPELINE_CHECKPOINT_DIR = "/opt/flink/checkpoints"
PIPELINE_SAVEPOINT_DIR = "/opt/flink/savepoints"

WINDOW_MINUTES = 5
WINDOW_SLIDE_MINUTES = 1