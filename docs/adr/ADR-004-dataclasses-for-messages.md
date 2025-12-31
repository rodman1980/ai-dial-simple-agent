# ADR-004: Dataclasses for Message Representation

**Status:** Accepted

**Date:** 2025-12-30

**Deciders:** Development Team

## Context

The agent needs to represent messages in conversations with proper structure for:
- Type safety and IDE autocompletion
- Serialization to OpenAI API format
- Memory efficiency
- Maintainability

We needed to choose a data modeling approach for the `Message` and `Conversation` classes. Options included:
1. Plain dictionaries
2. Python dataclasses
3. Pydantic models
4. Named tuples
5. Custom classes with manual `__init__`

Key requirements:
- Lightweight (minimal overhead)
- Type hints for safety
- Easy serialization to OpenAI format
- Immutability not required (messages are one-way)
- Simple to understand and maintain

## Decision

Use **Python dataclasses** for `Message` and `Conversation`:

```python
from dataclasses import dataclass, field
from typing import Any

@dataclass
class Message:
    role: Role
    content: str
    tool_call_id: str | None = None
    name: str | None = None
    tool_calls: list[dict[str, Any]] | None = None

    def to_dict(self) -> dict[str, Any]:
        result = {
            "role": self.role.value,
            "content": self.content
        }
        if self.tool_call_id:
            result["tool_call_id"] = self.tool_call_id
        if self.name:
            result["name"] = self.name
        if self.tool_calls:
            result["tool_calls"] = self.tool_calls
        return result

@dataclass
class Conversation:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    messages: list[Message] = field(default_factory=list)
```

No Pydantic validation, no complex inheritance, just clean data containers.

## Consequences

### Positive

- **Minimal Boilerplate**: Auto-generated `__init__`, `__repr__`, `__eq__`
- **Type Safety**: IDE autocompletion and type checking work
- **Readable**: Clear declaration of fields and types
- **Performance**: Near-zero overhead compared to plain classes
- **Standard Library**: No external dependencies
- **Flexibility**: Easy to add methods like `to_dict()`
- **Debugging**: Automatic `__repr__` shows field values
- **Mutable**: Can modify fields when needed (conversation history)

### Negative

- **No Validation**: Types are hints only, not enforced at runtime
- **No Serialization Magic**: Must manually implement `to_dict()`
- **Limited Features**: No nested model validation like Pydantic
- **Mutable by Default**: Need frozen=True for immutability
- **No JSON Schema**: Cannot auto-generate OpenAPI specs

### Neutral

- **Learning Curve**: Developers need to understand dataclass decorators
- **Python 3.7+**: Requires modern Python (not an issue for this project)

## Alternatives Considered

### Alternative 1: Plain Dictionaries

**Approach:**
```python
message = {
    "role": "user",
    "content": "Hello",
    "tool_calls": None
}
```

**Pros:**
- Zero overhead
- Maximum flexibility
- Familiar to all Python developers
- Built-in serialization

**Cons:**
- No type safety
- No IDE autocompletion
- Typo-prone (key name errors)
- Harder to refactor
- No structure enforcement
- Poor debugging (generic dict repr)

**Reason for rejection:** Sacrifices too much safety and maintainability. Type hints essential for project quality.

### Alternative 2: Pydantic Models

**Approach:**
```python
from pydantic import BaseModel

class Message(BaseModel):
    role: Role
    content: str
    tool_call_id: str | None = None
    name: str | None = None
    tool_calls: list[dict] | None = None
    
    def to_dict(self):
        return self.model_dump(exclude_none=True)
```

**Pros:**
- Runtime validation
- JSON schema generation
- Nested model validation
- Rich ecosystem
- Serialization helpers

**Cons:**
- External dependency (already used for tool inputs)
- Performance overhead (~10x slower than dataclass)
- Over-engineered for simple containers
- Validation unnecessary (API validates)
- Extra complexity for minimal benefit

**Reason for rejection:** Pydantic excellent for tool input validation (where we use it), but overkill for internal message passing. Messages come from trusted sources (our code, DIAL API).

### Alternative 3: Named Tuples

