from typing import Literal

import chainlit as cl
from langchain.schema.runnable.config import RunnableConfig
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from langgraph.graph import END, StateGraph, START
from langgraph.graph.message import MessagesState

from config import environment_variables
from tools import final_model, tool_node
from utils import get_inference_model


def should_continue(state: MessagesState) -> Literal["tools", "final"]:
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return "final"


async def call_model(state: MessagesState) -> dict:
    model = get_inference_model(
        model_provider=environment_variables.LLM_INFERENCE_PROVIDER
    )
    messages = state["messages"]
    response = await model.ainvoke(messages)
    if not isinstance(response, BaseMessage):
        raise TypeError(f"Expected BaseMessage, got {type(response)}")
    return {"messages": [response]}


async def call_final_model(state: MessagesState) -> dict:
    messages = state["messages"]
    last_ai_message = messages[-1]

    response = await final_model.ainvoke(
        [
            SystemMessage(content="Rewrite this in the voice of Al Roker"),
            HumanMessage(content=last_ai_message.content),
        ]
    )

    if not isinstance(response, BaseMessage):
        raise TypeError(f"Expected BaseMessage, got {type(response)}")

    # Don't override ID unless absolutely necessary
    return {"messages": [response]}


builder = StateGraph(MessagesState)
builder.add_node("agent", call_model)
builder.add_node("tools", tool_node)
builder.add_node("final", call_final_model)

builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", should_continue)
builder.add_edge("tools", "agent")
builder.add_edge("final", END)

graph = builder.compile()


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
