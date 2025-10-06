from typing import Union

from langchain_core.language_models import BaseChatModel

from inference_models import ollama, gemini


def get_inference_model(
    model_provider: str,
) -> Union[BaseChatModel, None]:
    """
    Get the pre-configured LLM model provider.

    Args:
        model_provider ():

    Returns:
        The LLM model `BaseChatModel`
    """
    provider_name_mapping: dict = {
        "ollama": ollama,
        "gemini": gemini,
    }
    model = provider_name_mapping.get(model_provider, None)

    if not model:
        raise ValueError(f"Unable to map LLM model with provider: {model_provider}")

    return model
