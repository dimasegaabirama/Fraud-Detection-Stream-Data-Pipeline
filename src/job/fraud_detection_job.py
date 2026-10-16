from pyflink.table import StreamTableEnvironment, udf
from pyflink.table.types import DataTypes

from src.config.settings import AppSettings
from src.rules import AmountRules, VelocityRules
from src.udf.base_threshold_udf import BaseThresholdUDF


class FraudDetectionJob:
    def __init__(self, settings: AppSettings, t_env: StreamTableEnvironment) -> None:
        self.settings = settings
        self.t_env = t_env

    def preparing_data(self) -> None:
        table_name = "transactions"
        self.t_env.execute_sql(f"""
            WITH cleaned_transactions AS (
                SELECT
                    transaction_id,
                    user_id,
                    COALESCE(amount, 0.0) AS amount,
                    TRIM(UPPER(currency)) AS currency,
                    TRIM(UPPER(status)) AS status,
                    TRIM(UPPER(transaction_type)) AS transaction_type,
                    TRIM(UPPER(direction)) AS direction,
                    ip_address,
                    TRIM(UPPER(device_type)) AS device_type,
                    latitude,
                    longitude,
                    `timestamp`,
                    DAY(`timestamp`) AS `day`,
                    MONTH(`timestamp`) AS `month`,
                    YEAR(`timestamp`) AS `year`
                FROM {table_name}
                WHERE `timestamp` IS NOT NULL
            )

            CREATE TEMPORARY VIEW cleaned_transactions AS
            SELECT 
                window_start, 
                window_end,
                transaction_id,
                user_id,
                segment,
                direction,
                amount,
                currency,
                status,
                transaction_type,
                ip_address,
                device_type,
                longitude,
                latitude,
                `timestamp`,
                `day`,
                `month`,
                `year`
                ROW_NUMBER() OVER (
                    PARTITION BY window_start, window_end, transaction_id
                    ORDER BY `timestamp` ASC) AS rn
            FROM TABLE(
                HOP(
                    TABLE cleaned_transactions,
                    DESCRIPTOR(`timestamp`),
                    INTERVAL '5' MINUTES,
                    INTERVAL '10' MINUTES
                )
            WHERE rn = 1
        """)

        return self.t_env

    def velocity_fraud_detection(self, cleaned_table) -> None:

        rules = VelocityRules

        self.t_env.create_temporary_function(
            "velocity_fraud_detection", udf(BaseThresholdUDF(rules), result_type=DataTypes.INT())
        )

        self.t_env.execute_sql(f"""
            CREATE TEMPORARY VIEW velocity_aggregated AS
                SELECT
                    window_start,
                    window_end,
                    user_id,
                    segment,
                    direction,
                    COUNT(transaction_id) AS transaction_count,
                    velocity_fraud_detection(segment, direction, transaction_count) AS score,
                FROM {cleaned_table}
                GROUP BY window_start, window_end, user_id, segment, direction

            INSERT INTO fraud_detection_results
            SELECT 
                user_id, 
                segment, 
                direction, 
                score, 
                "velocity" AS fraud_type 
            FROM velocity_aggregated
        """)

        return self.t_env

    def amount_fraud_detection(self, cleaned_table) -> None:

        rules = AmountRules

        self.t_env.create_temporary_function(
            "amount_fraud_detection", udf(BaseThresholdUDF(rules), result_type=DataTypes.INT())
        )

        self.t_env.execute_sql(f"""
            CREATE TEMPORARY VIEW amount_aggregated AS
                SELECT
                    window_start,
                    window_end,
                    user_id,
                    segment,
                    direction,
                    SUM(amount) AS total_amount,
                    AVG(amount) OVER(
                        PARTITION BY user_id, segment, direction
                        ORDER BY window_start
                        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                    ) AS avg_amount,
                    amount_fraud_detection(segment, direction, avg_amount) AS score
                FROM {cleaned_table}
                GROUP BY window_start, window_end, user_id, segment, direction

            INSERT INTO fraud_detection_results
            SELECT 
                user_id, 
                segment, 
                direction, 
                score, 
                "amount" AS fraud_type
            FROM amount_aggregated

        """)

        return self.t_env
