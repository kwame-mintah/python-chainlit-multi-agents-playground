from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEndpoint
from langchain_ollama import ChatOllama

from config.settings import environment_variables

ollama = ChatOllama(
    model=environment_variables.OLLAMA_LLM_MODEL,
    base_url=str(environment_variables.OLLAMA_URL),
    validate_model_on_init=(
        True if environment_variables.LLM_INFERENCE_PROVIDER == "ollama" else False
    ),
)

gemini = ChatGoogleGenerativeAI(
    model=environment_variables.GOOGLE_GEMINI_LLM_MODEL,
    google_api_key=environment_variables.GOOGLE_GEMINI_API_KEY,
    include_thoughts=True,
)

hugging_face = HuggingFaceEndpoint(
    repo_id=environment_variables.HUGGING_FACE_INFERENCE_MODEL,
    huggingfacehub_api_token=environment_variables.HUGGINGFACEHUB_API_TOKEN,
)
