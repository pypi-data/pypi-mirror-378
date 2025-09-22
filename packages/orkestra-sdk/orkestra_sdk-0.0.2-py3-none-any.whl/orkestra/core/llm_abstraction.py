from enum import Enum
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional, Generator, Type, Union

from .llm.orkestra_openai import OrkestraOpenAI


class LLMProvider(str, Enum):
    """Enumerates supported LLM providers.

    Values:
        OPENAI: Use OpenAI models.
        GEMINI: Reserved for Google Gemini integration.
        CLAUDE: Reserved for Anthropic Claude integration.
    """
    OPENAI = "openai"
    GEMINI = "gemini"
    CLAUDE = "claude"


class LLMConfig(BaseModel):
    """Configuration for an LLM client instance.

    Attributes:
        provider (LLMProvider): Which provider to use (e.g., `LLMProvider.OPENAI`).
        model_name (str): The model identifier (e.g., "gpt-4o").
        api_secret (str): The provider API key/secret for authentication.
        params (dict): Provider-specific optional parameters (e.g., temperature).

    Example:
        >>> from orkestra.core.llm_abstraction import LLMConfig, LLMProvider
        >>> cfg = LLMConfig(provider=LLMProvider.OPENAI, model_name="gpt-4o", api_secret="sk-...")
    """
    provider: LLMProvider
    model_name: str
    api_secret: str
    params: Dict[str, Any] = Field(default_factory=dict)


class LLM:
    """Thin abstraction over specific LLM provider clients.

    Parameters:
        config (LLMConfig): The configuration for instantiating the underlying client.

    Attributes:
        config (LLMConfig): The active configuration.
        client (Any): The underlying provider client.

    Example:
        >>> from orkestra.core.llm_abstraction import LLM, LLMConfig, LLMProvider
        >>> llm = LLM(LLMConfig(provider=LLMProvider.OPENAI, model_name="gpt-3.5-turbo", api_secret="sk-..."))
        >>> llm.generate("Hello", model_name="gpt-3.5-turbo")
        'Hi there!'
    """
    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = self._get_client()

    def _get_client(self) -> Any:
        if self.config.provider == LLMProvider.OPENAI:
            # Placeholder for OpenAI client initialization
            return OrkestraOpenAI(self.config.api_secret)
        elif self.config.provider == LLMProvider.GEMINI:
            # Placeholder for Gemini client initialization
            pass
        elif self.config.provider == LLMProvider.CLAUDE:
            # Placeholder for Claude client initialization
            pass
        else:
            raise ValueError(f"Unsupported LLM provider: {self.config.provider}")

    def generate(
        self,
        prompt: str,
        model_name: str,
        response_model: Optional[Type[BaseModel]] = None,
    ) -> Union[str, BaseModel]:
        """Generate a completion from the current provider.

        Parameters:
            prompt (str): Input prompt.
            model_name (str): Model to use for this call.
            response_model (type[BaseModel] | None): Optional Pydantic model for structured output.

        Returns:
            str | BaseModel: Plain text or a validated Pydantic object when `response_model` is supplied.
        """
        return self.client.generate(
            prompt, model_name=model_name, response_model=response_model
        )

    def stream(self, prompt: str, model_name: str) -> Generator[str, None, None]:
        """Stream tokens from the current provider for the given prompt and model."""
        return self.client.stream(prompt, model_name=model_name)