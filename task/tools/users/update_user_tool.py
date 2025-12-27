# Tool for updating existing user records in the user service.
# Accepts a user ID and optional fields to update—only specified fields are modified.

from typing import Any

from task.tools.users.base import BaseUserServiceTool
from task.tools.users.models.user_info import UserUpdate


class UpdateUserTool(BaseUserServiceTool):

    @property
    def name(self) -> str:
        """Unique identifier for the tool as referenced by the LLM."""
        return "update_user"

    @property
    def description(self) -> str:
        """Natural language description used by the LLM to understand tool purpose and when to use it."""
        return "Updates an existing user's information by user ID. All fields are optional - only provide the fields you want to update."

    @property
    def input_schema(self) -> dict[str, Any]:
        """
        JSON schema defining update parameters the LLM can provide.
        
        Schema contains two required fields:
        - id: Target user ID (numeric)
        - new_info: Object with optional user fields to update (name, email, gender, etc.)
        
        Only fields provided in new_info are updated; absent fields remain unchanged.
        """
        # Extract UserUpdate schema for nested field validation
        user_update_schema = UserUpdate.model_json_schema()
        return {
            "type": "object",
            "properties": {
                "id": {
                    "type": "number",
                    "description": "User ID that should be updated"
                },
                "new_info": user_update_schema
            },
            "required": ["id", "new_info"]
        }

    def execute(self, arguments: dict[str, Any]) -> str:
        """
        Execute a user update with provided ID and field values.
        
        Args:
            arguments: Dictionary containing 'id' (int) and 'new_info' (dict) with fields to update.
        
        Returns:
            Markdown-formatted string with updated user details, or error message on failure.
        
        Raises:
            Returns error as formatted string rather than raising exception to ensure
            graceful LLM integration. Handles validation and HTTP errors gracefully.
        """
        try:
            # Extract and convert user ID to integer (comes as number from JSON schema)
            user_id = int(arguments["id"])
            # Validate update payload against UserUpdate model to catch invalid fields early
            new_info = UserUpdate.model_validate(arguments["new_info"])
            # Delegate to user_client which handles the HTTP PATCH request
            return self._user_client.update_user(user_id, new_info)
        except Exception as e:
            # Return error as string to maintain consistent tool output contract
            return f"Error while updating user: {str(e)}"
