---
name: version-start
description: Open a version from the closed Story Map: read the Product Brief and the current release of the Story Map from Confluence, set its open questions aside, have the maintainer confirm each card as a Story or an Epic, create the fix version named after the product and its number (Product vX.Y.Z) with its dates before anything is declared, once declared replace each story of the Story Map with the card of its issue, and postpone a declared issue to the next release. Use when someone says "abre la versión", "arranca la versión", "inicia el release", or that discovery closed a release and development starts.
---

# Start a version

You open a version from what discovery agreed. Confluence is the only source: the Product Brief and the Story Map are read from the product's space every time, and no copy of them goes to the repository, in Markdown or any other format.

## 1. Find the project

Read the `## Gemba` section of the project's `CLAUDE.md`: `Jira Project`, `Confluence Space` and `Language`. If it is missing, propose running `setup` first and stop. Get the cloudId once with `getAccessibleAtlassianResources`.

Then check that Gemba Code's `gemba-code:start` is among the available skills, because it declares every issue of the version. If it is not, say that Gemba Code is required to open a version and has to be installed, and stop: read nothing, create no fix version and declare nothing.

## 2. Read the Product Brief

Find it with `searchConfluence` (`space = "<Confluence Space>" AND title ~ "Product Brief"`) and read it with `getConfluenceContent` (`detail: full`, `content_format: markdown`). If the space has more than one brief, ask which product the version is for. If it has none, say that discovery has to write it first and stop.

## 3. Read the current release of the Story Map

Find the whiteboard with `searchConfluence` (`space = "<Confluence Space>" AND type = whiteboard AND title ~ "Story Map"`), the one of the same product as the brief. Read it with `getConfluenceContent` (`content_format: svg`).

Save the SVG to a temporary file outside the repository (`mktemp`), run `python3 ../story-map/scripts/read_story_map.py <file> --mvp --json` and delete the file. The script takes the current release, the first green one that is not delivered: green is the release about to be declared and gray the ones after it. It returns that release's `release` name, its `description` (the value it delivers), how many of its stories are `declared` (already the card of an issue) and `pending` (still a rectangle or a sticky), and its `stories` by activity and task, each with its `key` when it is already the card of an issue, with the red stickies apart in `open_questions`: see step 4. A story with a `key` is already declared, usually because it was postponed from an earlier version (step 10): it is not a story to declare.

If `release` comes back empty, no release is green: say that the Story Map has no release left to open and that discovery has to plan the next one, and stop.

## 4. Set the open questions aside

A red sticky is an open question, not a story: it gets no issue. When `open_questions` is not empty, name each one in the person's `Language`, in its own words, and say that it does not enter this version: step 9 moves it, still red, to the release after the current one, where discovery decides it before that release opens. The version goes on without it: do not ask for the decision here, do not hold the version for it and do not turn it into a story.

When `open_questions` is empty, go on to step 5.

## 5. Confirm the release

Before showing anything, ask the maintainer once, in a single message, for what their request did not give: the start date and the delivery date of the version, and the hours of work per day. Wait for the answer. The hours per day are asked for every version and are never written to the `CLAUDE.md` or anywhere else; the dates are the ones step 6 uses. If the request already confirms the release and gives the Epics' due dates, do not ask: go on to steps 6 and 7.

Each Story Map card of the release is an activity with its stories in this release. A story that is already declared is shown apart, with its key and its state in Jira, and you never declare it again: only the stories with no key are declared. Show every card once, in board order:

