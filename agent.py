from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI

import os

#os.environ["GOOGLE_API_KEY"] = "your-api-key-here"

def get_weather(city: str) -> str:  
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", include_thoughts=True)

agent = create_react_agent(
    model=llm,
    tools=[get_weather],
    prompt="You are a helpful assistant"
)
