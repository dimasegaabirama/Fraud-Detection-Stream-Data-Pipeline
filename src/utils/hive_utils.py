from contextlib import contextmanager

from pyflink.table import SqlDialect, StreamTableEnvironment


@contextmanager
def use_hive_catalog(catalog_name: str, database_name: str, t_env: StreamTableEnvironment):
    original_catalog = t_env.get_current_catalog()

    t_env.use_catalog(catalog_name)
    t_env.use_database(database_name)
    t_env.get_config().set_sql_dialect(SqlDialect.HIVE)
    try:
        yield
    finally:
        t_env.use_catalog(original_catalog)
        t_env.get_config().set_sql_dialect(SqlDialect.DEFAULT)
