from pydantic import BaseModel, Field

class HiveSettings(BaseModel):
    version: str
    hostname: str
    conf_dir: str
    warehouse_dir: str
    metastore_port: str = Field(min_length=4, description="Port for the Hive Metastore service")
    server_port: str = Field(min_length=4, description="Port for the HiveServer2 service")

    @property
    def metastore_url(self) -> str:
        return f"thrift://{self.hostname}:{self.metastore_port}"

    @property
    def server_url(self) -> str:
        return f"beeline://{self.hostname}:{self.server_port}"

if __name__ == "__main__":
    hive_settings = HiveSettings(
        version="3.1.2",
        hostname="localhost",
        conf_dir="/path/to/hive/conf",
        warehouse_dir="/path/to/hive/warehouse",
        metastore_port="9083",
        server_port="10000"
    )
    print(hive_settings)
    print(hive_settings)