from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    postgres_url: str = Field(alias="INGEST_POSTGRES_URL")
    oracle_user: str = Field(default="ZC_INGEST", alias="ORACLE_INGEST_USER")
    oracle_password: str = Field(alias="ORACLE_INGEST_PASSWORD")
    oracle_dsn: str = Field(default="dataprd_low", alias="ORACLE_DSN")
    oracle_wallet_dir: Path = Field(default=Path("/opt/oracle/wallet"), alias="ORACLE_WALLET_DIR")
    oracle_wallet_password: str = Field(alias="ORACLE_WALLET_PASSWORD")
    code_version: str = Field(default="phase3-local", alias="CODE_VERSION")

