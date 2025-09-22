# Orkestra SDK

The Python SDK for Orkestra, a powerful platform for building, deploying, and managing AI-native workflows and agents.

**For more information, visit [Orkestration.com](https://orkestration.com).**
**For detailed documentation, visit [docs.orkestration.com](https://docs.orkestration.com).**

## Quickstart

Install the SDK:

```bash
pip install orkestra-sdk
```

Here's a simple example of a two-step workflow:

```python
from orkestra import Orkestra

# 1. Initialize your client
orkestra_client = Orkestra()

# 2. Create agents
researcher = orkestra_client.Agent(
    name="Researcher",
    description="Gathers detailed information on a topic.",
    model_provider="openai",
    model_name="gpt-4o",
    api_secret="YOUR_OPENAI_API_KEY",
)

summarizer = orkestra_client.Agent(
    name="Summarizer",
    description="Condenses complex information into a concise summary.",
    model_provider="openai",
    model_name="gpt-3.5-turbo",
    api_secret="YOUR_OPENAI_API_KEY",
)

# 3. Create and run the workflow
workflow = orkestra_client.Workflow().add(researcher).add(summarizer)
result = workflow.run("What are the key differences between nuclear fission and fusion?")

print(result)
```
