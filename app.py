from typing import Literal, TypedDict

from agents.prompts import SoftwareDevelopmentTeamPrompts
import chainlit as cl
from langchain.schema.runnable.config import RunnableConfig
from langchain_core.messages import HumanMessage, BaseMessage
from langgraph.graph import END, StateGraph, START
from langgraph.graph.message import MessagesState

from agents.development import (
    scrum_orchestrator_agent,
    software_engineer_agent,
    product_owner_agent,
    model
)
from agents.tools.tools import tool_node

class State(TypedDict):
    user_input : str
    product_manager_spec: str
    response: str
    code: str
    

def product_manager_node(state: State) -> State:

    print(state)

    messages = [
    (
        "system",
        SoftwareDevelopmentTeamPrompts.product_manager_prompt()
    ),
    ("human", state["user_input"])
    ]

    response = model.invoke(messages)
    print(response)

    state["product_manager_spec"] = response.content
    return state


def dev_node(state: State) -> State:
    # Get the product spec from the previous node's output
    spec = state["product_manager_spec"]

    messages = [
        (
            "system",
            "You are a smart software developer that can write code based on product specs.",
        ),
        ("human", f"Write code based on this spec: {spec}") # Pass the spec to the LLM
    ]

    response = software_engineer_agent.model.invoke(messages)
    print(response)

    state["code"] = response.content
    return state

graph = (
    StateGraph(State)
    # Add nodes
    .add_node("product_owner_agent", product_manager_node)
    .add_node("software_engineer_agent", software_engineer_agent)

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

    print("Starting graph execution")
    print(inputs)

    async for msg, metadata in graph.astream(
        inputs, stream_mode="messages", config=RunnableConfig(callbacks=[cb], **config)
    ):
        if isinstance(msg, HumanMessage):
            continue

        if msg.content and metadata.get("langgraph_node") == "final":
            await final_answer.stream_token(msg.content)

    await final_answer.send()
