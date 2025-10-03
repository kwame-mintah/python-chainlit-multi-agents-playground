import chainlit as cl
from agent import agent


@cl.on_message
async def main(message: cl.Message):
    # Your custom logic goes here...

    response = agent.invoke(
        {"messages": [{"role": "user", "content": message.content}]}
    )

    print(response)

    # Send a response back to the user
    await cl.Message(
        content=response['messages'][-1].content,
    ).send()
