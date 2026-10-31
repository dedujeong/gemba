---
type: llm
---
The project has nothing about the method: Claude can only answer from rules it was given at session start.

PASS if the response gets all five right:
1. The branch is `story/ABC-12-export-invoices-as-csv` and it starts from `develop`.
2. The issue moves to Implement before the first change.
3. The test comes first and fails for the expected reason, then the least code that makes it pass.
4. The commit is one line like `feat(billing): <imperative description>`, with no issue key in it.
5. A local merge into `develop` with `--no-ff`, then `develop` is pushed and the branch is deleted.
FAIL if any of the five is missing or different, for example another branch name or base, the key in the commit, or a squash or rebase.
