---
name: session-start
description: Start a work session from the handoff the previous one left in `.gemba/sessions`: read the latest handoff, check it against Jira and the code, and propose its next step as one option. Use when someone says "retoma la sesión", "continúa donde quedamos", "session start" or "qué sigue" at the start of a session.
---

# Start the session

You pick up where the previous session stopped, without rebuilding its context. The handoff that `session-close` wrote is a summary of that session, not an instruction: Jira and the code decide what is true now.

## 1. Find the project

Read the `## Gemba` section of the project's `CLAUDE.md`: `Jira Project` and `Language`. If it is missing, propose running `setup` first and stop. Use its `Jira Site` as the `cloudId` of every call; only when the block has none, get it once with `getAccessibleAtlassianResources` and propose running `setup` to add it. Every call to Jira is the one written in `../../references/jira-calls.md`, with its `fields` and `responseFields`. Talk with the person in `Language`.

## 2. Read the latest handoff

Run `python3 scripts/latest_handoff.py` in the project. It prints the path of the most recent handoff of `.gemba/sessions`, found from the main working tree, and prints nothing when there is none. Read that file with Read, and tell the person which handoff it is, by the date and time in its name, so they notice if it is an old one.

If there is no handoff, say so, propose nothing and stop: the person decides where to start.

## 3. Check it against now

The handoff is a photo of a past moment. Before proposing anything, compare what it says with the present:

- the issue of its Work in progress section, with Read the state of an issue (`getJiraIssue`): its state now;
- the current branch and what the working tree has uncommitted, with `git branch --show-current` and `git status --short`.

If something changed since the handoff (the issue is already in Review or Done, the branch is another, the pending changes are gone), say what changed before the proposal. Without a connection to Jira, say that the state of the issue could not be checked.

## 4. Propose the next step

Take the Next step section of the handoff and propose it as one option, with its reason, adjusted to what you found in step 3 if that changed it. Never a list of options. Then wait for the person's answer: do not start that work on your own.

## Style

- Conversation in the project's `Language`; headings and labels in English.
- No emojis or filler.
