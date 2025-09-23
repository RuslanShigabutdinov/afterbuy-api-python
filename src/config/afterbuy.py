from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    jv_base_url: str = Field("farm01", alias="APP_JV_BASE_URL")
    xl_base_url: str = Field("farm04", alias="APP_XL_BASE_URL")

    jv_username: str = Field("RoboCop_KAZAKSTAN", alias="JV_USERNAME")
    xl_username: str = Field("xlmoebel_de", alias="XL_USERNAME")

    jv_password: str = Field("Robostic2025!", alias="JV_PASSWORD")
    xl_password: str = Field("NeustartParol2025!", alias="XL_PASSWORD")

    parsing_per_page: int = Field(500, alias="PARSING_PER_PAGE")
    parser_process_count: int = Field(10, alias="PARSER_PROCESS_COUNT")
    parser_batch_size: int = Field(3, alias="PARSER_BATCH_SIZE")
    max_concurrent_parses: int = Field(13, alias="MAX_CONCURRENT_PARSES")


settings = Settings()
