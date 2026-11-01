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

## 3. Review the diff

Once the issue is in Review, review what was built against what was agreed. Read the diff of the branch against `develop` (`git diff develop...<branch>`) and its commits (`git log develop..<branch>`).

- Per criterion: say whether it is met, with the evidence, the test or the code that shows it. Do it for every criterion of the issue, never only for the ones that fail.
- Commit by commit: compare the real commits, in order, against the list of commits planned in `implement`. Name each planned commit and say whether the real one matches it, is missing or is extra. If you do not have the planned list because the plan was made in another session, ask the maintainer for it: never invent one, and say that this comparison could not be done.

## 4. Report and stop

Report the result of the review: the verdict of each criterion and the commit comparison. Integrate nothing: do not merge, do not push and do not move the issue to Done. The issue stays in Review until the maintainer says to close it.
