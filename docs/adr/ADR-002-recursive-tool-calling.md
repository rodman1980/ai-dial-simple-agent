# ADR-002: Recursive Tool Calling Pattern

**Status:** Accepted

**Date:** 2025-12-30

**Deciders:** Development Team

## Context

The agent needs to handle multi-step workflows where tools provide information needed for subsequent operations. For example:
- "Find John Smith and update his email" requires searching first, then updating
- The AI must autonomously chain tool calls without explicit workflow code

We needed to decide how to orchestrate tool execution when the AI requests multiple operations in sequence. Options included:
1. Manual workflow orchestration with hardcoded sequences
2. Imperative tool chaining with explicit next-step logic
3. Recursive pattern where AI drives the workflow

Key requirements:
- Support arbitrary tool combinations
- Maintain conversation context
- Allow AI to determine execution flow
- Handle errors gracefully
- Keep implementation simple

## Decision

Implement a **recursive tool calling pattern** in `DialClient.get_completion()`:

1. Send messages to DIAL API
2. Check `finish_reason` in response:
   - If `stop`: Return final message
   - If `tool_calls`: Execute tools, add results to conversation, **recurse**
3. Recursion naturally handles multi-step workflows

```python
def get_completion(self, messages: list[Message]) -> Message:
    response = self._send_request(messages)
    
    if response.finish_reason == "stop":
        return response.message
    
    if response.finish_reason == "tool_calls":
        # Execute all requested tools
        tool_results = self._execute_tools(response.tool_calls)
        
        # Add AI message and tool results to conversation
        messages.append(response.message)
        messages.extend(tool_results)
        
        # Recursive call with updated context
        return self.get_completion(messages)
```

## Consequences

### Positive

- **Autonomous Workflow**: AI determines execution flow without hardcoded logic
- **Flexibility**: Supports arbitrary tool combinations and sequences
- **Simplicity**: Clean, elegant implementation (~20 lines)
- **Context Preservation**: Full conversation history maintained automatically
- **Extensibility**: New tools work immediately without workflow changes
- **Transparency**: All tool calls logged in message history for debugging
- **Natural Termination**: DIAL API controls when to stop (via `finish_reason`)

### Negative

- **Stack Depth Risk**: Deep recursion could hit Python stack limits (unlikely in practice)
- **Runaway Loops**: Potential for infinite loops if AI misbehaves (mitigated by DIAL API limits)
- **Debugging Complexity**: Recursive calls harder to trace than linear execution
- **No Loop Control**: Cannot set max iterations without modifying recursion
- **Eager Execution**: All tool results computed before next AI call (no lazy evaluation)
- **Memory Growth**: Conversation grows with each recursion (cleared on new user input)

### Neutral

- **Performance**: Recursion overhead negligible compared to network I/O
- **Error Propagation**: Errors bubble up recursion stack (may need handling)

## Alternatives Considered

### Alternative 1: Iterative Loop

**Approach:**
```python
def get_completion(self, messages):
    while True:
        response = self._send_request(messages)
        if response.finish_reason == "stop":
            return response.message
        
        tool_results = self._execute_tools(response.tool_calls)
        messages.append(response.message)
        messages.extend(tool_results)
```

**Pros:**
- No stack depth concerns
- Easier to add max iteration limit
- Simpler debugging (linear flow)
- Explicit loop control

**Cons:**
- Less elegant/idiomatic
- Requires explicit state management
- `while True` considered code smell
- Harder to understand intent

**Reason for rejection:** Recursion better expresses the problem domain (agent reasoning loop). Stack depth not a practical concern.

### Alternative 2: Explicit Workflow Orchestration

**Approach:**
- Define workflow graphs
- Manually chain tool calls
- Hard-code common sequences

```python
# Workflow: find_and_update_user
1. search_users(name, surname)
2. extract user_id from results
3. update_user(user_id, updates)
```

**Pros:**
- Predictable execution
- Easy to optimize specific workflows
- Clear performance characteristics
- Testable workflows

**Cons:**
- Inflexible: requires code changes for new workflows
- Defeats agentic behavior purpose
- Cannot handle unexpected queries
- High maintenance burden
- Tight coupling between tools and orchestration

**Reason for rejection:** Violates agentic pattern. Agent should discover workflows autonomously.

### Alternative 3: State Machine

**Approach:**
- Define states: PENDING, EXECUTING_TOOLS, SYNTHESIZING
- Explicit state transitions
- FSM controls execution flow

**Pros:**
- Clear state tracking
- Explicit transitions
- Easy to visualize
- Well-defined error states

**Cons:**
- Over-engineering for simple use case
- Boilerplate code overhead
- Less intuitive than recursion
- Requires state management library

**Reason for rejection:** Adds complexity without proportional benefit. Recursion achieves same result more simply.

### Alternative 4: Continuation-Passing Style

**Approach:**
- Pass callback functions for next steps
- Functional programming pattern
- Avoids explicit recursion

**Pros:**
- Flexible control flow
- No stack depth issues
- Functional purity

**Cons:**
- Unfamiliar pattern for many developers
- Harder to understand and maintain
- Callback hell potential
- Poor Python idiomaticity

**Reason for rejection:** Python community prefers clear, readable code over functional patterns.

## Implementation Details

### Termination Conditions

**Normal Termination:**
- `finish_reason == "stop"` → Final response ready
- DIAL API decides when task complete

**Error Termination:**
- HTTP errors bubble up and terminate
- Tool execution errors returned as tool messages
- AI handles errors in next completion

**Implicit Limits:**
- DIAL API enforces token/time limits
- Prevents runaway recursion in practice
- No explicit loop counter needed

### Context Management

Each recursive call receives updated message list:
```python
messages = [
    system_message,
    user_message_1,
    assistant_message_1,  # with tool_calls
    tool_message_1,
    tool_message_2,
    # Recursive call adds these to context
]
```

### Memory Considerations

- Messages accumulate during single completion
- Cleared when user sends new query
- Token limit naturally bounds recursion depth
- No memory leak risk (messages dropped after return)

## Examples

### Single Tool Call

```
User: "Find user 123"
  → AI: tool_calls=[get_user_by_id(123)]
  → Recursive call with tool result
  → AI: "Here's user 123: ..."
  → Return
```

**Recursion depth:** 1

### Multi-Tool Sequence

```
User: "Find John Smith and update his email"
  → AI: tool_calls=[search_users(name="John", surname="Smith")]
  → Recursive call 1 with search results
  → AI: tool_calls=[update_user(123, email="new@...")]
  → Recursive call 2 with update confirmation
  → AI: "Updated John Smith's email to..."
  → Return
```

**Recursion depth:** 2

## Related Decisions

- **ADR-001**: OpenAI-compatible API format (defines tool_calls structure)
- **ADR-003**: Markdown tool results (format of tool messages in recursion)

## Future Considerations

- **Max Depth Limit**: Could add safety counter if needed
- **Streaming Support**: Would require rethinking recursion for SSE
- **Parallel Tool Execution**: Currently sequential; could parallelize
- **Tool Result Caching**: Avoid re-executing identical tool calls

## References

- [task/client.py](../../task/client.py) - `get_completion()` implementation
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
- [Recursive Design Patterns](https://en.wikipedia.org/wiki/Recursion_(computer_science))

---

**Last Updated**: 2025-12-30 | **Status**: Accepted | **Impact**: High
