from contextlib import contextmanager

from pyflink.table import StreamTableEnvironment
from pyflink.table.catalog import (
    Catalog,
    CatalogBaseTable,
    CatalogDatabase,
    HiveCatalog,
    ObjectPath,
)
from pyflink.table.sql_dialect import SqlDialect

from src.models.enums import SchemaLevel


class HiveUtils:
    @staticmethod
    def use(
        t_env: StreamTableEnvironment,
        name: str,
        schema_level: SchemaLevel,
    ) -> None:
        if schema_level == SchemaLevel.CATALOG:
            t_env.use_catalog(name)
        elif schema_level == SchemaLevel.DATABASE:
            t_env.use_database(name)
        else:
            raise ValueError(f"Invalid schema level: {schema_level}")

    @staticmethod
    def get(
        t_env: StreamTableEnvironment,
        name: str,
        schema_level: SchemaLevel,
    ) -> Catalog | CatalogDatabase | CatalogBaseTable | None:
        if schema_level not in (
            SchemaLevel.CATALOG,
            SchemaLevel.DATABASE,
            SchemaLevel.TABLE,
        ):
            raise ValueError(f"Invalid schema level: {schema_level}")

        try:
            if schema_level == SchemaLevel.CATALOG:
                return t_env.get_catalog(name)
            catalog = t_env.get_catalog(t_env.get_current_catalog())
            if schema_level == SchemaLevel.DATABASE:
                return catalog.get_database(name)
            return catalog.get_table(ObjectPath(t_env.get_current_database(), name))
        except Exception:
            return None

    @classmethod
    def create_or_replace_catalog(
        cls,
        t_env: StreamTableEnvironment,
        catalog_name: str,
        hive_conf_dir: str | None = None,
        hadoop_conf_dir: str | None = None,
        hive_version: str | None = None,
        overwrite: bool = False,
        set_as_current: bool = True,
    ) -> Catalog:
        existing = cls.get(t_env, catalog_name, SchemaLevel.CATALOG)
        if existing is not None and not overwrite:
            return existing

        if existing is not None:
            t_env.use_catalog("default_catalog")
            t_env.execute_sql(f"DROP CATALOG IF EXISTS {catalog_name}")

        catalog = HiveCatalog(
            catalog_name,
            hive_conf_dir=hive_conf_dir,
            hadoop_conf_dir=hadoop_conf_dir,
            hive_version=hive_version,
        )
        t_env.register_catalog(catalog_name, catalog)

        if set_as_current:
            cls.use(t_env, catalog_name, SchemaLevel.CATALOG)
        return catalog

    @classmethod
    def create_or_replace_database(
        cls,
        t_env: StreamTableEnvironment,
        catalog_name: str,
        database_name: str,
        catalog: Catalog | None = None,
        properties: dict[str, str] | None = None,
        comment: str | None = None,
        overwrite: bool = False,
        set_as_current: bool = True,
    ) -> CatalogDatabase:
        if catalog is None:
            catalog = t_env.get_catalog(catalog_name)

        existing = cls.get(t_env, database_name, SchemaLevel.DATABASE)
        if existing is not None:
            if not overwrite:
                return existing
            catalog.drop_database(database_name, True, True)

        database = CatalogDatabase.create_instance(properties or {}, comment)
        catalog.create_database(database_name, database, True)

        if set_as_current:
            cls.use(t_env, database_name, SchemaLevel.DATABASE)
        return database

    @staticmethod
    @contextmanager
    def use_hive_dialect(
        t_env: StreamTableEnvironment,
    ):
        config = t_env.get_config()
        original = config.get_sql_dialect()
        config.set_sql_dialect(SqlDialect.HIVE)
        try:
            yield t_env
        finally:
            config.set_sql_dialect(original)
