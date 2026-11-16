---
type: llm
focus: trace
---
The layout of the prompt is organized by vertical slices per domain, each with one public entry file, with dependencies in one direction. That matches layouts that have a name (vertical slice architecture, a modular monolith, feature folders).

PASS if the drafted ADR says that the layout matches a named layout and cites it by its name (for example vertical slice architecture or modular monolith).
FAIL if the ADR does not name any established layout that the derived one matches.
