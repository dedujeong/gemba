---
name: review
description: Move an issue from Implement to Review once every test is green, and review it there. Use when someone says "revisa", "revisemos" or "review" followed by an issue key.
---

# Review an issue

You take one issue that is in Implement, move it to Review and review it. You never merge anything: merging and Done belong to the maintainer's decision, afterwards.

## 1. Find the project

Read the `## Gemba` section of the project's `CLAUDE.md`: `Jira Project`, `Integration` and `Language`. If it is missing, propose running `setup` first and stop. Get the cloudId once with `getAccessibleAtlassianResources`. Talk with the person in `Language`.

## 2. Move the issue to Review

Read the issue with `getJiraIssue` (view `evidence`, which includes its links). Only an issue in Implement is reviewed: if it is in any other state, do not move it, say which state it is in and stop. Then, if it is an Epic, review it as in section 7; if it is a Spike, as in section 8; otherwise run the project's tests.

- If every test passes, move the issue to Review with `transitionJiraIssue`, using the transition that goes to Review.
- If a test fails, the issue stays in Implement: say which test fails and stop.

## 3. Review the diff

Once the issue is in Review, review what was built against what was agreed. Read the diff of the branch against `develop` (`git diff develop...<branch>`) and its commits (`git log develop..<branch>`).

- Per criterion: say whether it is met, with the evidence, the test or the code that shows it. Do it for every criterion of the issue, never only for the ones that fail.
- Commit by commit: compare the real commits, in order, against the list of commits planned in `implement`. Name each planned commit and say whether the real one matches it, is missing or is extra. If you do not have the planned list because the plan was made in another session, ask the maintainer for it: never invent one, and say that this comparison could not be done.

### New files against the layout

Every new file of the branch must follow the project's layout, so the repository does not get disordered issue after issue. List the files the branch adds or renames with `git diff --name-status --diff-filter=AR develop...<branch>`; for a renamed file the new path counts. Modified files are not reviewed against the layout. Read the `## Code layout` section of the project's `CLAUDE.md` and check each of those files against its four lines (Folders, Tests, File names, Migrations).

- A file whose kind the layout covers but that is in the wrong place or has the wrong name is outside the layout: name the file and where the layout says it should go. The issue does not pass: it goes back to Implement, as in section 4.
- A file whose kind the layout does not cover: name the file and ask whether the layout should cover it. A file the layout does not cover does not block the issue.
- A project with no `## Code layout` section in its `CLAUDE.md`: say so and check nothing. Never invent a layout, not even a common one for the stack. The missing layout does not block the issue.

## 4. Return an unmet criterion to Implement

If a criterion is not met, or a new file is outside the layout, the review ends here. What is not met is corrected in Implement, never inside Review:

1. Move the issue back to Implement with `transitionJiraIssue`, using the transition that goes to Implement.
2. Name the criterion that is missing and say what is missing from it, or the file that is outside the layout and where the layout says it should go.
3. Log the real time worked in Review on the issue with `addOrEditJiraIssueWorklog` (`executeWrite`): read the issue's changelog with `executeRead` → `listJiraIssueChangelogs` (`maxResults`: 50, and the next pages with `startAt` while `total` is larger), save it, with all its pages in one list, to a temporary file and run `python3 ../implement/scripts/state_time.py <file> Review`. It adds up every stretch in Review, the one still open included, and prints `started` and `timeSpent`: log those two values, never the estimate. Tell the person the time you logged, so they can correct it.

## 5. Open the pull request

Only when `Integration` is `pull request` and every criterion is met, so the review comes out clean. In `merge` mode, go on to section 6. An unmet criterion went back to Implement in section 4 and nothing is pushed; an Epic or a Spike never opens a pull request.

1. Push the branch: `git push -u origin <branch>`. If this branch already has an open pull request (`gh pr list --head <branch> --state open --json url`), the push updates it: do not open another, give its link in the report and skip the next two steps.
2. Write the body in a temporary file outside the repository (`mktemp`) from `assets/pull-request.md`: under Criteria, the verdict and evidence of each criterion from section 3; under For the maintainer's decision, what the criteria do not cover, a new file the layout does not cover and any commit of the comparison that is missing or extra; under Not verified, what no test shows. Remove a section that has nothing; Criteria always has content. Delete the file afterwards.
3. Open the pull request: `gh pr create --base develop --head <branch> --title "<KEY> <Summary>" --body-file <file>`. The title is the issue's key and its Summary exactly as in Jira.

Without the GitHub CLI or the remote, write the commands and the body you would use and say that nothing was pushed.

## 6. Report and stop

If every criterion is met, report the result of the review: the verdict of each criterion and the commit comparison, and in `pull request` mode the link of the pull request. Integrate nothing: do not merge and do not move the issue to Done; the only push is the branch of the pull request in section 5. The issue stays in Review until the maintainer says to close it.

## 7. Review an Epic

An Epic has no branch, no tests and no diff: it is done through its children. List them (`parent = <KEY>`, `searchJiraIssuesUsingJql`).

- If every child is Done or Cancelled, move the Epic to Review with `transitionJiraIssue` and report that its children are finished.
- If any child is not, the Epic stays in Implement: name each child that is not finished and its state, and stop.

## 8. Review a Spike

A Spike has no tests and no criteria to diff: it is reviewed on whether what it tested can be reproduced. Move it to Review with `transitionJiraIssue`, then:

1. Run its test again in its worktree (`.claude/worktrees/<KEY>-<slug>`), with the steps its findings page documents.
2. Compare the result with the answer of the findings page and say whether it is reproducible: the same answer comes out, or it does not.
3. Read the findings page against the Spike's Done when and say whether each point is covered.

If it is not reproducible, return it to Implement and log the Review time, as in section 4. Otherwise report the result and stop, as in section 6: merging is never part of a Spike.
