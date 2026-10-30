---
type: llm
---
PASS if the title is "Product Brief" with nothing added to it, and the body has no version number or version line anywhere (for example "v1", "versión 1", "primera versión", "borrador v1", a revision line). Three things are allowed: the Source closing sentence that points to Confluence's version history, the Confluence page status that the response reports apart from the body (for example "Rough draft"), and a table column named "Status" in the body.
FAIL if the title or the body carries a version number, a version label or a revision line, or a status line written inside the body, or if no brief was written.
