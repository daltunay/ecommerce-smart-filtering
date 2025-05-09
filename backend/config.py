import typing as tp

from pydantic import BaseModel, Field, computed_field, field_serializer, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .common.logging import log


class ApiConfig(BaseModel):
    """API configuration settings."""

    key: str | None = Field(
        default=None,
        description="API key for authentication",
    )

    @computed_field
    @property
    def is_secure(self) -> bool:
        """Check if the API key is set."""
        return self.key is not None

    @field_serializer("key")
    def serialize_key(self, value: str | None) -> str | None:
        if value is None:
            return None
        return "*" * len(value)


class RemoteModelConfig(BaseModel):
    """Remote model configuration settings."""

    base_url: str = Field(default="https://generativelanguage.googleapis.com/v1beta/openai/")
    api_key: str = Field(...)
    name: str = Field(default="gemini-2.0-flash-lite")

    @field_serializer("api_key")
    def serialize_key(self, value: str) -> str:
        return "*" * len(value)


class LocalModelConfig(BaseModel):
    """Local model configuration settings."""

    name: str = Field(default="HuggingFaceTB/SmolVLM-Instruct")
    dtype: str = Field(default="bfloat16")
    device: str = Field(default="auto")


class ModelConfig(BaseModel):
    """Unified model configuration settings."""

    use_local: bool = Field(default=False)
    remote: RemoteModelConfig | None = Field(default=None)
    local: LocalModelConfig | None = Field(default=None)

    @model_validator(mode="after")
    def update_model_config(self) -> tp.Self:
        if self.use_local:
            if self.local is None:
                self.local = LocalModelConfig()
        else:
            if self.remote is None:
                self.remote = RemoteModelConfig()
        return self


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_ignore_empty=True,
        env_nested_delimiter="__",
        env_nested_max_split=2,
        env_file=".env",
        env_file_encoding="utf-8",
    )

    api: ApiConfig = Field(default_factory=ApiConfig)
    model: ModelConfig = Field(default_factory=ModelConfig)


settings = Settings()
log.info("Settings loaded", **settings.model.model_dump(exclude_none=True))
