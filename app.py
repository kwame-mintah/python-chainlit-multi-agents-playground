from typing import Literal

import chainlit as cl
from langchain.schema.runnable.config import RunnableConfig
from langchain_core.messages import HumanMessage
from langgraph.graph import END, StateGraph, START
from langgraph.graph.message import MessagesState

from agents.development import (
    scrum_orchestrator_agent,
    software_engineer_agent,
    product_owner_agent,
)
from agents.tools.tools import tool_node


def route_from_product_owner(
    state: MessagesState,
) -> Literal["scrum_master", "wait_for_user"]:
    messages = state["messages"]
    if not messages:
        return "scrum_master"

    last_message = messages[-1]

    if "NEED_USER_INPUT:" in last_message.content:
        return "wait_for_user"

    return "scrum_master"


def route_from_engineer(state: MessagesState) -> Literal["tools", "scrum_master"]:
    messages = state["messages"]
    last_message = messages[-1]

    if getattr(last_message, "tool_calls", None):
        return "tools"

    return "scrum_master"


def route_from_scrum_master(
    state: MessagesState,
) -> Literal["engineer", "product_owner", "end"]:
    messages = state["messages"]
    last_message = messages[-1]

    if "FINAL:" in last_message.content:
        return "end"

    if "CLARIFY_WITH_PO" in last_message.content:
        return "product_owner"

    return "engineer"


async def wait_for_user():
    # Do nothing. Just pause.
    return {}


graph = StateGraph(MessagesState)

graph.add_node("product_owner", product_owner_agent)
graph.add_node("scrum_master", scrum_orchestrator_agent)
graph.add_node("engineer", software_engineer_agent)
graph.add_node("tools", tool_node)
graph.add_node("wait_for_user", wait_for_user)

# Entry
graph.add_edge(START, "product_owner")
graph.add_edge("wait_for_user", END)

graph.add_conditional_edges(
    "product_owner",
    route_from_product_owner,
    {
        "scrum_master": "scrum_master",
        "wait_for_user": "wait_for_user",
    },
)

graph.add_conditional_edges(
    "scrum_master",
    route_from_scrum_master,
    {
        "engineer": "engineer",
        "product_owner": "product_owner",
        "end": END,
    },
)

# Conditional routing from engineer
graph.add_conditional_edges(
    "engineer",
    route_from_engineer,
    {
        "tools": "tools",
        "scrum_master": "scrum_master",
    },
)
# Tool returns to engineer
graph.add_edge("tools", "engineer")

graph = graph.compile()


@cl.on_message
async def on_message(user_msg: cl.Message):
    config = {"configurable": {"thread_id": cl.context.session.id}}
    cb = cl.LangchainCallbackHandler()
    final_answer = cl.Message(content="")

    # Include only the new human message; previous context is preserved via thread_id
    inputs = {"messages": [HumanMessage(content=user_msg.content)]}

    async for msg, metadata in graph.astream(
        inputs, stream_mode="messages", config=RunnableConfig(callbacks=[cb], **config)
    ):
        if isinstance(msg, HumanMessage):
            continue  # skip user messages

        node = metadata.get("langgraph_node", "")
        if msg.content and node in ["product_owner", "scrum_master", "engineer"]:
            await final_answer.stream_token(msg.content)

        # Optionally detect wait_for_user node
        if node == "wait_for_user":
            continue

    await final_answer.send()
