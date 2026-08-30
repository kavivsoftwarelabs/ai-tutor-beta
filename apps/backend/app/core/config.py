from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "ai-tutor-beta"
    postgres_user: str = "aitutor_user"
    postgres_password: str = "aitutor_secure_pass"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "aitutor_beta_state"

    class Config:
        env_file = ".env"


settings = Settings()
