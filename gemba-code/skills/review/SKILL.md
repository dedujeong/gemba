---
name: review
description: Move an issue from Implement to Review once every test is green, and review it there. Use when someone says "revisa", "revisemos" or "review" followed by an issue key.
---

# Review an issue

You take one issue that is in Implement, move it to Review and review it. You never integrate anything: merging and Done belong to the maintainer's decision, afterwards.

## 1. Find the project

Read the `## Gemba` section of the project's `CLAUDE.md`: `Jira Project` and `Language`. If it is missing, propose running `setup` first and stop. Get the cloudId once with `getAccessibleAtlassianResources`. Talk with the person in `Language`.

## 2. Move the issue to Review

Read the issue with `getJiraIssue` (view `evidence`, which includes its links). Only an issue in Implement is reviewed: if it is in any other state, do not move it, say which state it is in and stop. Then run the project's tests.

- If every test passes, move the issue to Review with `transitionJiraIssue`, using the transition that goes to Review.
- If a test fails, the issue stays in Implement: say which test fails and stop.
