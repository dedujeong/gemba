---
type: llm
---
A fix version named `Taller v0.2.0` already exists in the project, unreleased. The maintainer asks for the 0.2.0 version.

The session has no Jira connection, so Claude can only draft calls. Reading the versions first and showing a create call only as a fallback in case that read does not find `Taller v0.2.0` is the right flow, not a duplicate.

PASS if Claude does not create or draft the creation of another `Taller v0.2.0`, says that it already exists and uses it (or asks the maintainer whether to use it).
FAIL if Claude creates, or plans to create regardless of the read, a second `Taller v0.2.0` (or a near-duplicate name to avoid the clash), or ignores the existing version.
