"""Provider API credentials management for Celeste AI Framework."""

from typing import Optional

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings

from celeste.core import Provider

# Provider to credential field mapping
PROVIDER_CREDENTIAL_MAP = {
    Provider.OPENAI: "openai_api_key",
    Provider.ANTHROPIC: "anthropic_api_key",
    Provider.GOOGLE: "google_api_key",
    Provider.MISTRAL: "mistral_api_key",
    Provider.HUGGINGFACE: "huggingface_token",
    Provider.STABILITYAI: "stabilityai_api_key",
    Provider.REPLICATE: "replicate_api_token",
    Provider.COHERE: "cohere_api_key",
    Provider.XAI: "xai_api_key",
    Provider.LUMA: "luma_api_key",
    Provider.TOPAZLABS: "topazlabs_api_key",
    # LOCAL, OLLAMA, TRANSFORMERS have no credentials
}


class Credentials(BaseSettings):
    """API credentials for all supported providers.

    Credentials are loaded from environment variables or .env file.
    All credentials are optional - only configure the providers you use.
    Uses SecretStr for API keys to prevent accidental exposure in logs.
    """

    openai_api_key: Optional[SecretStr] = Field(None, alias="OPENAI_API_KEY")
    anthropic_api_key: Optional[SecretStr] = Field(None, alias="ANTHROPIC_API_KEY")
    google_api_key: Optional[SecretStr] = Field(None, alias="GOOGLE_API_KEY")
    mistral_api_key: Optional[SecretStr] = Field(None, alias="MISTRAL_API_KEY")
    huggingface_token: Optional[SecretStr] = Field(None, alias="HUGGINGFACE_TOKEN")
    stabilityai_api_key: Optional[SecretStr] = Field(None, alias="STABILITYAI_API_KEY")
    replicate_api_token: Optional[SecretStr] = Field(None, alias="REPLICATE_API_TOKEN")
    cohere_api_key: Optional[SecretStr] = Field(None, alias="COHERE_API_KEY")
    xai_api_key: Optional[SecretStr] = Field(None, alias="XAI_API_KEY")
    luma_api_key: Optional[SecretStr] = Field(None, alias="LUMA_API_KEY")
    topazlabs_api_key: Optional[SecretStr] = Field(None, alias="TOPAZLABS_API_KEY")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }

    def get_credentials(self, provider: Provider) -> SecretStr:
        """Get credentials for a specific provider."""
        if not self.has_credential(provider):
            raise ValueError(f"Provider {provider} has no credentials configured.")

        credential: SecretStr = getattr(self, PROVIDER_CREDENTIAL_MAP[provider])
        return credential

    def list_available_providers(self) -> list[Provider]:
        """List all providers that have credentials configured."""
        return [
            provider
            for provider in PROVIDER_CREDENTIAL_MAP
            if self.has_credential(provider)
        ]

    def has_credential(self, provider: Provider) -> bool:
        """Check if a specific provider has credentials configured."""
        credential_field = PROVIDER_CREDENTIAL_MAP.get(provider)
        if not credential_field:
            raise ValueError(f"Provider {provider} has no credential mapping")
        return getattr(self, credential_field, None) is not None


credentials = Credentials()  # type: ignore[call-arg]

__all__ = ["Credentials", "credentials"]
