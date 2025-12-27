# Abstract base class defining the tool interface for AI agent integration.
# Provides contract for all tool implementations to expose execution logic,
# metadata (name, description), input validation schema, and OpenAI-compatible
# function calling schema.

from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):
    """Abstract base class for AI agent tools.
    
    Defines the interface that all tools must implement for integration with the
    DIAL API and the AI agent's tool calling system. Subclasses must provide
    execution logic, tool metadata, and JSON Schema for input validation.
    """

    @abstractmethod
    def execute(self, arguments: dict[str, Any]) -> str:
        """Execute the tool's core logic with provided arguments.
        
        Args:
            arguments: Tool-specific keyword arguments validated against input_schema.
            
        Returns:
            String result (formatted data or error message). Always returns string
            for consistent message integration in the conversation flow.
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool identifier used by the AI agent for function calling.
        
        Returns:
            Unique tool name (e.g., "add_user", "search_users").
        """
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Natural language description of tool purpose and capabilities.
        
        Used by the AI model for function selection and planning. Should clearly
        explain what the tool does and when it should be called.
        
        Returns:
            Human-readable tool description.
        """
        pass

    @property
    @abstractmethod
    def input_schema(self) -> dict[str, Any]:
        """JSON Schema validating the tool's input arguments.
        
        Typically generated from Pydantic models using model_json_schema() to ensure
        type safety and provide the AI model with parameter requirements.
        
        Returns:
            JSON Schema dict conforming to OpenAI function calling format.
        """
        pass

    @property
    def schema(self) -> dict[str, Any]:
        """OpenAI-compatible function calling schema.
        
        Wraps tool metadata (name, description, input schema) into the format
        expected by the DIAL API for function calling. This schema tells the
        AI model what tools are available and how to call them.
        
        Returns:
            Structured function schema dict for OpenAI chat completions API.
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.input_schema
            }
        }