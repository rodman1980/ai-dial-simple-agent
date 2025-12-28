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
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of users to return (helps avoid overloading context)",
                    "minimum": 1,
                    "maximum": 25
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
            # Validate optional 'limit' argument if provided and coerce to int
            kwargs = dict(arguments)
            if "limit" in kwargs and kwargs["limit"] is not None:
                try:
                    limit_val = int(kwargs["limit"])
                except Exception:
                    return "Error: 'limit' must be an integer"
                if limit_val < 1:
                    return "Error: 'limit' must be >= 1"
                # enforce an upper bound to protect context
                if limit_val > 100:
                    limit_val = 100
                kwargs["limit"] = limit_val

            # Delegate to user_client with validated arguments
            return self._user_client.search_users(**kwargs)
        except Exception as e:
            # Return error as string to maintain consistent tool output contract
            return f"Error while searching users: {str(e)}"
