---
name: version-close
description: Close a version: check that no issue of its fix version is outside Done or Cancelled, and when one is, do not close and name the open ones. Use when someone says "cierra la versión", "termina el release", "libera la versión" or that the work of a version is finished.
---

# Close a version

You close a version only when all its work is closed. Jira is the source: the issues of the fix version are read every time, never remembered from earlier in the conversation.

## 1. Find the project

Read the `## Gemba` section of the project's `CLAUDE.md`: `Jira Project` and `Language`. If it is missing, propose running `setup` first and stop. Get the cloudId once with `getAccessibleAtlassianResources`.

## 2. Check the issues

The version is the one the maintainer names. If they did not name one, take the earliest unreleased version (`executeRead` → `getJiraProjectVersions`).

Search its open issues with `searchJiraIssuesUsingJql`: `project = <Jira Project> AND fixVersion = "<version>" AND status NOT IN (Done, Cancelled)`. Leave out the release Task of the version, `Release <Product> vX.Y.Z`: it is the last to close, together with the close itself, so it never counts as open work.

- **Some issue is left:** do not close the version. List each one on its own line, as a link with its summary and status, and say that the version stays open until they are Done or Cancelled. Change nothing in them and stop there.
- **None is left:** say that no issue keeps the version open and go on with the close.

Without a connection to Jira, write the search you would make and take as its result the list the person gives you. Say that nothing was changed.

## Style

- Conversation in the project's `Language`; headings and labels in English.
- No emojis or filler.
