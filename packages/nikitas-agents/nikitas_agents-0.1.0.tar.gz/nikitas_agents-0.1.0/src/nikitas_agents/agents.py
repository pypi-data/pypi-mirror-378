import os
from typing import Optional

from dotenv import load_dotenv
from mistralai import Mistral
from openai import OpenAI

from . import schema


class BaseAgent:
    def __init__(
        self,
        name: str,
        description: str,
        provider: str = "openai",
        model: str = "gpt-4o-mini",
    ):
        self.name = name
        self.description = description

        # Load environment variables from .env once at initialization
        load_dotenv()

        self.provider = schema.validate_provider(provider)
        self.model = schema.validate_model(self.provider, model)

        if self.provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise RuntimeError("Missing OPENAI_API_KEY. Add it to your .env file.")
            self._client = OpenAI(api_key=api_key)
        elif self.provider == "mistral":
            api_key = os.getenv("MISTRAL_API_KEY")
            if not api_key:
                raise RuntimeError("Missing MISTRAL_API_KEY. Add it to your .env file.")
            if Mistral is None:
                raise RuntimeError(
                    "Mistral SDK not installed. Run: pip install mistralai"
                )
            self._client = Mistral(api_key=api_key)
        else:
            raise RuntimeError(f"Unsupported LLM provider: {self.provider}")

    def run(self, input):
        pass

    def invoke(
        self,
        user_prompt: str,
        system_prompt: str = "You are a helpful assistant",
        *,
        temperature: float = 0.2,
        max_output_tokens: int = 1024,
        timeout: Optional[float] = 60.0,
    ) -> str:
        """Invoke the selected provider's model with system and user prompts."""
        if getattr(self, "provider", "openai") == "openai":
            client = (
                self._client.with_options(timeout=timeout) if timeout else self._client
            )  # type: ignore[attr-defined]

            # Prefer the modern Responses API. Fallback to Chat Completions if not available.
            try:
                response = client.responses.create(  # type: ignore[call-arg]
                    model=self.model,
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                    input=[
                        {
                            "role": "system",
                            "content": [
                                {"type": "text", "text": system_prompt},
                            ],
                        },
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": user_prompt},
                            ],
                        },
                    ],
                )

                # New SDKs provide a convenience property for text output
                output_text = getattr(response, "output_text", None)
                if isinstance(output_text, str) and output_text.strip():
                    return output_text.strip()

                # If convenience property is missing, extract from the content array
                try:
                    parts = []
                    for item in getattr(response, "output", []) or []:
                        for content_part in getattr(item, "content", []) or []:
                            if getattr(content_part, "type", "") == "output_text":
                                parts.append(getattr(content_part, "text", ""))
                    text = "".join(parts).strip()
                    if text:
                        return text
                except Exception:
                    pass

                # As a last resort, stringify the response
                return str(response)
            except Exception:
                # Fallback to Chat Completions for environments with older SDKs
                completion = client.chat.completions.create(  # type: ignore[call-arg]
                    model=self.model,
                    temperature=temperature,
                    max_tokens=max_output_tokens,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                )
                message = (
                    completion.choices[0].message.content if completion.choices else ""
                )
                return (message or "").strip()

        if getattr(self, "provider", "openai") == "mistral":
            messages = [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ]
            response = self._client.chat.complete(  # type: ignore[call-arg]
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_output_tokens,
            )
            content = (
                response.choices[0].message.content
                if getattr(response, "choices", None)
                else ""
            )
            return (content or "").strip()

        raise RuntimeError(
            f"Unsupported LLM provider at runtime: {getattr(self, 'provider', None)}"
        )
