---
type: llm
---
The project's `.gitignore` is given with two sections: a comment that says what is ignored, the pattern, and a blank line before the next section. It does not ignore `.gemba/sessions/` yet.

PASS if the response shows the `.gitignore` as it would end up with the two original sections unchanged, then a blank line, then a comment line that says the session handoffs are what is ignored, then the line `.gemba/sessions/`; and the response does this before it writes the handoff.
FAIL if the `.gitignore` is not shown, if the new section has no comment or no blank line before it, if an original line is changed or removed, or if the handoff is written first.
