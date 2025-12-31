# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) documenting key design decisions made during the development of DIAL Simple Agent.

## What is an ADR?

An Architecture Decision Record captures an important architectural decision made along with its context and consequences. ADRs help team members and stakeholders understand:
- Why particular design choices were made
- What alternatives were considered
- What tradeoffs were accepted
- Current status of each decision

## ADR Format

Each ADR follows this structure:

```markdown
# ADR-NNN: Title

**Status:** Proposed | Accepted | Rejected | Deprecated | Superseded by ADR-XXX

**Date:** YYYY-MM-DD

**Deciders:** Name(s) of decision makers

## Context

What is the issue we're trying to solve? What are the forces at play?

## Decision

What change are we actually proposing/making?

## Consequences

What becomes easier or harder as a result of this decision?

### Positive
- Benefit 1
- Benefit 2

### Negative
- Drawback 1
- Drawback 2

### Neutral
- Impact 1

## Alternatives Considered

### Alternative 1
**Pros:** ...
**Cons:** ...
**Reason for rejection:** ...

## References
- Link to related documentation
- External resources
```

## Index of ADRs

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [ADR-001](./ADR-001-openai-compatible-api.md) | OpenAI-Compatible API Format | Accepted | 2025-12-30 |
| [ADR-002](./ADR-002-recursive-tool-calling.md) | Recursive Tool Calling Pattern | Accepted | 2025-12-30 |
| [ADR-003](./ADR-003-markdown-tool-results.md) | Markdown-Formatted Tool Results | Accepted | 2025-12-30 |
| [ADR-004](./ADR-004-dataclasses-for-messages.md) | Dataclasses for Message Representation | Accepted | 2025-12-30 |
| [ADR-005](./ADR-005-included-virtual-environment.md) | Pre-Configured Virtual Environment | Accepted | 2025-12-30 |

## Creating New ADRs

When making significant architectural decisions:

1. Copy the template above
2. Number sequentially (ADR-006, ADR-007, etc.)
3. Use descriptive kebab-case filenames
4. Fill out all sections thoughtfully
5. Link related ADRs
6. Update this index
7. Get review from team members

## ADR Lifecycle

- **Proposed**: Under discussion
- **Accepted**: Decision approved and implemented
- **Rejected**: Decision considered but not adopted
- **Deprecated**: No longer relevant
- **Superseded**: Replaced by newer ADR

---

**Last Updated**: 2025-12-30
