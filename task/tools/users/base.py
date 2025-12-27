# Base class for user service tools providing shared access to the user client.
# 
# This module defines the abstract base for all user service tools (create, read, update, delete).
# It ensures consistent access patterns to the UserClient across all user-related operations.

from abc import ABC

from task.tools.base import BaseTool
from task.tools.users.user_client import UserClient


class BaseUserServiceTool(BaseTool, ABC):
    """
    Abstract base class for user service tools.
    
    Provides shared UserClient instance for CRUD operations on the user service.
    Inherits from BaseTool to integrate with the tool system and support function calling.
    """

    def __init__(self, user_client: UserClient):
        """
        Initialize the base user service tool.
        
        Args:
            user_client (UserClient): Client instance for communicating with the user service.
        """
        super().__init__()
        # Store reference to user client for subclasses to use in execute() implementations
        self._user_client = user_client
