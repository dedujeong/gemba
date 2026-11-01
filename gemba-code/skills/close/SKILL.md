---
name: close
description: Close an issue that is in Review: merge its branch into develop, push, delete the branch and move the issue to Done. Use when the maintainer says "cierra", "close" or "intégralo" followed by an issue key.
---

# Close an issue

You close one issue that is in Review, once the maintainer has said to. Nothing reaches `develop` without having been in Review.

## 1. Find the project

Read the `## Gemba` section of the project's `CLAUDE.md`: `Jira Project` and `Language`. If it is missing, propose running `setup` first and stop. Get the cloudId once with `getAccessibleAtlassianResources`. Talk with the person in `Language`.

## 2. Merge and move to Done

Read the issue with `getJiraIssue` (view `evidence`). Only an issue in Review is closed: if it is in any other state, do not merge, do not push and do not move it to Done; say which state it is in and stop. If it is an Epic, close it as in section 3; if it is a Spike, as in section 4. Otherwise, in this order:

1. Merge the branch into `develop`: `git switch develop`, then `git merge --no-ff <branch>` with Git's default message. Never squash and never rebase.
2. Push `develop`: `git push origin develop`.
3. Delete the branch: `git branch -d <branch>`.
4. Log the real time worked in Review with `addOrEditJiraIssueWorklog` (`executeWrite`): `started` is the time the issue entered Review, read from its changelog (`getJiraIssue` with `expand: changelog`), and `timeSpent` the time from then until now. Never copy the estimate. Tell the person the time you logged, so they can correct it.
5. Move the issue to Done with `transitionJiraIssue`, using the transition that goes to Done.

## 3. Close an Epic

An Epic has no branch: there is nothing to merge, push or delete. Only move it to Done with `transitionJiraIssue`, using the transition that goes to Done.

## 4. Close a Spike

A Spike is never merged: its work is not code for `develop`, its answer is the findings page. Do not run `git merge` and do not push. In this order:

1. Remove its worktree: `git worktree remove .claude/worktrees/<KEY>-<slug>`.
2. Delete its branch, forced because it was never merged: `git branch -D spike/<KEY>-<slug>`.
3. Set its findings page to Verified with `updateConfluenceContent`.
4. Log the real time worked in Review, as in section 2.
5. Move the Spike to Done with `transitionJiraIssue`, using the transition that goes to Done.
