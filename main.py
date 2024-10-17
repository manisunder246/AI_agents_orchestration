import asyncio
from setup_agents_and_plugins import setup_agents
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.contents.utils.author_role import AuthorRole

async def main():
    print("Welcome to the AI Assistant! Type 'exit' to quit.")
    
    while True:
        user_input = input("Your query: ")

        if user_input.lower() == 'exit':
            print("Exiting the assistant. Goodbye!")
            break

        # Set up agents and plugins after capturing user input
        agent_group_chat, agents = await setup_agents(user_input)

        # Create a message object for the user input
        user_message = ChatMessageContent(role=AuthorRole.USER, content=user_input)

        # Add user message to the agent group chat
        await agent_group_chat.add_chat_message(user_message)

        # Process the chat and retrieve responses asynchronously
        async for response in agent_group_chat.invoke():
            print(f"Response: {response}")

if __name__ == "__main__":
    asyncio.run(main())

