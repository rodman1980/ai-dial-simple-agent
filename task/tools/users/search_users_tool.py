# Tool for querying users from the user service with optional filter criteria.
# Supports filtering by name, surname, email, and gender—all parameters are optional.

from typing import Any

from task.tools.users.base import BaseUserServiceTool


class SearchUsersTool(BaseUserServiceTool):

    @property
    def name(self) -> str:
        """Unique identifier for the tool as referenced by the LLM."""
        return "search_users"

    @property
    def description(self) -> str:
        """Natural language description used by the LLM to understand tool purpose and when to use it."""
        return "Searches for users based on optional filter criteria. Can search by name, surname, email, or gender. All parameters are optional."

    @property
    def input_schema(self) -> dict[str, Any]:
        """
        JSON schema defining the search filters the LLM can provide.
        
        All filter parameters (name, surname, email, gender) are optional,
        allowing flexible searches from simple name-only queries to complex multi-filter combinations.
        """
        return {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Filter by user's first name"
                },
                "surname": {
                    "type": "string",
                    "description": "Filter by user's last name"
                },
                "email": {
                    "type": "string",
                    "description": "Filter by user's email address"
                },
                "gender": {
                    "type": "string",
                    "description": "Filter by user's gender"
                }
            },
            "required": []
        }

    def execute(self, arguments: dict[str, Any]) -> str:
        """
        Execute a user search with the provided filter criteria.
        
        Args:
            arguments: Dictionary of optional filter parameters (name, surname, email, gender)
        
        Returns:
            Markdown-formatted string with matching users, or error message on failure.
        
        Raises:
            Returns error as formatted string rather than raising exception to ensure
            graceful LLM integration. The user service client handles HTTP errors and formatting.
        """
        try:
            # Delegate to user_client with unpacked filter arguments
            return self._user_client.search_users(**arguments)
        except Exception as e:
            # Return error as string to maintain consistent tool output contract
            return f"Error while searching users: {str(e)}"
