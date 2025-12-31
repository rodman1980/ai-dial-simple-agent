---
title: DIAL Simple Agent - Glossary
description: Comprehensive definitions of domain terms, technical vocabulary, and acronyms used throughout the project
version: 1.0.0
last_updated: 2025-12-30
related: [README.md, architecture.md, api.md]
tags: [glossary, terminology, reference]
---

# Glossary

> Definitions of key terms, concepts, and acronyms used in DIAL Simple Agent

## Table of Contents

- [Core Concepts](#core-concepts)
- [DIAL & AI Terms](#dial--ai-terms)
- [Tool System](#tool-system)
- [Architecture Patterns](#architecture-patterns)
- [API & Protocols](#api--protocols)
- [Development Tools](#development-tools)
- [Acronyms](#acronyms)

## Core Concepts

### Agent
An autonomous AI system that can make decisions, use tools, and execute multi-step tasks to achieve goals. In this project, the agent manages user data through natural language interactions.

**Related Terms:** Agentic Pattern, LLM Agent, AI Assistant

### Agentic Loop
A recursive execution pattern where the AI repeatedly:
1. Receives a request
2. Decides which tools to use
3. Executes tools
4. Incorporates results
5. Continues until task completion

**Example:** User asks to "find and update John's email" → agent searches → retrieves ID → updates → confirms

### Conversation
A stateful sequence of messages between user and AI, maintaining context across multiple turns. Includes system instructions, user queries, assistant responses, and tool invocations.

**Components:** System message, user messages, assistant messages, tool messages

### Message
An individual unit of communication in a conversation, containing role (system/user/assistant/tool), content, and optional metadata (tool calls, tool results).

**Format:** Follows OpenAI chat completions message schema

### Tool
A callable function exposed to the AI agent for performing specific operations (e.g., database queries, API calls, web searches). Tools extend the AI's capabilities beyond text generation.

**Synonyms:** Function, Plugin, Capability

## DIAL & AI Terms

### DIAL (Distributed AI Lab)
EPAM's AI proxy service that provides unified access to multiple LLM providers (OpenAI, Google, Anthropic) through a single API endpoint with authentication and routing.

**Endpoint:** `https://ai-proxy.lab.epam.com`

### DIAL API Key
Authentication credential required to access EPAM's DIAL proxy. Must be included in request headers as `api-key`.

**Request:** Via [EPAM Service Portal](https://support.epam.com/ess)

### Deployment Name
Model identifier used in DIAL API URLs to specify which LLM to use.

**Examples:** `gpt-4o`, `gemini-2.5-pro`, `claude-3-opus`

### Chat Completions
OpenAI API format for conversational AI interactions. Takes a list of messages and returns an AI-generated response.

**Format:** POST request with messages array and optional tools

### Function Calling
LLM capability to request tool execution by returning structured function calls with arguments, rather than just text responses.

**Also Known As:** Tool Calling, Plugin System

### Tool Call
Structured request from the AI to execute a specific tool with provided arguments.

**Format:**
```json
{
  "id": "call_abc123",
  "type": "function",
  "function": {
    "name": "search_users",
    "arguments": "{\"name\": \"John\"}"
  }
}
```

### Finish Reason
Status indicator in LLM responses showing why generation stopped.

**Values:**
- `stop` - Natural completion
- `tool_calls` - Requesting tool execution
- `length` - Token limit reached

### System Prompt
Initial instruction message that defines the AI's role, capabilities, constraints, and behavior guidelines. Sets the context for all subsequent interactions.

**Location:** [prompts.py](../task/prompts.py)

### Temperature
LLM parameter controlling response randomness. Lower values (0.0-0.3) produce deterministic outputs; higher values (0.7-1.0) increase creativity.

**Default:** 0.7 in this project

### Token
Basic unit of text processing in LLMs. Approximately 4 characters or 0.75 words in English.

**Limit:** Varies by model (e.g., GPT-4o: 128K tokens)

### Grounding
LLM technique that connects responses to external data sources (web search, databases) to reduce hallucinations and improve accuracy.

**Example:** Gemini 2.5 Pro with Google Search

## Tool System

### BaseTool
Abstract base class defining the interface all tools must implement: `execute()`, `name`, `description`, `input_schema`.

**Pattern:** Template Method design pattern

### BaseUserServiceTool
Specialized tool base class for user service operations, providing shared `UserClient` instance.

**Inherits From:** BaseTool

### Tool Schema
JSON Schema describing a tool's input parameters, used by the AI to generate valid function calls.

**Generation:** Automatically derived from Pydantic models via `model_json_schema()`

### Tool Registry
Collection of available tools passed to the DIAL client during initialization. Maps tool names to executable instances.

**Format:** `{name: tool_instance}` dictionary

### Input Schema
JSON Schema specification of valid arguments for a tool.

**Properties:**
- `type` - Data type (object, string, integer)
- `properties` - Field definitions
- `required` - Mandatory fields

### Tool Result
String output returned by tool execution, formatted for LLM consumption (typically markdown).

**Example:**
```markdown
```
  id: 123
  name: John Smith
  email: john.smith@example.com
```
```

### CRUD Tools
Set of five user management tools:
- **Create** (`add_user`) - Add new user
- **Read** (`get_user_by_id`, `search_users`) - Retrieve users
- **Update** (`update_user`) - Modify user fields
- **Delete** (`delete_user`) - Remove user

## Architecture Patterns

### REPL (Read-Eval-Print Loop)
Interactive command-line interface pattern: read user input → evaluate (send to AI) → print response → repeat.

**Implementation:** [app.py](../task/app.py) main loop

### Dataclass
Python decorator for creating classes with automatic `__init__`, comparison methods, and type hints. Used for lightweight data containers.

**Example:** `Message`, `Conversation`

### Dependency Injection
Design pattern where dependencies (like `UserClient`) are passed to classes rather than created internally, improving testability.

**Example:** Tools receive `UserClient` in constructor

### Recursive Pattern
Programming technique where a function calls itself, used in `get_completion()` for agentic loop implementation.

**Use Case:** Process tool calls and recurse with results

### Abstract Base Class (ABC)
Python mechanism for defining interfaces that subclasses must implement.

**Example:** `BaseTool` with `@abstractmethod` decorators

### Template Method Pattern
Design pattern where base class defines algorithm structure, subclasses implement specific steps.

**Example:** `BaseTool.schema` uses abstract properties from subclasses

## API & Protocols

### REST API
Architectural style for web services using HTTP methods (GET, POST, PATCH, DELETE) for resource operations.

**Implementation:** User service API

### HTTP Methods
- **GET** - Retrieve resources
- **POST** - Create resources
- **PATCH** - Partial update
- **DELETE** - Remove resources

### JSON (JavaScript Object Notation)
Text-based data interchange format using key-value pairs.

**Usage:** API requests/responses, tool arguments

### JSON Schema
Vocabulary for validating JSON data structure, defining types, required fields, and constraints.

**Usage:** Tool input validation

### Markdown
Lightweight markup language for formatting text with simple syntax.

**Usage:** Tool results formatting for LLM readability

### OpenAI Compatible API
API design that follows OpenAI's specification, allowing interoperability with OpenAI-compatible clients.

**Example:** DIAL API mirrors OpenAI chat completions format

### Health Check
Endpoint for verifying service availability and operational status.

**Example:** `http://localhost:8041/health`

### Base URL
Root address for API endpoints.

**Examples:**
- DIAL: `https://ai-proxy.lab.epam.com`
- User Service: `http://localhost:8041`

## Development Tools

### Virtual Environment (venv)
Isolated Python environment with its own packages, preventing dependency conflicts.

**Location:** `dial_simple_agent/` directory

### Docker
Platform for running applications in isolated containers with consistent environments across systems.

**Usage:** User service containerization

### Docker Compose
Tool for defining and running multi-container Docker applications using YAML configuration.

**File:** `docker-compose.yml`

### Docker Image
Read-only template containing application code, runtime, and dependencies.

**Example:** `khshanovskyi/mockuserservice:latest`

### Container
Running instance of a Docker image with its own filesystem, network, and process space.

**Example:** `userservice` container on port 8041

### Pydantic
Python library for data validation using type hints and automatic model generation.

**Usage:** `UserCreate`, `UserUpdate` models

### Type Hints
Python syntax for specifying expected types of variables, function parameters, and return values.

**Example:** `def execute(self, arguments: dict[str, Any]) -> str:`

### Environment Variable
OS-level configuration value accessible to running programs.

**Example:** `DIAL_API_KEY`, `USER_SERVICE_ENDPOINT`

### Pip
Python package installer and dependency manager.

**Usage:** `pip install -r requirements.txt`

### requirements.txt
File listing Python package dependencies with optional version constraints.

**Contents:** `requests>=2.28.0`, `pydantic>=2.11.9`

## Acronyms

### AI
**Artificial Intelligence** - Computer systems performing tasks requiring human intelligence

### API
**Application Programming Interface** - Set of protocols for building and integrating software

### CRUD
**Create, Read, Update, Delete** - Four basic database operations

### CSV
**Comma-Separated Values** - Text file format for tabular data

### DIAL
**Distributed AI Lab** - EPAM's AI proxy service

### DNS
**Domain Name System** - Internet service translating domain names to IP addresses

### ER
**Entity-Relationship** - Database design diagram showing entities and relationships

### HTTP
**Hypertext Transfer Protocol** - Foundation of data communication on the web

### HTTPS
**HTTP Secure** - Encrypted version of HTTP

### ID
**Identifier** - Unique reference for an entity

### JSON
**JavaScript Object Notation** - Text-based data format

### LLM
**Large Language Model** - AI model trained on text for language understanding/generation

### OS
**Operating System** - Software managing computer hardware and services

### REST
**Representational State Transfer** - Architectural style for web services

### REPL
**Read-Eval-Print Loop** - Interactive programming environment

### SSE
**Server-Sent Events** - HTTP standard for server-to-client streaming

### URL
**Uniform Resource Locator** - Web address

### VPN
**Virtual Private Network** - Encrypted connection over public network

### YAML
**YAML Ain't Markup Language** - Human-readable data serialization format

### WSL
**Windows Subsystem for Linux** - Linux environment on Windows

## Domain-Specific Terms

### User Service
Mock REST API providing CRUD operations on user data, running in Docker container on port 8041.

**Features:** Auto-generates 1000 users, supports search filters, includes health endpoint

### Mock User
Synthetic user record generated for testing with realistic data (name, email, address, etc.).

**Count:** 1000 pre-generated users in default configuration

### User Client
HTTP client class abstracting communication with user service API.

**Methods:** `get_user()`, `search_users()`, `add_user()`, `update_user()`, `delete_user()`

### Markdown Formatting
Converting structured data to markdown code blocks for optimal LLM comprehension.

**Pattern:**
```markdown
```
  field1: value1
  field2: value2
```
```

### Tool Execution Result
String output from tool containing either successful operation data or error message.

**Format:** Always returns string (never raises exceptions)

### System Message
First message in every conversation defining agent behavior and capabilities.

**Role:** `system`

### Tool Message
Message containing results from tool execution, linked to original tool call via `tool_call_id`.

**Role:** `tool`

### Assistant Message
AI-generated response containing either text or tool calls.

**Role:** `assistant` (OpenAI format) or `AI` (internal Role enum)

### User Message
Input from human user requesting information or action.

**Role:** `user`

---

**Last Updated**: 2025-12-30 | **Version**: 1.0.0 | **Terms**: 80+

## Quick Reference

**Essential Terms:**
- **Agent** - Autonomous AI system using tools
- **Tool** - Callable function for specific operations
- **DIAL** - EPAM's AI proxy service
- **CRUD** - Create, Read, Update, Delete
- **REPL** - Interactive command loop

**Key Files:**
- [BaseTool](../task/tools/base.py) - Tool interface
- [DialClient](../task/client.py) - DIAL API client
- [UserClient](../task/tools/users/user_client.py) - User service client
- [Message](../task/models/message.py) - Message dataclass
- [Conversation](../task/models/conversation.py) - Conversation manager
