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
    def __init__(self, t_env: StreamTableEnvironment, table_name: str,
                 catalog_name: str, database_name: str,
                 hive_conf_dir: str | None = None,
                 hadoop_conf_dir: str | None = None,
                 hive_version: str | None = None):
        self._t_env = t_env
        self.table_name = table_name
        self.catalog_name = catalog_name
        self.database_name = database_name
        self.hive_conf_dir = hive_conf_dir
        self.hadoop_conf_dir = hadoop_conf_dir
        self.hive_version = hive_version
        self.catalog: Catalog | None = None

    def use(self, name: str, schema_level: SchemaLevel) -> None:
        if schema_level == SchemaLevel.CATALOG:
            self._t_env.use_catalog(name)
        elif schema_level == SchemaLevel.DATABASE:
            self._t_env.use_database(name)
        else:
            raise ValueError(f"Invalid schema level: {schema_level}")

    def get(
        self,
        name: str,
        schema_level: SchemaLevel,
    ) -> Catalog | CatalogDatabase | CatalogBaseTable | None:
        if schema_level not in (SchemaLevel.CATALOG, SchemaLevel.DATABASE, SchemaLevel.TABLE):
            raise ValueError(f"Invalid schema level: {schema_level}")

        try:
            if schema_level == SchemaLevel.CATALOG:
                return self._t_env.get_catalog(name)
            catalog = self._t_env.get_catalog(self._t_env.get_current_catalog())
            if schema_level == SchemaLevel.DATABASE:
                return catalog.get_database(name)
            if schema_level == SchemaLevel.TABLE:
                db = self._t_env.get_current_database()
                return catalog.get_table(ObjectPath(db, name))
        except Exception:
            return None

    def catalog_exists(self) -> bool:
        return self.get(self.catalog_name, SchemaLevel.CATALOG) is not None

    def database_exists(self) -> bool:
        return self.get(self.database_name, SchemaLevel.DATABASE) is not None

    def create_or_replace_catalog(
        self,
        overwrite: bool = False,
        set_as_current: bool = True,
    ) -> Catalog:
        if self.catalog_exists() and not overwrite:
            self.catalog = self.get(self.catalog_name, SchemaLevel.CATALOG)
            return self.catalog

        if self.catalog_exists():
            self._t_env.use_catalog("default_catalog")
            self._t_env.execute_sql(f"DROP CATALOG IF EXISTS {self.catalog_name}")

        self.catalog = HiveCatalog(
            self.catalog_name,
            hive_conf_dir=self.hive_conf_dir,
            hadoop_conf_dir=self.hadoop_conf_dir,
            hive_version=self.hive_version,
        )
        self._t_env.register_catalog(self.catalog_name, self.catalog)

        if set_as_current:
            self.use(self.catalog_name, SchemaLevel.CATALOG)
        return self.catalog

    def create_or_replace_database(
        self,
        properties: dict[str, str] | None = None,
        comment: str | None = None,
        overwrite: bool = False,
        set_as_current: bool = True,
    ) -> CatalogDatabase:
        if self.catalog is None:
            self.catalog = self._t_env.get_catalog(self.catalog_name)

        if self.database_exists():
            if not overwrite:
                return self.catalog.get_database(self.database_name)
            self.catalog.drop_database(self.database_name, True, True)

        db = CatalogDatabase.create_instance(properties or {}, comment)
        self.catalog.create_database(self.database_name, db, True)

        if set_as_current:
            self.use(self.database_name, SchemaLevel.DATABASE)
        return db

    @contextmanager
    def use_hive_dialect(self):
        config = self._t_env.get_config()
        original = config.get_sql_dialect()
        config.set_sql_dialect(SqlDialect.HIVE)
        try:
            yield self._t_env
        finally:
            config.set_sql_dialect(original)