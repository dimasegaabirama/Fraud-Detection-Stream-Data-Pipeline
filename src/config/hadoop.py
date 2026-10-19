from pydantic import BaseModel, Field

class HadoopSettings(BaseModel):
    version: str
    hostname: str
    port: str = Field(min_length=4, description="Port for the Hadoop service")
    conf_dir: str

    @property
    def url(self):
        return f"hdfs://{self.hostname}:{self.port}"

    
if __name__ == "__main__":
    hadoop_settings = HadoopSettings(
        version="3.3.1",
        hostname="localhost",
        port="9000",
        conf_dir="/path/to/hadoop/conf"
    )
    print(hadoop_settings)
