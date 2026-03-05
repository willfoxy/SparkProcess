from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # AWS Bedrock
    aws_region: str = "us-east-1"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_session_token: str = ""
    # Cross-region inference profile ID (recommended for production)
    bedrock_model_id: str = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
    bedrock_haiku_model_id: str = "us.anthropic.claude-3-5-haiku-20241022-v1:0"

    # AWS DynamoDB (AgentCore memory store)
    dynamodb_table_name: str = "spark-process-memory"
    dynamodb_endpoint_url: str = ""  # Leave empty for real AWS

    # Datadog LLM Observability
    dd_api_key: str = ""
    dd_site: str = "datadoghq.com"
    dd_env: str = "development"
    dd_service: str = "spark-process"
    dd_ml_app: str = "double-diamond-agents"
    dd_llm_obs_enabled: bool = True

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Agent behaviour
    max_tokens_per_agent: int = 2048
    agent_temperature: float = 0.7
    security_strict_mode: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
