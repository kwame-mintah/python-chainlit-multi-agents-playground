from typing import Literal

import chainlit as cl
from langchain.schema.runnable.config import RunnableConfig
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from langgraph.graph import END, StateGraph, START
from langgraph.graph.message import MessagesState

from agents.development import (
    scrum_orchestrator_agent,
    software_engineer_agent,
    product_owner_agent,
)
from agents.prompts import SoftwareDevelopmentTeamPrompts
from agents.tools.tools import final_model


def should_continue(state: MessagesState) -> Literal["tools", "final"]:
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return "final"


async def call_model(state: MessagesState) -> dict:
    messages = state["messages"]
    response = await scrum_orchestrator_agent.ainvoke(messages)
    if not isinstance(response, BaseMessage):
        raise TypeError(f"Expected BaseMessage, got {type(response)}")
    return {"messages": [response]}


async def call_final_model(state: MessagesState) -> dict:
    messages = state["messages"]
    last_ai_message = messages[-1]

    response = await final_model.ainvoke(
        [
            SystemMessage(content=SoftwareDevelopmentTeamPrompts.system_prompt),
            HumanMessage(content=last_ai_message.content),
        ]
    )

    if not isinstance(response, BaseMessage):
        raise TypeError(f"Expected BaseMessage, got {type(response)}")

    # Don't override ID unless absolutely necessary
    return {"messages": [response]}


graph = (
    StateGraph(MessagesState)
    .add_node("development_team", scrum_orchestrator_agent)
    .add_node("software_engineer_agent", software_engineer_agent)
    .add_node("product_owner_agent", product_owner_agent)
    .add_edge(START, "development_team")
    .add_edge("development_team", "software_engineer_agent")
    .add_edge("software_engineer_agent", "product_owner_agent")
    .add_edge("product_owner_agent", END)
    .compile(name="development_team_graph")
)


@cl.on_message
async def on_message(user_msg: cl.Message):
    config = {"configurable": {"thread_id": cl.context.session.id}}
    cb = cl.LangchainCallbackHandler()
    final_answer = cl.Message(content="")

    inputs = {"messages": [HumanMessage(content=user_msg.content)]}

    async for msg, metadata in graph.astream(
        inputs, stream_mode="messages", config=RunnableConfig(callbacks=[cb], **config)
    ):
        if isinstance(msg, HumanMessage):
            continue

        if msg.content and metadata.get("langgraph_node") == "final":
            await final_answer.stream_token(msg.content)

    await final_answer.send()
