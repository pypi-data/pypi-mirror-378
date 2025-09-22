from __future__ import annotations

from typing import TYPE_CHECKING, Generator, Optional, Type, Union

from pydantic import BaseModel

from .llm_abstraction import LLM, LLMConfig

if TYPE_CHECKING:
    from ..orkestra import Orkestra


class AgentConfig(BaseModel):
    name: str
    description: str


class Agent:
    """An LLM-powered worker that performs a specific task.

    Parameters:
        orkestra_client (Orkestra): The parent client used to create this agent. Enables future orchestration/tracing.
        name (str): A human-friendly name for the agent.
        description (str): What this agent is responsible for.
        model_provider (str | LLMProvider): The LLM provider identifier (e.g., "openai").
        model_name (str): The concrete model to use (e.g., "gpt-4o").
        api_secret (str): Provider-specific API secret used by this agent's LLM calls.

    Attributes:
        orkestra_client (Orkestra): The client that created this agent.
        config (AgentConfig): Basic metadata about the agent.
        llm (LLM): The low-level LLM wrapper bound to this agent.

    Example:
        >>> from orkestra import Orkestra, LLMProvider
        >>> client = Orkestra(api_key="YOUR_ORKESTRA_API_KEY")
        >>> agent = client.Agent(
        ...     name="Summarizer",
        ...     description="Summarizes text",
        ...     model_provider=LLMProvider.OPENAI,
        ...     model_name="gpt-3.5-turbo",
        ...     api_secret="YOUR_OPENAI_API_KEY",
        ... )
        >>> agent.generate("Summarize: Orkestra is a lightweight orchestration SDK.")
    """
    def __init__(
        self,
        orkestra_client: Orkestra,
        name: str,
        description: str,
        model_provider: str,
        model_name: str,
        api_secret: str,
    ):
        self.orkestra_client = orkestra_client
        self.config = AgentConfig(name=name, description=description)
        self.llm = LLM(
            LLMConfig(
                provider=model_provider, model_name=model_name, api_secret=api_secret
            )
        )

    def __str__(self):
        return f"Agent(name={self.config.name}, description={self.config.description}, model_provider={self.llm.config.provider}, model_name={self.llm.config.model_name})"

    def generate(
        self,
        prompt: Union[str, BaseModel],
        response_model: Optional[Type[BaseModel]] = None,
    ) -> Union[str, BaseModel]:
        """Generate a response from the agent.

        Parameters:
            prompt (str | BaseModel): Input for the agent. If a Pydantic model is provided, it will be serialized to JSON.
            response_model (type[BaseModel] | None): Optional structured output model. If provided, the response is validated and returned as that Pydantic model.

        Returns:
            str | BaseModel: Plain text by default, or an instance of `response_model` when specified.

        Example:
            >>> agent.generate("Write a haiku about orchestration.")
            'Silent threads align...'

            >>> from pydantic import BaseModel
            >>> class CalendarEvent(BaseModel):
            ...     name: str
            ...     date: str
            ...     participants: list[str]
            >>> agent.generate("Alice and Bob meet Friday", response_model=CalendarEvent)
            CalendarEvent(name='...', date='...', participants=['Alice','Bob'])
        """
        prompt_str = (
            prompt.model_dump_json() if isinstance(prompt, BaseModel) else str(prompt)
        )
        return self.llm.generate(
            prompt_str,
            model_name=self.llm.config.model_name,
            response_model=response_model,
        )

    def stream(self, prompt: str) -> Generator[str, None, None]:
        """Stream tokens from the agent for the given prompt.

        Parameters:
            prompt (str): The input text to stream a response for.

        Yields:
            str: Incremental chunks/tokens of the LLM response.
        """
        return self.llm.stream(prompt, model_name=self.llm.config.model_name)