# Tool for creating new users in the user service.
#
# Provides LLM-callable function to create users with validated input fields.
# Handles validation of user data and error reporting.

from typing import Any

from task.tools.users.base import BaseUserServiceTool
from task.tools.users.models.user_info import UserCreate


class CreateUserTool(BaseUserServiceTool):
    """
    Tool for creating new users via the user service.
    
    Validates user creation input against the UserCreate schema and delegates
    to UserClient for persistence. Provides error handling with user-friendly
    error messages for LLM consumption.
    """

    @property
    def name(self) -> str:
        """Tool identifier for function calling in DIAL API."""
        return "add_user"

    @property
    def description(self) -> str:
        """User-facing description of tool capabilities and available fields."""
        return "Creates a new user with the provided information. Required fields: name, surname, email, about_me. Optional fields: phone, date_of_birth, address, gender, company, salary, credit_card."

    @property
    def input_schema(self) -> dict[str, Any]:
        """
        JSON schema for tool input validation.
        
        Returns the Pydantic model schema to ensure LLM provides all required fields
        and validates field types before execution.
        """
        return UserCreate.model_json_schema()

    def execute(self, arguments: dict[str, Any]) -> str:
        """
        Create a new user with the provided data.
        
        Args:
            arguments (dict[str, Any]): Raw arguments from LLM containing user fields.
        
        Returns:
            str: Markdown-formatted user data on success, or error message on failure.
        
        Flow:
            1. Validate arguments against UserCreate schema using Pydantic
            2. Call user_client.add_user() to persist user to service
            3. Return formatted result or catch exceptions as user-friendly error strings
        """
        try:
            # Validate and deserialize arguments to UserCreate model
            user_create = UserCreate.model_validate(arguments)
            # Delegate to user client for HTTP call to user service
            return self._user_client.add_user(user_create)
        except Exception as e:
            # Return error message instead of raising to maintain conversational flow
            return f"Error while creating a new user: {str(e)}"
