from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class CustodiaSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        populate_by_name=True,
    )

    environment: str = Field("local", validation_alias="CUSTODIA_ENV")
    service_name: str = Field("custodia-server", validation_alias="CUSTODIA_SERVICE_NAME")
    debug: bool = Field(False, validation_alias="CUSTODIA_DEBUG")
    log_level: str = Field("INFO", validation_alias="CUSTODIA_LOG_LEVEL")

    database_url: str = Field(
        "postgresql://custodia:custodia@localhost:5432/custodia",
        validation_alias="DATABASE_URL",
    )

    keycloak_realm: str = Field("custodia", validation_alias="KEYCLOAK_REALM")
    keycloak_base_url: str = Field("http://localhost:8080", validation_alias="KEYCLOAK_BASE_URL")
    keycloak_client_id: str = Field("custodia-server", validation_alias="KEYCLOAK_CLIENT_ID")

    jaeger_endpoint: str = Field("http://localhost:4318", validation_alias="JAEGER_ENDPOINT")
