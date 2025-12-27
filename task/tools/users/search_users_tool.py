from typing import Any

from task.tools.users.base import BaseUserServiceTool


class SearchUsersTool(BaseUserServiceTool):

    @property
    def name(self) -> str:
        #TODO: Provide tool name as `search_users`
        return "search_users"

    @property
    def description(self) -> str:
        #TODO: Provide description of this tool
        return "Searches for users based on optional filter criteria. Can search by name, surname, email, or gender. All parameters are optional."

    @property
    def input_schema(self) -> dict[str, Any]:
        #TODO:
        # Provide tool params Schema:
        # - name: str
        # - surname: str
        # - email: str
        # - gender: str
        # None of them are required (see UserClient.search_users method)
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
        #TODO:
        # 1. Call user_client search_users (with `**arguments`) and return its results
        # 2. Optional: You can wrap it with `try-except` and return error as string `f"Error while searching users: {str(e)}"`
        try:
            return self._user_client.search_users(**arguments)
        except Exception as e:
            return f"Error while searching users: {str(e)}"
