"""
Centralized application configuration, loaded from environment variables (.env).
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"
    ollama_temperature: float = 0.4

    # MCP
    mcp_server_host: str = "localhost"
    mcp_server_port: int = 8765

    # FastAPI
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_env: str = "development"

    # Automation
    daily_task_hour: int = 8
    daily_task_minute: int = 0
    daily_task_topic: str = "Latest developments in local-first AI tooling"

    # Logging
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
