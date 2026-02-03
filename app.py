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

    # Extract the structured_response if available, otherwise use message content
    if "structured_response" in response:
        state["product_manager_spec"] = response["structured_response"]
    elif "messages" in response and len(response["messages"]) > 0:
        # Try to parse from message content as fallback
        response_content = response["messages"][-1].content
        try:
            parsed_spec = json.loads(response_content) if isinstance(response_content, str) else response_content
            state["product_manager_spec"] = parsed_spec
        except (json.JSONDecodeError, TypeError):
            state["product_manager_spec"] = response_content
    else:
        state["product_manager_spec"] = str(response)
    
    return state


def dev_node(state: State) -> State:
    # Get the product spec from the previous node's output
    product_spec = state["product_manager_spec"]
    
    # Format the requirements for the developer
    if isinstance(product_spec, dict):
        # Build a comprehensive requirements document
        requirements_doc = f"""
# {product_spec.get('product_name', 'Project Specification')}

## Description
{product_spec.get('description', 'No description provided')}

## Requirements
"""
        for req in product_spec.get('requirements', []):
            requirements_doc += f"""
### {req.get('id', '')} - {req.get('title', '')}
- **Type**: {req.get('type', '')}
- **Priority**: {req.get('priority', '')}
- **Status**: {req.get('status', '')}
- **Description**: {req.get('description', '')}
- **Acceptance Criteria**:
"""
            for ac in req.get('acceptance_criteria', []):
                requirements_doc += f"  - {ac}\n"

        # Add User Stories
        requirements_doc += "\n## User Stories\n"
        for story in product_spec.get('user_stories', []):
            requirements_doc += f"""
### {story.get('id', '')} - {story.get('title', '')}
{story.get('story', '')}
- **Linked Requirements**: {', '.join(story.get('requirements_linked', []))}
- **Status**: {story.get('status', '')}
"""

        # Add Technical Notes
        tech_notes = product_spec.get('technical_notes', {})
        if tech_notes:
            requirements_doc += "\n## Technical Notes\n"
            requirements_doc += f"- **Frontend**: {tech_notes.get('frontend', 'Not specified')}\n"
            requirements_doc += f"- **Backend**: {tech_notes.get('backend', 'Not specified')}\n"
            if tech_notes.get('datamodel'):
                requirements_doc += f"- **Data Model**: {json.dumps(tech_notes.get('datamodel'), indent=2)}\n"

        # Add Next Steps
        next_steps = product_spec.get('next_steps', {})
        if next_steps:
            requirements_doc += "\n## Next Steps\n"
            requirements_doc += f"{next_steps.get('instruction_to_software_engineer', '')}\n"
            requirements_doc += "\n**Initial Tasks**:\n"
            for task in next_steps.get('initial_tasks', []):
                requirements_doc += f"- {task}\n"
            requirements_doc += f"\n**Current Progress**: {next_steps.get('current_progress', 'Not specified')}\n"

        requirements = requirements_doc
    else:
        requirements = str(product_spec)
    
    print("Product Spec for Developer:")
    print(requirements)
    state["requirements"] = requirements

    # Format the input as expected by create_react_agent
    response = software_engineer_agent.invoke({
        "messages": [
            ("system", SoftwareDevelopmentTeamPrompts.software_engineer_prompt()),
            ("human", requirements)
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
