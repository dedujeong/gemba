# Gemba Code

Development for Claude Code: from a closed Story Map to released versions, with every issue declared in Jira and driven to done.

Gemba Product ends discovery with a closed Story Map. Gemba Code picks it up there: it declares each issue of the version in Jira with its acceptance criteria and estimate, and takes each one from its branch to the merge. The version itself is opened and closed with Gemba Product's `version-start` and `version-close`; publishing the release (merging `develop` into `main`, tagging, creating the GitHub release and releasing the fix version) is done by hand for now.

## Install

```bash
/plugin marketplace add dedujeong/gemba
/plugin install gemba-code@gemba
```

## Requirements

- Claude Code.
- The Atlassian connector, with access to the product's Jira project and Confluence space.
- A closed Story Map from Gemba Product in that Confluence space.
- Gemba Product, whose `version-start` hands each card to Gemba Code's `start` and whose `version-close` checks that the version has no open issues.

## Skills

Each step rests on a method, named here so you know what it is based on before you use it.

- `setup` writes the project's `## Gemba` block in its `CLAUDE.md`: Jira project, Jira site, Confluence space, integration mode (`merge` or `pull request`) and language. It asks for any value it cannot read, never assumes one. It also turns off Claude's attribution lines, makes every `git push` ask for confirmation, writes the base `.gitignore` (Claude's local files, the Spikes' worktrees and the session handoffs, adding only the entries the file lacks), asks for the project license (Apache-2.0, MIT or none) and writes its `LICENSE` with the official text, fetched when it runs, and a `NOTICE` for Apache-2.0 and, when the repository has no README, writes it from a template with the data of the Product Brief.
- `start` declares one Jira issue, and is the only way an existing one is edited.
  - Work type: Epic (a Story Map card with two or more stories), Story (something a user can do that they could not), Task (technical work no user sees), Bug (something Done that does not do what it should; if its issue is not Done it is a missing criterion, not a bug) or Spike (a question answered in a fixed timebox).
  - Acceptance criteria follow the Given-When-Then form of behavior-driven specification, written in the project's language. Each states a result an automated test can check as true or false, and the issue describes what the person observes, never how it is built.
  - Every Story passes through nine edge-case heuristics: nothing, one, many, limit, duplicate, no permission, half-done failure, undo and other state. Each gap ends as a criterion, a line of Out of scope or a question to the maintainer, never as an inferred criterion. Questions go in one round and name the criterion and the heuristic that raised them.
  - A rule with two or more conditions is worked in a decision table: one row per combination, impossible rows struck, and one criterion per distinct result. The table never goes in the issue.
  - The original estimate is the hours of one person working with Claude, from branch to Done, anchored to a reference scale (1h, 2h, 3h to 4h, 6h to 8h). Above 8h the issue is split. No correction factor is applied.
  - Blocking links are declared only between direct dependencies; Jira already shows the chain.
- `implement` takes an issue from Backlog to Implement with its branch, and builds it.
  - It refuses an issue that is not in Backlog or is blocked by one that is not Done or Cancelled.
  - Before touching code it walks the work (criteria, code, tests, recent history, a manual reproduction for a Bug) and presents a plan in plan mode: the commits in order, and for each criterion the test and why it fails now, unless the maintainer says the change is mechanical: then it skips the plan and goes straight to the red test.
  - It builds with test-driven development: red, green, refactor, one criterion at a time. Red is never committed, and a test is never skipped, weakened or deleted to get green.
  - Commits follow Conventional Commits. Mechanical changes (renames, moves, formatting) go in their own commit first.
  - A Spike does not follow TDD: it works in a separate worktree, and its answer is a findings page in Confluence (Recommendation, Options, Impact on scope, Sources).
  - It logs the real time worked in Implement, never the estimate.
- `review` moves an issue from Implement to Review only when every test passes, then reviews it against what was agreed: a verdict with evidence for every criterion, and a commit-by-commit comparison with the planned commits. An unmet criterion sends the issue back to Implement. In `pull request` mode a clean review pushes the branch and opens the pull request. An Epic is reviewed through its children, and a Spike on whether its test can be reproduced.
- `close` merges a reviewed issue into `develop`, deletes the branch, logs the Review time and moves the issue to Done. In `pull request` mode the maintainer merges, and it only syncs `develop`, deletes the branch and moves the issue.
- `session-close` saves a handoff of the session: version, work in progress, what was done, what is pending, decisions and one next step. It is a summary; Jira and the code stay the source of the facts.
- `session-start` reads the latest handoff, checks it against Jira and the branch as they are now, says what changed and proposes the next step as one option.

## Conventions

- An issue is edited only while it is in Backlog.
- One branch per Story, Task, Bug or Spike, named `<type>/<KEY>-<slug>` and created from `develop`. An Epic has no branch.
- Commits are one line, `<type>(<scope>): <description>`, with no body or footer. The scope is the Jira component of the issue, the description starts with a verb in the imperative mood, and the issue key goes only in the branch.
- Merges into `develop` use `git merge --no-ff` with Git's default message; never squash and never rebase a branch onto `develop`.
- The time logged on an issue is the real time worked in each state, never the estimate.
- Session handoffs live in `.gemba/sessions`, which git ignores.
