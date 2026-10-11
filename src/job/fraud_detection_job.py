from pyflink.table import StreamTableEnvironment

from src.config.settings import AppSettings
from src.utils.hive_utils import use_hive_catalog


class FraudDetectionJob:
    def __init__(
        self,
        settings: AppSettings,
        t_env: StreamTableEnvironment
    ) -> None:
        self.settings = settings
        self.t_env = t_env

    def preparation_data(self) -> None:
        table_name = "transactions"
        table_path = f"{self.settings.pipeline.catalog}.{self.settings.pipeline.default_database}.{table_name}" 

        with use_hive_catalog("hive_catalog", "fraud_detection", self.t_env):
            self.t_env.execute_sql(f"""
                WITH CTE AS (
                    SELECT DISTINCT * FROM {table_path}
                    
                )
            """
            )