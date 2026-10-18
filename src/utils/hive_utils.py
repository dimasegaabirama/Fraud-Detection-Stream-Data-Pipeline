from typing_extensions import Optional, Dict
from contextlib import contextmanager

from pyflink.table import StreamTableEnvironment
from pyflink.table.catalog import Catalog, CatalogDatabase, HiveCatalog
from pyflink.table.sql_dialect import SqlDialect


class HiveUtils:

    def __init__(
        self,
        t_env: StreamTableEnvironment,
        catalog_name: str,
        hive_conf_dir: Optional[str] = None,
        hadoop_conf_dir: Optional[str] = None,
        hive_version: Optional[str] = None,
    ):
        self.t_env = t_env
        self.catalog_name = catalog_name
        self.hive_conf_dir = hive_conf_dir
        self.hadoop_conf_dir = hadoop_conf_dir
        self.hive_version = hive_version

    @property
    def catalog(self) -> Catalog:
        return self.t_env.get_catalog(self.catalog_name)

    def catalog_exists(self) -> bool:
        return self.catalog_name in self.t_env.list_catalogs()

    def create_or_replace_catalog(self, overwrite: bool = False) -> Catalog:
        exists = self.catalog_exists()

        if exists and overwrite:
            self.t_env.use_catalog("default_catalog")
            self.t_env.execute_sql(f"DROP CATALOG `{self.catalog_name}`")
            exists = False

        if not exists:
            self.t_env.register_catalog(
                self.catalog_name,
                HiveCatalog(
                    self.catalog_name,
                    hive_conf_dir=self.hive_conf_dir,
                    hadoop_conf_dir=self.hadoop_conf_dir,
                    hive_version=self.hive_version,
                ),
            )

        self.t_env.use_catalog(self.catalog_name)
        return self.catalog

    def create_or_replace_database(
        self,
        database_name: str,
        properties: Optional[Dict[str, str]] = None,
        comment: Optional[str] = None,
        overwrite: bool = False,
    ) -> CatalogDatabase:
        catalog = self.catalog

        if overwrite:
            catalog.drop_database(database_name, True)

        db = CatalogDatabase.create_instance(properties or {}, comment)
        catalog.create_database(database_name, db, True)
        return catalog.get_database(database_name)

    @contextmanager
    def use_hive_dialect(self, database_name: str):
        original_catalog = self.t_env.get_current_catalog()
        original_database = self.t_env.get_current_database()
        original_dialect = self.t_env.get_config().get_sql_dialect()

        self.t_env.use_catalog(self.catalog_name)
        self.t_env.use_database(database_name)
        self.t_env.get_config().set_sql_dialect(SqlDialect.HIVE)

        try:
            yield self.t_env
        finally:
            self.t_env.use_catalog(original_catalog)
            self.t_env.use_database(original_database)
            self.t_env.get_config().set_sql_dialect(original_dialect)