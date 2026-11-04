---
name: version-close
description: Close the planning of a version: check that no issue of its fix version is outside Done or Cancelled, and when one is, do not close and name the open ones. Use when someone says "cierra la planeación de la versión", "revisa si la versión se puede cerrar" or that the work of a version is finished and its planning has to close.
---

# Close the planning of a version

You close a version only when all its work is closed. Jira is the source: the issues of the fix version are read every time, never remembered from earlier in the conversation. It changes no color of the Story Map: the Done state of the issues already shows what was delivered.

## 1. Find the project

Read the `## Gemba` section of the project's `CLAUDE.md`: `Jira Project` and `Language`. If it is missing, say that Gemba Code's `setup` writes it and stop. Get the cloudId once with `getAccessibleAtlassianResources`.

## 2. Check the issues

The version is the one the maintainer names. If they did not name one, take the earliest unreleased version (`executeRead` → `getJiraProjectVersions`).

Search its open issues with `searchJiraIssuesUsingJql`: `project = <Jira Project> AND fixVersion = "<version>" AND status NOT IN (Done, Cancelled)`. Leave out the release Task of the version, `Release <Product> vX.Y.Z`: it is the last to close, together with the publication, so it never counts as open work.

- **Some issue is left:** do not close the version. List each one on its own line, as a link with its summary and status, and say that the version stays open until they are Done or Cancelled. Change nothing in them and stop there.
- **None is left:** say that no issue keeps the version open and go on with the close.

Without a connection to Jira, write the search you would make and take as its result the list the person gives you. Say that nothing was changed.

## 3. Hand the facts to learn

Only once no issue keeps the version open, as the search of step 2 showed. Learn is the review of a closed release in Gemba Product's `story-map` skill; you give it the facts from Jira, and you do not calibrate anything or compute a delivery date from the worklogs.

1. Search the version's issues with `searchJiraIssuesUsingJql` (`project = <Jira Project> AND fixVersion = "<version>"`), asking for key, type, summary, status, original estimate and time spent. The delivered ones are those in Done; one in Cancelled was not delivered, so it is listed apart and its estimate does not enter the totals. The release Task of the version is listed apart as pending while it is not Done: it closes with the publication, so its estimate and time are in neither the table nor the totals.
2. Hand over a table with every delivered issue, each with its original estimate and the time recorded in its worklogs, and say `none` where it has no estimate or no time. Add the estimates and the times with a tool (Bash), never from memory, and give both totals.
3. Tell the maintainer that Gemba Product's `story-map` skill takes it from here to review the release and prepare the next one.

Without a connection to Jira, write the search, take the list the person gives you as its result, and hand over the same facts.

## Style

- Conversation in the project's `Language`; headings and labels in English.
- No emojis or filler.
