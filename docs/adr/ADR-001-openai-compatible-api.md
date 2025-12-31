# ADR-001: OpenAI-Compatible API Format

**Status:** Accepted

**Date:** 2025-12-30

**Deciders:** Development Team

## Context

DIAL Simple Agent needs to communicate with EPAM's DIAL API proxy for LLM interactions. The DIAL API mirrors OpenAI's chat completions API format. We needed to decide whether to:
1. Use the OpenAI-compatible format directly
2. Create a custom abstraction layer
3. Design a proprietary message format

Key considerations:
- DIAL API already implements OpenAI compatibility
- Developer familiarity with OpenAI API patterns
- Ecosystem tooling and documentation availability
- Potential for future multi-provider support
- Maintainability and learning curve

## Decision

We will use the **OpenAI-compatible API format** directly for all DIAL API communications, including:
- Message structure (`role`, `content`, `tool_calls`)
- Tool calling schema (function definitions with parameters)
- Response format (choices, finish_reason, usage)
- Error handling patterns

Implementation details:
- `Message.to_dict()` serializes to OpenAI format
- `DialClient` constructs OpenAI-compatible requests
- Tool schemas follow OpenAI function calling specification
- No intermediate abstraction layer between our models and API

## Consequences

### Positive

- **Reduced Development Time**: Leverages existing OpenAI documentation and examples
- **Ecosystem Compatibility**: Can reuse OpenAI client libraries, tools, and patterns
- **Developer Familiarity**: Most AI developers know OpenAI API format
- **Future-Proof**: Easy migration to native OpenAI or other compatible providers
- **Rich Documentation**: Extensive OpenAI API documentation available
- **Tooling Support**: IDEs, linters, and validators support OpenAI schema

### Negative

- **Vendor Lock-In Risk**: Tied to OpenAI's API design decisions
- **Limited Customization**: Cannot optimize for DIAL-specific features without breaking compatibility
- **Schema Constraints**: Must work within OpenAI's message and tool schema limitations
- **Breaking Changes**: OpenAI API updates may require code changes
- **Provider-Specific Features**: Cannot easily leverage non-OpenAI provider capabilities

### Neutral

- **Abstraction Trade-off**: Direct format usage means less abstraction but tighter coupling
- **Learning Curve**: New developers must learn OpenAI API conventions
- **Testing Complexity**: Must test against actual OpenAI schema, not custom format

## Alternatives Considered

### Alternative 1: Custom Abstraction Layer

**Approach:**
- Create proprietary message format
- Build adapters for OpenAI/DIAL API
- Allow provider-agnostic message handling

**Pros:**
- Complete control over message structure
- Easy to add custom metadata
- Provider-independent design
- Can optimize for specific use cases

**Cons:**
- Significant development overhead
- Additional maintenance burden
- Reduces ecosystem compatibility
- Harder for new developers to understand
- Requires comprehensive documentation

**Reason for rejection:** Premature optimization. OpenAI format meets all current requirements without added complexity.

### Alternative 2: LangChain Integration

**Approach:**
- Use LangChain framework
- Leverage built-in abstractions
- Benefit from ecosystem tools

**Pros:**
- Rich tooling and integrations
- Standardized patterns
- Active community support
- Built-in prompt management

**Cons:**
- Heavy dependency (100+ packages)
- Learning curve for LangChain APIs
- Overkill for simple use case
- Potential version conflicts
- Framework lock-in

**Reason for rejection:** Too heavyweight for learning project. Direct API usage better demonstrates core concepts.

### Alternative 3: Hybrid Approach

**Approach:**
- Internal custom format
- Conversion layer to OpenAI format
- Best of both worlds

**Pros:**
- Internal flexibility
- External compatibility
- Gradual migration path

**Cons:**
- Conversion overhead
- Maintenance complexity
- Potential serialization bugs
- Unclear benefits for current scope

**Reason for rejection:** Added complexity without clear benefits. YAGNI principle applies.

## Implementation Notes

### Message Serialization

```python
# Internal representation
@dataclass
class Message:
    role: Role
    content: str
    tool_calls: list[dict] | None = None
    
    def to_dict(self) -> dict:
        """Convert to OpenAI format"""
        return {
            "role": self.role.value,
            "content": self.content,
            "tool_calls": self.tool_calls
        }
```

### Tool Schema Format

```python
{
    "type": "function",
    "function": {
        "name": "search_users",
        "description": "Search for users...",
        "parameters": {
            "type": "object",
            "properties": {...},
            "required": [...]
        }
    }
}
```

## Related Decisions

- **ADR-002**: Recursive tool calling pattern
- **ADR-004**: Dataclasses for message representation

## References

- [OpenAI Chat Completions API](https://platform.openai.com/docs/api-reference/chat)
- [OpenAI Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)
- [DIAL API Documentation](https://dialx.ai/dial_api)
- [task/models/message.py](../../task/models/message.py)
- [task/client.py](../../task/client.py)

---

**Last Updated**: 2025-12-30 | **Status**: Accepted | **Impact**: High
