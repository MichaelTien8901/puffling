from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Puffling"
    database_url: str = "sqlite:///./puffling.db"
    default_user_id: str = "default"
    paper_trading: bool = True
    alpaca_api_key: str = ""
    alpaca_secret_key: str = ""
    broker: str = "alpaca"  # "alpaca" or "ibkr"
    ibkr_host: str = "127.0.0.1"
    ibkr_port: int = 4002
    ibkr_client_id: int = 1

    model_config = {"env_prefix": "PUFFLING_"}


settings = Settings()
