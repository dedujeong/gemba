---
type: llm
focus: trace
---
Gemba Code is not installed in this session, so its start skill is not among the available skills. version-start needs it to declare the issues of the version.

PASS if Claude says that Gemba Code is required to open the version and has to be installed, and does not go on: it does not name or create a fix version, does not show the release and does not draft or declare any issue.
FAIL if Claude goes on with the version without mentioning that Gemba Code is missing, proposes or creates the fix version, shows the release, or drafts any declaration.
