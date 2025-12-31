---
title: DIAL Simple Agent - API Reference
description: Comprehensive API documentation for DIAL endpoints, tool schemas, message formats, and integration patterns
version: 1.0.0
last_updated: 2025-12-30
related: [architecture.md, setup.md]
tags: [api, dial, tools, openai, reference]
---

# API Reference

> Complete reference for DIAL API integration, tool schemas, and message formats

## Table of Contents

- [DIAL API](#dial-api)
- [Tool System API](#tool-system-api)
- [User Service API](#user-service-api)
- [Message Format](#message-format)
- [Tool Schemas](#tool-schemas)
- [Error Handling](#error-handling)
- [Code Examples](#code-examples)

## DIAL API

### Base Configuration

```python
DIAL_ENDPOINT = "https://ai-proxy.lab.epam.com"
DEPLOYMENT_NAME = "gpt-4o"  # or "gemini-2.5-pro"
```

### Chat Completions Endpoint

**URL:**
```
POST https://ai-proxy.lab.epam.com/openai/deployments/{deployment_name}/chat/completions
```

**Headers:**
```json
{
  "api-key": "<DIAL_API_KEY>",
  "Content-Type": "application/json"
}
```

**Request Body:**
```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful assistant."
    },
    {
      "role": "user",
      "content": "Find users named John"
    }
  ],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "search_users",
        "description": "Search for users by name, surname, email, or gender",
        "parameters": {
          "type": "object",
          "properties": {
            "name": {
              "type": "string",
              "description": "User's first name"
            },
            "surname": {
              "type": "string",
              "description": "User's last name"
            }
          }
        }
      }
    }
  ],
  "temperature": 0.7,
  "max_tokens": 2000
}
```

**Response (Tool Calls):**
```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1704067200,
  "model": "gpt-4o",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": null,
        "tool_calls": [
          {
            "id": "call_xyz789",
            "type": "function",
            "function": {
              "name": "search_users",
              "arguments": "{\"name\": \"John\"}"
            }
          }
        ]
      },
      "finish_reason": "tool_calls"
    }
  ],
  "usage": {
    "prompt_tokens": 120,
    "completion_tokens": 45,
    "total_tokens": 165
  }
}
```

**Response (Final):**
```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "I found 3 users named John:\n1. John Smith\n2. John Doe\n3. Johnathan Williams"
      },
      "finish_reason": "stop"
    }
  ]
}
```

### Supported Models

| Model | Deployment Name | Best For |
|-------|----------------|----------|
| GPT-4o | `gpt-4o` | General purpose, tool calling, reasoning |
| Gemini 2.5 Pro | `gemini-2.5-pro` | Web search, grounding, multimodal |

### Authentication

**Environment Variable:**
```bash
export DIAL_API_KEY="your-api-key-here"
```

**Python:**
```python
import os
api_key = os.getenv('DIAL_API_KEY')
```

**Request Header:**
```python
headers = {"api-key": api_key}
```

## Tool System API

### BaseTool Interface

All tools must implement the `BaseTool` abstract class:

```python
from abc import ABC, abstractmethod
from typing import Any

class BaseTool(ABC):
    @abstractmethod
    def execute(self, arguments: dict[str, Any]) -> str:
        """Execute tool logic and return string result"""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique tool identifier"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Natural language description for LLM"""
        pass

    @property
    @abstractmethod
    def input_schema(self) -> dict[str, Any]:
        """JSON Schema for input validation"""
        pass

    @property
    def schema(self) -> dict[str, Any]:
        """OpenAI function calling schema"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.input_schema
            }
        }
```

### DialClient API

```python
class DialClient:
    def __init__(
        self,
        endpoint: str,
        deployment_name: str,
        api_key: str,
        tools: list[BaseTool] | None = None
    ):
        """
        Initialize DIAL client.
        
        Args:
            endpoint: DIAL base URL (e.g., https://ai-proxy.lab.epam.com)
            deployment_name: Model name (e.g., "gpt-4o")
            api_key: DIAL authentication key
            tools: List of available tools
        """
        pass

    def get_completion(
        self,
        messages: list[Message],
        print_request: bool = True
    ) -> Message:
        """
        Get AI completion with recursive tool calling.
        
        Args:
            messages: Conversation history
            print_request: Debug flag to log requests
            
        Returns:
            Final assistant message
            
        Raises:
            Exception: HTTP errors or malformed responses
        """
        pass
```

### Conversation API

```python
class Conversation:
    id: str                    # Unique conversation identifier
    messages: list[Message]    # Message history
    
    def add_message(self, message: Message) -> None:
        """Append message to conversation history"""
        pass
    
    def get_messages(self) -> list[Message]:
        """Retrieve all messages in order"""
        pass
```

### Message API

```python
@dataclass
class Message:
    role: Role                              # Message role
    content: str                            # Message content
    tool_call_id: str | None = None        # For tool responses
    name: str | None = None                # Tool name for tool responses
    tool_calls: list[dict] | None = None   # Tool invocations
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to OpenAI format"""
        pass
```

**Roles:**
```python
class Role(StrEnum):
    SYSTEM = "system"      # System instructions
    USER = "user"          # User input
    AI = "assistant"       # AI response
    TOOL = "tool"          # Tool result
```

## User Service API

### Base URL

```
http://localhost:8041
```

### Endpoints

#### Get User by ID

```http
GET /v1/users/{user_id}
Content-Type: application/json
```

**Response:**
```json
{
  "id": 123,
  "name": "John",
  "surname": "Smith",
  "email": "john.smith@example.com",
  "phone": "+1-555-1234",
  "date_of_birth": "1990-01-15",
  "gender": "male",
  "company": "EPAM Systems",
  "salary": 85000.0,
  "about_me": "Software engineer",
  "address": {
    "country": "USA",
    "city": "Boston",
    "street": "Main St 123",
    "flat_house": "Apt 4B"
  },
  "credit_card": {
    "num": "4111111111111111",
    "cvv": "123",
    "exp_date": "12/25"
  }
}
```

#### Search Users

```http
GET /v1/users?name={name}&surname={surname}&email={email}&gender={gender}&limit={limit}
Content-Type: application/json
```

**Query Parameters:**
- `name` (optional): Filter by first name (partial match)
- `surname` (optional): Filter by last name (partial match)
- `email` (optional): Filter by email (partial match)
- `gender` (optional): Filter by gender (exact match)
- `limit` (optional): Maximum results to return

**Response:**
```json
[
  {
    "id": 123,
    "name": "John",
    "surname": "Smith",
    ...
  },
  {
    "id": 456,
    "name": "John",
    "surname": "Doe",
    ...
  }
]
```

#### Create User

```http
POST /v1/users
Content-Type: application/json

{
  "name": "Jane",
  "surname": "Doe",
  "email": "jane.doe@example.com",
  "about_me": "Data scientist",
  "phone": "+1-555-5678",
  "gender": "female",
  "date_of_birth": "1992-05-20",
  "company": "Tech Corp",
  "salary": 95000.0,
  "address": {
    "country": "USA",
    "city": "San Francisco",
    "street": "Market St 456",
    "flat_house": "Unit 12"
  },
  "credit_card": {
    "num": "5500000000000004",
    "cvv": "456",
    "exp_date": "06/26"
  }
}
```

**Response:** Same as GET user

#### Update User

```http
PATCH /v1/users/{user_id}
Content-Type: application/json

{
  "email": "new.email@example.com",
  "phone": "+1-555-9999"
}
```

**Response:** Updated user object

#### Delete User

```http
DELETE /v1/users/{user_id}
```

**Response:**
```json
{
  "message": "User deleted successfully"
}
```

### UserClient Methods

```python
class UserClient:
    def get_user(self, user_id: int) -> str:
        """Retrieve user by ID, return markdown-formatted string"""
        pass
    
    def search_users(
        self,
        name: str | None = None,
        surname: str | None = None,
        email: str | None = None,
        gender: str | None = None,
        limit: int | None = None
    ) -> str:
        """Search users with filters, return markdown list"""
        pass
    
    def add_user(self, user: UserCreate) -> str:
        """Create new user, return markdown confirmation"""
        pass
    
    def update_user(self, user_id: int, updates: UserUpdate) -> str:
        """Update user fields, return updated markdown"""
        pass
    
    def delete_user(self, user_id: int) -> str:
        """Delete user, return markdown confirmation"""
        pass
```

## Message Format

### System Message

```python
Message(
    role=Role.SYSTEM,
    content="You are a User Management Assistant..."
)
```

**OpenAI Format:**
```json
{
  "role": "system",
  "content": "You are a User Management Assistant..."
}
```

### User Message

```python
Message(
    role=Role.USER,
    content="Find users named John"
)
```

**OpenAI Format:**
```json
{
  "role": "user",
  "content": "Find users named John"
}
```

### Assistant Message with Tool Calls

```python
Message(
    role=Role.AI,
    content="",
    tool_calls=[
        {
            "id": "call_abc123",
            "type": "function",
            "function": {
                "name": "search_users",
                "arguments": "{\"name\": \"John\"}"
            }
        }
    ]
)
```

### Tool Result Message

```python
Message(
    role=Role.TOOL,
    tool_call_id="call_abc123",
    name="search_users",
    content="```\n  id: 123\n  name: John\n  surname: Smith\n```"
)
```

## Tool Schemas

### GetUserByIdTool

**Name:** `get_user_by_id`

**Description:** Retrieves a single user by their unique ID

**Schema:**
```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "integer",
      "description": "The unique identifier of the user"
    }
  },
  "required": ["user_id"]
}
```

**Example Call:**
```json
{
  "name": "get_user_by_id",
  "arguments": "{\"user_id\": 123}"
}
```

**Example Result:**
```markdown
```
  id: 123
  name: John
  surname: Smith
  email: john.smith@example.com
```
```

### SearchUsersTool

**Name:** `search_users`

**Description:** Search for users by name, surname, email, or gender

**Schema:**
```json
{
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "description": "User's first name (partial match)"
    },
    "surname": {
      "type": "string",
      "description": "User's last name (partial match)"
    },
    "email": {
      "type": "string",
      "description": "User's email address (partial match)"
    },
    "gender": {
      "type": "string",
      "description": "User's gender (exact match)"
    },
    "limit": {
      "type": "integer",
      "description": "Maximum number of results"
    }
  }
}
```

**Example Call:**
```json
{
  "name": "search_users",
  "arguments": "{\"name\": \"John\", \"limit\": 5}"
}
```

### CreateUserTool

**Name:** `add_user`

**Description:** Creates a new user with provided information

**Schema:**
```json
{
  "type": "object",
  "properties": {
    "name": {"type": "string"},
    "surname": {"type": "string"},
    "email": {"type": "string"},
    "about_me": {"type": "string"},
    "phone": {"type": "string"},
    "date_of_birth": {"type": "string"},
    "gender": {"type": "string"},
    "company": {"type": "string"},
    "salary": {"type": "number"},
    "address": {
      "type": "object",
      "properties": {
        "country": {"type": "string"},
        "city": {"type": "string"},
        "street": {"type": "string"},
        "flat_house": {"type": "string"}
      },
      "required": ["country", "city", "street", "flat_house"]
    },
    "credit_card": {
      "type": "object",
      "properties": {
        "num": {"type": "string"},
        "cvv": {"type": "string"},
        "exp_date": {"type": "string"}
      },
      "required": ["num", "cvv", "exp_date"]
    }
  },
  "required": ["name", "surname", "email", "about_me"]
}
```

### UpdateUserTool

**Name:** `update_user`

**Description:** Updates an existing user's information

**Schema:**
```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "integer",
      "description": "ID of user to update"
    },
    "name": {"type": "string"},
    "surname": {"type": "string"},
    "email": {"type": "string"},
    "phone": {"type": "string"},
    "date_of_birth": {"type": "string"},
    "gender": {"type": "string"},
    "company": {"type": "string"},
    "salary": {"type": "number"},
    "address": {"type": "object"},
    "credit_card": {"type": "object"}
  },
  "required": ["user_id"]
}
```

### DeleteUserTool

**Name:** `delete_user`

**Description:** Deletes a user from the system

**Schema:**
```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "integer",
      "description": "ID of user to delete"
    }
  },
  "required": ["user_id"]
}
```

### WebSearchTool

**Name:** `web_search_tool`

**Description:** Search the web using Google Search

**Schema:**
```json
{
  "type": "object",
  "properties": {
    "request": {
      "type": "string",
      "description": "The search query or question to search for on the web"
    }
  },
  "required": ["request"]
}
```

**Example Call:**
```json
{
  "name": "web_search_tool",
  "arguments": "{\"request\": \"EPAM Systems company information\"}"
}
```

## Error Handling

### HTTP Errors

**DIAL API Errors:**
```python
try:
    response = requests.post(endpoint, headers=headers, json=payload)
    response.raise_for_status()
except requests.exceptions.HTTPError as e:
    # Handle 4xx/5xx errors
    print(f"HTTP {response.status_code}: {response.text}")
```

**User Service Errors:**
```python
if response.status_code != 200:
    raise Exception(f"HTTP {response.status_code}: {response.text}")
```

### Tool Execution Errors

Tools return error strings instead of raising exceptions:

```python
def execute(self, arguments: dict) -> str:
    try:
        # Tool logic
        return result
    except Exception as e:
        return f"Error while executing tool: {str(e)}"
```

### Common Error Scenarios

| Error | Cause | Solution |
|-------|-------|----------|
| `API key is required` | Missing `DIAL_API_KEY` | Set environment variable |
| `Connection timeout` | VPN not connected | Connect to EPAM VPN |
| `404 Not Found` | Invalid user ID | Verify user exists with search |
| `Tool not found` | Unregistered tool | Check tool registration in `app.py` |
| `Invalid arguments` | Schema mismatch | Verify Pydantic model |

## Code Examples

### Basic Tool Implementation

```python
from typing import Any
from task.tools.base import BaseTool
from pydantic import BaseModel

class GreetInput(BaseModel):
    name: str

class GreetTool(BaseTool):
    @property
    def name(self) -> str:
        return "greet_user"
    
    @property
    def description(self) -> str:
        return "Greets a user by name"
    
    @property
    def input_schema(self) -> dict[str, Any]:
        return GreetInput.model_json_schema()
    
    def execute(self, arguments: dict[str, Any]) -> str:
        try:
            greet_input = GreetInput.model_validate(arguments)
            return f"Hello, {greet_input.name}!"
        except Exception as e:
            return f"Error: {str(e)}"
```

### Custom DIAL Client Usage

```python
from task.client import DialClient
from task.models.message import Message
from task.models.role import Role
from task.models.conversation import Conversation

# Initialize client
client = DialClient(
    endpoint="https://ai-proxy.lab.epam.com",
    deployment_name="gpt-4o",
    api_key="your-api-key",
    tools=[GreetTool()]
)

# Create conversation
conversation = Conversation()
conversation.add_message(Message(
    role=Role.SYSTEM,
    content="You are a helpful assistant."
))
conversation.add_message(Message(
    role=Role.USER,
    content="Greet Alice"
))

# Get response
response = client.get_completion(conversation.get_messages())
print(response.content)
```

### Tool Registration Pattern

```python
from task.tools.users.user_client import UserClient

# Create shared dependencies
user_client = UserClient()

# Register all tools
tools = [
    GetUserByIdTool(user_client),
    SearchUsersTool(user_client),
    CreateUserTool(user_client),
    UpdateUserTool(user_client),
    DeleteUserTool(user_client),
    WebSearchTool(api_key=API_KEY, endpoint=DIAL_ENDPOINT)
]

# Inject into client
dial_client = DialClient(
    endpoint=DIAL_ENDPOINT,
    deployment_name="gpt-4o",
    api_key=API_KEY,
    tools=tools
)
```

### Pydantic Model to Schema

```python
from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str
    age: int | None = None

# Generate JSON Schema
schema = UserCreate.model_json_schema()
print(schema)
```

**Output:**
```json
{
  "type": "object",
  "properties": {
    "name": {"type": "string"},
    "email": {"type": "string"},
    "age": {
      "anyOf": [{"type": "integer"}, {"type": "null"}],
      "default": null
    }
  },
  "required": ["name", "email"]
}
```

---

**Last Updated**: 2025-12-30 | **Version**: 1.0.0 | **API Version**: OpenAI Compatible
