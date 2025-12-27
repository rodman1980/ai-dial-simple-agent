"""
DIAL-powered User Management Agent.

This module implements an interactive AI agent that connects to EPAM's DIAL proxy service
and provides user management capabilities through natural language interactions. The agent
maintains conversation history and uses integrated tools to perform CRUD operations on users
and web search operations.

Key responsibilities:
- Initialize the DIAL client with configured tools
- Manage multi-turn conversation history
- Process user input and retrieve AI responses
- Handle graceful shutdown and error cases
"""

import os

from task.client import DialClient
from task.models.conversation import Conversation
from task.models.message import Message
from task.models.role import Role
from task.prompts import SYSTEM_PROMPT
from task.tools.users.create_user_tool import CreateUserTool
from task.tools.users.delete_user_tool import DeleteUserTool
from task.tools.users.get_user_by_id_tool import GetUserByIdTool
from task.tools.users.search_users_tool import SearchUsersTool
from task.tools.users.update_user_tool import UpdateUserTool
from task.tools.users.user_client import UserClient
from task.tools.web_search import WebSearchTool

# DIAL API configuration
DIAL_ENDPOINT = "https://ai-proxy.lab.epam.com"
# API key retrieved from environment; required for DIAL proxy authentication
API_KEY = os.getenv('DIAL_API_KEY')

def main():
    """
    Initialize and run the interactive user management agent.
    
    Execution flow:
    1. Creates a UserClient for accessing the mock user service (http://localhost:8041)
    2. Initializes DialClient with all available tools (user CRUD + web search)
    3. Sets up conversation with system prompt defining agent behavior
    4. Enters REPL loop: reads user input → sends to AI → displays response
    5. Handles graceful shutdown on 'exit'/'quit' or KeyboardInterrupt
    
    Tool integration:
    - GetUserByIdTool: Retrieves a user by ID
    - SearchUsersTool: Searches/lists users
    - CreateUserTool: Adds a new user
    - UpdateUserTool: Modifies existing user
    - DeleteUserTool: Removes a user
    - WebSearchTool: Performs web searches (optional enhancement)
    
    Raises:
    - Exception: Network/API errors are caught and logged without terminating
    """
    # Initialize client for the mock user service (runs on port 8041 via Docker)
    user_client = UserClient()
    
    # Register all available tools with DialClient; AI can invoke these as needed
    tools = [
        WebSearchTool(api_key=API_KEY, endpoint=DIAL_ENDPOINT),
        GetUserByIdTool(user_client),
        SearchUsersTool(user_client),
        CreateUserTool(user_client),
        UpdateUserTool(user_client),
        DeleteUserTool(user_client)
    ]
    
    # Create DIAL client configured for gpt-4o model with tools support
    dial_client = DialClient(
        endpoint=DIAL_ENDPOINT,
        deployment_name="gpt-4o",
        api_key=API_KEY,
        tools=tools
    )
    
    # Initialize conversation with system prompt to establish agent's role and behavior
    conversation = Conversation()
    conversation.add_message(Message(role=Role.SYSTEM, content=SYSTEM_PROMPT))
    
    print("User Management Agent started. Type 'exit' or 'quit' to stop.")
    print("="*60)
    
    # Main REPL loop: continuously read user input, get AI response, maintain history
    while True:
        try:
            # Read and normalize user input
            user_input = input("> ").strip()
            
            # Check for exit command
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            
            # Skip empty input lines
            if not user_input:
                continue
            
            # Add user message to conversation history
            conversation.add_message(Message(role=Role.USER, content=user_input))
            
            # Call DIAL API with full conversation history for context
            # AI processes tools and previous messages to generate response
            ai_message = dial_client.get_completion(conversation.get_messages(), print_request=False)
            
            # Add AI response to conversation history and display to user
            conversation.add_message(ai_message)
            print(f"\nAssistant: {ai_message.content}\n")
            
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            print("\n\nGoodbye!")
            break
        except Exception as e:
            # Log errors without terminating; user can continue or exit
            print(f"\nError: {str(e)}\n")


if __name__ == "__main__":
    main()