- the activity;
- how it will be declared: a card with one story is a Story; a card with two or more is an Epic with one Story per story;
- its stories, by task, each with the original estimate in hours that `gemba-code:start` proposes for it (`gemba-code:start`'s `references/estimation.md`); an Epic has none;
- one table with a row for every issue, the Epic's row too, and always the columns Priority, Component, Estimate and Blockers, as `gemba-code:start` would ask for them, proposed by you. Propose the components for the whole release together: the same part of the product carries the same component in every row, so one part never shows under two names (`api` and `backend`). Unify them before asking for the confirmation. Fill every cell: write `none` where a field is empty (an Epic has no component or estimate), and never leave a column out of a row, the Blockers of an Epic included. For an Epic, add its due date, which you propose and the maintainer can change.

Propose the Epics' due dates in board order, each one different from the others and none after the delivery date. Space them by the hours: an Epic's date is the day on which the hours of work since the start date, counted at the hours per day, reach the estimates of the Epics so far, rounded up to a whole day. An Epic fits when the sum of its Stories' estimates is not more than the hours available from the day after the previous Epic's due date (from the start date, for the first) through its own due date. When an Epic does not fit, say so before asking for the confirmation: name the Epic, its hours and the hours available. Never cut stories, lower estimates or move the dates on your own: the maintainer decides.

Propose the version number with the project's published versions: read them with `executeRead` → `getJiraProjectVersions`, save the result to a temporary file outside the repository (`mktemp`), run `python3 scripts/next_version.py "<Product>" <file>` and delete the file. It prints the name of the next release, which raises the minor number. If the maintainer says the version is a bug fix on a published one, run it again with `--fix`, which raises the third number. Show that name as the fix version, and use its number in the release Task. The maintainer confirms it or changes it together with the release.

After the cards, show the release Task `Release <Product> vX.Y.Z` that step 8 declares, with the number proposed above, its component, High priority and a 1h estimate. The component is one the project already has (`executeRead` → `listJiraProjectComponents`): the one where the version is bumped or, if none is, the component of the last card. In a project with no components yet, it is the component proposed for those same cards. A component the maintainer names for the Task is the one used. Never ask for it and never name one apart from these: it only labels the Task, and the maintainer can change it when they confirm.

Then ask the maintainer to confirm the release. They can change any estimate, priority, component, blocker or due date before confirming; keep their value as it is. Only an explicit confirmation counts: until they confirm, nothing is created in Jira, not even when they ask to skip the review.

If they ask for a change (a story in or out, moved to another release or activity, reworded), it is made on the Story Map, never only in what will be declared: Confluence is the only source. Make it with Gemba Product's `story-map` skill if it is installed, or ask the person to make it on the board. Then read the release again (step 3) and show it again from step 4. Until that new reading, show no release at all, neither as it would look after the change nor as it is before it: only a reading of the board after the change counts. Each change goes through the board and a new reading before declaring.

## 6. Create the fix version

Once the maintainer confirms the release, create its fix version before declaring anything, so every issue hangs from it.

- Name: `<Product> vX.Y.Z`, with the product name as the brief and the board give it and the number the maintainer confirmed in step 5, without asking for it again. If the maintainer changed it and it breaks the rule (each release raises the minor number, a bug fix on a released version raises the third, the major stays at 0 until the first paying customer), say so and ask again.
- Start date and release date: the ones the maintainer gave in step 5. Ask only for one that is still missing.
- Description: only the value the version delivers, from the release's row label on the board (the reading returns it as `description`). No stories, issues, dates or numbers.

First list the project's versions with `executeRead` → `getJiraProjectVersions`. If one with the same name already exists, do not create another: say so and use it. Otherwise create it with `executeDestructive` → `manageJiraProjectVersion` (`action: "create"`, `projectIdOrKey`, `name`, `startDate`, `releaseDate`, `description`), then read the versions again and report the one that is there.

Without a connection to Jira, write the call you would make and say that nothing was created.

## 7. Declare the cards

Right after the fix version, hand `gemba-code:start` all the confirmed cards in one request, so it checks the Stories of the whole version before creating any issue, and declare them through `gemba-code:start` in that fix version, in board order: a card with one story as a Story with no Epic, a card with two or more as an Epic with one Story per story as its children. Hand `gemba-code:start` the card, its fields as the maintainer confirmed them and the Story Map link for an Epic's Source. The maintainer already confirmed the whole version in step 5: once `gemba-code:start` has no open edge-case question, it creates each issue without asking again, and you do not ask either: do not offer a last chance to change something before creating. While `gemba-code:start`'s round has a question without an answer, no issue of the version is created or drafted as ready: report which questions are missing and stop. If the maintainer already confirmed the release in their request, do not show it again; go on to steps 6 and 7. Then report the keys, one line per card.

A story that is already declared (it has a `key`) never creates another issue. Read it with `getJiraIssue`: when its fix version is empty, because it was postponed, edit it through `gemba-code:start` so its fix version is the one created in step 6 (it edits only an issue in Backlog); when it has another fix version, leave it as it is and name it in the result with its key and that version, so the maintainer decides. Report the key of each one with the others.

## 8. Declare the release Task

When all the cards are declared, declare the version's release through `gemba-code:start`, as a Task in the same fix version: summary `Release <Product> vX.Y.Z`, the component confirmed in step 5 (when the maintainer confirmed the release in their request, the one chosen by the rule of step 5: it is not a pending question and you do not offer to change it), with no blocking links. It is the last issue to close, because it waits for every other issue of the version to be Done or Cancelled, so publishing is part of the plan. Its Done when lists, in the project's `Language`:

- the version bump, integrated into `develop`;
- `develop` merged into `main`;
- the tag of the version;
- the release on GitHub, with its notes;
- the fix version released in Jira.

Like the cards, it is created without asking again. Report its key with the others.

## 9. Put the cards on the Story Map

When every issue is declared, replace the stories of the release on the board with the cards of their issues, so the map shows the real state of each story without copying keys by hand. Read the board again, because the earlier reading is stale after the declaration:

1. Read the Story Map with `getConfluenceContent` (`content_format: svg`) and save the SVG to a temporary file outside the repository (`mktemp`).
2. Write a `keys.json` in another temporary file: the key of each Story `gemba-code:start` created, by the text of its story on the board (`{"Save a date per customer": "GEMBA-1"}`). An Epic has no card of its own: only its Stories go in, and the rows of persona, activities and tasks are never touched.
3. Run `python3 ../story-map/scripts/card_story_map.py <board> <keys> --site <url of the Jira site>`, with the `url` that `getAccessibleAtlassianResources` gave. It prints the patch: the card of each story in the same place, the open questions moved to the next release and, on a board in the old colors, the next releases in gray. A story without a key in `keys.json` is named on stderr and left as it is.
4. Apply the patch with `updateConfluenceContent`, with the SVG you read as `context.content`. The response of the patch says nothing about what happened.
5. Read the board again and run the same script with `--check` on that second reading, then delete the temporary files. Report from that reading, never from the response: how many stories are now cards (the cards are always gray) and each story whose card could not be put. A story whose card could not be put stays on the board as it was: name it in the result with its key, so the maintainer can place it by hand.

Without a connection to Confluence, write the patch you would apply and say that the board was not changed.

## 10. Postpone a declared issue

When the maintainer says that an issue already declared does not go in this version, move it to the next release; nothing else about the issue changes. Read the issue first with `getJiraIssue`: only an issue in Backlog is postponed, because `gemba-code:start` edits an issue only while it is in Backlog. An issue outside Backlog is not postponed: say its state, leave its card where it is and stop. Its state in Jira decides what the card shows, and a cancellation changes nothing on the board.

1. Read the Story Map with `getConfluenceContent` (`content_format: svg`) and save the SVG to a temporary file outside the repository (`mktemp`). Find the card of the issue with `python3 ../story-map/scripts/read_story_map.py <file> --json`: it carries its key and its `id`.
2. Run `python3 ../story-map/scripts/move_story_map.py <file> --story <id> --to "<release after the current one>"`. The card keeps its column and its issue. Apply the patch with `updateConfluenceContent`, with the SVG you read as `context.content`, and delete the temporary file. Never recolor it: a card is always gray, and it waits in that release until its version is declared.
3. Through `gemba-code:start`, edit the issue so its fix version is empty. It is not given the version of the next release, because that version does not exist until the release opens: step 7 gives it when the release is declared.
4. Read the board again and report from that reading, never from the response of the patch: the release the card is in now, and the issue with its fix version empty.

Without a connection to Confluence or Jira, write the patch or the edit you would make and say that nothing was changed.

## Without a connection

If there is no connection to Confluence, say that the brief and the Story Map are read only from Confluence and could not be read. Do not ask for a copy in the repository. If the person pastes the board as Confluence returns it, read that the same way.

## Style

- Conversation in the project's `Language`; headings and labels in English.
- No emojis or filler.
