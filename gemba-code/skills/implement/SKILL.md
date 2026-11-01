---
name: implement
description: Take an issue from Backlog and move it to Implement, with its branch created from develop. Taking an Epic moves it to Implement and takes its first child that is in Backlog and not blocked. Use when someone says "toma", "implementa", "empecemos con" or "vamos con" followed by an issue key.
---

# Implement an issue

You take one issue from Backlog and start its work: its branch exists and the issue is in Implement before the first change.

## 1. Find the project

Read the `## Gemba` section of the project's `CLAUDE.md`: `Jira Project` and `Language`. If it is missing, propose running `setup` first and stop. Get the cloudId once with `getAccessibleAtlassianResources`. Talk with the person in `Language`.

## 2. Take the issue

Read the issue with `getJiraIssue` (view `evidence`, which includes its links). Do not take it, and say why, when:

- It is not in Backlog: say which state it is in.
- An issue that blocks it is not Done or Cancelled: name the blocking issue and its state. Jira does not enforce this, so the check is yours.

When it is not taken, no branch is created and the issue stays where it is. Then, by its work type:

- Story, Task or Bug: create its branch and move it to Implement, as in section 3.
- Spike: create its branch in a separate worktree and move it to Implement, as in section 4.
- Epic: an Epic has no branch. Move it to Implement and take its first child, as in section 5.

## 3. Create the branch and move the issue

1. From `develop`, create the branch `<type>/<KEY>-<slug>`: the work type in lowercase and the Summary as a slug of lowercase letters, digits and single hyphens (`story/ABC-12-export-invoices-as-csv`).
2. Move the issue to Implement with `transitionJiraIssue`, using the transition that goes to Implement.

The branch comes first, so the issue never reads Implement without a branch. Carry nothing else onto it: leave any uncommitted change of the working tree uncommitted.

## 4. Take a Spike

A Spike is never worked on a branch of the main working tree, which stays on `develop`. Create a worktree in `.claude/worktrees/`, which `.gitignore` already ignores, with the Spike's branch from `develop`: `git worktree add -b spike/<KEY>-<slug> .claude/worktrees/<KEY>-<slug> develop`. Then move the Spike to Implement and work in that worktree.

## 5. Take an Epic

1. Move the Epic to Implement. It has no branch.
2. List its children in rank order (`parent = <KEY> ORDER BY Rank`). The first child is the first one that is in Backlog and has no open issue blocking it, read from its links.
3. Take that child by its work type, as in section 2. Take one child only; the next one is taken when the person asks for it.
