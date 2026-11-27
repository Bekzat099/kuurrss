from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Kuurrss API"
    environment: str = "local"
    database_url: str
    secret_key: str
    keycloak_url: str = "http://localhost:8080"
    keycloak_realm: str = "quizai"
    keycloak_client_id: str = "quizai-web"
    keycloak_issuer: str = "http://localhost:8080/realms/quizai"
    keycloak_jwks_url: str = ""
    keycloak_audience: str = "quizai-api"
    ollama_url: str = "http://localhost:11434"

    @property
    def jwks_url(self) -> str:
        if self.keycloak_jwks_url:
            return self.keycloak_jwks_url
        return f"{self.keycloak_issuer.rstrip('/')}/protocol/openid-connect/certs"

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
