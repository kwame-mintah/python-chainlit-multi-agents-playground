from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama

from config import environment_variables

ollama = ChatOllama(
    model=environment_variables.OLLAMA_LLM_MODEL,
    base_url=str(environment_variables.OLLAMA_URL),
)

gemini = ChatGoogleGenerativeAI(
    model="gemini-pro",
    google_api_key=environment_variables.GOOGLE_GEMINI_API_KEY,
    include_thoughts=True,
)
