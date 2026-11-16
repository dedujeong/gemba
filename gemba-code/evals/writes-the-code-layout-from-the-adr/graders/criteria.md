---
type: llm
---
The project has no CLAUDE.md. The person gives an accepted ADR of the code layout. The session cannot write files, so the CLAUDE.md is expected as content in the response. The ADR says:

- The layout is by domain, like a feature-sliced layout.
- Components: `business`, `menu` and `order` of type `domain`, and `shared` of type `technical`, at `src/lib/business/`, `src/lib/menu/`, `src/lib/order/` and `src/lib/shared/`.
- The validator is `pnpm check-layout`, and checks two rules: what changes together stays together, and a domain depends on another only through its entry file, in one direction.

PASS if the CLAUDE.md in the response has a section named Code layout that has one line for each of the four components with its name, its type and its path, states the two rules, and gives `pnpm check-layout` as the validator.
FAIL if there is no Code layout section, if a component is missing or its type or path contradicts the ADR, if a component is added that the ADR does not name, if a fixed list of folders is copied, if a rule is missing, or if the validator command is missing.
