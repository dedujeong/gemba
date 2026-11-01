---
name: implement
description: Take an issue from Backlog, move it to Implement with its branch created from develop, and start its work by exploring the code before changing anything. Taking an Epic moves it to Implement and takes its first child that is in Backlog and not blocked. Also publishes the findings of a Spike when its test ends. Use when someone says "toma", "implementa", "empecemos con" or "vamos con" followed by an issue key, or that the test of a Spike ended.
---

# Implement an issue

You take one issue from Backlog and start its work: its branch exists and the issue is in Implement before the first change, and the work begins by exploring.

## 1. Find the project

Read the `## Gemba` section of the project's `CLAUDE.md`: `Jira Project` and `Language`. If it is missing, propose running `setup` first and stop. Get the cloudId once with `getAccessibleAtlassianResources`. Talk with the person in `Language`.

## 2. Take the issue

Read the issue with `getJiraIssue` (view `evidence`, which includes its links). Do not take it, and say why, when:

- It is not in Backlog: say which state it is in.
- An issue that blocks it is not Done or Cancelled: name the blocking issue and its state. Jira does not enforce this, so the check is yours.

When it is not taken, no branch is created and the issue stays where it is. Then, by its work type:

- Story, Task or Bug: create its branch and move it to Implement, as in section 3, then walk the work, as in section 6.
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

## 6. Walk the work

Before changing anything, go and see where the work happens, without modifying a file, a test or the repository:

- Read the issue: its criteria (Story) or Done when (Task, Bug), and its links.
- Read the code it touches and the tests that already cover that code.
- Look at the recent history: `git log` of those files.
- Run the existing tests and note which pass.
- For a Bug, reproduce it by hand and note what you saw.

What you find feeds the plan, in section 7; it is not a separate deliverable.

## 7. Plan the work

When the walk is done and before any code or test changes, enter plan mode (`EnterPlanMode`) and present the plan:

- The commits you intend to make, in order: first the mechanical changes (renames, moves, formatting), each in its own commit, then at least one commit per criterion.
- For each criterion, the test that will show it and why it fails now.
- A criterion too big for one commit is split here, by behavior, into commits you would revert separately, each one a red, green, refactor cycle. If it cannot be split, say so in the plan and let the person decide: the issue is not edited outside Backlog.
- Anything the walk found that the criteria do not cover. If a criterion looks wrong or incomplete, say so: the issue is not edited outside Backlog, so the person decides.

Change nothing until the maintainer approves the plan (`ExitPlanMode`). Then build it, as in section 8.

## 8. Build each criterion

Once the plan is approved, build the criteria in the planned order, each one in a red, green, refactor cycle:

1. Red: write the test of the criterion and run it. It must fail for the expected reason, the one the plan gave. A test that passes before the code, or fails for another reason, is wrong: fix the test first.
2. Green: write the least code that makes it pass.
3. Refactor with the tests still green.
4. Commit the test and the code together. Red is never committed. The message is one line, with no body or footer:

   `<type>(<scope>): <description>`

   - `<type>` is one of `build`, `chore`, `ci`, `docs`, `feat`, `fix`, `perf`, `refactor`, `revert`, `style`, `test`.
   - `<scope>` is the Jira component of the issue, in lowercase.
   - `<description>` starts with a verb in the imperative mood, has no final period and keeps proper names in their canonical form (Jira, GitHub, API).
   - The issue key does not go in the message; only the branch carries it.

A commit is one change you would revert whole, and it leaves the branch working. A mechanical change (a rename, a move, formatting) goes in its own commit before the behavior change. Build the commits as the plan split them.

Never skip, weaken or delete a test to get green. If the test is wrong, say why and fix it in its own commit.

## 9. Finish

When every criterion is built and every test is green, log the real time worked in Implement on the issue with `addOrEditJiraIssueWorklog` (`executeWrite`):

- `started`: the time the issue entered Implement, read from the issue's changelog (`getJiraIssue` with `expand: changelog`).
- `timeSpent`: the time from then until now. Never copy the original estimate.

Tell the person the time you logged, so they can correct it. Moving the issue to Review is not part of this skill.

## 10. Finish a Spike

A Spike has no criteria to build and does not follow TDD: its test answers the question. When the test ends, and not before, publish its answer in a findings page in the product's Confluence space, never in the issue or the repo:

1. Search for the `Work` > `Spikes` folders of the space; create a folder only if it does not exist.
2. Create the page there with `createConfluenceContent`, titled `<KEY> <Summary>` exactly as in Jira, with the issue as a block card at the top and then the sections Recommendation, Options, Impact on scope and Sources. Answer the Spike's question in it, with what the test showed. Its status is Rough draft.
3. Link the issue to the page once, in the issue's remote links.

Then log the real time worked, as in section 9. Moving the Spike to Review is not part of this skill.
