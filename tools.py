from typing import Literal

from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode

from config import environment_variables
from utils import get_inference_model


@tool
def get_weather(city: Literal["nyc", "sf"]):
    """Use this to get weather information."""
    if city == "nyc":
        return "It might be cloudy in nyc"
    elif city == "sf":
        return "It's always sunny in sf"
    else:
        raise AssertionError("Unknown city")


llm_model = get_inference_model(
    model_provider=environment_variables.LLM_INFERENCE_PROVIDER
)

tools = [get_weather]
model = llm_model
final_model = llm_model

model = model.bind_tools(tools)
# NOTE: this is where we're adding a tag that we'll can use later to filter the model stream events to only the model called in the final node.
# This is not necessary if you call a single LLM but might be important in case you call multiple models within the node and want to filter events
# from only one of them.
final_model = final_model.with_config(tags=["final_node"])
tool_node = ToolNode(tools=tools)
