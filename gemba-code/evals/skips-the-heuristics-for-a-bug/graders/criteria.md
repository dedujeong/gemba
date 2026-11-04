---
type: llm
---
The maintainer asks for a Bug and gives its steps, expected and actual result. A Bug is not passed through edge-case heuristics.

PASS if the response drafts the complete Bug declaration and asks no edge-case question (nothing about empty data, more than one, limits, duplicates, permissions, failures halfway, undoing or other states).
FAIL if the response asks edge-case questions or holds the declaration for them instead of drafting the Bug.
