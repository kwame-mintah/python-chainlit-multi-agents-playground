from typing import Optional

from pydantic import Field
from pydantic_core import Url
from pydantic_settings import BaseSettings


class EnvironmentVariables(BaseSettings):
    LLM_INFERENCE_PROVIDER: str = Field(
        description="The inference model provider to use",
        default="ollama",
    )
    OLLAMA_URL: Url = Field(
        description="The Ollama host URL", default="http://localhost:11434"
    )
    OLLAMA_LLM_MODEL: str = Field(
        description="The Ollama model to use", default="deepseek-r1:1.5b"
    )
    GOOGLE_GEMINI_API_KEY: str = Field(
        description="Your Google Gemini API key", alias="GOOGLE_API_KEY", default=""
    )
    GOOGLE_GEMINI_LLM_MODEL: str = Field(
        description="The Gemini model to use", default="gemini-2.5-flash"
    )
    HUGGING_FACE_INFERENCE_MODEL: str = Field(
        description="The name of the hugging face repository for model inference",
        default="Qwen/Qwen2.5-72B-Instruct",
    )
    HUGGINGFACEHUB_API_TOKEN: Optional[str] = Field(
        description="Your hugging face API token", default=None, alias="HF_TOKEN"
    )


environment_variables = EnvironmentVariables()
