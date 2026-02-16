from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Puffling"
    database_url: str = "sqlite:///./puffling.db"
    default_user_id: str = "default"
    paper_trading: bool = True

    model_config = {"env_prefix": "PUFFLING_"}


settings = Settings()
