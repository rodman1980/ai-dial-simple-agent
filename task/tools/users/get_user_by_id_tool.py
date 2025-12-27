# Tool for retrieving user information by ID from the user service.
#
# Provides LLM-callable function to fetch detailed user records by unique identifier.
# Returns formatted user data or error messages for LLM consumption.

from typing import Any

from task.tools.users.base import BaseUserServiceTool


class GetUserByIdTool(BaseUserServiceTool):
    """
    Tool for retrieving user details by their unique ID.
    
    Queries the user service for a specific user record and returns formatted
    user information. Handles errors gracefully to maintain conversational flow.
    """

    @property
    def name(self) -> str:
        """Tool identifier for function calling in DIAL API."""
        return "get_user_by_id"

    @property
    def description(self) -> str:
        """User-facing description of tool capability."""
        return "Retrieves detailed information about a specific user by their ID."

    @property
    def input_schema(self) -> dict[str, Any]:
        """
        JSON schema for tool input validation.
        
        Requires a single parameter: user ID (number) to identify which user to retrieve.
        """
        return {
            "type": "object",
            "properties": {
                "id": {
                    "type": "number",
                    "description": "User ID to retrieve"
                }
            },
            "required": ["id"]
        }

    def execute(self, arguments: dict[str, Any]) -> str:
        """
        Retrieve detailed information for a specific user.
        
        Args:
            arguments (dict[str, Any]): Dict containing 'id' key with numeric user ID.
        
        Returns:
            str: Markdown-formatted user data on success, or error message on failure.
        
        Flow:
            1. Extract and convert 'id' from arguments to integer
            2. Call user_client.get_user() to fetch user record from service
            3. Return formatted user data or catch exceptions as error strings
        
        Note:
            Returns empty result if user ID does not exist in service.
        """
        try:
            # Convert ID to integer for user service API compatibility
            user_id = int(arguments["id"])
            # Delegate to user client for HTTP GET request to user service
            return self._user_client.get_user(user_id)
        except Exception as e:
            # Return error message instead of raising to maintain conversational flow
            return f"Error while retrieving user by id: {str(e)}"