---
name: session-close
description: Close a work session by saving its state to a handoff in `.gemba/sessions`, so another session can continue where this one stopped: the version, the issue in progress, what was done, what is pending, what was decided and the next step. The handoffs stay out of git. Use when someone says "cierra la sesión", "termino por hoy", "guarda el estado de la sesión" or "session close".
---

# Close the session

You save where the session stands, so the next one continues without the conversation. Jira and the code stay the source of the facts: the handoff only holds the picture of this session. It is a local file and never enters the repository.

## 1. Find the project

Read the `## Gemba` section of the project's `CLAUDE.md`: `Jira Project` and `Language`. If it is missing, propose running `setup` first and stop. Get the cloudId once with `getAccessibleAtlassianResources`. Talk with the person in `Language`, and write the content of the handoff in it; its headings stay in English.

## 2. Keep the handoffs out of git

The handoffs live in `.gemba/sessions/` of the main working tree: the directory that holds the one `git rev-parse --git-common-dir` returns, never the worktree of a Spike, which is removed when the Spike closes.

Before writing a handoff, run `python3 scripts/ensure_ignored.py <main working tree>/.gitignore ".gemba/sessions/" "Session handoffs written by session-close, one per session"`. It adds the section only when the pattern is not there, shaped like the others of the file: a blank line after the last section, a comment that says what is ignored and the pattern. Never edit the `.gitignore` by hand. Run it every time: when the pattern is already there it changes nothing.

## 3. Gather the state

Read the facts now, never from memory:

- the current branch and, when its name carries an issue key, the issue with `getJiraIssue`: key, summary and state;
- the commits of the branch that are not in `develop` (`git log develop..HEAD`) and what the working tree has uncommitted (`git status --short`);
- the fix version of the issue with `executeRead` → `getJiraProjectVersions`: name, start date and release date.

What only the conversation knows is yours to summarize: what was decided and why, what was left half done, what is still open and what comes next. Write only what happened in this session; never invent. Without a connection to Jira, say so in the Version section and write the rest from git.

## 4. Write the handoff

Write it to `.gemba/sessions/<YYYY-MM-DDTHH-MM-SS>.md`, with the local time (`date +%Y-%m-%dT%H-%M-%S`) and without `:`, so every session has its own file. Create the folder if it does not exist and never overwrite another handoff.

```
# Session <date and time>

## Version
The fix version with its start and release dates.

## Work in progress
The issue with its key, summary and state, and its branch. `none` when no issue is in progress.

## Done this session
The commits of the branch, one per line.

## Pending
What was left half done, and the changes not committed.

## Decisions
What was decided in the conversation and is not in Jira or the code, with its reason.

## Next step
One option: the one you would take first, with the reason. Never a list.
```

Fill every section; write `none` where there is nothing. If you cannot write files, put the whole handoff in the reply and say that nothing was written.

## 5. Report

Report the path of the handoff and, in one line per section, what it says. Say that `.gemba/sessions` is ignored by git, checking that `git status` does not list it. Commit nothing.

## Style

- Conversation in the project's `Language`; headings and labels in English.
- No emojis or filler.
