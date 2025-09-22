from openai import OpenAI
from typing import Generator, Union, Type, Optional
from pydantic import BaseModel

class OrkestraOpenAI:
    def __init__(self, api_secret: str, base_url: str = None):
        if base_url:
            self.client = OpenAI(api_key=api_secret, base_url=base_url)
        else:
            self.client = OpenAI(api_key=api_secret)

    def generate(
        self,
        prompt: str,
        model_name: str = "gpt-5",
        temperature: float = 0.0,
        base_url: str = None,
        response_model: Optional[Type[BaseModel]] = None,
    ) -> Union[str, BaseModel]:
        if response_model:
            response = self.client.responses.parse(
                model=model_name,
                input=[
                    {
                        "role": "system",
                        "content": f"Extract information into the requested Pydantic model format: {response_model.__name__}",
                    },
                    {"role": "user", "content": prompt},
                ],
                text_format=response_model,
                stream=False
            )
            return response.output_parsed
        else:
            response = self.client.responses.create(
                model=model_name,
                input=prompt,
            )

        return response.output_text

    def stream(self, prompt: str, model_name: str = "gpt-5") -> Generator[str, None, None]:
        response = self.client.responses.create(
            model=model_name,
            input=prompt,
            stream=True,
        )

        for event in response:
            yield event