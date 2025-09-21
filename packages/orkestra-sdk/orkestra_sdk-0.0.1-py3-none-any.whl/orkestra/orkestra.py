from functools import partial

from .core import Agent, Workflow


class Orkestra:
    """Top-level client and factory for Orkestra components.

    Parameters:
        api_key (str): Orkestra platform API key. Used for orchestration/tracing features.

    Attributes:
        Agent (callable): Factory that creates `Agent` instances with this client bound.
        Workflow (callable): Factory that creates `Workflow` instances with this client bound.

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
        >>> wf = client.Workflow().add(agent)
        >>> wf.run("Summarize this paragraph ...")
    """
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.Agent = partial(Agent, orkestra_client=self)
        self.Workflow = partial(Workflow, orkestra_client=self)