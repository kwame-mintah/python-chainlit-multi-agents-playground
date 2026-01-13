from typing import Literal, TypedDict

import chainlit as cl
from langchain.schema.runnable.config import RunnableConfig
from langchain_core.messages import HumanMessage, BaseMessage
from langgraph.graph import END, StateGraph, START
from langgraph.graph.message import MessagesState

from agents.development import (
    scrum_orchestrator_agent,
    software_engineer_agent,
    product_owner_agent,
)
from agents.prompts import SoftwareDevelopmentTeamPrompts
from agents.tools.tools import tool_node

class State(TypedDict):
    user_input : str
    product_manager_spec: str
    response: str
    code: str
    requirements: dict

def product_manager_node(state: State) -> State:

    print(state)

    messages = [
    (
        "system",
        SoftwareDevelopmentTeamPrompts.product_manager_prompt()
    ),
    ("human", state["user_input"])
    ]

    response = product_owner_agent.invoke(messages)
    print("Product Manager Response:")
    print(response.content)

    state["product_manager_spec"] = response.content
    return state


def dev_node(state: State) -> State:
    # Get the product spec from the previous node's output
    spec = state["product_manager_spec"]["requirements"]
    
    print("Product Spec for Developer:")
    print(spec)
    state["requirements"] = spec

    response = software_engineer_agent.invoke(spec)
    print("Developer Response:")
    print(response)


    state["code"] = response["messages"][0].content

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

        if msg.content and metadata.get("langgraph_node") == "dev_node":
            await final_answer.stream_token(msg.content)

    await final_answer.send()
