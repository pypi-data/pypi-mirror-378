from openai import OpenAI
from typing import Generator, Union, Type, Optional
from pydantic import BaseModel
import json

class OrkestraStandardLLM:
    """Generic OpenAI-compatible LLM client for any provider with OpenAI-style API."""
    
    def __init__(self, api_secret: str, base_url: str):
        """
        Initialize the client with API key and base URL.
        
        Args:
            api_secret (str): The API key for authentication
            base_url (str): The base URL for the API endpoint
        """
        self.client = OpenAI(api_key=api_secret, base_url=base_url)

    def generate(
        self,
        prompt: str,
        model_name: str,
        temperature: float = 0.0,
        response_model: Optional[Type[BaseModel]] = None,
    ) -> Union[str, BaseModel]:
        """
        Generate a completion from the provider.
        
        Args:
            prompt (str): Input prompt
            model_name (str): Model to use for this call
            temperature (float): Sampling temperature
            response_model (Optional[Type[BaseModel]]): Optional Pydantic model for structured output
            
        Returns:
            Union[str, BaseModel]: Plain text or validated Pydantic object when response_model is supplied
        """
        messages = [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": prompt}
        ]
        
        if response_model:
            # Add specific instructions for structured output
            structured_messages = [
                {
                    "role": "system", 
                    "content": f"You are a helpful assistant that extracts information and returns it as valid JSON matching this schema: {response_model.model_json_schema()}. Only return the JSON object, no additional text."
                },
                {"role": "user", "content": prompt}
            ]
            
            response = self.client.chat.completions.create(
                model=model_name,
                messages=structured_messages,
                temperature=temperature,
                stream=False,
                response_format={
                    'type': 'json_object'
                }
            )
            
            # Parse the response as JSON and validate with the Pydantic model
            try:
                parsed_data = json.loads(response.choices[0].message.content)
                return response_model(**parsed_data)
            except (json.JSONDecodeError, TypeError, ValueError) as e:
                # If parsing fails, try a more direct approach
                raise ValueError(f"Failed to parse structured output: {e}. Response was: {response.choices[0].message.content}")
            
        else:
            response = self.client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=temperature,
                stream=False
            )
            return response.choices[0].message.content

    def stream(self, prompt: str, model_name: str, temperature: float = 0.0) -> Generator[str, None, None]:
        """
        Stream tokens from the provider for the given prompt and model.
        
        Args:
            prompt (str): Input prompt
            model_name (str): Model to use for this call
            temperature (float): Sampling temperature
            
        Yields:
            str: Token chunks from the streaming response
        """
        messages = [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": prompt}
        ]
        
        response = self.client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=temperature,
            stream=True
        )

        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content 