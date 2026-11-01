---
name: close
description: Close an issue that is in Review: merge its branch into develop, push, delete the branch and move the issue to Done. Use when the maintainer says "cierra", "close" or "intégralo" followed by an issue key.
---

# Close an issue

You close one issue that is in Review, once the maintainer has said to. Nothing reaches `develop` without having been in Review.

## 1. Find the project

Read the `## Gemba` section of the project's `CLAUDE.md`: `Jira Project` and `Language`. If it is missing, propose running `setup` first and stop. Get the cloudId once with `getAccessibleAtlassianResources`. Talk with the person in `Language`.

## 2. Merge and move to Done

Read the issue with `getJiraIssue` (view `evidence`). Only an issue in Review is closed: if it is in any other state, do not merge, do not push and do not move it to Done; say which state it is in and stop. Otherwise, in this order:

1. Merge the branch into `develop`: `git switch develop`, then `git merge --no-ff <branch>` with Git's default message. Never squash and never rebase.
2. Push `develop`: `git push origin develop`.
3. Delete the branch: `git branch -d <branch>`.
4. Log the real time worked in Review with `addOrEditJiraIssueWorklog` (`executeWrite`): `started` is the time the issue entered Review, read from its changelog (`getJiraIssue` with `expand: changelog`), and `timeSpent` the time from then until now. Never copy the estimate. Tell the person the time you logged, so they can correct it.
5. Move the issue to Done with `transitionJiraIssue`, using the transition that goes to Done.
