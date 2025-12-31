# ADR-003: Markdown-Formatted Tool Results

**Status:** Accepted

**Date:** 2025-12-30

**Deciders:** Development Team

## Context

Tools need to return results to the AI for synthesis into natural language responses. The format of these results significantly impacts:
- AI's ability to understand and process data
- Response quality and accuracy
- Implementation complexity
- Human readability during debugging

User service returns JSON objects, but we need to decide how to format these for tool messages sent back to the LLM. Options included:
1. Return raw JSON strings
2. Convert to natural language descriptions
3. Use structured markdown format
4. Custom serialization format

Key considerations:
- LLM comprehension and information extraction
- Consistency across different tool types
- Human readability for debugging
- Ease of implementation
- Token efficiency

## Decision

Format all tool results as **markdown code blocks** with key-value pairs:

```python
def __user_to_string(self, user: dict[str, Any]) -> str:
    user_str = "```\n"
    for key, value in user.items():
        user_str += f"  {key}: {value}\n"
    user_str += "```\n"
    return user_str
```

**Example output:**
```markdown
```
  id: 123
  name: John
  surname: Smith
  email: john.smith@example.com
  phone: +1-555-1234
```
```

This format is used by all user service tools (`UserClient` methods).

## Consequences

### Positive

- **LLM Comprehension**: Markdown recognized and parsed well by modern LLMs
- **Human Readable**: Easy to debug and inspect tool results
- **Structured Yet Flexible**: Key-value format maintains structure without rigidity
- **Consistent**: Same format across all user tools
- **Token Efficient**: More concise than verbose natural language
- **IDE Support**: Code blocks render nicely in terminals and editors
- **Nested Data**: Can represent complex objects (addresses, credit cards) clearly
- **No Parsing Required**: LLM consumes directly without JSON parsing

### Negative

- **Programmatic Access**: Hard to parse back to objects (one-way transformation)
- **Type Loss**: Everything becomes strings (numbers, booleans as text)
- **Schema-less**: No formal structure validation
- **Consistency Burden**: Developers must manually maintain format
- **Multi-Record Formatting**: Lists less elegant than JSON arrays
- **Whitespace Sensitivity**: Indentation matters for readability

### Neutral

- **Convention Over Configuration**: Format defined by implementation, not interface
- **Learning Curve**: Developers must understand formatting conventions

## Alternatives Considered

### Alternative 1: Raw JSON Strings

**Approach:**
```python
return json.dumps(user_data)
```

**Example:**
```json
{"id": 123, "name": "John", "surname": "Smith", "email": "john.smith@example.com"}
```

**Pros:**
- Preserves data types
- Standard format
- Easy to parse programmatically
- Self-documenting schema

**Cons:**
- Less LLM-friendly (requires understanding JSON syntax)
- Harder for humans to read (dense, no whitespace)
- Token-inefficient (quotes, braces, commas)
- Poor rendering in conversation logs

**Reason for rejection:** LLMs perform better with readable text than compact JSON.

### Alternative 2: Natural Language Descriptions

**Approach:**
```python
return f"Found user {user['name']} {user['surname']} with email {user['email']}"
```

**Example:**
```
Found user John Smith with email john.smith@example.com. 
Phone: +1-555-1234. Works at EPAM Systems with salary $85,000.
```

**Pros:**
- Highly readable
- LLM can directly quote in response
- Natural conversation flow
- No parsing needed

**Cons:**
- Verbose (high token cost)
- Inconsistent formatting
- Hard to extract specific fields
- Prone to template errors
- Difficult with nested data (addresses, lists)

**Reason for rejection:** Too verbose for users with many fields (10+ attributes). Inconsistent structure makes information extraction harder.

### Alternative 3: YAML Format

**Approach:**
```python
return yaml.dump(user_data)
```

**Example:**
```yaml
id: 123
name: John
surname: Smith
email: john.smith@example.com
phone: +1-555-1234
```

**Pros:**
- Human-readable
- Preserves structure
- Standard format
- Handles nested data well

**Cons:**
- Requires YAML library dependency
- Overkill for simple key-value data
- Less familiar than markdown
- Indentation-sensitive (more than markdown)

**Reason for rejection:** Added dependency not justified. Markdown achieves same readability without external library.

### Alternative 4: HTML Tables

**Approach:**
```python
return f"<table><tr><td>Name</td><td>{user['name']}</td></tr>...</table>"
```

**Pros:**
- Structured presentation
- Good for multi-record results
- Familiar format

**Cons:**
- Verbose markup
- Poor terminal rendering
- Token-inefficient
- Not designed for LLM consumption

**Reason for rejection:** HTML designed for browsers, not LLMs. Too verbose.

### Alternative 5: Structured JSON with Markdown Wrapper

**Approach:**
```python
return f"```json\n{json.dumps(user_data, indent=2)}\n```"
```

**Example:**
```json
{
  "id": 123,
  "name": "John",
  "surname": "Smith"
}
```

**Pros:**
- Preserves JSON structure
- Markdown code block benefits
- Syntax highlighting potential

**Cons:**
- JSON overhead (quotes, braces)
- Less readable than plain key-value
- No significant advantages over plain markdown

**Reason for rejection:** JSON syntax adds noise without benefit for LLM consumption.

## Implementation Details

### Single User Formatting

```python
def __user_to_string(self, user: dict[str, Any]) -> str:
    user_str = "```\n"
    for key, value in user.items():
        user_str += f"  {key}: {value}\n"
    user_str += "```\n"
    return user_str
```

**Output:**
```
```
  id: 123
  name: John
  surname: Smith
```
```

### Multiple Users Formatting

```python
def __users_to_string(self, users: list[dict[str, Any]]) -> str:
    users_str = ""
    for user in users:
        users_str += self.__user_to_string(user)
    users_str += "\n"
    return users_str
```

**Output:**
```
```
  id: 123
  name: John
```

```
  id: 456
  name: Jane
```
```

### Nested Data Handling

Python's default string conversion handles nested objects:
```python
# Address object becomes:
address: {'country': 'USA', 'city': 'Boston', 'street': 'Main St 123'}
```

While not perfect, it's readable and LLMs handle it well.

## Token Efficiency Analysis

**Example user with 10 fields:**

| Format | Token Count (approx) | Savings |
|--------|---------------------|---------|
| Raw JSON | ~150 tokens | Baseline |
| Markdown | ~120 tokens | 20% |
| Natural language | ~180 tokens | -20% |
| YAML | ~115 tokens | 23% |

Markdown strikes good balance between readability and efficiency.

## Error Message Format

Errors also use consistent formatting:

```python
return f"Error while creating user: {str(e)}"
```

Plain text (no markdown) for error messages keeps them distinct from successful results.

## Related Decisions

- **ADR-002**: Recursive tool calling (defines tool message flow)
- **ADR-004**: Dataclasses for messages (tool results become message.content)

## Future Considerations

- **Standardized Format**: Could define formal schema for markdown structure
- **Rich Formatting**: Could add colors/emphasis using ANSI codes
- **Hybrid Approach**: JSON for programmatic tools, markdown for user-facing
- **Bidirectional Parsing**: If tool results need parsing, add utility functions

## References

- [task/tools/users/user_client.py](../../task/tools/users/user_client.py) - Implementation
- [Markdown Specification](https://spec.commonmark.org/)
- [LLM Best Practices for Structured Data](https://platform.openai.com/docs/guides/prompt-engineering)

---

**Last Updated**: 2025-12-30 | **Status**: Accepted | **Impact**: Medium
