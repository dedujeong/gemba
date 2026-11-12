---
name: close
description: Close an issue that is in Review: merge its branch into develop, push, delete the branch and move the issue to Done; in a project in pull request mode the maintainer merges the pull request and this only syncs develop, deletes the branch and moves the issue to Done. Use when the maintainer says "cierra", "close" or "intégralo" followed by an issue key.
---

# Close an issue

You close one issue that is in Review, once the maintainer has said to. Nothing reaches `develop` without having been in Review.

## 1. Find the project

Read the `## Gemba` section of the project's `CLAUDE.md`: `Jira Project`, `Integration` and `Language`. If it is missing, propose running `setup` first and stop. Use its `Jira Site` as the `cloudId` of every call; only when the block has none, get it once with `getAccessibleAtlassianResources` and propose running `setup` to add it. Every call to Jira is the one written in `../../references/jira-calls.md`, with its `fields` and `responseFields`. Talk with the person in `Language`.

## 2. Merge and move to Done

Read the issue with Read an issue (`getJiraIssue`). Only an issue in Review is closed: if it is in any other state, do not merge, do not push and do not move it to Done; say which state it is in and stop. If it is an Epic, close it as in section 3; if it is a Spike, as in section 4. Otherwise, if `Integration` is `pull request`, close it as in section 5. If it is `merge`, in this order:

1. Merge the branch into `develop`: `git switch develop`, then `git merge --no-ff <branch>` with Git's default message. Never squash and never rebase.
2. Push `develop`: `git push origin develop`.
3. Delete the branch: `git branch -d <branch>`.
4. Log the real time worked in Review with Log the time (`addOrEditJiraIssueWorklog`): read the issue's changelog with Read the changelog (`listJiraIssueChangelogs`), every page, save it, with all its pages in one list, to a temporary file and run `python3 ../implement/scripts/state_time.py <file> Review`. It adds up every stretch in Review, the one still open included, and prints `started` and `timeSpent`: log those two values, never the estimate. Tell the person the time you logged, so they can correct it.
5. Move the issue to Done with Move an issue (`transitionJiraIssue`, `transitionName`: `to Done`).

## 3. Close an Epic

An Epic has no branch: there is nothing to merge, push or delete. Only move it to Done with Move an issue (`transitionJiraIssue`, `transitionName`: `to Done`).

## 4. Close a Spike

A Spike is never merged: its work is not code for `develop`, its answer is the findings page. Do not run `git merge` and do not push. In this order:

1. Remove its worktree: `git worktree remove .claude/worktrees/<KEY>-<slug>`.
2. Delete its branch, forced because it was never merged: `git branch -D spike/<KEY>-<slug>`.
3. Set its findings page to Verified with `updateConfluenceContent`.
4. Log the real time worked in Review, as in section 2.
5. Move the Spike to Done with Move an issue (`transitionJiraIssue`, `transitionName`: `to Done`).

## 5. Close in pull request mode

When `Integration` is `pull request`, the maintainer merges the pull request on GitHub and nothing is merged here. Check the pull request of the branch with `gh pr view <branch> --json state,mergedAt,url`:

- If it is not merged (open, or closed without merging): do not move the issue to Done and do not delete the branch. Say the state of the pull request with its link, and that the merge is the maintainer's decision. Stop there.
- If it is merged, in this order:
  1. `git switch develop` and `git pull origin develop`, which bring in the merge commit the maintainer made.
  2. Delete the local branch: `git branch -d <branch>`. Delete the remote one with `git push origin --delete <branch>` only if it still exists (`git ls-remote --exit-code --heads origin <branch>`).
  3. Log the real time worked in Review, as in section 2 (`addOrEditJiraIssueWorklog`).
  4. Move the issue to Done with Move an issue (`transitionJiraIssue`, `transitionName`: `to Done`).

Without the GitHub CLI or the remote, say that the state of the pull request could not be checked, and do not move the issue to Done.
