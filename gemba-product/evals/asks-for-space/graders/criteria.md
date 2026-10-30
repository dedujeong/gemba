---
type: llm
focus: trace
---
PASS if Claude asks which Confluence space the product lives in, and the trace shows no call that creates or updates Confluence content (no page, no live doc, no whiteboard) in any space.
FAIL if Claude picks a space on its own, assumes a default space, or creates or updates any Confluence content without having been told the space.
