from typing import TypedDict
import json

import chainlit as cl
from langchain.schema.runnable.config import RunnableConfig
from langchain_core.messages import HumanMessage
from langgraph.graph import END, StateGraph, START

from agents.development import (
    software_engineer_agent,
    product_owner_agent,
)
from agents.prompts import SoftwareDevelopmentTeamPrompts

class State(TypedDict):
    user_input : str
    product_manager_spec: str
    response: str
    code: str
    requirements: dict

def product_manager_node(state: State) -> State:

    print(state)

    # Pass input in the format expected by create_react_agent
    response = product_owner_agent.invoke({
        "messages": [
            ("system", SoftwareDevelopmentTeamPrompts.product_manager_prompt()),
            ("human", state["user_input"])
        ]
    })
    
    print("Product Manager Response:")
    print(response)

    # Extract content from the response messages
    if "messages" in response and len(response["messages"]) > 0:
        response_content = response["messages"][-1].content
    else:
        response_content = str(response)
    
    # Parse the structured output from the response
    try:
        # The response content should be JSON from the structured output
        parsed_spec = json.loads(response_content) if isinstance(response_content, str) else response_content
        state["product_manager_spec"] = parsed_spec
    except json.JSONDecodeError:
        # Fallback if not valid JSON
        state["product_manager_spec"] = response_content
    
    return state


def dev_node(state: State) -> State:
    # Get the product spec from the previous node's output
    product_spec = state["product_manager_spec"]
    
    # Extract requirements if product_spec is a dict, otherwise use full spec
    if isinstance(product_spec, dict):
        requirements = product_spec.get("requirements", product_spec)
    else:
        requirements = product_spec
    
    print("Product Spec for Developer:")
    print(requirements)
    state["requirements"] = requirements

    # Format the input as expected by create_react_agent
    response = software_engineer_agent.invoke({
        "messages": [
            ("system", SoftwareDevelopmentTeamPrompts.software_engineer_prompt()),
            ("human", str(requirements))
        ]
    })
    
    print("Developer Response:")
    print(response)

    # Extract code from response messages
    if "messages" in response and len(response["messages"]) > 0:
        state["code"] = response["messages"][-1].content
    else:
        state["code"] = str(response)

    return state
 


graph = (
    StateGraph(State)
    # Add nodes
    .add_node("product_owner_agent", product_manager_node)
    .add_node("software_engineer_agent", dev_node)

    # Add edges
    .add_edge(start_key=START, end_key="product_owner_agent")
    .add_edge(start_key="product_owner_agent", end_key="software_engineer_agent")
    .add_edge(start_key="software_engineer_agent", end_key=END)
    # Compile the graph
    .compile(name="development_team_graph")
)


@cl.on_message
async def on_message(user_msg: cl.Message):
    config = {"configurable": {"thread_id": cl.context.session.id}}
    cb = cl.LangchainCallbackHandler()
    final_answer = cl.Message(content="")

    inputs = {
        "user_input": user_msg.content
    }

    async for msg, metadata in graph.astream(
        inputs, stream_mode="messages", config=RunnableConfig(callbacks=[cb], **config)
    ):
        if isinstance(msg, HumanMessage):
            continue

        if msg.content and metadata.get("langgraph_node") == "software_engineer_agent":
            await final_answer.stream_token(msg.content)

    await final_answer.send()
