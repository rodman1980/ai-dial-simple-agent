"""
DIAL API Client for OpenAI-compatible chat completions with tool calling.

This module handles all communication with EPAM's DIAL proxy service, implementing
the OpenAI chat completions API with support for function calling (tool execution).
It manages the request/response cycle, tool invocation, and recursive calls when
tools are used to gather information for follow-up responses.
"""

import json
from typing import Any

import requests

from task.models.message import Message
from task.models.role import Role
from task.tools.base import BaseTool


class DialClient:
    """
    Client for DIAL API chat completions with integrated tool support.
    
    Manages OpenAI-compatible API calls to EPAM's DIAL service with:
    - Multi-turn conversation history management
    - Tool registration and schema preparation
    - Recursive tool calling: if AI requests tools, execute and recursively call API
    - Error handling for HTTP and unknown function calls
    
    Key design: When finish_reason='tool_calls', the response is processed recursively:
    AI message → extract tools → execute tools → add tool results → call API again
    This allows the AI to gather information and refine responses.
    """

    def __init__(
            self,
            endpoint: str,
            deployment_name: str,
            api_key: str,
            tools: list[BaseTool] | None = None
    ):
        """
        Initialize DIAL client with API credentials and tools.
        
        Args:
            endpoint: DIAL proxy base URL (e.g., https://ai-proxy.lab.epam.com)
            deployment_name: Model deployment name in DIAL (e.g., "gpt-4o")
            api_key: DIAL authentication token from environment
            tools: List of BaseTool instances available to the AI
        
        Raises:
            ValueError: If api_key is not provided (required for DIAL authentication)
        """
        # Validate API key before proceeding; all requests require authentication
        if not api_key:
            raise ValueError("API key is required")
        
        # Build full endpoint URL following OpenAI API format
        # DIAL proxy mirrors OpenAI's deployment-based routing
        self.__endpoint = f"{endpoint}/openai/deployments/{deployment_name}/chat/completions"
        self.__api_key = api_key
        
        # Index tools by name for fast lookup when processing tool calls from API response
        # format: {"get_user_by_id": GetUserByIdTool(), ...}
        self.__tools_dict = {tool.name: tool for tool in (tools or [])}
        
        # Extract and prepare tool schemas for sending to DIAL API
        # AI uses these schemas to decide when and how to call tools
        self.__tools = [tool.schema for tool in (tools or [])]
        
        # Debug output: helps verify correct endpoint and available tools
        print(f"DIAL Endpoint: {self.__endpoint}")
        print(f"Tools: {[tool.name for tool in (tools or [])]}")


    def get_completion(self, messages: list[Message], print_request: bool = True) -> Message:
        """
        Get AI response from DIAL API, with automatic tool calling support.
        
        Implements agentic loop: if AI responds with tool_calls, this method
        recursively executes tools and re-calls the API with results, continuing
        until the AI produces a final response (finish_reason != 'tool_calls').
        
        Args:
            messages: Conversation history (system, user, assistant, tool messages)
            print_request: If True, logs request payload for debugging
        
        Returns:
            Message: Final assistant response (role=AI, content=text answer, tool_calls=None)
        
        Raises:
            Exception: HTTP errors from DIAL API or malformed responses
        
        Network I/O: Makes POST request to DIAL endpoint; requires VPN access
        Recursion: May call itself if finish_reason='tool_calls' (agentic behavior)
        """
        # Prepare API request headers with authentication
        headers = {
            "api-key": self.__api_key,
            "Content-Type": "application/json"
        }
        
        # Prepare request body: serialize messages and include tool schemas
        # Schemas tell AI what tools are available and how to call them
        request_data = {
            "messages": [msg.to_dict() for msg in messages],
            "tools": self.__tools
        }
        
        # Debug output: helpful for tracing conversation flow
        if print_request:
            print(f"\n{'='*50}\nREQUEST:\n{json.dumps(request_data, indent=2)}\n{'='*50}")
        
        # Make network call to DIAL API; may fail if VPN disconnected or quota exceeded
        response = requests.post(
            url=self.__endpoint,
            headers=headers,
            json=request_data
        )
        
        # Only proceed if API returned successful response
        if response.status_code == 200:
            response_json = response.json()
            choices = response_json.get("choices", [])
            choice = choices[0]
            
            # Debug output: shows raw response for troubleshooting
            print(f"\nCHOICE:\n{json.dumps(choice, indent=2)}")
            
            # Extract message components from API response
            message_data = choice.get("message", {})
            content = message_data.get("content", "")  # Fallback to empty if no content
            tool_calls = message_data.get("tool_calls")  # None if AI didn't call tools
            
            # Create assistant message from API response
            ai_response = Message(
                role=Role.AI,
                content=content,
                tool_calls=tool_calls
            )
            
            # Key decision point: Check if AI wants to use tools or is done
            finish_reason = choice.get("finish_reason")
            if finish_reason == "tool_calls":
                # AGENTIC LOOP: AI called tools, so execute them and ask AI again
                # 1. Add AI's request to history (proves AI called a tool)
                messages.append(ai_response)
                # 2. Execute the tool calls and get results
                tool_messages = self._process_tool_calls(tool_calls)
                # 3. Add tool results to history for AI to see
                messages.extend(tool_messages)
                # 4. Recursively call API with extended history; AI can now refine response
                return self.get_completion(messages, print_request)
            else:
                # AI finished without needing tools; return final response
                return ai_response
        else:
            # HTTP error: API returned non-200 status (auth failure, rate limit, etc.)
            raise Exception(f"HTTP {response.status_code}: {response.text}")


    def _process_tool_calls(self, tool_calls: list[dict[str, Any]]) -> list[Message]:
        """
        Execute tools requested by AI and prepare tool result messages.
        
        For each tool call in the AI response:
        1. Extract tool name and parsed arguments from OpenAI format
        2. Execute the tool via _call_tool()
        3. Wrap result in Message with tool_call_id linking to the AI's request
        
        Args:
            tool_calls: List of tool call objects from API response[choices][message][tool_calls]
                       Each has: id, function.name, function.arguments (JSON string)
        
        Returns:
            List of Message objects with role=TOOL, ready to add to conversation history
        
        Critical: tool_call_id in Message MUST match id from AI's tool_calls list.
        If missing/mismatched, AI receives error: "Tool message with id X not found".
        """
        tool_messages = []
        for tool_call in tool_calls:
            # Extract tool call details from API response structure
            tool_call_id = tool_call.get("id")  # Unique ID linking this call to AI request
            function = tool_call.get("function")
            function_name = function.get("name")  # Tool to invoke (e.g., "get_user_by_id")
            # Arguments come as JSON string from API; parse to dict for tool execution
            arguments = json.loads(function.get("arguments"))
            
            # Execute the tool with parsed arguments; returns string result or error message
            tool_execution_result = self._call_tool(function_name, arguments)
            
            # Create tool result message with critical tool_call_id reference
            # This links the result back to the AI's request in the conversation
            tool_messages.append(Message(
                role=Role.TOOL,
                name=function_name,
                tool_call_id=tool_call_id,  # MUST match AI's tool_call[i][id]
                content=tool_execution_result
            ))
            
            # Debug output: shows which tools were called and their results
            print(f"FUNCTION '{function_name}'\n{tool_execution_result}\n{'-'*50}")

        return tool_messages

    def _call_tool(self, function_name: str, arguments: dict[str, Any]) -> str:
        """
        Execute a named tool with given arguments.
        
        Args:
            function_name: Tool name to look up (e.g., "get_user_by_id")
            arguments: Dict of arguments parsed from tool_calls[function.arguments]
        
        Returns:
            String result from tool.execute(arguments), or error message if tool not found
        
        Design: Graceful fallback to error string (not raising exception)
        allows conversation to continue with AI handling the error.
        """
        # Look up tool in registry by name (built during __init__)
        tool = self.__tools_dict.get(function_name)
        if tool:
            # Execute tool and return result (may be success data or error message string)
            return tool.execute(arguments)
        else:
            # Tool not found; return error message for AI to see and explain to user
            return f"Unknown function: {function_name}"
