import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class DatabaseSettings:
    host: str = "localhost"
    port: int = 5432
    name: str = "application"
    user: str = "app_user"
    password: Optional[str] = None

    @property
    def connection_string(self) -> str:
        password = self.password or ""
        return (
            f"postgresql://{self.user}:{password}"
            f"@{self.host}:{self.port}/{self.name}"
        )


@dataclass
class ApplicationSettings:
    debug: bool = True
    environment: str = "development"
    database: DatabaseSettings = None
    secret_key: str = "replace-this-with-a-secret-key"

    def __post_init__(self) -> None:
        if self.database is None:
            self.database = DatabaseSettings()


def load_settings() -> ApplicationSettings:
    database = DatabaseSettings(
        host=os.getenv("DATABASE_HOST", "localhost"),
        port=int(os.getenv("DATABASE_PORT", "5432")),
        name=os.getenv("DATABASE_NAME", "application"),
        user=os.getenv("DATABASE_USER", "app_user"),
        password=os.getenv("DATABASE_PASSWORD"),
    )

    return ApplicationSettings(
        debug=os.getenv("DEBUG", "true").lower() == "true",
        environment=os.getenv("ENVIRONMENT", "development"),
        database=database,
        secret_key=os.getenv("SECRET_KEY", "replace-this-with-a-secret-key"),
    )


def validate_settings(settings: ApplicationSettings) -> bool:
    if not settings.secret_key:
        raise ValueError("A secret key is required.")

    if settings.database.port < 1 or settings.database.port > 65535:
        raise ValueError("Database port must be between 1 and 65535.")

    return True


if __name__ == "__main__":
    app_settings = load_settings()
    if validate_settings(app_settings):
        print(f"Running in {app_settings.environment} mode")
