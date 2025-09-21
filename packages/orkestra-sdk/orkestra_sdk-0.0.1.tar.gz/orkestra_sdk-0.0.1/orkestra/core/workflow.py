from __future__ import annotations
from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    List,
    Optional,
    Tuple,
    Type,
    Union,
)
from pydantic import BaseModel

if TYPE_CHECKING:
    from .agent import Agent
    from ..orkestra import Orkestra


@dataclass
class WorkflowStep:
    """A single step in a workflow.

    Attributes:
        agent (Agent): The agent to execute for this step.
        response_model (type[BaseModel] | None): Optional structured output model for this agent's response.
        handler (Callable[[str | BaseModel], tuple[str, Any]] | None): Optional post-step function that receives
            the agent output and returns a tuple of (action, next_input). `action` must be either:
            - "CONTINUE": proceed to the next step using `next_input` as the new prompt
            - "STOP": terminate the workflow immediately and return the current step's output
    """
    agent: Agent
    response_model: Optional[Type[BaseModel]] = None
    handler: Optional[
        Callable[[Union[str, BaseModel]], Tuple[str, Any]]
    ] = None


class Workflow:
    """Orchestrates a sequence of agents with optional conditional logic.

    Parameters:
        orkestra_client (Orkestra): The client that owns this workflow.

    Example:
        >>> from orkestra import Orkestra, LLMProvider
        >>> from pydantic import BaseModel
        >>> client = Orkestra(api_key="YOUR_ORKESTRA_API_KEY")
        >>> researcher = client.Agent("Researcher", "Gathers info", LLMProvider.OPENAI, "gpt-4o", "OPENAI_KEY")
        >>> summarizer = client.Agent("Summarizer", "Summarizes", LLMProvider.OPENAI, "gpt-3.5-turbo", "OPENAI_KEY")
        >>> wf = client.Workflow().add(researcher).add(summarizer)
        >>> wf.run("Explain RAG in simple terms")
        '...'

        Conditional step with a handler:
        >>> from pydantic import BaseModel
        >>> class Triage(BaseModel):
        ...     ambiguous: bool
        ...     follow_up_details: str
        ...     reply_to_user: str
        >>> def triage_handler(output: Triage):
        ...     return ("STOP", None) if output.ambiguous else ("CONTINUE", output.follow_up_details)
        >>> wf = client.Workflow().add(researcher, response_model=Triage, handler=triage_handler).add(summarizer)
        >>> wf.run("Tell me about the big tech company")
    """
    def __init__(self, orkestra_client: Orkestra):
        self.orkestra_client = orkestra_client
        self.steps: List[WorkflowStep] = []

    def add(
        self,
        agent: Agent,
        response_model: Optional[Type[BaseModel]] = None,
        handler: Optional[Callable[[Any], Tuple[str, Any]]] = None,
    ) -> Workflow:
        """Add a step to the workflow.

        Parameters:
            agent (Agent): The agent to execute.
            response_model (type[BaseModel] | None): Optional structured output model for this step.
            handler (Callable | None): Optional function to post-process step output and decide whether to continue or stop.

        Returns:
            Workflow: The workflow instance (for chaining).
        """
        self.steps.append(
            WorkflowStep(agent=agent, response_model=response_model, handler=handler)
        )
        return self

    def run(
        self,
        initial_prompt: str,
        response_model: Optional[Type[BaseModel]] = None,
    ) -> Union[str, BaseModel]:
        """Execute the workflow from start to finish.

        Parameters:
            initial_prompt (str): The initial input to the first step.
            response_model (type[BaseModel] | None): Optional structured model for the FINAL step if that step has no specific `response_model`.

        Returns:
            str | BaseModel: The output of the last executed step, or the step that requested STOP.
        """
        if not self.steps:
            raise ValueError("Cannot run an empty workflow. Add steps before running.")

        current_data: Union[str, BaseModel] = initial_prompt
        num_steps = len(self.steps)

        for i, step in enumerate(self.steps):
            is_last_step = i == num_steps - 1
            model_for_step = (
                step.response_model
                if step.response_model
                else response_model if is_last_step else None
            )

            output = step.agent.generate(current_data, response_model=model_for_step)

            if step.handler:
                action, next_data = step.handler(output)
                if action == "STOP":
                    return output
                elif action == "CONTINUE":
                    current_data = next_data
                else:
                    raise ValueError(f"Invalid action from handler: {action}")
            else:
                current_data = output

        return current_data 