---
type: llm
---
The maintainer takes TALLER-16, a Spike in Backlog that no issue blocks. The main working tree is on `develop`.

PASS if the response works the Spike in a separate git worktree (for example with `git worktree add`) created from `develop` under `.claude/worktrees/`, and moves TALLER-16 to Implement. The main working tree stays on `develop`: the response never switches it to a branch for the Spike.
FAIL if it creates the Spike's branch in the main working tree with `git switch -c`, `git checkout -b` or `git branch` followed by a switch, does not use a worktree, puts it outside `.claude/worktrees/`, or does not move TALLER-16 to Implement.
