# Web search tool integration with DIAL API
# Provides a tool for LLM agents to search the web via Google Search through the DIAL proxy service.
# Uses Gemini 2.5 Pro model with static Google Search function for grounded responses.

from typing import Any

import requests

from task.tools.base import BaseTool


class WebSearchTool(BaseTool):
    """
    Tool that enables LLM agents to perform web searches via DIAL API.
    
    Execution flow:
    - Receives a search query from the LLM agent
    - Constructs a request with Google Search tool configuration
    - Sends to DIAL proxy using Gemini 2.5 Pro deployment
    - Extracts and returns grounded search results
    """

    def __init__(self, api_key: str, endpoint: str):
        """
        Initialize web search tool with DIAL API credentials.
        
        Args:
            api_key: API key for DIAL service authentication
            endpoint: Base DIAL proxy endpoint (e.g., https://ai-proxy.lab.epam.com)
        """
        self.__api_key = api_key
        self.__endpoint = f"{endpoint}/openai/deployments/gemini-2.5-pro/chat/completions"

    # https://dialx.ai/dial_api#operation/sendChatCompletionRequest (-> tools -> function)
    # Sample of tool config:
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "web_search_tool",
    #         "description": "Tool for WEB searching.",
    #         "parameters": {
    #             "type": "object",
    #             "properties": {
    #                 "request": {
    #                     "type": "string",
    #                     "description": "The search query or question to search for on the web"
    #                 }
    #             },
    #             "required": [
    #                 "request"
    #             ]
    #         }
    #     }
    # }

    @property
    def name(self) -> str:
        """Unique identifier for this tool as seen by the LLM."""
        return "web_search_tool"

    @property
    def description(self) -> str:
        """User-facing description of what this tool does. Guides LLM when to use it."""
        return "Tool for searching the web using Google Search. Use this to find information online about people, companies, or any topic."

    @property
    def input_schema(self) -> dict[str, Any]:
        """
        JSON schema defining the tool's input parameters for DIAL API.
        
        Returns:
            Dictionary with OpenAI function-calling format defining 'request' string parameter.
        """
        return {
            "type": "object",
            "properties": {
                "request": {
                    "type": "string",
                    "description": "The search query or question to search for on the web"
                }
            },
            "required": ["request"]
        }

    def execute(self, arguments: dict[str, Any]) -> str:
        """
        Execute web search via DIAL API with Google Search grounding.
        
        Args:
            arguments: Dictionary containing 'request' key with search query string
            
        Returns:
            Search result content on success, or error message with status code/details on failure.
            
        Error handling:
            - Non-200 HTTP responses return error string with status code and response text
            - Missing choices or message content return descriptive fallback messages
        """
        # Step 1: Prepare authentication headers for DIAL API
        headers = {
            "api-key": self.__api_key,
            "Content-Type": "application/json"
        }
        
        # Step 2: Build request payload with user search query and Google Search tool configuration
        # The static_function type tells DIAL to use built-in Google Search capability
        request_data = {
            "messages": [{"role": "user", "content": str(arguments["request"])}],
            "tools": [
                {
                    "type": "static_function",
                    "static_function": {
                        "name": "google_search",
                        "description": "Grounding with Google Search",
                        "configuration": {}
                    }
                }
            ]
        }
        
        # Step 3: Send POST request to DIAL proxy (Gemini model will process with web grounding)
        response = requests.post(url=self.__endpoint, headers=headers, json=request_data)
        
        # Step 4: Parse response and extract search results, with graceful error handling
        if response.status_code == 200:
            response_json = response.json()
            choices = response_json.get("choices", [])
            if choices:
                message = choices[0].get("message", {})
                return message.get("content", "No content in response")
            return "No choices in response"
        else:
            # Network or API error: return error details for debugging
            return f"Error: {response.status_code} {response.text}"
