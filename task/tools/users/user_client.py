"""
User Service Client module.

Provides HTTP-based CRUD operations for managing users via the user service API.
Handles serialization of user data to markdown-formatted strings for LLM consumption.
"""

from typing import Any, Optional

import requests

from task.tools.users.models.user_info import UserCreate, UserUpdate

# User service base URL (mock service running on localhost)
USER_SERVICE_ENDPOINT = "http://localhost:8041"


class UserClient:
    """HTTP client for user service CRUD operations.
    
    Handles communication with the user service API and formats responses
    as markdown strings for optimal LLM readability.
    """

    def __user_to_string(self, user: dict[str, Any]):
        """Format a single user dict as a markdown code block.
        
        Args:
            user: Dictionary containing user data with string keys and any-type values.
            
        Returns:
            Formatted markdown string with user data in a code block for LLM readability.
        """
        user_str = "```\n"
        # Iterate over user fields and format each as "key: value" pairs
        for key, value in user.items():
            user_str += f"  {key}: {value}\n"
        user_str += "```\n"

        return user_str

    def __users_to_string(self, users: list[dict[str, Any]]):
        """Format a list of user dicts as markdown code blocks.
        
        Args:
            users: List of dictionaries containing user data.
            
        Returns:
            Concatenated markdown string with all users formatted in code blocks.
        """
        users_str = ""
        # Format each user using the single user formatter
        for value in users:
            users_str += self.__user_to_string(value)
        users_str += "\n"

        return users_str

    def get_user(self, user_id: int) -> str:
        """Retrieve a single user by ID.
        
        Args:
            user_id: Numeric identifier for the user to retrieve.
            
        Returns:
            Formatted markdown string with user data on success.
            
        Raises:
            Exception: On HTTP error (non-200 status code).
        """
        headers = {"Content-Type": "application/json"}

        # GET request to retrieve user by ID
        response = requests.get(url=f"{USER_SERVICE_ENDPOINT}/v1/users/{user_id}", headers=headers)

        if response.status_code == 200:
            data = response.json()
            return self.__user_to_string(data)

        # Propagate HTTP error to caller
        raise Exception(f"HTTP {response.status_code}: {response.text}")

    def search_users(
            self,
            name: Optional[str] = None,
            surname: Optional[str] = None,
            email: Optional[str] = None,
            gender: Optional[str] = None,
            limit: Optional[int] = None,
    ) -> str:
        """Search for users by optional filter criteria.
        
        Args:
            name: Optional user first name to filter by.
            surname: Optional user last name to filter by.
            email: Optional user email to filter by.
            gender: Optional user gender to filter by.
            
        Returns:
            Formatted markdown string with matching users; includes count logged to stdout.
            Returns empty markdown for zero matches.
            
        Raises:
            Exception: On HTTP error (non-200 status code).
        """
        headers = {"Content-Type": "application/json"}

        # Build query params from provided filter criteria (omit None values)
        params = {}
        if name:
            params["name"] = name
        if surname:
            params["surname"] = surname
        if email:
            params["email"] = email
        if gender:
            params["gender"] = gender

        # GET request to search endpoint with filters as query parameters
        response = requests.get(url=USER_SERVICE_ENDPOINT + "/v1/users/search", headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            # Log match count for debugging/monitoring purposes
            total = len(data)
            print(f"Get {total} users successfully")

            # If a limit is provided, trim the results to avoid large context
            if limit is not None:
                try:
                    limit_val = int(limit)
                except Exception:
                    raise Exception("'limit' must be an integer")
                if limit_val < 1:
                    raise Exception("'limit' must be >= 1")
                # enforce safe upper bound
                if limit_val > 100:
                    limit_val = 100

                if total > limit_val:
                    data = data[:limit_val]
                    print(f"Trimmed users to {limit_val} results to protect context")

            return self.__users_to_string(data)

        # Propagate HTTP error to caller
        raise Exception(f"HTTP {response.status_code}: {response.text}")

    def add_user(self, user_create_model: UserCreate) -> str:
        """Create a new user in the service.
        
        Args:
            user_create_model: Pydantic UserCreate model containing required user fields.
            
        Returns:
            Success message with raw service response on creation (201).
            
        Raises:
            Exception: On HTTP error (non-201 status code).
        """
        headers = {"Content-Type": "application/json"}

        # POST request to create user; serialize Pydantic model to JSON
        response = requests.post(
            url=f"{USER_SERVICE_ENDPOINT}/v1/users",
            headers=headers,
            json=user_create_model.model_dump()
        )

        if response.status_code == 201:
            return f"User successfully added: {response.text}"

        # Propagate HTTP error to caller
        raise Exception(f"HTTP {response.status_code}: {response.text}")

    def update_user(self, user_id: int, user_update_model: UserUpdate) -> str:
        """Update an existing user by ID.
        
        Args:
            user_id: Numeric identifier for the user to update.
            user_update_model: Pydantic UserUpdate model with fields to modify.
            
        Returns:
            Success message with raw service response on update (201).
            
        Raises:
            Exception: On HTTP error (non-201 status code).
        """
        headers = {"Content-Type": "application/json"}

        # PUT request to update user; serialize Pydantic model to JSON
        response = requests.put(
            url=f"{USER_SERVICE_ENDPOINT}/v1/users/{user_id}",
            headers=headers,
            json=user_update_model.model_dump()
        )

        if response.status_code == 201:
            return f"User successfully updated: {response.text}"

        # Propagate HTTP error to caller
        raise Exception(f"HTTP {response.status_code}: {response.text}")

    def delete_user(self, user_id: int) -> str:
        """Delete a user by ID.
        
        Args:
            user_id: Numeric identifier for the user to delete.
            
        Returns:
            Success message on deletion (204 No Content).
            
        Raises:
            Exception: On HTTP error (non-204 status code).
        """
        headers = {"Content-Type": "application/json"}

        # DELETE request to remove user; expects 204 No Content on success
        response = requests.delete(url=f"{USER_SERVICE_ENDPOINT}/v1/users/{user_id}", headers=headers)

        if response.status_code == 204:
            return "User successfully deleted"

        # Propagate HTTP error to caller
        raise Exception(f"HTTP {response.status_code}: {response.text}")