**Approach:**
```python
from typing import NamedTuple

class Message(NamedTuple):
    role: Role
    content: str
    tool_call_id: str | None = None
    name: str | None = None
    tool_calls: list[dict] | None = None
```

**Pros:**
- Immutable (hashable)
- Memory efficient
- Type hints supported
- Tuple compatibility

**Cons:**
- Immutable (can't modify conversation history easily)
- No methods (can't add `to_dict()`)
- Less intuitive than classes
- Awkward for optional fields

**Reason for rejection:** Immutability hinders conversation management. Need to mutate message lists.

### Alternative 4: attrs Library

**Approach:**
```python
import attr

@attr.s(auto_attribs=True)
class Message:
    role: Role
    content: str
    tool_call_id: str | None = None
```

**Pros:**
- Similar to dataclasses with extra features
- Mature library
- Validators, converters available
- Better frozen support

**Cons:**
- External dependency
- Dataclasses now standard (PEP 557)
- Learning curve for attrs-specific features
- Minimal advantage over dataclasses

**Reason for rejection:** Dataclasses are standard library and sufficient. No need for attrs extras.

### Alternative 5: Custom Classes

**Approach:**
```python
class Message:
    def __init__(self, role, content, tool_call_id=None, name=None, tool_calls=None):
        self.role = role
        self.content = content
        self.tool_call_id = tool_call_id
        self.name = name
        self.tool_calls = tool_calls
    
    def __repr__(self):
        return f"Message(role={self.role}, content={self.content}...)"
```

**Pros:**
- Complete control
- No decorators
- Explicit implementation
- Familiar pattern

**Cons:**
- Boilerplate `__init__`
- Manual `__repr__`, `__eq__`
- More code to maintain
- Harder to modify fields

**Reason for rejection:** Dataclasses eliminate boilerplate without sacrificing control.

## Implementation Details

### Optional Fields Handling

```python
def to_dict(self) -> dict[str, Any]:
    result = {"role": self.role.value, "content": self.content}
    
    # Only include optional fields if present
    if self.tool_call_id:
        result["tool_call_id"] = self.tool_call_id
    if self.name:
        result["name"] = self.name
    if self.tool_calls:
        result["tool_calls"] = self.tool_calls
    
    return result
```

This ensures clean JSON without `null` values.

### Conversation Default Values

```python
@dataclass
class Conversation:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    messages: list[Message] = field(default_factory=list)
```

Using `field(default_factory=list)` avoids mutable default argument pitfall.

### Type Hints with Modern Python

```python
tool_calls: list[dict[str, Any]] | None = None
```

Using `|` syntax (Python 3.10+) instead of `Union` for cleaner code.

## Why Not Pydantic for Messages?

We **do** use Pydantic for tool inputs (e.g., `UserCreate`, `UserUpdate`) because:
- External data needs validation
- JSON schema generation for OpenAI API
- Runtime type checking important

But for messages:
- Internal data structures (trusted)
- Performance matters (high frequency)
- Simpler is better

**Pattern:** Pydantic at boundaries, dataclasses internally.

## Related Decisions

- **ADR-001**: OpenAI-compatible API format (defines message structure)
- **ADR-002**: Recursive tool calling (messages accumulated in list)

## Future Considerations

- **Validation Layer**: Could add Pydantic validator if needed
- **Immutability**: Could use `frozen=True` for thread safety
- **Slots**: Could use `__slots__` for memory optimization
- **Rich Repr**: Could use rich library for colored output

## Migration Path

If validation becomes needed:

```python
from pydantic.dataclasses import dataclass

@dataclass  # Pydantic version
class Message:
    role: Role
    content: str
    # Validation now automatic
```

This maintains API compatibility while adding validation.

## References

- [PEP 557 - Data Classes](https://peps.python.org/pep-0557/)
- [Python dataclasses documentation](https://docs.python.org/3/library/dataclasses.html)
- [task/models/message.py](../../task/models/message.py)
- [task/models/conversation.py](../../task/models/conversation.py)

---

**Last Updated**: 2025-12-30 | **Status**: Accepted | **Impact**: Medium
