# Tool for deleting users from the user service.
#
# Provides LLM-callable function to delete users by ID with permanent removal.
# Includes error handling and confirmation of destructive action.

from typing import Any

from task.tools.users.base import BaseUserServiceTool


class DeleteUserTool(BaseUserServiceTool):
    """
    Tool for deleting users from the user service.
    
    Accepts a user ID and permanently removes the user record via UserClient.
    Returns confirmation or error message. This is a destructive operation
    with no undo capability.
    """

    @property
    def name(self) -> str:
        """Tool identifier for function calling in DIAL API."""
        return "delete_users"

    @property
    def description(self) -> str:
        """User-facing description emphasizing irreversible nature of deletion."""
        return "Deletes a user by their ID. This action is permanent and cannot be undone."

    @property
    def input_schema(self) -> dict[str, Any]:
        """
        JSON schema for tool input validation.
        
        Requires a single parameter: user ID (number) to identify which user to delete.
        """
        return {
            "type": "object",
            "properties": {
                "id": {
                    "type": "number",
                    "description": "User ID to delete"
                }
            },
            "required": ["id"]
        }

    def execute(self, arguments: dict[str, Any]) -> str:
        """
        Permanently delete a user by their ID.
        
        Args:
            arguments (dict[str, Any]): Dict containing 'id' key with numeric user ID.
        
        Returns:
            str: Confirmation message on success, or error message on failure.
        
        Flow:
            1. Extract and convert 'id' from arguments to integer
            2. Call user_client.delete_user() to remove user from service
            3. Return confirmation or catch exceptions as error strings
        
        Note:
            This operation is permanent. No recovery is possible after execution.
        """
        try:
            # Convert ID to integer for user service API compatibility
            user_id = int(arguments["id"])
            # Delegate to user client for HTTP DELETE request to user service
            return self._user_client.delete_user(user_id)
        except Exception as e:
            # Return error message instead of raising to maintain conversational flow
            return f"Error while deleting user by id: {str(e)}"