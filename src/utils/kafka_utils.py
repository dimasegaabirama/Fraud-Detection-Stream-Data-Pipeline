from pydantic import BaseModel
from pyflink.datastream.connectors.kafka import (
    DeliveryGuarantee,
    KafkaOffsetsInitializer,
    KafkaRecordSerializationSchema,
    KafkaSink,
    KafkaSource,
)
from pyflink.datastream.formats.json import (
    JsonRowDeserializationSchema,
    JsonRowSerializationSchema,
)

from src.models.endpoint import KafkaEndpoint
from src.utils.flink_utils import FlinkUtils


class KafkaUtils:
    @staticmethod
    def _build_jaas_config(username: str, password: str) -> str:
        return (
            "org.apache.kafka.common.security.plain.PlainLoginModule required "
            f'username="{username}" password="{password}";'
        )

    @classmethod
    def build_source(cls, endpoint: KafkaEndpoint, model: type[BaseModel]) -> KafkaSource:
        deserializer = (
            JsonRowDeserializationSchema.builder()
            .type_info(FlinkUtils.build_row_type_info(model))
            .build()
        )

        source_builder = (
            KafkaSource.builder()
            .set_bootstrap_servers(endpoint.bootstrap_servers)
            .set_topics(endpoint.topic)
            .set_starting_offsets(KafkaOffsetsInitializer.latest())
            .set_property("security.protocol", "SASL_PLAINTEXT")
            .set_property("sasl.mechanism", "PLAIN")
            .set_property(
                "sasl.jaas.config",
                cls._build_jaas_config(
                    endpoint.username,
                    endpoint.password.get_secret_value(),
                ),
            )
            .set_value_only_deserializer(deserializer)
        )
        if endpoint.group_id is not None:
            source_builder.set_group_id(endpoint.group_id)

        return source_builder.build()

    @classmethod
    def build_sink(cls, endpoint: KafkaEndpoint, model: type[BaseModel]) -> KafkaSink:
        serializer = (
            JsonRowSerializationSchema.builder()
            .with_type_info(FlinkUtils.build_row_type_info(model))
            .build()
        )
        record_serializer = (
            KafkaRecordSerializationSchema.builder()
            .set_topic(endpoint.topic)
            .set_value_serialization_schema(serializer)
            .build()
        )

        return (
            KafkaSink.builder()
            .set_bootstrap_servers(endpoint.bootstrap_servers)
            .set_record_serializer(record_serializer)
            .set_delivery_guarantee(DeliveryGuarantee.EXACTLY_ONCE)
            .set_transactional_id_prefix(f"fraud-{endpoint.name}")
            .set_property("security.protocol", "SASL_PLAINTEXT")
            .set_property("sasl.mechanism", "PLAIN")
            .set_property(
                "sasl.jaas.config",
                cls._build_jaas_config(
                    endpoint.username,
                    endpoint.password.get_secret_value(),
                ),
            )
            .build()
        )
